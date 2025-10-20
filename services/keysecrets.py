import secrets

print("FLASK_SECRET_KEY =", secrets.token_urlsafe(64))
print("JWT_SECRET_KEY   =", secrets.token_urlsafe(64))
