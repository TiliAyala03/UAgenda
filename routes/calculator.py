"""Calculadora de notas por grupos con porcentaje."""
from flask import Blueprint, abort, render_template, request, session

from extensions import mysql
from utils import login_required, registrar_traza

calculator_bp = Blueprint("calculator", __name__)


# ---------- helpers de validación ----------
def _entero(valor):
    try:
        return int(valor)
    except (TypeError, ValueError):
        abort(400)


def _numero(valor):
    try:
        return float(valor)
    except (TypeError, ValueError):
        abort(400)


def _hay(valor):
    return valor is not None and valor != "None"


# ---------- helpers de base de datos (todo parametrizado) ----------
def _borrar_nota(db, uid, id_nota):
    db.execute(
        "DELETE FROM grupoNotas WHERE idNota = %s AND idUsuario = %s", (id_nota, uid)
    )


def _borrar_grupo(db, uid, num_grupo):
    db.execute(
        "DELETE FROM grupoNotas WHERE numGrupo = %s AND idUsuario = %s", (num_grupo, uid)
    )


def _actualizar_porcentaje(db, uid, num_grupo, porcentaje):
    db.execute(
        "UPDATE grupoNotas SET porcentaje = %s WHERE numGrupo = %s AND idUsuario = %s",
        (_numero(porcentaje), num_grupo, uid),
    )


def _insertar_nota(db, uid, num_grupo, porcentaje, nota):
    db.execute(
        "INSERT INTO grupoNotas (idUsuario, numGrupo, porcentaje, nota) VALUES (%s, %s, %s, %s)",
        (uid, _entero(num_grupo), _numero(porcentaje), _numero(nota)),
    )


def _reacomodar_grupos(db, uid, grupo_borrado, total, id_updt, n_perc):
    """Tras borrar un grupo, baja en 1 el número de los grupos siguientes y
    actualiza el porcentaje del grupo indicado. Devuelve True si hubo desplazamiento."""
    desplazo = grupo_borrado < total - 1
    if desplazo:
        # Un solo UPDATE en lugar de un bucle de UPDATE + commit por grupo.
        db.execute(
            "UPDATE grupoNotas SET numGrupo = numGrupo - 1 "
            "WHERE idUsuario = %s AND numGrupo BETWEEN %s AND %s",
            (uid, grupo_borrado + 1, total - 1),
        )

    if id_updt is not None and n_perc is not None:
        id_updt = _entero(id_updt)
        destino = id_updt - 1 if desplazo and grupo_borrado <= id_updt else id_updt
        _actualizar_porcentaje(db, uid, destino, n_perc)
    return desplazo


@calculator_bp.route("/calculator", methods=["GET", "POST"])
@login_required
def calculator():
    a = request.args
    uid = session["idUsuario"]
    db = mysql.connection.cursor()

    # ---------- 1) Borrados ----------
    deleted_event = a.get("deletedEvent")
    delete_group = a.get("delete_group")
    length_ul = a.get("lengthUl")
    id_group_del = a.get("id_group_del")
    porc_del = a.get("porc_del")
    len_ul = a.get("len")
    id_updt = a.get("id_updt")
    n_perc = a.get("n_perc")

    if deleted_event is not None and delete_group is None:
        _borrar_nota(db, uid, deleted_event)

    elif deleted_event is not None and delete_group is not None and length_ul is not None:
        _borrar_nota(db, uid, deleted_event)
        if _reacomodar_grupos(
            db, uid, _entero(delete_group), _entero(length_ul), id_updt, n_perc
        ):
            registrar_traza(db, "Calculadora", "Ha eliminado notas")

    elif id_group_del is not None and porc_del is not None and len_ul is not None:
        _borrar_grupo(db, uid, id_group_del)
        _reacomodar_grupos(
            db, uid, _entero(id_group_del), _entero(len_ul), id_updt, n_perc
        )

    # ---------- 2) Alta / edición de notas ----------
    note = a.get("note")
    percentage = a.get("percentage")
    id_group = a.get("id_group")
    is_update = a.get("isUpdate")

    if all(_hay(v) for v in (note, percentage, id_group, is_update)):
        if _entero(is_update) == 1:
            db.execute(
                "UPDATE grupoNotas SET nota = %s WHERE idNota = %s AND idUsuario = %s",
                (_numero(note), _entero(a.get("id_nota")), uid),
            )
        else:
            _insertar_nota(db, uid, id_group, percentage, note)
            li_id, new_perc = a.get("li_id"), a.get("new_perc")
            if li_id is not None and new_perc is not None:
                _actualizar_porcentaje(db, uid, _entero(li_id), new_perc)
                registrar_traza(db, "Calculadora", "Ha actualizado notas")

    elif a.get("percs") is not None and a.get("id_groups") is not None:
        for porc, grupo in zip(a["percs"].split(","), a["id_groups"].split(",")):
            _actualizar_porcentaje(db, uid, _entero(grupo), porc)

    mysql.connection.commit()

    # ---------- 3) Lectura: una sola consulta, el promedio se calcula en Python ----------
    db.execute(
        "SELECT * FROM grupoNotas WHERE idUsuario = %s ORDER BY numGrupo, idNota", (uid,)
    )
    notas = db.fetchall()
    db.close()

    grupos = []
    ultimo = None
    for n in notas:
        if n["numGrupo"] != ultimo:
            grupos.append([])
            ultimo = n["numGrupo"]
        grupos[-1].append(n)

    promedio_final = 0
    for grupo in grupos:
        peso = grupo[0]["porcentaje"] / 100
        promedio_final += (sum(n["nota"] for n in grupo) / len(grupo)) * peso

    return render_template(
        "calculator.html",
        nota_ordenadas=grupos,
        len_group=len(grupos),
        promedioFinal=promedio_final,
    )
