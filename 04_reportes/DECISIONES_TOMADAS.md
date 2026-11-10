# Decisiones tomadas

> Cada valor por defecto usado (CLAUDE.md §4) y cada decisión propia, con su porqué. La coordinación del proyecto revisa al final.
> Formato: **[Fase] Decisión** — porqué.

## B01 v1.5 y columna «Vocabulario» (10-nov-2026) — manda sobre lo de abajo en lo que se contradiga

Pedido de la coordinación: poner en el repositorio el `B01_traductor_v1_5_collao.docx` actualizado, «solo sobreponlo, nada más», y dejar vacía la parte de «Vocabulario» en los otros bloques.

- **[B01] Se copió el archivo tal cual** sobre `03_bloques/B01/B01_traductor.docx` (mismo hash). La versión anterior quedó en `02_maestro/congelados/B01_original/B01_traductor_collao_antes_de_v1_5.docx`. No se corrió `congelar_bloque.py`, así que el maestro y `congelados/B01.xlsx` siguen con la versión anterior. `f6_armar_bloques.py` no rehace el Word de B01, de modo que la copia no se pierde al regenerar.
- **[B01] Lo que trae ese archivo y no se tocó:** 190 filas (faltan 10), columna «Vocabulario» con 118 filas llenas, 148 filas distintas del B01 anterior (quechua, notas y, en muchas, también el español), y notas con fuentes en «Observaciones». Se dejó así porque el pedido fue solo sobreponerlo.
- **[B01] Título, instrucción 1 y ortografía pasados a collao** (a pedido de la coordinación, después de sobreponer): título «Traducción al quechua de Cusco (collao)», «quechua de Cusco natural» y la tabla de ortografía de cinco vocales copiada de B02. Solo cambió ese texto; las filas siguen idénticas al archivo de Descargas. B01 no lleva la instrucción 2 de los otros bloques («el quechua es un borrador…»).
- **[B01] Las 10 filas que faltan no se vuelven a agregar** (N° 25, 39, 43, 44, 52, 53, 56, 58, 61 y 62). La coordinación entiende que se quitaron durante la grabación y que eso es parte del proceso. B01 queda con 190 filas; al importar su respuesta, esas 10 aparecerán como ausentes y es lo esperado.
- **[B02–B05] Columna «Vocabulario (español – quechua)» vacía** como 7.ª columna, con los anchos del B01 nuevo (`f6_armar_bloques.py`). `f7_verificacion.py` acepta ahora las 7 columnas y comprueba que esa columna esté vacía en B02–B05. `06_importar_traductor.py` usa las columnas 0 a 5, así que no se afecta; por ahora no importa el vocabulario.
- **[F7] 153/160:** las 7 fallas son todas de B01 (no coincide con el maestro ni con su foto). No se relajaron las pruebas para taparlas.

## Segunda revisión antes de enviar (5-nov-2026, cuarta parte) — manda sobre lo de abajo

Pedido de la coordinación: «¿Podrías darle una segunda revisada antes de enviar los bloques?». Detalle, fila por fila, en `04_reportes/SEGUNDA_REVISION.md`.

- **[B01] Solo 3 frases más, a pedido de la coordinación** («Cámbialas tú»): «La soga está rota.» (fila 104), «Ahora estoy cocinando mote.» (152) y «Mi tía hace chicha de jora.» (183). Están después de la fila 24, tenían el quechua vacío y conservan ID y lugar. Las frases nuevas son redacción de Claude, y el traductor puede cambiarlas. Si avanzó hasta alguna de esas filas, queda su versión (`ESPAÑOL_CAMBIADO` en `congelar_bloque.py`).
- **[Español] Faltas de la fuente sí se corrigen** (`erratas_es.yaml`); lo que es redacción mía va a `adaptaciones_es.yaml` y queda `Por_revisar`. Esto incluye frases de fuentes oficiales: la fuente oficial se respeta en su quechua, no en sus faltas de tipeo en español.
- **[Quechua] Lo desalineado no se corrige a mano: se avisa** (`avisos_manuales.yaml`, 5 avisos). Claude no es hablante. La excepción es la regla mecánica de siempre (§10.3): «Purijtiyki» ya no se confunde con un préstamo, así que su «j» pasa a «h».
- **[Control] Se excluye QCH-0708** (`control.excluir_codigos`): su borrador trae un trozo de otra frase y daría una medida falsa de anclaje.
- **[Selva] Se cambian solo 3 frases** sin sentido en Cusco (barbasco, achiote, arco y flecha), porque el traductor ya comentó «no hay remar». Jaguar, tigre, yuca, plátano y bosque se quedan: se pueden decir en quechua y yuca y plátano se dan en el valle de La Convención.
- **[Fuentes] Segunda búsqueda: nada entra sin decisión de la coordinación** (`FUENTES_COLLAO.md`, sección 4). Solo cuenta como validado lo que se abrió. B01–B05 ya están completos y sus borradores no cambian por esto. El bloqueo de gob.pe no se intentó saltar.
- **[Verificación] Pasar F7 no bastaba.** Había avisos falsos, faltas de tilde y un borrador con otro significado (pulmón con *kunka*, que es cuello) que F7 no medía. Se agregaron esos puntos a F7 y a `test_qa.py`, pero la lectura fila por fila no se reemplaza con un script.

## B01 a collao, 5 vocales y glosarios (5-nov-2026, tercera parte) — manda sobre lo de abajo

Respuestas de la coordinación: «Si el traductor usó 5, son 5»; «Mejor Cusco. Si es posible también cambia las oraciones del bloque 1 a collao»; pasarle al traductor el Word corregido; «¿por qué no lo extrajiste?» (glosarios).

- **[P3] 5 vocales** (`variedad.vocales: 5`), en todos los bloques. Las fuentes con 3 vocales se dejan como vienen: el traductor las corrige.
- **[Escritura] «c» y «j» del traductor.** Coordinación: «en lo que ya esté traducido, no se toca; lo que sí, puedes modificarlo; si hay algo que no le parezca, lo cambiará». La tabla del Word sigue pidiendo «k» y «h». En los borradores pendientes, «cc» y la «c» final pasan a «q», aunque la palabra no esté en el léxico (quedaban 2 filas: «killatac» → «killataq» en B02 y «seccsisunkicho» → «seqsisunkicho» en B04).
- **[B01] Solo se cambia lo que el traductor no ha trabajado** (`scripts/congelar_bloque.py`, detalle en `04_reportes/B01_COLLAO.md`):
  - filas 1–24 (hasta la última que tocó, incluida la 21, que dejó igual pero coloreó): idénticas a su archivo;
  - filas 25–200: el borrador chanka sale. Entra el de una fuente collao con el mismo español (7 filas) o queda vacía (96 filas que traían borrador chanka; 73 ya estaban vacías);
  - **no se convirtió el chanka a collao con reglas** (kachkanki → kashanki, etc.): sería escribir quechua sin fuente, y la regla del proyecto es no inventarlo. La coordinación lo confirmó: «dejarlas vacías». Además, de las 16 filas con borrador que el traductor vio, cambió 14;
  - «Soy de Ayacucho.» → «Soy de Cusco.» (fila 30). Es el único español que cambió;
  - sin oraciones de control en B01: su borrador oculto era chanka y la medida no serviría. El anclaje se mide con las 10 de B02;
  - tabla de ortografía igual a la de los demás bloques (se agregó la fila de semivocales).
- **[Excel de B01]** Ya no es byte a byte el de git: f6 lo rehace con la foto, conservando lo que anote el equipo. El original sigue en `02_maestro/congelados/B01_original/`. Los borradores chanka de las filas 1–24 se quedan en lo interno, porque son la base para medir cuánto corrigió.
- **[Mi error] Los glosarios sí se podían extraer.** Dije que separar las columnas «requiere más trabajo» sin haberlo probado:
  - *PIAS Lago Titicaca (Puno)*: 49 frases de atención, por la altura del texto en dos páginas enfrentadas. Entran como `fuente collao oficial` (36 al corpus, el resto al léxico). «Mi nombre es (…)» no entra al corpus porque no se puede grabar;
  - *COVID-19 VMI*: 135 términos, por su línea «quechua Cusco Collao:». Son términos: van al léxico y al texto paralelo, no a los bloques;
  - *Guía de señalética*: **no se extrajo**. Lo probé: el ancho de sus columnas cambia en cada tabla y salía mezclada con aimara, para ~40 letreros casi nada médicos. Guardar un par equivocado como «oficial» haría más daño que ayuda.
- **[F5]** Dos preguntas de PIAS entraron a B05, así que llevan respuesta redactada en español («Me llamo Rosa.», «Tengo cuarenta años.»).
- **[Avisos]** Ya no nombran otras variedades, porque el traductor los lee: dicen lo que se usa en Cusco. «Machkha» ya no se confunde con el progresivo -chka-.

## B01 congelado con el avance del traductor + fuentes collao oficiales (5-nov-2026, segunda parte)

Pedidos de la coordinación: «descarga lo que encuentres… también la de AmericasNLP pero en collao»; «aprovechar la data gold»; «combinas puneño con cusqueño»; «prioriza lo necesario para el desarrollo del producto». Y la corrección: «el bloque 3 no era el que quedaba como ya estaba, ese era el 1 y ya empezamos […] Incluso el 1, no lo cambies, pero cámbiale las referencias al chanka […] Los demás, sigue tal cual».

- **[B01] Tal cual lo tiene el traductor.**
  - Se recibió `B01_traductor_v1.docx`: las mismas 200 filas (IDs y orden) que la versión de git (commit «Generealizando Documentos», 16-oct-2026), con 22 filas de quechua trabajadas y 11 comentarios.
  - Copia exacta en `02_maestro/congelados/B01_original/`, junto con el Word de git, el Excel, el maestro y el checkpoint F6 de esa versión.
  - `scripts/congelar_bloque.py` crea la foto `02_maestro/congelados/B01.xlsx` (200 filas, con Corpus, Origen y QA) y deja el Word en `03_bloques/B01/`, cambiando solo el título, la instrucción y la tabla de ortografía. Si las filas cambiaran, no lo guarda.
  - El Excel de trabajo es idéntico byte a byte al de git. Su pestaña Detalle todavía nombra fuentes chanka: es rastro interno y el traductor no la ve.
  - Con `bloque.congelados: [B01]`, F5 no lo replanifica y F6 copia sus filas al maestro, sin rearmarlo ni regenerar sus archivos. Ninguna frase con el mismo español se usa en otro bloque.
  - En esta primera versión se dejaron sus borradores chanka y «Soy de Ayacucho.» (fila 30), porque el pedido fue no cambiar sus filas. La tercera parte, arriba, los cambia.
  - **Se marcó `Enviado` solo en el maestro**, con `06 --marcar-enviado` y sin tocar su Excel. No se importó v1 como validado, porque el bloque sigue en curso.
  - El congelamiento de B03 de la primera parte del día se deshizo: B03 se rearmó en collao como B02, B04 y B05.
- **[Traductor] Lo que enseña su avance** (`04_reportes/AVANCE_B01.md`, generado por `scripts/avance_traductor.py`):
  - «desayuno», «remar» y «buenos días» no se dicen así. Se cambiaron 5 oraciones redactadas (desayuno, almuerzo y mar). Se dejaron las frases del Principito con cosas que no hay en los Andes, porque el Word ya le pide escribirlas como las diría un hablante;
  - sus filas entran al texto paralelo como `traductor_en_curso`;
  - para P3: escribe con 5 vocales y a la castellana, aunque la tabla pedía otra cosa.
- **[Pruebas]** `test_ida_vuelta.py` ahora usa B02, porque el Word de B01 ya tiene trabajo real. F7 revisa B01 aparte: filas idénticas al Word del traductor y Excel idéntico byte a byte, en lugar de «celda Quechua = borrador».
- **[IDs] Se volvió al registro de IDs de esa versión** (el de git), para que B01 conserve sus IDs. La numeración collao de la primera prueba de hoy (que empezaba de cero) quedó en `02_maestro/checkpoints/ids_collao_primera_prueba_20261105.csv`. Así, una frase que no cambió tiene el mismo ID que el 16-oct. Una oración cuyo español se reescribe recibe un ID nuevo (pasó con las 5 de arriba, que nunca se enviaron).
- **[F2] Fuentes collao oficiales** (`Fuentes/collao/`, detalle en `FUENTES_COLLAO.md`):
  - *Palabras clave para la atención en salud – Quechua Cusco* (MINSA): 1 077 pares extraídos por la posición del texto en la página.
  - *Manual del quechua Cusco Collao en la administración de justicia* (Ministerio de Cultura, 2015): 106 líneas de diálogo no legales.
  - Entran como frases médicas con `Tipo_borrador = fuente collao oficial` (calidad 1) y `Origen_verificado = Sí (fuente oficial)`.
  - No se normalizan (fuente oficial: tal cual) y se ubican en la consulta por palabras clave (saludo, filiación, familia, embarazo, anticoncepción, violencia, medicación…).
  - Cuando la fuente dice quién habla (F/C), F4 ya no lo recalcula.
  - Las entradas de *Palabras clave* de 3 palabras o menos que no son pregunta ni orden («Examen de sangre.») van al Léxico.
- **[«Data gold»]** Las frases oficiales son lo más cercano a gold que hay: traducidas por el Estado al quechua de Cusco. Siguen la regla D8 (el traductor las confirma y se graban), pero casi no deberían necesitar cambios.
  - Se priorizan en el plan médico (calidad 1).
  - **Entran pocas a los bloques** (B02: 2, B03: 7, B04: 2, B05: 14) porque son sobre todo de salud reproductiva y los temas de B02–B04 son otros. No se torció el plan por eso, porque el producto manda.
  - Las ~500 oficiales sin bloque quedan para bloques futuros y para el texto paralelo del equipo de modelo.
- **[No] Emparejar pregunta–respuesta automáticamente en *Palabras clave*:** se probó con «la fila siguiente», pero solo ~12 de 28 eran pregunta y respuesta reales. Se siguió con respuestas redactadas en español (17 nuevas para preguntas oficiales).
- **[Léxico] JW300 es–quz (AmericasNLP 2021)**, la misma fuente de antes pero en quechua de Cusco, descargado de GitHub. Las palabras que aparecen 2+ veces entran al léxico de referencia (de ~1 550 a ~39 000 palabras), igual que antes se usaba el JW300 quy. No se graba (P4).
- **[Producto]** `scripts/09_texto_paralelo.py` → `06_dataset/texto_paralelo_collao.csv`: 1 881 pares es–quz con su confiabilidad, para que el equipo de modelo pueda entrenar o probar traducción mientras se graban los bloques. No incluye nada chanka: de B01 solo entran las 22 filas que el traductor ya trabajó y las que tienen borrador collao.
- **[Variedad]** Cusco + Puno juntos, como pidió la coordinación: los borradores de Lopera (Puno/Cusco) se usan igual que los cusqueños; solo lo boliviano lleva aviso de adaptar. La revisión final de la variedad es del traductor.
- **[No descargado]** El dataset de Hugging Face no se bajó (parece el mismo JW300, licencia sin confirmar). Los glosarios multilingües quedaron sin extraer en esta parte; ver la tercera parte, arriba.

## Cambio a quechua collao (5-nov-2026) — manda sobre lo que diga «chanka» más abajo

Pedido de la coordinación del proyecto: «ya no trabajaremos con ni uno de chanka… estamos de 0»; variedad **collao de Cusco** («posiblemente Puno también, pero collao en general»); vocales «se definirá después». Las secciones F0–F6 de abajo describen la versión chanka; donde choquen, vale esto:

- **[§0] Qué se conserva y qué sale.** Se conserva todo el español (no depende de la variedad) y el diseño de bloques. Sale el quechua de toda fuente chanka: el «Quechua_final (chanka)» del unificado, SOCEMURP, MinCul, afiche, diabetes, YouTube, MINSA, Allin Kawsay, Grupo 2 y Principito (este último traducido con un modelo `quy`). El quechua chanka sigue en las fuentes y en `Origen` → `Propuestas_equipo` (rastro), pero no es borrador.
- **[§0] Allin Kawsay es chanka.** Es la app del INS/MINSA probada en Chopccas (Huancavelica) según la prensa de su lanzamiento; además está transcrita de oído. Por eso su quechua también sale.
- **[F2] Borradores collao en su forma original:**
  - Lopera (2020): la forma del libro que el unificado guardaba con el prefijo «Libro:»; 564 filas, 287 en el corpus (el resto son palabras sueltas en Léxico).
  - Farfán (2001): la tabla del HTML, cusqueño; los 24 del unificado más **25 frases que el unificado no tenía**, que entran como filas nuevas `FA-xx`.
  - OPS/OMS Bolivia (2013): el quechua del PDF (661 pares), emparejado por el español con similitud ≥ 92 (con 90–91 aparecían empates falsos como «tomografía» ↔ «radiografía»); 174 filas.
  - El parser del PDF de OPS distingue continuación del español, notas entre paréntesis, títulos de sección y quechua.
- **[F2] Sin verificación P6.** Era para saber si el Grupo 2 salía del diccionario chanka; del Grupo 2 ya solo se usa el español.
- **[F4] Ortografía collao (§10.3):**
  - Las glotalizadas y aspiradas **se conservan**.
  - «j» → h siempre (Cusco escribe h).
  - c/qu/hu → k/q/w solo si la palabra resultante existe en el léxico collao.
  - Semivocales: «ai» → «ay», «y» entre consonantes → «i» (sin tocar la «qu» castellana: «Yupanqui»).
  - Tres vocales solo si `variedad.vocales` = 3 (P3).
- **[F4] Léxico de referencia collao:**
  - Contiene todo el quechua de Lopera, Farfán y OPS. Los préstamos que traen esas fuentes no cuentan («tomanki», «verdura»).
  - Se compara sin glotales ni aspiración y con 3 vocales, así «p'unchay» = «punchay».
  - Las raíces sacadas al quitar sufijos deben tener 4+ letras, salvo que sean palabra completa (evita raíces espurias como «lli», «tuma»).
  - Es chico (~1 550 palabras): por eso OOV va en BAJA. Del AmericasNLP solo queda el lado español, como léxico español.
- **[F4] Avisos de variedad invertidos.** Ahora se marca lo que no es de Cusco: -chka-, validador -m, -nchik, -pti-, yaku, upyay/ukyay, llamkay, punchaw, haykap, machkha, llawar. En los borradores de OPS va un solo aviso ALTA («borrador en quechua boliviano: adáptelo al quechua de Cusco») y los rasgos sueltos bajan a MEDIA. Nuevo aviso MEDIA cuando la palabra se escribe siempre con glotalizada o aspirada en las fuentes collao y aquí no.
- **[F4] Calidad del borrador** (`config.medico.calidad_borrador`): fuente collao oficial 1 > Farfán 2 > Lopera 3 > OPS/OMS Bolivia 4 > solo español 7. Si el equipo marcó «Revisar – duda de traducción», baja a 5. «Revisar – adaptación propuesta» ya no cuenta como duda, porque era sobre adaptar a chanka.
- **[F4] Español:**
  - Lugares de la zona chanka → Cusco/Puno: «Soy de Ayacucho» → «Soy de Cusco»; en las oraciones redactadas, Huamanga → Sicuani, Huanta → Urubamba, Huancavelica → Puno, carnaval de Ayacucho → Inti Raymi; en las respuestas, Andahuaylas → Sicuani.
  - «intérprete de quechua chanka» → «de quechua».
  - 8 correcciones del español de Farfán que no calzaba con su quechua (p. ej. «¿Por qué vives?» → «¿Por qué vienes?», «hamusianki»).
- **[F5] Más respuestas del paciente.** Con la nueva calidad, el plan médico prefiere frases con borrador collao, y aparecieron 54 preguntas sin respuesta más 7 indicaciones que hacían falta para completar 60 médicas en B03–B05. Se redactaron en español, sin contradecir las demás del bloque y sin repetir texto. F5 ahora encuentra las filas del guion de B01 y las respuestas aunque su código haya quedado unido a otra fila al deduplicar (p. ej. «¿Cómo te llamas?» de SOCEMURP, que quedó en la versión de Farfán con borrador).
- **[F6] Parte general sin borrador → cobertura medida en el español.** La selección voraz usa rasgos gramaticales del español que en quechua son sufijos (tiempo, persona, posesivo, caso, subordinación, negación, pregunta, plural) y palabras nuevas (`heuristicas.unidades_es`, pesos en `config.general.pesos_cobertura`). La medición de tiempo reconoce ahora pretéritos irregulares («fui», «hizo»). Presente por bloque: 55 / 57 / 51 / 43 / 39 %.
- **[F6] Control (D7) repartido.** La parte general ya no tiene borrador y en B01 solo hay 11 frases médicas con borrador, así que se toman 15 frases médicas con borrador: 5 en B01 y 10 en B02 (`config.control.por_bloque`). Siguen sin «hermanas» visibles en B01+B02.
- **[F6] Word:** título «quechua de Cusco (collao)», tabla de ortografía collao (cambia sola si se elige 5 vocales) e instrucción «el borrador puede tener formas de otras zonas: déjelo como se dice en Cusco». No dice de qué fuente viene cada borrador (§8.4).
- **[06] Sublote devuelto sin tocar:** el mínimo baja de 10 a 5 filas con borrador, porque con collao hay ~4–8 borradores por sublote.
- **[Pruebas]** `test_qa` se reescribió con casos collao (lo que antes se marcaba como «no chanka» ahora es lo correcto). `test_ida_vuelta` pone borradores simulados en la copia de B01, porque B01 real casi no los tiene.
- **[IDs]** Como se empieza de cero, el registro de IDs se rehízo. El chanka quedó en `02_maestro/checkpoints/ids_chanka_hasta_20261105.csv`; la fecha de los datos pasó a `2026-11-05`.
- **[Fuentes]** Al probar la ingesta se sobrescribió por error el checkpoint F2 chanka del 15-oct. Se renombró `F2_ingesta_20261015_sobrescrito_con_prueba_collao.xlsx` para que no se confunda; los checkpoints chanka del 14 y 15-oct (F3–F6) siguen intactos. `CLAUDE.md` cambió (sección 0): la huella anterior quedó en `huella_fuentes_F0_hasta_20261105.json`.
- **[Investigación]** Fuentes collao nuevas encontradas, sin descargar (requieren permiso): `04_reportes/FUENTES_COLLAO.md`.

## Instalaciones (regla del proyecto: instalar lo necesario, nada de simulaciones)

| Qué | Versión | Para qué |
|---|---|---|
| Entorno `.venv` (Python 3.14.7, `py -3.14`) | 3.14.7 | Entorno propio del proyecto; no se tocan `inf659_env` ni `.venvs`. |
| pandas, openpyxl, python-docx, rapidfuzz, pypdfium2, pyyaml, matplotlib | ver `requirements.txt` (versiones fijadas) | Lo pedido en F0. |
| numpy, pillow | ver `requirements.txt` | Ya venían con pandas/matplotlib; se fijan porque f6 (matriz de similitud) y `render_revision.py` (PNG) los usan directamente. |
| LibreOffice (winget `TheDocumentFoundation.LibreOffice`) | 26.8.1 | En la PC no hay Word ni Excel. Se usa en F7 para abrir de verdad cada `.docx`/`.xlsx`, convertirlo a PDF y mirar las páginas. |

## F0 – Preparación

- **[F0] Estructura real de carpetas ≠ §7.1.** Las fuentes están en `Fuentes/` (no en la raíz) y CLAUDE.md en `Estrategia/`. Las salidas (`02_maestro/`, `03_bloques/`, `04_reportes/`, `05_audio/`, `06_dataset/`, `scripts/`, `config.yaml`, `.venv/`) van en la raíz `D:\Corpus_Quechua\`. Las rutas están en `config.yaml` (`rutas.fuentes`). No cambia la composición de los bloques.
- **[F0] `Estrategia/INF657_CLAUDE_corpus.md`** es una copia idéntica de CLAUDE.md anterior a la regla de instalación. No se usa ni se modifica.
- **[F0] Python 3.14** (el más nuevo instalado; también hay 3.10). Todos los paquetes tienen ruedas para 3.14.
- **[F0] Fecha fija en `config.yaml` (`fecha_generacion`)** para checkpoints, Cambios y la pestaña LEEME: así volver a correr los scripts produce exactamente lo mismo (§14, idempotencia). Era `2026-10-14`; pasó a `2026-10-15` al regenerar todo tras la revisión ultracode (los checkpoints del 14 quedan como historia).
- **[F0] LibreOffice instalado** porque la PC no tiene Word ni Excel y F7 exige abrir cada archivo generado (regla del proyecto: instalar, no simular).
- **[F0] Huella de las fuentes** (`04_reportes/huella_fuentes_F0.json`: tamaño, fecha y sha256 de los 31 archivos de `Fuentes/` y `Estrategia/`) para comprobar en F7 que no se tocaron. Se tomó **después** de agregar la regla de instalación a CLAUDE.md (requisito del proyecto).

## F1 – Inventario

- **[F1] Las cifras de §5 coinciden** (0 diferencias grandes). No hubo que detenerse. Diferencias pequeñas explicadas en `INVENTARIO.md`: Grupo 2 tiene 669 oraciones reales (F-0517 vacía, F-0013 duplicado, 3 filas de bibliografía); AmericasNLP tiene 135 647 pares (no ~180k); solo se usa como léxico (P4), así que no cambia los bloques.
- **[F1] `Quechua médico.html` = Farfán Cantero (2001), SITUA (Cusco)**, no Allin Kawsay. Está en Windows-1252.
- **[F1] `entrevistaquechua_spa.pdf` = OPS/OMS Bolivia 2013** (confirmado por la portada).
- **[F1] Grupo 3 «Términos médicos»:** última fila con columnas invertidas (Aycha/Músculo) y «Hueso → Tullu nanay» desalineado. Es solo referencia; no se corrige.

## F2 – Ingesta

- **[F2] Qué entra a los bloques:** unificado (médico) + Principito + Grupo 2 (general). Grupo 3 original, Términos y Corpus_Construido solo para cruzar (D10). Corpus_Construido: sus 111 filas están en el unificado (por español o quechua).
- **[F2] Tipo_borrador ampliado.** La lista de §8.2 no cubría todas las fuentes del unificado; se agregaron: «Allin Kawsay (transcripción)», «normalizado de Farfán (cusqueño)», «fuente chanka oficial» (MinCul y afiche), «YouTube (transcripción)», «MINSA (material en quechua)». Filas sin quechua → «ninguno».
- **[F2] P6 verificado de verdad contra el diccionario MINEDU.** El PDF del diccionario tiene capa de texto: se extrajeron sus ~2 300 ejemplos y se compararon (rapidfuzz, ≥ 90) con el quechua y el español de cada fila del Grupo 2, junto con las 643 frases MINEDU de AmericasNLP. **Solo 2 de 669 coinciden.** Conclusión: las frases del Grupo 2 no son ejemplos del diccionario; son frases del equipo con léxico chanka. Se mantiene la clasificación de §5.2 (minúscula o pronombre inicial → «ejercicio generado»; el resto → «MINEDU», pool «frases variadas») con `Origen_verificado = No` (salvo las 2). La evidencia (similitud máxima y texto más parecido) queda en `Origen`.
- **[F2] Grupo 2: 124 frases variadas y 545 ejercicios** (no ~170 / ~500 como estimaba §11.1).
- **[F2] Rol por heurística** (`scripts/heuristicas.py`): preguntas y órdenes → Médico; 1.ª persona → Paciente; «Si …» sin tilde es condicional (Médico); «Le voy a…», «Quiero preguntar…», «Yo soy el doctor…» y la sección «Presentación del profesional / acceso lingüístico» → Médico. Revisé a mano las 40 filas que salen como Paciente.
- **[F2] Etapas:** mapeo de §11.3. Secciones que no estaban en la tabla: «14. Puericultura y controles» → Recolección; «16. Hospital, procedimientos y evolución» → Explicación y plan; 2 filas de Farfán sin sección quedan «Sin sección» (prioridad baja).
- **[F2] EL-0001:** la nota de plantilla de Observaciones se ignora (§5.2).

## F3 – EDA

- **[F3] Léxico de referencia para OOV/préstamos:** JW300 quy (2+ apariciones), diccionario MINEDU (PDF + AmericasNLP), Dict_misc, MinCul, afiche y diabetes en quechua; solo formas escritas con el alfabeto chanka. Raíces: ~1 000 lemas del diccionario MINEDU + entradas de una palabra de Dict_misc. El español de referencia sale del lado español de AmericasNLP (solo palabras vistas en minúscula, para no contar nombres propios).
- **[F3] Reglas de QA probadas con los casos de §6** (`scripts/test_qa.py`): los 32 casos salen marcados, el DUP de QCH-0050 también, y la normalización mecánica da lo esperado sin tocar préstamos ni nombres propios («Lince», «Ayacuchomanta», «Coronavirus»).
- **[F3] Casi duplicados:** similitud ≥ 90 **y** misma polaridad **y** mismos números; máximo 2 por grupo, y si dos tienen el **mismo borrador quechua** solo queda 1 (p. ej. «ellos/ellas bajan al río» → «Paykuna mayuman uraykunku»: grabarlo dos veces no aporta).
- **[F3] Figuras** con la paleta de referencia validada (slots 1–3), barras finas, texto en tinta y leyenda solo con 2+ series. Son PNG estáticos dentro de un .md, sin capa interactiva; las tablas del EDA hacen de «vista de tabla».

## F4 – Limpieza

- **[F4] Datos revisados a mano** en `scripts/datos/`: `erratas_es.yaml` (erratas evidentes y tildes, sacadas de las palabras que no están en el léxico español de referencia), `adaptaciones_es.yaml` (giros bolivianos del OPS/OMS, preguntas múltiples, notas entre paréntesis → Por_revisar) y `particiones_es.yaml` (oraciones de más de 20 palabras). Todo cambio queda en `Cambios` con su regla.
- **[F4] Oraciones largas:** 15 se partieron en unidades de ≤ 15 palabras (Por_revisar) y 2 se descartaron (QCH-0520: datos administrativos de 2020; QCH-0544: cortada en la fuente a 255 caracteres). Las piezas solo llevan borrador si es un trozo **literal** del borrador original (el script lo comprueba); si no, quedan sin borrador.
- **[F4] Varias celdas del unificado están cortadas a 255 caracteres** (QCH-0478, QCH-0483, QCH-0544): defecto de la fuente. Al partirlas se completó la idea en español.
- **[F4] Notas entre paréntesis** («(hablando de otra persona)», «(tórax)», «(deseo de comer)») se quitan del español porque no se leen en voz alta. Cuando cambiaban el sentido («Tiene que quedarse en el hospital (hablando de otra persona)»), se reescribió con el pronombre («Él tiene que quedarse…», Por_revisar).
- **[F4] Coletilla «¿sí o no?»** al final de preguntas (indicación al entrevistador) se quita.
- **[F4] Léxico:** van a `Lexico` las filas médicas de 1 palabra y las de 2–3 palabras de secciones de vocabulario que no son preguntas. Prioritarias = categorías «Signos y síntomas», «Cuerpo humano», «Enfermedades…», «Fluidos…», «Funciones…». Reciben IDs `LEX-0001…` (decisión propia; §8.1 solo define GEN/CLI).
- **[F4] Duplicados exactos (mismo español normalizado):** queda el de mejor borrador; entre dominios gana el médico («Buenos días», «¿Cuántos años tienes?» del Principito/Grupo 2 se descartan a favor de las del unificado). Los otros borradores distintos quedan en `Origen` (Otros_borradores) y en QA (DUP/BAJA).
- **[F4] Casi duplicados:** además de polaridad y números, pregunta y afirmación nunca son paráfrasis («¿Le duele la cabeza?» ≠ «Me duele la cabeza.»).
- **[F4] Ortografía mecánica (§10.3)** solo cuando no es préstamo ni nombre propio; la escritura castellana (c/qu/j/hu) solo se cambia si la palabra resultante existe en el léxico de referencia (así no se inventan palabras: «mayllijunayki» queda marcado en QA, no se «corrige» a algo inexistente). Fuentes oficiales chanka: tal cual.
- **[F4] Registro de IDs** `02_maestro/ids.csv` (uid → ID): un uid nunca cambia de ID entre corridas; las filas nuevas toman el siguiente número libre. Mientras nada se envió al traductor, el registro se regeneró desde cero para que los IDs queden correlativos.
- **[F4] Avisos de QA ajustados tras revisar la pestaña** (falsos positivos que ya no salen, con prueba en `test_qa.py`): «nada» (verbo nadar) no cuenta como negación; ordinales y compuestos se comparan por componentes («catorce» = chunka tawayuq; «segundo piso» = iskay); «cuarto» no es número; si el español ofrece «¿poco o mucho?» no hay contradicción; la sugerencia de transcripción solo propone palabras completas frecuentes del léxico. Negación ausente pasa a MEDIA (el quechua puede expresarla de otro modo).

## F5 – Llenar huecos

- **[F5] B01 curado a mano** (`scripts/datos/plan_b01.yaml`): una consulta completa de dolor de barriga (paciente mujer de 20 años de Ayacucho), con las 6 etapas de §11.2: Inicio 10, Motivo 8, Caracterizar 14, Síntomas asociados 10, Examen físico 7, Explicación/plan/cierre 11 = 60 (32 médico / 28 paciente). Esqueleto con frases del manual SOCEMURP; 23 líneas nuevas en español (22 del paciente y «¿Entendiste lo que tienes que hacer?» del médico, que no existía en el corpus).
- **[F5] B02–B05 por tema** (`scripts/plan_medico.py`), en el orden por defecto de §11.2: B02 fiebre, respiratorio, digestivo, urinario, antecedentes básicos (medicamentos, alergias), niño enfermo (fiebre, diarrea, vómitos: «¿Su niño puede beber o mamar?»), embarazo («¿Estás embarazada?», que antes quedaba en B05); B03 pérdida de conocimiento, dolor de pecho, falta de aire, embarazo con señales de alarma (sangrado, líquido, el bebé se mueve menos, hinchazón), sangrados, tratamiento, seguimiento, tranquilizar; B04 cabeza/nervios, huesos, ojos/oídos, otros síntomas, examen físico, diagnóstico; B05 salud reproductiva, anticoncepción, salud mental, violencia (frases neutras), promoción, hospitalización, antecedentes y entorno. En cada tema: primero preguntas y luego mejor borrador; reparto en ronda para que cada tema tenga voz. 30 frases del médico por bloque.
- **[F5] Datos de morbilidad:** se buscó en la web el ranking de consulta externa de Ayacucho/Apurímac/Huancavelica (MINSA/CDC). No se encontró un ranking regional publicado en línea; solo cifras regionales de IRA (Diresa Ayacucho, ~25 000 casos de IRA a la semana 18 de 2024, según elbuho.pe) y el ranking nacional de consulta externa (Rev. Med. Herediana). Se usó el orden por defecto de §11.2, que pone respiratorio y digestivo primero (B02), coherente con esos datos.
- **[F5] Respuestas del paciente** (`scripts/datos/respuestas_paciente.yaml`): 1 por pregunta (a veces 2), en español peruano sencillo; también respuestas breves a algunas indicaciones o diagnósticos («¿Por eso me arde al orinar?»). 111 filas en B02–B05 (más 22 del paciente en B01). Ninguna repite otra frase del corpus (F5 lo controla y con `--estricto` no escribe nada si hay repetidas o preguntas sin respuesta).
- **[F5] Oraciones generales redactadas por Claude** (`scripts/datos/oraciones_generales.yaml`, pool `g_claude`), a requisito del proyecto («el 70 % general en distintos tiempos para que aprenda el modelo»; «puedes redactar algunas para enviarlas al traductor»): 375 oraciones cortas de vida cotidiana andina, solo en español, en 10 grupos (pasado -rqa-, pasado narrativo/«dicen que», futuro, progresivo, pasado habitual, imperativo, condicional, preguntas, subordinadas, derivación verbal). El quechua lo pone el traductor. Quedan con Estado Por_revisar.
- **[F5] Frases portadoras** (`scripts/datos/frases_portadoras.yaml`): 9 dentro de B03–B05 y 20 más que quedan en el corpus para bloques futuros; cada una enlazada a su palabra en `Lexico` (columna Frase_portadora).
- **[F5] Rol de las filas nuevas**: lo pone Claude (Paciente / Médico), no la heurística. Quien responde puede ser el acompañante (p. ej. la mamá).
- **[F5] Excluidas a mano** del plan QCH-0588 «¿Esta su hijo o hija o la señora gestante?» (redacción confusa) y QCH-0607 «¿Miras bien?» (mismo borrador que «¿Ves bien?»; en el mismo bloque se contradecían). Siguen en el corpus.
- **[F5] El plan médico se calcula en F5** (para saber qué preguntas necesitan respuesta) y F6 lo usa tal cual (columnas Plan_bloque / Plan_unidad / Plan_orden del checkpoint F5).

## F6 – Priorización y bloques

- **[F6] Bloques planificados: 5** (B01–B05), los 5 con Word y Excel (se solicitaron todos). Límite: la parte general de las fuentes (739 tras la limpieza) más las 375 redactadas por Claude; con el tope de 35 ejercicios por bloque no alcanza para un sexto bloque (quedan 14 redactadas y 400 ejercicios). La parte médica tiene material de sobra (840 frases sin asignar), pero cada bloque necesita voz del paciente redactada.
- **[F6] Selección voraz (§11.1)** con cobertura **dentro de cada bloque** (el conjunto cubierto se reinicia en cada bloque, para que cada bloque sea por sí mismo variado). Puntaje = (3 × sufijos nuevos + 1 × bigramas nuevos + 0.5 × palabras nuevas) ÷ (palabras del quechua)^0.5. Empates: Principito > frases variadas > ejercicios, luego la más corta. Determinista (sin azar).
- **[F6] B01 general con oraciones de ≤ 12 palabras** en español (§11.1).
- **[F6] Cuotas de la parte general** (`config.yaml` → `general.cuotas_por_bloque`): Principito ~35, frases variadas ~70, **al menos 40 oraciones redactadas por Claude en varios tiempos** y como máximo 35 ejercicios del Grupo 2 (todos en presente). Si un origen se acaba, se completa en el orden Principito → frases variadas → redactadas → ejercicios. Resultado (Principito / frases variadas / ejercicios / redactadas): B01 35/65/0/40, B02 35/56/9/40, B03 34/0/35/71, B04 0/0/35/105, B05 0/0/35/105. El mínimo era 25 y se subió a 40 porque con 25 B02 quedaba con 76 % de la parte general en presente (medido sobre el verbo en español, igual para todas las filas).
- **[F6] Mezcla de tiempos resultante** (parte general, verbo en español): presente 57 % / 65 % / 55 % / 45 % / 44 % en B01–B05; el resto pasado (12–24 %), futuro (6–15 %), progresivo (5–10 %), condicional e imperativo. F7 exige ≤ 65 % de presente por bloque.
- **[F6] Sublotes:** cada unidad médica (pregunta + respuestas) va entera en el sublote donde empieza (15 por sublote); por eso hay sublotes de 34+16 o 36+14. La parte general se reparte **por origen** en ronda entre los 4 sublotes (así los ejercicios no se juntan en un sublote) y dentro del sublote se mezclan los orígenes y se intercalan entre las unidades médicas.
- **[F6] Control (D7, activo):** 15 filas de B01 con borrador (10 generales + 5 médicas de buena calidad, calidad ≤ 4), repartidas entre los 4 sublotes con semilla fija 657. Van con la celda Quechua vacía y **sin aviso** en Observaciones (el aviso podría revelar el borrador). No se elige una fila que tenga una «hermana» con borrador visible en la misma entrega B01+B02 (quechua ≥ 75 % o español ≥ 85 % parecido), porque el traductor vería casi la misma solución. Tampoco «Mi tía hace chicha punta» (`control.excluir_codigos`): sin borrador, «punta» no se entiende.
- **[F6] Test_sugerido (P1):** 20 filas por bloque (14 generales proporcionales a cada origen + 3 pares completos pregunta/respuesta), sin tocar las de control ni filas con una casi gemela (≥ 85 %) en los bloques. Semilla fija. Todo sigue con Split = train.
- **[F6] Prioridad** = número del bloque planificado (1–5); vacío si aún no tiene bloque.
- **[F6] Columnas extra en Corpus** (al final): Control, Responde_a, N_bloque. Origen lleva además Códigos_unidos, Otros_borradores, Propuestas_equipo, Parte_de, Evidencia_P6, Fuente_detalle.
- **[F6] Estados:** Borrador, Sin borrador, Por_revisar, Enviado, Validado, Grabado (lista desplegable). «Enviado» se pone con `06_importar_traductor.py BXX --marcar-enviado` al mandar el Word (queda en Cambios).
- **[F6] Bloques congelados:** un bloque con filas Enviado/Validado/Grabado (o listado en `bloque.congelados`) ya no se rearma: f6 copia su composición, N°, sublotes, control y test del maestro anterior y no regenera su Word ni su Excel. Si una de sus filas desaparece del corpus, f6 se detiene y lo dice.
- **[F6] Word del traductor:** A4 horizontal, Calibri 11, instrucciones y tabla de ortografía en la página 1, una tabla por sublote con encabezado repetido y filas que no se parten entre páginas; **1 aviso ALTA por fila**, en letra 11, cursiva gris (§8.4: una línea breve). Instrucción de no usar Control de cambios. Sin fuentes, estados ni columnas técnicas.
- **[F6] Al regenerar el maestro** se conserva lo que ya devolvió el traductor (Quechua_validado, Estado, Traductor_metricas y los registros de 06 en Cambios) **solo si el español de la fila sigue igual**; si cambió, la fila vuelve a Por_revisar con una nota (hay que reenviarla). Del Excel de trabajo se conservan las casillas de grabación, Notas, % de edición y comentarios del traductor.
- **[F6] Marca de corrida completa:** el checkpoint F6 se escribe al final; si algo falla antes (p. ej. un Word abierto), la siguiente corrida rehace todo aunque no se pase `--forzar`.
- **[F6] Archivo devuelto por el traductor:** se guarda como `03_bloques/BXX/BXX_traductor_devuelto.docx` y se importa con `06_importar_traductor.py BXX`.
- **[F6] Métricas del traductor:** distancia de edición normalizada (Levenshtein, rapidfuzz) entre borrador y final: 0 = sin cambios; ≤ 0.5 = editado; > 0.5 = reescrito. Anclaje (D7): razón entre la distancia media con borrador y la distancia entre el borrador oculto y la traducción libre de las oraciones de control; < 0.5 = posible anclaje. Si reescribe más del 50 % → recomendar dejar de dar borradores.
- **[F6] Importación del traductor (06):** no importa un Word con Control de cambios sin aceptar; una fila cuyo español cambió el traductor no se valida (queda Por_revisar y su propuesta va a Cambios); si un sublote vuelve 100 % igual al borrador (≥ 10 filas) sus filas no se validan solas hasta confirmarlo (`--confirmar-sublotes`); todo lo importado queda en Cambios y reimportar no duplica registros.
- **[F6] Audios:** se buscan por nombre `{ID}_es.wav` / `{ID}_qu.wav` en cualquier subcarpeta de `05_audio/`, sin distinguir mayúsculas; si el mismo nombre aparece en dos carpetas, se avisa. Duración razonable: 0.4–20 s y no más de 2 s por palabra (si dura más de 3 s). Se revisan con el módulo `wave` de Python (no hizo falta instalar nada más).

## Revisión ultracode (§14.2), 15-oct-2026

Tres revisores independientes (A: datos y trazabilidad; B: bloques y archivos; C: scripts y reproducibilidad) encontraron 39 hallazgos (H1–H39), ninguno que invalidara los datos. El verificador cruzado se detuvo por límite de uso; los hallazgos que reportaron dos revisores se dieron por confirmados. Todo lo corregido se probó (`test_qa.py`, `test_ida_vuelta.py`) y se regeneró la cadena completa 01 → f7.

| Hallazgo | Qué se hizo |
|---|---|
| H1 IDs que dependían de la posición en los YAML; quechua validado que podía quedar pegado a otra frase | El uid de toda fila redactada o partida lleva una huella del texto; f6 y 06 comparan el español antes de conservar o validar. Como nada se envió, el registro de IDs se rehízo desde cero (el anterior quedó en `02_maestro/checkpoints/ids_antes_revision_20261015.csv`): **los IDs cambiaron respecto de los archivos del 14-oct.** |
| H2, H6, H7 importación (Control de cambios, control con distancia 0, Word devuelto sin tocar) | 06 reescrito (ver F6). |
| H3 regenerar borraba lo del equipo; 06 sin rastro | Se conservan columnas del equipo y registros de 06; 06 escribe en Cambios. |
| H4 B01/B02 casi todo en presente | Mínimo de 40 oraciones redactadas en varios tiempos por bloque; F7 lo controla (≤ 65 % presente). |
| H5 bloques enviados no se congelaban | Congelado automático (ver F6). |
| H8 reintento tras un fallo | Checkpoint F6 al final. |
| H9 parámetros fijos en el código | A `config.yaml`: médico por bloque, largo máximo, calidad del control, umbrales de 02/06/08, avisos por fila, formato de audio. |
| H10, H17, H25, H26 reportes y maestro | REVISION apunta al archivo correcto y muestra el borrador de las filas adaptadas; Bloques separa redactadas generales/médicas y calcula «Sin asignar»; LEEME describe todas las pestañas y el prefijo LEX-. |
| H11, H12, H29 cifras desactualizadas | Se regeneraron INVENTARIO, EDA, ENTREGA, PROGRESO y estas decisiones con las cifras de la corrida final. |
| H13 frase repetida entre bloques | F5 compara las frases nuevas con todo el corpus; F7 controla que ningún español se repita en los bloques. |
| H14, H22 erratas y frases poco naturales | 9 erratas nuevas (`erratas_es.yaml`), 27 adaptaciones (`adaptaciones_es.yaml`, Por_revisar) y 9 fragmentos o frases inoportunas descartadas (`descartes_es.yaml`, nuevo). No se cambió el calco «no + una» de algunos ejercicios («Yo no leo una revista»): es opcional y la coordinación del proyecto decide. |
| H15, H23, H24, H27 avisos de QA | Préstamos de fuentes oficiales, médicos o que repiten un sustantivo del español → BAJA; sin pista «(de …)»; sugerencias de transcripción más prudentes; aviso cuando el equipo marcó el borrador como dudoso; 3 avisos puestos a mano (`avisos_manuales.yaml`). |
| H16, H28, H34 duplicados | La clave conserva la ñ («Año» ≠ «Ano»); el paréntesis del léxico se mantiene; no se agrupan frases con quechua distinto; las oraciones redactadas no pasan por el filtro de casi duplicados. |
| H18 ejercicios juntos en un sublote | Reparto por origen. |
| H19, H39 respuestas contradictorias o sin Responde_a | 8 respuestas corregidas (caso de B01 sin «dolor que se mueve a la derecha», medicamentos, sangre, gusanos, pareja), «Responde_a» en B01, QCH-0607 excluida. |
| H20, H37 control con hermanas; test con gemelas | Ver F6. |
| H21 temas faltantes de §11.2 | Niño enfermo y embarazo en B02; embarazo con señales de alarma en B03; las respuestas que dejaban al paciente preguntando dosis sin respuesta se cambiaron. |
| H30–H33, H35, H36, H38 scripts y pruebas | `--estricto` no escribe nada; `00_huella_fuentes --forzar` no pisa una huella distinta sin `--aceptar-cambios`; F7 corre las pruebas en el momento y su pie depende de lo que hizo; 08 avisa audios repetidos; pruebas nuevas en `test_qa` y `test_ida_vuelta`; rutas relativas iguales en 06–08; mezcla de tiempos medida igual en todos los bloques. |

## Valores por defecto usados (§4)

| # | Valor usado | Dónde se ve |
|---|---|---|
| P1 | Todo `Split = train`; `Test_sugerido = Sí` en 20 filas por bloque (10 %, estratificado). | Corpus, Detalle, Resumen |
| P2 | Fecha desconocida → B01 y B02 listos para enviar ya (D5); por requisito del proyecto, también B03–B05 tienen archivos. | `03_bloques/B01` … `B05` |
| P3 | Collao: 3 vocales (alfabeto oficial MINEDU) por defecto; la coordinación lo definirá después (3 o 5, Academia Mayor de la Lengua Quechua). Se cambia con `variedad.vocales`. | Página 1 del Word, `config.yaml` |
| P4 | AmericasNLP **no** se usa (es chanka; solo su lado español sirve como léxico español). Para pasar de 5 bloques: fuentes collao nuevas (`FUENTES_COLLAO.md`) o más oraciones redactadas. | ENTREGA |
| P5 | WAV, 16 kHz, mono, 16 bits (en `config.yaml` y en la guía); falta confirmarlo con el equipo de modelo. | GUIA_GRABACION, 08_manifest |
| P6 | Ya no aplica desde el cambio a collao (del Grupo 2 solo se usa el español). Antes: verificado que no eran ejemplos del diccionario MINEDU (2 de 669). | Origen |
| P7 | Audios de Allin Kawsay no se usan (no hay `.mp3` en la carpeta). | INVENTARIO |


## Mantenimiento de documentación y etiquetas (2026-10-16)

- Se generalizaron las referencias personales a la coordinación del proyecto. El estado y la columna de revisión se denominan `Por_revisar`, y el informe es `REVISION.md`.
- Se conservaron las oraciones del corpus, los identificadores, las fórmulas, las cuotas y las reglas de procesamiento. En la fuente `Corpus_Equipos (1).xlsx` solo se generalizó la celda de coordinación de la hoja de equipos.
- Se actualizan únicamente las huellas de los dos documentos de estrategia y de esa fuente para reflejar este cambio autorizado de presentación.
