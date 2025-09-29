import jwt
import datetime

SECRET_KEY = "supersecretkey123"  # ganti ke env var biar aman
ALGORITHM = "HS256"

def generate_token(user_id, role):
    """Generate JWT token dengan expiry 1 jam"""
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token):
    """Decode JWT token"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        return {"error": "Token expired"}
    except jwt.InvalidTokenError:
        return {"error": "Token invalid"}
