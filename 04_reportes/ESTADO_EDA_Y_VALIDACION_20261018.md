# Estado del EDA y preparación de la validación

Fecha de corte: 18 de octubre de 2026 (America/Lima).

## Dictamen actual

El EDA automático tiene suficiente alcance para iniciar la validación humana. No se necesita agregar más gráficos antes del piloto. El cuello de botella actual es comprobar claridad y naturalidad del español, equivalencia y variedad del quechua chanka, y adecuación de las frases médicas.

Todavía no existe un corpus paralelo validado ni un dataset de voz terminado. El maestro contiene candidatos y borradores. Una alerta automática no confirma un error, y la ausencia de alertas tampoco confirma calidad.

## Estado cuantitativo

| Componente | Estado |
|---|---:|
| Filas del maestro | 2 254 |
| IDs duplicados en el maestro | 0 |
| Candidatos asignados a B01–B05 | 1 000 |
| Filas todavía sin bloque | 1 254 |
| Tamaño de cada bloque | 200 |
| Composición de cada bloque | 140 generales + 60 médicas |
| Quechua validado en producción | **0** |
| Split actual | Todo `train` |
| Test reservado real | No definido |
| Audios de producción aprobados | 0 |

Los 100 registros `Test_sugerido` no constituyen un conjunto de prueba mientras continúen en `train`. Las particiones definitivas deberán diseñarse después de disponer de traducciones, hablantes y sesiones reales.

## Mejoras realizadas

### 1. Auditoría independiente del proyecto

Se revisaron estructura, documentos, maestro, bloques, procedencia, scripts y archivos de prueba. Se inventariaron 173 archivos, 96 hojas Excel y 11 Word. Los Word vigentes de B01–B05 coinciden con el maestro en IDs, español y borradores.

Se identificó que `02_maestro/checkpoints/prueba_06_08/B01_grabacion.docx` es un fixture técnico con traducciones simuladas y no debe utilizarse para grabar.

Informe: [revision_independiente_20261018/REVISION_INDEPENDIENTE.md](revision_independiente_20261018/REVISION_INDEPENDIENTE.md).

### 2. EDA posterior a la selección

Se creó y ejecutó `EDA_Postseleccion_Corpus_Chanka.ipynb`. El nuevo EDA compara recopilación, limpieza, ampliación, maestro y selección; analiza cobertura de flashcards, procedencia, redundancia, roles, diálogo y estado del pareado.

Resultados principales:

- `flashcards.xlsx`: 83,48 % de cobertura de formas escritas en las 1 000 frases.
- `flashcards2.xlsx`: 17,58 %.
- 636 referencias tienen coincidencia exacta conservadora en el maestro.
- 285 formas objetivo existen en el maestro, pero no aparecen en las frases seleccionadas.
- Ninguna traducción del shiwilu de las flashcards se trató como quechua.

Archivos: [notebook](../EDA_Postseleccion_Corpus_Chanka.ipynb), [Excel automático](eda_postseleccion/EDA_POSTSELECCION.xlsx) y [resultados](eda_postseleccion/RESULTADOS.md).

### 3. Plantilla de revisión humana general

Se creó `REVISION_HUMANA.xlsx` con una muestra diagnóstica de 119 frases. Sus columnas humanas quedaron vacías: no se inventaron calificaciones, aprobaciones ni decisiones de hablantes.

Archivo: [REVISION_HUMANA.xlsx](eda_postseleccion/REVISION_HUMANA.xlsx).

### 4. Priorización de candidatos no seleccionados

Se localizaron 466 frases no seleccionadas que contienen alguna de las 285 formas disponibles. Se construyó una lista exploratoria de 30 candidatos: 21 generales y 9 médicos.

La simulación mostró que maximizar palabras puede favorecer ejercicios repetitivos: 20 de los 30 candidatos proceden de ejercicios generados y 14 contienen negación. Por ello la lista se usa para revisar, no para modificar bloques automáticamente.

Archivos: [PROPUESTA_CANDIDATOS.xlsx](eda_postseleccion/propuesta_candidatos/PROPUESTA_CANDIDATOS.xlsx) y [REVISION_CANDIDATOS.md](eda_postseleccion/propuesta_candidatos/REVISION_CANDIDATOS.md).

### 5. Evaluación de posibles intercambios

Se simularon seis intercambios dentro de B04/B05. La estructura permanecería correcta y la cobertura subiría de 954 a 963 formas objetivo, pero se perderían dos frases en pasado, una en futuro, una condicional y una imperativa, a cambio de cinco presentes adicionales.

La decisión documentada es **no aplicar todavía** esos intercambios. La diversidad gramatical y comunicativa tiene prioridad sobre una ganancia pequeña de vocabulario.

También se detectaron ocho casos donde la heurística de tiempo necesita revisión. Por ejemplo, «Esta tarde iré a recoger a los niños» aparece como pasado. Las estadísticas temporales son aproximaciones, no anotaciones lingüísticas definitivas.

Archivos: [EVALUACION_INTERCAMBIOS.xlsx](eda_postseleccion/evaluacion_intercambios/EVALUACION_INTERCAMBIOS.xlsx) y [DICTAMEN.md](eda_postseleccion/evaluacion_intercambios/DICTAMEN.md).

### 6. Piloto humano de 50 frases

Se preparó el sublote existente B01-S1 completo. Tiene 50 filas: 34 generales y 16 médicas. La diferencia respecto de 35/15 está dentro de la tolerancia del diseño del proyecto y permite conservar un sublote operativo completo. Las 16 médicas se reparten en 8 intervenciones del médico y 8 del paciente.

Se generaron dos libros:

- [PILOTO_B01_S1_REVISOR.xlsx](eda_postseleccion/piloto_validacion_50/PILOTO_B01_S1_REVISOR.xlsx): archivo que se puede enviar al revisor.
- [PILOTO_B01_S1_COORDINACION_NO_ENVIAR.xlsx](eda_postseleccion/piloto_validacion_50/PILOTO_B01_S1_COORDINACION_NO_ENVIAR.xlsx): trazabilidad interna; contiene borradores ocultos y **no debe enviarse**.

El libro del revisor contiene 19 celdas quechuas inicialmente vacías:

- 5 son controles ciegos con borrador oculto.
- 14 no tenían borrador en el maestro.

Se verificó que ningún borrador de control aparece en el libro enviable. El archivo tiene instrucciones, códigos, listas desplegables y campos para claridad, naturalidad, autonomía, facilidad de lectura, utilidad, equivalencia, chanka natural, ortografía, adecuación clínica, decisión, comentario, revisor y fecha.

## Cómo ejecutar el piloto

1. Enviar únicamente `PILOTO_B01_S1_REVISOR.xlsx` al revisor lingüístico.
2. Pedir que revise primero el español. Si propone cambiarlo, debe usar `Corregir español` y describir el cambio en `Comentario`; no debe editar silenciosamente el original.
3. Después revisar o escribir `Quechua_trabajo`. En controles ciegos no debe consultar otro borrador.
4. Para frases médicas, completar `Adecuación_clínica` solo con un revisor competente; los demás seleccionan `No aplica`.
5. La coordinación compara el archivo devuelto con `PILOTO_B01_S1_COORDINACION_NO_ENVIAR.xlsx`, resuelve desacuerdos y registra cada decisión por ID.
6. No generar hoja real de grabación hasta cerrar todas las filas del sublote con estado aprobado y texto quechua validado.
7. Después del piloto, recalcular el EDA con resultados humanos: porcentaje aprobado, tipos de corrección, alertas acertadas/fallidas, calidad por fuente y tiempo empleado.

## Controles técnicos pendientes antes de grabar

| Prioridad | Pendiente | Riesgo si no se corrige |
|---|---|---|
| Alta | Bloquear traducciones distintas con el mismo ID al importar Word | Se valida la primera aparición según el orden del documento. |
| Alta | Exigir estado aprobado además de `Quechua_validado` | Una fila que volvió a `Por_revisar` puede llegar a grabación. |
| Alta | Separar texto previsto de transcripción realmente pronunciada | El manifest puede etiquetar el audio con un texto diferente. |
| Alta | Detectar silencio, saturación y archivos truncados | Un WAV silencioso puede pasar los controles básicos. |
| Media | Versionar Word/PDF/PNG mediante SHA256 | Se pueden revisar imágenes correspondientes a una versión anterior. |
| Media | Revisar la clasificación heurística de tiempo verbal | Algunas comparaciones gramaticales contienen etiquetas incorrectas. |
| Media | Definir `dev` y `test` reales | No existe evaluación independiente del entrenamiento. |

Estos problemas están reproducidos y documentados. No se corrigieron dentro del pipeline de producción durante el trabajo del EDA para evitar modificar el flujo sin una revisión específica.

## Estado por fase

| Fase | Estado actual | Siguiente condición |
|---|---|---|
| Recopilación y trazabilidad | Completada para el material actual | Incorporar nuevas fuentes solo con procedencia y versión. |
| Limpieza automática y EDA | Completada, con limitaciones documentadas | Recalcular después del piloto. |
| Selección de 1 000 candidatos | Preparada | No cambiar por cobertura léxica sin revisión humana. |
| Revisión humana del español | **Pendiente** | Completar piloto B01-S1. |
| Traducción/validación chanka | **Pendiente** | Traductor competente y conciliación por ID. |
| Revisión clínica | **Pendiente** | Profesional competente para las frases médicas. |
| Grabación | **No procede todavía** | Textos aprobados y controles técnicos corregidos. |
| Transcripción de audio | No iniciada | Registrar lo pronunciado por toma. |
| Split train/dev/test | No definido | Definir tarea, hablantes, sesiones y familias de frases. |
| Dataset final | No disponible | Requiere texto validado, audio, transcripción y manifest revisado. |

## Qué archivo es cada cosa

- Maestro vigente: `02_maestro/corpus_maestro.xlsx`.
- Notebook principal nuevo: `EDA_Postseleccion_Corpus_Chanka.ipynb`.
- Informe automático del EDA: `04_reportes/eda_postseleccion/EDA_POSTSELECCION.xlsx`.
- Plantilla diagnóstica amplia: `04_reportes/eda_postseleccion/REVISION_HUMANA.xlsx`.
- Piloto que se envía: `04_reportes/eda_postseleccion/piloto_validacion_50/PILOTO_B01_S1_REVISOR.xlsx`.
- Libro interno que no se envía: `04_reportes/eda_postseleccion/piloto_validacion_50/PILOTO_B01_S1_COORDINACION_NO_ENVIAR.xlsx`.

## Integridad

El maestro conserva SHA256 `ca52cc9383e92560a5c95f48b532340c2645ed10977e2df6d4ff7689e8bcac02`. Los análisis y simulaciones se escribieron en `04_reportes`; no se aplicaron intercambios ni validaciones al corpus. Las fuentes, bloques y documentos originales no fueron modificados por la preparación del piloto.

## Próximo hito

El siguiente hito ya no es producir otra gráfica: es recibir el `PILOTO_B01_S1_REVISOR.xlsx` completado, conciliar las 50 decisiones y medir el resultado. Con esa evidencia se decidirá si se mantienen los borradores, qué fuentes requieren más revisión y qué frases conviene reemplazar antes de trabajar los otros sublotes.
