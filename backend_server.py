import base64
import json
import mimetypes
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
LANDING_DIR = ROOT_DIR / "landing page"
AUTH_DB_PATH = ROOT_DIR / "auth_users.json"
STREAMLIT_URL = "http://127.0.0.1:8501"
STREAMLIT_PROCESS = None


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
            self.redirect_to_app()
            return

        if path == "/health":
            self.send_json({"status": "ok", "landing_page": "/"})
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
            "password": password,
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

        users = load_users()
        user = next(
            (
                item for item in users
                if (item.get("email") == identifier or item.get("mobile") == identifier)
                and item.get("password") == password
            ),
            None,
        )

        if user is None:
            self.send_json({"ok": False, "message": "Invalid email/mobile number or password."}, 401)
            return

        self.send_json({
            "ok": True,
            "message": f"Welcome back, {user['name']}!",
            "user": {
                "name": user["name"],
                "email": user["email"],
                "mobile": user["mobile"],
            },
        })

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

    def redirect_to_app(self):
        app_url = ensure_streamlit_running()
        self.send_response(307)
        self.send_header("Location", app_url)
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
    server = ThreadingHTTPServer(("127.0.0.1", 8000), AppRequestHandler)
    print("Landing page server running at http://127.0.0.1:8000")
    print("Open http://127.0.0.1:8000/ to view the landing page")
    print("Open http://127.0.0.1:8000/app to launch the main app")
    server.serve_forever()


if __name__ == "__main__":
    main()
