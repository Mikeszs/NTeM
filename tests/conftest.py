"""
Configuração dos testes de API.

Usa um SQLite temporário (nunca o banco real) e uma SECRET_KEY descartável.
As variáveis precisam ser definidas ANTES de importar main/database, que
exigem DATABASE_URL e SECRET_KEY já no import.
"""
import os
import sys
import tempfile
from pathlib import Path

_TMP = tempfile.mkdtemp(prefix="ntem_tests_")
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP}/teste.db"
os.environ["SECRET_KEY"] = "chave-apenas-para-testes"
os.environ.pop("RESEND_API_KEY", None)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import main  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(main.app) as c:
        yield c


def _criar_e_logar(client, nome, email, role):
    client.post("/auth/cadastro", json={"nome": nome, "email": email, "senha": "senha-teste-123", "role": role})
    r = client.post("/auth/login", data={"username": email, "password": "senha-teste-123"})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture(scope="session")
def headers_prof(client):
    return _criar_e_logar(client, "Profissional Teste", "prof@teste.com", "profissional")


@pytest.fixture(scope="session")
def headers_paciente(client):
    return _criar_e_logar(client, "Paciente Teste", "pac@teste.com", "paciente")


@pytest.fixture
def paciente(client, headers_prof):
    """Um paciente novo por teste (isola histórico e contagens)."""
    r = client.post("/pacientes/", json={"nome": "Everton Teste", "objetivo": "Emagrecimento"}, headers=headers_prof)
    assert r.status_code == 200, r.text
    return r.json()["dados"]
