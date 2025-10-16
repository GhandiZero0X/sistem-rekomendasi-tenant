from functools import wraps
from flask import request, jsonify, session, redirect, url_for
from utils.jwt_utils import decode_token

def token_required(f):
    """
    Middleware untuk memastikan user sudah login.
    Bisa baca token dari Authorization header ATAU session Flask.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # 1️⃣ Ambil token dari header Authorization
        auth_header = request.headers.get("Authorization")

        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]
            else:
                token = auth_header.strip()
        else:
            # 2️⃣ Kalau gak ada header, ambil token dari session Flask
            token = session.get("token")

        # 3️⃣ Kalau token gak ditemukan → redirect ke login
        if not token:
            # Kalau request dari API (JSON), kirim error JSON
            if request.path.startswith("/api") or request.is_json:
                return jsonify({"error": "Authorization header missing"}), 401
            # Kalau dari halaman web → redirect ke login
            return redirect(url_for("routes.login_page"))

        # 4️⃣ Decode token JWT
        data = decode_token(token)
        if "error" in data:
            session.clear()  # hapus session biar gak nyangkut
            # kalau token invalid/expired, arahkan ke login
            if request.path.startswith("/api") or request.is_json:
                return jsonify(data), 401
            return redirect(url_for("routes.login_page"))

        # 5️⃣ Simpan user info ke request
        request.user = data
        return f(*args, **kwargs)

    return decorated


def role_required(required_role):
    """
    Middleware untuk validasi role user (bisa single atau list).
    Contoh:
    @role_required("superadmin")
    @role_required(["admin", "superadmin"])
    """
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = getattr(request, "user", None)
            if not user:
                return jsonify({"error": "Authentication required"}), 401

            user_role = str(user.get("role", "")).lower()

            # 🔹 Bisa handle list atau string
            if isinstance(required_role, list):
                allowed_roles = [r.lower() for r in required_role]
                if user_role not in allowed_roles:
                    return jsonify({
                        "error": f"Forbidden: role {required_role} required"
                    }), 403
            else:
                if user_role != str(required_role).lower():
                    return jsonify({
                        "error": f"Forbidden: role '{required_role}' required"
                    }), 403

            return f(*args, **kwargs)
        return decorated
    return wrapper
