# Decisiones tomadas

> Cada valor por defecto usado (CLAUDE.md §4) y cada decisión propia, con su porqué. Juan revisa al final.
> Formato: **[Fase] Decisión** — porqué.

## Instalaciones (regla de Juan: instalar lo necesario, nada de simulaciones)

| Qué | Versión | Para qué |
|---|---|---|
| Entorno `.venv` (Python 3.14.7, `py -3.14`) | 3.14.7 | Entorno propio del proyecto; no se tocan `inf659_env` ni `.venvs`. |
| pandas, openpyxl, python-docx, rapidfuzz, pypdfium2, pyyaml, matplotlib | ver `requirements.txt` (versiones fijadas) | Lo pedido en F0. |
| numpy, pillow | ver `requirements.txt` | Ya venían con pandas/matplotlib; se fijan porque f6 (matriz de similitud) y `render_revision.py` (PNG) los usan directamente. |
| LibreOffice (winget `TheDocumentFoundation.LibreOffice`) | 26.8.1 | En la PC no hay Word ni Excel. Se usa en F7 para abrir de verdad cada `.docx`/`.xlsx`, convertirlo a PDF y mirar las páginas. |

## F0 – Preparación

- **[F0] Estructura real de carpetas ≠ §7.1.** Las fuentes están en `Fuentes/` (no en la raíz) y CLAUDE.md en `Estrategia/`. Las salidas (`02_maestro/`, `03_bloques/`, `04_reportes/`, `05_audio/`, `06_dataset/`, `scripts/`, `config.yaml`, `.venv/`) van en la raíz `D:\Corpus_Quechua\`. Las rutas están en `config.yaml` (`rutas.fuentes`). No cambia la composición de los bloques.
- **[F0] `Estrategia/INF657_CLAUDE_corpus.md`** es una copia idéntica de CLAUDE.md anterior a la regla de instalación. No se usa ni se modifica.
- **[F0] Python 3.14** (el más nuevo instalado; también hay 3.10). Todos los paquetes tienen ruedas para 3.14.
- **[F0] Fecha fija en `config.yaml` (`fecha_generacion`)** para checkpoints, Cambios y la pestaña LEEME: así volver a correr los scripts produce exactamente lo mismo (§14, idempotencia). Era `2026-10-14`; pasó a `2026-10-15` al regenerar todo tras la revisión ultracode (los checkpoints del 14 quedan como historia).
- **[F0] LibreOffice instalado** porque la PC no tiene Word ni Excel y F7 exige abrir cada archivo generado (regla de Juan: instalar, no simular).
- **[F0] Huella de las fuentes** (`04_reportes/huella_fuentes_F0.json`: tamaño, fecha y sha256 de los 31 archivos de `Fuentes/` y `Estrategia/`) para comprobar en F7 que no se tocaron. Se tomó **después** de agregar la regla de instalación a CLAUDE.md (pedido de Juan).

## F1 – Inventario

- **[F1] Las cifras de §5 coinciden** (0 diferencias grandes). No hubo que detenerse. Diferencias pequeñas explicadas en `INVENTARIO.md`: Grupo 2 tiene 669 oraciones reales (F-0517 vacía, F-0013 duplicado, 3 filas de bibliografía); AmericasNLP tiene 135 647 pares (no ~180k); solo se usa como léxico (P4), así que no cambia los bloques.
- **[F1] `Quechua médico.html` = Farfán Cantero (2001), SITUA (Cusco)**, no Allin Kawsay. Está en Windows-1252.
- **[F1] `entrevistaquechua_spa.pdf` = OPS/OMS Bolivia 2013** (confirmado por la portada).
- **[F1] Grupo 3 «Términos médicos»:** última fila con columnas invertidas (Aycha/Músculo) y «Hueso → Tullu nanay» desalineado. Es solo referencia; no se corrige.

## F2 – Ingesta

- **[F2] Qué entra a los bloques:** unificado (médico) + Principito + Grupo 2 (general). Grupo 3 original, Términos y Corpus_Construido solo para cruzar (D10). Corpus_Construido: sus 111 filas están en el unificado (por español o quechua).
- **[F2] Tipo_borrador ampliado.** La lista de §8.2 no cubría todas las fuentes del unificado; se agregaron: «Allin Kawsay (transcripción)», «normalizado de Farfán (cusqueño)», «fuente chanka oficial» (MinCul y afiche), «YouTube (transcripción)», «MINSA (material en quechua)». Filas sin quechua → «ninguno».
- **[F2] P6 verificado de verdad contra el diccionario MINEDU.** El PDF del diccionario tiene capa de texto: se extrajeron sus ~2 300 ejemplos y se compararon (rapidfuzz, ≥ 90) con el quechua y el español de cada fila del Grupo 2, junto con las 643 frases MINEDU de AmericasNLP. **Solo 2 de 669 coinciden.** Conclusión: las frases del Grupo 2 no son ejemplos del diccionario; son frases del equipo con léxico chanka. Se mantiene la clasificación de §5.2 (minúscula o pronombre inicial → «ejercicio generado»; el resto → «MINEDU», pool «frases variadas») con `Origen_verificado = No` (salvo las 2). La evidencia (similitud máxima y texto más parecido) queda en `Origen`.
- **[F2] Grupo 2: 124 frases variadas y 545 ejercicios** (no ~170 / ~500 como estimaba §11.1).
- **[F2] Rol por heurística** (`scripts/heuristicas.py`): preguntas y órdenes → Médico; 1.ª persona → Paciente; «Si …» sin tilde es condicional (Médico); «Le voy a…», «Quiero preguntar…», «Yo soy el doctor…» y la sección «Presentación del profesional / acceso lingüístico» → Médico. Revisé a mano las 40 filas que salen como Paciente.
- **[F2] Etapas:** mapeo de §11.3. Secciones que no estaban en la tabla: «14. Puericultura y controles» → Recolección; «16. Hospital, procedimientos y evolución» → Explicación y plan; 2 filas de Farfán sin sección quedan «Sin sección» (prioridad baja).
- **[F2] EL-0001:** la nota de plantilla de Observaciones se ignora (§5.2).

## F3 – EDA

- **[F3] Léxico de referencia para OOV/préstamos:** JW300 quy (2+ apariciones), diccionario MINEDU (PDF + AmericasNLP), Dict_misc, MinCul, afiche y diabetes en quechua; solo formas escritas con el alfabeto chanka. Raíces: ~1 000 lemas del diccionario MINEDU + entradas de una palabra de Dict_misc. El español de referencia sale del lado español de AmericasNLP (solo palabras vistas en minúscula, para no contar nombres propios).
- **[F3] Reglas de QA probadas con los casos de §6** (`scripts/test_qa.py`): los 32 casos salen marcados, el DUP de QCH-0050 también, y la normalización mecánica da lo esperado sin tocar préstamos ni nombres propios («Lince», «Ayacuchomanta», «Coronavirus»).
- **[F3] Casi duplicados:** similitud ≥ 90 **y** misma polaridad **y** mismos números; máximo 2 por grupo, y si dos tienen el **mismo borrador quechua** solo queda 1 (p. ej. «ellos/ellas bajan al río» → «Paykuna mayuman uraykunku»: grabarlo dos veces no aporta).
- **[F3] Figuras** con la paleta de referencia validada (slots 1–3), barras finas, texto en tinta y leyenda solo con 2+ series. Son PNG estáticos dentro de un .md, sin capa interactiva; las tablas del EDA hacen de «vista de tabla».

## F4 – Limpieza

- **[F4] Datos revisados a mano** en `scripts/datos/`: `erratas_es.yaml` (erratas evidentes y tildes, sacadas de las palabras que no están en el léxico español de referencia), `adaptaciones_es.yaml` (giros bolivianos del OPS/OMS, preguntas múltiples, notas entre paréntesis → Revisar_Juan) y `particiones_es.yaml` (oraciones de más de 20 palabras). Todo cambio queda en `Cambios` con su regla.
- **[F4] Oraciones largas:** 15 se partieron en unidades de ≤ 15 palabras (Revisar_Juan) y 2 se descartaron (QCH-0520: datos administrativos de 2020; QCH-0544: cortada en la fuente a 255 caracteres). Las piezas solo llevan borrador si es un trozo **literal** del borrador original (el script lo comprueba); si no, quedan sin borrador.
- **[F4] Varias celdas del unificado están cortadas a 255 caracteres** (QCH-0478, QCH-0483, QCH-0544): defecto de la fuente. Al partirlas se completó la idea en español.
- **[F4] Notas entre paréntesis** («(hablando de otra persona)», «(tórax)», «(deseo de comer)») se quitan del español porque no se leen en voz alta. Cuando cambiaban el sentido («Tiene que quedarse en el hospital (hablando de otra persona)»), se reescribió con el pronombre («Él tiene que quedarse…», Revisar_Juan).
- **[F4] Coletilla «¿sí o no?»** al final de preguntas (indicación al entrevistador) se quita.
- **[F4] Léxico:** van a `Lexico` las filas médicas de 1 palabra y las de 2–3 palabras de secciones de vocabulario que no son preguntas. Prioritarias = categorías «Signos y síntomas», «Cuerpo humano», «Enfermedades…», «Fluidos…», «Funciones…». Reciben IDs `LEX-0001…` (decisión propia; §8.1 solo define GEN/CLI).
- **[F4] Duplicados exactos (mismo español normalizado):** queda el de mejor borrador; entre dominios gana el médico («Buenos días», «¿Cuántos años tienes?» del Principito/Grupo 2 se descartan a favor de las del unificado). Los otros borradores distintos quedan en `Origen` (Otros_borradores) y en QA (DUP/BAJA).
- **[F4] Casi duplicados:** además de polaridad y números, pregunta y afirmación nunca son paráfrasis («¿Le duele la cabeza?» ≠ «Me duele la cabeza.»).
- **[F4] Ortografía mecánica (§10.3)** solo cuando no es préstamo ni nombre propio; la escritura castellana (c/qu/j/hu) solo se cambia si la palabra resultante existe en el léxico de referencia (así no se inventan palabras: «mayllijunayki» queda marcado en QA, no se «corrige» a algo inexistente). Fuentes oficiales chanka: tal cual.
- **[F4] Registro de IDs** `02_maestro/ids.csv` (uid → ID): un uid nunca cambia de ID entre corridas; las filas nuevas toman el siguiente número libre. Mientras nada se envió al traductor, el registro se regeneró desde cero para que los IDs queden correlativos.
- **[F4] Avisos de QA ajustados tras revisar la pestaña** (falsos positivos que ya no salen, con prueba en `test_qa.py`): «nada» (verbo nadar) no cuenta como negación; ordinales y compuestos se comparan por componentes («catorce» = chunka tawayuq; «segundo piso» = iskay); «cuarto» no es número; si el español ofrece «¿poco o mucho?» no hay contradicción; la sugerencia de transcripción solo propone palabras completas frecuentes del léxico. Negación ausente pasa a MEDIA (el quechua puede expresarla de otro modo).

## F5 – Llenar huecos

- **[F5] B01 curado a mano** (`scripts/datos/plan_b01.yaml`): una consulta completa de dolor de barriga (paciente mujer de 20 años de Ayacucho), con las 6 etapas de §11.2: Inicio 10, Motivo 8, Caracterizar 14, Síntomas asociados 10, Examen físico 7, Explicación/plan/cierre 11 = 60 (32 médico / 28 paciente). Esqueleto con frases del manual SOCEMURP; 23 líneas nuevas en español (22 del paciente y «¿Entendiste lo que tienes que hacer?» del médico, que no existía en el corpus).
- **[F5] B02–B05 por tema** (`scripts/plan_medico.py`), en el orden por defecto de §11.2: B02 fiebre, respiratorio, digestivo, urinario, antecedentes básicos (medicamentos, alergias), niño enfermo (fiebre, diarrea, vómitos: «¿Su niño puede beber o mamar?»), embarazo («¿Estás embarazada?», que antes quedaba en B05); B03 pérdida de conocimiento, dolor de pecho, falta de aire, embarazo con señales de alarma (sangrado, líquido, el bebé se mueve menos, hinchazón), sangrados, tratamiento, seguimiento, tranquilizar; B04 cabeza/nervios, huesos, ojos/oídos, otros síntomas, examen físico, diagnóstico; B05 salud reproductiva, anticoncepción, salud mental, violencia (frases neutras), promoción, hospitalización, antecedentes y entorno. En cada tema: primero preguntas y luego mejor borrador; reparto en ronda para que cada tema tenga voz. 30 frases del médico por bloque.
- **[F5] Datos de morbilidad:** se buscó en la web el ranking de consulta externa de Ayacucho/Apurímac/Huancavelica (MINSA/CDC). No se encontró un ranking regional publicado en línea; solo cifras regionales de IRA (Diresa Ayacucho, ~25 000 casos de IRA a la semana 18 de 2024, según elbuho.pe) y el ranking nacional de consulta externa (Rev. Med. Herediana). Se usó el orden por defecto de §11.2, que pone respiratorio y digestivo primero (B02), coherente con esos datos.
- **[F5] Respuestas del paciente** (`scripts/datos/respuestas_paciente.yaml`): 1 por pregunta (a veces 2), en español peruano sencillo; también respuestas breves a algunas indicaciones o diagnósticos («¿Por eso me arde al orinar?»). 111 filas en B02–B05 (más 22 del paciente en B01). Ninguna repite otra frase del corpus (F5 lo controla y con `--estricto` no escribe nada si hay repetidas o preguntas sin respuesta).
- **[F5] Oraciones generales redactadas por Claude** (`scripts/datos/oraciones_generales.yaml`, pool `g_claude`), a pedido de Juan («el 70 % general en distintos tiempos para que aprenda el modelo»; «puedes redactar algunas para enviarlas al traductor»): 375 oraciones cortas de vida cotidiana andina, solo en español, en 10 grupos (pasado -rqa-, pasado narrativo/«dicen que», futuro, progresivo, pasado habitual, imperativo, condicional, preguntas, subordinadas, derivación verbal). El quechua lo pone el traductor. Quedan con Estado Revisar_Juan.
- **[F5] Frases portadoras** (`scripts/datos/frases_portadoras.yaml`): 9 dentro de B03–B05 y 20 más que quedan en el corpus para bloques futuros; cada una enlazada a su palabra en `Lexico` (columna Frase_portadora).
- **[F5] Rol de las filas nuevas**: lo pone Claude (Paciente / Médico), no la heurística. Quien responde puede ser el acompañante (p. ej. la mamá).
- **[F5] Excluidas a mano** del plan QCH-0588 «¿Esta su hijo o hija o la señora gestante?» (redacción confusa) y QCH-0607 «¿Miras bien?» (mismo borrador que «¿Ves bien?»; en el mismo bloque se contradecían). Siguen en el corpus.
- **[F5] El plan médico se calcula en F5** (para saber qué preguntas necesitan respuesta) y F6 lo usa tal cual (columnas Plan_bloque / Plan_unidad / Plan_orden del checkpoint F5).

## F6 – Priorización y bloques

- **[F6] Bloques planificados: 5** (B01–B05), los 5 con Word y Excel (Juan los pidió todos). Límite: la parte general de las fuentes (739 tras la limpieza) más las 375 redactadas por Claude; con el tope de 35 ejercicios por bloque no alcanza para un sexto bloque (quedan 14 redactadas y 400 ejercicios). La parte médica tiene material de sobra (840 frases sin asignar), pero cada bloque necesita voz del paciente redactada.
- **[F6] Selección voraz (§11.1)** con cobertura **dentro de cada bloque** (el conjunto cubierto se reinicia en cada bloque, para que cada bloque sea por sí mismo variado). Puntaje = (3 × sufijos nuevos + 1 × bigramas nuevos + 0.5 × palabras nuevas) ÷ (palabras del quechua)^0.5. Empates: Principito > frases variadas > ejercicios, luego la más corta. Determinista (sin azar).
- **[F6] B01 general con oraciones de ≤ 12 palabras** en español (§11.1).
- **[F6] Cuotas de la parte general** (`config.yaml` → `general.cuotas_por_bloque`): Principito ~35, frases variadas ~70, **al menos 40 oraciones redactadas por Claude en varios tiempos** y como máximo 35 ejercicios del Grupo 2 (todos en presente). Si un origen se acaba, se completa en el orden Principito → frases variadas → redactadas → ejercicios. Resultado (Principito / frases variadas / ejercicios / redactadas): B01 35/65/0/40, B02 35/56/9/40, B03 34/0/35/71, B04 0/0/35/105, B05 0/0/35/105. El mínimo era 25 y se subió a 40 porque con 25 B02 quedaba con 76 % de la parte general en presente (medido sobre el verbo en español, igual para todas las filas).
- **[F6] Mezcla de tiempos resultante** (parte general, verbo en español): presente 57 % / 65 % / 55 % / 45 % / 44 % en B01–B05; el resto pasado (12–24 %), futuro (6–15 %), progresivo (5–10 %), condicional e imperativo. F7 exige ≤ 65 % de presente por bloque.
- **[F6] Sublotes:** cada unidad médica (pregunta + respuestas) va entera en el sublote donde empieza (15 por sublote); por eso hay sublotes de 34+16 o 36+14. La parte general se reparte **por origen** en ronda entre los 4 sublotes (así los ejercicios no se juntan en un sublote) y dentro del sublote se mezclan los orígenes y se intercalan entre las unidades médicas.
- **[F6] Control (D7, activo):** 15 filas de B01 con borrador (10 generales + 5 médicas de buena calidad, calidad ≤ 4), repartidas entre los 4 sublotes con semilla fija 657. Van con la celda Quechua vacía y **sin aviso** en Observaciones (el aviso podría revelar el borrador). No se elige una fila que tenga una «hermana» con borrador visible en la misma entrega B01+B02 (quechua ≥ 75 % o español ≥ 85 % parecido), porque el traductor vería casi la misma solución. Tampoco «Mi tía hace chicha punta» (`control.excluir_codigos`): sin borrador, «punta» no se entiende.
- **[F6] Test_sugerido (P1):** 20 filas por bloque (14 generales proporcionales a cada origen + 3 pares completos pregunta/respuesta), sin tocar las de control ni filas con una casi gemela (≥ 85 %) en los bloques. Semilla fija. Todo sigue con Split = train.
- **[F6] Prioridad** = número del bloque planificado (1–5); vacío si aún no tiene bloque.
- **[F6] Columnas extra en Corpus** (al final): Control, Responde_a, N_bloque. Origen lleva además Códigos_unidos, Otros_borradores, Propuestas_equipo, Parte_de, Evidencia_P6, Fuente_detalle.
- **[F6] Estados:** Borrador, Sin borrador, Revisar_Juan, Enviado, Validado, Grabado (lista desplegable). «Enviado» se pone con `06_importar_traductor.py BXX --marcar-enviado` al mandar el Word (queda en Cambios).
- **[F6] Bloques congelados:** un bloque con filas Enviado/Validado/Grabado (o listado en `bloque.congelados`) ya no se rearma: f6 copia su composición, N°, sublotes, control y test del maestro anterior y no regenera su Word ni su Excel. Si una de sus filas desaparece del corpus, f6 se detiene y lo dice.
- **[F6] Word del traductor:** A4 horizontal, Calibri 11, instrucciones y tabla de ortografía en la página 1, una tabla por sublote con encabezado repetido y filas que no se parten entre páginas; **1 aviso ALTA por fila**, en letra 11, cursiva gris (§8.4: una línea breve). Instrucción de no usar Control de cambios. Sin fuentes, estados ni columnas técnicas.
- **[F6] Al regenerar el maestro** se conserva lo que ya devolvió el traductor (Quechua_validado, Estado, Traductor_metricas y los registros de 06 en Cambios) **solo si el español de la fila sigue igual**; si cambió, la fila vuelve a Revisar_Juan con una nota (hay que reenviarla). Del Excel de trabajo se conservan las casillas de grabación, Notas, % de edición y comentarios del traductor.
- **[F6] Marca de corrida completa:** el checkpoint F6 se escribe al final; si algo falla antes (p. ej. un Word abierto), la siguiente corrida rehace todo aunque no se pase `--forzar`.
- **[F6] Archivo devuelto por el traductor:** se guarda como `03_bloques/BXX/BXX_traductor_devuelto.docx` y se importa con `06_importar_traductor.py BXX`.
- **[F6] Métricas del traductor:** distancia de edición normalizada (Levenshtein, rapidfuzz) entre borrador y final: 0 = sin cambios; ≤ 0.5 = editado; > 0.5 = reescrito. Anclaje (D7): razón entre la distancia media con borrador y la distancia entre el borrador oculto y la traducción libre de las oraciones de control; < 0.5 = posible anclaje. Si reescribe más del 50 % → recomendar dejar de dar borradores.
- **[F6] Importación del traductor (06):** no importa un Word con Control de cambios sin aceptar; una fila cuyo español cambió el traductor no se valida (queda Revisar_Juan y su propuesta va a Cambios); si un sublote vuelve 100 % igual al borrador (≥ 10 filas) sus filas no se validan solas hasta confirmarlo (`--confirmar-sublotes`); todo lo importado queda en Cambios y reimportar no duplica registros.
- **[F6] Audios:** se buscan por nombre `{ID}_es.wav` / `{ID}_qu.wav` en cualquier subcarpeta de `05_audio/`, sin distinguir mayúsculas; si el mismo nombre aparece en dos carpetas, se avisa. Duración razonable: 0.4–20 s y no más de 2 s por palabra (si dura más de 3 s). Se revisan con el módulo `wave` de Python (no hizo falta instalar nada más).

## Revisión ultracode (§14.2), 15-oct-2026

Tres revisores independientes (A: datos y trazabilidad; B: bloques y archivos; C: scripts y reproducibilidad) encontraron 39 hallazgos (H1–H39), ninguno que invalidara los datos. El verificador cruzado se detuvo por límite de uso; los hallazgos que reportaron dos revisores se dieron por confirmados. Todo lo corregido se probó (`test_qa.py`, `test_ida_vuelta.py`) y se regeneró la cadena completa 01 → f7.

| Hallazgo | Qué se hizo |
|---|---|
| H1 IDs que dependían de la posición en los YAML; quechua validado que podía quedar pegado a otra frase | El uid de toda fila redactada o partida lleva una huella del texto; f6 y 06 comparan el español antes de conservar o validar. Como nada se envió, el registro de IDs se rehízo desde cero (el anterior quedó en `02_maestro/checkpoints/ids_antes_revision_20261015.csv`): **los IDs cambiaron respecto de los archivos del 14-oct.** |
| H2, H6, H7 importación (Control de cambios, control con distancia 0, Word devuelto sin tocar) | 06 reescrito (ver F6). |
| H3 regenerar borraba lo del equipo; 06 sin rastro | Se conservan columnas del equipo y registros de 06; 06 escribe en Cambios. |
| H4 B01/B02 casi todo en presente | Mínimo de 40 oraciones redactadas en varios tiempos por bloque; F7 lo controla (≤ 65 % presente). |
| H5 bloques enviados no se congelaban | Congelado automático (ver F6). |
| H8 reintento tras un fallo | Checkpoint F6 al final. |
| H9 parámetros fijos en el código | A `config.yaml`: médico por bloque, largo máximo, calidad del control, umbrales de 02/06/08, avisos por fila, formato de audio. |
| H10, H17, H25, H26 reportes y maestro | REVISION_JUAN apunta al archivo correcto y muestra el borrador de las filas adaptadas; Bloques separa redactadas generales/médicas y calcula «Sin asignar»; LEEME describe todas las pestañas y el prefijo LEX-. |
| H11, H12, H29 cifras desactualizadas | Se regeneraron INVENTARIO, EDA, ENTREGA, PROGRESO y estas decisiones con las cifras de la corrida final. |
| H13 frase repetida entre bloques | F5 compara las frases nuevas con todo el corpus; F7 controla que ningún español se repita en los bloques. |
| H14, H22 erratas y frases poco naturales | 9 erratas nuevas (`erratas_es.yaml`), 27 adaptaciones (`adaptaciones_es.yaml`, Revisar_Juan) y 9 fragmentos o frases inoportunas descartadas (`descartes_es.yaml`, nuevo). No se cambió el calco «no + una» de algunos ejercicios («Yo no leo una revista»): es opcional y Juan decide. |
| H15, H23, H24, H27 avisos de QA | Préstamos de fuentes oficiales, médicos o que repiten un sustantivo del español → BAJA; sin pista «(de …)»; sugerencias de transcripción más prudentes; aviso cuando el equipo marcó el borrador como dudoso; 3 avisos puestos a mano (`avisos_manuales.yaml`). |
| H16, H28, H34 duplicados | La clave conserva la ñ («Año» ≠ «Ano»); el paréntesis del léxico se mantiene; no se agrupan frases con quechua distinto; las oraciones redactadas no pasan por el filtro de casi duplicados. |
| H18 ejercicios juntos en un sublote | Reparto por origen. |
| H19, H39 respuestas contradictorias o sin Responde_a | 8 respuestas corregidas (caso de B01 sin «dolor que se mueve a la derecha», medicamentos, sangre, gusanos, pareja), «Responde_a» en B01, QCH-0607 excluida. |
| H20, H37 control con hermanas; test con gemelas | Ver F6. |
| H21 temas faltantes de §11.2 | Niño enfermo y embarazo en B02; embarazo con señales de alarma en B03; las respuestas que dejaban al paciente preguntando dosis sin respuesta se cambiaron. |
| H30–H33, H35, H36, H38 scripts y pruebas | `--estricto` no escribe nada; `00_huella_fuentes --forzar` no pisa una huella distinta sin `--aceptar-cambios`; F7 corre las pruebas en el momento y su pie depende de lo que hizo; 08 avisa audios repetidos; pruebas nuevas en `test_qa` y `test_ida_vuelta`; rutas relativas iguales en 06–08; mezcla de tiempos medida igual en todos los bloques. |

## Valores por defecto usados (§4)

| # | Valor usado | Dónde se ve |
|---|---|---|
| P1 | Todo `Split = train`; `Test_sugerido = Sí` en 20 filas por bloque (10 %, estratificado). | Corpus, Detalle, Resumen |
| P2 | Fecha desconocida → B01 y B02 listos para enviar ya (D5); por pedido de Juan, también B03–B05 tienen archivos. | `03_bloques/B01` … `B05` |
| P3 | Se asume el alfabeto oficial de 3 vocales; el Word se lo pide al traductor con una tabla corta. | Página 1 del Word |
| P4 | AmericasNLP **no** se usa para oraciones; solo como léxico de referencia (OOV/préstamos). La variedad de tiempos de B03–B05 la dan las oraciones redactadas por Claude; P4 haría falta solo para pasar de 5 bloques. | ENTREGA |
| P5 | WAV, 16 kHz, mono, 16 bits (en `config.yaml` y en la guía); falta confirmarlo con el equipo de modelo. | GUIA_GRABACION, 08_manifest |
| P6 | Verificado contra el diccionario MINEDU en PDF: las frases del Grupo 2 no son ejemplos del diccionario (2 de 669). `Origen_verificado = No` salvo esas 2. | Origen |
| P7 | Audios de Allin Kawsay no se usan (no hay `.mp3` en la carpeta). | INVENTARIO |
