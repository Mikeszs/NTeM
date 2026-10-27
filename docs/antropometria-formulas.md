# Fórmulas antropométricas do NTeM

Implementadas em `app/antropometria.py` (fonte única de verdade; o frontend só envia medidas e exibe o retorno).
Unidades: dobras em mm, circunferências e altura em cm, peso em kg, idade em anos.
Densidade (D) em g/mL; `S` = soma das dobras da fórmula; `log` = log10.

Percentual de gordura a partir da densidade: **Brozek et al. (1963)** → `%G = (4,57 / D − 4,142) × 100`.

## Dobras cutâneas

| Fórmula | Sexo | Dobras | Equação de densidade |
|---|---|---|---|
| Pollock 3 | M | torácica, abdominal, coxa | 1,10938 − 0,0008267·S + 0,0000016·S² − 0,0002574·idade |
| Pollock 3 | F | tricipital, suprailíaca, coxa | 1,0994921 − 0,0009929·S + 0,0000023·S² − 0,0001392·idade |
| Pollock 7 | M | torácica, axilar média, tricipital, subescapular, abdominal, suprailíaca, coxa | 1,112 − 0,00043499·S + 0,00000055·S² − 0,00028826·idade |
| Pollock 7 | F | (mesmas 7) | 1,097 − 0,00046971·S + 0,00000056·S² − 0,00012828·idade |
| Petroski | M | subescapular, tricipital, suprailíaca, panturrilha | 1,10726863 − 0,00081201·S + 0,00000212·S² − 0,00041761·idade |
| Petroski | F | axilar média, suprailíaca, coxa, panturrilha | 1,1954713 − 0,07513507·log(S) − 0,00041072·idade |
| Guedes | M | tricipital, suprailíaca, abdominal | 1,1714 − 0,0671·log(S) |
| Guedes | F | coxa, suprailíaca, subescapular | 1,1665 − 0,0706·log(S) |
| Durnin & Womersley | M/F | bicipital, tricipital, subescapular, suprailíaca | D = c − m·log(S), com c e m por faixa etária (tabela em `_DURNIN_TABELA`) |
| Faulkner | M/F | tricipital, subescapular, suprailíaca, abdominal | **%G direto** = 0,153·S + 5,783 (sem densidade) |

Faixas de validade (aviso, não bloqueio): Pollock M 18–61 / F 18–55; Petroski M 18–61 / F 18–51; Guedes M 17–27 / F 18–30; Durnin 16–72.

## Circunferências (protótipo)

- **RFM** (Woolcott & Bergman, 2018): `64 − 20·(altura/cintura)` (M) · `76 − 20·(altura/cintura)` (F).
- **US Navy** (Hodgdon & Beckett, 1984), medidas convertidas para polegadas: M usa abdômen e pescoço; F usa cintura, quadril e pescoço.

## Outros indicadores

- IMC = peso / altura²; classificação OMS. Faixa de peso ideal = IMC 18,5 a 24,9.
- RCQ = cintura / quadril; risco por **Bray & Gray (1988)**, por sexo e faixa etária de 20 a 69 anos.
- CMB = braço relaxado − π × (tricipital em cm).
- TMB: **Harris & Benedict (1919)**, mesmos coeficientes da tela anterior.
- Peso de gordura = peso × %G; peso residual (**Würch, 1974**) = 24,1 % (M) ou 20,9 % (F) do peso; massa livre de gordura = peso − peso de gordura.

## Conferência

Caso de referência (WebDiet: homem, 32 anos, 83 kg, 175 cm, Petroski, Σ = 41 mm) reproduzido pelo NTeM: D = 1,064; %G = 15,2; peso de gordura 12,6 kg; residual 20,0 kg; MLG 70,4 kg; IMC 27,1; RCQ 0,84 (risco moderado); CMB 33,8 cm. Está coberto em `tests/test_antropometria.py`.

Pontos a confirmar com o orientador/fonte primária:
- Pollock 3 feminino: uma fonte secundária traz 0,0001395 no termo da idade; o valor original de Jackson, Pollock & Ward (1980) é 0,0001392 (adotado).
- Guedes: uma fonte consultada cita a equação como de 1994; a atribuição usual é 1985.
