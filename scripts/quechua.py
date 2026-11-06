"""Herramientas para los borradores en quechua COLLAO (Cusco–Puno): léxico de referencia, sufijos, detectores (§12)
y normalización ortográfica mecánica (§10.3).

IMPORTANTE: Claude no es hablante de quechua. Todo lo que sale de aquí son SOSPECHAS para que el traductor sepa dónde
mirar, nunca correcciones válidas. Los únicos cambios automáticos son los ortográficos mecánicos de §10.3 y se
registran en la pestaña Cambios.

Convención (alfabeto oficial del quechua collao, P3 en config.variedad.vocales):
- glotalizadas (ch' k' p' q' t') y aspiradas (chh kh ph qh th) SÍ se escriben;
- 3 vocales (a, i, u) por defecto, o 5 si se elige la escritura de la Academia Mayor de la Lengua Quechua;
- k, q, w, h en lugar de c, qu, hu, j castellanas; semivocales con y/w («kunkayki», no «kunkaiki»).

Desde el 5-nov-2026 el léxico de referencia sale SOLO de fuentes collao (Lopera, Farfán, OPS/OMS Bolivia y las
fuentes collao que se agreguen); del material chanka solo se usa el lado español como léxico español.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from functools import lru_cache

from comun import CFG, RAIZ, asegurar_dir, escribir_json, fuente, ruta, sin_tildes, texto
import fuentes as F

VOCALES = int(CFG.get("variedad", {}).get("vocales", 3))

# ------------------------------------------------------------------ alfabeto y tokens

RE_TOKEN_QU = re.compile(r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü'’´`]+")
RE_GLOTAL = re.compile(r"(ch|k|q|p|t)'", re.I)
RE_ASPIRADA = re.compile(r"(chh|kh|ph|qh|th)", re.I)
ASPIRADA_A_SIMPLE = {"chh": "ch", "kh": "k", "ph": "p", "qh": "q", "th": "t"}


def apostrofos(s: str) -> str:
    return re.sub(r"[’´`]", "'", s)


def tokens_qu(s: str) -> list[str]:
    return [apostrofos(t) for t in RE_TOKEN_QU.findall(texto(s))]


def norm(t: str) -> str:
    return sin_tildes(apostrofos(t).lower()).replace("'", "") if t else ""


def norm_ñ(t: str) -> str:
    """Minúsculas sin tildes, conservando ñ (sin_tildes la quita) y sin apóstrofos."""
    t = apostrofos(t).lower().replace("'", "")
    return "".join("ñ" if c == "ñ" else sin_tildes(c) for c in t)


def llave(t: str) -> str:
    """Forma de comparación: sin glotalización ni aspiración, con 3 vocales y h por j. Así «p'unchay», «punchay»,
    «P'UNCHAY» y «phunchay» se reconocen como la misma palabra al buscarla en el léxico (no se usa para escribir)."""
    w = apostrofos(t).lower()
    w = RE_GLOTAL.sub(lambda m: m.group(1), w)
    w = RE_ASPIRADA.sub(lambda m: ASPIRADA_A_SIMPLE[m.group(1).lower()], w)
    w = norm_ñ(w).replace("j", "h").replace("e", "i").replace("o", "u")
    return w


def tiene_laringal(t: str) -> bool:
    return bool(RE_GLOTAL.search(apostrofos(t)) or RE_ASPIRADA.search(t))


# ------------------------------------------------------------------ sufijos (§11.1), collao

SUFIJOS_CATEGORIA = {
    "Nominales": ["kuna", "y", "yki", "n", "nchis", "yku", "ykichis", "nku", "ta", "man", "pi", "manta", "wan",
                  "paq", "pa", "p", "kama", "rayku", "hina", "nta", "yuq", "ntin", "pura"],
    "Persona verbal": ["ni", "nki", "n", "nchis", "yku", "nkichis", "nku", "wa", "su", "yki"],
    "Tiempo/aspecto/modo": ["sha", "rqa", "sqa", "saq", "nqa", "sun", "man", "waq", "y", "ychis", "chun"],
    "Derivativos": ["chi", "ku", "mu", "pu", "ri", "rqu", "yku", "naku", "ysi", "pa", "ykacha"],
    "Nominalizadores": ["q", "sqa", "na", "y"],
    "Subordinadores": ["spa", "qti", "stin"],
    "Enclíticos": ["mi", "n", "si", "s", "cha", "chu", "taq", "qa", "pas", "pis", "lla", "ña", "raq", "ya", "puni", "ri"],
}
# Formas de otras variedades que aparecen en los borradores (boliviano, Lopera): sirven para segmentar, no para
# medir cobertura (la cobertura cuenta solo los sufijos collao de arriba).
SUFIJOS_OTRAS = ["chka", "nchik", "ykichik", "nkichik", "ychik", "pti", "hti"]
SUFIJOS = sorted({s for v in SUFIJOS_CATEGORIA.values() for s in v} | set(SUFIJOS_OTRAS), key=len, reverse=True)
SUFIJOS_COLLAO = {s for v in SUFIJOS_CATEGORIA.values() for s in v}
RAICES_CORTAS = {"ka", "ri", "qu", "ni", "pi", "ma", "may", "ima", "pay", "kay", "chay", "wak", "huk", "uma", "ñan", "unu"}


@lru_cache(maxsize=None)
def segmentar(palabra: str) -> tuple[str, tuple[str, ...]]:
    """Segmentación heurística: quita sufijos desde el final (el más largo primero) hasta llegar a una raíz
    conocida o a una raíz de 3+ letras. Trabaja sobre la llave (sin glotales). Es aproximada."""
    w = llave(palabra)
    lx = lexico()
    raices, conocidas = lx["raices"], lx["qu"]
    sufs: list[str] = []
    while len(sufs) < 7:
        if sufs and (w in raices or w in conocidas):
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
    """Unidades para medir cobertura: sufijos collao, bigramas de letras y palabras."""
    sufijos, bigramas, palabras = set(), set(), set()
    for t in tokens_qu(qu):
        w = norm_ñ(t)
        if not w or es_prestamo_o_propio(t)[0]:
            continue
        palabras.add(llave(t))
        _, sufs = segmentar(w)
        sufijos.update(f"-{s}" for s in sufs if s in SUFIJOS_COLLAO)
        ww = f"#{apostrofos(t).lower()}#"
        bigramas.update(ww[i:i + 2] for i in range(len(ww) - 1))
    return {"sufijo": sufijos, "bigrama": bigramas, "palabra": palabras}


# ------------------------------------------------------------------ léxicos de referencia (solo collao)


def textos_collao() -> dict[str, list[str]]:
    """Quechua collao de las fuentes disponibles, por fuente."""
    out: dict[str, list[str]] = {}
    U = F.cargar_unificado()
    lop = U[U["Fuente_original"].str.startswith("Lopera")]
    out["Lopera (libro)"] = [x for x in (F.forma_del_libro(a, b, c) for a, b, c in
                                          zip(lop["quechua_marshall"], lop["quechua_kim1"], lop["quechua_kim2"])) if x]
    out["Farfán"] = [p["qu"] for p in F.pares_farfan()]
    out["OPS/OMS Bolivia"] = [p["qu"] for p in F.pares_ops_bolivia()]
    for nombre, pares in F.pares_collao_extra().items():
        out[nombre] = [p["qu"] for p in pares]
    for nombre, paginas in F.textos_collao_sueltos().items():
        out[nombre] = paginas
    return out


def _firma() -> dict:
    f = {k: fuente(k).stat().st_size for k in ["unificado", "web_html", "ops_bolivia_pdf", "diabetes_es_pdf"]}
    f["americasnlp_es"] = sum(p.stat().st_size for p in fuente("americasnlp_dir").rglob("*.es") if p.is_file())
    f["americasnlp_quz"] = sum(p.stat().st_size for p in fuente("americasnlp_dir").rglob("*.quz") if p.is_file())
    d = F.dir_collao()
    f["collao"] = sum(p.stat().st_size for p in d.rglob("*") if p.is_file()) if d.exists() else 0
    f["version"] = "collao-5"
    return f


@lru_cache(maxsize=1)
def lexico() -> dict:
    """Léxico quechua collao (llaves, frecuencias, formas escritas, raíces) y léxico español, con caché en disco."""
    cache = asegurar_dir(ruta("checkpoints") / "cache") / "lexicos_collao.json"
    firma = _firma()
    if cache.exists():
        d = json.loads(cache.read_text(encoding="utf-8"))
        if d.get("firma") == firma:
            return {"qu": set(d["qu"]), "qu_frec": d["qu_frec"], "formas": d["formas"], "raices": set(d["raices"]),
                    "es": set(d["es"])}
    # Español: solo palabras que aparecen alguna vez en minúscula (así no entran nombres propios). Se usa el lado
    # español de AmericasNLP (es texto en español, no depende de la variedad), el de OPS/OMS y el PDF de diabetes.
    es = set()
    re_es = re.compile(r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü]+")
    A = F.americasnlp()
    lineas_es = [l for nombre in ["train (JW300)", "dict (MINEDU + Dict_misc)", "dev (sureño estándar)", "test (solo español)"]
                 for l in A.get(nombre, {}).get("es", [])] + F.texto_pdf("diabetes_es_pdf") + [p["es"] for p in F.pares_ops_bolivia()]
    for linea in lineas_es:
        es.update(norm_ñ(x) for x in re_es.findall(linea) if x[:1].islower())
    # Quechua collao
    frec: Counter = Counter()
    formas: dict[str, Counter] = defaultdict(Counter)
    def parece_prestamo(t: str, w: str) -> bool:
        # préstamos dentro del quechua de las fuentes («tomanki», «verdura», «hospitalpi»): no cuentan como quechua
        if tiene_laringal(t):
            return False
        if w in es or set(w) & set("bdfgvxz"):
            return True
        if not re.search(r"[eo]|c(?!h)|j", w):
            return False
        for L in range(len(w), 3, -1):
            p = w[:L]
            if any(v in es for v in (p, p + "r", p + "ar", p + "er", p + "ir")):
                return True
        return False

    for lineas in textos_collao().values():
        for linea in lineas:
            for t in tokens_qu(linea):
                w = norm_ñ(t)
                if len(w) < 2 or parece_prestamo(t, w):
                    continue
                k = llave(t)
                frec[k] += 1
                formas[k][apostrofos(t).lower()] += 1
    # JW300 en quechua de Cusco (AmericasNLP 2021, es-quz): prosa religiosa, solo como léxico; cuentan las palabras que
    # aparecen 2+ veces (así no entran erratas sueltas)
    frec_jw: Counter = Counter()
    formas_jw: dict[str, Counter] = defaultdict(Counter)
    for linea in F.jw300_quz()["qu"]:
        for t in tokens_qu(linea):
            w = norm_ñ(t)
            if len(w) < 2 or parece_prestamo(t, w):
                continue
            k = llave(t)
            frec_jw[k] += 1
            formas_jw[k][apostrofos(t).lower()] += 1
    for k, n in frec_jw.items():
        if n >= 2:
            frec[k] += n
            formas[k].update(formas_jw[k])
    qu = set(frec)
    datos = {"firma": firma, "qu": sorted(qu), "qu_frec": dict(frec), "formas": {k: dict(v) for k, v in formas.items()},
             "raices": [], "es": sorted(es)}
    escribir_json(cache, datos)
    lx = {"qu": qu, "qu_frec": datos["qu_frec"], "formas": datos["formas"], "raices": set(), "es": es}
    # raíces: lo que queda tras quitar sufijos a cada palabra conocida, parando en cuanto lo que queda es otra palabra
    # conocida («allinllachu» → «allin», no «alli»). Solo raíces de 3+ letras.
    raices = set()
    for k in qu:
        w = k
        for _ in range(6):
            for s in SUFIJOS:
                if w.endswith(s) and len(w) - len(s) >= 3:
                    w = w[: -len(s)]
                    break
            else:
                break
            if w in qu:
                break
        if len(w) >= 4 or w in qu:          # raíces de 3 letras solo si son palabra completa (evita «lli», «tuma»)
            raices.add(w)
    datos["raices"] = sorted(raices)
    escribir_json(cache, datos)
    lx["raices"] = raices
    return lx


def conocida(w: str) -> bool:
    """¿La palabra (o alguna de sus raíces tras quitar sufijos) aparece en el léxico collao de referencia?"""
    lx = lexico()
    k = llave(w)
    if k in lx["qu"] or k in lx["raices"]:
        return True
    raiz, sufs = segmentar(w)
    if raiz in lx["raices"] or (raiz in lx["qu"] and len(raiz) >= 3):
        return True
    actual = raiz
    for s in sufs:
        actual += s
        if actual in lx["qu"] and len(actual) >= 4:
            return True
    return False


def forma_laringal(t: str) -> str:
    """Si en las fuentes collao esta palabra se escribe siempre con glotalizada o aspirada y aquí no la tiene,
    devuelve la forma de las fuentes («punchay» → «p'unchay»). Si no, vacío."""
    if tiene_laringal(t):
        return ""
    formas = lexico()["formas"].get(llave(t), {})
    if not formas:
        return ""
    con = {f: n for f, n in formas.items() if tiene_laringal(f)}
    sin = sum(n for f, n in formas.items() if not tiene_laringal(f))
    if con and sum(con.values()) >= 2 and sin == 0:
        return max(con, key=con.get)
    return ""


# ------------------------------------------------------------------ préstamos y nombres propios

PRESTAMOS_COMUNES = {
    "hospital", "pastilla", "pastillas", "doctor", "doctora", "posta", "enfermera", "inyeccion", "ampolla", "jarabe",
    "vacuna", "misa", "kuchara", "plato", "papel", "papil", "jabon", "jabun", "tuwalla", "semana", "simana", "minuto",
    "minutos", "hora", "ura", "medicina", "remedio", "suero", "analisis", "examen", "operacion", "kama", "cama",
    "covid", "coronavirus", "alcohol", "cerveza", "trago", "fruta", "frutakuna", "arroz", "arrus", "azucar", "asukar",
    "sal", "mascarilla", "termometro", "presion", "diabetes", "diabetis", "glucosa", "insulina", "hipoglicemia",
    "emergencia", "establecimiento", "salud", "receta", "sulfato", "ferroso", "condon", "regla", "anillo", "pulsira",
    "jeringa", "dosis", "litro", "kilo", "gramo", "metro", "mes", "domingo", "lunes", "martes", "sabado", "tumingu",
    "sabadu", "tiyanda", "platanu", "mantikilla", "futbul", "arku", "blukiku", "kuartu", "pisu",
    "yerro", "hierro", "yirru", "enema", "pomada", "gotas", "pildora", "lentes", "sonda", "anticonceptivo",
    "anemia", "infeccion", "inficcion", "radiografia", "ecografia", "tomografia", "tableta", "tabletas",
    "hipertension", "tuberculosis", "prostata", "vesicula", "bronquios", "yeso", "ambulancia", "seguro",
    "medico", "medicu", "segundo", "segundos", "minoto", "minutu", "urinaria", "orinaria", "desnutricion", "gastritis",
    "control", "kuntrul", "cuntrul", "vacunachi", "vacunachikunayki", "color", "kulur", "mate", "mati", "verdura",
}
NOMBRES_PROPIOS = {"lince", "lima", "victoria", "peru", "piru", "maria", "dios", "diosninchis", "cusco", "cuzco", "qusqu",
                   "qosqo", "puno", "punu", "juliaca", "sicuani", "urubamba", "quillabamba", "calca", "anta", "espinar",
                   "canchis", "paucartambo", "chumbivilcas", "bolivia", "cochabamba", "minsa", "essalud", "diresa",
                   "pedro", "juan", "jose", "rosa", "carmen", "hearts", "ayacucho", "apurimac", "huancavelica"}


@lru_cache(maxsize=None)
def _raiz_espanola(t: str) -> str:
    """Si la palabra empieza con una palabra (o raíz verbal) española, devuelve esa raíz.

    Los préstamos llevan sufijos quechuas pegados a una raíz española, a veces ya adaptada: «hospitalman»,
    «operachikunan» (operar), «inyectachikunayki» (inyectar). Se prueba cada prefijo de 4+ letras, también con la
    vocal final adaptada (u→o, i→e) y como verbo (+r, +ar, +er, +ir)."""
    es = lexico()["es"]
    w = norm_ñ(t)
    for L in range(len(w), 3, -1):
        p = w[:L]
        variantes = [p, p + "r", p + "ar", p + "er", p + "ir"]
        if "k" in p:
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
        if len(segmentar(w)[1]) <= 1 and not conocida(w):
            return True, "nombre propio"
    if any(f in PRESTAMOS_COMUNES for f in _formas(w)):
        return True, "préstamo común"
    if tiene_laringal(t):
        return False, ""                             # una glotalizada o aspirada es señal clara de palabra quechua
    if re.search(r"[aeiou]jti", w):
        return False, ""                             # subordinador -jti- («purijtiyki»): es quechua de otra zona, no español
    if set(w) & set("bdfgvxz"):
        return True, "préstamo"
    # también con 5 vocales: «tomani» y «piensani» siguen siendo préstamos; «qolqe» no, porque su raíz no es española
    if re.search(r"[eo]|c(?!h)|j", w) and _raiz_espanola(t):
        return True, "préstamo"
    return False, ""


# ------------------------------------------------------------------ normalización ortográfica mecánica (§10.3)


def _con_mayus(orig: str, nuevo: str) -> str:
    return nuevo[:1].upper() + nuevo[1:] if orig[:1].isupper() else nuevo


def corregir_token(t: str, inicio: bool) -> tuple[str, list[str]]:
    """Aplica solo las reglas mecánicas de §10.3 a una palabra quechua. Devuelve (nuevo, reglas aplicadas).
    Las glotalizadas y aspiradas se CONSERVAN (son parte del alfabeto collao)."""
    prestamo, _ = es_prestamo_o_propio(t, inicio)
    if prestamo:
        return t, []
    w = apostrofos(t)
    reglas = []
    if w != t:
        reglas.append("apóstrofo normalizado (')")
    # 1) semivocales: «kunkaiki» → «kunkayki»; «allyntachu» → «allintachu», «puñunky» → «puñunki»
    # (no se toca la «u» de «qu»/«gu» castellanos: «Yupanqui», «sunquimampis»; «oiy» → «oy», no «oyy»)
    nuevo = re.sub(r"(?:(?<=[aeo])|(?<=[^qg]u))i(?=y)", "", w, flags=re.I)
    nuevo = re.sub(r"(?:(?<=[aeo])|(?<=[^qg]u))i(?=[^aeiou'\W]|$)", "y", nuevo, flags=re.I)
    nuevo = re.sub(r"(?<=[bcdfghjklmnñpqrstvwxz])y(?=[^aeiou'\W]|$)", "i", nuevo, flags=re.I)
    if nuevo != w:
        reglas.append("semivocales con y (ai→ay; y entre consonantes → i)")
        w = nuevo
    # 2) escritura castellana: j → h siempre (en Cusco se escribe h); c/qu/hu solo si el resultado existe en el
    #    léxico collao de referencia (así no se inventan palabras: «c» puede ser k o q)
    if "j" in w.lower():
        w = w.replace("j", "h").replace("J", "H")
        reglas.append("j → h")
    cand = w.lower()
    cand = re.sub(r"qu(?=[ei])", "k", cand)
    cand = re.sub(r"c(?!h)", "k", cand)
    cand = re.sub(r"hu(?=[aeiou])", "w", cand)
    # (una palabra en mayúscula a mitad de frase puede ser un nombre: «Yupanqui» no pasa a «Yupanki»)
    if cand != w.lower() and conocida(cand) and (inicio or not t[:1].isupper()):
        reglas.append("sin c/qu/hu castellanas")
        w = _con_mayus(w, cand)
    # «cc» y la «c» final son la q de la escritura castellana (-tac → -taq, seccsi- → seqsi-). No exige estar en el léxico:
    # los borradores siguen la tabla del Word y el traductor cambia lo que no le parezca (coordinación, 5-nov-2026)
    cand = re.sub(r"c$", "q", re.sub(r"cc", "q", w.lower()))
    if cand != w.lower() and (inicio or not t[:1].isupper()):
        reglas.append("«cc» y «c» final → q")
        w = _con_mayus(w, cand)
    # 3) vocales
    if VOCALES == 3 and re.search(r"[eoéó]", w, re.I):
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
    partes = re.split(r"([A-Za-zÁÉÍÓÚáéíóúÑñÜü'’´`]+)", s)
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

# Rasgos que NO son del quechua de Cusco: chanka (Ayacucho) o boliviano. Se marcan, nunca se cambian.
LEXICO_VARIEDAD = [
    # el traductor lee estos textos en el Word: dicen lo que se usa en Cusco, sin nombrar otras variedades
    (re.compile(r"^yaku(ta|wan|pi|manta|lla|mi|m|n|y|yki|cha)?$"), "léxico «yaku» (en Cusco: unu)"),
    (re.compile(r"^upya"), "léxico «upyay» (en Cusco: uhyay)"),
    (re.compile(r"^ukya"), "léxico «ukyay» (en Cusco: uhyay)"),
    (re.compile(r"^llamk"), "léxico «llamkay» (en Cusco: llank'ay)"),
    (re.compile(r"^punchaw"), "«punchaw/p'unchaw» (en Cusco: p'unchay)"),
    (re.compile(r"^haykap"), "«haykap» (en Cusco: hayk'aq)"),
    (re.compile(r"^wichq"), "léxico «wichqay» (en Cusco: wisq'ay)"),
    (re.compile(r"^machk"), "«machkha» (en Cusco: hayk'a)"),
    (re.compile(r"^llawar"), "«llawar» (en Cusco: yawar)"),
]


def detectar_variedad(qu: str) -> list[str]:
    hall = []
    inicio = True
    for t in tokens_qu(qu):
        w = llave(t)
        prestamo = es_prestamo_o_propio(t, inicio)[0]
        inicio = False
        if prestamo:
            continue
        if re.search(r"\w{2,}chka", w) and not w.startswith("machk"):      # machkha es «cuánto», no un progresivo
            hall.append(f"progresivo -chka- en «{t}» (en Cusco: -sha-)")
        if re.search(r"\w[aiu]m$", w) and len(w) >= 3:
            hall.append(f"validador -m en «{t}» (en Cusco, tras vocal: -n)")
        if re.search(r"(nchik|ykichik|nkichik|ychik)", w):
            hall.append(f"plural -chik en «{t}» (en Cusco: -chis)")
        if re.search(r"\w(pti|hti)", w):
            hall.append(f"subordinador -pti-/-jti- en «{t}» (en Cusco: -qti-)")
        for pat, msg in LEXICO_VARIEDAD:
            if pat.search(w):
                hall.append(f"{msg} en «{t}»")
    return hall


def detectar_orto(qu: str) -> list[tuple[str, str]]:
    """(severidad, detalle) por letras fuera de la convención collao en palabras quechuas."""
    hall = []
    inicio = True
    for t in tokens_qu(qu):
        prestamo, _ = es_prestamo_o_propio(t, inicio)
        inicio = False
        if prestamo:
            continue
        w = t.lower()
        if VOCALES == 3 and re.search(r"[eoéó]", w):
            hall.append(("MEDIA", f"vocal e/o en «{t}» (alfabeto oficial: a, i, u)"))
        if re.search(r"c(?!h)|qu(?=[ei])|hu(?=[aeiou])", w):
            hall.append(("ALTA", f"escritura castellana (c/qu/hu) en «{t}»"))
        if "j" in w:
            hall.append(("ALTA", f"«j» en «{t}» (en Cusco se escribe h)"))
        otras = set(norm(w)) & set("bdfgvxz")
        if otras:
            hall.append(("ALTA", f"letra fuera del alfabeto ({', '.join(sorted(otras))}) en «{t}»"))
        if re.search(r"(^|[^chkpqt])'|'$", w):
            hall.append(("MEDIA", f"apóstrofo fuera de lugar en «{t}» (solo va en ch' k' p' q' t')"))
        if re.search(r"(?:[aeo]|[^qg]u)i(?=[^aeiou'\W]|$)|[bcdfghjklmnñpqrstvwxz]y(?=[^aeiou'\W]|$)", w):
            hall.append(("MEDIA", f"semivocal mal escrita en «{t}» (ai→ay; y entre consonantes → i)"))
        fl = forma_laringal(t)
        if fl:
            hall.append(("MEDIA", f"¿falta glotalizada o aspirada? «{t}» → en las fuentes collao «{fl}»"))
    return hall


RE_RESTO_VERBAL = re.compile(r"^[aei]?(ni|nki|nchis|yku|nkichis|nku|spa|sqa|sha|chka|rqa|qtin|qti|ptin|pti|saq|sun|nqa|chun|y|n)(\W|$|[a-zñ]*)")
# terminaciones de un verbo español conjugado o en infinitivo («entienden», «comemos», «tomar»)
RE_VERBO_ES = re.compile(r"(an|en|amos|emos|imos|ais|eis|ar|er|ir|aba|aban|ia|ian)$")


def _palabra_en_espanol(t: str, es: str) -> str:
    """Palabra del español de la misma fila que el préstamo repite como SUSTANTIVO, sola o con sufijos quechuas
    («radiografiata» ↔ «radiografía», «anticonceptivota» ↔ «anticonceptivo»): eso es un préstamo esperable. No cuenta
    si el token es un VERBO español tal cual («entienden») ni si lleva sufijos verbales («piensani»)."""
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


@lru_cache(maxsize=None)
def sugerencia_transcripcion(t: str) -> str:
    """Si la palabra no está en el léxico collao pero una variante típica de transcribir de oído sí («y» por «ll»,
    letra inicial que falta, «r» final que falta), devuelve la sugerencia. Con el léxico collao (más chico que el
    chanka que había) las sugerencias son pocas y prudentes."""
    lx = lexico()
    w = llave(t)
    if len(w) < 3:
        return ""
    if "y" in w[:-1]:
        f_w = lx["qu_frec"].get(w, 0)
        for m in re.finditer("y", w[:-1]):
            v = w[:m.start()] + "ll" + w[m.end():]
            f_v = lx["qu_frec"].get(v, 0)
            if f_v >= 10 and f_v >= 10 * max(f_w, 1):
                return f"«{t}» → ¿«{v}»? (y por ll; «{v}» es mucho más frecuente)"
    if conocida(w):
        return ""
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
NUMEROS_QU = {"2": ["iskay"], "3": ["kimsa", "kinsa"], "4": ["tawa"], "5": ["pichqa", "pisqa", "phisqa"], "6": ["suqta", "soqta"],
              "7": ["qanchis"], "8": ["pusaq"], "9": ["isqun", "isqon", "iskun"], "10": ["chunka"],
              "100": ["pachak", "pachaq"], "1000": ["waranqa"]}
SUF_NUM = re.compile(r"^(kaq|ta|pi|man|manta|yuq|yuqta|ntin|chu|mi|m|lla|llata|wan|kama|niyuq|kuti|kutita|pa|qa|taq|ña|raq|y|yki|n)*$")
MARCAS_PREGUNTA_QU = re.compile(r"(chu|taq|tak)\b|\b(ima|may|pi|hayka|machkha|imayna|imarayku|mayqan|mayqin|maymanta|maypi|pitaq|piwan|pin|imam|iman)", re.I)


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
        def decir(numeros: set[str]) -> str:      # este texto llega al Word: sin corchetes ni comillas de programa
            return "dice " + ", ".join(sorted(numeros, key=int)) if numeros else "no da ningún número"
        hall.append(("ALTA", f"números distintos: el español {decir(ne)} y el quechua {decir(nq)}"))
    if ("?" in es or "¿" in es) and "?" not in qu and not MARCAS_PREGUNTA_QU.search(norm(qu)):
        hall.append(("MEDIA", "pregunta en español sin marca interrogativa en quechua (-chu, -taq, ima-, pi-, may-, hayk'a-)"))
    return hall


RE_MUCHO = re.compile(r"\b(mucho|mucha|muchos|muchas|muy|bastante|harto|fuerte|intenso)\b")
RE_POCO = re.compile(r"\b(poco|poca|poquito|poquita|leve|suave)\b")
SENTIDO_REGLAS = [
    (RE_MUCHO, re.compile(r"\b(pisi|tumpa)"), "español dice «mucho» pero el quechua tiene «pisi/tumpa» (= poco)"),
    (RE_POCO, re.compile(r"\b(achka|achkha|ashka|askha|ancha|anchata|nisyu|sinchi)"), "español dice «poco» pero el quechua tiene «ashka/ancha» (= mucho)"),
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
            if "mes" in msg and re.search(r"\bkilla", q):
                continue
            if "«año»" in msg and re.search(r"\bwata", q):
                continue
            if (pe is RE_MUCHO and RE_POCO.search(e)) or (pe is RE_POCO and RE_MUCHO.search(e)):
                continue
            hall.append(("ALTA", msg))
    neg_es = re.search(r"\b(no|nunca|ni|tampoco|jamas)\b", e)          # «nada» se omite: suele ser el verbo nadar
    neg_qu = re.search(r"\b(mana|ama|manam|amam|manan|aman|manachu|ni)\w*|chu\b", q)
    if neg_es and not neg_qu and not ("?" in es or "¿" in es):
        hall.append(("MEDIA", "el español es negativo pero el quechua no tiene mana/ama/-chu"))
    return hall
