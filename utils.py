"""Utilidades compartidas por todos los módulos."""
import secrets
import string
from datetime import datetime
from functools import wraps

import pytz
from flask import redirect, session, url_for

ZONA_HORARIA = pytz.timezone("America/Bogota")
_ALFABETO_TOKEN = string.ascii_letters + string.digits


def ahora():
    """Fecha y hora actuales en zona horaria de Colombia."""
    return datetime.now(ZONA_HORARIA)


def login_required(f):
    @wraps(f)
    def decorada(*args, **kwargs):
        if "nombre" not in session or "idUsuario" not in session:
            return redirect(url_for("auth.homepage"))
        return f(*args, **kwargs)

    return decorada


def registrar_traza(cur, servicio, descripcion, id_usuario=None, nombre=None):
    """Inserta una fila en la tabla Traza usando el usuario de la sesión
    (o el indicado). NO hace commit: lo hace quien llama, junto con su operación."""
    if id_usuario is None:
        id_usuario = session["idUsuario"]
    if nombre is None:
        nombre = session["nombre"]
    cur.execute(
        "INSERT INTO Traza (id_Usuario, nombre, descripcion, hora, servicio) "
        "VALUES (%s, %s, %s, %s, %s)",
        (id_usuario, nombre, descripcion, ahora().strftime("%Y-%m-%d %H:%M:%S"), servicio),
    )


def generar_token(longitud=32):
    return "".join(secrets.choice(_ALFABETO_TOKEN) for _ in range(longitud))
