"""
antropometria.py — Cálculos antropométricos do NTeM (sem dependência de banco/HTTP).

Este módulo é a FONTE ÚNICA DE VERDADE das fórmulas: o frontend apenas envia as
medidas e exibe o retorno. Assim, a regra clínica não fica duplicada em JS e o
resultado salvo no prontuário é sempre o calculado no servidor.

Convenções
----------
- sexo: "M" ou "F" (mesmo padrão já usado em Paciente.sexo)
- dobras cutâneas em milímetros; circunferências em centímetros
- peso em kg; altura em cm; idade em anos
- densidade corporal em g/mL; percentual de gordura em %

Referências das equações (coeficientes conferidos em fontes — ver
docs/antropometria-formulas.md):
- Pollock 3 e 7 dobras: Jackson & Pollock (1978); Jackson, Pollock & Ward (1980)
- Petroski (1995) — equações generalizadas, 4 dobras
- Guedes (1985)
- Durnin & Womersley (1974)
- Faulkner (1968)
- RFM: Woolcott & Bergman (2018) | US Navy: Hodgdon & Beckett (1984)
- Densidade → % de gordura: Brozek et al. (1963)
- Peso residual: Würch (1974)
- Risco pela RCQ: Bray & Gray (1988)
- TMB: Harris & Benedict (1919)
"""

from __future__ import annotations

import math
from typing import Callable, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Campos aceitos
# ---------------------------------------------------------------------------

DOBRAS: Tuple[str, ...] = (
    "tricipital", "bicipital", "abdominal", "subescapular", "axilar_media",
    "coxa", "toracica", "suprailiaca", "panturrilha", "supraespinhal",
)

CIRCUNFERENCIAS: Tuple[str, ...] = (
    "pescoco", "torax", "ombro", "cintura", "quadril", "abdomen",
    "braco_relaxado", "braco_contraido", "antebraco",
    "coxa_proximal", "coxa_distal", "panturrilha",
)

ROTULOS_DOBRAS: Dict[str, str] = {
    "tricipital": "Tricipital", "bicipital": "Bicipital", "abdominal": "Abdominal",
    "subescapular": "Subescapular", "axilar_media": "Axilar média", "coxa": "Coxa",
    "toracica": "Torácica", "suprailiaca": "Suprailíaca", "panturrilha": "Panturrilha",
    "supraespinhal": "Supraespinhal",
}

ROTULOS_CIRC: Dict[str, str] = {
    "pescoco": "Pescoço", "torax": "Tórax", "ombro": "Ombro", "cintura": "Cintura",
    "quadril": "Quadril", "abdomen": "Abdômen", "braco_relaxado": "Braço relaxado",
    "braco_contraido": "Braço contraído", "antebraco": "Antebraço",
    "coxa_proximal": "Coxa proximal", "coxa_distal": "Coxa distal",
    "panturrilha": "Panturrilha",
}

# Fatores do peso residual (Würch, 1974): fração do peso corporal.
PESO_RESIDUAL_FRACAO = {"M": 0.241, "F": 0.209}

# Faixa de IMC considerada adequada (OMS) para a "faixa de peso ideal".
IMC_MIN_ADEQUADO = 18.5
IMC_MAX_ADEQUADO = 24.9


# ---------------------------------------------------------------------------
# Densidade corporal por protocolo de dobras
# Cada função recebe (sexo, soma_das_dobras, idade) e devolve densidade em g/mL.
# ---------------------------------------------------------------------------

def _pollock3(sexo: str, soma: float, idade: float, **_) -> float:
    if sexo == "M":
        return 1.10938 - 0.0008267 * soma + 0.0000016 * soma ** 2 - 0.0002574 * idade
    return 1.0994921 - 0.0009929 * soma + 0.0000023 * soma ** 2 - 0.0001392 * idade


def _pollock7(sexo: str, soma: float, idade: float, **_) -> float:
    if sexo == "M":
        return 1.112 - 0.00043499 * soma + 0.00000055 * soma ** 2 - 0.00028826 * idade
    return 1.097 - 0.00046971 * soma + 0.00000056 * soma ** 2 - 0.00012828 * idade


def _petroski(sexo: str, soma: float, idade: float, **_) -> float:
    if sexo == "M":
        return 1.10726863 - 0.00081201 * soma + 0.00000212 * soma ** 2 - 0.00041761 * idade
    # Feminina: forma logarítmica (axilar média + suprailíaca + coxa + panturrilha).
    return 1.1954713 - 0.07513507 * math.log10(soma) - 0.00041072 * idade


def _guedes(sexo: str, soma: float, idade: float, **_) -> float:
    if sexo == "M":
        return 1.1714 - 0.0671 * math.log10(soma)
    return 1.1665 - 0.0706 * math.log10(soma)


# Durnin & Womersley (1974): D = c - m * log10(soma de 4 dobras)
# (limite inferior da faixa etária) -> (c, m)
_DURNIN_TABELA = {
    "M": [(0, 1.1533, 0.0643), (17, 1.1620, 0.0630), (20, 1.1631, 0.0632),
          (30, 1.1422, 0.0544), (40, 1.1620, 0.0700), (50, 1.1715, 0.0779)],
    "F": [(0, 1.1369, 0.0598), (17, 1.1549, 0.0678), (20, 1.1599, 0.0717),
          (30, 1.1423, 0.0632), (40, 1.1333, 0.0612), (50, 1.1339, 0.0645)],
}


def _durnin(sexo: str, soma: float, idade: float, **_) -> float:
    c, m = _DURNIN_TABELA[sexo][0][1:]
    for limite, c_faixa, m_faixa in _DURNIN_TABELA[sexo]:
        if idade >= limite:
            c, m = c_faixa, m_faixa
    return c - m * math.log10(soma)


def brozek(densidade: float) -> float:
    """% de gordura a partir da densidade (Brozek et al., 1963)."""
    return (4.57 / densidade - 4.142) * 100


def _faulkner_percentual(soma: float) -> float:
    """Faulkner (1968): devolve direto o % de gordura (sem densidade)."""
    return soma * 0.153 + 5.783


# ---------------------------------------------------------------------------
# Percentual de gordura por circunferências (sem dobras)
# Levantam ValueError com mensagem amigável quando a combinação é inválida.
# ---------------------------------------------------------------------------

def _rfm(sexo: str, altura: float, circ: Dict[str, Optional[float]]) -> float:
    """Relative Fat Mass: 64 − 20 × (altura/cintura) [M] | 76 − ... [F]."""
    return (64 if sexo == "M" else 76) - 20 * (altura / circ["cintura"])


def _us_navy(sexo: str, altura: float, circ: Dict[str, Optional[float]]) -> float:
    """US Navy (equações em polegadas; convertidas internamente)."""
    cm_para_pol = 1 / 2.54
    pescoco = circ["pescoco"]
    h = altura * cm_para_pol
    if sexo == "M":
        if circ["abdomen"] <= pescoco:
            raise ValueError("O abdômen deve ser maior que o pescoço.")
        return 86.010 * math.log10((circ["abdomen"] - pescoco) * cm_para_pol) \
            - 70.041 * math.log10(h) + 36.76
    soma = circ["cintura"] + circ["quadril"] - pescoco
    if soma <= 0:
        raise ValueError("Cintura + quadril devem ser maiores que o pescoço.")
    return 163.205 * math.log10(soma * cm_para_pol) - 97.684 * math.log10(h) - 78.387


# ---------------------------------------------------------------------------
# Catálogo de fórmulas
# 'dobras' e 'circunferencias' são funções do sexo -> tupla de campos exigidos.
# 'tipo' define o grupo na interface: dobras | circunferencias | nenhuma.
# 'faixa_etaria' (opcional) é a faixa em que a equação foi validada; fora dela
# o cálculo é feito, mas um aviso é devolvido.
# ---------------------------------------------------------------------------

def _fixo(*campos: str) -> Callable[[str], Tuple[str, ...]]:
    return lambda sexo: tuple(campos)


FORMULAS: Dict[str, dict] = {
    "pollock3": {
        "nome": "Pollock 3",
        "tipo": "dobras",
        "referencia": "Jackson & Pollock, 1978; Jackson, Pollock & Ward, 1980",
        "dobras": lambda sexo: ("toracica", "abdominal", "coxa") if sexo == "M"
                               else ("tricipital", "suprailiaca", "coxa"),
        "usa_idade": True,
        "densidade": _pollock3,
        "faixa_etaria": {"M": (18, 61), "F": (18, 55)},
    },
    "pollock7": {
        "nome": "Pollock 7",
        "tipo": "dobras",
        "referencia": "Jackson & Pollock, 1978; Jackson, Pollock & Ward, 1980",
        "dobras": _fixo("toracica", "axilar_media", "tricipital", "subescapular",
                        "abdominal", "suprailiaca", "coxa"),
        "usa_idade": True,
        "densidade": _pollock7,
        "faixa_etaria": {"M": (18, 61), "F": (18, 55)},
    },
    "petroski": {
        "nome": "Petroski",
        "tipo": "dobras",
        "referencia": "Petroski, 1995",
        "dobras": lambda sexo: ("subescapular", "tricipital", "suprailiaca", "panturrilha")
                               if sexo == "M"
                               else ("axilar_media", "coxa", "suprailiaca", "panturrilha"),
        "usa_idade": True,
        "densidade": _petroski,
        "faixa_etaria": {"M": (18, 61), "F": (18, 51)},
    },
    "guedes": {
        "nome": "Guedes",
        "tipo": "dobras",
        "referencia": "Guedes, 1985",
        "dobras": lambda sexo: ("tricipital", "suprailiaca", "abdominal") if sexo == "M"
                               else ("coxa", "suprailiaca", "subescapular"),
        "usa_idade": False,
        "densidade": _guedes,
        "faixa_etaria": {"M": (17, 27), "F": (18, 30)},
    },
    "durnin": {
        "nome": "Durnin",
        "tipo": "dobras",
        "referencia": "Durnin & Womersley, 1974",
        "dobras": _fixo("tricipital", "bicipital", "subescapular", "suprailiaca"),
        "usa_idade": True,
        "densidade": _durnin,
        "faixa_etaria": {"M": (16, 72), "F": (16, 72)},
    },
    "faulkner": {
        "nome": "Faulkner",
        "tipo": "dobras",
        "referencia": "Faulkner, 1968",
        "dobras": _fixo("tricipital", "subescapular", "suprailiaca", "abdominal"),
        "usa_idade": False,
        "densidade": None,  # resultado direto em %
    },
    "rfm": {
        "nome": "RFM (altura e cintura)",
        "tipo": "circunferencias",
        "referencia": "Woolcott & Bergman, 2018",
        "circunferencias": _fixo("cintura"),
        "usa_idade": False,
        "percentual": _rfm,
    },
    "navy": {
        "nome": "US Navy (circunferências)",
        "tipo": "circunferencias",
        "referencia": "Hodgdon & Beckett, 1984",
        "circunferencias": lambda sexo: ("pescoco", "abdomen") if sexo == "M"
                                        else ("pescoco", "cintura", "quadril"),
        "usa_idade": False,
        "percentual": _us_navy,
    },
    "nenhuma": {
        "nome": "Nenhuma",
        "tipo": "nenhuma",
        "referencia": None,
        "usa_idade": False,
    },
}


def campos_exigidos(formula: str, sexo: str) -> Tuple[Tuple[str, ...], Tuple[str, ...]]:
    """(dobras, circunferências) necessárias para a fórmula/sexo."""
    cfg = FORMULAS[formula]
    dobras = cfg["dobras"](sexo) if "dobras" in cfg else ()
    circ = cfg["circunferencias"](sexo) if "circunferencias" in cfg else ()
    return dobras, circ


def catalogo(sexo: str) -> List[dict]:
    """Descrição das fórmulas para o frontend destacar os campos necessários."""
    itens = []
    for chave, f in FORMULAS.items():
        dobras, circ = campos_exigidos(chave, sexo)
        itens.append({
            "id": chave,
            "nome": f["nome"],
            "tipo": f["tipo"],
            "referencia": f["referencia"],
            "dobras": list(dobras),
            "circunferencias": list(circ),
            "usa_idade": f["usa_idade"],
            "usa_altura": f["tipo"] == "circunferencias",
        })
    return itens


# ---------------------------------------------------------------------------
# Auxiliares de classificação
# ---------------------------------------------------------------------------

def classificar_imc(imc: float) -> str:
    if imc < 18.5:
        return "Abaixo do Peso"
    if imc < 25.0:
        return "Peso Normal"
    if imc < 30.0:
        return "Sobrepeso"
    if imc < 35.0:
        return "Obesidade grau I"
    if imc < 40.0:
        return "Obesidade grau II"
    return "Obesidade grau III"


# Bray & Gray (1988): faixa etária -> (limite do risco baixo, do moderado, do alto).
#   rcq <  t0 → Baixo | rcq <= t1 → Moderado | rcq <= t2 → Alto | acima → Muito alto
_RCQ_RISCO = {
    "M": {(20, 29): (0.83, 0.88, 0.94), (30, 39): (0.84, 0.91, 0.96),
          (40, 49): (0.88, 0.95, 1.00), (50, 59): (0.90, 0.96, 1.02),
          (60, 69): (0.91, 0.98, 1.03)},
    "F": {(20, 29): (0.71, 0.77, 0.82), (30, 39): (0.72, 0.78, 0.84),
          (40, 49): (0.73, 0.79, 0.87), (50, 59): (0.74, 0.81, 0.88),
          (60, 69): (0.76, 0.83, 0.90)},
}


def classificar_rcq(sexo: str, idade: float, rcq: float) -> Optional[str]:
    """Risco metabólico pela RCQ (Bray & Gray, 1988). None fora de 20–69 anos."""
    for (ini, fim), (t0, t1, t2) in _RCQ_RISCO[sexo].items():
        if ini <= idade < fim + 1:
            if rcq < t0:
                return "Baixo"
            if rcq <= t1:
                return "Moderado"
            if rcq <= t2:
                return "Alto"
            return "Muito alto"
    return None


def taxa_metabolica_basal(sexo: str, peso: float, altura: float, idade: float) -> float:
    """TMB pela equação original de Harris & Benedict (1919), em kcal/dia."""
    if sexo == "M":
        return 66.5 + 13.75 * peso + 5.003 * altura - 6.75 * idade
    return 655.1 + 9.563 * peso + 1.85 * altura - 4.676 * idade


def _positivo(v: Optional[float]) -> bool:
    return v is not None and v > 0


# ---------------------------------------------------------------------------
# Cálculo principal
# ---------------------------------------------------------------------------

def calcular(
    *,
    sexo: str,
    formula: str = "nenhuma",
    idade: Optional[float] = None,
    peso: Optional[float] = None,
    altura: Optional[float] = None,
    dobras: Optional[Dict[str, Optional[float]]] = None,
    circunferencias: Optional[Dict[str, Optional[float]]] = None,
) -> dict:
    """
    Calcula todos os indicadores possíveis com as medidas informadas.
    Nunca levanta exceção por falta de dado: o que não pode ser calculado
    volta como None e a razão aparece em 'pendencias'/'avisos'.
    """
    if sexo not in ("M", "F"):
        raise ValueError("sexo deve ser 'M' ou 'F'")
    if formula not in FORMULAS:
        raise ValueError(f"fórmula desconhecida: {formula}")

    dobras = dobras or {}
    circ = circunferencias or {}
    pendencias: List[str] = []
    avisos: List[str] = []
    cfg = FORMULAS[formula]

    r: dict = {
        "formula": formula,
        "formula_nome": cfg["nome"],
        "referencia": cfg["referencia"],
        "peso": peso if _positivo(peso) else None,
        "altura": altura if _positivo(altura) else None,
        "imc": None, "classificacao_imc": None,
        "faixa_peso_ideal": None,
        "rcq": None, "risco_rcq": None, "razao_cintura_altura": None, "cmb": None,
        "tmb": None,
        "soma_dobras": None, "densidade": None, "percentual_gordura": None,
        "peso_gordura": None, "peso_residual": None, "massa_livre_gordura": None,
        "pendencias": pendencias, "avisos": avisos,
    }

    # --- Peso e medidas ----------------------------------------------------
    if _positivo(altura):
        h_m = altura / 100
        r["faixa_peso_ideal"] = {
            "min": round(IMC_MIN_ADEQUADO * h_m ** 2, 1),
            "max": round(IMC_MAX_ADEQUADO * h_m ** 2, 1),
        }
        if _positivo(peso):
            imc = peso / h_m ** 2
            r["imc"] = round(imc, 1)
            r["classificacao_imc"] = classificar_imc(imc)

    if _positivo(peso) and _positivo(altura) and _positivo(idade):
        r["tmb"] = round(taxa_metabolica_basal(sexo, peso, altura, idade))

    cintura, quadril = circ.get("cintura"), circ.get("quadril")
    if _positivo(cintura) and _positivo(quadril):
        r["rcq"] = round(cintura / quadril, 2)
        if _positivo(idade):
            r["risco_rcq"] = classificar_rcq(sexo, idade, r["rcq"])
            if r["risco_rcq"] is None:
                avisos.append("A classificação de risco pela RCQ está disponível de 20 a 69 anos.")
    if _positivo(cintura) and _positivo(altura):
        r["razao_cintura_altura"] = round(cintura / altura, 2)

    # CMB = CB - π × DCT (DCT em cm)
    braco, tricipital = circ.get("braco_relaxado"), dobras.get("tricipital")
    if _positivo(braco) and _positivo(tricipital):
        r["cmb"] = round(braco - math.pi * (tricipital / 10), 1)

    # --- Percentual de gordura --------------------------------------------
    if cfg["tipo"] == "nenhuma":
        return r

    exigidas_dobras, exigidas_circ = campos_exigidos(formula, sexo)
    faltando_dobras = [ROTULOS_DOBRAS[d] for d in exigidas_dobras if not _positivo(dobras.get(d))]
    faltando_circ = [ROTULOS_CIRC[c] for c in exigidas_circ if not _positivo(circ.get(c))]
    if faltando_dobras:
        pendencias.append("Informe as dobras: " + ", ".join(faltando_dobras) + ".")
    if faltando_circ:
        pendencias.append("Informe as circunferências: " + ", ".join(faltando_circ) + ".")
    if cfg["tipo"] == "circunferencias" and not _positivo(altura):
        pendencias.append("Informe a altura.")
    if cfg["usa_idade"] and not _positivo(idade):
        pendencias.append("Informe a idade.")
    if pendencias:
        return r

    faixa = cfg.get("faixa_etaria", {}).get(sexo)
    if faixa and _positivo(idade) and not (faixa[0] <= idade <= faixa[1]):
        avisos.append(
            f"A equação foi validada para {faixa[0]} a {faixa[1]} anos; "
            "interprete o resultado com cautela."
        )

    if cfg["tipo"] == "circunferencias":
        try:
            pct = cfg["percentual"](sexo, altura, circ)
        except ValueError as erro:
            avisos.append(str(erro))
            return r
    else:
        soma = sum(dobras[d] for d in exigidas_dobras)
        r["soma_dobras"] = round(soma, 1)
        if cfg["densidade"] is None:  # Faulkner
            pct = _faulkner_percentual(soma)
        else:
            densidade = cfg["densidade"](sexo, soma, idade or 0)
            if densidade <= 0:
                avisos.append("Resultado fora da faixa plausível. Confira as medidas informadas.")
                return r
            r["densidade"] = round(densidade, 4)
            pct = brozek(densidade)

    if not (0 < pct < 100):
        avisos.append("Resultado fora da faixa plausível. Confira as medidas informadas.")
        return r

    r["percentual_gordura"] = round(pct, 1)

    if _positivo(peso):
        gordura = peso * pct / 100
        r["peso_gordura"] = round(gordura, 1)
        r["peso_residual"] = round(peso * PESO_RESIDUAL_FRACAO[sexo], 1)
        r["massa_livre_gordura"] = round(peso - gordura, 1)

    return r
