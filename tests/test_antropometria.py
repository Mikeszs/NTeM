"""
Testes das fórmulas antropométricas (módulo puro, sem banco).

O caso "WebDiet" reproduz uma avaliação real exibida no WebDiet (homem, 32 anos,
83 kg, 175 cm, Petroski): serve de referência para garantir que o NTeM devolve
os mesmos números que a ferramenta usada como base.
"""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))

import antropometria as an  # noqa: E402


# ---------------------------------------------------------------------------
# Caso de referência (WebDiet)
# ---------------------------------------------------------------------------

@pytest.fixture
def caso_webdiet():
    return dict(
        sexo="M", formula="petroski", idade=32, peso=83, altura=175,
        dobras={"tricipital": 7, "subescapular": 11, "suprailiaca": 14, "panturrilha": 9,
                "bicipital": 4, "abdominal": 14, "axilar_media": 7, "toracica": 5,
                "supraespinhal": 10},
        circunferencias={"cintura": 84, "quadril": 100, "braco_relaxado": 36},
    )


def test_webdiet_petroski_reproduz_resultados(caso_webdiet):
    r = an.calcular(**caso_webdiet)
    assert r["soma_dobras"] == 41
    assert r["densidade"] == pytest.approx(1.064, abs=0.0005)
    assert r["percentual_gordura"] == 15.2
    assert r["peso_gordura"] == 12.6
    assert r["peso_residual"] == 20.0
    assert r["massa_livre_gordura"] == 70.4
    assert r["imc"] == 27.1
    assert r["classificacao_imc"] == "Sobrepeso"
    assert r["faixa_peso_ideal"] == {"min": 56.7, "max": 76.3}
    assert r["rcq"] == 0.84
    assert r["risco_rcq"] == "Moderado"
    assert r["cmb"] == 33.8
    assert r["pendencias"] == [] and r["avisos"] == []


# ---------------------------------------------------------------------------
# Cada fórmula: campos exigidos, valores plausíveis e regressão numérica
# ---------------------------------------------------------------------------

TODAS_DOBRAS = {d: 12 for d in an.DOBRAS}
TODAS_CIRC = {"pescoco": 38, "cintura": 85, "quadril": 100, "abdomen": 90}


@pytest.mark.parametrize("formula", ["pollock3", "pollock7", "petroski", "guedes", "durnin", "faulkner"])
@pytest.mark.parametrize("sexo", ["M", "F"])
def test_formulas_de_dobras_calculam_percentual_plausivel(formula, sexo):
    r = an.calcular(sexo=sexo, formula=formula, idade=25, peso=70, altura=170, dobras=TODAS_DOBRAS)
    assert r["pendencias"] == []
    assert 3 < r["percentual_gordura"] < 40
    assert r["soma_dobras"] == pytest.approx(
        12 * len(an.campos_exigidos(formula, sexo)[0]))


@pytest.mark.parametrize("formula", ["pollock3", "pollock7", "petroski", "guedes", "durnin", "faulkner"])
def test_mais_gordura_subcutanea_gera_percentual_maior(formula):
    pct = []
    for mm in (8, 16, 24):
        d = {k: mm for k in an.DOBRAS}
        pct.append(an.calcular(sexo="M", formula=formula, idade=28, peso=75, altura=175,
                               dobras=d)["percentual_gordura"])
    assert pct == sorted(pct) and len(set(pct)) == 3


def test_valores_de_regressao_por_formula():
    """Valores calculados à mão a partir das equações publicadas (soma de 12 mm por dobra)."""
    def pct(formula, sexo, idade):
        return an.calcular(sexo=sexo, formula=formula, idade=idade, peso=70, altura=170,
                           dobras=TODAS_DOBRAS)["percentual_gordura"]

    # Pollock 3 M: soma 36 → D = 1.10938 − .0008267·36 + .0000016·36² − .0002574·25
    d = 1.10938 - 0.0008267 * 36 + 0.0000016 * 36 ** 2 - 0.0002574 * 25
    assert pct("pollock3", "M", 25) == round((4.57 / d - 4.142) * 100, 1)
    # Faulkner: soma 48 → 48·0,153 + 5,783 = 13,127
    assert pct("faulkner", "M", 25) == 13.1
    assert pct("faulkner", "F", 25) == 13.1  # Faulkner não depende de sexo
    # Guedes F: soma 36 → 1.1665 − .0706·log10(36)
    d = 1.1665 - 0.0706 * math.log10(36)
    assert pct("guedes", "F", 25) == round((4.57 / d - 4.142) * 100, 1)
    # Petroski F (log): axilar+coxa+supra+panturrilha = 48
    d = 1.1954713 - 0.07513507 * math.log10(48) - 0.00041072 * 25
    assert pct("petroski", "F", 25) == round((4.57 / d - 4.142) * 100, 1)


@pytest.mark.parametrize("idade,c,m", [(16, 1.1533, 0.0643), (17, 1.1620, 0.0630), (19, 1.1620, 0.0630),
                                       (20, 1.1631, 0.0632), (35, 1.1422, 0.0544),
                                       (45, 1.1620, 0.0700), (50, 1.1715, 0.0779), (70, 1.1715, 0.0779)])
def test_durnin_usa_a_faixa_etaria_correta_masculino(idade, c, m):
    assert an._durnin("M", 40, idade) == pytest.approx(c - m * math.log10(40))


@pytest.mark.parametrize("idade,c,m", [(16, 1.1369, 0.0598), (18, 1.1549, 0.0678), (25, 1.1599, 0.0717),
                                       (35, 1.1423, 0.0632), (45, 1.1333, 0.0612), (60, 1.1339, 0.0645)])
def test_durnin_usa_a_faixa_etaria_correta_feminino(idade, c, m):
    assert an._durnin("F", 40, idade) == pytest.approx(c - m * math.log10(40))


def test_dobras_exigidas_por_sexo():
    assert an.campos_exigidos("pollock3", "M")[0] == ("toracica", "abdominal", "coxa")
    assert an.campos_exigidos("pollock3", "F")[0] == ("tricipital", "suprailiaca", "coxa")
    assert len(an.campos_exigidos("pollock7", "M")[0]) == 7
    assert an.campos_exigidos("petroski", "F")[0] == ("axilar_media", "coxa", "suprailiaca", "panturrilha")
    assert an.campos_exigidos("guedes", "M")[0] == ("tricipital", "suprailiaca", "abdominal")
    assert an.campos_exigidos("durnin", "F")[0] == ("tricipital", "bicipital", "subescapular", "suprailiaca")
    assert an.campos_exigidos("faulkner", "M")[0] == ("tricipital", "subescapular", "suprailiaca", "abdominal")


# ---------------------------------------------------------------------------
# Circunferências (RFM e US Navy — protótipo)
# ---------------------------------------------------------------------------

def test_rfm_masculino_e_feminino():
    m = an.calcular(sexo="M", formula="rfm", peso=80, altura=175, circunferencias={"cintura": 90})
    f = an.calcular(sexo="F", formula="rfm", peso=60, altura=165, circunferencias={"cintura": 75})
    assert m["percentual_gordura"] == round(64 - 20 * 175 / 90, 1)
    assert f["percentual_gordura"] == round(76 - 20 * 165 / 75, 1)
    assert m["soma_dobras"] is None and m["densidade"] is None


def test_us_navy_masculino_usa_abdomen_e_feminino_cintura_quadril():
    m = an.calcular(sexo="M", formula="navy", peso=80, altura=175,
                    circunferencias={"pescoco": 38, "abdomen": 90})
    esperado = 86.010 * math.log10((90 - 38) / 2.54) - 70.041 * math.log10(175 / 2.54) + 36.76
    assert m["percentual_gordura"] == round(esperado, 1)
    f = an.calcular(sexo="F", formula="navy", peso=60, altura=165,
                    circunferencias={"pescoco": 32, "cintura": 75, "quadril": 98})
    esperado = 163.205 * math.log10((75 + 98 - 32) / 2.54) - 97.684 * math.log10(165 / 2.54) - 78.387
    assert f["percentual_gordura"] == round(esperado, 1)


def test_us_navy_abdomen_menor_que_pescoco_gera_aviso_sem_quebrar():
    r = an.calcular(sexo="M", formula="navy", peso=80, altura=175,
                    circunferencias={"pescoco": 40, "abdomen": 38})
    assert r["percentual_gordura"] is None
    assert any("abdômen" in a.lower() for a in r["avisos"])


# ---------------------------------------------------------------------------
# Pendências, avisos e entradas limite
# ---------------------------------------------------------------------------

def test_dobra_faltando_gera_pendencia_e_nao_calcula():
    r = an.calcular(sexo="M", formula="pollock3", idade=30, peso=80, altura=180,
                    dobras={"toracica": 10, "abdominal": 20})
    assert r["percentual_gordura"] is None
    assert r["pendencias"] == ["Informe as dobras: Coxa."]


def test_idade_ausente_gera_pendencia_quando_formula_usa_idade():
    r = an.calcular(sexo="F", formula="pollock7", peso=60, altura=165,
                    dobras={d: 10 for d in an.DOBRAS})
    assert "Informe a idade." in r["pendencias"]
    assert r["percentual_gordura"] is None


def test_faulkner_e_guedes_nao_exigem_idade():
    for f in ("faulkner", "guedes"):
        r = an.calcular(sexo="M", formula=f, peso=80, altura=180, dobras={d: 10 for d in an.DOBRAS})
        assert r["pendencias"] == [] and r["percentual_gordura"] is not None


def test_idade_fora_da_faixa_validada_avisa_mas_calcula():
    r = an.calcular(sexo="M", formula="guedes", idade=45, peso=80, altura=180,
                    dobras={d: 10 for d in an.DOBRAS})
    assert r["percentual_gordura"] is not None
    assert any("validada" in a for a in r["avisos"])
    # Guedes não usa idade no cálculo, mas o aviso de validade exige conhecê-la
    r2 = an.calcular(sexo="M", formula="guedes", peso=80, altura=180, dobras={d: 10 for d in an.DOBRAS})
    assert r2["avisos"] == []


def test_resultado_implausivel_nao_e_retornado():
    r = an.calcular(sexo="M", formula="faulkner", peso=80, altura=180,
                    dobras={d: 900 for d in an.DOBRAS})
    assert r["percentual_gordura"] is None
    assert any("plausível" in a for a in r["avisos"])


def test_formula_nenhuma_so_devolve_indicadores_basicos():
    r = an.calcular(sexo="F", formula="nenhuma", idade=30, peso=60, altura=160,
                    circunferencias={"cintura": 70, "quadril": 95})
    assert r["imc"] == 23.4 and r["percentual_gordura"] is None and r["pendencias"] == []
    assert r["tmb"] is not None and r["rcq"] == 0.74


def test_sem_nenhum_dado_nao_quebra():
    r = an.calcular(sexo="M")
    assert r["imc"] is None and r["faixa_peso_ideal"] is None and r["tmb"] is None


@pytest.mark.parametrize("peso,altura", [(0, 170), (-5, 170), (70, 0), (None, None)])
def test_peso_ou_altura_invalidos_nao_geram_imc(peso, altura):
    r = an.calcular(sexo="M", peso=peso, altura=altura)
    assert r["imc"] is None


def test_sexo_ou_formula_invalidos_levantam_erro():
    with pytest.raises(ValueError):
        an.calcular(sexo="X")
    with pytest.raises(ValueError):
        an.calcular(sexo="M", formula="inexistente")


# ---------------------------------------------------------------------------
# Classificações e TMB
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("imc,esperado", [(18.4, "Abaixo do Peso"), (18.5, "Peso Normal"),
                                          (24.9, "Peso Normal"), (25.0, "Sobrepeso"),
                                          (29.9, "Sobrepeso"), (30.0, "Obesidade grau I"),
                                          (35.0, "Obesidade grau II"), (40.0, "Obesidade grau III")])
def test_classificacao_imc_nos_limites(imc, esperado):
    assert an.classificar_imc(imc) == esperado


@pytest.mark.parametrize("sexo,idade,rcq,esperado", [
    ("M", 32, 0.83, "Baixo"), ("M", 32, 0.84, "Moderado"), ("M", 32, 0.91, "Moderado"),
    ("M", 32, 0.92, "Alto"), ("M", 32, 0.96, "Alto"), ("M", 32, 0.97, "Muito alto"),
    ("F", 25, 0.70, "Baixo"), ("F", 25, 0.77, "Moderado"), ("F", 25, 0.82, "Alto"),
    ("F", 25, 0.83, "Muito alto"), ("F", 69, 0.91, "Muito alto"),
    ("M", 19, 0.80, None), ("F", 70, 0.80, None),
])
def test_risco_rcq_bray_gray(sexo, idade, rcq, esperado):
    assert an.classificar_rcq(sexo, idade, rcq) == esperado


def test_rcq_fora_da_faixa_etaria_gera_aviso():
    r = an.calcular(sexo="M", idade=17, circunferencias={"cintura": 80, "quadril": 100})
    assert r["rcq"] == 0.8 and r["risco_rcq"] is None
    assert any("RCQ" in a for a in r["avisos"])


def test_tmb_harris_benedict_mantem_valores_da_tela_anterior():
    """Mesmos coeficientes que o frontend usava antes da refatoração."""
    assert an.taxa_metabolica_basal("M", 83, 175, 32) == pytest.approx(
        66.5 + 13.75 * 83 + 5.003 * 175 - 6.75 * 32)
    assert an.taxa_metabolica_basal("F", 60, 160, 30) == pytest.approx(
        655.1 + 9.563 * 60 + 1.85 * 160 - 4.676 * 30)
