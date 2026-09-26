import base64
import hashlib
import hmac
import json
import mimetypes
import os
import secrets
import smtplib
import ssl
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
import uuid
from email.message import EmailMessage
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent
LANDING_DIR = ROOT_DIR / "landing page"
AUTH_DB_PATH = ROOT_DIR / "auth_users.json"
STREAMLIT_URL = "http://127.0.0.1:8501"
STREAMLIT_BASE_PATH = os.environ.get("STREAMLIT_BASE_PATH", "").strip("/")
if STREAMLIT_BASE_PATH:
    STREAMLIT_URL = f"{STREAMLIT_URL}/{STREAMLIT_BASE_PATH}"
STREAMLIT_PROCESS = None
LAUNCH_TICKET_TTL_SECONDS = 60
LAUNCH_TICKETS = {}
LAUNCH_TICKETS_LOCK = threading.Lock()
AUTH_USERS_LOCK = threading.Lock()
PASSWORD_HASH_ITERATIONS = 310_000
RESET_CODE_TTL_SECONDS = 10 * 60
RESET_CODE_MAX_ATTEMPTS = 5
RESET_REQUEST_LIMIT = 3
RESET_REQUEST_WINDOW_SECONDS = 15 * 60
RESET_CHALLENGES = {}
RESET_REQUESTS = {}
RESET_STATE_LOCK = threading.Lock()
RESET_HASH_SECRET = secrets.token_bytes(32)


class PasswordResetDeliveryError(RuntimeError):
    def __init__(self, message, user_message):
        super().__init__(message)
        self.user_message = user_message


def create_launch_ticket(user):
    ticket = secrets.token_urlsafe(32)
    safe_user = {
        "name": user["name"],
        "email": user["email"],
        "mobile": user["mobile"],
    }
    now = time.monotonic()

    with LAUNCH_TICKETS_LOCK:
        expired_tickets = [
            value for value, (_, expires_at) in LAUNCH_TICKETS.items()
            if expires_at <= now
        ]
        for value in expired_tickets:
            del LAUNCH_TICKETS[value]
        LAUNCH_TICKETS[ticket] = (
            safe_user,
            now + LAUNCH_TICKET_TTL_SECONDS,
        )

    return ticket


def has_launch_ticket(ticket):
    with LAUNCH_TICKETS_LOCK:
        entry = LAUNCH_TICKETS.get(ticket)
        return entry is not None and entry[1] > time.monotonic()


def consume_launch_ticket(ticket):
    with LAUNCH_TICKETS_LOCK:
        entry = LAUNCH_TICKETS.pop(ticket, None)

    if entry is None or entry[1] <= time.monotonic():
        return None
    return entry[0]


def hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_HASH_ITERATIONS,
    )
    return "pbkdf2_sha256${}${}${}".format(
        PASSWORD_HASH_ITERATIONS,
        salt.hex(),
        digest.hex(),
    )


def verify_password(password, stored_password):
    if not stored_password.startswith("pbkdf2_sha256$"):
        return hmac.compare_digest(
            password.encode("utf-8"),
            stored_password.encode("utf-8"),
        ), False

    try:
        algorithm, iterations, salt, expected_digest = stored_password.split("$")
        if algorithm != "pbkdf2_sha256":
            return False, False
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt),
            int(iterations),
        )
        return hmac.compare_digest(digest.hex(), expected_digest), True
    except (ValueError, TypeError):
        return False, True


def _password_reset_code_digest(code):
    return hmac.new(
        RESET_HASH_SECRET,
        code.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def send_password_reset_code(user, channel, code):
    message_text = (
        f"Your AI Gym Coach password reset code is {code}. "
        f"It expires in {RESET_CODE_TTL_SECONDS // 60} minutes."
    )

    if channel == "email":
        host = os.environ.get("SMTP_HOST")
        username = os.environ.get("SMTP_USERNAME")
        password = os.environ.get("SMTP_PASSWORD")
        sender = os.environ.get("SMTP_FROM")
        if not all((host, username, password, sender)):
            raise PasswordResetDeliveryError(
                "Email OTP is not configured.",
                "Email reset is not configured. Ask the site administrator to configure a reset delivery method.",
            )

        email = EmailMessage()
        email["Subject"] = "Your AI Gym Coach password reset code"
        email["From"] = sender
        email["To"] = user["email"]
        email.set_content(message_text)

        port = int(os.environ.get("SMTP_PORT", "587"))
        with smtplib.SMTP(host, port, timeout=15) as client:
            client.starttls(context=ssl.create_default_context())
            client.login(username, password)
            client.send_message(email)
        return

    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    sender = os.environ.get("TWILIO_FROM_NUMBER")
    if not all((account_sid, auth_token, sender)):
        raise PasswordResetDeliveryError(
            "SMS OTP is not configured.",
            "SMS reset is not configured. Ask the site administrator to configure a reset delivery method.",
        )

    endpoint = (
        f"https://api.twilio.com/2010-04-01/Accounts/"
        f"{urllib.parse.quote(account_sid, safe='')}/Messages.json"
    )
    body = urllib.parse.urlencode({
        "From": sender,
        "To": user["mobile"],
        "Body": message_text,
    }).encode("utf-8")
    credentials = f"{account_sid}:{auth_token}".encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=body,
        headers={
            "Authorization": "Basic " + base64.b64encode(credentials).decode("ascii"),
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        if response.status < 200 or response.status >= 300:
            raise RuntimeError(f"SMS provider returned HTTP {response.status}.")


def get_password_reset_methods():
    return {
        "email": all(os.environ.get(key) for key in (
            "SMTP_HOST",
            "SMTP_USERNAME",
            "SMTP_PASSWORD",
            "SMTP_FROM",
        )),
        "sms": all(os.environ.get(key) for key in (
            "TWILIO_ACCOUNT_SID",
            "TWILIO_AUTH_TOKEN",
            "TWILIO_FROM_NUMBER",
        )),
    }


def normalize_phone_number(value):
    digits = "".join(character for character in value if character in "0123456789")
    return f"+{digits}" if value.strip().startswith("+") else digits


def find_reset_user(users, identifier):
    normalized_identifier = identifier.strip().lower()
    for user in users:
        if user.get("email", "").strip().lower() == normalized_identifier:
            return user
        if normalize_phone_number(user.get("mobile", "")) == normalize_phone_number(identifier):
            return user
    return None


def create_password_reset_challenge(remote_address, identifier, channel, user):
    now = time.monotonic()
    recipient_hash = hashlib.sha256(
        identifier.strip().lower().encode("utf-8")
    ).hexdigest()
    request_keys = (
        (remote_address, "all"),
        (remote_address, channel, recipient_hash),
    )
    code = f"{secrets.randbelow(1_000_000):06d}"
    reset_id = secrets.token_urlsafe(32)

    with RESET_STATE_LOCK:
        for challenge_id, challenge in list(RESET_CHALLENGES.items()):
            if challenge["expires_at"] <= now:
                del RESET_CHALLENGES[challenge_id]
        for key, request_times in list(RESET_REQUESTS.items()):
            recent_requests = [
                requested_at
                for requested_at in request_times
                if requested_at > now - RESET_REQUEST_WINDOW_SECONDS
            ]
            if recent_requests:
                RESET_REQUESTS[key] = recent_requests
            else:
                del RESET_REQUESTS[key]

        request_limits = (10, RESET_REQUEST_LIMIT)
        recent_requests = [
            RESET_REQUESTS.get(key, [])
            for key in request_keys
        ]
        if any(
            len(times) >= limit
            for times, limit in zip(recent_requests, request_limits)
        ):
            return None, None
        for key, request_times in zip(request_keys, recent_requests):
            request_times.append(now)
            RESET_REQUESTS[key] = request_times
        RESET_CHALLENGES[reset_id] = {
            "email": user.get("email") if user else None,
            "mobile": user.get("mobile") if user else None,
            "channel": channel,
            "code_digest": _password_reset_code_digest(code),
            "expires_at": now + RESET_CODE_TTL_SECONDS,
            "attempts": 0,
            "request_keys": request_keys,
            "request_time": now,
        }

    return reset_id, code if user else None


def release_password_reset_request(reset_id):
    with RESET_STATE_LOCK:
        challenge = RESET_CHALLENGES.pop(reset_id, None)
        if challenge is None:
            return

        request_time = challenge["request_time"]
        for key in challenge["request_keys"]:
            request_times = RESET_REQUESTS.get(key, [])
            for index in range(len(request_times) - 1, -1, -1):
                if request_times[index] == request_time:
                    del request_times[index]
                    break
            if request_times:
                RESET_REQUESTS[key] = request_times
            else:
                RESET_REQUESTS.pop(key, None)


def complete_password_reset(reset_id, code, new_password):
    with RESET_STATE_LOCK:
        challenge = RESET_CHALLENGES.get(reset_id)
        if challenge is None or challenge["expires_at"] <= time.monotonic():
            RESET_CHALLENGES.pop(reset_id, None)
            return "invalid"

        if challenge["attempts"] >= RESET_CODE_MAX_ATTEMPTS:
            del RESET_CHALLENGES[reset_id]
            return "invalid"

        if not hmac.compare_digest(
            _password_reset_code_digest(code),
            challenge["code_digest"],
        ):
            challenge["attempts"] += 1
            if challenge["attempts"] >= RESET_CODE_MAX_ATTEMPTS:
                del RESET_CHALLENGES[reset_id]
            return "invalid"

        if not challenge["email"]:
            del RESET_CHALLENGES[reset_id]
            return "invalid"

        with AUTH_USERS_LOCK:
            users = load_users()
            user = next(
                (item for item in users if item.get("email") == challenge["email"]),
                None,
            )
            if user is None:
                del RESET_CHALLENGES[reset_id]
                return "invalid"

            user["password"] = hash_password(new_password)
            save_users(users)

        del RESET_CHALLENGES[reset_id]
        return "ok"


def load_users():
    if not AUTH_DB_PATH.exists():
        return []

    try:
        return json.loads(AUTH_DB_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_users(users):
    AUTH_DB_PATH.write_text(json.dumps(users, indent=2), encoding="utf-8")


def ensure_streamlit_running():
    global STREAMLIT_PROCESS

    try:
        with urllib.request.urlopen(f"{STREAMLIT_URL}/healthz", timeout=1) as response:
            if response.status == 200:
                return STREAMLIT_URL
    except Exception:
        pass

    if STREAMLIT_PROCESS is None or STREAMLIT_PROCESS.poll() is not None:
        command = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "main.py",
            "--server.address",
            "127.0.0.1",
            "--server.port",
            "8501",
        ]
        if STREAMLIT_BASE_PATH:
            command.extend(["--server.baseUrlPath", STREAMLIT_BASE_PATH])
        startupinfo = None
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        STREAMLIT_PROCESS = subprocess.Popen(
            command,
            cwd=str(ROOT_DIR),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            startupinfo=startupinfo,
        )

    for _ in range(30):
        try:
            with urllib.request.urlopen(f"{STREAMLIT_URL}/healthz", timeout=1) as response:
                if response.status == 200:
                    return STREAMLIT_URL
        except Exception:
            time.sleep(0.5)

    return STREAMLIT_URL


class AppRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        if path in ("/", "/index.html"):
            self.serve_file(LANDING_DIR / "index.html", "text/html; charset=utf-8")
            return

        if path == "/app":
            ticket = urllib.parse.parse_qs(parsed_path.query).get("ticket", [""])[0]
            self.redirect_to_app(ticket)
            return

        if path == "/health":
            self.send_json({"status": "ok", "landing_page": "/"})
            return

        if path == "/api/password-reset/methods":
            self.send_json({"methods": get_password_reset_methods()})
            return

        if path.startswith("/style.css"):
            self.serve_file(LANDING_DIR / "style.css", "text/css; charset=utf-8")
            return

        if path.startswith("/IMGs/"):
            candidate = LANDING_DIR / "IMGs_add_itself" / path[len("/IMGs/"):]
            if candidate.exists():
                self.serve_file(candidate)
                return
            if path == "/IMGs/placeholder.svg":
                self.serve_file(LANDING_DIR / "IMGs_add_itself" / "placeholder.svg")
                return

        if path.startswith("/videos/"):
            candidate = LANDING_DIR / "Videos_add_itself" / path[len("/videos/"):]
            if candidate.exists():
                self.serve_file(candidate)
                return

        if path.startswith("/Fonts/"):
            candidate = LANDING_DIR / "Fonts" / path[len("/Fonts/"):]
            if candidate.exists():
                self.serve_file(candidate)
                return

        self.send_error(404, "Page not found")

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        if path == "/api/register":
            self.handle_register()
            return

        if path == "/api/login":
            self.handle_login()
            return

        if path == "/api/password-reset/request":
            self.handle_password_reset_request()
            return

        if path == "/api/password-reset/confirm":
            self.handle_password_reset_confirm()
            return

        if path == "/api/redeem":
            self.handle_redeem()
            return

        if path == "/api/feedback":
            self.handle_feedback()
            return

        self.send_error(404, "Endpoint not found")

    def handle_register(self):
        try:
            payload = self.read_json_body()
        except Exception:
            self.send_json({"ok": False, "message": "Invalid JSON body."}, 400)
            return

        name = (payload.get("name") or "").strip()
        email = (payload.get("email") or "").strip().lower()
        mobile = (payload.get("mobile") or "").strip()
        password = (payload.get("password") or "").strip()

        if not all([name, email, mobile, password]):
            self.send_json({"ok": False, "message": "Please fill in all fields."}, 400)
            return

        with AUTH_USERS_LOCK:
            users = load_users()
            if any(user.get("email") == email for user in users):
                self.send_json({"ok": False, "message": "An account with this email already exists."}, 409)
                return

            if any(user.get("mobile") == mobile for user in users):
                self.send_json({"ok": False, "message": "An account with this mobile number already exists."}, 409)
                return

            users.append({
                "name": name,
                "email": email,
                "mobile": mobile,
                "password": hash_password(password),
            })
            save_users(users)
        self.send_json({"ok": True, "message": "Registration successful. You can now log in."})

    def handle_login(self):
        try:
            payload = self.read_json_body()
        except Exception:
            self.send_json({"ok": False, "message": "Invalid JSON body."}, 400)
            return

        identifier = (payload.get("identifier") or "").strip().lower()
        password = (payload.get("password") or "").strip()

        if not identifier or not password:
            self.send_json({"ok": False, "message": "Please enter your email or mobile number and password."}, 400)
            return

        with AUTH_USERS_LOCK:
            users = load_users()
            user = next(
                (
                    item for item in users
                    if (item.get("email") == identifier or item.get("mobile") == identifier)
                ),
                None,
            )
            password_valid = False
            if user is not None:
                password_valid, password_is_hashed = verify_password(
                    password,
                    user.get("password", ""),
                )
                if password_valid and not password_is_hashed:
                    user["password"] = hash_password(password)
                    save_users(users)

        if user is None or not password_valid:
            self.send_json({"ok": False, "message": "Invalid email/mobile number or password."}, 401)
            return

        ticket = create_launch_ticket(user)
        self.send_json({
            "ok": True,
            "message": f"Welcome back, {user['name']}!",
            "ticket": ticket,
            "user": {
                "name": user["name"],
                "email": user["email"],
                "mobile": user["mobile"],
            },
        })

    def handle_password_reset_request(self):
        try:
            payload = self.read_json_body()
        except Exception:
            self.send_json({"ok": False, "message": "Invalid JSON body."}, 400)
            return

        identifier = payload.get("identifier", "")
        channel = payload.get("channel", "")
        if not isinstance(identifier, str) or not identifier.strip() or channel not in ("email", "sms"):
            self.send_json({"ok": False, "message": "Enter your registered email or mobile number and choose a delivery method."}, 400)
            return

        identifier = identifier.strip()
        with AUTH_USERS_LOCK:
            user = find_reset_user(load_users(), identifier)

        reset_id, code = create_password_reset_challenge(
            self.client_address[0],
            identifier,
            channel,
            user,
        )
        if reset_id is None:
            self.send_json({"ok": False, "message": "Too many code requests. Please wait before trying again."}, 429)
            return

        if code is not None:
            try:
                send_password_reset_code(user, channel, code)
            except PasswordResetDeliveryError as error:
                release_password_reset_request(reset_id)
                self.send_json({
                    "ok": False,
                    "message": error.user_message,
                }, 503)
                return
            except Exception as error:
                release_password_reset_request(reset_id)
                print(f"Password reset code delivery failed: {error}")
                if channel == "sms":
                    message = "SMS delivery failed. Check the registered mobile number or contact the site administrator."
                else:
                    message = "Email delivery failed. Check the registered email or contact the site administrator."
                self.send_json({
                    "ok": False,
                    "message": message,
                }, 503)
                return

        self.send_json({
            "ok": True,
            "reset_id": reset_id,
            "message": "If an account matches those details, a reset code has been sent.",
        })

    def handle_password_reset_confirm(self):
        try:
            payload = self.read_json_body()
        except Exception:
            self.send_json({"ok": False, "message": "Invalid JSON body."}, 400)
            return

        reset_id = payload.get("reset_id", "")
        code = payload.get("code", "")
        new_password = payload.get("new_password", "")
        if not all(isinstance(value, str) and value for value in (reset_id, code, new_password)):
            self.send_json({"ok": False, "message": "Enter the reset code and a new password."}, 400)
            return
        new_password = new_password.strip()
        if len(code) != 6 or not code.isdigit():
            self.send_json({"ok": False, "message": "Enter the six-digit reset code."}, 400)
            return
        if len(new_password) < 8:
            self.send_json({"ok": False, "message": "Your new password must be at least 8 characters."}, 400)
            return

        try:
            result = complete_password_reset(reset_id, code, new_password)
        except Exception as error:
            print(f"Password reset failed: {error}")
            self.send_json({"ok": False, "message": "We could not reset your password right now. Please try again."}, 500)
            return

        if result != "ok":
            self.send_json({"ok": False, "message": "The reset code is invalid or expired. Request a new code and try again."}, 401)
            return

        self.send_json({
            "ok": True,
            "message": "Password updated. Sign in with your new password.",
        })

    def handle_redeem(self):
        try:
            payload = self.read_json_body()
        except Exception:
            self.send_json({"ok": False, "message": "Invalid JSON body."}, 400)
            return

        ticket = payload.get("ticket")
        if not isinstance(ticket, str) or not ticket:
            self.send_json({"ok": False, "message": "A launch ticket is required."}, 400)
            return

        user = consume_launch_ticket(ticket)
        if user is None:
            self.send_json({"ok": False, "message": "This login link has expired or was already used."}, 401)
            return

        self.send_json({"ok": True, "user": user})

    def handle_feedback(self):
        try:
            payload = self.read_json_body()
        except Exception:
            self.send_json({"ok": False, "message": "Invalid JSON body."}, 400)
            return

        note = (payload.get("note") or "").strip()
        file_name = (payload.get("file_name") or "").strip()
        mime_type = (payload.get("mime_type") or "").strip()
        content_base64 = (payload.get("content_base64") or "").strip()

        if not note or not file_name or not content_base64:
            self.send_json({"ok": False, "message": "Please add a note and upload a photo or video."}, 400)
            return

        try:
            file_bytes = base64.b64decode(content_base64, validate=True)
        except Exception:
            self.send_json({"ok": False, "message": "The uploaded file was not valid base64 data."}, 400)
            return

        uploads_dir = ROOT_DIR / "feedback_uploads"
        uploads_dir.mkdir(exist_ok=True)

        suffix = Path(file_name).suffix.lower()
        if not suffix:
            suffix = mimetypes.guess_extension(mime_type) or ".bin"

        saved_name = f"review_{uuid.uuid4().hex}{suffix}"
        (uploads_dir / saved_name).write_bytes(file_bytes)

        self.send_json({
            "ok": True,
            "message": "Feedback media received and queued for review.",
            "file_name": saved_name,
        })

    def read_json_body(self):
        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length).decode("utf-8") if content_length else "{}"
        return json.loads(body)

    def redirect_to_app(self, ticket):
        if not ticket or not has_launch_ticket(ticket):
            self.send_response(303)
            self.send_header("Location", "/#auth")
            self.end_headers()
            return

        query = urllib.parse.urlencode({"ticket": ticket})
        public_app_path = os.environ.get("APP_PUBLIC_PATH")
        if public_app_path:
            self.send_response(303)
            self.send_header("Location", f"{public_app_path}?{query}")
            self.end_headers()
            return

        app_url = ensure_streamlit_running()
        self.send_response(303)
        self.send_header("Location", f"{app_url}/?{query}")
        self.end_headers()

    def serve_file(self, file_path: Path, content_type: str | None = None):
        if not file_path.exists():
            self.send_error(404, "File not found")
            return

        if content_type is None:
            content_type, _ = mimetypes.guess_type(str(file_path))
            if content_type is None:
                content_type = "application/octet-stream"

        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")


def main():
    load_dotenv()
    server = ThreadingHTTPServer(("127.0.0.1", 8000), AppRequestHandler)
    print("Landing page server running at http://127.0.0.1:8000")
    print("Open http://127.0.0.1:8000/ to view the landing page")
    print("Open http://127.0.0.1:8000/app to launch the main app")
    server.serve_forever()


if __name__ == "__main__":
    main()
