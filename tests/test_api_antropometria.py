"""Testes de API da antropometria: segurança, validação, histórico e idempotência."""
from datetime import date, timedelta

import pytest
from sqlalchemy.exc import OperationalError

# Avaliação real do WebDiet (homem, 32 anos, 83 kg, 175 cm, Petroski)
WEBDIET = {
    "sexo": "M", "formula": "petroski", "idade": 32, "peso": 83, "altura": 175,
    "dobras": {"tricipital": 7, "subescapular": 11, "suprailiaca": 14, "panturrilha": 9},
    "circunferencias": {"cintura": 84, "quadril": 100, "braco_relaxado": 36},
}


def _copia(**mudancas):
    corpo = {**WEBDIET, "dobras": dict(WEBDIET["dobras"]), "circunferencias": dict(WEBDIET["circunferencias"])}
    corpo.update(mudancas)
    return corpo


# ---------------------------------------------------------------------------
# Autenticação e autorização (backend decide; esconder botão não protege nada)
# ---------------------------------------------------------------------------

ROTAS_PROTEGIDAS = [
    ("get", "/antropometria/formulas", None),
    ("post", "/antropometria/calcular", WEBDIET),
    ("post", "/pacientes/1/avaliacoes", WEBDIET),
    ("get", "/pacientes/1/avaliacoes", None),
]


@pytest.mark.parametrize("metodo,url,corpo", ROTAS_PROTEGIDAS)
def test_sem_token_retorna_401(client, metodo, url, corpo):
    r = getattr(client, metodo)(url, **({"json": corpo} if corpo else {}))
    assert r.status_code == 401


@pytest.mark.parametrize("metodo,url,corpo", ROTAS_PROTEGIDAS)
def test_usuario_com_papel_paciente_recebe_403(client, headers_paciente, metodo, url, corpo):
    r = getattr(client, metodo)(url, headers=headers_paciente, **({"json": corpo} if corpo else {}))
    assert r.status_code == 403


# ---------------------------------------------------------------------------
# Catálogo e cálculo
# ---------------------------------------------------------------------------

def test_catalogo_lista_formulas_e_campos_por_sexo(client, headers_prof):
    m = client.get("/antropometria/formulas?sexo=M", headers=headers_prof).json()
    ids = [f["id"] for f in m]
    assert ids == ["pollock3", "pollock7", "petroski", "guedes", "durnin", "faulkner", "rfm", "navy", "nenhuma"]
    pollock3_m = next(f for f in m if f["id"] == "pollock3")
    assert pollock3_m["dobras"] == ["toracica", "abdominal", "coxa"] and pollock3_m["tipo"] == "dobras"
    f = client.get("/antropometria/formulas?sexo=F", headers=headers_prof).json()
    assert next(x for x in f if x["id"] == "pollock3")["dobras"] == ["tricipital", "suprailiaca", "coxa"]
    assert client.get("/antropometria/formulas?sexo=X", headers=headers_prof).status_code == 422


def test_calcular_reproduz_resultado_do_webdiet(client, headers_prof):
    r = client.post("/antropometria/calcular", json=WEBDIET, headers=headers_prof)
    assert r.status_code == 200
    res = r.json()
    assert res["percentual_gordura"] == 15.2 and res["imc"] == 27.1
    assert res["massa_livre_gordura"] == 70.4 and res["risco_rcq"] == "Moderado"
    assert res["tmb"] == round(66.5 + 13.75 * 83 + 5.003 * 175 - 6.75 * 32)


def test_calcular_nao_persiste_nada(client, headers_prof, paciente):
    client.post("/antropometria/calcular", json=WEBDIET, headers=headers_prof)
    r = client.get(f"/pacientes/{paciente['id']}/avaliacoes", headers=headers_prof).json()
    assert r == {"total": 0, "itens": []}


# ---------------------------------------------------------------------------
# Entradas inválidas / maliciosas (não confiar no frontend)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("mudanca", [
    {"sexo": "X"}, {"sexo": "masculino"}, {"formula": "inventada"},
    {"idade": 0}, {"idade": 121}, {"idade": 32.5},
    {"peso": 0}, {"peso": -1}, {"peso": 501}, {"peso": "abc"},
    {"altura": 1750}, {"altura": 10},
    {"dobras": {"tricipital": 0}}, {"dobras": {"tricipital": 101}}, {"dobras": {"tricipital": -3}},
    {"dobras": {"campo_inventado": 5}},
    {"circunferencias": {"cintura": 251}}, {"circunferencias": {"cintura": "x"}},
    {"circunferencias": {"outro": 1}},
    {"campo_extra": 1},
    {"data_avaliacao": (date.today() + timedelta(days=10)).isoformat()},
    {"data_avaliacao": "ontem"},
])
def test_entradas_invalidas_sao_rejeitadas_com_422(client, headers_prof, mudanca):
    r = client.post("/antropometria/calcular", json=_copia(**mudanca), headers=headers_prof)
    assert r.status_code == 422, r.text


def test_nan_e_infinito_sao_rejeitados(client, headers_prof):
    for literal in ("NaN", "Infinity", "-Infinity"):
        corpo = '{"sexo":"M","formula":"nenhuma","peso":%s,"altura":175}' % literal
        r = client.post("/antropometria/calcular", content=corpo,
                        headers={**headers_prof, "Content-Type": "application/json"})
        assert r.status_code == 422, literal


def test_exige_ao_menos_uma_medida(client, headers_prof):
    r = client.post("/antropometria/calcular", json={"sexo": "F", "formula": "nenhuma"}, headers=headers_prof)
    assert r.status_code == 422
    assert "ao menos uma medida" in r.text


def test_dobra_ausente_nao_e_erro_e_volta_como_pendencia(client, headers_prof):
    corpo = _copia(dobras={"tricipital": 7})
    r = client.post("/antropometria/calcular", json=corpo, headers=headers_prof)
    assert r.status_code == 200
    assert r.json()["percentual_gordura"] is None
    assert r.json()["pendencias"]


def test_erro_de_validacao_nao_vaza_detalhes_internos(client, headers_prof):
    r = client.post("/antropometria/calcular", json=_copia(peso="abc"), headers=headers_prof)
    texto = r.text.lower()
    assert "traceback" not in texto and "sqlalchemy" not in texto


# ---------------------------------------------------------------------------
# Persistência e histórico
# ---------------------------------------------------------------------------

def test_registrar_avaliacao_grava_snapshot_e_atualiza_prontuario(client, headers_prof, paciente):
    r = client.post(f"/pacientes/{paciente['id']}/avaliacoes", json=WEBDIET, headers=headers_prof)
    assert r.status_code == 201, r.text
    av = r.json()
    assert av["resultado"]["percentual_gordura"] == 15.2
    assert av["formula"] == "petroski" and av["data_avaliacao"] == date.today().isoformat()
    assert av["dobras"] == WEBDIET["dobras"]  # só o que foi informado

    pac = client.get(f"/pacientes/{paciente['id']}", headers=headers_prof).json()
    assert (pac["sexo"], pac["idade"], pac["peso"], pac["altura"]) == ("M", 32, 83.0, 175.0)
    assert (pac["cintura"], pac["quadril"], pac["abdomen"]) == (84.0, 100.0, 0.0)  # abdômen não informado: preservado


def test_medida_nao_informada_nao_apaga_valor_do_prontuario(client, headers_prof, paciente):
    client.post(f"/pacientes/{paciente['id']}/avaliacoes", json=WEBDIET, headers=headers_prof)
    segunda = {"sexo": "M", "formula": "nenhuma", "peso": 81.5, "data_avaliacao": "2026-01-15"}
    assert client.post(f"/pacientes/{paciente['id']}/avaliacoes", json=segunda, headers=headers_prof).status_code == 201
    pac = client.get(f"/pacientes/{paciente['id']}", headers=headers_prof).json()
    assert pac["peso"] == 81.5 and pac["altura"] == 175.0 and pac["cintura"] == 84.0


def test_paciente_inexistente_retorna_404(client, headers_prof):
    assert client.post("/pacientes/999999/avaliacoes", json=WEBDIET, headers=headers_prof).status_code == 404
    assert client.get("/pacientes/999999/avaliacoes", headers=headers_prof).status_code == 404


def test_reenvio_identico_nao_duplica_historico(client, headers_prof, paciente):
    url = f"/pacientes/{paciente['id']}/avaliacoes"
    primeira = client.post(url, json=WEBDIET, headers=headers_prof)
    segunda = client.post(url, json=WEBDIET, headers=headers_prof)   # duplo clique
    assert primeira.status_code == 201 and segunda.status_code == 200
    assert primeira.json()["id"] == segunda.json()["id"]
    assert client.get(url, headers=headers_prof).json()["total"] == 1


def test_dados_diferentes_geram_nova_avaliacao(client, headers_prof, paciente):
    url = f"/pacientes/{paciente['id']}/avaliacoes"
    client.post(url, json=WEBDIET, headers=headers_prof)
    r = client.post(url, json=_copia(peso=82), headers=headers_prof)
    assert r.status_code == 201
    assert client.get(url, headers=headers_prof).json()["total"] == 2


def test_historico_ordenado_por_data_e_paginado(client, headers_prof, paciente):
    url = f"/pacientes/{paciente['id']}/avaliacoes"
    for i, dia in enumerate(["2026-03-01", "2026-05-01", "2026-04-01"]):
        assert client.post(url, json=_copia(peso=80 + i, data_avaliacao=dia), headers=headers_prof).status_code == 201
    todos = client.get(url, headers=headers_prof).json()
    assert todos["total"] == 3
    assert [a["data_avaliacao"] for a in todos["itens"]] == ["2026-05-01", "2026-04-01", "2026-03-01"]
    pag = client.get(url + "?limite=1&deslocamento=1", headers=headers_prof).json()
    assert pag["total"] == 3 and [a["data_avaliacao"] for a in pag["itens"]] == ["2026-04-01"]


@pytest.mark.parametrize("qs", ["limite=0", "limite=51", "limite=-1", "deslocamento=-1", "limite=abc"])
def test_paginacao_tem_limites(client, headers_prof, paciente, qs):
    r = client.get(f"/pacientes/{paciente['id']}/avaliacoes?{qs}", headers=headers_prof)
    assert r.status_code == 422


def test_falha_de_banco_retorna_mensagem_amigavel_e_nao_vaza_detalhes(client, headers_prof, paciente, monkeypatch):
    from sqlalchemy.orm import Session

    def commit_quebrado(self):
        raise OperationalError("INSERT secreto", {}, Exception("senha do banco: hunter2"))

    monkeypatch.setattr(Session, "commit", commit_quebrado)
    r = client.post(f"/pacientes/{paciente['id']}/avaliacoes", json=WEBDIET, headers=headers_prof)
    assert r.status_code == 500
    assert r.json()["detail"].startswith("Não foi possível salvar")
    assert "hunter2" not in r.text and "INSERT" not in r.text
    monkeypatch.undo()
    assert client.get(f"/pacientes/{paciente['id']}/avaliacoes", headers=headers_prof).json()["total"] == 0
