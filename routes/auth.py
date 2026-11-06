"""Inicio, login, registro, logout y recuperación de contraseña."""
from datetime import timedelta

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_mail import Message
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import mail, mysql
from utils import ZONA_HORARIA, ahora, generar_token, registrar_traza

auth_bp = Blueprint("auth", __name__)

VALIDEZ_TOKEN = timedelta(hours=1)


@auth_bp.route("/")
def homepage():
    return render_template("index.html")


@auth_bp.route("/loginAccess", methods=["GET", "POST"])
def login():
    if (
        request.method == "POST"
        and "txtEmail" in request.form
        and "txtPassword" in request.form
    ):
        correo = request.form["txtEmail"]
        contrasena = request.form["txtPassword"]

        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT idUsuario, nombre, contrasena FROM usuario WHERE correo = %s",
            (correo,),
        )
        cuenta = cur.fetchone()

        if cuenta and check_password_hash(cuenta["contrasena"], contrasena):
            session["logueado"] = True
            session["idUsuario"] = cuenta["idUsuario"]
            session["nombre"] = cuenta["nombre"]

            registrar_traza(cur, "Login", "Ha iniciado sesión")
            mysql.connection.commit()
            cur.close()
            return redirect(url_for("reminders.admin"))

        cur.close()
        return render_template("index.html", error_message="Credenciales incorrectas")

    return redirect(url_for("auth.homepage"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if (
        request.method == "POST"
        and "txtEmail" in request.form
        and "txtPassword" in request.form
    ):
        correo = request.form["txtEmail"]
        contrasena = request.form["txtPassword"]
        nombre = request.form["txtNombre"]

        cur = mysql.connection.cursor()
        cur.execute("SELECT 1 FROM usuario WHERE correo = %s", (correo,))
        if cur.fetchone():
            cur.close()
            return render_template(
                "register.html", error_message="El correo ya está en uso"
            )

        cur.execute(
            "INSERT INTO usuario (nombre, correo, contrasena) VALUES (%s, %s, %s)",
            (nombre, correo, generate_password_hash(contrasena)),
        )
        id_usuario = cur.lastrowid

        session["logueado"] = True
        session["idUsuario"] = id_usuario
        session["nombre"] = nombre

        registrar_traza(cur, "Login", "Se ha Registrado Exitosamente", id_usuario, nombre)
        mysql.connection.commit()
        cur.close()

        return redirect("/")

    return render_template("register.html")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("auth.homepage"))


@auth_bp.route("/recuperacion", methods=["GET", "POST"])
def recuperacion():
    if request.method == "POST":
        destinatario = request.form["recipient"]
        token = generar_token()
        creado = ahora()

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO password_reset_tokens (email, token, created_at, expiration) "
            "VALUES (%s, %s, %s, %s)",
            (destinatario, token, creado, creado + VALIDEZ_TOKEN),
        )
        mysql.connection.commit()
        cur.close()

        enlace = url_for("auth.reset_password", token=token, _external=True)
        msg = Message("Recuperación de contraseña", recipients=[destinatario])
        msg.body = f"Utilice este enlace para restablecer su contraseña: {enlace}"
        mail.send(msg)

        flash("Se ha enviado un enlace de recuperación por correo electrónico.", "success")

    return render_template("recuperacion.html")


@auth_bp.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    token = request.args.get("token")

    if token is None:
        flash("Token no encontrado en la URL.", "danger")
        return render_template("reset.html", data=None)

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM password_reset_tokens WHERE token = %s", (token,))
    data = cur.fetchone()

    if data is None:
        cur.close()
        flash(
            f"Token no válido: {token}. Por favor, solicita otro enlace de recuperación.",
            "danger",
        )
        return render_template("reset.html", data=None)

    if ahora() > ZONA_HORARIA.localize(data["created_at"] + VALIDEZ_TOKEN):
        cur.close()
        flash(
            "El token ha caducado. Por favor, solicita otro enlace de recuperación.",
            "danger",
        )
        return render_template("reset.html", data=data)

    if request.method == "POST":
        nueva = request.form.get("new_password")
        cur.execute(
            "UPDATE usuario SET contrasena = %s WHERE correo = %s",
            (generate_password_hash(nueva), data["email"]),
        )
        mysql.connection.commit()
        cur.close()
        return redirect("/")

    cur.close()
    return render_template("reset.html", data=data)
