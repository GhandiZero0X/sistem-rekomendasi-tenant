# utils/jwt_utils.py
import jwt
import datetime
import os
from dotenv import load_dotenv
from jwt import ExpiredSignatureError, InvalidTokenError

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")  # gunakan env di prod
ALGORITHM = "HS256"

def generate_token(user_id: int, role: str, expires_hours: int = 1) -> str:
    """Generate JWT dengan masa berlaku tertentu (default: 1 jam)"""
    payload = {
        "user_id": int(user_id),
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=expires_hours),
        "iat": datetime.datetime.utcnow(),  # issued at
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token if isinstance(token, str) else token.decode("utf-8")

def decode_token(token: str):
    """Decode dan validasi token"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        return {"error": "Token expired"}
    except InvalidTokenError:
        return {"error": "Token invalid"}
    except Exception as e:
        return {"error": f"Token decode error: {str(e)}"}
