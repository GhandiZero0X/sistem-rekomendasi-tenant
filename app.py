# app.py
from flask import Flask
from routes.routes import routes
from services.watcher import start_watcher
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

    # === Daftarkan blueprint routes ===
    app.register_blueprint(routes)

    # === Jalankan file watcher ===
    observer = start_watcher()
    atexit.register(lambda: observer.stop() or observer.join())

    return app


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "False") == "True"
    app = create_app()

    app.run(host="0.0.0.0", port=5000, debug=debug_mode) # jalankan di jaringan lokal dan ip public

    # Jalankan di localhost (aman dari bandit B104)
    # app.run(host="127.0.0.1", port=5000, debug=debug_mode)
