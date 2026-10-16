# Verificación final (F7) — checklist de CLAUDE.md §13

Generado por `scripts/f7_verificacion.py`. **123 de 123 puntos PASAN.**

| Sección | Punto | Resultado | Detalle |
|---|---|---|---|
| Progreso | PROGRESO.md con las fases F0–F7 en «hecha» | PASA | {'F0': 'hecha', 'F1': 'hecha', 'F2': 'hecha', 'F3': 'hecha', 'F4': 'hecha', 'F5': 'hecha', 'F6': 'hecha', 'F7': 'hecha'} |
| Fuentes | Fuentes intactas (tamaño y sha256 iguales a F0) | PASA | {   "archivos": 31,   "problemas": [] } |
| Fuentes | Cifras de §5 verificadas (0 «✖ DIFIERE» en INVENTARIO.md) | PASA |  |
| Maestro | corpus_maestro.xlsx con todas sus pestañas | PASA | LEEME, Corpus, Origen, Cambios, Descartes, Lexico, QA, Bloques, Traductor_metricas |
| Maestro | IDs únicos y con formato GEN-/CLI- | PASA | (2254 filas) |
| Maestro | Toda fila de Corpus tiene su fila en Origen | PASA |  |
| Maestro | Corpus tiene las columnas de §8.2 | PASA |  |
| Maestro | Todo descarte tiene motivo | PASA | (92 descartes) |
| Maestro | Cambios registrados | PASA | (933 cambios) |
| Maestro | Nada se borra sin rastro (cada registro de F2 está en Corpus, Léxico o Descartes) | PASA | (2314 registros; sin rastro: []) |
| Bloques | Ninguna fila repetida entre bloques | PASA | (1000 filas en 5 bloques) |
| B01 | 200 filas = 140 generales + 60 médicas | PASA | (200: 140 + 60) |
| B01 | 4 sublotes de 50 con ~35 + ~15 | PASA | B01-S1: 34+16 / B01-S2: 36+14 / B01-S3: 35+15 / B01-S4: 35+15 |
| B01 | Médico / paciente ≈ 50/50 | PASA | (32 / 28) |
| B01 | Pares pregunta–respuesta en el mismo sublote | PASA | (28 respuestas) |
| B01 | Consulta completa: las 6 etapas de §11.2 | PASA | Caracterizar el síntoma, Examen físico, Explicación, plan y cierre, Inicio, Motivo de consulta, Síntomas asociados |
| B01 | ~15 oraciones de control (10 generales + 5 médicas), en los 4 sublotes | PASA | (15: {'General': 10, 'Médico': 5}) |
| B01 | Word: A4 horizontal | PASA | (29.7 × 21.0 cm) |
| B01 | Word: instrucciones y convención ortográfica en la página 1 | PASA |  |
| B01 | Word: una tabla por sublote | PASA | (4) |
| B01 | Word: fila de encabezado repetida en cada página | PASA |  |
| B01 | Word: columnas N° | ID | Quién habla | Español | Quechua | Observaciones | PASA | ['N°', 'ID', 'Quién habla', 'Español', 'Quechua (corrija o escriba aquí)', 'Observaciones'] |
| B01 | Word: mismas 200 filas y en el mismo orden (por ID) | PASA | (200) |
| B01 | Word: sin información de origen ni columnas técnicas | PASA | [] |
| B01 | Word: celda Quechua = borrador; vacía en control y en filas sin borrador | PASA | (distintas: []) |
| B01 | Word: Observaciones solo con «Aviso:» (ALTA) o vacía | PASA | (7 avisos) |
| B01 | Excel de trabajo: pestañas Bloque / Detalle / Resumen (Bloque activa) | PASA | ['Bloque', 'Detalle', 'Resumen'] |
| B01 | Excel de trabajo: columnas de §8.3 | PASA | ['N°', 'ID', 'Sublote', 'Dominio', 'Rol', 'Español', 'Quechua', 'Estado', 'Grabado_ES', 'Grabado_QU', 'Notas'] |
| B01 | Excel de trabajo: encabezado inmovilizado, autofiltro y lista en Estado | PASA |  |
| B01 | Excel de trabajo: solo valores (sin fórmulas) | PASA |  |
| B02 | 200 filas = 140 generales + 60 médicas | PASA | (200: 140 + 60) |
| B02 | 4 sublotes de 50 con ~35 + ~15 | PASA | B02-S1: 34+16 / B02-S2: 36+14 / B02-S3: 34+16 / B02-S4: 36+14 |
| B02 | Médico / paciente ≈ 50/50 | PASA | (30 / 30) |
| B02 | Pares pregunta–respuesta en el mismo sublote | PASA | (30 respuestas) |
| B02 | Word: A4 horizontal | PASA | (29.7 × 21.0 cm) |
| B02 | Word: instrucciones y convención ortográfica en la página 1 | PASA |  |
| B02 | Word: una tabla por sublote | PASA | (4) |
| B02 | Word: fila de encabezado repetida en cada página | PASA |  |
| B02 | Word: columnas N° | ID | Quién habla | Español | Quechua | Observaciones | PASA | ['N°', 'ID', 'Quién habla', 'Español', 'Quechua (corrija o escriba aquí)', 'Observaciones'] |
| B02 | Word: mismas 200 filas y en el mismo orden (por ID) | PASA | (200) |
| B02 | Word: sin información de origen ni columnas técnicas | PASA | [] |
| B02 | Word: celda Quechua = borrador; vacía en control y en filas sin borrador | PASA | (distintas: []) |
| B02 | Word: Observaciones solo con «Aviso:» (ALTA) o vacía | PASA | (13 avisos) |
| B02 | Excel de trabajo: pestañas Bloque / Detalle / Resumen (Bloque activa) | PASA | ['Bloque', 'Detalle', 'Resumen'] |
| B02 | Excel de trabajo: columnas de §8.3 | PASA | ['N°', 'ID', 'Sublote', 'Dominio', 'Rol', 'Español', 'Quechua', 'Estado', 'Grabado_ES', 'Grabado_QU', 'Notas'] |
| B02 | Excel de trabajo: encabezado inmovilizado, autofiltro y lista en Estado | PASA |  |
| B02 | Excel de trabajo: solo valores (sin fórmulas) | PASA |  |
| B03 | 200 filas = 140 generales + 60 médicas | PASA | (200: 140 + 60) |
| B03 | 4 sublotes de 50 con ~35 + ~15 | PASA | B03-S1: 34+16 / B03-S2: 36+14 / B03-S3: 34+16 / B03-S4: 36+14 |
| B03 | Médico / paciente ≈ 50/50 | PASA | (30 / 30) |
| B03 | Pares pregunta–respuesta en el mismo sublote | PASA | (24 respuestas) |
| B03 | Word: A4 horizontal | PASA | (29.7 × 21.0 cm) |
| B03 | Word: instrucciones y convención ortográfica en la página 1 | PASA |  |
| B03 | Word: una tabla por sublote | PASA | (4) |
| B03 | Word: fila de encabezado repetida en cada página | PASA |  |
| B03 | Word: columnas N° | ID | Quién habla | Español | Quechua | Observaciones | PASA | ['N°', 'ID', 'Quién habla', 'Español', 'Quechua (corrija o escriba aquí)', 'Observaciones'] |
| B03 | Word: mismas 200 filas y en el mismo orden (por ID) | PASA | (200) |
| B03 | Word: sin información de origen ni columnas técnicas | PASA | [] |
| B03 | Word: celda Quechua = borrador; vacía en control y en filas sin borrador | PASA | (distintas: []) |
| B03 | Word: Observaciones solo con «Aviso:» (ALTA) o vacía | PASA | (27 avisos) |
| B03 | Excel de trabajo: pestañas Bloque / Detalle / Resumen (Bloque activa) | PASA | ['Bloque', 'Detalle', 'Resumen'] |
| B03 | Excel de trabajo: columnas de §8.3 | PASA | ['N°', 'ID', 'Sublote', 'Dominio', 'Rol', 'Español', 'Quechua', 'Estado', 'Grabado_ES', 'Grabado_QU', 'Notas'] |
| B03 | Excel de trabajo: encabezado inmovilizado, autofiltro y lista en Estado | PASA |  |
| B03 | Excel de trabajo: solo valores (sin fórmulas) | PASA |  |
| B04 | 200 filas = 140 generales + 60 médicas | PASA | (200: 140 + 60) |
| B04 | 4 sublotes de 50 con ~35 + ~15 | PASA | B04-S1: 34+16 / B04-S2: 36+14 / B04-S3: 34+16 / B04-S4: 36+14 |
| B04 | Médico / paciente ≈ 50/50 | PASA | (30 / 30) |
| B04 | Pares pregunta–respuesta en el mismo sublote | PASA | (29 respuestas) |
| B04 | Word: A4 horizontal | PASA | (29.7 × 21.0 cm) |
| B04 | Word: instrucciones y convención ortográfica en la página 1 | PASA |  |
| B04 | Word: una tabla por sublote | PASA | (4) |
| B04 | Word: fila de encabezado repetida en cada página | PASA |  |
| B04 | Word: columnas N° | ID | Quién habla | Español | Quechua | Observaciones | PASA | ['N°', 'ID', 'Quién habla', 'Español', 'Quechua (corrija o escriba aquí)', 'Observaciones'] |
| B04 | Word: mismas 200 filas y en el mismo orden (por ID) | PASA | (200) |
| B04 | Word: sin información de origen ni columnas técnicas | PASA | [] |
| B04 | Word: celda Quechua = borrador; vacía en control y en filas sin borrador | PASA | (distintas: []) |
| B04 | Word: Observaciones solo con «Aviso:» (ALTA) o vacía | PASA | (3 avisos) |
| B04 | Excel de trabajo: pestañas Bloque / Detalle / Resumen (Bloque activa) | PASA | ['Bloque', 'Detalle', 'Resumen'] |
| B04 | Excel de trabajo: columnas de §8.3 | PASA | ['N°', 'ID', 'Sublote', 'Dominio', 'Rol', 'Español', 'Quechua', 'Estado', 'Grabado_ES', 'Grabado_QU', 'Notas'] |
| B04 | Excel de trabajo: encabezado inmovilizado, autofiltro y lista en Estado | PASA |  |
| B04 | Excel de trabajo: solo valores (sin fórmulas) | PASA |  |
| B05 | 200 filas = 140 generales + 60 médicas | PASA | (200: 140 + 60) |
| B05 | 4 sublotes de 50 con ~35 + ~15 | PASA | B05-S1: 35+15 / B05-S2: 35+15 / B05-S3: 34+16 / B05-S4: 36+14 |
| B05 | Médico / paciente ≈ 50/50 | PASA | (30 / 30) |
| B05 | Pares pregunta–respuesta en el mismo sublote | PASA | (28 respuestas) |
| B05 | Word: A4 horizontal | PASA | (29.7 × 21.0 cm) |
| B05 | Word: instrucciones y convención ortográfica en la página 1 | PASA |  |
| B05 | Word: una tabla por sublote | PASA | (4) |
| B05 | Word: fila de encabezado repetida en cada página | PASA |  |
| B05 | Word: columnas N° | ID | Quién habla | Español | Quechua | Observaciones | PASA | ['N°', 'ID', 'Quién habla', 'Español', 'Quechua (corrija o escriba aquí)', 'Observaciones'] |
| B05 | Word: mismas 200 filas y en el mismo orden (por ID) | PASA | (200) |
| B05 | Word: sin información de origen ni columnas técnicas | PASA | [] |
| B05 | Word: celda Quechua = borrador; vacía en control y en filas sin borrador | PASA | (distintas: []) |
| B05 | Word: Observaciones solo con «Aviso:» (ALTA) o vacía | PASA | (1 avisos) |
| B05 | Excel de trabajo: pestañas Bloque / Detalle / Resumen (Bloque activa) | PASA | ['Bloque', 'Detalle', 'Resumen'] |
| B05 | Excel de trabajo: columnas de §8.3 | PASA | ['N°', 'ID', 'Sublote', 'Dominio', 'Rol', 'Español', 'Quechua', 'Estado', 'Grabado_ES', 'Grabado_QU', 'Notas'] |
| B05 | Excel de trabajo: encabezado inmovilizado, autofiltro y lista en Estado | PASA |  |
| B05 | Excel de trabajo: solo valores (sin fórmulas) | PASA |  |
| Bloques | Ningún español repetido entre las filas de los bloques (§10.4) | PASA | (repetidos: []) |
| B01 | Parte general con varios tiempos (presente ≤ 65 %; requisito del proyecto) | PASA | presente 80 · pasado 31 · progresivo 9 · futuro 8 · imperativo 6 · condicional 6 |
| B02 | Parte general con varios tiempos (presente ≤ 65 %; requisito del proyecto) | PASA | presente 91 · pasado 17 · futuro 13 · imperativo 7 · progresivo 7 · condicional 5 |
| B03 | Parte general con varios tiempos (presente ≤ 65 %; requisito del proyecto) | PASA | presente 77 · pasado 33 · futuro 12 · progresivo 9 · imperativo 5 · condicional 4 |
| B04 | Parte general con varios tiempos (presente ≤ 65 %; requisito del proyecto) | PASA | presente 63 · pasado 29 · futuro 21 · progresivo 13 · condicional 8 · imperativo 6 |
| B05 | Parte general con varios tiempos (presente ≤ 65 %; requisito del proyecto) | PASA | presente 61 · pasado 34 · futuro 18 · progresivo 14 · condicional 7 · imperativo 6 |
| Scripts | Pruebas de la revisión automática y la limpieza (test_qa) | PASA | (0 fallas) |
| Scripts | 06, 07 y 08 probados ahora con datos simulados (ida y vuelta por ID) | PASA | (0 fallas) |
| Scripts | Existen 06_importar_traductor.py, 07_hoja_grabacion.py y 08_manifest.py | PASA |  |
| Grabación | GUIA_GRABACION.docx creada | PASA |  |
| Reportes | EDA.md con conclusiones en lenguaje simple | PASA |  |
| Reportes | DECISIONES_TOMADAS.md con los valores por defecto P1–P7 y las decisiones de cada fase | PASA |  |
| Reportes | ENTREGA.md con: listo, qué enviar a quién, qué revisar, pendientes P1–P7, cuántos bloques | PASA | [] |
| LibreOffice | B01_traductor.docx abre y se convierte a PDF | PASA | (9 páginas) |
| LibreOffice | B01_trabajo.xlsx abre y se convierte a PDF | PASA | (8 páginas) |
| LibreOffice | B02_traductor.docx abre y se convierte a PDF | PASA | (9 páginas) |
| LibreOffice | B02_trabajo.xlsx abre y se convierte a PDF | PASA | (8 páginas) |
| LibreOffice | B03_traductor.docx abre y se convierte a PDF | PASA | (9 páginas) |
| LibreOffice | B03_trabajo.xlsx abre y se convierte a PDF | PASA | (8 páginas) |
| LibreOffice | B04_traductor.docx abre y se convierte a PDF | PASA | (9 páginas) |
| LibreOffice | B04_trabajo.xlsx abre y se convierte a PDF | PASA | (8 páginas) |
| LibreOffice | B05_traductor.docx abre y se convierte a PDF | PASA | (9 páginas) |
| LibreOffice | B05_trabajo.xlsx abre y se convierte a PDF | PASA | (8 páginas) |
| LibreOffice | GUIA_GRABACION.docx abre y se convierte a PDF | PASA | (1 páginas) |
| LibreOffice | corpus_maestro.xlsx abre y se convierte a PDF | PASA | (135 páginas) |

Las páginas convertidas por LibreOffice están en `04_reportes/revision_visual/` (PDF + PNG de la primera página de cada archivo).