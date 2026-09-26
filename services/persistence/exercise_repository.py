import ast
import json
import sqlite3
import streamlit as st
from pathlib import Path

_DB_PATH = str(Path(__file__).parent.parent.parent / "data.db")


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = _get_connection()

    try:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    username   TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS exercises (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id       INTEGER NOT NULL REFERENCES users(id),
                    exercise_name TEXT    NOT NULL,
                    reps          INTEGER NOT NULL DEFAULT 0,
                    sets          INTEGER NOT NULL DEFAULT 0,
                    time          INTEGER NOT NULL DEFAULT 0,
                    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_plans (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id       INTEGER NOT NULL UNIQUE REFERENCES users(id),
                    plan_data     TEXT NOT NULL,
                    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
    finally:
        conn.close()


def get_user(username: str) -> sqlite3.Row:
    conn = _get_connection()

    try:
        return conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
    finally:
        conn.close()


def create_user(username: str) -> sqlite3.Row:
    conn = _get_connection()

    try:
        with conn:
            conn.execute(
                "INSERT INTO users (username) VALUES (?)", (username,)
            )
    finally:
        conn.close()

    return get_user(username)


def get_or_create_user(username: str) -> sqlite3.Row:
    user = get_user(username)

    if user is None:
        user = create_user(username)
    
    return user


def add_exercise(user_id, exercise_name, reps, sets, time):
    conn = _get_connection()

    try:
        with conn:
            existing = conn.execute(
                "SELECT * FROM exercises WHERE user_id = ? AND exercise_name = ? AND date(created_at) = date('now')",
                (user_id, exercise_name),
            ).fetchone()

            if existing:
                conn.execute(
                    "UPDATE exercises SET reps = reps + ?, sets = sets + ?, time = time + ? WHERE id = ?",
                    (reps, sets, time, existing["id"]),
                )
            else:
                conn.execute(
                    "INSERT INTO exercises (user_id, exercise_name, reps, sets, time) VALUES (?, ?, ?, ?, ?)",
                    (user_id, exercise_name, reps, sets, time),
                )
    finally:
        conn.close()


def get_users_exercises(user_id):
    conn = _get_connection()

    try:
        return conn.execute(
            "SELECT * FROM exercises WHERE user_id = ?",
            (user_id,),
        ).fetchall()
    finally:
        conn.close()


def save_user_plan(user_id, plan_data):
    conn = _get_connection()

    try:
        with conn:
            conn.execute(
                "INSERT INTO user_plans (user_id, plan_data) VALUES (?, ?) "
                "ON CONFLICT(user_id) DO UPDATE SET plan_data = excluded.plan_data, updated_at = CURRENT_TIMESTAMP",
                (user_id, json.dumps(plan_data)),
            )
    finally:
        conn.close()


def get_user_plan(user_id):
    conn = _get_connection()

    try:
        row = conn.execute(
            "SELECT plan_data FROM user_plans WHERE user_id = ?",
            (user_id,),
        ).fetchone()

        if row is None:
            return None

        return json.loads(row["plan_data"])
    finally:
        conn.close()


def delete_user_plan(user_id):
    conn = _get_connection()

    try:
        with conn:
            conn.execute(
                "DELETE FROM user_plans WHERE user_id = ?",
                (user_id,),
            )
    finally:
        conn.close()
