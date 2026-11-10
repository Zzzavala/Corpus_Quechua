# PROGRESO — Corpus quechua collao médico

> Archivo de estado (CLAUDE.md §14.1). Si la sesión se corta: leer CLAUDE.md (`Estrategia/CLAUDE.md`, **empezando por la sección 0: cambio a collao**), luego este archivo, y continuar desde **Siguiente paso**.
> Comando base: `.\.venv\Scripts\python.exe scripts\<script>.py --forzar` desde `D:\Corpus_Quechua`. Nada usa la GPU.
> Orden de la cadena: 00_huella_fuentes → 01_inventario → 02_ingesta → 03_eda → 04_limpieza → 05_huecos → f6_armar_bloques → f7_verificacion.
> Scripts de operación (§8.5–8.7): 06_importar_traductor, 07_hoja_grabacion, 08_manifest.

## Estado (5-nov-2026): B01 con el traductor; B02–B05 listos en collao

- **Hecho:**
  - **P3 decidido: 5 vocales**, en todos los bloques.
  - **B01 pasado a collao** (`scripts/congelar_bloque.py`, detalle en `B01_COLLAO.md`): filas 1–24 del traductor intactas; desde la 25, borrador collao (7) o vacía (169). «Soy de Cusco.» y otras 3 frases cambiadas (filas 104, 152 y 183). Sin control. Marcado `Enviado` en el maestro.
  - **B02–B05 rearmados en collao**, sin repetir el español de B01.
  - Fuentes descargadas a `Fuentes/collao/` y `Fuentes/AmericasNLP/es-quz/`; Palabras clave, justicia y PIAS integrados (calidad 1); glosario COVID en léxico y texto paralelo; señalética descartada; léxico collao de ~39 000 palabras.
  - `06_dataset/texto_paralelo_collao.csv` (1 883 pares) para el equipo de modelo; `04_reportes/AVANCE_B01.md` con lo que comentó el traductor.
  - `ENTREGA.md`, `DECISIONES_TOMADAS.md`, `FUENTES_COLLAO.md` y CLAUDE.md §0 actualizados.
  - **Segunda revisión antes de enviar** (`SEGUNDA_REVISION.md`): se leyeron a mano las 1 000 oraciones y los borradores; 21 frases en español corregidas, 5 avisos de sentido puestos a mano, avisos falsos o ilegibles arreglados, control sin el borrador desalineado. En B01, solo 3 frases que pidió la coordinación (filas 104, 152 y 183).
- **Siguiente paso (para la coordinación del proyecto):**
  1. **10-nov-2026:** `03_bloques/B01/B01_traductor.docx` es ahora el `B01_traductor_v1_5_collao.docx` del equipo, sin cambios (190 filas, columna «Vocabulario»; título, instrucción 1 y ortografía pasados a collao; ver `ENTREGA.md`). B02–B05 traen la columna «Vocabulario» vacía. `VERIFICACION_F7.md`: 153/160, con las 7 fallas solo en B01 (no coincide con el maestro). Las 10 filas que faltan en B01 se quedan fuera (se quitaron en la grabación; decisión de la coordinación, 10-nov-2026). Las notas con fuentes de B01 se dejaron tal cual. **Por ahora se trabaja solo con los Word** (decisión de la coordinación, 10-nov-2026): el Excel de trabajo de B01, su foto congelada y el maestro de B01 no se actualizan con el v1_5; no correr `congelar_bloque.py` con él sin que lo pidan.
  2. Revisar el español de B02 en `REVISION.md` y enviar `B02_traductor.docx`; después, `06_importar_traductor.py B02 --marcar-enviado`.
  3. Cuando el traductor devuelva B01: `06_importar_traductor.py B01`.
- **Otras decisiones pendientes:** ¿un sexto bloque con las 530 frases oficiales sin bloque? (faltan ~90 generales); ¿sumar los ~480 pares de OPS/OMS Bolivia?; ¿integrar las 4 fuentes validadas en `FUENTES_COLLAO.md`, sección 4? (no cambian los bloques); guardar desde un navegador los PDF de HEARTS del MINSA.

## Fases (versión collao, desde el 5-nov-2026)

| Fase | Estado | Última salida generada |
|---|---|---|
| F0 – Preparación | hecha | 2026-11-05: `config.yaml` (variedad collao), huella de fuentes rehecha tras editar CLAUDE.md (anterior guardada) |
| F1 – Inventario | hecha | 2026-11-05 (`INVENTARIO.md`) |
| F2 – Ingesta al maestro | hecha | 2026-11-05 (`F2_ingesta_20261105.xlsx`, 2 339 registros) |
| F3 – EDA | hecha | 2026-11-05 (`EDA.md`) |
| F4 – Limpieza | hecha | 2026-11-05 (`F4_limpio_20261105.xlsx`) |
| F5 – Llenar huecos | hecha | 2026-11-05 (`F5_huecos_20261105.xlsx`) |
| F6 – Priorización y bloques | hecha | 2026-11-05 (maestro, B01–B05, `F6_bloques_20261105.xlsx`) |
| F7 – Verificación final | hecha | 2026-11-05 (`VERIFICACION_F7.md`) |

> Los checkpoints chanka (14 y 15-oct) quedan en `02_maestro/checkpoints/` como historia; los scripts leen siempre el más reciente (20261105).

## Archivos generados

| Fase | Archivo | Script |
|---|---|---|
| F0 | `04_reportes/PROGRESO.md`, `DECISIONES_TOMADAS.md`, `FUENTES_COLLAO.md` | (a mano) |
| F0 | `.venv/`, `requirements.txt`, `config.yaml` | (a mano) |
| F0 | `04_reportes/huella_fuentes_F0.json` (+ `huella_fuentes_F0_hasta_20261105.json`) | `scripts/00_huella_fuentes.py` |
| F1 | `04_reportes/INVENTARIO.md`, `inventario_cifras.json` | `scripts/01_inventario.py` |
| F1 | `02_maestro/checkpoints/cache/` (texto de PDF, `lexicos_collao.json`) | `scripts/fuentes.py`, `scripts/quechua.py` |
| F2 | `02_maestro/checkpoints/F2_ingesta_20261105.xlsx` | `scripts/02_ingesta.py` |
| F3 | `04_reportes/EDA.md`, `04_reportes/fig/`, `F3_eda_20261105.xlsx` | `scripts/03_eda.py` |
| F4 | `02_maestro/checkpoints/F4_limpio_20261105.xlsx`, `02_maestro/ids.csv` | `scripts/04_limpieza.py` + `scripts/datos/*.yaml` |
| F5 | `02_maestro/checkpoints/F5_huecos_20261105.xlsx`, `04_reportes/F5_huecos.md` | `scripts/05_huecos.py` + `scripts/plan_medico.py` |
| F6 | `02_maestro/corpus_maestro.xlsx` (2 847 oraciones), `03_bloques/B02…B05/`, `GUIA_GRABACION.docx`, `04_reportes/REVISION.md`, `F6_bloques_20261105.xlsx` | `scripts/f6_armar_bloques.py` |
| Congelar | `02_maestro/congelados/B01.xlsx`, `B01_original/`, `03_bloques/B01/B01_traductor.docx`, `04_reportes/B01_COLLAO.md` | `scripts/congelar_bloque.py` |
| Avance | `04_reportes/AVANCE_B01.md` | `scripts/avance_traductor.py` |
| Modelo | `06_dataset/texto_paralelo_collao.csv` | `scripts/09_texto_paralelo.py` |
| F6 | `04_reportes/PRUEBA_06_07_08.md` | `scripts/test_ida_vuelta.py` |
| F7 | `04_reportes/VERIFICACION_F7.md`, `04_reportes/revision_visual/` | `scripts/f7_verificacion.py` |
| F7 | `04_reportes/ENTREGA.md` | (a mano) |

## Decisiones de esta sesión aún no pasadas a DECISIONES_TOMADAS.md

- (todas pasadas)

## Problemas abiertos / dudas para la coordinación del proyecto

- ¿Sumar los ~480 pares de OPS/OMS Bolivia que el unificado no tomó?
- Cusco y Puno se combinan por ahora: lo confirma el traductor.
- Por confirmar (como antes): el calco «no + una».
