"""Herramientas para los borradores en quechua: léxico de referencia, sufijos, detectores (§12) y
normalización ortográfica mecánica (§10.3).

IMPORTANTE: Claude no es hablante de quechua chanka. Todo lo que sale de aquí son SOSPECHAS para que el
traductor sepa dónde mirar, nunca correcciones válidas. Los únicos cambios automáticos son los ortográficos
mecánicos de §10.3 y se registran en la pestaña Cambios.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from functools import lru_cache

from comun import asegurar_dir, escribir_json, fuente, ruta, sin_tildes, texto
import fuentes as F

# ------------------------------------------------------------------ alfabeto y tokens

RE_TOKEN_QU = re.compile(r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü'’]+")
ALFABETO_CHANKA = set("achiklmnñpqrstuwy")          # ch, ll como dígrafos; sin e/o (§10.3)
LETRAS_ESPANOLAS = set("bdefgjovxzc")                # fuera del alfabeto (c solo vale dentro de "ch")


def tokens_qu(s: str) -> list[str]:
    return [t.replace("’", "'") for t in RE_TOKEN_QU.findall(texto(s))]


def norm(t: str) -> str:
    return sin_tildes(t.lower().replace("’", "'")).replace("'", "") if t else ""


def norm_ñ(t: str) -> str:
    """Minúsculas sin tildes, conservando ñ (sin_tildes la quita) y sin apóstrofos."""
    t = t.lower().replace("’", "'").replace("'", "")
    return "".join("ñ" if c == "ñ" else sin_tildes(c) for c in t)


# ------------------------------------------------------------------ sufijos (§11.1)

SUFIJOS_CATEGORIA = {
    "Nominales": ["kuna", "y", "yki", "n", "nchik", "yku", "ykichik", "nku", "ta", "man", "pi", "manta", "wan",
                  "paq", "pa", "p", "kama", "rayku", "hina", "nta", "yuq", "ntin"],
    "Persona verbal": ["ni", "nki", "n", "nchik", "yku", "nkichik", "nku", "wa", "su", "yki"],
    "Tiempo/aspecto/modo": ["chka", "rqa", "sqa", "saq", "nqa", "sun", "man", "waq", "y", "ychik", "chun"],
    "Derivativos": ["chi", "ku", "mu", "pu", "ri", "yku", "naku", "ysi", "pa"],
    "Nominalizadores": ["q", "sqa", "na", "y"],
    "Subordinadores": ["spa", "pti", "stin"],
    "Enclíticos": ["mi", "m", "si", "s", "cha", "chu", "taq", "qa", "pas", "pis", "lla", "ña", "raq", "ya", "puni"],
}
SUFIJOS = sorted({s for v in SUFIJOS_CATEGORIA.values() for s in v}, key=len, reverse=True)
RAICES_CORTAS = {"ka", "ri", "qu", "ni", "pi", "ma", "may", "ima", "pay", "kay", "chay", "wak", "huk", "uma", "ñan"}
RE_SOLO_CHANKA = re.compile(r"^[achiklmnñpqrstuwy]+$")


@lru_cache(maxsize=None)
def segmentar(palabra: str) -> tuple[str, tuple[str, ...]]:
    """Segmentación heurística: quita sufijos desde el final (el más largo primero) hasta llegar a una raíz
    conocida o a una raíz de 3+ letras. Devuelve (raíz, sufijos en orden de aparición). Es aproximada."""
    w = norm_ñ(palabra)
    raices = lexico()["raices"]
    sufs: list[str] = []
    while len(sufs) < 7:
        if w in raices and sufs:
            break
        hecho = False
        for s in SUFIJOS:
            if w.endswith(s):
                resto = w[: -len(s)]
                if len(resto) >= 3 or resto in RAICES_CORTAS:
                    sufs.append(s)
                    w = resto
                    hecho = True
                    break
        if not hecho:
            break
    return w, tuple(reversed(sufs))


def unidades_cobertura(qu: str) -> dict[str, set[str]]:
    """Unidades para la selección voraz (§11.1): sufijos, bigramas de letras y palabras."""
    sufijos, bigramas, palabras = set(), set(), set()
    for t in tokens_qu(qu):
        w = norm_ñ(t)
        if not w or es_prestamo_o_propio(t)[0]:
            continue
        palabras.add(w)
        _, sufs = segmentar(w)
        sufijos.update(f"-{s}" for s in sufs)
        ww = f"#{w}#"
        bigramas.update(ww[i:i + 2] for i in range(len(ww) - 1))
    return {"sufijo": sufijos, "bigrama": bigramas, "palabra": palabras}


# ------------------------------------------------------------------ léxicos de referencia


def _tokens_texto(t: str) -> list[str]:
    return [norm_ñ(x) for x in RE_TOKEN_QU.findall(t)]


@lru_cache(maxsize=1)
def lexico() -> dict:
    """Léxico quechua (palabras, raíces, raíces derivadas) y léxico español, con caché en disco."""
    cache = asegurar_dir(ruta("checkpoints") / "cache") / "lexicos.json"
    firma = {k: fuente(k).stat().st_size for k in ["minedu_pdf", "mincul_pdf", "afiche_pdf", "diabetes_qu_pdf"]}
    firma["americasnlp"] = sum(p.stat().st_size for p in fuente("americasnlp_dir").rglob("*") if p.is_file())
    if cache.exists():
        d = json.loads(cache.read_text(encoding="utf-8"))
        if d.get("firma") == firma:
            return {"qu": set(d["qu"]), "qu_frec": d["qu_frec"], "raices": set(d["raices"]), "es": set(d["es"])}
    A = F.americasnlp()
    frec = Counter()
    for nombre in ["train (JW300)", "dict (MINEDU + Dict_misc)"]:
        for linea in A.get(nombre, {}).get("qu", []):
            frec.update(_tokens_texto(linea))
    pdf_qu = Counter()
    for clave in ["minedu_pdf", "mincul_pdf", "afiche_pdf", "diabetes_qu_pdf"]:
        for pag in F.texto_pdf(clave):
            pdf_qu.update(_tokens_texto(pag))
    # Solo formas escritas con el alfabeto chanka: así las palabras españolas de los PDF (y los préstamos con e/o
    # de JW300) no cuentan como quechua conocido.
    qu = {w for w, n in frec.items() if n >= 2 and RE_SOLO_CHANKA.match(w)} | \
         {w for w, n in pdf_qu.items() if n >= 1 and RE_SOLO_CHANKA.match(w)}
    # raíces: lemas del diccionario MINEDU (PDF) + entradas de una palabra de Dict_misc / MINEDU (AmericasNLP)
    raices = set()
    pat = re.compile(r"^([A-ZÑ][a-zñ' ]{1,30}?)\.\s*(?:\d\.\s*)?\(([a-z]{1,3})\)")
    for pag in F.texto_pdf("minedu_pdf"):
        for l in pag.replace("\r", "\n").split("\n"):
            m = pat.match(l.strip())
            if m:
                for w in m.group(1).split():
                    w = norm_ñ(w)
                    raices.add(w)
                    if w.endswith("y") and len(w) > 3:
                        raices.add(w[:-1])          # verbo: raíz sin -y
    for linea in A.get("es-quy/dict_misc", {}).get("qu", []):
        toks = _tokens_texto(linea)
        if len(toks) == 1:
            w = toks[0]
            raices.add(w)
            if w.endswith("y") and len(w) > 3:
                raices.add(w[:-1])
    raices = {r for r in raices if len(r) >= 2}
    # Español: solo palabras que aparecen alguna vez en minúscula (así no entran nombres propios como «Norton»).
    es = set()
    re_es = re.compile(r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü]+")
    lineas_es = [l for nombre in ["train (JW300)", "dict (MINEDU + Dict_misc)", "dev (sureño estándar)", "test (solo español)"]
                 for l in A.get(nombre, {}).get("es", [])] + F.texto_pdf("diabetes_es_pdf")
    for linea in lineas_es:
        es.update(norm_ñ(x) for x in re_es.findall(linea) if x[:1].islower())
    datos = {"firma": firma, "qu": sorted(qu), "qu_frec": {w: frec[w] + pdf_qu[w] for w in qu}, "raices": sorted(raices),
             "es": sorted(es)}
    escribir_json(cache, datos)
    return {"qu": qu, "qu_frec": datos["qu_frec"], "raices": raices, "es": es}


def conocida(w: str) -> bool:
    """¿La palabra (o alguna de sus raíces tras quitar sufijos) aparece en el léxico de referencia?"""
    lx = lexico()
    w = norm_ñ(w)
    if w in lx["qu"] or w in lx["raices"]:
        return True
    raiz, sufs = segmentar(w)
    if raiz in lx["raices"] or (raiz in lx["qu"] and len(raiz) >= 3):
        return True
    # también vale si alguna forma intermedia existe como palabra
    actual = raiz
    for s in sufs:
        actual += s
        if actual in lx["qu"] and len(actual) >= 4:
            return True
    return False


# ------------------------------------------------------------------ préstamos y nombres propios

PRESTAMOS_COMUNES = {
    "hospital", "pastilla", "pastillas", "doctor", "doctora", "posta", "enfermera", "inyeccion", "ampolla", "jarabe",
    "vacuna", "misa", "kuchara", "plato", "papel", "papil", "jabon", "jabun", "tuwalla", "semana", "simana", "minuto",
    "minutos", "hora", "ura", "medicina", "remedio", "suero", "analisis", "examen", "operacion", "kama", "cama",
    "covid", "coronavirus", "alcohol", "cerveza", "trago", "fruta", "frutakuna", "arroz", "arrus", "azucar", "asukar",
    "sal", "mascarilla", "termometro", "presion", "diabetes", "diabetis", "glucosa", "insulina", "hipoglicemia",
    "emergencia", "establecimiento", "salud", "receta", "sulfato", "ferroso", "condon", "regla", "anillo", "pulsira",
    "jeringa", "dosis", "litro", "kilo", "gramo", "metro", "mes", "domingo", "lunes", "martes", "sabado", "tumingu",
    "sabadu", "tiyanda", "platanu", "mantikilla", "futbul", "arku", "blukiku", "kuartu", "pisu", "misa",
    "yerro", "hierro", "yirru", "enema", "inyeccion", "pomada", "gotas",
    # préstamos médicos y de uso diario que no tienen otra forma corriente en quechua (aviso BAJA, no ALTA)
    "anemia", "infeccion", "inficcion", "radiografia", "ecografia", "tomografia", "tableta", "tabletas", "operacion",
    "hipertension", "tuberculosis", "prostata", "vesicula", "bronquios", "sonda", "yeso", "ambulancia", "seguro",
    "medico", "medicu", "segundo", "segundos", "minoto", "minutu", "urinaria", "orinaria", "desnutricion", "gastritis",
    "control", "kuntrul", "cuntrul", "vacunachi", "vacunachikunayki",
}
NOMBRES_PROPIOS = {"lince", "ayacucho", "ayakuchu", "lima", "huamanga", "wamanga", "victoria", "peru", "piru", "maria",
                   "dios", "diosninchik", "apurimac", "huancavelica", "cusco", "qusqu", "puno", "minsa", "essalud",
                   "diresa", "pedro", "juan", "jose", "rosa", "carmen", "andahuaylas", "abancay", "jehova", "hearts"}


@lru_cache(maxsize=None)
def _raiz_espanola(t: str) -> str:
    """Si la palabra empieza con una palabra (o raíz verbal) española, devuelve esa raíz.

    Los préstamos llevan sufijos quechuas pegados a una raíz española, a veces ya adaptada: «hospitalman»,
    «naceruspan» (nacer), «tocasayki» (tocar), «pechuyki» (pecho), «controlniki» (control). Se prueba cada prefijo
    de 4+ letras, también con la vocal final adaptada (u→o, i→e) y como verbo (+r, +ar, +er, +ir)."""
    es = lexico()["es"]
    w = norm_ñ(t)
    for L in range(len(w), 3, -1):
        p = w[:L]
        variantes = [p, p + "r", p + "ar", p + "er", p + "ir"]
        if "k" in p:                                   # préstamo con k adaptada: «ronkankichu» (roncar)
            pc = p.replace("k", "c")
            variantes += [pc, pc + "r", pc + "ar"]
        if p.endswith("u"):
            variantes.append(p[:-1] + "o")
        if p.endswith("i"):
            variantes += [p[:-1] + "e", p[:-1] + "er"]
        for v in variantes:
            if v in es and len(v) >= 4:
                return v
    return ""


def _formas(w: str):
    """La palabra y sus formas tras quitar sufijos quechuas uno a uno."""
    yield w
    actual = w
    for _ in range(6):
        for s in SUFIJOS:
            if actual.endswith(s) and len(actual) - len(s) >= 3:
                actual = actual[: -len(s)]
                yield actual
                break
        else:
            return


@lru_cache(maxsize=None)
def es_prestamo_o_propio(t: str, inicio_oracion: bool = False) -> tuple[bool, str]:
    """(True, motivo) si el token es un préstamo del español o un nombre propio (conserva su escritura)."""
    w = norm_ñ(t)
    if w in {"o", "y", "e", "u"}:
        return True, "conjunción española"
    if any(f in NOMBRES_PROPIOS for f in _formas(w)):
        return True, "nombre propio"
    if t[:1].isupper() and not inicio_oracion and len(t) > 2:
        if any(f in lexico()["es"] for f in _formas(w)):
            return True, "nombre propio"
        # Mayúscula a mitad de frase, sin sufijos quechuas y desconocida en el léxico → nombre propio («Annel»)
        if len(segmentar(w)[1]) <= 1 and not conocida(w):
            return True, "nombre propio"
    if any(f in PRESTAMOS_COMUNES for f in _formas(w)):
        return True, "préstamo común"
    if set(w) & set("bdfgvxz"):
        return True, "préstamo"                      # letras que el quechua no usa ni en escritura castellanizada
    tiene_letras_es = bool(re.search(r"[eo]|c(?!h)|j", w))
    if tiene_letras_es and _raiz_espanola(t):
        return True, "préstamo"
    return False, ""


# ------------------------------------------------------------------ normalización ortográfica mecánica (§10.3)

RE_GLOTAL = re.compile(r"(ch|k|q|p|t)['’]", re.I)
RE_ASPIRADA = re.compile(r"(chh|kh|ph|qh|th)", re.I)


def _con_mayus(orig: str, nuevo: str) -> str:
    return nuevo[:1].upper() + nuevo[1:] if orig[:1].isupper() else nuevo


def corregir_token(t: str, inicio: bool) -> tuple[str, list[str]]:
    """Aplica solo las reglas mecánicas de §10.3 a una palabra quechua. Devuelve (nuevo, reglas aplicadas)."""
    prestamo, _ = es_prestamo_o_propio(t, inicio)
    if prestamo:
        return t, []
    w = t.replace("’", "'")
    reglas = []
    # 1) glotalizadas y aspiradas
    nuevo = RE_GLOTAL.sub(lambda m: m.group(1), w)
    nuevo = RE_ASPIRADA.sub(lambda m: {"chh": "ch", "kh": "k", "ph": "p", "qh": "q", "th": "t"}[m.group(1).lower()], nuevo)
    if nuevo != w:
        reglas.append("sin glotalizadas/aspiradas")
    w = nuevo
    # 3) escritura castellana (solo si el resultado existe en el léxico de referencia: así no se inventan palabras)
    cand = w.lower()
    cand = re.sub(r"qu(?=[ei])", "k", cand)
    cand = re.sub(r"c(?!h)", "k", cand)
    cand = cand.replace("j", "h")
    cand = re.sub(r"hu(?=[aeiou])", "w", cand)
    if cand != w.lower():
        cand_v = cand.replace("e", "i").replace("o", "u")
        if conocida(cand_v) or conocida(cand):
            reglas.append("sin c/qu/j/hu castellanas")
            w = _con_mayus(w, cand)
    # 2) tres vocales
    if re.search(r"[eoéó]", w, re.I):
        trad = str.maketrans({"e": "i", "o": "u", "E": "I", "O": "U", "é": "i", "ó": "u", "É": "I", "Ó": "U"})
        w = w.translate(trad)
        reglas.append("tres vocales (e→i, o→u)")
    return w, reglas


def normalizar_ortografia(qu: str) -> tuple[str, list[str]]:
    """Normalización mecánica de toda la frase. Devuelve (nuevo, reglas aplicadas)."""
    s = texto(qu)
    if not s:
        return s, []
    reglas_tot: list[str] = []
    partes = re.split(r"([A-Za-zÁÉÍÓÚáéíóúÑñÜü'’]+)", s)
    inicio = True
    out = []
    for p in partes:
        if RE_TOKEN_QU.fullmatch(p or "#"):
            nuevo, reglas = corregir_token(p, inicio)
            out.append(nuevo)
            reglas_tot += reglas
            inicio = False
        else:
            out.append(p)
            if re.search(r"[.!?¿¡]", p):
                inicio = True
    return "".join(out), sorted(set(reglas_tot))


# ------------------------------------------------------------------ detectores (§12)

LEXICO_VARIEDAD = [
    (re.compile(r"^unu(ta|wan|pi|manta|lla|mi|m|n|y|yki|cha)?$"), "léxico «unu» (en chanka: yaku)"),
    (re.compile(r"^uhya"), "léxico «uhyay» (en chanka: upyay)"),
    (re.compile(r"^llank"), "léxico «llank'ay» (en chanka: llamkay)"),
    (re.compile(r"^p?unchay$"), "léxico «p'unchay» (en chanka: punchaw)"),
    (re.compile(r"^hayka[qc](manta|mantan)?n?$"), "«haykaq» (en chanka: haykap)"),
    (re.compile(r"^wisq"), "léxico «wisq'ay» (en chanka: wichqay)"),
    (re.compile(r"^maqchi"), "léxico «maqchiy» (collao; en chanka: mayllay)"),
    (re.compile(r"^wiqsa"), "«wiqsa» (cusqueño; en chanka: wiksa)"),
]
VALIDADOR_N = {"manan", "arin", "iman", "imaykin", "maypin", "pin", "haykan", "imaynan", "imatan", "maymantan",
               "haykacmantan", "haykaqmantan", "kaypin", "chaypin", "imaraykun", "imapin", "pitan", "imaykitan",
               "hinan", "chaytan", "kaytan", "imaynatan", "maytan", "imanan", "pipan"}


def detectar_variedad(qu: str) -> list[str]:
    hall = []
    for t in tokens_qu(qu):
        w = norm_ñ(t)
        if re.search(r"\w{2,}(sha|shia|sia)(n|ni|nki|nchik|nchis|yku|nkichik|nku|spa|q)(\w*)$", w) and not w.startswith("musia"):
            hall.append(f"progresivo -sha- en «{t}» (chanka: -chka-)")
        if w in VALIDADOR_N:
            hall.append(f"validador -n en «{t}» (chanka: -mi/-m)")
        if w.endswith("nchis") and w not in {"qanchis"} and not w.startswith("qanchis"):
            hall.append(f"inclusivo -nchis en «{t}» (chanka: -nchik)")
        if re.search(r"\w[qj]ti", w):
            hall.append(f"subordinador -qti-/-jti- en «{t}» (chanka: -pti-)")
        for pat, msg in LEXICO_VARIEDAD:
            if pat.search(w):
                hall.append(f"{msg} en «{t}»")
    return hall


def detectar_orto(qu: str) -> list[tuple[str, str]]:
    """(severidad, detalle) por letras fuera de la convención en palabras quechuas."""
    hall = []
    inicio = True
    for t in tokens_qu(qu):
        prestamo, _ = es_prestamo_o_propio(t, inicio)
        inicio = False
        if prestamo:
            continue
        w = t.lower()
        if RE_GLOTAL.search(w) or RE_ASPIRADA.search(w):
            hall.append(("ALTA", f"glotalizada/aspirada en «{t}»"))
        if re.search(r"[eoéó]", w):
            hall.append(("MEDIA", f"vocal e/o en «{t}»"))
        if re.search(r"c(?!h)|j|qu(?=[ei])|hu(?=[aeiou])", w):
            hall.append(("ALTA", f"escritura castellana (c/qu/j/hu) en «{t}»"))
        otras = set(norm(w)) & set("bdfgvxz")
        if otras:
            hall.append(("ALTA", f"letra fuera del alfabeto ({', '.join(sorted(otras))}) en «{t}»"))
    return hall


RE_RESTO_VERBAL = re.compile(r"^[aei]?(ni|nki|nchik|yku|nkichik|nku|spa|sqa|chka|rqa|ptin|pti|saq|sun|nqa|chun|y|n)(\W|$|[a-zñ]*)")
# terminaciones de un verbo español conjugado o en infinitivo («entienden», «comemos», «tomar»)
RE_VERBO_ES = re.compile(r"(an|en|amos|emos|imos|ais|eis|ar|er|ir|aba|aban|ia|ian)$")


def _palabra_en_espanol(t: str, es: str) -> str:
    """Palabra del español de la misma fila que el préstamo repite como SUSTANTIVO, sola o con sufijos quechuas (p. ej.
    «Asteroide», «baobab», «barbaskupa» ↔ «barbasco», «Radiografiata» ↔ «radiografía», «Ministrotam» ↔ «ministro»):
    eso es un préstamo esperable. No cuenta si el token es un VERBO español tal cual («entienden») ni si lleva sufijos
    verbales («piensani» ↔ «pienso»): eso suele ser traducción automática perezosa y se deja en ALTA."""
    w = norm_ñ(t)
    for e in re.findall(r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü]+", texto(es)):
        ne = norm_ñ(e)
        if w == ne:
            return "" if RE_VERBO_ES.search(ne) else e
        k = 0
        while k < min(len(w), len(ne)) and w[k] == ne[k]:
            k += 1
        if k >= 5 or (k >= 4 and k == len(ne)):
            if RE_RESTO_VERBAL.match(w[k:]) and not w[k:].startswith(("ta", "man", "pi", "wan", "kuna", "qa", "pa")):
                return ""
            return e
    return ""


def detectar_prestamos(qu: str, es: str = "") -> list[tuple[str, str]]:
    """Préstamos del español. ALTA solo si es una palabra española sin adaptar que el español de la fila no usa
    (señal de traducción automática: «piensani», «entienden»); BAJA si es un préstamo común o repite la palabra del español."""
    hall = []
    inicio = True
    for t in tokens_qu(qu):
        es_p, motivo = es_prestamo_o_propio(t, inicio)
        inicio = False
        if motivo in ("nombre propio", "conjunción española"):
            continue
        if motivo == "préstamo común":
            hall.append(("BAJA", f"préstamo común «{t}»"))
        elif motivo == "préstamo":
            igual = _palabra_en_espanol(t, es)
            if igual:
                hall.append(("BAJA", f"préstamo que repite la palabra del español «{igual}»"))
            else:
                hall.append(("ALTA", f"posible préstamo del español «{t}»"))
    return hall


def _variantes(w: str):
    letras = "achiklmnñpqrstuwy"
    vistos = set()
    for i in range(len(w) + 1):
        for c in letras:
            yield w[:i] + c + w[i:], f"falta «{c}»"
    for i in range(len(w)):
        yield w[:i] + w[i + 1:], f"sobra «{w[i]}»"
    if "y" in w:
        for m in re.finditer("y", w):
            yield w[:m.start()] + "ll" + w[m.end():], "y por ll"
    for a, b in [("o", "u"), ("e", "i")]:
        if a in w:
            yield w.replace(a, b), f"{a} por {b}"


@lru_cache(maxsize=None)
def sugerencia_transcripcion(t: str) -> str:
    """Si la palabra no está en el léxico pero una variante de 1 edición sí, devuelve la sugerencia.
    Caso especial (yeísmo al transcribir de oído): aunque la palabra exista, si la forma con «ll» es mucho
    más frecuente («tuyu» → «tullu»), también se sugiere."""
    lx = lexico()
    w = norm_ñ(t)
    if len(w) < 3:
        return ""
    if "y" in w[:-1]:
        f_w = lx["qu_frec"].get(w, 0)
        for m in re.finditer("y", w[:-1]):
            v = w[:m.start()] + "ll" + w[m.end():]
            f_v = lx["qu_frec"].get(v, 0)
            if f_v >= 20 and f_v >= 10 * max(f_w, 1):
                return f"«{t}» → ¿«{v}»? (y por ll; «{v}» es mucho más frecuente)"
    if conocida(w):
        return ""
    # Solo los errores típicos de transcribir de oído (§6): «y» por «ll» («siyu» → «sillu»), letra inicial que falta
    # («llinllachu» → «allinllachu») y «r» final que falta («yawa» → «yawar»). Otras ediciones (insertar o quitar letras en
    # medio) proponían formas equivocadas («qusqay» → «qusay», «churasayki» → «churasqayki») y ya no se sugieren.
    candidatos = [(w[:m.start()] + "ll" + w[m.end():], "y por ll") for m in re.finditer("y", w)]
    candidatos += [(c + w, f"falta «{c}» al inicio") for c in "achiklmnñpqrstuwy"]
    candidatos.append((w + "r", "falta «r» final"))
    mejor = ("", 0, "")
    for v, motivo in candidatos:
        frec = lx["qu_frec"].get(v, 0)
        if frec >= 3:
            puntaje = frec + (1000 if motivo == "y por ll" else 0)
            if puntaje > mejor[1]:
                mejor = (v, puntaje, motivo)
    return f"«{t}» → ¿«{mejor[0]}»? ({mejor[2]})" if mejor[0] else ""


def detectar_transcripcion(qu: str) -> list[str]:
    hall = []
    inicio = True
    for t in tokens_qu(qu):
        es_p, _ = es_prestamo_o_propio(t, inicio)
        inicio = False
        if es_p:
            continue
        w = norm_ñ(t)
        if re.match(r"^(st|sp|sk|tr|dr|bl|pl|kl|fl|gr|br|pr|kr)", w) or re.search(r"(rd|st[^a-z]?$|nd)", w):
            hall.append(f"grupo de consonantes del español en «{t}»")
            continue
        s = sugerencia_transcripcion(t)
        if s:
            hall.append(s)
    return hall


def detectar_oov(qu: str) -> list[str]:
    fuera = []
    inicio = True
    for t in tokens_qu(qu):
        es_p, _ = es_prestamo_o_propio(t, inicio)
        inicio = False
        if es_p or len(norm_ñ(t)) < 3:
            continue
        if not conocida(t):
            fuera.append(t)
    return fuera


# ------------------------------------------------------------------ alineación y sentido

# Números del español → componentes como se dicen en quechua ("catorce" = chunka tawayuq → {10, 4}).
NUM_ES = {"dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10,
          "once": 11, "doce": 12, "trece": 13, "catorce": 14, "quince": 15, "dieciseis": 16, "diecisiete": 17,
          "dieciocho": 18, "diecinueve": 19, "veinte": 20, "treinta": 30, "cuarenta": 40, "cincuenta": 50,
          "sesenta": 60, "setenta": 70, "ochenta": 80, "noventa": 90, "cien": 100, "ciento": 100, "mil": 1000,
          "segundo": 2, "segunda": 2, "tercero": 3, "tercera": 3, "tercer": 3, "quinto": 5, "quinta": 5}
# («cuarto» no se cuenta: casi siempre es la habitación)
NUMEROS_QU = {"2": ["iskay"], "3": ["kimsa"], "4": ["tawa"], "5": ["pichqa", "pisqa"], "6": ["suqta", "soqta"],
              "7": ["qanchis"], "8": ["pusaq"], "9": ["isqun", "isqon"], "10": ["chunka"], "100": ["pachak"],
              "1000": ["waranqa"]}
SUF_NUM = re.compile(r"^(kaq|ta|pi|man|manta|yuq|yuqta|ntin|chu|mi|m|lla|llata|wan|kama|niyuq|kuti|kutita|pa|qa|taq|ña|raq|y|yki|n)*$")
MARCAS_PREGUNTA_QU = re.compile(r"(chu|taq|tak)\b|\b(ima|may|pi|hayka|imayna|imarayku|mayqan|maymanta|maypi|pitaq|piwan|pim|imam)", re.I)


def _componentes(n: int) -> set[str]:
    if n <= 0:
        return set()
    if n <= 10 or n in (100, 1000):
        return {str(n)} if n != 1 else set()
    out = set()
    if n >= 1000:
        out |= {"1000"} | _componentes(n // 1000 if n // 1000 > 1 else 0) | _componentes(n % 1000)
        return out
    if n >= 100:
        out |= {"100"} | _componentes(n // 100 if n // 100 > 1 else 0) | _componentes(n % 100)
        return out
    decenas, unidades = divmod(n, 10)
    out.add("10")
    if decenas > 1:
        out.add(str(decenas))
    if unidades:
        out |= _componentes(unidades)
    return out


def numeros_es(es: str) -> set[str]:
    s = sin_tildes(texto(es).lower())
    out = set()
    for d in re.findall(r"\d+", s):
        out |= _componentes(int(d))
    for p, v in NUM_ES.items():
        if re.search(rf"\b{p}\b", s):
            out |= _componentes(v)
    return out


def numeros_qu(qu: str) -> set[str]:
    s = norm(texto(qu))
    out = set()
    for d in re.findall(r"\d+", s):
        out |= _componentes(int(d))
    for t in re.findall(r"[a-zñ]+", s):
        for k, palabras in NUMEROS_QU.items():
            for p in palabras:
                if t.startswith(p) and SUF_NUM.match(t[len(p):]):
                    out.add(k)
    return out


def detectar_alineacion(es: str, qu: str, cfg_qa: dict) -> list[tuple[str, str]]:
    hall = []
    es, qu = texto(es), texto(qu)
    if not es or not qu:
        return hall
    r = len(qu) / max(len(es), 1)
    if r < cfg_qa["ratio_longitud_min"] or r > cfg_qa["ratio_longitud_max"]:
        hall.append(("MEDIA", f"longitud quechua/español = {r:.2f} (fuera de [{cfg_qa['ratio_longitud_min']}, {cfg_qa['ratio_longitud_max']}])"))
    ne, nq = numeros_es(es), numeros_qu(qu)
    if (ne or nq) and ne != nq:
        hall.append(("ALTA", f"números distintos: español {sorted(ne, key=int) or '—'} vs quechua {sorted(nq, key=int) or '—'}"))
    if ("?" in es or "¿" in es) and "?" not in qu and not MARCAS_PREGUNTA_QU.search(norm(qu)):
        hall.append(("MEDIA", "pregunta en español sin marca interrogativa en quechua (-chu, -taq, ima-, pi-, may-, hayka-)"))
    return hall


RE_MUCHO = re.compile(r"\b(mucho|mucha|muchos|muchas|muy|bastante|harto|fuerte|intenso)\b")
RE_POCO = re.compile(r"\b(poco|poca|poquito|poquita|leve|suave)\b")
SENTIDO_REGLAS = [
    (RE_MUCHO, re.compile(r"\b(pisi|tumpa)"), "español dice «mucho» pero el quechua tiene «pisi/tumpa» (= poco)"),
    (RE_POCO, re.compile(r"\b(achka|ancha|anchata|nisyu|sinchi)"), "español dice «poco» pero el quechua tiene «achka/ancha» (= mucho)"),
    (re.compile(r"\b(mes|meses)\b"), re.compile(r"\bwata"), "español dice «mes» pero el quechua tiene «wata» (= año)"),
    (re.compile(r"\b(año|años|ano|anos)\b"), re.compile(r"\bkilla"), "español dice «año» pero el quechua tiene «killa» (= mes)"),
    (re.compile(r"\b(semana|semanas)\b"), re.compile(r"\b(wata|killa)"), "español dice «semana» pero el quechua tiene «wata/killa»"),
]


def detectar_sentido(es: str, qu: str) -> list[tuple[str, str]]:
    """(severidad, detalle). Contradicciones de cantidad/tiempo → ALTA; negación ausente → MEDIA (el quechua puede
    expresarla de otro modo)."""
    hall = []
    e, q = sin_tildes(texto(es).lower()), norm(texto(qu))
    if not e or not q:
        return hall
    for pe, pq, msg in SENTIDO_REGLAS:
        if pe.search(e) and pq.search(q):
            # "mes" junto con "killa" en quechua no es contradicción
            if "mes" in msg and re.search(r"\bkilla", q):
                continue
            if "«año»" in msg and re.search(r"\bwata", q):
                continue
            # si el español ofrece las dos opciones («¿poco o mucho?») no hay contradicción
            if (pe is RE_MUCHO and RE_POCO.search(e)) or (pe is RE_POCO and RE_MUCHO.search(e)):
                continue
            hall.append(("ALTA", msg))
    neg_es = re.search(r"\b(no|nunca|ni|tampoco|jamas)\b", e)          # «nada» se omite: suele ser el verbo nadar
    neg_qu = re.search(r"\b(mana|ama|manam|amam|manan|manachu|ni)\w*|chu\b", q)
    if neg_es and not neg_qu and not ("?" in es or "¿" in es):
        hall.append(("MEDIA", "el español es negativo pero el quechua no tiene mana/ama/-chu"))
    return hall
