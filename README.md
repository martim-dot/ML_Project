# Ler - sobre Numerical_Features.ipynb - Decisões - Tudo o necessário

Formato de cada tópico: **Normal** (valores esperados) · **Mal** (o que está errado) · **Gráficos** (muito resumido) · **Decisão** (o que fazer no NB1).

Regra geral para os missing values: **mediana do training set** + **missing indicator** (quando a taxa de fatais muda).

---

## Sobre Temperatura e Dew Point

**Normal:** temperatura entre -60 e 130 °F; dew point nunca acima da temperatura.

**Mal:**
- `wx_temp_c` é só `wx_temp` convertida (diferença máxima 0.0), logo repete tudo, inclusive os erros.
- 0 usado como "não medido": 832 linhas com ambos a 0; mais 692 com dew point = 0 e temperatura > 40 °F.
- 31 temperaturas > 130 °F (133 a 203 e 3005).
- 268 linhas com dew point > temperatura (impossível).

**Gráficos:** pico enorme em 0 nos dois histogramas; no scatter há uma linha horizontal em dew point = 0 e um ponto em (0,0). Fatal rate nas linhas com 0: 4-6%, contra 18% nas normais.

**Decisão:**
- Remover `wx_temp_c`.
- Marcar `wx_temp` e `wx_dew_pt` como missing quando ambos forem 0, quando dew point = 0 com temperatura > 40 °F, quando temperatura > 130 °F e quando dew point > temperatura.
- Guardar esta informação como indicator, juntamente com a do altímetro (ver 5.2), porque a fatal rate é muito diferente nestas linhas.
- Questão: o spread (temperatura - dew point) pode ser mais útil do que os dois valores isolados (spread pequeno = nevoeiro ou nuvens baixas). Testar após a limpeza.
- Preencher os restantes missing com a **mediana** do training set.

---

## Sobre Altimeter

**Normal:** pressão em inHg, padrão **29.92**, na prática **entre 28 e 31** (pico muito estreito).

**Mal:**
- 1510 linhas com 0 (não medido).
- 54 linhas à volta de 3000: são pressões normais sem a vírgula (divididas por 100 dão 29.37 a 30.53).
- 4 valores impossíveis sem reparação (16, 20.05, 230.16, 1974.02).
- Os 0 coincidem com outras colunas meteorológicas em falta (771 com temp = 0, 875 sem wind speed, 942 com wind dir = 0): é "sem observação meteorológica".

**Gráficos:** pico à volta de 29.92 a 30.2. Os 0 por ano descem de 282 (2008) para ~30 por ano (com um pico de 88 em 2019). Fatal rate com altimeter = 0: 5.6% (contra 18.2%).

**Decisão:**
- Altimeter a rondar os 3000: dividir por 100.
- Altimeter = 0 ou qualquer outro valor impossível: marcar como missing.
- Criar um indicator `no_weather` (altimeter = 0), porque assinala um grupo de acidentes com uma fatal rate muito diferente e está relacionado com outras colunas meteorológicas (temperature, dew point, wind).
- No NB1 devemos verificar se é melhor usar um único indicator para todas as colunas meteorológicas, em vez de um para cada.
- Preencher os restantes valores com a **mediana** do training set.

---

## Sobre Engine Power, Horsepower ou Pounds of Thrust

**Normal:** HP para piston (REC), turboprop (TP) e turboshaft (TS); lbs de thrust para jets (TF, TJ). Medianas: REC 179, TP 754, TS 519, TJ 3424, TF 8926.

**Mal:**
- Duas unidades na mesma coluna, logo valores não comparáveis entre `eng_type`.
- 171 linhas com `eng_power` = 0 (147 REC, 12 TF, 4 TP, 2 TJ, 6 sem eng_type).
- 1801 missing (10.6%); 602 sem `eng_type`, e 30 delas têm potência.
- Extremos: TS com 75552, REC com 3293.

**Gráficos:** um pico à volta de 200 e uma cauda longa à direita (os jets); no boxplot por tipo as escalas ficam separadas por ordens de grandeza. Fatal rate: TP 22.9%, TS 19.2%, REC 16.9%, TF 9.2%.

**Decisão:**
- Não usar `eng_power` tal como está. Dividir em duas features: `hp` (para motores medidos em horsepower) e `thrust_lbs` (para TF e TJ), para que cada coluna tenha apenas uma unidade. A outra opção é um rank da potência dentro de cada `eng_type`.
- `eng_power` = 0 passa a missing, depois preencher com a mediana dentro do engine type (apenas no training set) e criar um missing indicator.
- Questão: as 30 linhas com potência mas sem `eng_type`. Temos de decidir em qual das duas features entram (talvez olhando para a aircraft category).
- Usar escala logarítmica (log scale) ou um cap para a potência, devido aos valores extremos, pelo menos para os modelos sensíveis a eles.

---

## Sobre Wind e Gusts

**Normal:** `wind_dir_deg` de 1 a 360; `wind_vel_kts` tipicamente 0 a 25 (mediana 7); `gust_kts` = 0 quando não há rajada (é um 0 verdadeiro).

**Mal:**
- `wind_dir_deg` = 0 em 4387 linhas; 3543 delas sem wind speed, logo placeholder. Só 51 são calmaria real. As 793 com velocidade > 0 podem ser vento variável (não confirmado).
- `wind_vel_kts`: 21% missing; 8 valores > 50 kts (até 185).
- `gust_kts`: um valor de 1077; 24 rajadas abaixo da velocidade do vento.
- `gust_ind` contradiz o dicionário: T aparece em 10934 linhas mas só 5 têm rajada; F é mistura (2616 com rajada, 3429 sem). Não é fiável.

**Gráficos:** direção sem os zeros é razoavelmente espalhada; velocidade concentrada em baixo; poucas rajadas. Quase sem relação com o target (mediana 7 kts nos dois grupos; fatal rate 16.3% com rajada vs 17.1% sem).

**Decisão:**
- `wind_dir_deg` = 0 com wind speed missing passa a missing (é o grupo "no weather" do 5.2). Para o 0 com velocidade > 0, deixar a questão em aberto.
- A direção é circular (359 está perto de 1): transformar com seno e cosseno ou em grupos, se for usada.
- `wind_vel_kts` > 100 e `gust_kts` = 1077 passam a missing; as 24 rajadas abaixo do vento: missing ou igual à velocidade do vento.
- Criar `has_gust` = `gust_kts` > 0, a partir do número e não do `gust_ind`.
- Missing de wind speed: indicator + mediana do training set.

---

## Sobre Visibility e Cloud Ceiling

**Normal:** visibilidade até 10 milhas (83% têm exatamente 10); teto de nuvens em pés, com 0 = sem teto (76% das linhas, 0 verdadeiro).

**Mal:**
- `vis_sm`: 4500 e 5000 são impossíveis; 445 linhas > 10 (20, 15, 30, 50...), possíveis em algumas estações; 721 missing.
- `sky_ceil_ht`: 241340 e 40331 impossíveis.
- Inconsistências com `sky_cond_ceil`: 114 com BKN/OVC/VV mas altura 0; 21 com NONE mas altura > 0; 15 sem `sky_cond_ceil` mas com altura.

**Gráficos:** são as duas features mais fortes. Fatal rate por visibilidade: ≤1 milha 51%, 1-3 43%, 3-5 38%, 5-10 24%, =10 16%, >10 9%. Por teto: até 500 ft 57%, 500-1000 52%, 1000-3000 31%, sem teto 14.5%, >10000 ft 14.4%.

**Decisão:**
- `vis_sm` = 4500 e 5000 passam a missing. Os outros valores > 10 ficam (têm fatal rate própria de 9%); testar cap em 10 + indicator "acima de 10" e log scale para modelos que precisem.
- `sky_ceil_ht` > 40000 passa a missing. Manter o 0 (é real) e criar `has_ceiling`; log scale na altura para os modelos lineares.
- Questão: BKN/OVC/VV com altura 0 (114 linhas): provavelmente a altura é missing.
- Manter ambas no modelo (são fortes). Missing de visibilidade: indicator (fatal rate ~9% quando falta) + mediana.

---

## Sobre Distance to Airport e Airport Elevation

**Normal:** `apt_dist` em milhas: 77% das linhas têm 0 (acidente no aeroporto, 0 real), quase todas as restantes entre 1 e 25. `apt_elev` em pés, tipicamente entre 0 e 6000.

**Mal:**
- `apt_dist`: 52 valores > 500 (até 7208), impossíveis em milhas. Se forem pés dão 0.12 a 1.37 milhas, e a fatal rate (9.6%) bate com acidentes no aeroporto (14.1%), logo provavelmente são pés. 18 linhas entre 101 e 500 são duvidosas.
- `apt_elev`: 34% missing, e 5586 dos 5712 estão em linhas com `apt_dist` = 0 (missing não aleatório). Um valor 33333 (placeholder).
- Os valores > 9000 ft (9028 a 9955) e os 3 negativos (-214 a -224) parecem aeroportos reais (muito altos / Death Valley), por isso ficam.

**Gráficos:** distância: quanto mais longe, mais fatal (0: 14%, 1: 22%, 2-5: 33%, 6-100: 36-40%). Elevação: fatal rate quase plana (10-15%).

**Decisão:**
- `apt_dist` > 500: dividir por 5280 (pés para milhas), como hipótese suportada pela fatal rate. As 18 linhas entre 101 e 500 ficam como estão.
- Manter os zeros e criar `at_airport` (`apt_dist` = 0). Testar `log1p` ou grupos (0, 1, 2-5, 6-25, >25).
- `apt_elev` = 33333 passa a missing; os restantes ficam. Mediana do training set + indicator (o missing está ligado a `apt_dist` = 0 e a uma fatal rate diferente).
- `apt_elev` tem pouca relação com o target.

---

## Sobre Aircraft Year, Seats e Number of Engines

**Normal:** `acft_year` entre ~1930 e o ano do acidente (+1 ou +2 é normal, é o ano-modelo); `total_seats` 1 a 10 na maioria (modas 2 e 4), aviões de linha com 50 a ~600 são reais; `num_eng` 1 ou 2 (0 só em gliders e balloons).

**Mal:**
- `acft_year`: 40% missing (em todas as categorias, não depende do tipo de avião); um 0 e dois anos antes de 1903 (1062 e 163). 86 "depois do acidente", mas 75 por 1 ano e 10 por 2: não são erros (só há 1 com 3 anos).
- `total_seats`: 7% missing; 37 com 0; 4 com > 600 (8300, 3300, 2500, 1979).
- `num_eng`: 485 missing; 2 aviões com 0 motores (erro); 241 gliders/balloons com 0 (real).

**Gráficos:** fatal rate por idade do avião é plana (17-20%) até 60 anos e desce para 11.6% acima disso. Seats: >50 lugares só 0.9% fatais; 5-6 lugares 23.6%. Motores: 2 motores 22.2% vs 1 motor 16.5%.

**Decisão:**
- `acft_year` = 0 e < 1903 passam a missing; anos depois do acidente só são erro se a diferença for > 2 anos. Criar `aircraft_age` = `ev_year` - `acft_year` (mínimo 0) em vez do ano. Missing: indicator + mediana.
- `total_seats` = 0 e > 600 passam a missing; os valores 50 a 600 ficam. Testar log ou grupos.
- `num_eng`: os 2 aviões com 0 passam a missing; missing com mediana ou moda por categoria + indicator.

### seat_vintage_ratio (exigido pelo enunciado)

**Mal:** 45% missing, um valor infinito (`acft_year` = 0), correlação de 0.95 com `total_seats` (é praticamente o nº de lugares noutra escala) e relação fraca com o target (0.013).

**Decisão:**
- Criar só depois de limpar `total_seats` e `acft_year`, sem criar infinitos.
- Manter no modelo final (como o enunciado exige) e justificar com estes números: adiciona pouca informação além de `total_seats`.

---

## Sobre Pilot Age

**Normal:** 14 a 100 anos; a fatal rate sobe de forma suave com a idade.

**Mal:**
- 12 idades impossíveis: quatro 0, um 1, um 7 e seis > 100 (115, 116, 144, 181, 199, 214).
- 122 missing (0.7%), com fatal rate de 11.5%.
- 14 e 15 anos (11 linhas) são limite, mas ficam.

**Gráficos:** fatal rate: 14-20 anos 10.6%, 21-30 11.8%, 31-40 15.5%, ~17% de 41 a 60, 19-20% acima de 60. Cresce depressa nos jovens e estabiliza depois dos 60 (não é linear).

**Decisão:**
- Idades < 14 e > 100 (12 linhas) passam a missing e vão para a mediana junto com os 122 missing (manter o indicator, por causa da fatal rate mais baixa).
- Manter como número (árvores) e testar grupos de idade para os outros modelos.

---

## Sobre Hour of the Accident

**Normal:** 0 a 23, mas é **circular** (23h está ao lado das 0h), não uma quantidade.

**Mal:**
- O dicionário diz "hora local", mas os dados parecem **UTC**: há 1216 acidentes com `light_cond` = DAYL entre as 0h e as 5h, e a percentagem de luz do dia é 91-99% das 12h às 22h mas só 14-28% entre as 4h e as 10h. Os EUA estão 5 a 8 horas atrás do UTC, o que explica o desfasamento. Não dá para confirmar (não há fuso nem estado).
- 19 missing.

**Gráficos:** acidentes concentrados das 12h às 23h e das 0h às 2h (mínimo 5h-10h). Fatal rate alta entre as 4h e as 10h (26-45%) e 13-18% à tarde/noite. Por `light_cond`: NDRK 55.7%, NITE 29.6%, DAYL 15.5%.

**Decisão:**
- Não tratar `ev_hour` como número normal: testar seno/cosseno ou grupos de horas, e a combinação com `light_cond` e `ev_month` (a luz é a informação local real).
- Não criar features que assumam hora local (horário de trabalho, noite de fim de semana...) a partir de `ev_hour`. Referir isto no relatório.
- 19 missing: categoria "missing" (se for em grupos) ou mediana, com indicator.
