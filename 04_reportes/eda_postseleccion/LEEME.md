# Cómo trabajar con este EDA

1. Abrir `../../EDA_Postseleccion_Corpus_Chanka.ipynb` en VS Code o Jupyter y seleccionar un entorno Python con pandas, numpy, matplotlib, openpyxl e IPython.
2. Ejecutar las celdas desde el inicio. El notebook detecta el proyecto y las flashcards del workspace. Si se trasladan a otra ubicación, configurar `FLASHCARDS_DIR` en la primera celda.
3. Leer `RESULTADOS.md` y `EDA_POSTSELECCION.xlsx`. Las hojas `Cobertura_por_archivo`, `Palabras_objetivo`, `Candidatos_referencia` y `Revision_seleccion` ayudan a decidir qué revisar.
4. Completar únicamente `REVISION_HUMANA.xlsx` con las anotaciones del traductor o revisor. El informe automático se sobrescribe; la plantilla humana existente se conserva.
5. Cerrar Excel antes de ejecutar otra vez para evitar bloqueos del archivo. Si cambia el maestro, conciliar la plantilla humana por ID, texto y huella; no copiar decisiones solo porque coincide el ID.

La plantilla contiene 119 filas en la primera ejecución; el tamaño se recalcula según los estratos del corpus. Es una muestra diagnóstica, no una estimación representativa de la tasa global de error.

Para las columnas de evaluación usar `Sí`, `No`, `Dudoso` o `No aplica`. Aclarar en `Comentario` los cambios necesarios. `Equivalencia_par` solo se evalúa con una traducción disponible y un revisor competente; dejar `No aplica` si falta. `Adecuacion_clinica` necesita revisión pertinente al dominio. Registrar `Revisor` y `Fecha`. Las decisiones sugeridas son `Conservar`, `Revisar español`, `Traducir`, `Revisar quechua` o `Posponer`; ninguna se importa automáticamente al maestro.

Las traducciones shiwilu de las flashcards no se incorporan. Los candidatos recuperados conservan el español y quechua originales del maestro. Si se adapta el español, se necesita revisar o rehacer su traducción.

La cobertura combinada está muy influida por flashcards2.xlsx, que es mucho mayor. Comparar ambos archivos por separado. No confundir cobertura de formas escritas con calidad, naturalidad, cobertura conceptual o morfológica.

## Ejecución alternativa

Desde la raíz de Corpus_Quechua:

```powershell
python scripts/ejecutar_eda_postseleccion.py
```

Este ejecutor procesa las celdas Python en orden y guarda tablas, texto y figuras dentro del notebook. No usa un kernel Jupyter, magics ni herramientas externas; las 12 celdas del notebook son Python ordinario. La ejecución inicial se verificó de esta manera.

`scripts/crear_eda_postseleccion.py` reconstruye el notebook desde la plantilla de código. **Sobrescribe el notebook y sus salidas**; usarlo solo para regenerar la plantilla, no para una ejecución cotidiana ni después de editar manualmente sus celdas sin conservar una copia.

## Alcance y pendientes

Se incorporaron comparaciones entre etapas, cobertura del español de las flashcards, recuperación de pares, señales editoriales, alertas con denominadores, redundancia, diversidad por bloque, pares de diálogo y muestra humana. Las entradas se comprueban con SHA256 y no se modifican.

No se ejecuta nuevamente el pipeline F0–F7, no se corrigen sus defectos de importación en este trabajo y no se generan traducciones quechuas. Quedan pendientes la validación humana, análisis morfológico adjudicado, agrupaciones semánticas revisadas, particiones definitivas y evaluación de audio/transcripción cuando estén disponibles.
