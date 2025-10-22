# controllers/authController.py
import os
import re
import pandas as pd
import bcrypt
import re
from flask import request, jsonify, session
from datetime import datetime
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from utils.jwt_utils import generate_token, decode_token


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data")
USERPATH = os.path.join(DATA_DIR, "users.csv")

# === Rate limiter ===
limiter = Limiter(key_func=get_remote_address, default_limits=["100 per hour"])

# === Utility functions ===
def _read_users_df():
    if not os.path.exists(USERPATH):
        return pd.DataFrame(columns=["id", "username", "password", "status_approval", "role"])
    return pd.read_csv(USERPATH)

def _validate_input(value):
    # izinkan huruf, angka, titik, underscore, dan @
    return re.match(r'^[A-Za-z0-9@._-]+$', value)

def get_user_role():
    """Ambil role user dari JWT token"""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None

    token = auth_header.replace("Bearer ", "")
    decoded = decode_token(token)

    if isinstance(decoded, dict) and "role" in decoded:
        return decoded["role"]

    return None


# === REGISTER ADMIN ===
def register():
    data = request.get_json() or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()

    # Validasi basic
    if not username or not password:
        return jsonify({"error": "Username dan password wajib diisi"}), 400

    # Validasi karakter username
    if not _validate_input(username):
        return jsonify({"error": "Format username tidak valid. Gunakan huruf, angka, titik, atau underscore."}), 400

    # Validasi panjang password
    if len(password) < 6:
        return jsonify({"error": "Password minimal 6 karakter"}), 400

    df = _read_users_df()
    if username in df.get("username", []).values:
        return jsonify({"error": "Username sudah terdaftar"}), 400

    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    next_id = int(df["id"].max()) + 1 if not df.empty else 1
    new_user = {
        "id": next_id,
        "username": username,
        "password": hashed_pw,
        "status_approval": 0,
        "role": "admin",
    }
    df = pd.concat([df, pd.DataFrame([new_user])], ignore_index=True)
    df.to_csv(USERPATH, index=False)
    return jsonify({"success": f"User {username} berhasil registrasi. Menunggu approval superadmin."}), 201


# === LOGIN ADMIN / SUPERADMIN ===
@limiter.limit("5 per minute")  # Batasi login 5x per menit per IP
def login():
    data = request.get_json() or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()

    # Cek validasi input
    if not username or not password:
        return jsonify({"error": "Username dan password wajib diisi"}), 400

    if not _validate_input(username):
        return jsonify({"error": "Format username tidak valid"}), 400

    # Pastikan data user ada
    if not os.path.exists(USERPATH):
        return jsonify({"error": "Belum ada user terdaftar"}), 400

    df = pd.read_csv(USERPATH)
    user = df[df["username"].astype(str) == username]

    if user.empty:
        return jsonify({"error": "User tidak ditemukan"}), 404

    user = user.iloc[0]

    # Validasi approval
    if int(user["status_approval"]) == 0:
        return jsonify({"error": "Akun belum di-approve superadmin"}), 403

    # Validasi password hash
    if not bcrypt.checkpw(password.encode("utf-8"), str(user["password"]).encode("utf-8")):
        return jsonify({"error": "Password salah"}), 401

    user_id = int(user["id"])
    role = str(user["role"])

    # Buat token dengan masa berlaku (1 jam default)
    token = generate_token(user_id, role, expires_hours=1)

    # Simpan session tambahan untuk keamanan (opsional)
    session["token"] = token
    session["user_id"] = user_id
    session["login_time"] = datetime.utcnow().isoformat()

    return jsonify({"token": token, "role": role}), 200


# === APPROVAL SUPERADMIN ===
def approve_user(user_id):
    df = _read_users_df()
    if int(user_id) not in df["id"].astype(int).values:
        return jsonify({"error": "User tidak ditemukan"}), 404

    df.loc[df["id"].astype(int) == int(user_id), "status_approval"] = 1
    df.to_csv(USERPATH, index=False)
    return jsonify({"success": f"User dengan ID {int(user_id)} berhasil di-approve."}), 200


# === LOGOUT (clear session) ===
def logout_user():
    session.clear()
    return jsonify({"success": "Logout berhasil"}), 200
