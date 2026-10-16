# CLAUDE.md — Corpus quechua chanka médico (INF657, PUCP)

> **Lee este archivo completo antes de hacer cualquier cosa.**
> Resume los acuerdos de la estrategia del proyecto (14 de octubre de 2026), donde se revisaron los Excel, el manual SOCEMURP y se definió la estrategia. Aquí no debe perderse nada.
> Si algo de este archivo no coincide con lo que encuentres en los archivos reales, **no adivines**: anótalo en `04_reportes/DECISIONES_TOMADAS.md` y, si cambia la composición de los bloques, pregúntale a la coordinación del proyecto antes de seguir.

---

## Índice

1. El proyecto
2. Problemas y criterios del proyecto
3. Decisiones tomadas (definitivas)
4. Decisiones pendientes (con valor por defecto)
5. Inventario de fuentes y hallazgos
6. Errores conocidos (para calibrar tus chequeos)
7. Estructura de la carpeta
8. Diseño de los archivos de salida
9. Plan de trabajo por fases
10. Reglas de limpieza (preprocesamiento)
11. Priorización y armado de bloques
12. Revisión automática de calidad
13. Definición de terminado (checklist final)
14. Reglas de trabajo y qué NO hacer (incluye 14.1 Puntos de retorno y 14.2 Esfuerzo/ultracode)
15. Referencias
16. Glosario

---

## 1. El proyecto

- **Curso:** INF657 – Ingeniería y Gestión del Conocimiento (maestría, PUCP). Proyecto grupal de 15 personas.
- **Objetivo:** apoyar la interacción **paciente quechuahablante ↔ médico** en **quechua chanka** (variedad de Ayacucho, Apurímac y Huancavelica; código ISO `quy`).
- **Dirección del sistema: bidireccional.**
  - El paciente habla quechua → el médico recibe español (reconocimiento de voz + traducción).
  - El médico habla español → el paciente recibe quechua.
  - Por eso sirven tanto las frases del médico como las del paciente. Las del paciente son las que más faltan.
- **Esta etapa es SOLO el corpus.** Los detalles técnicos de los modelos (STT, traducción, despliegue) se definen después. Pero el corpus debe quedar listo para que, con el **bloque 1**, el equipo pueda ir de modelo a despliegue mientras se traducen y graban los siguientes bloques.

### Equipos (hoja `Equipos` de `Corpus_Equipos_1.xlsx`)

| Grupo 1 – Traducción Principito | Grupo 2 – Corpus Quechua | Grupo 3 – Corpus Médico |
|---|---|---|
| Jorge Fatama | Christian Rosales | **Coordinación del proyecto** |
| Neftali Tejada | Gustavo Elmer | Marshall |
| Andres Flores | Jose Avalos | María De La Guarda |
| | Ronny Huerta | Kimberly Chávez |
| | Fernando De La Cruz | Flavio Huaman |

En el vocabulario unificado aparecen las columnas "Marshall", "Kim 1" y "Kim 2": son tres archivos de revisión del Grupo 3 que se fusionaron. En las revisiones de Kim y Marshall se utilizó el mismo prompt para revisar el corpus y extraer lo útil del libro de semiología; luego otro compañero unificó los tres Excel.

### Colaboradores externos (cuello de botella)

- **Traductor español → quechua chanka** (profesor de quechua).
  - Trabaja **solo en Word**.
  - **No traduce en vivo:** recibe el bloque con anticipación y llega a la sesión con todo traducido.
- **Grabador:** lee en voz alta cada oración **primero en español y luego en quechua**. Idealmente solo graba; puede anotar observaciones.

### Entorno de trabajo y comunicación

- Idioma de trabajo: español. Responde de forma simple y directa, sin jerga innecesaria.
- Conocimientos de trabajo: Python.
- Entorno de trabajo: Windows. Existen otros entornos de Python (`inf659_env`, `.venvs`) ajenos al proyecto: **no los uses ni los modifiques**.

---

## 2. Problemas y criterios del proyecto

Por qué existe este trabajo:

1. **Todo está suelto.** Cada grupo avanzó por su cuenta. Nada está consolidado ni dividido para sesiones reales de 3–4 horas con el traductor y el grabador.
2. **Sesgo y "gold".** Parte del quechua viene de un **traductor automático** (Grupo 1) o de **normalizar con reglas quechua cusqueño, collao o boliviano** (Grupo 3). Eso NO es dato "gold". El corpus debe evitar el sesgo de las traducciones automáticas.
3. **La prosa bíblica no sirve para grabar.** Al Grupo 2 le dijeron que oraciones de la Biblia (AmericasNLP) no aportan para esto.
4. **Poco tiempo.** Hay que trabajar por bloques en paralelo: con un bloque ya se avanza el modelo mientras se traduce y graba el siguiente.
5. **Excels gigantes que no ayudan a la vista.** Se debe conservar la trazabilidad de cada elemento, pero los bloques deben verse limpios. El origen va en otra pestaña (ver §8).
6. **El traductor solo maneja Word**, y el resultado tiene que volver al Excel.
7. El equipo discutió si dar los borradores automáticos al traductor. Criterio de calidad: no son gold. Utilidad para la revisión: ayudan si coinciden. **Decisión: sí se dan, con las reglas de §3.**

---

## 3. Decisiones tomadas (definitivas)

| # | Decisión | Detalle |
|---|---|---|
| D1 | **70 % general / 30 % médico en cada bloque** | Lo indica el profesor por su experiencia. El 70 % enseña al modelo las "reglas" del quechua (morfología, sufijos, estructura). El 30 % es la especialización médica. Todo es entrenamiento ("todo es train"). |
| D2 | **200 oraciones por bloque** | = **140 generales + 60 médicas**. |
| D3 | **4 sublotes de 50 por bloque** | Cada sublote ≈ 35 generales + 15 médicas (mantiene 70/30). Equivale a ~1 hora de grabación cada uno. Si la sesión se corta, se cierran sublotes completos. |
| D4 | **Parte médica ≈ mitad médico, mitad paciente** | ~30 frases del médico y ~30 del paciente por bloque. Cada pregunta del médico va **con sus respuestas en el mismo sublote**. |
| D5 | **El traductor siempre va un bloque adelante** | Si la sesión va bien, en la misma reunión pasan al siguiente bloque. Por eso cada sesión necesita **dos bloques traducidos**. **Primera entrega al traductor = B01 + B02.** |
| D6 | **Se le dan borradores al traductor** | En el Word, la celda "Quechua" viene **prellenada con el borrador** y él corrige ahí mismo. Luego se compara automáticamente borrador vs. final (porcentaje de edición). |
| D7 | **Oraciones de control en B01** (recomendado, activo por defecto) | ~15 oraciones de B01 que **sí tienen borrador** se entregan con la celda Quechua **vacía**. Sirve para medir el "anclaje": si con borrador corrige mucho menos de lo que difiere su traducción libre, el borrador lo está sesgando. Si en las oraciones con borrador reescribe más del 50 %, los borradores no ahorran tiempo y se dejan de dar. Se puede desactivar en `config.yaml`. |
| D8 | **Regla del gold** | Ningún borrador entra al entrenamiento ni a la evaluación como verdad. **Gold = validado por el traductor y luego grabado.** Si al grabar el hablante dice la frase distinto a lo escrito, **se transcribe lo que dijo** y se anota (la transcripción tiene que coincidir con el audio). |
| D9 | **Convención ortográfica = alfabeto oficial del quechua chanka** | 3 vocales (a, i, u) en palabras quechuas; sin glotalizadas ni aspiradas; sin c/qu/j/hu castellanas. Las reglas detalladas están en §10.3 (son las mismas que aplicó el vocabulario unificado). Falta confirmar con el traductor (P3). |
| D10 | **Fuente médica principal = vocabulario unificado** | `Vocabulario_Quechua_Chanka_unificado_2.xlsx` es la última versión: toma todo el Grupo 3 de `Corpus_Equipos` y agrega cosas. `Corpus_Construido.xlsx` y la hoja Grupo 3 de `Corpus_Equipos_1.xlsx` quedan **solo como referencia** (están superados). |
| D11 | **Fuente general = Grupo 1 (Principito) + Grupo 2** | El profesor dice que las oraciones del Principito "valen bastante": **tienen prioridad**. El unificado NO trae estas hojas; se sacan de `Corpus_Equipos_1.xlsx`. AmericasNLP 2021 **no se graba tal cual** (ver P4). |
| D12 | **Bloques limpios + origen en otra pestaña** | Ver §8. Nada de columnas ocultas ni Excels de 30 columnas en la vista principal. |
| D13 | **Dónde se ejecuta** | Claude Code en el equipo de trabajo (Windows), dentro de esta carpeta. La conversación de estrategia fue en otra sesión. Este archivo es el traspaso. |

---

## 4. Decisiones pendientes (con valor por defecto)

Si no hay respuesta de la coordinación del proyecto, **usa el valor por defecto** y regístralo en `DECISIONES_TOMADAS.md`.

| # | Pendiente | Por defecto |
|---|---|---|
| P1 | **¿Se aparta un conjunto de prueba?** El profesor dijo "todo es train". Se recomendó igual apartar un conjunto que el modelo no vea. | Todas las filas con `Split = train`. Además, una columna `Test_sugerido` (Sí/No) que marca un **10 % estratificado** de cada bloque (14 generales + 6 médicas) para poder activarlo si se confirma. |
| P2 | Fecha de la primera sesión y con cuántos días de anticipación recibe el traductor el Word. | Desconocido. Generar B01 y B02 lo antes posible. |
| P3 | ¿El traductor usa el alfabeto oficial (3 vocales)? | Asumir que sí. Las instrucciones del Word se lo piden explícitamente. |
| P4 | ¿Se usan oraciones de AmericasNLP 2021 para la parte general? | **No**, solo como léxico de referencia. Si la parte general no alcanza para los bloques planificados, **pregúntale a la coordinación del proyecto** antes de usarlas, y solo con oraciones cortas no religiosas filtradas. |
| P5 | Formato de audio. | WAV, 16 kHz, mono, 16 bits (habitual en reconocimiento de voz). Confirmar con el equipo de modelo. |
| P6 | Origen real de las filas del Grupo 2 (¿ejemplos del diccionario MINEDU o ejercicios generados?). | Clasificar con la heurística de §5.2 y verificar contra el PDF del diccionario si está en la carpeta. Si no se puede verificar, marcar `Origen_verificado = No`. |
| P7 | Audios de Allin Kawsay (`*.mp3`). | **Resuelto: no se usan** (decisión del proyecto). No inventariarlos ni procesarlos. |

---

## 5. Inventario de fuentes y hallazgos

Cifras verificadas en la revisión anterior. **Úsalas para comprobar que estás leyendo la misma versión de cada archivo.** Si difieren mucho, avisa a la coordinación del proyecto.

> ⚠️ Varios Excel usan **fórmulas** en la columna N° (`=A2+1`, `=CONCATENATE("S1-",B2)`). Al leerlos con openpyxl o pandas pueden salir como texto de fórmula o vacíos. **No dependas de esas columnas**: genera tus propios IDs. Las cifras de la hoja `Resumen` del unificado también son fórmulas (`COUNTIF`): recalcúlalas tú.

### 5.1 `Vocabulario_Quechua_Chanka_unificado_2.xlsx` — parte médica, versión vigente

- **Hojas:**
  - `Resumen`: criterios de chanka aplicados, significado de cada estado y referencias.
  - `Vocabulario_unificado`: **1 528 filas**, 11 columnas. IDs `QCH-0001…`
  - `Trazabilidad`: 1 542 filas, 30 columnas, con el detalle por código original de Marshall, Kim 1 y Kim 2.
- **Columnas de `Vocabulario_unificado`:** `Id_unificado`, `Español (palabra o frase)`, `Quechua_final (chanka)`, `quechua_marshall`, `quechua_kim1`, `quechua_kim2`, `Observaciones_finales`, `Estado`, `Sección`, `Fuente_original`, `Códigos_origen`.
- **Ninguna fila fue validada por un hablante.** La propia hoja lo dice: "Final" significa "unificado y normalizado con reglas de chanka", no gold.
- **Estados:**

| Estado | Filas |
|---|---|
| Final – corregido/normalizado a chanka | 522 |
| Pendiente – sin traducción chanka | 361 |
| Final – coincide en los Excel | 281 |
| Final – forma del libro compatible con chanka | 122 |
| Revisar – duda de traducción | 89 |
| Revisar – adaptación propuesta | 72 |
| Final – única fuente | 58 |
| Final – fuente chanka oficial | 12 |
| Pendiente – no usar (ver observación) | 11 |

- **Fuentes (`Fuente_original`):**

| Fuente | Filas | Nota |
|---|---|---|
| Lopera Quiroga (2020), *Manual de Semiología en Quechua* | 566 | **Quechua de Puno / collao.** Se había supuesto que de aquí solo se tomó el español, pero **409 filas tienen quechua derivado de este libro** (287 "corregidas a chanka" por reglas + 122 "compatibles"). Son borradores, no chanka real. |
| Allin Kawsay (INS/MINSA) | 510 | **Fuente confiable según el equipo** (es una sola página web). Variedad sin confirmar. Igual se revisan posibles errores de transcripción (las 521 filas "Validar escritura" del Grupo 3 original, ver §5.2). |
| OPS/OMS Bolivia (2013), *Diálogo médico paciente en quechua* | 234 | **Solo español** (bien: no se tomó el quechua boliviano). El español tiene giros bolivianos que hay que adaptar. |
| Corpus original del equipo | 117 | Es la extracción del **manual SOCEMURP** (= `Corpus_Construido`). |
| Pregunta añadida por Kim 1 (cobertura clínica) | 43 | Solo español. |
| Farfán Cantero (2001), revista SITUA | 24 | Probablemente cusqueño. |
| Manual del quechua chanka para la administración de justicia (MinCul) | 13 | Fuente chanka oficial. |
| YouTube | 9 | |
| Afiche MINSA/MinCul «Lavado de manos» (chanka) | 6 | Fuente chanka oficial. |
| MINSA | 4 | |
| Manual de quechua médico SOCEMURP-FAMURP (2021) | 1 | |
| OMS (2009), Lista de verificación de cirugía | 1 | |

- **Composición:**
  - 515 palabras sueltas (34 %); 323 de 2–3 palabras; 690 de 4 o más palabras (máximo 44).
  - ~615 preguntas (casi todas del médico).
  - Solo **~47 frases del paciente** en primera persona (heurística).
  - 1 156 filas con quechua.
- **Lo bueno:** la revisión de Marshall y Kim detectó y corrigió todos los errores del manual SOCEMURP y de su transcripción que se listan en §6. Como **base de borradores** es lo mejor que hay.
- **Secciones (`Sección`):** numeradas `01 Presentación y saludo` … `24 Vocabulario médico (palabras sueltas)`, más algunas con otra numeración (`04. Motivo, evolución y dolor`, `03. Antecedentes y entorno`…) y anexos de Lopera (`Lopera – Anexo. …`). Mapeo a etapas de consulta en §11.3.

### 5.2 `Corpus_Equipos_1.xlsx` — corpus original de los tres grupos

| Hoja | Filas | Qué es |
|---|---|---|
| `Equipos` | — | Integrantes (tabla de §1). |
| `Grupo 1 - Principito` | **113** (IDs `EL-0001…`) | Oraciones del Principito en español: **valen mucho según el profesor**. El quechua lo generó un **traductor automático**: *Rosettia GSPO-NLLB* (`Thermostatic/rosettia-quy-gspo-nllb13b-merged`, basado en NLLB-200 1.3B). Se nota en préstamos del español: «Carnerota» (cordero), «piensani», «lliwtam entienden», «amistadniymi». **Solo borrador.** La fila EL-0001 trae una nota de plantilla en Observaciones ("opcional: fuente / fila de ejemplo, borrar al usar"): ignórala. |
| `Grupo 2 - Corpus Chanka` | **676** (IDs `F-0001…`, 672 con quechua) | Todas dicen ": Yachakuqkunapa simi qullqa (MINEDU). Pendiente de validar con hablante nativo." Pero **507 empiezan en minúscula y 396 empiezan con pronombre** ("nosotros no nadamos en el río", "ellas no cierran la puerta"): parecen **ejercicios de conjugación generados**, no ejemplos reales del diccionario. Unas ~170 (mayúscula inicial, frases variadas) sí parecen ejemplos del diccionario. Útiles para enseñar reglas, pero hay que verificar el origen (P6). Hay filas vacías al final. |
| `Grupo 3 - Corpus Medico` | 685 | Superado por el unificado. **521 filas dicen "Validar escritura"** y parecen transcritas de oído: «tuyu» (tullu), «ñorton» (ñutqu), «qolqe» (qullqi), «runto» (runtu), «siyu» (sillu), «yawa» (yawar), «stardin manchu». Hay referencias a audios (`222. Zancudo.mp3`) y a fuentes web. Una fila trae un párrafo larguísimo de instrucciones de micronutrientes. |
| `Grupo 3 - Términos médicos` | 58 | Términos del manual SOCEMURP (pp. 52–57). |

### 5.3 `Corpus_Construido.xlsx`

- **111 filas** extraídas a mano del manual SOCEMURP (secciones 9, 11, 14).
- **109 ya están dentro del unificado**, con los errores corregidos.
- Usarlo solo para cruzar información. **No es fuente.**

### 5.4 Manual SOCEMURP (PDF, 78 páginas)

- *Manual de Quechua médico SOCEMURP* (2021), de estudiantes de medicina de la Universidad Ricardo Palma, con asesoría de una docente del Centro de Idiomas URP. Declara **variante chanka** (Apurímac, Ayacucho, Huancavelica).
- **Es solo imagen, sin capa de texto.** Para consultarlo, renderiza las páginas a PNG (pypdfium2) y míralas.
- **Mapa de páginas:**
  - 1–26: portada, contenido, introducción, alfabeto, saludos, colores, números, familia, calendario, gramática.
  - 27–30: formación de oraciones.
  - **31–32: preguntas de filiación.**
  - 33: instrumentos.
  - **34–51: interrogatorio** (dolor y deposiciones).
  - **52–57: signos, síntomas y enfermedades.**
  - **58–64: frases médico–paciente** (órdenes de examen y recomendaciones).
  - 65–72: partes del cuerpo, léxico, especialidades.
  - 73–78: afiches (antimicrobianos, COVID, ODS).
- **Contenido clínico útil:** ~110 oraciones y ~150 palabras. Casi todo son **preguntas del médico** sobre dolor y deposiciones, más órdenes de examen respiratorio y 6 recomendaciones.
- **No alcanza para una consulta.** Faltan respuestas del paciente, fiebre, vómitos, alergias, medicamentos, embarazo, niños y emergencias.
- **No es gold:** tiene errores propios (§6).
- Ya fue extraído casi por completo. Su valor es ser **semilla chanka** y **esqueleto del flujo de consulta**.

### 5.5 AmericasNLP 2021 (español–quechua, `quy`)

- Según el equipo, son ~180k oraciones. Verifica la cifra al cargar y anota qué archivos son (train/dev/test).
- `quy` = quechua ayacuchano = **chanka**: la variedad coincide.
- **Problemas:**
  - Dominio mayormente religioso (JW300 / Biblia).
  - Es texto traducido.
  - **No tiene audio.**
- **Usos permitidos:**
  - Léxico de referencia: ¿la palabra existe en chanka escrito?
  - Frecuencias.
  - Más adelante, preentrenamiento de texto.
- **No se graba tal cual** (P4).
- **Según el README del repositorio:**
  - `train.*` = **solo JW300 quy** (Testigos de Jehová). Léxico de referencia; nunca se graba.
  - `dict.*` = **diccionario oficial MINEDU (quy)** + Dict_misc (Diego Huarcaya). **Úsalo para verificar P6**: qué filas del Grupo 2 son ejemplos reales del diccionario.
  - `dev.*` / `test.*` = **quechua sureño estándar** (mezcla rasgos cusqueños y ayacuchanos): referencia general, **no chanka puro**. Solo existe `test.es` (sin quechua).
  - `parallel_data/` = solo se incluyó `es-quy` (fuentes separadas: JW300, MINEDU, Dict_misc). Úsalo para identificar el origen exacto de cada oración. Se excluyeron a propósito `en-quy`, `en-quz` y `es-quz` (inglés y cusqueño).

### 5.6 Diccionario MINEDU (si está en la carpeta)

- *Yachakuqkunapa Simi Qullqa – Ayakuchu Chanka Qichwa simipi*: diccionario escolar del MINEDU para el chanka (repositorio MINEDU, handle `20.500.12799/10380`).
- **Usos:**
  - Verificar que las palabras existen y están bien escritas en chanka.
  - Decidir qué filas del Grupo 2 son ejemplos reales del diccionario (P6).
- Si el PDF no tiene texto, consulta páginas puntuales como imagen. No intentes procesarlo entero.

### 5.7 Trabajo previo de un compañero (solo precedente)

En la carpeta `Trabajo - Otro Compañero/` hay un EDA anterior: `[Vibe]EDA_Corpus_NLP.ipynb` + `Corpus_Recopilado.xlsx` (y quizá `flashcards.xlsx` y `resultados_vibe/`).

- **Decisión del proyecto: es solo un precedente.** No es lo acordado y **será reevaluado**. Tu EDA es el que manda: hazlo con tus propios criterios (§9.1), no copies sus decisiones, filtros ni su preselección.
- Contexto para que no te confunda: `Corpus_Recopilado.xlsx` son las 3 hojas de `Corpus_Equipos_1.xlsx` con la **hoja médica antigua** (no el unificado), y su preselección fue 100 + 100 + 100 por cobertura de palabras del español de unas flashcards. Nada de eso aplica (D1–D4, D10).
- Uso permitido: como mucho, mencionarlo en `EDA.md` en un párrafo ("existe un EDA previo; diferencias principales: …"). No lo uses como fuente de datos ni de alertas.

---

## 6. Errores conocidos (para calibrar tus chequeos)

Tus chequeos automáticos deberían detectar casos como estos. Úsalos como **pruebas** de tus reglas.

**Errores del propio manual SOCEMURP** (ya corregidos o marcados en el unificado):

| Texto | Problema |
|---|---|
| «Qayna wata tumpallata wiksay nanachkan» ↔ "Desde un mes me duele mucho mi estómago" (p. 32) | Desalineado: dice "desde el año pasado me duele un poco". Unificado: `QCH-0037`, "Revisar". |
| «Amam pisi kachiyuq mikunata mikunkichu» ↔ "No debes comer comida con mucha sal" (p. 63) | *pisi* = poca: sentido invertido. Unificado: `QCH-0111`, corregido a *achka*. |
| «¿Achkhachu karqa?» (p. 51) | Aspirada *kh*, que no existe en chanka. Unificado: `QCH-0086`, corregido. |
| «¿Kunallanmantachu nanasunki?» usado para "¿Desde hoy nomás te duele?" y para "¿Es la primera vez que te duele?" | El mismo quechua para dos significados. Unificado: `QCH-0050`, "Revisar". |

**Errores de transcripción** en `Corpus_Construido` (ya corregidos en el unificado):

| Escrito | Correcto | Unificado |
|---|---|---|
| «llinllachu» | Allinllachu | `QCH-0010` |
| «Itaq kanki» | Pitaq kanki | `QCH-0013` |
| «mayllijunayki» | mayllikunayki | `QCH-0110` |
| «Imaynatoq» | Imaynataq | `QCH-0063` |
| «nanasuki» | nanasunki | — |

**Traductor automático (Grupo 1):** «Carnerota», «piensani», «lliwtam entienden», «amistadniymi», «Dibujoyniyqa».

**Transcripción de oído (Grupo 3 original):** «tuyu», «ñorton», «qolqe», «runto», «siyu», «yawa», «stardin manchu», «waranqa hukniyoq», «qellqaytay yachankichu».

**Rasgos no chanka que aparecen en las fuentes:**
- progresivo *-sha-* («kashanki»);
- validador *-n* tras vocal («Imaykin», «manan»);
- glotalizadas y aspiradas («p'acha», «qhaway»);
- *ñoqanchis*;
- *-qti-* / *-jti-*;
- léxico como «unu» (por *yaku*) o «uhyay» (por *upyay*).

---

## 7. Estructura de la carpeta

### 7.1 Archivos disponibles (estado real al 14-oct-2026, unidad `D:`)

```
D:.
|   CLAUDE.md                                         ← este archivo
|   Vocabulario_Quechua_Chanka_unificado (2).xlsx     ← unificado médico (D10, §5.1)
|   Corpus_Equipos (1).xlsx                           ← corpus de los 3 grupos (§5.2)
|   Corpus_Construido (1).xlsx                        ← extracción SOCEMURP, solo referencia (§5.3)
|   PDF Manual de Quechua Socemurp Compress _ ILIDE.INFO Platform PDF Viewer (1).pdf   ← manual SOCEMURP (§5.4, 78 pp., solo imagen)
|   Yachakuqkunapa simi qullqa. Ayakuchu Chanka Qichwa simipi (1).pdf   ← diccionario MINEDU (§5.6)
|   ManualSemiologiaQuechua-2020.pdf                  ← Lopera Quiroga 2020 (Puno/collao)
|   entrevistaquechua_spa.pdf                         ← probablemente OPS/OMS Bolivia 2013 (verificar por contenido)
|   Quechua médico.html                               ← página web guardada: Allin Kawsay o Farfán/SITUA (verificar por contenido)
|   manualparaelempleodelquechuachankaenlaadministraciondejusticia.pdf   ← manual MinCul (chanka oficial)
|   AFICHE_COVID 19 LAVADO DE MANOS MINSA quechua  chanka.pdf            ← afiche MINSA (chanka oficial)
|   8361447-diabetes_mellitus_quechua.pdf             ← diabetes en quechua (gob.pe)
|   5660130-manejo-de-paciente-con-diabetes-mellitus-2.pdf  ← diabetes en español (gob.pe)
|   arbol.txt                                         ← listado de la carpeta (ignorar)
|
+---AmericasNLP                                       ← §5.5
|   |   README.md, train.es/.quy, dev.es/.quy, dict.es/.quy, test.es
|   \---es-quy                                       ← fuentes separadas
|           jw300.es-quy.es / .quy                    (religioso)
|           minedu.quy-es.es / .quy                   (diccionario MINEDU → clave para P6)
|           dict_misc.quy-es.es / .quy                (Diego Huarcaya)
|
\---Trabajo - Otro Compañero                          ← solo precedente (§5.7)
        Corpus_Recopilado.xlsx
        [Vibe]EDA_Corpus_NLP.ipynb
```

- **Todos los archivos de arriba son FUENTES: solo lectura.** No los muevas, renombres ni modifiques. (No se utilizó la subcarpeta `00_fuentes/`; las fuentes están en la raíz. Trátalas igual que si estuvieran ahí.)
- Los nombres tienen sufijos como "(1)" o "(2)": son las mismas versiones descritas en §5. Verifica por contenido y cifras.
- Los archivos marcados "verificar por contenido" ábrelos y confirma qué son; anótalo en `INVENTARIO.md`.
- La carpeta "Trabajo - Otro Compañero" tiene caracteres especiales (ñ, espacios): usa `pathlib` y comillas.

### 7.2 Lo que generas tú (en la raíz, junto a las fuentes)

```
D:.
├── 02_maestro/        (corpus_maestro.xlsx, checkpoints/)
├── 03_bloques/        (B01/, B02/, GUIA_GRABACION.docx)
├── 04_reportes/       (PROGRESO.md, INVENTARIO.md, EDA.md, DECISIONES_TOMADAS.md, ENTREGA.md, fig/)
├── 05_audio/          (más adelante)
├── 06_dataset/        (más adelante)
├── scripts/
├── config.yaml
├── requirements.txt
└── .venv/
```

- Si falta una fuente **esencial** (unificado o Corpus_Equipos), detente y avisa. Si falta una opcional, sigue y anota qué chequeo no se pudo hacer.

---

## 8. Diseño de los archivos de salida

**Principio:** cada archivo muestra **solo lo que su usuario necesita**. El origen y los detalles viven en otra pestaña, unidos por `ID`.

### 8.1 IDs

- **ID global y estable** por oración: `GEN-0001…` (general) y `CLI-0001…` (médico/clínico). **No uses el prefijo `MED-`**: ya lo usan los códigos originales de Kim 2 y se confundirían. Se asigna en el maestro después de la limpieza, en orden determinista (por fuente y luego por orden original).
- **Nunca se renumera** una fila que ya fue enviada al traductor. Las filas nuevas toman el siguiente número libre.
- Bloques: `B01`, `B02`… Sublotes: `B01-S1` … `B01-S4`.
- Audios: `{ID}_es.wav` y `{ID}_qu.wav`. Se nombran por ID y no por bloque, porque una fila puede moverse de bloque antes de grabarse.
- Los códigos originales (`QCH-xxxx`, `EL-xxxx`, `F-xxxx`, `CM-xxxx`, `MED-xxxx` de Kim 2…) se conservan en la pestaña `Origen`.

### 8.2 `02_maestro/corpus_maestro.xlsx` — la única fuente de verdad

La coordinación del proyecto designa una única persona responsable de este archivo. Nadie trabaja sobre copias propias.

| Pestaña | Contenido |
|---|---|
| `LEEME` | Qué es cada pestaña y columna, leyenda de estados y fecha de generación. |
| `Corpus` | **Vista limpia** (una fila por oración): `ID`, `Dominio` (General/Médico), `Escenario`, `Etapa_consulta`, `Rol` (Médico/Paciente/—), `Español`, `Quechua_borrador`, `Quechua_validado`, `Estado`, `Prioridad`, `Bloque`, `Sublote`, `Split`, `Test_sugerido`. |
| `Origen` | `ID`, `Fuente`, `Archivo`, `Hoja`, `Código_original`, `Fila_original`, `Tipo_borrador` (traductor automático Rosettia / normalizado de Lopera / SOCEMURP / MINEDU / ejercicio generado / redactado por Claude / ninguno), `Variedad_fuente`, `Origen_verificado`, `Estado_unificado` (el original), `Observaciones_heredadas`. |
| `Cambios` | Registro de **cada** modificación: `ID`, `Campo`, `Antes`, `Después`, `Regla`, `Fecha`. |
| `Descartes` | Todo lo que no entra: código original, texto, **motivo** e ID del que lo reemplaza (si es duplicado). **Nada se borra sin dejar rastro aquí.** |
| `Lexico` | Palabras sueltas (no se graban solas; ver §10.2). |
| `QA` | Avisos de la revisión automática (§12): `ID`, `Tipo`, `Severidad`, `Detalle`. |
| `Bloques` | Plan de **todos** los bloques posibles: conteos por dominio, rol, etapa y sublote; estado de cada bloque. |
| `Traductor_metricas` | Se llena tras cada devolución: % sin cambios, % editado, distancia de edición media y resultado de las oraciones de control. |

### 8.3 `03_bloques/BXX/BXX_trabajo.xlsx` — lo que el equipo mira día a día

- **Pestaña `Bloque` (vista limpia, lo único visible por defecto):**
  `N°`, `ID`, `Sublote`, `Dominio`, `Rol`, `Español`, `Quechua` (borrador mientras no vuelva el traductor; luego, el validado), `Estado`, `Grabado_ES` (☐), `Grabado_QU` (☐), `Notas`.
- **Pestaña `Detalle`:** solo las filas de este bloque con la información de `Origen` + `Quechua_borrador` + avisos de QA + % de edición del traductor.
- **Pestaña `Resumen`:** conteos (140/60, 70/30 por sublote, médico/paciente, etapas cubiertas, sufijos cubiertos) y si es control o no.
- **Formato:**
  - encabezado en negrita con color suave;
  - primera fila inmovilizada y autofiltro;
  - anchos razonables y ajuste de texto en Español y Quechua;
  - lista desplegable en `Estado`;
  - color suave por `Dominio`.
  - Sin fórmulas frágiles: valores, no fórmulas.

### 8.4 `03_bloques/BXX/BXX_traductor.docx` — para el traductor (solo Word)

- Página A4 **horizontal**, letra legible (11–12 pt).
- **Página 1: instrucciones breves en español:**
  - Qué hacer: revisar y corregir el quechua de cada fila, o escribirlo si la celda está vacía.
  - **Convención ortográfica** (tabla corta de §10.3).
  - Si una frase en español no se diría así, escribir cómo lo diría naturalmente un hablante y anotarlo en Observaciones.
  - **No borrar, mover ni editar la columna ID.** No cambiar la estructura de la tabla.
  - Devolver el mismo archivo.
- **Tablas:** una por sublote, con un título "Sublote 1 (filas 1–50)". La fila de encabezado se repite en cada página. Columnas:
  `N°` | `ID` | `Quién habla` (Médico / Paciente / —) | `Español` | `Quechua (corrija o escriba aquí)` | `Observaciones`
- **Celda Quechua:**
  - prellenada con el borrador (D6);
  - **vacía** en las ~15 oraciones de control de B01 (D7);
  - vacía en las filas sin borrador (solo español).
- **No pongas el origen del borrador** en el Word: no le dice al traductor si vino de una máquina o de un libro.
- **Observaciones:** solo avisos de severidad ALTA de §12, en una línea breve y en cursiva gris, con el prefijo `Aviso:` (p. ej. "Aviso: posible préstamo del español «entienden»"). El traductor escribe su comentario a continuación.
- No incluyas nada más: ni fuentes, ni estados, ni columnas técnicas.

### 8.5 Ida y vuelta Word ↔ Excel

- `scripts/06_importar_traductor.py BXX` lee el `.docx` devuelto y:
  1. Empareja **por ID** (no por posición). Reporta IDs faltantes, sobrantes o duplicados.
  2. Escribe el quechua final en `BXX_trabajo.xlsx` y en el maestro (`Quechua_validado`, `Estado = Validado`).
  3. Separa el comentario del traductor del `Aviso:` prellenado.
  4. Calcula métricas (sin cambios / editado / reescrito, distancia de edición) y el análisis de las oraciones de control. Las guarda en `Traductor_metricas`.
  5. Aplica las reglas ortográficas de §10.3 **solo para avisar**, nunca para corregir al traductor.
- **Pruébalo** con una copia del Word donde simules ediciones (cambios, celdas vacías, un comentario) antes de dar por terminado el script.

### 8.6 Grabación

- **Plantilla general (desde ya):** `03_bloques/GUIA_GRABACION.docx` con:
  - el protocolo: leer primero el español y luego el quechua, con buena pausa entre ambos;
  - un sublote por vez;
  - la regla de D8 (si se dice distinto, se anota);
  - el nombre de archivos `{ID}_es.wav` / `{ID}_qu.wav`;
  - el formato de P5;
  - una sala silenciosa.
- **Por bloque:** `BXX_grabacion.docx` se genera **cuando vuelve el traductor** (script `07_hoja_grabacion.py`). Contiene, por sublote: `ID` (grande), `Español`, `Quechua` validado, casillas ☐ ES ☐ QU y un espacio para notas.

### 8.7 Dataset para el modelo (cuando haya audios)

`scripts/08_manifest.py BXX` genera `06_dataset/manifest_BXX.csv` con: `id`, `bloque`, `sublote`, `split`, `dominio`, `rol`, `es`, `qu`, `audio_es`, `audio_qu`, `dur_es`, `dur_qu`, `qa_audio`. Además verifica que existan los audios, su formato y duraciones razonables.

---

## 9. Plan de trabajo por fases

**Modo de trabajo:**
- Trabaja **de corrido**.
- Usa una lista de tareas para mostrar el avance.
- **Solo detente a preguntar** si:
  - (a) falta una fuente esencial;
  - (b) las cifras de §5 difieren mucho, lo que indicaría otra versión;
  - (c) hay una contradicción que cambia la composición de los bloques.
- Todo lo demás: decide con el valor por defecto documentado y regístralo en `04_reportes/DECISIONES_TOMADAS.md`. La coordinación del proyecto revisa al final.

| Fase | Qué hacer | Salida |
|---|---|---|
| **F0 – Preparación** | Leer este archivo. Crear `04_reportes/PROGRESO.md` (§14.1). Crear entorno virtual propio en `.venv` (no tocar `inf659_env` ni `.venvs`). `requirements.txt`: pandas, openpyxl, python-docx, rapidfuzz, pypdfium2, pyyaml, matplotlib. Crear `config.yaml` con todos los parámetros (tamaño de bloque, 70/30, sublotes, cuotas, umbrales, semilla). | Entorno listo, `config.yaml` |
| **F1 – Inventario** | Localizar cada fuente, verificar cifras contra §5 y listar hojas, columnas y filas. No procesar audios de Allin Kawsay (P7). | `04_reportes/INVENTARIO.md` |
| **F2 – Ingesta al maestro** | Cargar todas las fuentes en un esquema único. Asignar `Tipo_borrador`, `Variedad_fuente`, `Rol` y `Etapa_consulta`. Clasificar el Grupo 2 (diccionario vs. ejercicio) y verificar contra el PDF si existe (P6). | Maestro preliminar |
| **F3 – EDA** | Describir el corpus con números **antes** de limpiar (lista en §9.1). | `04_reportes/EDA.md` + figuras en `04_reportes/fig/` |
| **F4 – Limpieza** | Aplicar §10. Todo cambio va a `Cambios` y todo descarte a `Descartes`. Revisión automática §12 → pestaña `QA`. | Maestro limpio |
| **F5 – Llenar huecos** | (a) Para cada pregunta del médico de los bloques planificados sin respuesta, **redactar en español** 1–3 respuestas típicas del paciente. (b) Convertir palabras sueltas prioritarias en frases portadoras (§10.2). Todo lo redactado por ti va con `Tipo_borrador = redactado por Claude (solo español)` y queda marcado para revisión de la coordinación del proyecto. **Nunca redactes quechua como si fuera válido.** | Filas nuevas marcadas |
| **F6 – Priorización y bloques** | Aplicar §11. Planificar todos los bloques que permita el material (pestaña `Bloques`). **Generar archivos completos solo para B01 y B02** (D5): Word del traductor, Excel de trabajo y control en B01. Además: `GUIA_GRABACION.docx` y los scripts 06, 07 y 08 **probados con datos simulados**. | `03_bloques/B01/`, `03_bloques/B02/` |
| **F7 – Verificación final** | Ejecutar el checklist de §13. Abrir cada `.docx` y `.xlsx` generado y comprobar que se ven bien. Escribir el reporte de entrega. | `04_reportes/ENTREGA.md` |

### 9.1 Contenido mínimo del EDA

- Conteo por fuente, variedad, tipo de borrador, sección, etapa de consulta, rol, dominio y estado del unificado.
- Longitudes (palabras y caracteres) en español y quechua: distribución y extremos.
- Palabras sueltas vs. frases; preguntas vs. afirmaciones vs. órdenes.
- Duplicados exactos y casi duplicados (en español y en quechua).
- Rasgos no chanka (§6) y letras fuera de la convención, por fuente.
- Relación de longitud quechua/español (alineación) y valores atípicos.
- Vocabulario: tamaño, palabras más frecuentes, y palabras del quechua no encontradas en AmericasNLP/diccionario (si están).
- **Cobertura de sufijos** (§11.1) por fuente: qué enseña cada pool.
- **Cobertura clínica:** qué etapas y escenarios faltan; cuántas frases del paciente hay por escenario.
- **Conclusiones en lenguaje simple:** qué se descarta, qué falta y cuántos bloques caben.

---

## 10. Reglas de limpieza (preprocesamiento)

**Nunca se borra nada sin rastro.** Cambios → `Cambios`. Descartes → `Descartes` con motivo.

### 10.1 Español

- Normalizar espacios y signos (¿? ¡!), mayúscula inicial y punto final cuando corresponda.
- Corregir erratas evidentes:
  - «¿Dé dónde eres?» → «¿De dónde eres?»
  - «sliba» → «silba»
  - «Entreñimiento» → «Estreñimiento»
  - «Vómitar» → «Vomitar»
  - «¿Estas estreñido?» → «¿Estás estreñido?»
  - …
- **Giros bolivianos o poco naturales** (OPS/OMS Bolivia y otros): proponer una versión en español peruano neutro. Ejemplos: «¿Te ha bajado como mucha agua?», «¿Cómo punzado te está doliendo?», «¿Siente que le ronda o le silba el pecho?». Guardar el original en `Cambios` y marcar `Por_revisar`.
- **Oraciones largas** (más de 20 palabras): partir en unidades de 15 palabras o menos si son listas de instrucciones. Si no se pueden partir limpiamente → `Descartes` (motivo: larga).
- Mantener la variación natural (tú/usted, paráfrasis). No uniformizar de más.

### 10.2 Palabras sueltas

- **No se graban solas.** Van a la pestaña `Lexico`.
- Las prioritarias (síntomas, partes del cuerpo, enfermedades frecuentes) entran a los bloques mediante **frases portadoras en español** redactadas por ti: "Me duele ___", "¿Tienes ___?", "Tengo ___". Marcadas como redactadas por Claude. El quechua lo pone el traductor.

### 10.3 Quechua (borradores): convención ortográfica

**Únicos cambios automáticos permitidos:** los ortográficos mecánicos de esta tabla, registrados en `Cambios`. **Prohibido** cambiar léxico, gramática o sentido: eso se marca en QA para el traductor.

| Regla | Ejemplo |
|---|---|
| Sin glotalizadas ni aspiradas (k', q', p', t', ch', kh, ph, qh, th) | «p'acha» → «pacha», «qhaway» → «qaway», «achkha» → «achka» |
| 3 vocales en palabras quechuas (a, i, u) | «onqoy» → «unquy», «-yoq» → «-yuq», «qolqe» → «qullqi» |
| Sin c/qu/j/hu castellanas en palabras quechuas | «wicsa» → «wiksa», «jamuy» → «hamuy», «huasi» → «wasi» |

**Solo marcar en QA, sin cambiar** (no es mecánico):

| Rasgo | Ejemplo |
|---|---|
| Progresivo -sha- → -chka- | «kashanki» → «kachkanki» |
| Validador -n tras vocal → -m | «manan» → «manam» |
| Inclusivo -nchis → -nchik | |
| Subordinador -qti- / -jti- → -pti- | |
| Léxico chanka | yaku (no unu), upyay (no uhyay), llamkay, punchaw, haykap, hurquy, wichqay, mayllay, kiri |

- Los **préstamos y nombres propios conservan su escritura** («hospital», «Lince», «Ayacucho»).
- Las fuentes oficiales chanka (afiches MINSA/MinCul, manual MinCul) **se respetan tal cual**.

### 10.4 Descartar (siempre con motivo)

- Filas "Pendiente – no usar" (títulos).
- Prosa bíblica o religiosa.
- Filas sin español.
- Filas de plantilla.
- Filas vacías.
- Párrafos de instrucciones imposibles de partir.
- **Duplicados exactos** (tras normalizar): queda uno y los códigos de los demás se guardan en `Origen`.
- **Casi duplicados** (similitud en español ≥ 90 con rapidfuzz): máximo **2 paráfrasis** por significado en todo el plan; el resto va a `Descartes` con el ID que lo reemplaza. Las paráfrasis son útiles para la voz, así que no se eliminan todas.

---

## 11. Priorización y armado de bloques

**Objetivo:** que **B01 sea un mínimo viable** con el que se pueda entrenar, evaluar y hacer una demo. Cada bloque siguiente agrega lo que más falta.

### 11.1 Parte general (140 por bloque): selección voraz por cobertura

- **Base metodológica:** al diseñar corpus de voz se trata la selección de oraciones como un problema de cobertura. Un algoritmo voraz elige en cada paso la oración que aporta más unidades aún no cubiertas (François y Boëffard 2001; *Comparing Set-Covering Strategies for Optimal Corpus Design*, LREC 2008).
- El quechua es aglutinante, así que la unidad principal son los **sufijos**:
  - **Nominales:** -kuna; posesivos -y, -yki, -n, -nchik, -yku, -ykichik, -nku; casos -ta, -man, -pi, -manta, -wan, -paq, -pa/-p, -kama, -rayku, -hina, -nta, -yuq, -ntin.
  - **Verbales de persona:** -ni, -nki, -n, -nchik, -yku, -nkichik, -nku; objeto -wa-, -su-, -yki.
  - **Tiempo, aspecto y modo:** -chka-, -rqa-, -sqa-; futuro -saq, -nqa, -sun; condicional -man, -waq; imperativo -y, -ychik, -chun.
  - **Derivativos:** -chi-, -ku-, -mu-, -pu-, -ri-, -yku-, -naku-, -ysi-, -pa-.
  - **Nominalizadores:** -q, -sqa, -na, -y.
  - **Subordinadores:** -spa, -pti-, -stin.
  - **Enclíticos:** -mi/-m, -si/-s, -chá, -chu, -taq, -qa, -pas/-pis, -lla, -ña, -raq, -yá, -puni.
- Segmentación **heurística** (sufijos desde el final de la palabra, priorizando el más largo) sobre los borradores. Documenta que es aproximada. Unidades secundarias: bigramas de letras (fonotaxis) y palabras nuevas.
- **Puntaje** = unidades nuevas cubiertas (con pesos; sufijos > bigramas > palabras) ÷ penalización por longitud. Empates: prioridad de pool, luego la más corta. Semilla fija.
- **Cuotas por bloque** (configurables; ajústalas y justifica si el material no da):
  - ~35 del **Principito** (prioridad del profesor; se agota en ~3 bloques);
  - ~70 del **Grupo 2 tipo diccionario**;
  - **35 como máximo** de **ejercicios del Grupo 2** (son repetitivos).
- **B01:** preferir oraciones cortas (12 palabras o menos en español).
- Material general disponible: ~113 + ~170 + ~500 ≈ 780 oraciones → **~5 bloques**. Si se necesitan más, ver P4.

### 11.2 Parte médica (60 por bloque): flujo de consulta + frecuencia + alarma

**Base metodológica:** el modelo **Calgary-Cambridge** divide la consulta en: inicio, recolección de información, examen físico, explicación y plan, y cierre. La relación con el paciente es transversal.

**B01 = una consulta completa de punta a punta** (~30 médico / ~30 paciente). Distribución orientativa:

| Etapa | Frases aprox. | Contenido |
|---|---|---|
| Inicio | 8 | Saludo, nombre, edad, de dónde viene, quién lo trajo, con respuestas. |
| Motivo de consulta | 8 | "¿Por qué viniste?", "Me duele…", "¿Desde cuándo?", con respuestas. |
| Caracterizar el dolor o síntoma | 16 | Dónde, desde cuándo, cómo, intensidad, qué lo empeora o alivia, con respuestas. |
| Síntomas asociados frecuentes | 10 | Fiebre, tos, vómito, diarrea, con sí/no y detalle. |
| Examen físico | 8 | Órdenes básicas: abra la boca, respire hondo, recuéstese… |
| Explicación, plan y cierre | 10 | Indicaciones simples, cuándo volver, "¿Entendiste?", "Sí, entendí". |

- **Esqueleto:** las frases del manual SOCEMURP (las más cercanas al chanka), más las respuestas que redactes en F5.

**Bloques siguientes (orden por defecto):**
- **B02:** síntomas y sistemas más frecuentes (respiratorio, digestivo, urinario, fiebre en niños) + antecedentes básicos (alergias, medicamentos, embarazo).
- **B03:** señales de alarma y emergencias (sangrado, desmayo, falta de aire, embarazo con sangrado, niño deshidratado) + tratamiento (dosis, horarios) + tranquilizar al paciente.
- **B04 en adelante:** el resto, por frecuencia. Si tienes acceso web, consulta datos del MINSA o del CDC-MINSA sobre las principales causas de consulta en Ayacucho, Apurímac y Huancavelica y **cita la fuente**; si no, usa este orden y anótalo. Después: salud sexual y reproductiva, anticoncepción, salud mental, ojos, oídos y nariz, exámenes auxiliares. Violencia: frases neutras, sin detalles explícitos.

**Calidad del borrador** para elegir entre frases equivalentes, de mejor a peor:
1. Fuente chanka oficial.
2. "Final – coincide" (incluye SOCEMURP).
3. "Final – única fuente".
4. "Final – corregido/normalizado".
5. "Final – forma del libro compatible" (Lopera).
6. "Revisar".
7. Solo español: válido; el traductor traduce desde cero.

**Integridad de pares:** pregunta y respuestas en el mismo sublote.

### 11.3 Mapeo de secciones del unificado a etapas

| Etapa | Secciones |
|---|---|
| Inicio | 01 Presentación y saludo; 02 Filiación; 01. Presentación y acceso lingüístico; 02. Filiación |
| Recolección de información | 03 Motivo de consulta; 04 Antecedentes; 06 Indagar el síntoma; 07 Síntomas generales; 08–16 sistemas (cardiorrespiratorio, digestivo, urinario, ojos, nariz, oídos, nervioso, salud mental); 03./04./05.–12. de la otra numeración |
| Examen físico | 05 Examen físico: indicaciones; 18 Exámenes auxiliares; 13. Examen clínico; 15. Laboratorio y pruebas |
| Explicación y plan | 17 Diagnóstico; 19 Tratamiento e indicaciones; 20 Promoción y prevención; 23 Métodos anticonceptivos; 18. Tratamiento y prevención; 19. Referencia y seguimiento |
| Relación (transversal) | 21 Tranquilizar al paciente |
| Sensible | 22 Violencia; 11 Salud sexual y reproductiva |
| Léxico | 24 Vocabulario médico (palabras sueltas); anexos de Lopera; Vocabulario (Allin Kawsay); 20. Léxico clínico de apoyo |

Si una sección no encaja, decide y anótalo.

### 11.4 Sublotes y orden

- Cada sublote ≈ 35 generales + 15 médicas.
- Las médicas siguen el orden de la consulta a lo largo de los sublotes, y las generales se reparten intercaladas.
- **Control (D7):** en B01, elegir ~15 filas con borrador (unas 10 generales y 5 médicas) repartidas entre sublotes. Esas filas van con la celda Quechua vacía en el Word. Se registran en `Detalle` y en el maestro.

---

## 12. Revisión automática de calidad ("evaluación como LLM")

Tú no eres hablante de quechua chanka. **Tus avisos son sospechas para que el traductor sepa dónde mirar primero, nunca correcciones que cuenten como válidas.**

Tipos de aviso (pestaña `QA`, severidad ALTA / MEDIA / BAJA):

| Tipo | Qué detecta |
|---|---|
| `ORTO` | Letras fuera de la convención (§10.3). |
| `VARIEDAD` | Rasgos cusqueños, collao o bolivianos (§6). |
| `PRESTAMO` | Palabra española sin adaptar dentro del quechua («entienden», «piensani»). Severidad baja si es un préstamo común y natural («hospital», «pastilla»). |
| `ALINEACION` | Relación de longitud quechua/español fuera de [0.5, 2.0]; números que no coinciden; pregunta en español sin marca interrogativa en quechua (-chu, -taq, ima-, pi-, may-, hayka-…). |
| `SENTIDO` | Sospecha semántica (tipo *pisi*/*achka*, *wata*/*killa*). Explica el porqué en una línea. |
| `OOV` | Palabra no encontrada en AmericasNLP ni en el diccionario tras quitar sufijos. **Severidad baja** en léxico médico, que es esperable que no esté. |
| `DUP` | Mismo quechua para dos españoles distintos (o viceversa). |
| `TRANSCRIPCION` | Patrones de transcripción de oído (y por ll, o/e, letras pegadas). |

Valida tus reglas con los casos de §6: deben salir marcados.

---

## 13. Definición de terminado (checklist final)

- [ ] `PROGRESO.md` al día, todas las fases en `hecha`.
- [ ] Fuentes de §7.1 intactas (compara fechas y tamaños del antes y el después).
- [ ] Cifras de §5 verificadas, con las diferencias explicadas en `INVENTARIO.md`.
- [ ] `corpus_maestro.xlsx` con todas sus pestañas.
  - [ ] IDs únicos.
  - [ ] Toda fila de `Corpus` tiene su fila en `Origen`.
  - [ ] Todo cambio está en `Cambios` y todo descarte en `Descartes`.
- [ ] `EDA.md` con conclusiones en lenguaje simple.
- [ ] B01 y B02:
  - [ ] exactamente **200 filas** cada uno = 140 generales + 60 médicas;
  - [ ] cada sublote con ~35 + ~15;
  - [ ] médico/paciente ≈ 50/50;
  - [ ] pares pregunta–respuesta juntos;
  - [ ] sin filas repetidas entre bloques.
- [ ] B01 contiene una **consulta completa** (las 6 etapas de §11.2) y ~15 oraciones de control.
- [ ] Los Word del traductor se abren bien.
  - [ ] Página horizontal, instrucciones, tablas por sublote, encabezado repetido.
  - [ ] Sin información de origen.
  - [ ] Celdas de control vacías.
- [ ] Los Excel de trabajo se ven limpios (`Bloque` / `Detalle` / `Resumen`).
- [ ] Scripts 06, 07 y 08 **probados con datos simulados** (ida y vuelta Word → Excel funciona por ID).
- [ ] `GUIA_GRABACION.docx` creada.
- [ ] `DECISIONES_TOMADAS.md`: cada valor por defecto usado y cada decisión propia, con su porqué.
- [ ] `ENTREGA.md` para la coordinación del proyecto, en lenguaje simple:
  - qué está listo;
  - **qué enviar a quién** (el Word de B01 y B02 al traductor);
  - qué debe revisar el equipo (frases redactadas por Claude, adaptaciones del español marcadas `Por_revisar`);
  - pendientes P1–P7;
  - cuántos bloques caben con el material actual.

---

## 14. Reglas de trabajo y qué NO hacer

- **No modifiques ninguna fuente (§7.1).** Trabaja sobre copias en memoria y escribe solo en `02_`–`06_`, `scripts/` y la raíz para config.
- **No inventes quechua válido.** Puedes redactar español; el quechua lo pone el traductor.
- **No borres sin rastro.**
- **No envíes nada a nadie.** La coordinación del proyecto entrega el Word al traductor.
- No uses ni modifiques `inf659_env`, `.venvs` u otros entornos ajenos al proyecto.
- Scripts **deterministas e idempotentes**: volver a correrlos desde las fuentes (§7.1) produce lo mismo. Toda la configuración en `config.yaml`.
- Windows:
  - usa `pathlib` y UTF-8;
  - si un `.xlsx` está abierto en Excel, la escritura falla: pide a la coordinación del proyecto que lo cierre;
  - lee con `openpyxl` (`data_only=True` cuando haya fórmulas).
- Explica a la coordinación del proyecto en español simple. Muestra el avance con la lista de tareas. Al terminar, un resumen breve y la ruta de `ENTREGA.md`.
- Si la coordinación del proyecto pide cambiar un parámetro (tamaño de bloque, cuotas, 70/30), cámbialo en `config.yaml`, regenera y registra el cambio.

### 14.1 Puntos de retorno (si la sesión se corta por límites)

El trabajo es largo y la sesión puede terminar a la mitad. **Siempre debe poder retomarse sin rehacer ni perder nada.**

**Archivo de estado: `04_reportes/PROGRESO.md`** (créalo en F0, antes de cualquier otra cosa). Contiene:
- Tabla de fases F0–F7 con estado: `pendiente` / `en curso` / `hecha`, fecha y hora.
- Dentro de la fase en curso: subpasos hechos y el **siguiente paso exacto** ("siguiente: generar B02_traductor.docx").
- Archivos generados en cada fase (ruta) y el script que los produce.
- Decisiones tomadas en esta sesión que aún no estén en `DECISIONES_TOMADAS.md`.
- Problemas abiertos o dudas para la coordinación del proyecto.

**Reglas:**
1. **Actualiza `PROGRESO.md` al terminar cada subpaso**, no solo al final de la fase. Es lo primero que se escribe después de producir algo.
2. **Trabajo en scripts, no en memoria:** todo cálculo vive en `scripts/` y su salida en disco. Nada importante debe existir solo en la conversación.
3. **Checkpoints intermedios en `02_maestro/checkpoints/`:** al cerrar F2, F3, F4, F5 y F6 guarda el estado en un archivo con fase y fecha (p. ej. `F4_limpio_20261014.xlsx` o `.parquet`). La fase siguiente lee desde el último checkpoint.
4. **Escritura segura:** escribe primero a un archivo temporal y renómbralo al final, para no dejar archivos a medias si se corta.
5. **Scripts reanudables:** cada script detecta si su salida ya existe y es válida; si es así, la salta (salvo que se pida `--forzar`). Nunca renumeres IDs al reanudar.
6. **Al retomar (en el mismo chat tras un límite, o si la conversación se compactó y perdiste detalle):** relee `PROGRESO.md` antes de seguir; no confíes solo en lo que recuerdas de la conversación. Continúa desde el siguiente paso indicado.
7. **Al iniciar cualquier sesión nueva:** lee este CLAUDE.md, luego `PROGRESO.md`, verifica que los archivos listados existan y **continúa desde el siguiente paso indicado**. No empieces de cero. Dile a la coordinación del proyecto en una línea desde dónde retomas.
8. Si un paso quedó a medias (archivo incompleto o temporal), rehaz **solo ese paso**.

**Para la coordinación del proyecto:** lo normal es seguir **en el mismo chat**: cuando se libere el límite, escribe *"Continúa desde PROGRESO.md"*. Solo si el chat ya no sirve, abre uno nuevo en la misma carpeta con el mismo mensaje.

### 14.2 Nivel de esfuerzo y ultracode (decisión del proyecto)

- **Trabajo principal (F0–F7): esfuerzo `xhigh`, sin ultracode.** Es una cadena de fases dependientes; los workflows multiagente no aportan aquí y gastan los límites más rápido. `max` no se usa (rendimientos decrecientes, tiende a sobrepensar).
- **No lances workflows por tu cuenta** durante F0–F7. Trabaja turno a turno con la lista de tareas y `PROGRESO.md`.
- **Revisión final (después de F7):** La coordinación del proyecto la pedirá con la palabra `ultracode` para ese único pedido. En ese caso sí: verificación independiente de todo lo generado contra el checklist de §13, con agentes que se revisan entre sí, y una lista de problemas ordenada por gravedad. Corrige solo lo que la coordinación del proyecto apruebe y actualiza `PROGRESO.md` y `ENTREGA.md`.
- Si un workflow llega al límite de uso, se pausa y continúa solo al liberarse; el resto del trabajo se retoma con §14.1.

**Para la coordinación del proyecto:**
1. Al abrir la sesión: `/effort xhigh` y luego el prompt de arranque.
2. Al terminar F7: *"ultracode: revisa de forma independiente todo lo generado contra CLAUDE.md (checklist de la sección 13), verifica cada hallazgo antes de reportarlo y dame una lista de problemas ordenada por gravedad."*

---

## 15. Referencias (para justificar decisiones en los reportes)

- Chu, Dabre y Kurohashi (2017). *An Empirical Comparison of Domain Adaptation Methods for Neural Machine Translation*. ACL. https://aclanthology.org/P17-2061/ — Mezclar datos del dominio con datos generales ("mixed fine-tuning") funciona mejor que entrenar solo con los del dominio, porque con poco dato el modelo se sobreajusta. Respalda el 70/30 del profesor.
- François y Boëffard (2001). Diseño de corpus de voz como problema de cobertura (Eurospeech). https://www.isca-archive.org/eurospeech_2001/francois01_eurospeech.html
- *Comparing Set-Covering Strategies for Optimal Corpus Design* (LREC 2008). https://aclanthology.org/L08-1527/
- Claude Code: niveles de esfuerzo y ultracode: https://code.claude.com/docs/en/model-config.md · workflows: https://code.claude.com/docs/en/workflows.md
- Kurtz y Silverman (1996), modelo Calgary-Cambridge de la entrevista médica. Resumen: https://en.wikipedia.org/wiki/Calgary%E2%80%93Cambridge_model
- MINEDU. *Yachakuqkunapa Simi Qullqa – Ayakuchu Chanka Qichwa simipi*. https://repositorio.minedu.gob.pe/handle/20.500.12799/10380

---

## 16. Glosario (términos del proyecto)

| Término | Significado |
|---|---|
| **Gold** | Dato confiable: validado por el traductor y grabado. |
| **Borrador** | Quechua no validado: de traductor automático, de normalizar otra variedad, de un libro o generado. |
| **EDA** | Describir el corpus con números antes de limpiarlo, para decidir qué cortar y cómo armar los bloques. |
| **Preprocesamiento** | Aplicar las decisiones del EDA: limpiar, deduplicar, partir, normalizar y registrar. |
| **Bloque** | 200 oraciones (140 + 60) que se traducen y graban juntas. |
| **Sublote** | 50 oraciones, ~1 hora de grabación. |
| **Control** | Oraciones con borrador que se entregan sin él para medir el sesgo del traductor. |
| **Unificado** | `Vocabulario_Quechua_Chanka_unificado_2.xlsx`, la versión vigente de la parte médica. |
| **Corpus equipos** | `Corpus_Equipos_1.xlsx`, el corpus original de los 3 grupos. |
