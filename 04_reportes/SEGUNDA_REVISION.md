# Segunda revisión antes de enviar los bloques

Fecha: 5-nov-2026 · Preparado por Claude (Claude Code) · Nada se envió a nadie.

## En breve

Esta vez se leyeron a mano las 1 000 oraciones de los Word y todos los borradores de las filas pendientes, comparando cada uno con su español. La verificación automática pasaba, pero no detectaba este tipo de errores.

- **B01:** la revisión no le cambió nada. Después, a pedido de la coordinación, se cambiaron 3 frases aún sin traducir (ver abajo). Las filas 1 a 24 siguen iguales al archivo del traductor, incluso en colores y comentarios (comparadas en el XML interno del Word).
- **B02 a B05:** 21 frases en español corregidas, 5 avisos nuevos puestos a mano y varios avisos arreglados.
- **Las oraciones de cada bloque son las mismas.** Solo cambiaron de ID dos respuestas de B05, porque se redactaron de nuevo.

## Español corregido

Las filas marcadas **Por_revisar** son redacción mía: entran en `REVISION.md` para que una persona las lea. Las otras son faltas evidentes (tildes y una palabra faltante).

| Bloque | Fila | Antes | Ahora | Tipo |
|---|---|---|---|---|
| B02 | 37 | Mi mamá cocina pescado. | Mi mamá cocina trucha con papas. | Por_revisar: era casi igual a «Mamá cocina pescado.», en el mismo bloque |
| B02 | 48 | Los adultos me desanimaron de ser pintor, cuando yo quería serlo, a la edad en que decidí dedicarme a ello. | Los adultos me desanimaron de ser pintor cuando tenía seis años. | Por_revisar: larga y enredada |
| B02 | 63 | ¿La tos se acompaña de dolor hacia alguna parte de la espalda? | Cuando tose, ¿le duele alguna parte de la espalda? | Por_revisar: poco natural |
| B02 | 89 | ¿Le funciona bien el intestino y formado? | ¿Le funciona bien el intestino? | Por_revisar: frase rota en el libro |
| B02 | 108 | ¿Dónde quieres llevarte mi cordero? | ¿A dónde quieres llevarte mi cordero? | Falta |
| B02 | 140 | Hoy hace buen día. | Hoy amaneció con sol. | Por_revisar: era casi igual a «Hoy es un buen día.», en el mismo bloque |
| B02 | 177 | ¿A que tiempo de gestación? | ¿A qué tiempo de gestación? | Falta |
| B02 | 183 | ¿Cuando fue tu última regla? | ¿Cuándo fue tu última regla? | Falta |
| B03 | 68 | Ella pinta con achiote. | Ella tiñe la lana con cochinilla. | Por_revisar: costumbre de la selva |
| B03 | 74 | Yo cazo con arco y flecha. | Yo cazo vizcachas con mi perro. | Por_revisar: costumbre de la selva |
| B03 | 116 | ¿Alguna vez ha orinado sangre y con olor? | ¿Alguna vez ha orinado sangre con dolor? | Por_revisar: el libro dice «olor», pero su quechua dice *nanay* (dolor) |
| B03 | 158 | Necesitamos examen por un médico. | Necesitamos que lo examine un médico. | Por_revisar: poco natural |
| B04 | 67 | Ellos pescan con veneno de barbasco. | Ellos pescan truchas en la laguna. | Por_revisar: costumbre de la selva |
| B04 | 155 | Cuando tose fuerte, ¿le duele?, ¿qué lado? | Cuando tose fuerte, ¿le duele? ¿De qué lado? | Por_revisar: igual que su frase hermana |
| B04 | 173 | Necesario hacer un examen. | Es necesario hacer un examen. | Falta |
| B05 | 5 | …o le dolía a orinar? | …o le dolía al orinar? | Falta |
| B05 | 11 | …o del pulmon? | …o del pulmón? | Falta |
| B05 | 29 | ¿Fueron espontáneos? | ¿Los abortos fueron espontáneos? | Por_revisar: sola no se entiende; en la fuente sigue a «¿Tuviste abortos?» |
| B05 | 41 | ¿Como se enteró de este método? | ¿Cómo se enteró de este método? | Falta |
| B05 | 106 | No, en eso no me obliga. | No, nunca me ha obligado. | Por_revisar: respuesta mía poco clara (ID nuevo: CLI-2050) |
| B05 | 118 | Sí, también me ha lastimado. | Sí, algunas veces me ha lastimado. | Por_revisar: «también» no se refería a nada (ID nuevo: CLI-2051) |

El quechua de estas filas no se tocó.

También se corrigieron 11 faltas parecidas en frases que aún no están en ningún bloque, como «¿Que edad…» o «el pené esta duro». Quedan en la pestaña `Cambios` del maestro. Al corregir «¿Le funciona bien el intestino?», esa frase quedó igual a otra que ya existía y se unieron: por eso el maestro pasó de 2 848 a 2 847 oraciones.

## Avisos para el traductor

**Nuevos, puestos a mano.** El borrador no dice lo mismo que el español. Se comprobó en el PDF de Lopera que el error viene del libro, no de la extracción:

| Bloque | Fila | Español | Borrador | Aviso |
|---|---|---|---|---|
| B02 | 46 | ¿Cuando tose le duele más? | ¿Sorq'an nanan ¿Uhunki hinachu nanan masta? | «¿Sorq'an nanan» parece sobrar: sería de la frase del pulmón |
| B03 | 29 | ¿Le duele el pulmón? | ¿Kunkayki nanan? | *Kunka* es cuello; el español dice pulmón |
| B03 | 56 | ¿Tiene agitación por momentos o todo el día? | ¿Sayk'unki hask'tachu pisillatachu? | Parece preguntar «mucho o poco» |
| B03 | 83 | ¿Se ha hinchado en los últimos meses? | ¿Tekneyki punkirkanchu iskay ultimo killata? | Menciona cadera y dos meses; el español no los dice |
| B04 | 29 | ¿Tiene dolor de cabeza y se acompaña de náuseas? | ¿Umaykichu mansunkiy… umayqkichu muyun? | Parece preguntar por mareo, no por náuseas |

No soy hablante de quechua: estos avisos son sospechas, y decide el traductor.

**Arreglados:**
- **B05, fila 129:** decía que los números no coincidían, pero *kinsa* sí es «tres». Aviso falso, quitado.
- **B03, fila 35:** decía que «Purijtiyki» era un préstamo del español. No lo es: es el subordinador *-jti-*, de otra zona. El aviso ahora dice eso. Por la regla de siempre, la «j» del borrador pasó a «h»: «Purihtiyki».
- **Texto de programa en el Word:** un aviso decía `español — vs quechua ['2']`. Esa fila ahora lleva el aviso escrito a mano. El detector ya no usa corchetes.
- **«(y otros)»:** se quitó de los avisos, porque el traductor no podía ver esos otros.

## Control de B02

Siguen siendo 10 frases con la celda vacía. Una de ellas (B02, fila 46) tenía el borrador desalineado de arriba, así que medir contra ella daría una cifra falsa.

- **Sale:** esa frase, que ahora muestra su borrador con el aviso. También sale «¿Tienes hambre?» (fila 70), porque la selección se recalculó, y ahora muestra su borrador.
- **Entran:** «¿A qué hora tienes fiebre?» (fila 17) y «Cada vez que orina, ¿tiene ardor?» (fila 95).

## Otras cosas que cambiaron

- **Orden:** 54 filas de B02 y 18 de B03 aparecen distintas, sobre todo porque varias oraciones generales cambiaron de posición: el armado reparte de nuevo los tiempos verbales por sublote. Las preguntas y respuestas médicas siguen juntas y en su lugar. No afecta nada, porque esos bloques aún no se envían.
- **Propiedades de los Word de B02–B05 y de la guía:** el autor ya no es «python-docx».
- **Verificación:** ahora revisa también tildes en preguntas, oraciones casi iguales dentro de un bloque, avisos legibles, que los avisos a mano lleguen al Word y que ningún control tenga un borrador marcado como desalineado.

## Lo que dejé sin tocar

- **Faltas de tipeo en los borradores** («Alllinmi», «Simiyku», «manua», «qhawanki'»): están así en la fuente. No corrijo quechua a mano; las arregla el traductor al revisar.
- **Palabras de selva que sí se pueden decir en quechua** (jaguar, tigre, yuca, plátano, bosque): se quedan. Si alguna no le parece, el Word ya le pide escribirla como la diría un hablante.
- **Pie «Información Interna» en B01:** ya venía en el archivo del traductor; no lo puse yo y no lo quité. Los otros bloques no lo tienen.

## Frases cambiadas en B01, a pedido de la coordinación

Eran frases que quizá no le sonarían al traductor, parecidas a las que ya comentó. Todas están después de la fila 24, tenían la celda de quechua vacía y conservan su ID y su lugar.

| Fila | ID | Antes | Ahora | Por qué |
|---|---|---|---|---|
| 104 | GEN-0185 | La canoa está rota. | La soga está rota. | Comentó «no hay remar»; la canoa tampoco es de la sierra de Cusco |
| 152 | GEN-0866 | Ahora estoy cocinando el almuerzo. | Ahora estoy cocinando mote. | Mismo problema que «desayuno», que comentó que no se dice |
| 183 | GEN-0161 | Mi tía hace chicha punta. | Mi tía hace chicha de jora. | «Chicha punta» estaba por confirmar |

**Si el traductor ya avanzó hasta alguna de estas filas,** su versión se queda: lo ya traducido no se toca.
