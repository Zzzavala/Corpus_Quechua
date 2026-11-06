"""Prueba de las reglas de QA y de la normalización mecánica con los casos conocidos de CLAUDE.md §6.

Uso: python scripts/test_qa.py   → imprime cada caso y falla (código 1) si alguno no sale marcado.
"""
from __future__ import annotations

import sys

import pandas as pd

from comun import clave_normalizada
from dedup import grupos_casi_duplicados
from qa import aviso_word, detectar_dup, revisar_fila
import quechua as Q

# Variedad objetivo: quechua COLLAO de Cusco (desde el 5-nov-2026). Los casos de §6 que eran «rasgos no chanka»
# (glotalizadas, -sha-, -n, -nchis, -qti-, unu, uhyay) ahora son lo CORRECTO; lo que se marca es lo chanka o boliviano.
CASOS = [
    # (español, quechua, dominio, tipos que deben aparecer (al menos uno))
    ("Desde un mes me duele mucho mi estómago", "Qayna wata tumpallata wiksay nanashan", "Médico", {"SENTIDO"}),
    ("No debes comer comida con mucha sal", "Aman pisi kachiyuq mikhunata mikhunkichu", "Médico", {"SENTIDO"}),
    ("¿Estás bien?", "¿llinllachu kashanki?", "Médico", {"TRANSCRIPCION", "OOV"}),
    ("En cada comida tienes que lavarte las manos.", "Makiykita sapa mikhunapi maqchijunayki.", "Médico", {"ORTO"}),
    ("¿Le duele el cuello?", "¿Kunkaiki nanan?", "Médico", {"ORTO"}),               # semivocal: kunkayki
    ("¿Duerme bien?", "¿Allyntachu puñunky?", "Médico", {"ORTO"}),                 # semivocal: allintachu, puñunki
    ("Estómago", "wicsa", "Médico", {"ORTO"}),
    ("Uno", "juk", "Médico", {"ORTO"}),                                             # j → h en Cusco
    ("Pido perdón por el cordero.", "Carnerota pampachaykuway.", "General", {"PRESTAMO"}),
    ("Pienso en ti.", "Qampi piensani.", "General", {"PRESTAMO"}),
    ("Todos entienden.", "Lliwtan entienden.", "General", {"PRESTAMO"}),
    ("Es mi amistad.", "Amistadniymi.", "General", {"PRESTAMO"}),
    ("Mi dibujo.", "Dibujoyniyqa.", "General", {"PRESTAMO"}),
    ("¡Bebo!", "¡Tomani!", "General", {"PRESTAMO"}),
    ("No es estándar", "stardin manchu", "Médico", {"PRESTAMO", "TRANSCRIPCION", "ORTO"}),
    # rasgos chanka o bolivianos (no son del quechua de Cusco)
    ("¿Cómo estás?", "¿Imaynam kachkanki?", "Médico", {"VARIEDAD"}),
    ("No", "Manam", "Médico", {"VARIEDAD"}),
    ("Nosotros", "ñuqanchik", "Médico", {"VARIEDAD"}),
    ("Cuando caminas", "puriptiyki", "Médico", {"VARIEDAD"}),
    ("Agua", "yaku", "Médico", {"VARIEDAD"}),
    ("Tomar", "upyay", "Médico", {"VARIEDAD"}),
    ("¿Cuántos años tienes?", "¿Machkha watayuqtaq kanki?", "Médico", {"VARIEDAD"}),
    ("Sangre", "llawar", "Médico", {"VARIEDAD"}),
]
# «e» y «o» solo son error con 3 vocales (P3: desde el 5-nov-2026 son 5)
if Q.VOCALES == 3:
    CASOS += [("¿Cómo era tu dolor?", "¿Imaynatoq nanayniyki karqa?", "Médico", {"ORTO"}),
              ("Plata", "qolqe", "Médico", {"ORTO"}),
              ("¿Sabes escribir?", "qellqaytay yachankichu", "Médico", {"ORTO"})]

# Lo que es correcto en collao NO debe marcarse (antes, con chanka, sí se marcaba).
NO_DEBEN = [
    ("¿Cómo estás?", "¿Imaynan kashanki?", "VARIEDAD"),
    ("No", "Manan", "VARIEDAD"),
    ("Nosotros", "ñuqanchis", "VARIEDAD"),
    ("Cuando caminas", "puriqtiyki", "VARIEDAD"),
    ("Agua", "unu", "VARIEDAD"),
    ("Tomar", "uhyay", "VARIEDAD"),
    ("Día", "p'unchay", "ORTO"),
    ("Mira", "qhaway", "ORTO"),
    ("Comida", "mikhuna", "ORTO"),
    ("¿Desde cuándo te duele?", "¿Hayk'aqmanta nanasunki?", "ORTO"),
    # falsos positivos de alineación y sentido que no deben volver
    ("Debe quedarse en casa por 14 días.", "Wasillaykipi qhipakuy chunka tawayuq p'unchay.", "ALINEACION"),
    ("Él sube al segundo piso.", "Pay iskay pisuman siqan.", "ALINEACION"),
    ("¡Un día vi ponerse el sol cuarenta y tres veces!", "¡Huk p'unchaymi inti siqaykuyta tawa chunka kimsayuq kutita rikurqani!", "ALINEACION"),
    ("El pez nada en el agua.", "Challwa unupi waytan.", "SENTIDO"),
    ("¿Poco, fuerte o leve?", "¿Pisitachu, sinchitachu?", "SENTIDO"),
]
if Q.VOCALES == 5:
    NO_DEBEN += [("¿Cómo era tu dolor?", "¿Imaynatoq nanayniyki karqa?", "ORTO"), ("Plata", "qolqe", "ORTO"),
                 ("Plata", "qolqe", "PRESTAMO"), ("¿Sabes escribir?", "qellqaytay yachankichu", "ORTO"),
                 ("Enfermedad", "onqoy", "PRESTAMO")]

TRES = Q.VOCALES == 3
NORMALIZACION = [
    # glotalizadas y aspiradas se conservan (alfabeto collao)
    ("p'acha", "p'acha"), ("qhaway", "qhaway"), ("p’unchay", "p'unchay"), ("mikhuy", "mikhuy"),
    # vocales según P3, j → h, semivocales
    ("onqoy", "unquy" if TRES else "onqoy"), ("hukniyoq", "hukniyuq" if TRES else "hukniyoq"), ("qolqe", "qulqi" if TRES else "qolqe"),
    ("jamuy", "hamuy"), ("Juk kutitachu", "Huk kutitachu"),
    ("¿Hayka killatac?", "¿Hayka killataq?"), ("seccsisunkichu", "seqsisunkichu"),      # «c» final y «cc» → q
    ("¿Kunkaiki nanan?", "¿Kunkayki nanan?"), ("Allyntachu puñunky?", "Allintachu puñunki?"), ("Taitaykiwan", "Taytaykiwan"),
    ("sonkoiykita", "sunkuykita" if TRES else "sonkoykita"), ("K’echaqtin", "K'ichaqtin" if TRES else "K'echaqtin"),
    # préstamos y nombres propios no se tocan (tampoco la «qu» castellana de un nombre)
    ("Ñuqa Lince nisqapi tiyani", "Ñuqa Lince nisqapi tiyani"), ("Cuscomanta kani", "Cuscomanta kani"),
    ("Sutiyqa Annel.", "Sutiyqa Annel."), ("Hospitalisakunayki.", "Hospitalisakunayki."),
    ("hospitalman rini", "hospitalman rini"), ("Carnerota", "Carnerota"), ("Coronavirus unquymanta", "Coronavirus unquymanta"),
    ("Iskay minotollapas.", "Iskay minotollapas."), ("hinatachu Yupanqui?", "hinatachu Yupanqui?"),
]

# Revisión ultracode (H15, H23, H24, H27): avisos que NO deben salir como ALTA en el Word.
SIN_ALTA = [
    # (español, quechua, oficial, tipo que no debe ser ALTA)
    ("Frota tus manos con jabón al menos veinte segundos.", "Makikita jabunwan qatuy iskay chunka segundo hinallapas.", True, "PRESTAMO"),
    ("Tienes anemia.", "Anemiawanmi kachkanki.", False, "PRESTAMO"),
    ("Tienes una infección.", "Infeccionniyuqmi kachkanki.", False, "PRESTAMO"),
    ("¿Le sacaron una radiografía?", "¿Radiografiata hurqurasunkichu?", False, "PRESTAMO"),
    ("El baobab es un árbol grande.", "Baobabqa hatun sachan.", False, "PRESTAMO"),
    ("Le llama Asteroide.", "Asteroide nispa sutichan.", False, "PRESTAMO"),
]

# Sugerencias de transcripción que la revisión encontró erradas (H24): no deben volver a proponerse.
SUGERENCIAS_MALAS = [("Qusqay", "qusay"), ("churasayki", "churasqayki"), ("qawasayki", "qawaspayki"), ("Awilu", "awiluy"),
                     ("uraykamun", "uraykamuni"), ("Kaypaq", "kallpaq"), ("Itaq", "nitaq")]


def main() -> int:
    fallos = 0
    print("== Detectores (§6) ==")
    for es, qu, dom, esperados in CASOS:
        av = revisar_fila(es, qu, dom)
        tipos = {t for t, _, _ in av}
        ok = bool(tipos & esperados)
        fallos += not ok
        print(f"[{'OK ' if ok else 'FALLA'}] «{qu}» → {sorted(tipos)}  " + " | ".join(f"{t}/{s}: {d}" for t, s, d in av if t in esperados)[:220])
    print("\n== Falsos positivos que no deben volver ==")
    for es, qu, tipo in NO_DEBEN:
        av = [x for x in revisar_fila(es, qu, "General") if x[0] == tipo]
        ok = not av
        fallos += not ok
        print(f"[{'OK ' if ok else 'FALLA'}] «{qu}» sin {tipo}" + ("" if ok else f" → {av}"))
    print("\n== DUP: mismo quechua para dos significados (QCH-0050) ==")
    df = pd.DataFrame([
        {"ID": "A", "Español": "¿Desde hoy nomás te duele?", "Quechua_borrador": "¿Kunallanmantachu nanasunki?"},
        {"ID": "B", "Español": "¿Es la primera vez que te duele?", "Quechua_borrador": "¿Kunallanmantachu nanasunki?"},
    ])
    d = detectar_dup(df, "ID")
    ok = len(d) == 2
    fallos += not ok
    print(f"[{'OK ' if ok else 'FALLA'}] {d}")
    print("\n== Normalización mecánica (§10.3) ==")
    for antes, esperado in NORMALIZACION:
        nuevo, reglas = Q.normalizar_ortografia(antes)
        ok = nuevo == esperado
        fallos += not ok
        print(f"[{'OK ' if ok else 'FALLA'}] «{antes}» → «{nuevo}» (esperado «{esperado}») {reglas}")

    def caso(nombre, ok, detalle=""):
        nonlocal fallos
        fallos += not ok
        print(f"[{'OK ' if ok else 'FALLA'}] {nombre} {detalle}")

    print("\n== Avisos que no deben ser ALTA (H15) ==")
    for es, qu, oficial, tipo in SIN_ALTA:
        av = [x for x in revisar_fila(es, qu, "Médico", oficial=oficial) if x[0] == tipo and x[1] == "ALTA"]
        caso(f"«{qu}» sin {tipo}/ALTA", not av, str(av) if av else "")
    print("\n== Sugerencias de transcripción erradas que no deben volver (H24) ==")
    for palabra, mala in SUGERENCIAS_MALAS:
        sug = Q.sugerencia_transcripcion(palabra)
        caso(f"«{palabra}» no sugiere «{mala}»", sug.lower() != mala, f"(sugiere «{sug}»)")
    print("\n== Aviso del Word: 1 línea, solo ALTA (H15, §8.4) ==")
    av = [("ORTO", "ALTA", "uno"), ("PRESTAMO", "ALTA", "dos"), ("OOV", "BAJA", "tres")]
    w = aviso_word(av, maximo=1)
    caso("aviso_word deja 1 aviso ALTA y avisa que hay más", w.startswith("Aviso:") and "uno" in w and "dos" not in w and "tres" not in w, f"«{w}»")
    caso("aviso_word vacío si no hay ALTA", aviso_word([("OOV", "BAJA", "x")]) == "", "")
    print("\n== Borrador marcado como dudoso por el equipo (H27) ==")
    av = revisar_fila("¿Tienen que curar sus heridas?", "¡Kiriykikunatam hampinanku!", "Médico",
                      estado_unificado="Revisar – duda de traducción")
    caso("Estado «Revisar – duda» → aviso SENTIDO/ALTA", any(t == "SENTIDO" and s == "ALTA" for t, s, _ in av), str(av)[:160])
    print("\n== Claves de duplicados (H16) y casi duplicados (§10.4) ==")
    caso("«Año» y «Ano» no son el mismo texto", clave_normalizada("Año") != clave_normalizada("Ano"))
    caso("«Adolescente» y «adolescente» sí", clave_normalizada("Adolescente.") == clave_normalizada("adolescente"))
    g = grupos_casi_duplicados(["¿Le duele la cabeza?", "Me duele la cabeza.", "Tengo 20 años.", "Tengo 30 años.",
                                "Ellos bajan al río.", "Ellos no bajan al río.", "Ellas bajan al río."], 80, 2)
    caso("pregunta ≠ afirmación, números distintos y negación no se agrupan", g[0][0] != g[1][0] and g[2][0] != g[3][0] and g[4][0] != g[5][0],
         str(g))
    g = grupos_casi_duplicados(["Ellos bajan al río.", "Ellas bajan al río."], 80, 2,
                               quechua=["Paykuna mayuman uraykunku.", "Paykuna mayuman uraykunku."])
    caso("mismo quechua dentro de un grupo → la segunda sobra", g[1][1] == 0, str(g))
    g = grupos_casi_duplicados(["El niño juega.", "Los niños juegan."], 70, 1,
                               quechua=["Qari warma pukllan.", "Warmakunam pukllanku."])
    caso("español parecido pero quechua distinto (singular/plural) → no se agrupan (H28)", g[0][0] != g[1][0], str(g))
    print(f"\nFallos: {fallos}")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
