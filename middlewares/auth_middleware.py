# middlewares/auth_middleware.py
from functools import wraps
from flask import request, jsonify
from utils.jwt_utils import decode_token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"error": "Authorization header missing"}), 401

        # kalau format ada "Bearer <token>" → ambil tokennya
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
        else:
            # kalau tidak ada "Bearer", anggap value langsung token mentah
            token = auth_header.strip()

        data = decode_token(token)
        if "error" in data:
            return jsonify(data), 401

        request.user = data
        return f(*args, **kwargs)
    return decorated

def role_required(required_role):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = getattr(request, "user", None)
            if not user:
                return jsonify({"error": "Authentication required"}), 401
            # normalize roles to string and check
            user_role = str(user.get("role", "")).lower()
            if user_role != str(required_role).lower():
                return jsonify({"error": "Forbidden: role '{}' required".format(required_role)}), 403
            return f(*args, **kwargs)
        return decorated
    return wrapper
