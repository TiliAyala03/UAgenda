"""Extensiones de Flask, creadas sin app para evitar imports circulares.
Se enlazan con la app en main.create_app()."""
from flask_mail import Mail
from flask_mysqldb import MySQL

mysql = MySQL()
mail = Mail()
