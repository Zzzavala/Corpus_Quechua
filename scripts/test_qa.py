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

CASOS = [
    # (español, quechua, dominio, tipos que deben aparecer (al menos uno))
    ("Desde un mes me duele mucho mi estómago", "Qayna wata tumpallata wiksay nanachkan", "Médico", {"SENTIDO"}),
    ("No debes comer comida con mucha sal", "Amam pisi kachiyuq mikunata mikunkichu", "Médico", {"SENTIDO"}),
    ("¿Era mucho?", "¿Achkhachu karqa?", "Médico", {"ORTO"}),
    ("¿Estás bien?", "¿llinllachu kachkanki?", "Médico", {"TRANSCRIPCION", "OOV"}),
    ("¿Quién eres?", "¿Itaq kanki?", "Médico", {"TRANSCRIPCION", "OOV"}),
    ("En cada comida tienes que lavarte las manos.", "Makiykita sapa mikunapi mayllijunayki.", "Médico", {"ORTO"}),
    ("¿Cómo era tu dolor?", "¿Imaynatoq nanayniyki karqa?", "Médico", {"ORTO"}),
    ("¿Te duele?", "¿Nanasukichu?", "Médico", {"TRANSCRIPCION", "OOV"}),
    ("Pido perdón por el cordero.", "Carnerota pampachaykuway.", "General", {"PRESTAMO"}),
    ("Pienso en ti.", "Qampi piensani.", "General", {"PRESTAMO"}),
    ("Todos entienden.", "Lliwtam entienden.", "General", {"PRESTAMO"}),
    ("Es mi amistad.", "Amistadniymi.", "General", {"PRESTAMO"}),
    ("Mi dibujo.", "Dibujoyniyqa.", "General", {"PRESTAMO"}),
    ("Hueso", "tuyu", "Médico", {"TRANSCRIPCION", "OOV"}),
    ("Nariz", "ñorton", "Médico", {"ORTO"}),
    ("Plata", "qolqe", "Médico", {"ORTO"}),
    ("Huevo", "runto", "Médico", {"ORTO"}),
    ("Uña", "siyu", "Médico", {"TRANSCRIPCION", "OOV"}),
    ("Sangre", "yawa", "Médico", {"TRANSCRIPCION", "OOV"}),
    ("No es estándar", "stardin manchu", "Médico", {"PRESTAMO", "TRANSCRIPCION", "ORTO"}),
    ("Mil uno", "waranqa hukniyoq", "Médico", {"ORTO"}),
    ("¿Sabes escribir?", "qellqaytay yachankichu", "Médico", {"ORTO"}),
    ("¿Cómo estás?", "¿Imayna kashanki?", "Médico", {"VARIEDAD"}),
    ("¿Qué te duele?", "¿Imaykin nanan?", "Médico", {"VARIEDAD"}),
    ("No", "Manan", "Médico", {"VARIEDAD"}),
    ("Ropa", "p'acha", "Médico", {"ORTO"}),
    ("Mira", "qhaway", "Médico", {"ORTO"}),
    ("Nosotros", "ñoqanchis", "Médico", {"VARIEDAD", "ORTO"}),
    ("Cuando caminas", "purijtiyki", "Médico", {"VARIEDAD"}),
    ("Agua", "unu", "Médico", {"VARIEDAD"}),
    ("Tomar", "uhyay", "Médico", {"VARIEDAD"}),
    ("¡Bebo!", "¡Tomani!", "General", {"PRESTAMO"}),
]

# Falsos positivos encontrados al revisar la pestaña QA: estos NO deben marcar el tipo indicado.
NO_DEBEN = [
    ("Debe quedarse en casa por 14 días.", "Wasillaykipi qipakuy chunka tawayuq punchaw.", "ALINEACION"),
    ("Él sube al segundo piso.", "Pay iskay pisuman siqan.", "ALINEACION"),
    ("Dudo sobre los colores de su traje.", "Pachaykipa colorninmanta iskayrayani.", "ALINEACION"),
    ("¡Un día vi ponerse el sol cuarenta y tres veces!", "¡Huk punchawmi inti siqaykuyta tawa chunka kimsayuq kutita rikurqani!", "ALINEACION"),
    ("El pez nada en el agua.", "Challwa yakupi waytan.", "SENTIDO"),
    ("¿Poco, fuerte o leve?", "¿Pisitachu, sinchitachu?", "SENTIDO"),
    ("En cada comida tienes que lavarte las manos.", "Makiykita sapa mikunapi mayllikunayki.", "TRANSCRIPCION"),
]

NORMALIZACION = [
    ("p'acha", "pacha"), ("qhaway", "qaway"), ("achkha", "achka"), ("onqoy", "unquy"), ("hukniyoq", "hukniyuq"),
    ("qolqe", "qulqi"), ("wicsa", "wiksa"), ("jamuy", "hamuy"), ("huasi", "wasi"), ("¿Achkhachu karqa?", "¿Achkachu karqa?"),
    ("Ñuqa Lince nisqapi tiyani", "Ñuqa Lince nisqapi tiyani"), ("Ayacuchomanta kani", "Ayacuchomanta kani"),
    ("Sutiyqa Annel.", "Sutiyqa Annel."),
    ("Hospitalisakunayki.", "Hospitalisakunayki."), ("Lluqi pechoykita tocasayki.", "Lluqi pechoykita tocasayki."),
    ("¿Samanki hina o ruwanki hina?", "¿Samanki hina o ruwanki hina?"), ("¿Wawacha naceruspan waqarqa?", "¿Wawacha naceruspan waqarqa?"),
    ("Weqeyta waqastin.", "Wiqiyta waqastin."), ("inti seqaykuyta", "inti siqaykuyta"),
    ("hospitalman rini", "hospitalman rini"), ("Carnerota", "Carnerota"), ("Coronavirus unquymanta", "Coronavirus unquymanta"),
    ("Iskay minotollapas.", "Iskay minotollapas."),          # H23: préstamo, la regla de vocales no lo toca
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
