"""Configuración de la aplicación."""
import os


class Config:
    # En producción define SECRET_KEY_UNAGENDA; el valor por defecto es solo para desarrollo.
    SECRET_KEY = os.environ.get("SECRET_KEY_UNAGENDA", "prFlask")

    # MySQL (local)
    MYSQL_HOST = "localhost"
    MYSQL_USER = "root"
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD_UNAGENDA")
    MYSQL_DB = "prflask"
    MYSQL_CURSORCLASS = "DictCursor"

    # Flask-Mail
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = "unagenda.of@gmail.com"
    MAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD_UNAGENDA")
    MAIL_DEFAULT_SENDER = "unagenda.of@gmail.com"
