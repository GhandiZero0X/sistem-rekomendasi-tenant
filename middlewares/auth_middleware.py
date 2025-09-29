# middlewares/auth_middleware.py
from functools import wraps
from flask import request, jsonify
from utils.jwt_utils import decode_token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]

        if not token:
            return jsonify({"error": "Token tidak ditemukan"}), 401

        data = decode_token(token)
        if "error" in data:
            return jsonify(data), 401

        request.user = data
        return f(*args, **kwargs)
    return decorated

def role_required(roles):
    """Cek role (superadmin/admin)"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = getattr(request, "user", None)
            if not user or user.get("role") not in roles:
                return jsonify({"error": "Tidak punya akses"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
