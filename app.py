from flask import Flask
from routes.routes import routes
from services.watcher import start_watcher
from dotenv import load_dotenv
import atexit
import os

load_dotenv()

def create_app():
    app = Flask(__name__)

    #secret key
    app.secret_key = os.getenv("FLASK_SECRET_KEY")

    app.register_blueprint(routes)

    # Mulai watcher
    observer = start_watcher()

    # Stop watcher pas app mati
    atexit.register(lambda: observer.stop() or observer.join())

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
