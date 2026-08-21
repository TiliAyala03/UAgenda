"""
Pruebas de humo (smoke tests) para UAgenda.

Objetivo de esta primera entrega: demostrar que el sistema base arranca
y responde, no cobertura exhaustiva. Se amplía en fases posteriores del
curso a medida que se identifiquen los drivers de calidad prioritarios
(ver 02-stakeholders-drivers.md en el dossier).

Cómo correrlas:
    pip install pytest    (si falta pytest)
    python -m pytest test_smoke.py -v

Requieren las mismas variables de entorno que main.py para arrancar
(MYSQL_PASSWORD_UNAGENDA, EMAIL_PASSWORD_UNAGENDA) y que MySQL esté
corriendo localmente con el schema prflask ya importado.
"""

import pytest
from main import app
 
 
@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client
 
 
def test_homepage_loads(client):
    """La página de login debe responder 200 sin necesitar sesión ni DB."""
    response = client.get("/")
    assert response.status_code == 200
 
 
def test_admin_requires_login(client):
    """/admin está protegida por @login_required. En esta app, sin sesión
    no redirige (302): sustituye el contenido y devuelve la página de
    login (index.html) con status 200. Lo que valida este test es que el
    contenido devuelto sea el del login, no el de la vista protegida."""
    response = client.get("/admin")
    assert response.status_code == 200
    assert b"INICIAR SESI" in response.data
 
 
def test_nonexistent_route_returns_404(client):
    """Ruta que no existe debe devolver 404, confirmando que el
    enrutamiento de Flask está vivo y respondiendo normalmente."""
    response = client.get("/esta-ruta-no-existe-xyz")
    assert response.status_code == 404
 