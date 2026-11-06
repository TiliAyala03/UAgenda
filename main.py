"""Punto de entrada de UnAgenda."""
import os

from flask import Flask

from config import Config
from extensions import mail, mysql
from routes import registrar_blueprints


def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(Config)

    mysql.init_app(app)
    mail.init_app(app)
    registrar_blueprints(app)

    return app


app = create_app()

if __name__ == "__main__":
    # El modo debug expone el depurador de Werkzeug: actívalo solo en local
    # con FLASK_DEBUG=1.
    app.run(
        debug=os.environ.get("FLASK_DEBUG") == "1",
        host="0.0.0.0",
        port=5000,
        threaded=True,
    )
