# Primera revisión de candidatos adicionales

Se encontraron 466 frases no seleccionadas que contienen alguna de las 285 formas objetivo disponibles. Se preparó una lista exploratoria de 30: 21 generales y 9 médicas. No se cambió ningún bloque.

## Qué revela la búsqueda

- 20 de las 30 proceden de ejercicios generados; 14 incluyen la palabra «no». Estas cantidades se solapan y no deben sumarse.
- La selección léxica recompensa formas como trabaja/trabajas/trabajamos, aunque sean de la misma familia. No se interpreta cada forma nueva como un concepto ni como un objetivo gramatical validado.
- «Ven» puede tener sentidos diferentes. Coincidir por token no demuestra que se cubra el uso buscado.
- Sólo/solo se mantiene en las cifras literales del EDA, pero no incentiva esta priorización cuando solo ya está cubierto.
- Algunas frases médicas necesitan referente, contexto o revisión especializada. No se recomiendan para grabación por su puntaje.

## Cómo leer el Excel

Abrir primero Revision_editorial_IA. Cada uno de los 30 candidatos tiene una observación y un siguiente paso. Son observaciones del asistente, no evaluaciones de un hablante chanka. Las decisiones humanas están vacías.
Propuesta_30 contiene la procedencia y los pares originales. Candidatos_disponibles permite buscar alternativas. Brechas_285 vincula cada forma con sus IDs disponibles.

## Impacto hipotético, no resultado de una nueva selección

- flashcards.xlsx: 83.48% actual → 87.74% si se añadieran las 30 frases completas.
- flashcards2.xlsx: 17.58% actual → 18.40% si se añadieran las 30 frases completas.

Esta simulación tendría 1030 frases. No mantiene el límite de 1 000 ni calcula pérdidas por reemplazos. No ejecutar esas adiciones automáticamente: primero revisar y después evaluar intercambios dentro de las cuotas y pares de diálogo.

## Método reproducible

Peso de cada forma: suma, por archivo de referencia, de log(1+frecuencia por frase única) dividido por el máximo de ese archivo. Cada archivo aporta hasta el mismo peso; flashcards2 no domina solo por su tamaño. Se selecciona por ganancia de formas todavía no cubiertas, con factor 1/(1+0.5×min(alertas altas,3)+0.25×contexto posible+0.25×varias preguntas), longitud entre 2 y 20 tokens y cuota 21/9. Estos parámetros organizan una lista de revisión; no están calibrados como probabilidades de calidad.
El puntaje usa alertas existentes: cero alertas no significa ausencia de errores. Ningún lado del par se modifica. Las huellas del maestro, EDA y revisión humana se verifican al terminar.

## Próximo paso

Revisar primero los candidatos breves y claros, resolver las observaciones contextuales y comparar las familias repetitivas con las frases ya seleccionadas. Si se cambia el español, revisar o rehacer su traducción. No buscar máxima cobertura a costa de naturalidad, variedad de situaciones o consistencia clínica.

Este Excel es una salida automática: guardar decisiones humanas en una copia antes de volver a ejecutar el script. La plantilla REVISION_HUMANA.xlsx anterior no se modificó.
