"""Cuadernos de apuntes."""
from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for

from extensions import mysql
from utils import login_required, registrar_traza

notebook_bp = Blueprint("notebook", __name__)


def _modo_oscuro():
    # Antes era una variable global compartida por todos los usuarios.
    return session.get("dark_mode", False)


def _decodificar_contenido(contenido):
    """Revierte la codificación que aplica el JavaScript del cliente."""
    return (
        contenido.replace(",", "\n")
        .replace("5hjis6754", "&")
        .replace("5hjdf4754", ",")
    )


def _abrir_o_crear_cuaderno(nombre):
    uid = session["idUsuario"]
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * FROM cuaderno WHERE id_usuario = %s AND nombreCuaderno = %s LIMIT 1",
        (uid, nombre),
    )
    cuaderno = cur.fetchone()

    if cuaderno is None:
        cur.execute(
            "INSERT INTO cuaderno (id_usuario, nombreCuaderno, contenido, modoOscuro) "
            "VALUES (%s, %s, %s, %s)",
            (uid, nombre, "Tus Nuevos Apuntes...", 0),
        )
        registrar_traza(cur, "Cuaderno", f"Ha creado el cuaderno {nombre}")
        mysql.connection.commit()
        cur.execute("SELECT * FROM cuaderno WHERE id_cuaderno = %s", (cur.lastrowid,))
        cuaderno = cur.fetchone()

    cur.close()
    return render_template("cuaderno.html", dark_mode=_modo_oscuro(), cuaderno=cuaderno)


@notebook_bp.route("/cuaderno", methods=["GET", "POST"])
@login_required
def cuaderno():
    if request.method == "POST":
        return _abrir_o_crear_cuaderno(request.form["nombreCuaderno"])

    uid = session["idUsuario"]
    contenido = request.args.get("contenido")
    id_cuaderno = request.args.get("id")
    nombre = request.args.get("nombre")
    borrar = request.args.get("borrar")

    cur = mysql.connection.cursor()

    if contenido is not None and id_cuaderno is not None and nombre is not None and borrar is None:
        contenido = _decodificar_contenido(contenido)
        cur.execute(
            "SELECT 1 FROM cuaderno WHERE id_usuario = %s AND id_cuaderno = %s AND nombreCuaderno = %s",
            (uid, id_cuaderno, nombre),
        )
        if cur.fetchone():
            cur.execute(
                "UPDATE cuaderno SET contenido = %s "
                "WHERE id_usuario = %s AND id_cuaderno = %s AND nombreCuaderno = %s",
                (contenido, uid, id_cuaderno, nombre),
            )
            registrar_traza(cur, "Cuaderno", f"Ha editado el cuaderno {nombre}")
        else:
            cur.execute(
                "INSERT INTO cuaderno (id_usuario, nombreCuaderno, contenido, modoOscuro) "
                "VALUES (%s, %s, %s, %s)",
                (uid, nombre, contenido, 0),
            )
        mysql.connection.commit()

    elif id_cuaderno is not None and nombre is not None and borrar is not None:
        cur.execute(
            "DELETE FROM cuaderno WHERE id_usuario = %s AND id_cuaderno = %s AND nombreCuaderno = %s",
            (uid, id_cuaderno, nombre),
        )
        registrar_traza(cur, "Cuaderno", f"Ha eliminado el cuaderno {nombre}")
        mysql.connection.commit()

    # Solo se muestra el primer cuaderno; el resto lo carga el cliente vía /obtener_cuadernos.
    cur.execute(
        "SELECT * FROM cuaderno WHERE id_usuario = %s ORDER BY id_cuaderno LIMIT 1", (uid,)
    )
    actual = cur.fetchone() or {"contenido": ""}
    cur.close()

    return render_template("cuaderno.html", dark_mode=_modo_oscuro(), cuaderno=actual)


@notebook_bp.route("/obtener_cuadernos", methods=["GET"])
@login_required
def obtener_cuadernos():
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT nombreCuaderno, contenido, id_cuaderno FROM cuaderno WHERE id_usuario = %s",
        (session["idUsuario"],),
    )
    cuadernos = cur.fetchall()

    registrar_traza(cur, "Cuaderno", "Ha cambiado de cuaderno")
    mysql.connection.commit()
    cur.close()

    return jsonify(
        [
            {
                "nombreCuaderno": c["nombreCuaderno"],
                "contenido": c["contenido"],
                "id_cuaderno": c["id_cuaderno"],
            }
            for c in cuadernos
        ]
    )


@notebook_bp.route("/toggle_dark_mode")
@login_required
def toggle_dark_mode():
    session["dark_mode"] = not _modo_oscuro()
    return redirect(url_for("notebook.cuaderno"))


@notebook_bp.route("/actualizar_modo_oscuro", methods=["POST"])
@login_required
def actualizar_modo_oscuro():
    modo_oscuro = request.get_json().get("modoOscuro")

    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE cuaderno SET modoOscuro = %s WHERE id_usuario = %s",
        (modo_oscuro, session["idUsuario"]),
    )
    mysql.connection.commit()
    cur.close()

    return jsonify({"message": "Modo oscuro actualizado con éxito"})
