"""Recordatorios y pantalla principal (admin)."""
from datetime import datetime, timedelta

from flask import Blueprint, redirect, render_template, request, session, url_for

from extensions import mysql
from utils import ZONA_HORARIA, ahora, login_required, registrar_traza

reminders_bp = Blueprint("reminders", __name__)


def _parsear_fecha_hora(fecha, hora):
    """'YYYY-MM-DD', 'HH:MM' -> (y, mm, d, h, m) como enteros."""
    y, mm, d = (int(p) for p in fecha.split("-"))
    h, m = (int(p) for p in hora.split(":")[:2])
    return y, mm, d, h, m


def _clasificar(filas, now):
    """Separa los recordatorios de los próximos 7 días en hoy / mañana / otros,
    cada grupo ordenado por fecha."""
    grupos = {"hoy": [], "manana": [], "otros": []}
    for fila in filas:
        _, y, mm, d, h, m = fila
        fecha = ZONA_HORARIA.localize(datetime(int(y), int(mm), int(d), int(h), int(m)))
        diferencia = fecha - now
        if diferencia < timedelta(0) or diferencia > timedelta(days=7):
            continue
        if fecha.day == now.day:
            clave = "hoy"
        elif diferencia < timedelta(hours=24):
            clave = "manana"
        else:
            clave = "otros"
        grupos[clave].append((fecha, fila))

    return [
        [fila for _, fila in sorted(grupos[k], key=lambda par: par[0])]
        for k in ("hoy", "manana", "otros")
    ]


@reminders_bp.route("/admin")
@login_required
def admin():
    now = ahora()

    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT nombreRecordatorio, y, mm, d, h, m FROM recordatorios WHERE idUsuario = %s",
        (session["idUsuario"],),
    )
    filas = [
        [r["nombreRecordatorio"], r["y"], r["mm"], r["d"], r["h"], r["m"]]
        for r in cur.fetchall()
    ]
    cur.close()

    hoy, manana, otros = _clasificar(filas, now)

    return render_template(
        "admin.html",
        username=session["nombre"],
        currentTimeList=tuple(now.strftime("%Y-%m-%d-%H-%M").split("-")),
        nombreRecordatorioList=[f[0] for f in filas],
        yearList=[f[1] for f in filas],
        monthList=[f[2] for f in filas],
        dayList=[f[3] for f in filas],
        hourList=[f[4] for f in filas],
        minuteList=[f[5] for f in filas],
        todayReminders=hoy,
        tomorrowReminders=manana,
        otherReminders=otros,
    )


@reminders_bp.route("/remindAdd", methods=["POST"])
@login_required
def addRemind():
    nombre = request.form["nameRemind"]
    y, mm, d, h, m = _parsear_fecha_hora(
        request.form["dateRemind"], request.form["timeRemind"]
    )

    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO recordatorios (idUsuario, nombreRecordatorio, y, mm, d, h, m) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (session["idUsuario"], nombre, y, mm, d, h, m),
    )
    registrar_traza(cur, "Recordatorio", "Ha añadido un recordatorio")
    mysql.connection.commit()
    cur.close()

    return redirect(url_for("reminders.admin"))


@reminders_bp.route("/remindRemove", methods=["GET", "POST"])
@login_required
def removeRemind():
    a = request.args
    cur = mysql.connection.cursor()
    cur.execute(
        "DELETE FROM recordatorios WHERE nombreRecordatorio = %s AND y = %s AND mm = %s "
        "AND d = %s AND h = %s AND m = %s AND idUsuario = %s",
        (
            a.get("remindSTR"),
            a.get("yearSTR"),
            a.get("monthSTR"),
            a.get("daySTR"),
            a.get("hourSTR"),
            a.get("minuteSTR"),
            session["idUsuario"],
        ),
    )
    registrar_traza(cur, "Recordatorio", "Ha Eliminado un recordatorio")
    mysql.connection.commit()
    cur.close()

    return redirect(url_for("reminders.admin"))


@reminders_bp.route("/remindEdit", methods=["POST"])
@login_required
def editRemind():
    f = request.form
    y, mm, d, h, m = _parsear_fecha_hora(f["dateRemind"], f["timeRemind"])

    # Un solo UPDATE (antes: SELECT del id + UPDATE). LIMIT 1 conserva el
    # comportamiento anterior de editar solo el primer recordatorio coincidente.
    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE recordatorios SET nombreRecordatorio = %s, y = %s, mm = %s, d = %s, h = %s, m = %s "
        "WHERE nombreRecordatorio = %s AND y = %s AND mm = %s AND d = %s AND h = %s AND m = %s "
        "AND idUsuario = %s LIMIT 1",
        (
            f["nameRemind"], y, mm, d, h, m,
            f["remindSTR"], f["yearSTR"], f["monthSTR"], f["daySTR"], f["hourSTR"], f["minuteSTR"],
            session["idUsuario"],
        ),
    )
    registrar_traza(cur, "Recordatorio", "Ha editado un recordatorio")
    mysql.connection.commit()
    cur.close()

    return redirect(url_for("reminders.admin"))
