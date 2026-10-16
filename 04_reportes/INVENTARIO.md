# Inventario de fuentes (F1)

Generado por `scripts/01_inventario.py` el 2026-10-15. Fuentes en `Fuentes/` (solo lectura).

## 1. Archivos encontrados

| Clave | Archivo | Existe | Tamaño | Tipo |
|---|---|---|---|---|
| unificado | `Vocabulario_Quechua_Chanka_unificado (2).xlsx` | sí | 392 KB | esencial |
| corpus_equipos | `Corpus_Equipos (1).xlsx` | sí | 96 KB | esencial |
| corpus_construido | `Corpus_Construido (1).xlsx` | sí | 11 KB | opcional |
| socemurp_pdf | `PDF Manual de Quechua Socemurp Compress _ ILIDE.INFO Platform PDF Viewer (1).pdf` | sí | 37,676 KB | opcional |
| minedu_pdf | `Yachakuqkunapa simi qullqa. Ayakuchu Chanka Qichwa simipi (1).pdf` | sí | 47,806 KB | opcional |
| lopera_pdf | `ManualSemiologiaQuechua-2020.pdf` | sí | 900 KB | opcional |
| ops_bolivia_pdf | `entrevistaquechua_spa.pdf` | sí | 18,150 KB | opcional |
| web_html | `Quechua médico.html` | sí | 11 KB | opcional |
| mincul_pdf | `manualparaelempleodelquechuachankaenlaadministraciondejusticia.pdf` | sí | 1,874 KB | opcional |
| afiche_pdf | `AFICHE_COVID 19 LAVADO DE MANOS MINSA quechua chanka.pdf` | sí | 398 KB | opcional |
| diabetes_qu_pdf | `8361447-diabetes_mellitus_quechua.pdf` | sí | 642 KB | opcional |
| diabetes_es_pdf | `5660130-manejo-de-paciente-con-diabetes-mellitus-2.pdf` | sí | 2,319 KB | opcional |
| arbol | `arbol.txt` | sí | 1 KB | opcional |
| americasnlp_dir | `AmericasNLP` | sí | 44,671 KB | opcional |
| otro_companero_dir | `Trabajo - Otro Compañero` | sí | 2,230 KB | opcional |

- Audios `.mp3` (Allin Kawsay) en la carpeta: **0**. No se inventarían ni procesan (P7).
- `arbol.txt` se ignora (es un listado de la carpeta).

## 2. Hojas, columnas y filas de los Excel

### `Vocabulario_Quechua_Chanka_unificado (2).xlsx`

| Hoja | Filas totales (rango usado) | Filas no vacías (incl. encabezado) | Columnas | Encabezado |
|---|---|---|---|---|
| Resumen | 52 | 46 | 3 | `Vocabulario médico español – quechua chanka (unificado)` |
| Vocabulario_unificado | 1529 | 1529 | 11 | `Id_unificado`, `Español (palabra o frase)`, `Quechua_final (chanka)`, `quechua_marshall`, `quechua_kim1`, `quechua_kim2`, `Observaciones_finales`, `Estado`, `Sección`, `Fuente_original`, `Códigos_origen` |
| Trazabilidad | 1543 | 1543 | 30 | `Id_unificado`, `Código Marshall`, `Código Kim 1`, `Código Kim 2`, `Español (Marshall)`, `Español (Kim 1)`, `Español (Kim 2)`, `Amarillo en origen`, `M · Quechua corpus`, `M · Traducción del libro`, `M · Corrección propuesta`, `M · Revisión preliminar`, `M · Justificación`, `M · Observaciones`, `K1 · Quechua corpus anterior`, `K1 · Quechua de la fuente (libro)`, `K1 · Propuesta documental (DM)`, `K1 · Evidencia léxica`, `K1 · Corrección anterior archivada`, `K1 · Prioridad`, `K1 · Contexto`, `K1 · Justificación`, `K1 · Origen del registro`, `K2 · Quechua chanka (corpus)`, `K2 · Traducción del libro`, `K2 · Comentario de celda (libro)`, `K2 · Corrección propuesta`, `K2 · Justificación`, `K2 · Estado para el modelo`, `K2 · Observaciones` |

### `Corpus_Equipos (1).xlsx`

| Hoja | Filas totales (rango usado) | Filas no vacías (incl. encabezado) | Columnas | Encabezado |
|---|---|---|---|---|
| Equipos | 10 | 6 | 4 |  |
| Grupo 1 - Principito | 1000 | 114 | 7 | `N°`, `Español`, `Quechua Chanka`, `Observaciones` |
| Grupo 2 - Corpus Chanka | 1000 | 674 | 4 | `N°`, `Español`, `Quechua Chanka`, `Observaciones` |
| Grupo 3 - Corpus Medico | 1006 | 686 | 6 | `N°`, `Español`, `Quechua Chanka`, `Observaciones` |
| Grupo 3 - Términos médicos | 898 | 59 | 7 | `N°`, `Tipo`, `Español`, `Quechua Chanka`, `Observaciones` |

### `Corpus_Construido (1).xlsx`

| Hoja | Filas totales (rango usado) | Filas no vacías (incl. encabezado) | Columnas | Encabezado |
|---|---|---|---|---|
| Hoja 1 | 112 | 112 | 5 | `N°`, `Español`, `Quechua Chanka`, `Grabación` |

> Las filas totales incluyen el rango vacío que Excel guarda (p. ej. 1000 filas en Corpus_Equipos). Lo que cuenta son las filas no vacías.

## 3. `Vocabulario_unificado` (§5.1) — parte médica vigente

| Cifra | Obtenido | Esperado (§5) | Resultado |
|---|---|---|---|
| Filas `Vocabulario_unificado` | 1528 | 1528 | ✔ igual |
| Filas `Trazabilidad` | 1542 | 1542 | ✔ igual |
| Filas con quechua final | 1156 | 1156 | ✔ igual |
| IDs únicos `QCH-` | 1528 | 1528 | ✔ igual |

### Estados

| Estado | Obtenido | Esperado | Resultado |
|---|---|---|---|
| Final – corregido/normalizado a chanka | 522 | 522 | ✔ igual |
| Pendiente – sin traducción chanka | 361 | 361 | ✔ igual |
| Final – coincide en los Excel | 281 | 281 | ✔ igual |
| Final – forma del libro compatible con chanka | 122 | 122 | ✔ igual |
| Revisar – duda de traducción | 89 | 89 | ✔ igual |
| Revisar – adaptación propuesta | 72 | 72 | ✔ igual |
| Final – única fuente | 58 | 58 | ✔ igual |
| Final – fuente chanka oficial | 12 | 12 | ✔ igual |
| Pendiente – no usar (ver observación) | 11 | 11 | ✔ igual |

### Fuentes (`Fuente_original` agrupada)

| Fuente | Filas | Con quechua | Esperado (§5.1) | Resultado |
|---|---|---|---|---|
| Lopera Quiroga (2020) | 566 | 510 | 566 | ✔ igual |
| Allin Kawsay (INS/MINSA) | 510 | 472 | 510 | ✔ igual |
| OPS/OMS Bolivia (2013) | 234 | 0 | 234 | ✔ igual |
| SOCEMURP (corpus original del equipo) | 118 | 118 | 118 | ✔ igual |
| Kim 1 (pregunta añadida) | 43 | 0 | 43 | ✔ igual |
| Farfán Cantero (2001), SITUA | 24 | 24 | 24 | ✔ igual |
| MinCul – manual de justicia (chanka) | 13 | 13 | 13 | ✔ igual |
| YouTube | 9 | 9 | 9 | ✔ igual |
| Afiche MINSA/MinCul lavado de manos (chanka) | 6 | 6 | 6 | ✔ igual |
| MINSA – diabetes (quechua) | 4 | 4 | 4 | ✔ igual |
| OMS (2009) – lista de verificación | 1 | 0 | 1 | ✔ igual |

> §5.1 cuenta 117 filas «Corpus original del equipo» + 1 «Manual SOCEMURP-FAMURP» por separado; aquí se agrupan (118). Las 510 filas de Allin Kawsay traen el nombre del audio en `Fuente_original` (p. ej. «audio 222. Zancudo.mp3, transcripción automática»); se agrupan por prefijo.

- Lopera con quechua: **510** filas (corregidas a chanka: 287; «compatible»: 122; otros estados: 101). §5.1 esperaba 409 (287 + 122) → ✔ igual.
- OPS/OMS Bolivia: 234 filas, con quechua: 0 (esperado: solo español).

### Composición

| Cifra | Obtenido | Esperado (§5.1) | Resultado |
|---|---|---|---|
| Palabras sueltas (1 palabra) | 515 | 515 | ✔ igual |
| 2–3 palabras | 324 | 323 | ≈ dentro de tolerancia |
| 4 o más palabras | 689 | 690 | ≈ dentro de tolerancia |
| Máximo de palabras | 45 | 44 | ≈ dentro de tolerancia |
| Preguntas | 615 | 615 | ✔ igual |
| Frases del paciente en 1.ª persona (heurística) | 46 | 47 | heurística distinta; ver nota |

> La cifra de frases del paciente depende de la heurística; la mía (`heuristicas.es_primera_persona`) es más amplia que la usada en la revisión anterior. No indica otra versión del archivo.

### Casos conocidos de §6 (comprobación de versión)

| ID | Español | Quechua final | Estado |
|---|---|---|---|
| QCH-0010 | ¿Estás bien? | ¿Allinllachu kachkanki? | Final – corregido/normalizado a chanka |
| QCH-0013 | ¿Quién eres? | ¿Pitaq kanki? | Final – corregido/normalizado a chanka |
| QCH-0037 | Desde un mes me duele mucho mi estómago. | Huk killañam wiksay anchata nanawachkan. | Revisar – duda de traducción |
| QCH-0050 | ¿Es la primera vez que te duele? | ¿Punta kutitachu nanasunki? | Revisar – duda de traducción |
| QCH-0063 | ¿Cómo era tu dolor? | ¿Imaynataq nanayniyki karqa? | Final – corregido/normalizado a chanka |
| QCH-0086 | ¿Era mucho? | ¿Achkachu karqa? | Final – corregido/normalizado a chanka |
| QCH-0110 | En cada comida tienes que lavarte las manos. | Makiykita sapa mikunapi mayllikunayki. | Final – corregido/normalizado a chanka |
| QCH-0111 | No debes comer comida con mucha sal. | Amam achka kachiyuq mikunata mikunkichu. | Final – corregido/normalizado a chanka |

## 4. `Corpus_Equipos` (§5.2)

### Grupo 1 – Principito

- Filas con datos: **113** (esperado 113) → ✔ igual. IDs `EL-0001`…`EL-0113`, únicos: 113.
- Con quechua: 113. Columna G (sin encabezado) dice «Modelo utilizado: Rosettia GSPO-NLLB (Thermostatic/rosettia-quy-gspo-nllb13b-merged), basado en NLLB-200 1.3B, para traducción de español a quechua Chanka (Ayacucho)».
- EL-0001 trae la nota de plantilla «opcional: fuente / fila de ejemplo, borrar al usar» → se ignora (no es una observación real).

### Grupo 2 – Corpus Chanka

| Cifra | Obtenido | Esperado (§5.2) | Resultado |
|---|---|---|---|
| Filas con ID `F-` | 670 | 676 | ≈ dentro de tolerancia |
| … con español | 669 | — |  |
| … con quechua | 669 | 672 | ≈ dentro de tolerancia |
| Empiezan en minúscula | 507 | 507 | ✔ igual |
| Empiezan con pronombre personal | 396 | 396 | ✔ igual |

- ID duplicado: F-0013. Filas con ID pero vacías: F-0517.
- Filas sin ID al final: 3 → son la bibliografía de la hoja («Referencias», MINEDU 2014, MINEDU 2021), no oraciones.
- **Explicación de la diferencia con §5.2:** §5.2 contó 676 filas y 672 con quechua incluyendo la fila vacía F-0517 y las 3 filas de referencias (que tienen texto en la columna Quechua). Contando solo oraciones reales: 669 con español y quechua. Es la misma versión del archivo.
- Pronombres contados: yo, tú/tu, él, ella, nosotros/as, ustedes, ellos/as, usted (no el artículo «el»).

### Grupo 3 – Corpus Médico (solo referencia, D10)

- Filas con español: **685** (esperado 685) → ✔ igual. «Validar escritura»: **521** (esperado 521) → ✔ igual.
- La columna N° es fórmula (`=A2+1`); se reconstruyó como `G3-0001…` solo para cruzar.

- Cobertura en el unificado (mismo español normalizado): **672 de 685**. Las que no coinciden exactamente suelen haber cambiado de redacción en la revisión (el unificado corrigió erratas).

### Grupo 3 – Términos médicos (solo referencia)

- Filas: **58** (esperado 58) → ✔ igual.
- Hallazgos: la última fila tiene las columnas invertidas («Aycha» en Español y «Músculo» en Quechua) y «Hueso → Tullu nanay» (= dolor de hueso) está desalineada. Como la hoja es solo referencia, no se corrige; se deja anotado.

## 5. `Corpus_Construido` (§5.3, solo referencia)

- Filas: **111** (esperado 111) → ✔ igual. N° es fórmula (`=CONCATENATE("S1-",B2)`): se reconstruyó `S1-1…`.
- Presentes en el unificado (mismo español o mismo quechua normalizado): **111 de 111** (esperado 109) → ≈ dentro de tolerancia. Las 2 que §5.3 no encontró sí aparecen al comparar también por quechua (el español se corrigió en el unificado).

## 6. AmericasNLP 2021 es–quy (§5.5)

| Conjunto | Archivos | Líneas es | Líneas quy |
|---|---|---|---|
| train (JW300) | `train.es`, `train.quy` | 125008 | 125008 |
| dev (sureño estándar) | `dev.es`, `dev.quy` | 996 | 996 |
| dict (MINEDU + Dict_misc) | `dict.es`, `dict.quy` | 9643 | 9643 |
| es-quy/jw300 | `es-quy/jw300.es-quy.es`, `es-quy/jw300.es-quy.quy` | 125008 | 125008 |
| es-quy/minedu | `es-quy/minedu.quy-es.es`, `es-quy/minedu.quy-es.quy` | 643 | 643 |
| es-quy/dict_misc | `es-quy/dict_misc.quy-es.es`, `es-quy/dict_misc.quy-es.quy` | 9000 | 9000 |
| test (solo español) | `test.es` | 1003 | — |

- Total de pares (train + dev + dict): **135,647**. El equipo hablaba de ~180k: **no coincide**. La cifra real es la del archivo (el README confirma que `train` = solo JW300 quy; `dict` = MINEDU 643 + Dict_misc 9 000). No afecta a los bloques: AmericasNLP solo se usa como léxico de referencia (P4).
- `es-quy/jw300` es idéntico a `train` (mismo tamaño); `dict` = `minedu` + `dict_misc`.
- `test` solo trae español (1 003 líneas), como dice §5.5.

## 7. PDF y página web (identificados por contenido)

| Archivo | Páginas | Páginas con texto | Qué es | Inicio del texto |
|---|---|---|---|---|
| `PDF Manual de Quechua Socemurp Compress _ ILIDE.INFO Platform PDF Viewer (1).pdf` | 78 | 0 | Manual de Quechua médico SOCEMURP (2021). Solo imagen (§5.4). | (sin texto) |
| `Yachakuqkunapa simi qullqa. Ayakuchu Chanka Qichwa simipi (1).pdf` | 264 | 263 | Diccionario MINEDU *Yachakuqkunapa Simi Qullqa* (2014), chanka. **Tiene capa de texto**: se usa en F2 para verificar P6. | «Yachakuqkunapa Simi Qullqa DISTRIBUIDO GRATUITAMENTE POR EL MINISTERIO DE EDUCACIÓN - PROH…» |
| `ManualSemiologiaQuechua-2020.pdf` | 80 | 75 | Lopera Quiroga (2020), *Manual de Semiología en Quechua* (Puno/collao). Con texto. | «Decano Dr. Miguel Palacios Celi Vicedecano Dr. Ciro Maguiña Vargas Secretario del Interior…» |
| `entrevistaquechua_spa.pdf` | 96 | 94 | Confirmado: «Diálogo médico paciente en QUECHUA – Bolivia 2013» (OPS/OMS). | «Diálogo médico paciente en QUECHUA Bolivia 2013…» |
| `manualparaelempleodelquechuachankaenlaadministraciondejusticia.pdf` | 150 | 136 | Manual para el empleo del quechua chanka en la administración de justicia (MinCul). Con texto. | «MANUAL PARA EL EMPLEO DEL EN LA ADMINISTRACIÓN DE JUSTICIA QUECHUA CHANKA Hablando en nues…» |
| `AFICHE_COVID 19 LAVADO DE MANOS MINSA quechua chanka.pdf` | 1 | 1 | Afiche MINSA lavado de manos en quechua chanka. Con texto. | «Makikipi pulsirakunata anillukunatapas urqukuy Makikita achka yakuwan chapuy Makikita achk…» |
| `8361447-diabetes_mellitus_quechua.pdf` | 1 | 1 | Diabetes mellitus 2, vía HEARTS, en quechua (gob.pe). Con texto. | «DIABETES MELLITUS 2 KAPTIN YANAPAY HEARTS NISQAPI RURAYKUNA *Kay documentoqa manam wiksaya…» |
| `5660130-manejo-de-paciente-con-diabetes-mellitus-2.pdf` | 1 | 1 | Diabetes mellitus 2, vía HEARTS, en español (gob.pe). Con texto. | «PARA DIABETES MELLITUS -2 VÍA DE ABORDAJE HEARTS *Este protocolo no aplica para personas g…» |

- SOCEMURP: 78 páginas (esperado 78) → ✔ igual.

- `Quechua médico.html`: **Farfán Cantero (2001), revista SITUA**, «Quechua médico» (UNSAAC, Cusco) → quechua **cusqueño**. Codificación Windows-1252 (las tildes se ven mal si se abre como UTF-8). No es Allin Kawsay.

## 8. Trabajo previo de un compañero (§5.7, solo precedente)

Archivos: `[Vibe]EDA_Corpus_NLP.ipynb`, `Corpus_Recopilado.xlsx`. No se usan como fuente de datos ni de alertas.

## 9. Veredicto

- Cifras marcadas «✖ DIFIERE»: **0**.
- Ver el comentario de cada sección: las diferencias se explican por cómo se cuenta (filas vacías, bibliografía, heurísticas), no por otra versión del archivo, salvo que se indique lo contrario.
- AmericasNLP: 135,647 pares, no ~180k. Solo se usa como léxico de referencia (P4), así que no cambia la composición de los bloques.
