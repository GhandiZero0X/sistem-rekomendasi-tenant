# controllers/authController.py
import os
import pandas as pd
import bcrypt
from flask import request, jsonify
from utils.jwt_utils import generate_token

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data")
USERPATH = os.path.join(DATA_DIR, "users.csv")

# register akun admin
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username & password wajib diisi"}), 400

    if os.path.exists(USERPATH):
        df = pd.read_csv(USERPATH)
        if username in df["username"].values:
            return jsonify({"error": "Username sudah terdaftar"}), 400
    else:
        df = pd.DataFrame(columns=["id", "username", "password", "status_approval", "role"])

    # hash password
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    next_id = 1 if df.empty else df["id"].max() + 1
    new_user = {
        "id": next_id,
        "username": username,
        "password": hashed_pw,
        "status_approval": 0,   # default belum di-approve
        "role": "admin"         # default role = admin
    }

    df = pd.concat([df, pd.DataFrame([new_user])], ignore_index=True)
    df.to_csv(USERPATH, index=False)

    return jsonify({"success": f"User {username} berhasil registrasi, menunggu approval superadmin."})

# login akun admin/superadmin
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not os.path.exists(USERPATH):
        return jsonify({"error": "Belum ada user terdaftar"}), 400

    df = pd.read_csv(USERPATH)
    user = df[df["username"] == username]

    if user.empty:
        return jsonify({"error": "User tidak ditemukan"}), 404

    user = user.iloc[0]

    if not bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
        return jsonify({"error": "Password salah"}), 400

    if int(user["status_approval"]) == 0:
        return jsonify({"error": "Akun belum di-approve superadmin"}), 403

    token = generate_token(user["id"], user["role"])
    return jsonify({"token": token, "role": user["role"]})

# Approval akun admin oleh superadmin
def approve_user(user_id):
    if not os.path.exists(USERPATH):
        return jsonify({"error": "User database tidak ditemukan"}), 400

    df = pd.read_csv(USERPATH)
    if user_id not in df["id"].values:
        return jsonify({"error": "User tidak ditemukan"}), 404

    df.loc[df["id"] == user_id, "status_approval"] = 1
    df.to_csv(USERPATH, index=False)

    return jsonify({"success": f"User dengan id {user_id} berhasil di-approve."})
