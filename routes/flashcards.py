"""Tarjetas didácticas (flashcards)."""
from flask import Blueprint, redirect, render_template, request, session, url_for

from extensions import mysql
from utils import login_required, registrar_traza

flashcards_bp = Blueprint("flashcards", __name__)

SERVICIO = "Tarjetas Didácticas"


def _insertar_tarjeta(cur, mazo, pregunta, respuesta):
    cur.execute(
        "INSERT INTO flashcards (id_Usuario, nombreMazo, pista, respuesta, dia, mes, año) "
        "VALUES (%s, %s, %s, %s, 0, 0, 0)",
        (session["idUsuario"], mazo, pregunta, respuesta),
    )


@flashcards_bp.route("/flashcards", methods=["GET", "POST"])
@login_required
def flashcards():
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT nombreMazo, pista, respuesta, dia, mes, año FROM flashcards WHERE id_Usuario = %s",
        (session["idUsuario"],),
    )
    tarjetas = [list(fila.values()) for fila in cur.fetchall()]
    cur.close()

    return render_template("flashcards.html", flashcards=tarjetas)


@flashcards_bp.route("/newDeck", methods=["GET", "POST"])
@login_required
def newDeck():
    mazo = request.form["nameDeck"]

    cur = mysql.connection.cursor()
    _insertar_tarjeta(
        cur, mazo, request.form["questionFirstCard"], request.form["answerFirstCard"]
    )
    registrar_traza(cur, SERVICIO, "Ha creado el mazo " + mazo)
    mysql.connection.commit()
    cur.close()

    return redirect(url_for("flashcards.flashcards"))


@flashcards_bp.route("/cardAdd", methods=["GET", "POST"])
@login_required
def addCard():
    mazo = request.form["nameDeckAdd"]

    cur = mysql.connection.cursor()
    _insertar_tarjeta(cur, mazo, request.form["questionCard"], request.form["answerCard"])
    registrar_traza(cur, SERVICIO, "Ha creado una tarjeta para el mazo " + mazo)
    mysql.connection.commit()
    cur.close()

    return redirect(url_for("flashcards.flashcards"))


@flashcards_bp.route("/deleteFlashcard", methods=["GET", "POST"])
@login_required
def deleteFlashcard():
    mazo = request.args.get("nombreMazo")

    cur = mysql.connection.cursor()
    cur.execute(
        "DELETE FROM flashcards WHERE nombreMazo = %s AND pista = %s AND id_Usuario = %s",
        (mazo, request.args.get("pregunta"), session["idUsuario"]),
    )
    registrar_traza(cur, SERVICIO, "Ha borrado una tarjeta del mazo " + mazo)
    mysql.connection.commit()
    cur.close()

    return redirect(url_for("flashcards.flashcards"))


@flashcards_bp.route("/editFlashcard", methods=["GET", "POST"])
@login_required
def editFlashcard():
    f = request.form
    mazo = f["nameDeck1"]

    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE flashcards SET pista = %s, respuesta = %s "
        "WHERE nombreMazo = %s AND pista = %s AND respuesta = %s AND id_Usuario = %s",
        (
            f["questionFirstCard"],
            f["answerFirstCard"],
            mazo,
            f["questionFirstCard1"],
            f["answerFirstCard1"],
            session["idUsuario"],
        ),
    )
    registrar_traza(cur, SERVICIO, "Ha editado una tarjeta del mazo " + mazo)
    mysql.connection.commit()
    cur.close()

    return redirect(url_for("flashcards.flashcards"))


@flashcards_bp.route("/saveStudyDate", methods=["POST"])
@login_required
def saveStudyDate():
    dia, mes, anio = request.args.get("date").split("/")

    cur = mysql.connection.cursor()
    # Se filtra también por usuario: antes se actualizaban los mazos con ese
    # nombre de TODOS los usuarios.
    cur.execute(
        "UPDATE flashcards SET dia = %s, mes = %s, año = %s "
        "WHERE nombreMazo = %s AND id_Usuario = %s",
        (dia, mes, anio, request.args.get("deck"), session["idUsuario"]),
    )
    mysql.connection.commit()
    cur.close()

    return "Fecha y mazo recibidos correctamente"
