# ENTREGA — Corpus quechua chanka médico (F0–F7 + revisión ultracode)

Para: equipo del proyecto · Fecha: 2026-10-15 · Preparado por Claude (Claude Code) en `D:\Corpus_Quechua`

## En 5 líneas

1. El corpus quedó en un solo archivo maestro: **2 254 oraciones** (1 114 generales + 1 140 médicas), 545 palabras sueltas en Léxico y 92 descartes con su motivo. Nada se borró sin rastro.
2. **Los 5 bloques (B01–B05) tienen su Word para el traductor y su Excel de trabajo.** B01 es una consulta completa de punta a punta (dolor de barriga) con 15 oraciones de control.
3. **La parte general (70 %) ahora enseña distintos tiempos:** en cada bloque hay entre 40 y 105 oraciones que redacté en español (pasado, futuro, progresivo, condicional, imperativo, preguntas, subordinadas). El presente quedó entre 44 % y 65 % según el bloque.
4. **Se hizo la revisión ultracode:** 3 revisores, 39 hallazgos, todos atendidos y probados (detalle en `DECISIONES_TOMADAS.md`). **Los IDs cambiaron** respecto de los archivos del 14-oct (no se había enviado nada).
5. Antes de enviar, **revisa el español que redacté o adapté** (`Por_revisar`): 72 filas en B01 y 77 en B02. Ningún quechua es «gold»: todo lo prellenado es borrador y yo no escribí quechua.

## Qué está listo

| Qué | Dónde |
|---|---|
| Archivo maestro (única fuente de verdad): LEEME, Corpus, Origen, Cambios, Descartes, Lexico, QA, Bloques, Traductor_metricas | `02_maestro/corpus_maestro.xlsx` |
| **Word para el traductor de B01–B05** (A4 horizontal, instrucciones, 4 tablas de 50, borrador prellenado, 1 aviso breve por fila como máximo) | `03_bloques/B0X/B0X_traductor.docx` |
| Excel de trabajo de B01–B05 (pestañas Bloque / Detalle / Resumen) | `03_bloques/B0X/B0X_trabajo.xlsx` |
| Guía de grabación (protocolo, regla D8, nombres de archivo, formato de audio) | `03_bloques/GUIA_GRABACION.docx` |
| **Español para tu revisión** (antes de enviar), con el archivo donde se corrige cada fila | `04_reportes/REVISION.md` |
| Reportes: inventario, EDA, decisiones, verificación final, prueba de scripts, huecos de F5 | `04_reportes/INVENTARIO.md`, `EDA.md`, `DECISIONES_TOMADAS.md`, `VERIFICACION_F7.md`, `PRUEBA_06_07_08.md`, `F5_huecos.md` |
| Scripts reproducibles (todo se regenera desde las fuentes) | `scripts/` + `config.yaml` |
| Scripts de operación probados con datos simulados | `scripts/06_importar_traductor.py`, `07_hoja_grabacion.py`, `08_manifest.py` |

La verificación final (`04_reportes/VERIFICACION_F7.md`) revisa cada punto del checklist de §13, corre las pruebas y abre cada .docx/.xlsx con LibreOffice; las páginas convertidas están en `04_reportes/revision_visual/`.

## Qué enviar a quién

1. **Revisión del equipo primero:** revisa `04_reportes/REVISION.md` (B01 y B02 son lo urgente). Si cambias algo, edita el archivo de `scripts/datos/` que indica la tabla y vuelve a generar (ver «Cómo regenerar»).
2. **Al traductor:** envía **`B01_traductor.docx` y `B02_traductor.docx`** juntos (D5: siempre un bloque adelante). Pídele que devuelva **el mismo archivo**, sin mover filas, sin tocar la columna ID y sin «Control de cambios». Yo no envié nada a nadie.
3. **Al enviarlos, márcalos como enviados:** `.venv\Scripts\python.exe scripts\06_importar_traductor.py B01 --marcar-enviado` (y lo mismo con B02). Desde ahí esos bloques quedan **congelados**: al regenerar, no cambian sus filas, N° ni sublotes.
4. **Cuando vuelva cada Word:** guárdalo como `03_bloques/B01/B01_traductor_devuelto.docx` y corre `.venv\Scripts\python.exe scripts\06_importar_traductor.py B01` (con los Excel cerrados). Escribe el quechua validado en el maestro y en el Excel de trabajo, registra todo en Cambios, separa los comentarios, calcula las métricas y el análisis de control, y deja `04_reportes/importacion_B01.md`. Protecciones:
   - Si el Word trae Control de cambios sin aceptar, no lo importa y te dice cómo aceptarlos.
   - Si el traductor cambió el español de una fila, esa fila no se valida: queda `Por_revisar` y decides tú.
   - Si un sublote vuelve sin ningún cambio, sus filas no se validan solas: confirma con el traductor que lo revisó y reimporta con `--confirmar-sublotes B01-S2`.
5. **Para la sesión de grabación:** `scripts\07_hoja_grabacion.py B01` → `03_bloques/B01/B01_grabacion.docx`. Dale al grabador esa hoja y `GUIA_GRABACION.docx`.
6. **Después de grabar:** pon los audios en `05_audio/` (`{ID}_es.wav`, `{ID}_qu.wav`) y corre `scripts\08_manifest.py B01` → `06_dataset/manifest_B01.csv`, con el control de formato, duración y nombres repetidos.

## Qué debes revisar

- **Español redactado o adaptado por mí (`Por_revisar`):** 72 filas en B01, 77 en B02, 109 en B03, 144 en B04 y 136 en B05. Son:
  - oraciones generales nuevas en varios tiempos (`oraciones_generales.yaml`);
  - respuestas del paciente y frases portadoras (no existían en las fuentes);
  - adaptaciones de giros bolivianos o frases poco naturales, y oraciones largas partidas. En estas, `REVISION.md` muestra el original y el borrador quechua, para que veas si siguen diciendo lo mismo.
- **El guion de B01** (`scripts/datos/plan_b01.yaml`): paciente mujer de 20 años de Ayacucho con dolor de barriga, fiebre y vómitos. Cambié una respuesta que sugería apendicitis («ahora me duele más abajo, al lado derecho») y no cuadraba con «No es nada grave».
- **Por confirmar:**
  - «Mi tía hace chicha punta» (B01): no sé qué significa «punta» aquí; por eso no se usa como oración de control.
  - Algunos ejercicios del Grupo 2 calcan «no + una» («Yo no leo una revista»). No los cambié: decides si se dejan.
- **Avisos en el Word:** 7 filas en B01, 13 en B02, 27 en B03, 3 en B04 y 1 en B05. Casi todos son «posible préstamo del español» o «el equipo marcó este borrador como dudoso». Son sospechas para que el traductor mire primero, no correcciones.

## Hallazgos que conviene que sepas

- **Grupo 2 (P6):** el diccionario MINEDU en PDF tiene texto, así que lo verifiqué de verdad: **solo 2 de 669 frases** del Grupo 2 aparecen como ejemplos del diccionario. Son frases del equipo con léxico chanka (útiles, pero `Origen_verificado = No`).
- **Lopera (collao):** 510 filas médicas tienen quechua derivado de Lopera, normalizado por reglas. Son borradores, no chanka real.
- **Celdas cortadas en el unificado:** algunas frases largas (COVID-19) están cortadas a 255 caracteres en la fuente; se partieron o descartaron.
- **AmericasNLP** tiene 135 647 pares (no ~180 000). Solo se usó como léxico de referencia.
- **La voz del paciente casi no existía:** 42 frases en el unificado (39 tras la limpieza; el inventario cuenta 46 con una regla de primera persona más amplia). Por eso redacté en español las respuestas del paciente de los 5 bloques.
- **Quedan pocas frases generales de las fuentes:** el Principito y las frases variadas se acaban en B03. Desde B03 la parte general son ejercicios (máximo 35 por bloque) y oraciones redactadas por mí.

## Pendientes (P1–P7)

| # | Qué se usó por ahora | Qué falta decidir |
|---|---|---|
| P1 | Todo `train`; 20 filas por bloque marcadas `Test_sugerido = Sí` (10 % estratificado, sin casi gemelas en los bloques y con pares pregunta/respuesta completos). | ¿Apartamos ese 10 % como prueba? |
| P2 | Fecha desconocida; B01 y B02 listos para enviar (y B03–B05 también tienen archivos). | Fecha de la primera sesión y con cuántos días se envía el Word. |
| P3 | Se asume el alfabeto oficial de 3 vocales; el Word lo pide con una tabla. | Confirmarlo con el traductor. |
| P4 | AmericasNLP **no** se usa para oraciones (solo léxico). La variedad de tiempos la dan las oraciones que redacté. | Solo si se quieren **más de 5 bloques**: usar oraciones cortas no religiosas de AmericasNLP o que yo redacte más. |
| P5 | WAV, 16 kHz, mono, 16 bits (en `config.yaml`, la guía, 07 y 08). | Confirmarlo con el equipo de modelo antes de grabar. |
| P6 | Verificado: el Grupo 2 no sale del diccionario (2 de 669). | Nada, salvo que alguien del Grupo 2 aclare de dónde salieron. |
| P7 | Audios de Allin Kawsay no se usan (y no están en la carpeta). | Nada. |

## Cuántos bloques caben

| Bloque | General: Principito / frases variadas / ejercicios / redactadas | Presente en la parte general | Médica (médico / paciente) y temas | Estado |
|---|---|---|---|---|
| B01 | 35 / 65 / 0 / 40 | 57 % | 32 / 28 — consulta completa (6 etapas) | Archivos listos |
| B02 | 35 / 56 / 9 / 40 | 65 % | 30 / 30 — fiebre, respiratorio, digestivo, urinario, antecedentes, niño enfermo, embarazo | Archivos listos |
| B03 | 34 / 0 / 35 / 71 | 55 % | 30 / 30 — pérdida de conocimiento, dolor de pecho, falta de aire, embarazo con señales de alarma, sangrados, tratamiento, seguimiento | Archivos listos |
| B04 | 0 / 0 / 35 / 105 | 45 % | 30 / 30 — cabeza, huesos, ojos/oídos, otros síntomas, examen, diagnóstico | Archivos listos |
| B05 | 0 / 0 / 35 / 105 | 44 % | 30 / 30 — salud reproductiva, anticoncepción, salud mental, violencia (neutra), promoción, hospital | Archivos listos |

- **Caben 5 bloques** (1 000 oraciones). Sobran 414 generales (400 ejercicios y 14 redactadas) y 840 médicas. Para un sexto bloque haría falta redactar ~100 oraciones generales más (o decidir P4).
- Cada sublote tiene 34–36 generales + 14–16 médicas; cada pregunta va con su respuesta en el mismo sublote.

## Cómo regenerar

Desde `D:\Corpus_Quechua`, con los Excel y Word cerrados (cada script acepta `--forzar` para rehacer su salida):

```
.venv\Scripts\python.exe scripts\04_limpieza.py --forzar
.venv\Scripts\python.exe scripts\05_huecos.py --forzar --estricto
.venv\Scripts\python.exe scripts\f6_armar_bloques.py --forzar
.venv\Scripts\python.exe scripts\f7_verificacion.py
```

- La cadena completa es `00_huella_fuentes → 01_inventario → 02_ingesta → 03_eda → 04_limpieza → 05_huecos → f6_armar_bloques → f7_verificacion`.
- Los IDs están fijados en `02_maestro/ids.csv`: al regenerar, una fila nunca cambia de ID. Si cambias el texto de una frase redactada, recibe un ID nuevo (nunca hereda la traducción de otra).
- Lo que ya devolvió el traductor se conserva solo si el español de la fila no cambió. Los bloques enviados no se rearman.
- Si un archivo está abierto en Word o LibreOffice, `f6` se detiene sin dejar nada a medias. Con `--solo-archivos B03,B04` regenera solo los archivos de esos bloques.

## Instalaciones hechas

- Entorno propio `.venv` (Python 3.14) con pandas, openpyxl, python-docx, rapidfuzz, pypdfium2, pyyaml, matplotlib, numpy y pillow (`requirements.txt`). No se tocaron `inf659_env` ni `.venvs`.
- **LibreOffice 26.8.1** (winget), porque la PC no tiene Word ni Excel y había que abrir de verdad cada archivo generado para revisarlo.
