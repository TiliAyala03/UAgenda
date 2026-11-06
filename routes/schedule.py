"""Horario semanal."""
from flask import Blueprint, redirect, render_template, request, session, url_for

from extensions import mysql
from utils import login_required, registrar_traza

schedule_bp = Blueprint("schedule", __name__)

DIAS = {
    "LUNES": 1,
    "MARTES": 2,
    "MIÉRCOLES": 3,
    "JUEVES": 4,
    "VIERNES": 5,
    "SÁBADO": 6,
    "DOMINGO": 7,
}


def _numero_dia(texto):
    return DIAS.get((texto or "").strip().upper(), 0)


def _render_horario(**extra):
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT evento, horaInicio, horaFin, diaSemana FROM horario WHERE idUsuario = %s",
        (session["idUsuario"],),
    )
    filas = cur.fetchall()
    cur.close()

    contexto = {
        "eventosList": [f["evento"] for f in filas],
        "horaInicioList": [f["horaInicio"] for f in filas],
        "horaFinList": [f["horaFin"] for f in filas],
        "diaSemanaList": [f["diaSemana"] for f in filas],
        "editEvent": 0,
    }
    contexto.update(extra)
    return render_template("schedule.html", **contexto)


def _borrar_evento(cur):
    """Borra el evento indicado en los argumentos de la URL. Devuelve (nombre, día)."""
    evento = request.args.get("eventoSTR")
    dia = _numero_dia(request.args.get("diaSTR"))
    cur.execute(
        "DELETE FROM horario WHERE evento = %s AND horaInicio = %s AND diaSemana = %s AND idUsuario = %s",
        (evento, request.args.get("horaInicioSTR"), dia, session["idUsuario"]),
    )
    return evento, dia


@schedule_bp.route("/schedule")
@login_required
def schedule():
    return _render_horario()


@schedule_bp.route("/eventAdd", methods=["POST"])
@login_required
def addEvent():
    nombre = request.form["nombreEvento"]

    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO horario (idUsuario, evento, horaInicio, horaFin, diaSemana) "
        "VALUES (%s, %s, %s, %s, %s)",
        (
            session["idUsuario"],
            nombre,
            request.form["horaInicio"],
            request.form["horaFin"],
            request.form["diaSemanal"],
        ),
    )

    # La bandera vive en la sesión (antes era una global compartida por todos los usuarios).
    accion = "editado" if session.pop("horario_editando", False) else "creado"
    registrar_traza(cur, "Horario", f"Ha {accion} el evento {nombre}")
    mysql.connection.commit()
    cur.close()

    return redirect(url_for("schedule.schedule"))


@schedule_bp.route("/eventRemove", methods=["GET", "POST"])
@login_required
def removeEvent():
    cur = mysql.connection.cursor()
    evento, _ = _borrar_evento(cur)
    registrar_traza(cur, "Horario", f"Ha eliminado el evento {evento}")
    mysql.connection.commit()
    cur.close()

    return redirect(url_for("schedule.schedule"))


@schedule_bp.route("/eventRemove2", methods=["GET", "POST"])
@login_required
def removeEvent2():
    """Borra el evento y abre el formulario en modo edición (sin traza: la traza
    se registra como 'editado' cuando se vuelve a guardar en /eventAdd)."""
    cur = mysql.connection.cursor()
    evento, dia = _borrar_evento(cur)
    mysql.connection.commit()
    cur.close()

    session["horario_editando"] = True
    return _render_horario(editEvent=1, editEventName=evento, editEventDay=dia)
