"""Consulta de la traza de actividad."""
from flask import Blueprint, jsonify, render_template, request

from extensions import mysql

traza_bp = Blueprint("traza", __name__)


@traza_bp.route("/traza")
def traza():
    return render_template("traza.html")


@traza_bp.route("/trazaSelect", methods=["POST"])
def trazaSelect():
    servicio = request.json.get("serviceSelected")

    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT Nombre, Descripcion, Hora, Servicio FROM Traza WHERE Servicio = %s",
        (servicio,),
    )
    filas = [list(fila.values()) for fila in cur.fetchall()]
    cur.close()

    return jsonify(filas)
