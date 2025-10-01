# utils/jwt_utils.py
import jwt
import datetime
from jwt import ExpiredSignatureError, InvalidTokenError

SECRET_KEY = "supersecretkey123"  # pindahkan ke env var di production
ALGORITHM = "HS256"

def generate_token(user_id: int, role: str, expires_hours: int = 1) -> str:
    payload = {
        "user_id": int(user_id),
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=expires_hours)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    # PyJWT >=2.0 returns a str, but ensure string:
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        return {"error": "Token expired"}
    except InvalidTokenError:
        return {"error": "Token invalid"}
    except Exception as e:
        return {"error": f"Token decode error: {str(e)}"}
