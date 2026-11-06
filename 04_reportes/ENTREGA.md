# ENTREGA — Corpus quechua collao médico

Para: equipo del proyecto · Fecha: 2026-11-05 · Preparado por Claude (Claude Code) en `D:\Corpus_Quechua`

## En 5 líneas

1. **Los 5 bloques están listos en quechua de Cusco (collao), con 5 vocales.** Cada uno tiene 200 oraciones: 140 generales + 60 médicas, en 4 sublotes de 50.
2. **B01 ya no tiene nada chanka por delante.** Las filas 1 a 24, que trabajó el traductor, no se tocaron. Desde la fila 25, cada fila trae un borrador collao o la celda vacía. También dice «Soy de Cusco.» y lleva la misma tabla de ortografía que los demás bloques.
3. **B02 a B05 son nuevos:** usan borradores collao en su forma original y traen frases oficiales del Estado en quechua de Cusco (lo más cercano a «data gold» que hay).
4. **Se extrajeron las fuentes oficiales:** Palabras clave de salud, manual de justicia, glosario PIAS Puno (49 frases de atención) y glosario COVID (135 términos). Además, hay texto paralelo para el equipo de modelo: `06_dataset/texto_paralelo_collao.csv`, 1 881 pares.
5. **Lo que sigue:** revisar el español de B02, pasar a B01 el Word corregido y enviar B02.

## Qué está listo

| Qué | Dónde |
|---|---|
| Archivo maestro (2 848 oraciones, única fuente de verdad) | `02_maestro/corpus_maestro.xlsx` |
| Word para el traductor de B01–B05 | `03_bloques/B0X/B0X_traductor.docx` |
| Excel de trabajo de B01–B05 | `03_bloques/B0X/B0X_trabajo.xlsx` |
| Guía de grabación | `03_bloques/GUIA_GRABACION.docx` |
| **Qué cambió en B01, fila por fila** | `04_reportes/B01_COLLAO.md` |
| **Avance del traductor en B01:** sus filas, sus comentarios y lo que se aprende | `04_reportes/AVANCE_B01.md` |
| **Español para revisar antes de enviar** (B02–B05), con el archivo donde se corrige cada fila | `04_reportes/REVISION.md` |
| Texto paralelo es–quz para el modelo, con la confiabilidad de cada par | `06_dataset/texto_paralelo_collao.csv` |
| JW300 es–quz, solo para preentrenar (religioso, no se graba) | `Fuentes/AmericasNLP/es-quz/` |
| Fuentes collao: qué variedad es cada una y qué se extrajo | `04_reportes/FUENTES_COLLAO.md` |
| Verificación final, prueba de scripts y decisiones | `04_reportes/VERIFICACION_F7.md`, `PRUEBA_06_07_08.md`, `DECISIONES_TOMADAS.md` |
| Especificación actualizada (sección 0) | `Estrategia/CLAUDE.md` |

## Qué pasó con B01

| Filas | Qué tienen ahora |
|---|---|
| 1 a 24 | **Idénticas a las del archivo del traductor:** su quechua, sus comentarios y sus colores. |
| 25 a 200, con borrador (7) | Borrador de una fuente collao: 6 de Farfán (Cusco) y 1 de OPS/OMS Bolivia, que lleva aviso. |
| 25 a 200, vacías (169) | El traductor escribe desde el español. De ellas, 96 traían borrador chanka: **ninguna fuente collao tiene esas frases y el quechua no se inventa ni se convierte a mano.** Las otras 73 ya estaban vacías. |

- **Más trabajo para el traductor:** esas 96 filas ya no traen borrador, igual que la parte general de B02–B05.
- **Español:** solo cambió la fila 30, «Soy de Cusco.». Los IDs y el orden son los mismos.
- **Ortografía:** el Word ya pide 5 vocales y no dice «chanka» en ninguna parte.
- **Control:** B01 ya no tiene oraciones de control, porque su borrador oculto era chanka y no servía para medir. El traductor no nota nada. El anclaje se mide con las 10 de B02.
- **Lo chanka que queda, solo en lo interno:** los borradores que el traductor vio en las filas 1 a 24, para medir cuánto corrigió, y los nombres de las fuentes del español en la pestaña Detalle del Excel.
- **Nada se perdió:** la versión anterior y la copia exacta de su archivo están en `02_maestro/congelados/B01_original/`.

## Qué enviar a quién

1. **B01: pasen al traductor `03_bloques/B01/B01_traductor.docx`.**
   - **Antes, pregúntenle si avanzó después de la fila 24.** Este Word no tiene lo que haya hecho después de su versión v1.
   - Si avanzó, no le pasen este archivo. Guarden el suyo como `02_maestro/congelados/B01_original/B01_traductor_v2.docx` y corran el comando de abajo, que deja intacto lo nuevo que hizo.

   ```
   .venv\Scripts\python.exe scripts\congelar_bloque.py B01 --word 02_maestro\congelados\B01_original\B01_traductor_v2.docx
   ```

2. **Revisen el español de B02** en `04_reportes/REVISION.md` (77 filas). No hace falta saber quechua: es ver si cada oración en español suena natural y dice lo que debe.
3. **Envíen `B02_traductor.docx`.** El traductor siempre va un bloque adelante (D5). Yo no envié nada a nadie.
4. **Al enviarlo, márquenlo:** desde ahí queda congelado.

   ```
   .venv\Scripts\python.exe scripts\06_importar_traductor.py B02 --marcar-enviado
   ```

5. **Cuando vuelva cada Word:** guárdenlo como `03_bloques/BXX/BXX_traductor_devuelto.docx` y corran `06_importar_traductor.py BXX`. Después siguen `07_hoja_grabacion.py` para grabar y `08_manifest.py` con los audios.

## Qué debes revisar

- **Español redactado o adaptado (`Por_revisar`):** 77 filas en B02, 104 en B03, 137 en B04 y 135 en B05. En B02 son 40 oraciones generales nuevas, 30 respuestas del paciente nuevas y 7 frases adaptadas. Las escribí o ajusté yo, no salen tal cual de una fuente; por eso una persona debe leerlas antes de que lleguen al traductor.
- **Avisos en el Word:** 1 en las filas nuevas de B01, 5 en B02, 9 en B03, 9 en B04 y 6 en B05. La mayoría dice que el borrador es boliviano y hay que adaptarlo a Cusco.
- **Cuánto borrador ve el traductor:** 16 filas en B02, 24 en B03 y 30 en B04 y B05. El resto lo traduce desde el español. B02 tiene además 10 frases de control con la celda vacía.
- **Lo que comentó el traductor** (`AVANCE_B01.md`):
  - «desayuno», «remar» y «buenos días» no se dicen así. Quité desayuno y almuerzo de B02–B05, y no quedaba ninguna de las otras;
  - el glosario oficial PIAS sí traduce los saludos («Allin p'unchay», «Allin sukha», «Allin tuta»): conviene preguntarle si le parecen forzados;
  - las frases del Principito con cosas que no hay en los Andes (baobabs, boa, elefante) siguen en B02 y B03. El Word ya le pide escribirlas como las diría un hablante.
- **Por confirmar:** «Mi tía hace chicha punta» y el calco «no + una» de algunos ejercicios (igual que antes).

## ¿Lo oficial y Lopera son gold?

**Ninguno es gold todavía.** Gold sigue siendo lo validado por el traductor y grabado (D8).

- **Fuentes oficiales (MINSA, Ministerio de Cultura):** son lo más cercano, porque son traducciones del Estado al quechua de Cusco. Tienen la máxima prioridad y casi no deberían necesitar cambios, aunque varias escriben con 3 vocales y el traductor las pasará a 5. Entran 25 a los bloques (B02: 2, B03: 7, B04: 2, B05: 14), porque son sobre todo de salud reproductiva y no se torció el plan de temas por eso. Las otras 530 quedan para bloques futuros y ya están en el texto paralelo.
- **Lopera (libro de semiología):** es buen material, pero escribe a la castellana y tiene frases desalineadas («¿Le duele el pulmón?» → «¿Kunkaiki nanan?», y kunka es cuello). Por eso va como borrador.

## Pendientes (P1–P7 y nuevos)

| # | Qué se usó por ahora | Qué falta decidir |
|---|---|---|
| P3 | **Decidido: 5 vocales**, como escribe el traductor. | Nada. El texto paralelo trae fuentes con 3 vocales: el equipo de modelo debe tenerlo en cuenta. |
| Escritura | **Decidido:** lo ya traducido no se toca, aunque use «c» y «j» (cashanqui, mijunchu). Los borradores pendientes siguen la tabla («k» y «h») y el traductor cambia lo que no le parezca. | Nada. El equipo de modelo tendrá que unificar la escritura antes de entrenar. |
| P1 | Todo `train`; 20 filas por bloque marcadas `Test_sugerido = Sí`. | ¿Apartamos ese 10 % como prueba? |
| P2 | B01 ya empezó; B02 listo. | Fecha de la siguiente sesión. |
| P4 | JW300 es–quz solo como léxico y para preentrenar. No se graba. | ¿Lo usa el equipo de modelo? |
| P5 | WAV, 16 kHz, mono, 16 bits. | Confirmarlo con el equipo de modelo. |
| P6 | Ya no aplica: del Grupo 2 solo se usa el español. | — |
| P7 | Los audios de Allin Kawsay no se usan. | — |
| Nuevo | Cusco y Puno juntos; solo lo boliviano lleva aviso. | Que el traductor confirme si le parece bien. |
| Nuevo | Sexto bloque: quedan 530 frases oficiales sin bloque, pero no hay generales suficientes. | ¿Redacto ~90 generales más? |
| Nuevo | OPS/OMS Bolivia: quedan unos 480 pares sin usar. | ¿Los sumamos? Son bolivianos y necesitan adaptación. |

La guía de señalética no se extrajo: sus tablas cambian de una página a otra y salía mezclada con aimara, y son ~40 letreros, casi ninguno médico. Guardar un par equivocado como «oficial» haría más daño que ayuda.

## Cuántos bloques caben

| Bloque | General: Principito / frases variadas / ejercicios / redactadas | Presente | Médica (médico / paciente) | Borradores en el Word | Control |
|---|---|---|---|---|---|
| B01 (con el traductor) | 35 / 65 / 0 / 40 | 51 % | 32 / 28 — consulta completa | 7 desde la fila 25 | — |
| B02 | 35 / 57 / 8 / 40 | 59 % | 30 / 30 | 16 | 10 |
| B03 | 34 / 0 / 35 / 71 | 53 % | 30 / 30 | 24 | — |
| B04 | 0 / 0 / 35 / 105 | 42 % | 30 / 30 | 30 | — |
| B05 | 0 / 0 / 35 / 105 | 39 % | 30 / 30 | 30 | — |

**Caben 5 bloques.** Sobran 431 generales (416 ejercicios y 15 redactadas) y 1 417 médicas. Para un sexto bloque hacen falta ~90 oraciones generales más.

## Cómo regenerar

Desde `D:\Corpus_Quechua`, con Excel y Word cerrados (el Word de B01 no se regenera aquí, y todo corre en CPU):

```
.venv\Scripts\python.exe scripts\02_ingesta.py --forzar
.venv\Scripts\python.exe scripts\03_eda.py --forzar
.venv\Scripts\python.exe scripts\04_limpieza.py --forzar
.venv\Scripts\python.exe scripts\05_huecos.py --forzar --estricto
.venv\Scripts\python.exe scripts\f6_armar_bloques.py --forzar
.venv\Scripts\python.exe scripts\09_texto_paralelo.py
.venv\Scripts\python.exe scripts\f7_verificacion.py
```
