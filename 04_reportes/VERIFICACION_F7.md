# Verificación final (F7) — checklist de CLAUDE.md §13

Generado por `scripts/f7_verificacion.py`. **153 de 160 puntos PASAN.**

| Sección | Punto | Resultado | Detalle |
|---|---|---|---|
| Progreso | PROGRESO.md con las fases F0–F7 en «hecha» | PASA | {'F0': 'hecha', 'F1': 'hecha', 'F2': 'hecha', 'F3': 'hecha', 'F4': 'hecha', 'F5': 'hecha', 'F6': 'hecha', 'F7': 'hecha'} |
| Fuentes | Fuentes intactas (tamaño y sha256 iguales a F0) | PASA | {   "archivos": 40,   "problemas": [] } |
| Fuentes | Cifras de §5 verificadas (0 «✖ DIFIERE» en INVENTARIO.md) | PASA |  |
| Maestro | corpus_maestro.xlsx con todas sus pestañas | PASA | LEEME, Corpus, Origen, Cambios, Descartes, Lexico, QA, Bloques, Traductor_metricas |
| Maestro | IDs únicos y con formato GEN-/CLI- | PASA | (2847 filas) |
| Maestro | Toda fila de Corpus tiene su fila en Origen | PASA |  |
| Maestro | Corpus tiene las columnas de §8.2 | PASA |  |
| Maestro | Todo descarte tiene motivo | PASA | (290 descartes) |
| Maestro | Cambios registrados | PASA | (2321 cambios) |
| Maestro | Nada se borra sin rastro (cada registro de F2 está en Corpus, Léxico o Descartes) | PASA | (3553 registros; sin rastro: []) |
| Bloques | Ninguna fila repetida entre bloques | PASA | (1000 filas en 5 bloques) |
| B01 | 200 filas = 140 generales + 60 médicas | PASA | (200: 140 + 60) |
| B01 | 4 sublotes de 50 con ~35 + ~15 | PASA | B01-S1: 34+16 / B01-S2: 36+14 / B01-S3: 35+15 / B01-S4: 35+15 |
| B01 | Médico / paciente ≈ 50/50 | PASA | (32 / 28) |
| B01 | Pares pregunta–respuesta en el mismo sublote | PASA | (28 respuestas) |
| B01 | Consulta completa: las 6 etapas de §11.2 | PASA | Caracterizar el síntoma, Examen físico, Explicación, plan y cierre, Inicio, Motivo de consulta, Síntomas asociados |
| B01 | Word: A4 horizontal | PASA | (29.7 × 21.0 cm) |
| B01 | Word: instrucciones y convención ortográfica en la página 1 | PASA |  |
| B01 | Word: una tabla por sublote | PASA | (4) |
| B01 | Word: fila de encabezado repetida en cada página | PASA |  |
| B01 | Word: columnas N° | ID | Quién habla | Español | Quechua | Observaciones | Vocabulario | PASA | ['N°', 'ID', 'Quién habla', 'Español', 'Quechua (corrija o escriba aquí)', 'Observaciones', 'Vocabulario (español – quechua)'] |
| B01 | Word: mismas 200 filas y en el mismo orden (por ID) | **FALLA** | (190) |
| B01 | Word: sin información de origen ni columnas técnicas | **FALLA** | ['MINEDU', 'Fuente'] |
| B01 | Word: ninguna referencia al chanka ni a Ayacucho (título, instrucciones, ortografía, español y avisos) | PASA |  |
| B01 | Word: tabla de ortografía de 5 vocales, igual en todos los bloques | PASA |  |
| B01 | Word: las filas 1–24, ya trabajadas por el traductor, son idénticas a B01_traductor_v1.docx | **FALLA** |  |
| B01 | Word: mismos IDs y en el mismo orden que el archivo del traductor | **FALLA** |  |
| B01 | Word: filas siguientes = borrador del maestro o vacía | **FALLA** | (distintas: ['GEN-0101', 'GEN-0824', 'GEN-0175', 'CLI-0019', 'CLI-0020']) |
| B01 | Word: filas siguientes sin borradores chanka (solo de fuentes collao) | **FALLA** | (147 con borrador, 19 vacías; chanka: ['GEN-0101', 'GEN-0824', 'GEN-0175', 'CLI-0020', 'GEN-0178']) |
| B01 | Word: el español solo cambió donde se pidió | **FALLA** | ['GEN-0101', 'GEN-0824', 'GEN-0175', 'CLI-0019', 'CLI-0020', 'GEN-0178', 'GEN-0083', 'GEN-0918', 'GEN-0135', 'CLI-0025', 'CLI-0008', 'GEN-0157', 'GEN-0998', 'GEN-0173', 'CLI-0033', 'CLI-0979', 'GEN-0189', 'CLI-0035', 'CLI-0980', 'GEN-0031', 'GEN-0919', 'GEN-0116', 'GEN-0128', 'GEN-0130', 'GEN-0916', 'CLI-0029', 'GEN-0140', 'GEN-0199', 'CLI-0042', 'CLI-0981', 'GEN-0154', 'GEN-0169', 'GEN-0867', 'GEN-0043', 'GEN-0579', 'CLI-0052', 'CLI-0982', 'GEN-0917', 'GEN-0036', 'GEN-0146', 'GEN-0145', 'GEN-0868', 'CLI-0141', 'CLI-0983', 'GEN-0049', 'GEN-0208', 'GEN-0902', 'GEN-0028', 'CLI-0061', 'CLI-0984', 'GEN-0207', 'GEN-0193', 'GEN-0825', 'GEN-0040', 'CLI-0058', 'CLI-0985', 'GEN-0171', 'GEN-0534', 'GEN-1023', 'GEN-0017', 'CLI-0069', 'CLI-0986', 'GEN-0137', 'GEN-0798', 'GEN-0015', 'GEN-0190', 'GEN-0541', 'GEN-0821', 'GEN-0021', 'GEN-0185', 'CLI-0072', 'CLI-0987', 'GEN-0996', 'GEN-0536', 'GEN-0019', 'GEN-0118', 'CLI-0127', 'CLI-0988', 'GEN-0901', 'GEN-0022', 'GEN-0538', 'GEN-0125', 'CLI-0135', 'CLI-0989', 'GEN-0743', 'GEN-0038', 'GEN-0162', 'GEN-0744', 'CLI-0375', 'CLI-0990', 'GEN-0187', 'GEN-0014', 'GEN-0147', 'GEN-0947', 'CLI-0373', 'CLI-0991', 'GEN-0532', 'GEN-0094', 'GEN-0745', 'GEN-0204', 'CLI-0387', 'CLI-0992', 'GEN-0543', 'GEN-0062', 'GEN-0869', 'GEN-0198', 'CLI-0271', 'CLI-0993', 'GEN-0034', 'GEN-0142', 'GEN-0948', 'GEN-0143', 'CLI-0193', 'GEN-0075', 'GEN-0870', 'GEN-0195', 'GEN-0124', 'GEN-0866', 'GEN-0069', 'GEN-0155', 'CLI-0229', 'GEN-1021', 'GEN-0106', 'GEN-0088', 'GEN-0138', 'CLI-0352', 'CLI-0994', 'GEN-0742', 'GEN-0087', 'GEN-0148', 'GEN-0141', 'CLI-0097', 'GEN-0967', 'GEN-0086', 'GEN-0181', 'GEN-0997', 'CLI-0254', 'CLI-0995', 'CLI-0924', 'GEN-0209', 'GEN-0016', 'GEN-0160', 'GEN-0797', 'CLI-0916', 'CLI-0996', 'GEN-0136', 'GEN-0058', 'GEN-0968', 'GEN-0161', 'CLI-0153', 'CLI-0997', 'GEN-0120', 'GEN-0066', 'GEN-0746', 'GEN-0167', 'CLI-0923', 'CLI-0998', 'GEN-0105', 'GEN-0177', 'GEN-0826', 'GEN-0179', 'CLI-0999', 'CLI-1000', 'GEN-0060', 'GEN-0969', 'GEN-0114'] |
| B01 | Excel de trabajo: pestañas Bloque / Detalle / Resumen (Bloque activa) | PASA | ['Bloque', 'Detalle', 'Resumen'] |
| B01 | Excel de trabajo: columnas de §8.3 | PASA | ['N°', 'ID', 'Sublote', 'Dominio', 'Rol', 'Español', 'Quechua', 'Estado', 'Grabado_ES', 'Grabado_QU', 'Notas'] |
| B01 | Excel de trabajo: encabezado inmovilizado, autofiltro y lista en Estado | PASA |  |
| B01 | Excel de trabajo: solo valores (sin fórmulas) | PASA |  |
| B02 | 200 filas = 140 generales + 60 médicas | PASA | (200: 140 + 60) |
| B02 | 4 sublotes de 50 con ~35 + ~15 | PASA | B02-S1: 34+16 / B02-S2: 36+14 / B02-S3: 34+16 / B02-S4: 36+14 |
| B02 | Médico / paciente ≈ 50/50 | PASA | (30 / 30) |
| B02 | Pares pregunta–respuesta en el mismo sublote | PASA | (30 respuestas) |
| B02 | Oraciones de control (D7): 10, con borrador, repartidas en los sublotes | PASA | (10: {'Médico': 10}; sublotes 4) |
| B02 | Word: A4 horizontal | PASA | (29.7 × 21.0 cm) |
| B02 | Word: instrucciones y convención ortográfica en la página 1 | PASA |  |
| B02 | Word: una tabla por sublote | PASA | (4) |
| B02 | Word: fila de encabezado repetida en cada página | PASA |  |
| B02 | Word: columnas N° | ID | Quién habla | Español | Quechua | Observaciones | Vocabulario | PASA | ['N°', 'ID', 'Quién habla', 'Español', 'Quechua (corrija o escriba aquí)', 'Observaciones', 'Vocabulario (español – quechua)'] |
| B02 | Word: columna Vocabulario vacía en todas las filas | PASA | (200 filas) |
| B02 | Word: mismas 200 filas y en el mismo orden (por ID) | PASA | (200) |
| B02 | Word: sin información de origen ni columnas técnicas | PASA | [] |
| B02 | Word: ninguna referencia al chanka ni a Ayacucho (título, instrucciones, ortografía, español y avisos) | PASA |  |
| B02 | Word: tabla de ortografía de 5 vocales, igual en todos los bloques | PASA |  |
| B02 | Word: celda Quechua = borrador; vacía en control y en filas sin borrador | PASA | (distintas: []) |
| B02 | Word: Observaciones solo con «Aviso:» (ALTA) o vacía | PASA | (5 avisos) |
| B02 | Word: avisos legibles (sin corchetes ni «y otros») | PASA | [] |
| B02 | Word: español sin interrogativos sin tilde | PASA | [] |
| B02 | Word: sin oraciones casi iguales dentro del bloque | PASA | [] |
| B02 | Control: ninguna fila con el borrador marcado a mano como desalineado | PASA | [] |
| B02 | Word: los avisos puestos a mano llegan al Word | PASA | [] |
| B02 | Excel de trabajo: pestañas Bloque / Detalle / Resumen (Bloque activa) | PASA | ['Bloque', 'Detalle', 'Resumen'] |
| B02 | Excel de trabajo: columnas de §8.3 | PASA | ['N°', 'ID', 'Sublote', 'Dominio', 'Rol', 'Español', 'Quechua', 'Estado', 'Grabado_ES', 'Grabado_QU', 'Notas'] |
| B02 | Excel de trabajo: encabezado inmovilizado, autofiltro y lista en Estado | PASA |  |
| B02 | Excel de trabajo: solo valores (sin fórmulas) | PASA |  |
| B03 | 200 filas = 140 generales + 60 médicas | PASA | (200: 140 + 60) |
| B03 | 4 sublotes de 50 con ~35 + ~15 | PASA | B03-S1: 34+16 / B03-S2: 36+14 / B03-S3: 35+15 / B03-S4: 35+15 |
| B03 | Médico / paciente ≈ 50/50 | PASA | (30 / 30) |
| B03 | Pares pregunta–respuesta en el mismo sublote | PASA | (24 respuestas) |
| B03 | Word: A4 horizontal | PASA | (29.7 × 21.0 cm) |
| B03 | Word: instrucciones y convención ortográfica en la página 1 | PASA |  |
| B03 | Word: una tabla por sublote | PASA | (4) |
| B03 | Word: fila de encabezado repetida en cada página | PASA |  |
| B03 | Word: columnas N° | ID | Quién habla | Español | Quechua | Observaciones | Vocabulario | PASA | ['N°', 'ID', 'Quién habla', 'Español', 'Quechua (corrija o escriba aquí)', 'Observaciones', 'Vocabulario (español – quechua)'] |
| B03 | Word: columna Vocabulario vacía en todas las filas | PASA | (200 filas) |
| B03 | Word: mismas 200 filas y en el mismo orden (por ID) | PASA | (200) |
| B03 | Word: sin información de origen ni columnas técnicas | PASA | [] |
| B03 | Word: ninguna referencia al chanka ni a Ayacucho (título, instrucciones, ortografía, español y avisos) | PASA |  |
| B03 | Word: tabla de ortografía de 5 vocales, igual en todos los bloques | PASA |  |
| B03 | Word: celda Quechua = borrador; vacía en control y en filas sin borrador | PASA | (distintas: []) |
| B03 | Word: Observaciones solo con «Aviso:» (ALTA) o vacía | PASA | (11 avisos) |
| B03 | Word: avisos legibles (sin corchetes ni «y otros») | PASA | [] |
| B03 | Word: español sin interrogativos sin tilde | PASA | [] |
| B03 | Word: sin oraciones casi iguales dentro del bloque | PASA | [] |
| B03 | Control: ninguna fila con el borrador marcado a mano como desalineado | PASA | [] |
| B03 | Word: los avisos puestos a mano llegan al Word | PASA | [] |
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
| B04 | Word: columnas N° | ID | Quién habla | Español | Quechua | Observaciones | Vocabulario | PASA | ['N°', 'ID', 'Quién habla', 'Español', 'Quechua (corrija o escriba aquí)', 'Observaciones', 'Vocabulario (español – quechua)'] |
| B04 | Word: columna Vocabulario vacía en todas las filas | PASA | (200 filas) |
| B04 | Word: mismas 200 filas y en el mismo orden (por ID) | PASA | (200) |
| B04 | Word: sin información de origen ni columnas técnicas | PASA | [] |
| B04 | Word: ninguna referencia al chanka ni a Ayacucho (título, instrucciones, ortografía, español y avisos) | PASA |  |
| B04 | Word: tabla de ortografía de 5 vocales, igual en todos los bloques | PASA |  |
| B04 | Word: celda Quechua = borrador; vacía en control y en filas sin borrador | PASA | (distintas: []) |
| B04 | Word: Observaciones solo con «Aviso:» (ALTA) o vacía | PASA | (10 avisos) |
| B04 | Word: avisos legibles (sin corchetes ni «y otros») | PASA | [] |
| B04 | Word: español sin interrogativos sin tilde | PASA | [] |
| B04 | Word: sin oraciones casi iguales dentro del bloque | PASA | [] |
| B04 | Control: ninguna fila con el borrador marcado a mano como desalineado | PASA | [] |
| B04 | Word: los avisos puestos a mano llegan al Word | PASA | [] |
| B04 | Excel de trabajo: pestañas Bloque / Detalle / Resumen (Bloque activa) | PASA | ['Bloque', 'Detalle', 'Resumen'] |
| B04 | Excel de trabajo: columnas de §8.3 | PASA | ['N°', 'ID', 'Sublote', 'Dominio', 'Rol', 'Español', 'Quechua', 'Estado', 'Grabado_ES', 'Grabado_QU', 'Notas'] |
| B04 | Excel de trabajo: encabezado inmovilizado, autofiltro y lista en Estado | PASA |  |
| B04 | Excel de trabajo: solo valores (sin fórmulas) | PASA |  |
| B05 | 200 filas = 140 generales + 60 médicas | PASA | (200: 140 + 60) |
| B05 | 4 sublotes de 50 con ~35 + ~15 | PASA | B05-S1: 34+16 / B05-S2: 35+15 / B05-S3: 35+15 / B05-S4: 36+14 |
| B05 | Médico / paciente ≈ 50/50 | PASA | (30 / 30) |
| B05 | Pares pregunta–respuesta en el mismo sublote | PASA | (28 respuestas) |
| B05 | Word: A4 horizontal | PASA | (29.7 × 21.0 cm) |
| B05 | Word: instrucciones y convención ortográfica en la página 1 | PASA |  |
| B05 | Word: una tabla por sublote | PASA | (4) |
| B05 | Word: fila de encabezado repetida en cada página | PASA |  |
| B05 | Word: columnas N° | ID | Quién habla | Español | Quechua | Observaciones | Vocabulario | PASA | ['N°', 'ID', 'Quién habla', 'Español', 'Quechua (corrija o escriba aquí)', 'Observaciones', 'Vocabulario (español – quechua)'] |
| B05 | Word: columna Vocabulario vacía en todas las filas | PASA | (200 filas) |
| B05 | Word: mismas 200 filas y en el mismo orden (por ID) | PASA | (200) |
| B05 | Word: sin información de origen ni columnas técnicas | PASA | [] |
| B05 | Word: ninguna referencia al chanka ni a Ayacucho (título, instrucciones, ortografía, español y avisos) | PASA |  |
| B05 | Word: tabla de ortografía de 5 vocales, igual en todos los bloques | PASA |  |
| B05 | Word: celda Quechua = borrador; vacía en control y en filas sin borrador | PASA | (distintas: []) |
| B05 | Word: Observaciones solo con «Aviso:» (ALTA) o vacía | PASA | (5 avisos) |
| B05 | Word: avisos legibles (sin corchetes ni «y otros») | PASA | [] |
| B05 | Word: español sin interrogativos sin tilde | PASA | [] |
| B05 | Word: sin oraciones casi iguales dentro del bloque | PASA | [] |
| B05 | Control: ninguna fila con el borrador marcado a mano como desalineado | PASA | [] |
| B05 | Word: los avisos puestos a mano llegan al Word | PASA | [] |
| B05 | Excel de trabajo: pestañas Bloque / Detalle / Resumen (Bloque activa) | PASA | ['Bloque', 'Detalle', 'Resumen'] |
| B05 | Excel de trabajo: columnas de §8.3 | PASA | ['N°', 'ID', 'Sublote', 'Dominio', 'Rol', 'Español', 'Quechua', 'Estado', 'Grabado_ES', 'Grabado_QU', 'Notas'] |
| B05 | Excel de trabajo: encabezado inmovilizado, autofiltro y lista en Estado | PASA |  |
| B05 | Excel de trabajo: solo valores (sin fórmulas) | PASA |  |
| Bloques | Ningún español repetido entre las filas de los bloques (§10.4) | PASA | (repetidos: []) |
| B01 | Parte general con varios tiempos (presente ≤ 65 %; requisito del proyecto) | PASA | presente 72 · pasado 39 · progresivo 9 · futuro 8 · imperativo 6 · condicional 6 |
| B02 | Parte general con varios tiempos (presente ≤ 65 %; requisito del proyecto) | PASA | presente 81 · pasado 28 · futuro 12 · progresivo 8 · imperativo 7 · condicional 4 |
| B03 | Parte general con varios tiempos (presente ≤ 65 %; requisito del proyecto) | PASA | presente 74 · pasado 37 · futuro 12 · progresivo 8 · imperativo 5 · condicional 4 |
| B04 | Parte general con varios tiempos (presente ≤ 65 %; requisito del proyecto) | PASA | presente 59 · pasado 32 · futuro 22 · progresivo 13 · condicional 8 · imperativo 6 |
| B05 | Parte general con varios tiempos (presente ≤ 65 %; requisito del proyecto) | PASA | presente 54 · pasado 40 · futuro 18 · progresivo 15 · condicional 7 · imperativo 6 |
| Scripts | Pruebas de la revisión automática y la limpieza (test_qa) | PASA | (0 fallas) |
| Scripts | 06, 07 y 08 probados ahora con datos simulados (ida y vuelta por ID) | PASA | (0 fallas) |
| Scripts | Existen 06_importar_traductor.py, 07_hoja_grabacion.py y 08_manifest.py | PASA |  |
| Grabación | GUIA_GRABACION.docx creada | PASA |  |
| Reportes | EDA.md con conclusiones en lenguaje simple | PASA |  |
| Reportes | DECISIONES_TOMADAS.md con los valores por defecto P1–P7 y las decisiones de cada fase | PASA |  |
| Reportes | ENTREGA.md con: listo, qué enviar a quién, qué revisar, pendientes P1–P7, cuántos bloques | PASA | [] |
| LibreOffice | B01_traductor.docx abre y se convierte a PDF | PASA | (36 páginas) |
| LibreOffice | B01_trabajo.xlsx abre y se convierte a PDF | PASA | (8 páginas) |
| LibreOffice | B02_traductor.docx abre y se convierte a PDF | PASA | (13 páginas) |
| LibreOffice | B02_trabajo.xlsx abre y se convierte a PDF | PASA | (8 páginas) |
| LibreOffice | B03_traductor.docx abre y se convierte a PDF | PASA | (13 páginas) |
| LibreOffice | B03_trabajo.xlsx abre y se convierte a PDF | PASA | (8 páginas) |
| LibreOffice | B04_traductor.docx abre y se convierte a PDF | PASA | (13 páginas) |
| LibreOffice | B04_trabajo.xlsx abre y se convierte a PDF | PASA | (8 páginas) |
| LibreOffice | B05_traductor.docx abre y se convierte a PDF | PASA | (13 páginas) |
| LibreOffice | B05_trabajo.xlsx abre y se convierte a PDF | PASA | (8 páginas) |
| LibreOffice | GUIA_GRABACION.docx abre y se convierte a PDF | PASA | (1 páginas) |
| LibreOffice | corpus_maestro.xlsx abre y se convierte a PDF | PASA | (197 páginas) |

Las páginas convertidas por LibreOffice están en `04_reportes/revision_visual/` (PDF + PNG de la primera página de cada archivo).