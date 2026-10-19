# Revisión independiente del corpus español–quechua chanka

Fecha de revisión: 18 de octubre de 2026. Estado revisado: archivos locales, sin regenerar el pipeline ni modificar producción.

**Dictamen: conservar la estructura y el trabajo de recopilación; corregir los controles de importación y preparación de audio antes de iniciar una entrega para grabación.** Hay un corpus de candidatos bien organizado, pero todavía no un corpus paralelo validado ni un dataset de voz terminado.

## 1. Qué se comprobó y qué significa

Se inventariaron 173 archivos existentes, excluyendo `.git`, `__pycache__` y esta carpeta de revisión. Se inspeccionaron las estructuras de 96 hojas Excel y se extrajo el contenido de 11 Word. Se contrastaron las filas de los cinco Word de traducción con el maestro vigente. También se revisaron configuración, estrategia, informes previos y las rutas críticas de ingesta, normalización, selección, importación, grabación y manifest; se hicieron pruebas adversariales sobre copias.

La revisión de los PDF fuente comprueba disponibilidad, integridad y posibilidad de extracción de texto. **No constituye una lectura lingüística o clínica completa de cada página ni una certificación de cada traducción.** El análisis del código combina comprobación de sintaxis, inspección estática y los casos ejecutados que se detallan abajo; no equivale a ejecutar nuevamente F0–F7. Los informes de 123/123 y 33/33 pruebas aprobadas pertenecen a ejecuciones anteriores, no se presentan aquí como nuevas ejecuciones.

Artefactos de esta revisión:

- `AUDITORIA_CORPUS.xlsx`: bloques, procedencia, filas B02 con alertas, observaciones editoriales, documentos, diferencias, inventario y sintaxis.
- `resumen.json`, `integridad.json`: resultados reproducibles y comprobación de que los archivos inventariados no cambiaron durante la auditoría.
- `pruebas_importacion.json`: resultados completos de los casos adversariales del importador.
- `complementos.json`: paralelos, huellas históricas, PDF y comparación de versiones.
- `estado_y_fuentes.png`: estado y mezcla de fuentes de los cinco bloques.
- `texto_documentos/`: extracción del texto de todos los Word, para facilitar búsquedas y revisión.

Los scripts auxiliares están en esta misma carpeta. Sus salidas son de auditoría; **ninguno de sus archivos simulados se debe enviar al traductor, grabar ni incorporar al dataset**.

## 2. Estado real del corpus

| Medida | Resultado |
|---|---:|
| Filas del maestro `Corpus` | 2 254 |
| Filas de `Origen` | 2 254 |
| IDs duplicados en `Corpus` | 0 |
| Candidatos asignados a bloques | 1 000 |
| Filas sin bloque | 1 254 |
| Quechua validado no vacío | **0** |
| Estado `Borrador` | 1 318 |
| Estado `Por_revisar` | 647 |
| Estado `Sin borrador` | 289 |
| Split `train` | 2 254 |

| Bloque | General / médico | Sin texto de borrador | Estado Por_revisar | Español redactado por Claude, ambos dominios |
|---|---:|---:|---:|---:|
| B01 | 140 / 60 | 67 | 72 | 63 |
| B02 | 140 / 60 | 75 | 77 | 70 |
| B03 | 140 / 60 | 107 | 109 | 101 |
| B04 | 140 / 60 | 137 | 144 | 135 |
| B05 | 140 / 60 | 144 | 136 | 135 |

“Sin texto de borrador” y “Estado Sin borrador” son medidas distintas: muchas frases nuevas carecen de quechua, pero están en `Por_revisar`. Las categorías no deben sumarse como si fueran excluyentes.

Los cinco Word vigentes coinciden con el maestro en los IDs esperados, el español y el borrador quechua mostrado —respetando los controles ocultos—. Las copias de B01/B02 en la raíz son idénticas, byte por byte, a las de `03_bloques`. Mantener una única ubicación de entrega evitaría futuras divergencias.

## 3. Hallazgos que conviene resolver primero

### R01 — Prioridad alta: el B01 de grabación señalado es una prueba simulada

Archivo: `02_maestro/checkpoints/prueba_06_08/B01_grabacion.docx`.

Contiene 200 IDs, **66 apariciones de traducciones ficticias de la forma “Rimay número” y tres marcas `FALTA VALIDAR`**. El script `test_ida_vuelta.py` y el informe `PRUEBA_06_07_08.md` explican que se generó para probar el flujo. Por ejemplo, CLI-0745 muestra “Buenos días.” con “Rimay 1.”.

El problema no es usar datos simulados en pruebas; es que el título y la apariencia del Word permiten confundirlos con una hoja lista para grabar. Además, los IDs de un checkpoint no deben interpretarse contra cualquier versión posterior del maestro.

**Cambio recomendado:** generar los fixtures bajo un directorio inequívoco de pruebas y añadir “PRUEBA SIMULADA — NO GRABAR” en título y encabezados. La hoja real debe salir del maestro de producción después de validar el bloque. No copiar el quechua de este checkpoint al maestro.

### R02 — Prioridad alta: una fila que vuelve a revisión puede pasar a grabación

Evidencia: `scripts/06_importar_traductor.py:294–301`, `scripts/07_hoja_grabacion.py:45`, `scripts/08_manifest.py:85`.

Caso reproducido sobre copia: una fila previamente validada recibe una propuesta de cambio del español. El importador cambia su estado a `Por_revisar`, pero conserva `Quechua_validado`. El generador de grabación comprueba únicamente que ese campo tenga contenido; por tanto genera la hoja sin `--permitir-faltantes` y devuelve código 0.

No se observó esta inconsistencia en el maestro actual —no tiene validaciones—; es un fallo comprobado de una transición futura. Conservar la traducción anterior como historial puede ser correcto, **habilitar su grabación mientras la revisión está abierta no lo es**.

**Cambio recomendado:** una función compartida de elegibilidad que exija estado aprobado, texto validado y correspondencia con la versión vigente del español. Conservar la validación anterior en historial o versionada. Aplicar el mismo criterio en hoja, manifest y exportación de entrenamiento. Añadir una prueba de regresión para esta transición.

### R03 — Prioridad alta: IDs duplicados con traducciones distintas se aceptan

Evidencia: `scripts/06_importar_traductor.py:195–201` y `256–265`.

Caso reproducido: un Word incluye dos filas del mismo ID con traducciones diferentes. El script informa el duplicado, selecciona la primera aparición y la deja `Validado`. El resultado depende del orden del documento.

**Cambio recomendado:** poner en conflicto ese ID y no validar ninguna alternativa hasta resolverlo. Se pueden seguir procesando los demás IDs válidos. Registrar ambas propuestas y su posición. Una advertencia posterior no sustituye el bloqueo de la fila ambigua.

### R04 — Prioridad alta: `qa_audio = OK` solo acredita controles básicos

Evidencia: `scripts/08_manifest.py:25–46`. Se leen frecuencia, canales, bits y número de frames, pero no las muestras de audio.

Caso reproducido: WAV PCM mono, 16 kHz, 16 bits, dos segundos, todas las muestras a cero. `revisar_wav` devuelve duración 2.0 y ninguna alerta. Eso permitiría un `OK` si los demás requisitos del manifest estuvieran satisfechos.

**Cambio recomendado:** separar `qa_formato`, `qa_senal`, `revision_escucha` y `transcripcion_revisada`. Detectar silencio total, archivo truncado, saturación y duraciones sospechosas. Las medidas acústicas tampoco demuestran que se pronunció el texto correcto: hace falta revisión de escucha/transcripción. No interpretar `OK` como validación lingüística.

### R05 — Prioridad alta antes de entrenar: la transcripción real no llega al manifest

La guía y `07_hoja_grabacion.py:60` dicen que se anote lo que efectivamente dijo el hablante. Sin embargo, `08_manifest.py:83–84` exporta `Español` y `Quechua_validado` del maestro; no importa las notas ni una transcripción por toma.

**Cambio recomendado:** separar texto previsto de texto pronunciado. Añadir una tabla de grabaciones con `utterance_id`, `ID_texto`, `version_texto`, `speaker_id`, `session_id`, `take_id`, idioma, ruta, transcripción literal y estado de revisión. Conservar las dos versiones. Para ASR, la etiqueta debe representar lo pronunciado; para traducción de voz, comprobar además que el texto de destino corresponde al contenido del audio.

Los nombres `{ID}_es.wav` y `{ID}_qu.wav` funcionan para una única toma por idioma; no modelan adecuadamente varios hablantes o regrabaciones. El manifest actual elige el primer archivo cuando encuentra nombres repetidos y avisa: conviene seleccionar explícitamente la toma aprobada.

### R06 — Prioridad media: PNG de revisión visual desactualizados

En `04_reportes/revision_visual/B02_traductor_p02.png`, la primera fila es GEN-0079 (“Tengo horror a las corrientes de aire”). El Word vigente y el PDF vigente empiezan por GEN-0206 (“Voy a escribir tu historia”). El PNG de página 6 también representa una versión anterior.

La comparación adicional encontró que **los PDFs vigentes de B01–B05 sí tienen los mismos 200 IDs en el mismo orden que sus Word**. Esto no prueba por sí solo igualdad de todo el texto de cada PDF, pero permite localizar el problema observado en los PNG antiguos. La página casi vacía del PNG antiguo no se atribuye al Word actual.

**Cambio recomendado:** asociar cada PDF/PNG al SHA256 de su DOCX, y regenerar todas las vistas de una entrega juntas. Se dejaron nuevas imágenes de las páginas 2 y 6 del PDF actual en esta carpeta para mostrar la diferencia.

## 4. Observaciones metodológicas de NLP

### M01 — Mantener la distinción entre fuente, borrador y validación

El proyecto ya distingue traducción automática, normalización de otra variedad, español nuevo y validación humana. Es una decisión importante que debe conservarse. Una etiqueta `quy`, el cumplimiento de un alfabeto o una sustitución de letras no demuestran equivalencia semántica ni procedencia chanka.

El verificador de procedencia de Grupo 2 toma la máxima similitud de **cualquiera de los dos lados** con textos de referencia (`02_ingesta.py:143–150`). Para SOCEMURP también hay una coincidencia por español **o** quechua (`:71–72`). Eso aporta evidencia de una coincidencia textual, pero no verifica el par bilingüe completo.

Recomendación: usar campos separados `coincidencia_es`, `coincidencia_qu`, `par_localizado`, `referencia_pagina_linea` y `validacion_semantica`. Evitar que “Origen_verificado = Sí” se lea como “traducción correcta”. Una frase de fuente oficial también necesita comprobarse en su contexto y en el par recuperado.

### M02 — Normalización y deduplicación no deben borrar distinciones

`comun.clave_normalizada` elimina tildes y puntuación; `04_limpieza.py:287–295` usa esa clave para el descarte llamado “duplicado exacto”. Se comprobó que “¿Tiene fiebre?” y “Tiene fiebre.” colisionan, así como “Sí” y “Si”. Son contraejemplos del método; no se afirma que esos pares concretos hayan sido descartados del corpus actual.

Recomendación: clave conservadora para eliminar duplicados y clave flexible solo para proponer candidatos a revisión. Preservar signos interrogativos, tildes distintivas, números, negación, persona y modalidad. Guardar variantes con su relación en lugar de eliminarlas por similitud superficial.

La normalización ortográfica de borradores de otras variedades debe conservar el original y sus reglas aplicadas, como ya empieza a hacer `Cambios`; no se debe elevar automáticamente a adaptación lingüística validada.

### M03 — La cobertura morfológica actual es una aproximación

`quechua.segmentar` elimina sufijos desde el final mediante reglas y un léxico; no es un analizador morfológico validado. `unidades_cobertura` cuenta sufijos, palabras y bigramas de letras de borradores. Sus resultados pueden priorizar variedad escrita, pero también premiar errores del borrador.

Recomendación: rotular las figuras como **“cobertura estimada en borradores”**, recalcular después de la traducción y revisar una muestra con el traductor. Añadir una matriz de objetivos comunicativos: persona, número, tiempo/aspecto, negación, pregunta, evidencia, posesión y subordinación; admitir múltiples rasgos por oración. No forzar una correspondencia uno a uno entre una forma española y un sufijo quechua.

Los bigramas de letras no constituyen cobertura fonética. Para planificar voz, elaborar con un especialista un inventario de sonidos/contextos pertinentes y medir también diversidad de hablantes y condiciones de grabación. No usar un gráfico ortográfico como prueba de cobertura acústica.

### M04 — El 70/30 es una decisión de diseño, no una proporción demostrada

Mantener el acuerdo de 140 generales y 60 médicas por bloque mientras se evalúa el piloto. La referencia de Chu et al. estudia adaptación de dominio y mezcla de datos; sus experimentos son chino–inglés y chino–japonés. **No demuestra que 70/30 sea óptimo para este corpus, quechua chanka o reconocimiento de voz.** La frase de `Estrategia/CLAUDE.md:708` que presenta el artículo como respaldo de esa proporción debe matizarse. [Artículo original, ACL 2017](https://aclanthology.org/P17-2061/).

En esta colección, además, la proporción de español redactado por Claude sube de 63/200 en B01 a 135/200 en B04/B05. Conservar 70/30 no mantiene constante el estilo ni la procedencia. Conviene medir naturalidad y representatividad con hablantes antes de ampliar esa parte. El material literario puede aportar variedad, pero no garantiza utilidad conversacional.

### M05 — Aún no existe una evaluación independiente

Las 100 filas `Test_sugerido = Sí` siguen dentro de `train`, por decisión documentada. No deben presentarse como test reservado. Además, `f6_armar_bloques.py:771` vuelve a asignar todo a `train`: una futura división editada a mano se perdería al regenerar.

Antes de entrenar, definir la tarea y el protocolo: para traducción, separar familias de frases/paráfrasis y pares de diálogo; para reconocimiento de voz, decidir si se medirá generalización a hablantes nuevos y separar hablantes cuando corresponda. Para traducción de voz, controlar ambas dimensiones. No asignar aleatoriamente tomas de una misma frase/persona a entrenamiento y prueba sin explicitar qué se está midiendo.

Revisar también los 1 254 candidatos no seleccionados antes de incorporarlos posteriormente a entrenamiento; excluir casi gemelas solo dentro de los bloques actuales no basta para todas las futuras ampliaciones. Mantener `dev` y `test` externos de AmericasNLP identificados, sin convertirlos en nuevas frases de entrenamiento si se pretende evaluar sobre ellos. El recurso original define una tarea de traducción para lenguas indígenas, no valida automáticamente la calidad de cada adaptación de este proyecto. [Descripción del shared task, AmericasNLP 2021](https://aclanthology.org/2021.americasnlp-1.23/).

### M06 — Las métricas de edición son indicadores, no mediciones de calidad

Una distancia pequeña al borrador puede significar que estaba bien, revisión superficial o una preferencia estilística; una distancia grande puede ser una buena corrección. El código selecciona controles médicos con restricciones de calidad (`f6_armar_bloques.py:256–257`), por lo que los grupos no son directamente equivalentes.

Mantener el diagnóstico de posible anclaje como exploratorio. Para estudiar si conviene mostrar borradores, comparar grupos equilibrados, registrar tiempo real de trabajo, corrección semántica y acuerdo entre revisores. El umbral de “más de 50 % reescrito” por sí solo no demuestra que se pierda tiempo. No exigir que se cambie una traducción correcta para demostrar que fue revisada.

## 5. Revisión específica del B02 vigente

**Sirve como documento de trabajo para el traductor; no como hoja de grabación aprobada.** Tiene 200 filas (140 generales y 60 médicas), 75 celdas sin borrador y 77 registros en `Por_revisar`. Las celdas vacías corresponden a trabajo pendiente, no a un error de exportación. El maestro no registra aún que el bloque haya sido enviado.

Son aciertos los IDs, el rol médico/paciente, el espacio para observaciones y la vinculación de respuestas. Recomendaciones concretas:

| ID vigente | Texto o situación | Observación y acción |
|---|---|---|
| GEN-0011 | “Los adultos me desanimaron de ser pintor…” | Oración larga con varias subordinadas; revisar facilidad de lectura y utilidad. Si se adapta, retraducir la nueva versión. |
| GEN-0533 | “Mi lengua vive en mi cabeza.” | Aclarar si se quiere una metáfora o habla cotidiana; la brevedad no asegura naturalidad. |
| GEN-0030 | “¿Dónde quieres llevarte mi cordero?” | Puede conservarse como literatura; decidir si corresponde al español conversacional buscado. |
| GEN-0056 | “Hay que esperar.” | QA ya advierte repetición en el borrador. Resolver sentido/modalidad, sin aceptar por apariencia ortográfica. |
| CLI-0364 | “¿Te sacude el cuerpo?” | Revisar naturalidad e intención con hablante y profesional sanitario. |
| CLI-0287 | “¿Después del nacimiento lo hospitalizaron?…” | QA ya registra posible discrepancia con “al enfermarse”. Mantener contexto pediátrico y resolver el par. |
| CLI-0624 → CLI-1140 | “Ahora que tiene diarrea, dele líquidos.” → respuesta sobre mate | Necesita revisión clínica y de equivalencia; este informe no aprueba una recomendación médica ni propone tratamiento. |

También conviene identificar el interlocutor cuidador en preguntas sobre niños, distinguir cambios de escenario de una consulta continua y acordar el uso de tú/usted. No convertir las 60 frases médicas en una historia clínica única si cambian paciente, edad o situación. El diálogo y el contexto deben acompañar al ID aunque no se lean dentro del audio.

El documento puede añadir versión de entrega, identificación del revisor, fecha de revisión y una forma explícita de indicar “aprobado sin cambios” o “requiere contexto”. El comentario libre por sí solo no define el estado de aprobación.

## 6. Revisión de los paralelos y fuentes

Los pares examinados tienen iguales cantidades de líneas por lado: train/JW300 125 008, dev 996, dict 9 643, Dict_misc 9 000 y MINEDU 643. **Hay líneas vacías**: train tiene 1 978 en español y 1 966 en quechua; dev y dict tienen dos vacías en español. No se deben borrar vacíos de cada idioma de forma independiente: se perdería la alineación por posición. Crear primero `(fuente, línea_original, es, qu)` y filtrar el par completo.

`test.es` tiene 1 003 líneas y no tiene pareja quechua local. Debe permanecer como monolingüe. Tampoco se deben sumar train y la copia JW300 como dos fuentes independientes sin comprobar duplicación.

De las 31 entradas de la huella histórica, 15 coinciden en bytes y 16 coinciden al normalizar CRLF a LF. **No se encontró evidencia de alteración del contenido en esa comparación**; las diferencias observadas son de finales de línea. Mantener huella binaria y, para texto, una huella canónica documentada evita falsos avisos entre sistemas operativos.

El PDF SOCEMURP tiene 78 páginas sin texto extraíble. No se puede certificar procedencia contra ese PDF con una búsqueda textual vacía: necesita OCR y comprobación visual de las páginas utilizadas. El resto de PDF también puede tener páginas sin texto; véase `complementos.json`.

La caché de extracción de PDF se invalida solo por tamaño de archivo (`fuentes.py:217–220`). Dos versiones con igual tamaño podrían reutilizar texto anterior. Recomendación: usar SHA256 de la fuente y versión del extractor como clave. Aplicar el mismo principio a checkpoints y parámetros.

## 7. Qué agregaría al EDA y en qué orden

1. **Embudo de preparación:** recopilado → español revisado → traducción validada → audio grabado → transcripción cotejada → exportable. Hoy solo puede completarse la primera parte; mostrar ceros reales después, no estimaciones como resultados.
2. **Fuente × bloque × estado:** ya se entrega un gráfico de estado y fuentes. Añadir una vista que separe textos humanos, traducción automática, normalización y español generado.
3. **Alertas por fuente con denominador:** cuántas filas se revisaron y cuántas recibieron alerta. No confundir número de alertas con número de filas ni con errores confirmados.
4. **Diversidad y ganancia acumulada:** longitud, vocabulario nuevo y objetivos comunicativos añadidos por bloque, comparando contra todo lo ya seleccionado. Separar palabras de español y quechua; la cobertura de una no demuestra la otra.
5. **Redundancia y evaluación:** grupos de paráfrasis, pares de diálogo, coincidencias entre futuras particiones y cambios de procedencia.
6. **Después del piloto:** duración real, silencios, saturación, tomas rechazadas, hablantes, horas efectivas por idioma y discrepancias audio–texto.

No es necesario rehacer toda la recopilación ni ejecutar todo el notebook para obtener estas vistas. Leer el maestro y sus tablas de procedencia ofrece una base estable; una regeneración completa debe hacerse después de corregir los fallos y verificar la conservación de validaciones, IDs, splits y entregas enviadas.

## 8. Plan de avance y archivos de referencia

1. Conservar una instantánea del maestro y de B01/B02 con sus huellas. Separar claramente pruebas y entregas.
2. Corregir R02/R03 y añadir sus pruebas de regresión; reforzar R04/R05 antes de aceptar audios.
3. Revisar el español de un sublote de 50 filas con el traductor; resolver alertas y contexto clínico. Registrar decisiones por ID.
4. Validar el quechua de ese piloto, incluyendo aprobación sin cambios cuando proceda. Una segunda revisión de casos dudosos permite calibrar las heurísticas.
5. Generar su hoja real y grabar el piloto con identificación de hablante, sesión y toma. Cotejar lo pronunciado.
6. Revisar los resultados del piloto antes de ampliar a las 1 000 filas. Mantener la cuota acordada y ajustar dentro de ella naturalidad, fuentes y cobertura según evidencia.
7. Definir particiones y exportar únicamente ejemplos elegibles, con versión reproducible y control de contaminación.

**Excel maestro vigente:** `02_maestro/corpus_maestro.xlsx`. **Excel operativo de B02:** `03_bloques/B02/B02_trabajo.xlsx`. **Excel de esta revisión:** `04_reportes/revision_independiente_20261018/AUDITORIA_CORPUS.xlsx`.

El Excel de auditoría no sustituye al maestro y contiene duplicación intencional de IDs en `B02_revision` cuando una frase tiene varias alertas. Un dataset final de voz requerirá además los audios, la tabla de tomas y el manifest revisado: no se reduce a un único Excel.

## 9. Cambios realizados en esta revisión

Solo se añadieron informes, scripts auxiliares, extracciones, un gráfico y casos simulados dentro de `revision_independiente_20261018/`. No se cambiaron fuentes, maestros, Word, bloques ni scripts de producción. Las correcciones enumeradas arriba son propuestas pendientes, no se presentan como implementadas.

Los dos defectos de importación se reprodujeron con RapidFuzz 3.14.6 instalado de forma aislada para la auditoría. Esto comprueba los comportamientos descritos en ese entorno; no certifica toda la matriz de versiones de `requirements.txt`. La prueba de audio usa el código original y un WAV de silencio generado expresamente.
