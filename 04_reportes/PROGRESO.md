# PROGRESO — Corpus quechua chanka médico

> Archivo de estado (CLAUDE.md §14.1). Si la sesión se corta: leer CLAUDE.md (`Estrategia/CLAUDE.md`), luego este archivo, y continuar desde **Siguiente paso**.
> Comando base: `.\.venv\Scripts\python.exe scripts\<script>.py --forzar` desde `D:\Corpus_Quechua`.
> Orden de la cadena: 00_huella_fuentes → 01_inventario → 02_ingesta → 03_eda → 04_limpieza → 05_huecos → f6_armar_bloques → f7_verificacion.
> Scripts de operación (§8.5–8.7): 06_importar_traductor, 07_hoja_grabacion, 08_manifest.

## Fases

| Fase | Estado | Última salida generada (fecha del archivo) |
|---|---|---|
| F0 – Preparación | hecha | 2026-10-14 (inicio 15:18); huella de fuentes verificada el 2026-10-15 (31 archivos, sin cambios) |
| F1 – Inventario | hecha | 2026-10-15 20:19 (`INVENTARIO.md`) |
| F2 – Ingesta al maestro | hecha | 2026-10-15 20:19 (`F2_ingesta_20261015.xlsx`, 2 314 registros) |
| F3 – EDA | hecha | 2026-10-15 20:19 (`EDA.md`) |
| F4 – Limpieza | hecha | 2026-10-15 20:24 (`F4_limpio_20261015.xlsx`) |
| F5 – Llenar huecos | hecha | 2026-10-15 20:24 (`F5_huecos_20261015.xlsx`) |
| F6 – Priorización y bloques | hecha | 2026-10-15 20:25 (maestro, B01–B05, `F6_bloques_20261015.xlsx`) |
| F7 – Verificación final | hecha | 2026-10-15 (`VERIFICACION_F7.md`) |

> Las fases se repitieron varias veces al corregir; la fecha es la de la última salida. Los checkpoints del 14-oct quedan en `02_maestro/checkpoints/` como historia (los scripts leen siempre el más reciente).

## Estado: TODO HECHO · revisión ultracode HECHA y corregida

- **Revisión ultracode (§14.2):** 3 revisores → 39 hallazgos (H1–H39), todos atendidos; tabla en `DECISIONES_TOMADAS.md` («Revisión ultracode»). Se regeneró la cadena completa 01 → f7 el 15-oct.
- **IDs renumerados** (nada se había enviado): el registro anterior quedó en `02_maestro/checkpoints/ids_antes_revision_20261015.csv`. Los IDs de los archivos del 14-oct ya no valen.
- **5 bloques con archivos** (B01–B05): 200 = 140 + 60, sublotes 34–36 + 14–16, médico/paciente 32/28 en B01 y 30/30 en B02–B05. Parte general con varios tiempos (presente 44–65 %), gracias a 375 oraciones generales redactadas por Claude en español (361 en bloques).
- **Pruebas:** `test_qa.py` 0 fallos; `test_ida_vuelta.py` todos PASA (`PRUEBA_06_07_08.md`); verificación F7 en `VERIFICACION_F7.md`.

**Siguiente paso (para Juan):** revisar `04_reportes/REVISION_JUAN.md` (B01 y B02 primero), enviar `B01_traductor.docx` + `B02_traductor.docx` al traductor y marcarlos con `06_importar_traductor.py B01 --marcar-enviado` (ver `04_reportes/ENTREGA.md`).

## Archivos generados

| Fase | Archivo | Script |
|---|---|---|
| F0 | `04_reportes/PROGRESO.md`, `04_reportes/DECISIONES_TOMADAS.md` | (a mano) |
| F0 | `.venv/`, `requirements.txt`, `config.yaml` | (a mano) |
| F0 | `04_reportes/huella_fuentes_F0.json` | `scripts/00_huella_fuentes.py` |
| F0 | LibreOffice 26.8.1 instalado (winget) | — |
| F1 | `04_reportes/INVENTARIO.md`, `04_reportes/inventario_cifras.json` | `scripts/01_inventario.py` |
| F1 | `02_maestro/checkpoints/cache/` (texto de PDF, léxicos) | `scripts/fuentes.py`, `scripts/quechua.py` |
| F2 | `02_maestro/checkpoints/F2_ingesta_20261015.xlsx` (2 314 registros) | `scripts/02_ingesta.py` |
| F3 | `04_reportes/EDA.md`, `04_reportes/fig/f01…f06.png`, `F3_eda_20261015.xlsx` | `scripts/03_eda.py` |
| F3 | Prueba de reglas QA y limpieza (0 fallos) | `scripts/test_qa.py` |
| F4 | `02_maestro/checkpoints/F4_limpio_20261015.xlsx` (1 716 frases, 545 léxico, 92 descartes) | `scripts/04_limpieza.py` + `scripts/datos/{erratas,adaptaciones,particiones,descartes}_es.yaml`, `avisos_manuales.yaml` |
| F4 | `02_maestro/ids.csv` (registro uid → ID) | `scripts/04_limpieza.py`, `05_huecos.py` |
| F5 | `02_maestro/checkpoints/F5_huecos_20261015.xlsx` (+538 filas en español), `04_reportes/F5_huecos.md` | `scripts/05_huecos.py` + `scripts/plan_medico.py` + `scripts/datos/{plan_b01,respuestas_paciente,frases_portadoras,oraciones_generales}.yaml` |
| F6 | `02_maestro/corpus_maestro.xlsx` (2 254 oraciones), `F6_bloques_20261015.xlsx` | `scripts/f6_armar_bloques.py` (+ `excel_formato.py`, `docs_word.py`) |
| F6 | `03_bloques/B01…B05/BXX_traductor.docx`, `BXX_trabajo.xlsx`, `03_bloques/GUIA_GRABACION.docx` | `scripts/f6_armar_bloques.py` |
| F6 | `04_reportes/REVISION_JUAN.md` | `scripts/f6_armar_bloques.py` |
| F6 | `scripts/06_importar_traductor.py`, `07_hoja_grabacion.py`, `08_manifest.py` (+ `planilla.py`) | — |
| F6 | `04_reportes/PRUEBA_06_07_08.md` (copias en `02_maestro/checkpoints/prueba_06_08/`) | `scripts/test_ida_vuelta.py` |
| F7 | `04_reportes/VERIFICACION_F7.md`, `04_reportes/revision_visual/*.pdf, *.png` | `scripts/f7_verificacion.py`, `scripts/render_revision.py` |
| F7 | `04_reportes/ENTREGA.md` | (a mano) |

## Decisiones de esta sesión aún no pasadas a DECISIONES_TOMADAS.md

- (todas pasadas)

## Problemas abiertos / dudas para Juan

- Ninguno bloqueante. Por confirmar: «chicha punta» (B01) y el calco «no + una» en algunos ejercicios (ver ENTREGA, «Qué debes revisar»).
