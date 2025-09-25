# app.py
from flask import Flask
from routes.routes import routes
from services.watcher import start_watcher
import atexit

def create_app():
    app = Flask(__name__)
    app.register_blueprint(routes)

    # Mulai watcher
    observer = start_watcher()

    # Stop watcher pas app mati
    atexit.register(lambda: observer.stop() or observer.join())

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
