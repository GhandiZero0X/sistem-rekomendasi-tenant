# app.py
from flask import Flask
from routes.routes import routes
from services.watcher import start_watcher
from flask_talisman import Talisman
from dotenv import load_dotenv
import atexit
import sys
import os

# === Load environment variables ===
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

def create_app():
    app = Flask(__name__)

    # === Secret key dari .env ===
    app.secret_key = os.getenv("FLASK_SECRET_KEY")

    # === Flask-Talisman untuk keamanan HTTP headers ===
    # Kamu bisa custom Content Security Policy (CSP) sesuai kebutuhan
    # csp = {
    #     'default-src': [
    #         "'self'",
    #         "https://cdn.jsdelivr.net",   # kalau kamu pakai js/css CDN
    #         "https://cdnjs.cloudflare.com",
    #     ],
    #     'img-src': [
    #         "'self'",
    #         "data:",                       # izinkan inline image base64
    #         "https://*",
    #     ],
    #     'script-src': [
    #         "'self'",
    #         "'unsafe-inline'",              # opsional, untuk inline JS sementara
    #         "https://cdn.jsdelivr.net",
    #         "https://cdnjs.cloudflare.com",
    #     ],
    #     'style-src': [
    #         "'self'",
    #         "'unsafe-inline'",              # supaya inline CSS gak ke-block
    #         "https://cdn.jsdelivr.net",
    #         "https://fonts.googleapis.com",
    #     ],
    #     'font-src': [
    #         "'self'",
    #         "https://fonts.gstatic.com",
    #     ],
    # }

    # # Terapkan Talisman
    # Talisman(
    #     app,
    #     content_security_policy=csp,
    #     force_https=False,  # ubah ke True kalau nanti udah pakai HTTPS
    #     session_cookie_secure=True,
    #     session_cookie_http_only=True,
    #     session_cookie_samesite="Lax"
    # )

    # === Daftarkan blueprint routes ===
    app.register_blueprint(routes)

    # === Jalankan file watcher ===
    observer = start_watcher()
    atexit.register(lambda: observer.stop() or observer.join())

    return app


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "False") == "True"
    app = create_app()

    # app.run(host="0.0.0.0", port=5000, debug=debug_mode) # jalankan di jaringan lokal dan ip public

    # Jalankan di localhost (aman dari bandit B104)
    app.run(host="127.0.0.1", port=5000, debug=debug_mode)
