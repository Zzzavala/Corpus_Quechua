"""Lectura de las fuentes (solo lectura). Cada función devuelve un DataFrame con la fila original.

Nunca se escribe sobre las fuentes. Los Excel con fórmulas se leen con data_only=True y los IDs
que dependen de fórmulas (N° de Grupo 3 y de Corpus_Construido) se reconstruyen por posición.
"""
from __future__ import annotations

import html as html_mod
import json
import re
from functools import lru_cache
from pathlib import Path

import openpyxl
import pandas as pd

from comun import CFG, RAIZ, asegurar_dir, clave_normalizada, escribir_json, fuente, ruta, texto

# --------------------------------------------------------------------------- Excel genérico


def _filas(path: Path, hoja: str, data_only: bool = True) -> list[tuple[int, list]]:
    wb = openpyxl.load_workbook(path, data_only=data_only, read_only=True)
    ws = wb[hoja]
    out = []
    for i, r in enumerate(ws.iter_rows(values_only=True), start=1):
        out.append((i, list(r)))
    wb.close()
    return out


def hojas(path: Path) -> list[str]:
    wb = openpyxl.load_workbook(path, read_only=True)
    n = list(wb.sheetnames)
    wb.close()
    return n


def resumen_hoja(path: Path, hoja: str) -> dict:
    filas = _filas(path, hoja)
    no_vacias = [f for f in filas if any(not _vacio(c) for c in f[1])]
    ncol = max((len(f[1]) for f in filas), default=0)
    encabezado = [texto(c) for c in filas[0][1]] if filas else []
    while encabezado and encabezado[-1] == "":
        encabezado.pop()
    return {"hoja": hoja, "filas_totales": len(filas), "filas_no_vacias": len(no_vacias), "columnas": ncol,
            "encabezado": encabezado}


def _vacio(c) -> bool:
    return c is None or (isinstance(c, str) and c.strip() == "")


def _col(r: list, i: int):
    return r[i] if i < len(r) else None


# --------------------------------------------------------------------------- unificado (§5.1)

COLS_UNIFICADO = ["Id_unificado", "Español (palabra o frase)", "Quechua_final (chanka)", "quechua_marshall",
                  "quechua_kim1", "quechua_kim2", "Observaciones_finales", "Estado", "Sección",
                  "Fuente_original", "Códigos_origen"]


@lru_cache(maxsize=1)
def cargar_unificado() -> pd.DataFrame:
    filas = _filas(fuente("unificado"), "Vocabulario_unificado")
    enc = [texto(c) for c in filas[0][1]]
    idx = {h: enc.index(h) for h in COLS_UNIFICADO}
    datos = []
    for n, r in filas[1:]:
        if all(_vacio(c) for c in r):
            continue
        d = {h: texto(_col(r, idx[h])) for h in COLS_UNIFICADO}
        d["Fila_original"] = n
        datos.append(d)
    return pd.DataFrame(datos)


@lru_cache(maxsize=1)
def cargar_trazabilidad() -> pd.DataFrame:
    filas = _filas(fuente("unificado"), "Trazabilidad")
    enc = [texto(c) for c in filas[0][1]]
    datos = []
    for n, r in filas[1:]:
        if all(_vacio(c) for c in r):
            continue
        d = {h: texto(_col(r, i)) for i, h in enumerate(enc) if h}
        d["Fila_original"] = n
        datos.append(d)
    return pd.DataFrame(datos)


def fuente_canonica(fuente_original: str) -> str:
    f = texto(fuente_original)
    reglas = [
        ("Lopera", "Lopera Quiroga (2020)"),
        ("Allin Kawsay", "Allin Kawsay (INS/MINSA)"),
        ("OPS/OMS Bolivia", "OPS/OMS Bolivia (2013)"),
        ("Corpus original del equipo", "SOCEMURP (corpus original del equipo)"),
        ("Manual de quechua médico SOCEMURP", "SOCEMURP (corpus original del equipo)"),
        ("Pregunta añadida por Kim 1", "Kim 1 (pregunta añadida)"),
        ("Farfán", "Farfán Cantero (2001), SITUA"),
        ("Manual del quechua chanka para la administración de justicia", "MinCul – manual de justicia (chanka)"),
        ("YouTube", "YouTube"),
        ("Afiche MINSA/MinCul", "Afiche MINSA/MinCul lavado de manos (chanka)"),
        ("MINSA", "MINSA – diabetes (quechua)"),
        ("OMS (2009)", "OMS (2009) – lista de verificación"),
    ]
    for clave, nombre in reglas:
        if f.startswith(clave):
            return nombre
    return f or "(sin fuente)"


# --------------------------------------------------------------------------- Corpus_Equipos (§5.2)


def _hoja_simple(hoja: str, col_es: int, col_qu: int, col_obs: int, col_id: int = 0, col_tipo: int | None = None):
    filas = _filas(fuente("corpus_equipos"), hoja)
    datos = []
    for n, r in filas[1:]:
        if all(_vacio(c) for c in r):
            continue
        d = {
            "Código_original": texto(_col(r, col_id)),
            "Español": texto(_col(r, col_es)),
            "Quechua": texto(_col(r, col_qu)),
            "Observaciones": texto(_col(r, col_obs)),
            "Extra": " | ".join(texto(c) for c in r[max(col_obs, col_qu) + 1:] if not _vacio(c)),
            "Fila_original": n,
        }
        if col_tipo is not None:
            d["Tipo"] = texto(_col(r, col_tipo))
        datos.append(d)
    return pd.DataFrame(datos)


@lru_cache(maxsize=1)
def cargar_principito() -> pd.DataFrame:
    return _hoja_simple("Grupo 1 - Principito", 1, 2, 3)


@lru_cache(maxsize=1)
def cargar_grupo2() -> pd.DataFrame:
    return _hoja_simple("Grupo 2 - Corpus Chanka", 1, 2, 3)


@lru_cache(maxsize=1)
def cargar_grupo3() -> pd.DataFrame:
    df = _hoja_simple("Grupo 3 - Corpus Medico", 1, 2, 3)
    # N° es fórmula (=A2+1): se reconstruye por posición.
    df["Código_original"] = [f"G3-{i:04d}" for i in range(1, len(df) + 1)]
    return df


@lru_cache(maxsize=1)
def cargar_terminos() -> pd.DataFrame:
    df = _hoja_simple("Grupo 3 - Términos médicos", 2, 3, 4, col_tipo=1)
    df["Código_original"] = [f"G3T-{i:03d}" for i in range(1, len(df) + 1)]
    return df


@lru_cache(maxsize=1)
def cargar_construido() -> pd.DataFrame:
    filas = _filas(fuente("corpus_construido"), "Hoja 1")
    datos = []
    for n, r in filas[1:]:
        if all(_vacio(c) for c in r):
            continue
        datos.append({"Español": texto(_col(r, 2)), "Quechua": texto(_col(r, 3)), "Fila_original": n})
    df = pd.DataFrame(datos)
    # N° es fórmula (=CONCATENATE("S1-",B2)): se reconstruye.
    df["Código_original"] = [f"S1-{i}" for i in range(1, len(df) + 1)]
    return df


# --------------------------------------------------------------------------- AmericasNLP (§5.5)


def _lineas(p: Path) -> list[str]:
    return p.read_text(encoding="utf-8-sig").splitlines()


@lru_cache(maxsize=1)
def americasnlp() -> dict[str, dict]:
    base = RAIZ / CFG["rutas"]["fuentes"] / CFG["archivos_fuente"]["americasnlp_dir"]
    out = {}
    for nombre, es, qu in [
        ("train (JW300)", "train.es", "train.quy"),
        ("dev (sureño estándar)", "dev.es", "dev.quy"),
        ("dict (MINEDU + Dict_misc)", "dict.es", "dict.quy"),
        ("es-quy/jw300", "es-quy/jw300.es-quy.es", "es-quy/jw300.es-quy.quy"),
        ("es-quy/minedu", "es-quy/minedu.quy-es.es", "es-quy/minedu.quy-es.quy"),
        ("es-quy/dict_misc", "es-quy/dict_misc.quy-es.es", "es-quy/dict_misc.quy-es.quy"),
    ]:
        pe, pq = base / es, base / qu
        if pe.exists() and pq.exists():
            out[nombre] = {"es": _lineas(pe), "qu": _lineas(pq), "archivos": [es, qu]}
    pt = base / "test.es"
    if pt.exists():
        out["test (solo español)"] = {"es": _lineas(pt), "qu": [], "archivos": ["test.es"]}
    return out


# --------------------------------------------------------------------------- PDF y HTML


def _cache_dir() -> Path:
    return asegurar_dir(ruta("checkpoints") / "cache")


def texto_pdf(clave: str) -> list[str]:
    """Texto por página (vacío si el PDF es solo imagen). Se guarda en caché."""
    p = fuente(clave)
    cache = _cache_dir() / f"pdf_{clave}.json"
    if cache.exists():
        datos = json.loads(cache.read_text(encoding="utf-8"))
        if datos.get("bytes") == p.stat().st_size:
            return datos["paginas"]
    import pypdfium2 as pdfium

    doc = pdfium.PdfDocument(p)
    paginas = []
    for i in range(len(doc)):
        tp = doc[i].get_textpage()
        paginas.append(tp.get_text_range())
    doc.close()
    escribir_json(cache, {"bytes": p.stat().st_size, "paginas": paginas})
    return paginas


def ejemplos_minedu_pdf() -> list[dict]:
    """Ejemplos (quechua + traducción) del diccionario MINEDU en PDF.

    Formato observado: líneas que empiezan con '- ' (o '1. ', '2. ' en acepciones); un ejemplo quechua
    seguido de su traducción al español. Las líneas de continuación se pegan a la anterior.
    """
    paginas = texto_pdf("minedu_pdf")
    items = []
    for npag, t in enumerate(paginas, start=1):
        bloques: list[str] = []
        actual = None
        for linea in t.replace("\r", "\n").split("\n"):
            s = linea.strip()
            if not s or "indd" in s or re.fullmatch(r"\d{1,3}", s):
                continue
            m = re.match(r"^(?:-|\d\.)\s+(.*)$", s)
            if m:
                if actual is not None:
                    bloques.append(actual)
                actual = m.group(1)
            elif actual is not None and not re.match(r"^[A-ZÑ][a-zñ' ]+\.?\s*(\d\.)?\s*\((s|r|rt|ch|tp|sy)\)", s):
                actual += " " + s
            else:
                if actual is not None:
                    bloques.append(actual)
                actual = None
        if actual is not None:
            bloques.append(actual)
        for b in bloques:
            items.append({"pagina": npag, "texto": re.sub(r"\s+", " ", b).strip()})
    return items


def pares_farfan() -> list[dict]:
    """Pares (español, quechua cusqueño ORIGINAL) de la tabla de Farfán Cantero (2001). La tabla tiene dos pares por
    fila (CASTELLANO | QUECHUA | CASTELLANO | QUECHUA): se leen las celdas en orden y se emparejan de a dos."""
    raw = fuente("web_html").read_bytes()
    try:
        h = raw.decode("utf-8")
        if "�" in h or "Ã" in h:
            raise UnicodeDecodeError("utf-8", b"", 0, 1, "mojibake")
    except UnicodeDecodeError:
        h = raw.decode("cp1252", errors="replace")
    celdas = [html_mod.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", c))).replace("\xa0", " ").strip()
              for c in re.findall(r"<td[^>]*>(.*?)</td>", h, flags=re.S | re.I)]
    try:
        i0 = max(i for i, c in enumerate(celdas) if c == "QUECHUA") + 1
    except ValueError:
        return []
    utiles = [c for c in celdas[i0:] if c and c.lower() != "regresar"]
    return [{"es": utiles[k], "qu": utiles[k + 1], "pos": k // 2 + 1} for k in range(0, len(utiles) - 1, 2)]


def pares_ops_bolivia() -> list[dict]:
    """Pares (español, quechua sureño boliviano) del *Diálogo médico paciente en quechua* (OPS/OMS Bolivia 2013).
    En el texto del PDF cada frase en español empieza con una viñeta (carácter U+F06C) y la sigue su versión quechua
    (una o más líneas). Se ignoran los encabezados de página («DIÁLOGO MÉDICO PACIENTE EN QUECHUA 33»).
    Las líneas que siguen a la viñeta pueden ser: continuación del español (frase cortada en dos líneas), una nota
    entre paréntesis («(refiriéndose a una tercera persona)»), un título de sección («CONDÓN», «Mareos») o el quechua.
    Se distinguen por las marcas del quechua (k, w, glotalizadas, aspiradas, q sin u) frente al español."""
    pares = []

    def es_quechua(s: str) -> bool:
        return bool(re.search(r"[ptkq]'|ch'|[kpqt]h|q(?!u)|w|k|ñ[aiu]", s.lower()))

    def es_titulo(s: str) -> bool:
        letras = [c for c in s if c.isalpha()]
        return bool(re.match(r"^\d+\.\s", s)) or (len(letras) >= 3 and sum(c.isupper() for c in letras) / len(letras) > 0.6)

    for npag, t in enumerate(texto_pdf("ops_bolivia_pdf"), start=1):
        actual = None
        for linea in t.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
            s = linea.strip().replace("￾", "­")
            if not s or "DIÁLOGO MÉDICO PACIENTE" in s.upper() or re.fullmatch(r"\d{1,3}", s):
                continue
            if s.startswith(""):
                if actual and actual["qu"]:
                    pares.append(actual)
                actual = {"es": s.lstrip("").strip(), "qu": "", "nota": "", "pagina": npag}
                continue
            if actual is None or es_titulo(s):
                continue
            m = re.match(r"^(\([^()]*\))\s*(.*)$", s)
            if m:                                        # nota entre paréntesis (no se lee en voz alta)
                actual["nota"] = (actual["nota"] + " " + m.group(1)).strip()
                s = m.group(2)
                if not s:
                    continue
            if not actual["qu"] and not es_quechua(s):
                actual["es"] = (actual["es"] + " " + s).strip()          # el español seguía en la línea siguiente
            elif actual["qu"] and not es_quechua(s):
                continue                                                    # subtítulo suelto («Mareos», «Ictericia»)
            elif actual["qu"].endswith("­"):
                actual["qu"] = actual["qu"][:-1] + s                       # palabra partida con guion
            else:
                actual["qu"] = (actual["qu"] + " " + s).strip()
        if actual and actual["qu"]:
            pares.append(actual)
    for p in pares:
        p["qu"] = re.sub(r"\s*\*+$", "", p["qu"].replace("’", "'").replace("­", "")).strip()
        p["es"] = re.sub(r"\s+", " ", p["es"].replace("’", "'")).strip()
    return pares


def dir_collao() -> Path:
    """Carpeta para fuentes collao nuevas (p. ej. PDF del Ministerio de Cultura), solo lectura como las demás."""
    return RAIZ / CFG["rutas"]["fuentes"] / "collao"


def _segmentos_pdf(path: Path) -> list[list[tuple[float, float, str]]]:
    """Por página: fragmentos de texto con su posición (y de arriba, x izquierda, texto). Con caché."""
    cache = _cache_dir() / f"seg_{path.stem}.json"
    if cache.exists():
        datos = json.loads(cache.read_text(encoding="utf-8"))
        if datos.get("bytes") == path.stat().st_size:
            return datos["paginas"]
    import pypdfium2 as pdfium

    doc = pdfium.PdfDocument(path)
    paginas = []
    for i in range(len(doc)):
        tp = doc[i].get_textpage()
        segs = []
        for k in range(tp.count_rects()):
            l, b, r, t = tp.get_rect(k)
            s = tp.get_text_bounded(l, b, r, t).replace("￾", "").replace("\r", " ").replace("\n", " ").strip()
            if s:
                segs.append((round(t, 1), round(l, 1), s))
        paginas.append(segs)
    doc.close()
    escribir_json(cache, {"bytes": path.stat().st_size, "paginas": paginas})
    return paginas


RE_CONECTOR_FINAL = re.compile(r"\b(de|del|la|el|los|las|que|y|o|a|al|con|en|por|para|se|su|sus|mi|tu|no|un|una|me|le|lo|te)$", re.I)


def _columnas(xs: list[float], salto_min: float = 25.0) -> list[float]:
    """x de inicio de cada columna: agrupa las x de inicio de los fragmentos (un salto de 25+ pt separa columnas)."""
    xs = sorted(xs)
    inicios = [xs[0]]
    for a, b in zip(xs, xs[1:]):
        if b - a >= salto_min:
            inicios.append(b)
    return inicios


def pares_dos_columnas(path: Path, paginas: range, x_min: float = 20, y_max: float = 9999,
                       ignorar: str = r"Salud Materna y Perinatal|Palabras? ?Clave|^Quechua$|Atención en Salud") -> list[dict]:
    """Pares (castellano, quechua) de las tablas de un PDF: dos columnas, o cuatro (dos pares por fila).

    - Las columnas se detectan por la x de inicio de los fragmentos (saltos de 25+ pt). Con 4 columnas, cada fila
      tiene dos pares (1.ª–2.ª y 3.ª–4.ª).
    - Una fila nueva empieza cuando hay texto a la misma altura en las dos columnas de un par, o texto en una sola
      columna que no parece continuación. Es continuación si empieza en minúscula, si la línea anterior termina en
      «de/la/que…» o si la anterior abrió «¿» sin cerrar.
    - Se ignoran encabezados de página, títulos en mayúsculas y números de página."""
    todas = _segmentos_pdf(path)
    pares: list[dict] = []
    re_ign = re.compile(ignorar)
    for npag in paginas:
        if npag - 1 >= len(todas):
            break
        segs = [(t, x, s) for t, x, s in todas[npag - 1]
                if x >= x_min and t <= y_max and not re.fullmatch(r"\d{1,3}", s) and not re_ign.search(s)]
        if len(segs) < 2:
            continue
        cols = _columnas([x for _, x, _ in segs])
        if len(cols) < 2:
            continue
        # 4+ columnas en pares (es, qu, es, qu); si no, el corte entre izquierda y derecha es el mayor salto
        grupos = [(cols[k], cols[k + 1], cols[k + 2] if k + 2 < len(cols) else 1e9) for k in range(0, len(cols) - 1, 2)] \
            if len(cols) >= 4 and len(cols) % 2 == 0 else [(cols[0], max(zip([b - a for a, b in zip(cols, cols[1:])], cols[1:]))[1], 1e9)]
        for x_es, x_qu, x_fin in grupos:
            filas: dict[float, dict] = {}
            for t, x, s in sorted(segs, key=lambda z: (-z[0], z[1])):
                if not (x_es - 2 <= x < x_fin - 2):
                    continue
                y = next((k for k in filas if abs(k - t) <= 2.0), t)
                f = filas.setdefault(y, {"izq": [], "der": []})
                f["izq" if x < x_qu - 2 else "der"].append((x, s))
            pares += _pares_de_filas(filas, npag)
    out = []
    for p in pares:
        es = re.sub(r"\s+", " ", p["es"]).strip()
        qu = re.sub(r"\s+", " ", p["qu"].replace("’", "'").replace("´", "'")).strip()
        if es and qu:
            out.append({"es": es, "qu": qu, "pagina": p["pagina"]})
    return out


def _pares_de_filas(filas: dict[float, dict], npag: int) -> list[dict]:
    pares: list[dict] = []
    actual = None
    for y in sorted(filas, reverse=True):
        if True:
            izq = " ".join(s for _, s in sorted(filas[y]["izq"])).strip()
            der = " ".join(s for _, s in sorted(filas[y]["der"])).strip()
            letras = [c for c in izq + der if c.isalpha()]
            if letras and sum(c.isupper() for c in letras) / len(letras) > 0.7:
                actual = None                                       # encabezado («CASTELLANO QUECHUA»)
                continue

            def sigue(prev: str, nuevo: str) -> bool:
                return bool(prev) and bool(nuevo) and (nuevo[:1].islower() or RE_CONECTOR_FINAL.search(prev)
                                                       or (prev.count("¿") > prev.count("?")))
            if actual and ((izq and der and sigue(actual["es"], izq) and sigue(actual["qu"], der))
                           or (izq and not der and sigue(actual["es"], izq))
                           or (der and not izq and (sigue(actual["qu"], der) or not actual["qu"]))):
                actual["es"] = (actual["es"] + " " + izq).strip()
                actual["qu"] = (actual["qu"] + " " + der).strip()
                continue
            actual = {"es": izq, "qu": der, "pagina": npag}
            pares.append(actual)
    return pares


PALABRAS_CLAVE_SALUD = "MinCul_Palabras_clave_salud_Quechua_Cusco.pdf"
CAPITULOS_PALABRAS_CLAVE = [                       # (páginas del PDF, capítulo)
    (range(13, 33), "I. Presentaciones, saludos y preguntas iniciales"),
    (range(33, 41), "II. El verbo tener y las partes del cuerpo"),
    (range(41, 89), "III. Atención integral de la salud reproductiva"),
    (range(89, 103), "IV. Medicación: efectos secundarios y forma de tomarla"),
]


def pares_palabras_clave_salud() -> list[dict]:
    """MINSA/Ministerio de Cultura, *Palabras clave para la atención en salud – Quechua* (traducción al quechua de
    Cusco): diálogos personal de salud ↔ usuaria. Tabla castellano | quechua."""
    p = dir_collao() / PALABRAS_CLAVE_SALUD
    if not p.exists():
        return []
    out = []
    for paginas, cap in CAPITULOS_PALABRAS_CLAVE:
        for par in pares_dos_columnas(p, paginas):
            par["capitulo"] = cap
            out.append(par)
    return out


MANUAL_JUSTICIA_COLLAO = "MinCul_Manual_justicia_Quechua_Cusco_Collao.pdf"
# Partes útiles para la consulta: atención y saludo, asegurar la comprensión, disculpas, datos personales, familia
# (pp. 18–47 del PDF) y descripción de personas, lugar y momento (pp. 82–89). Lo penal y legal no se usa.
PAGINAS_JUSTICIA = [range(18, 48), range(82, 90)]
RE_LEGAL = re.compile(r"(?i)juez|fiscal|denuncia|juzgado|abogad|polic|demanda|delit|comisar|audiencia|expediente|juicio|"
                      r"sentencia|acusad|testig|v[ií]ctima|agres|violen|violac|instituci|oficina|tr[aá]mite|documento|firma|"
                      r"celular|sala|fila|robo|robad|DNI|municipalidad|partida|s[oó]tano|piso|puerta|jefe")


def pares_justicia_collao() -> list[dict]:
    """Ministerio de Cultura (2015), *Manual para el empleo del quechua Cusco Collao en la administración de justicia*:
    solo las líneas de diálogo marcadas F (funcionario) / C (ciudadano), completas (empiezan en mayúscula y terminan
    en . ? !) y que no son del ámbito legal. F → Médico, C → Paciente."""
    p = dir_collao() / MANUAL_JUSTICIA_COLLAO
    if not p.exists():
        return []
    ign = r"MANUAL PARA EL|ADMINISTRACIÓN DE JUSTICIA|QUECHUA CUSCO COLLAO|^Quechua Cusco Collao$"
    out = []
    for paginas in PAGINAS_JUSTICIA:
        for x in pares_dos_columnas(p, paginas, ignorar=ign):
            m = re.match(r"^([FC])\s+(.*)$", x["es"])
            if not m:
                continue
            es, qu = m.group(2).strip(), x["qu"].strip()
            if not re.match(r"^[¿¡A-ZÁÉÍÓÚÑ]", es) or not re.search(r"[.?!]$", es) or not re.match(r"^[¿¡A-ZÁÉÍÓÚÑ]", qu):
                continue
            if RE_LEGAL.search(es):
                continue
            out.append({"es": es, "qu": qu, "pagina": x["pagina"], "rol": "Médico" if m.group(1) == "F" else "Paciente"})
    return out


def texto_pdf_ruta(p: Path) -> list[str]:
    """Texto por página de un PDF dado por ruta (fuentes collao nuevas). Con caché."""
    cache = _cache_dir() / f"pdf_{p.stem}.json"
    if cache.exists():
        datos = json.loads(cache.read_text(encoding="utf-8"))
        if datos.get("bytes") == p.stat().st_size:
            return datos["paginas"]
    import pypdfium2 as pdfium

    doc = pdfium.PdfDocument(p)
    paginas = [doc[i].get_textpage().get_text_range() for i in range(len(doc))]
    doc.close()
    escribir_json(cache, {"bytes": p.stat().st_size, "paginas": paginas})
    return paginas


def jw300_quz() -> dict[str, list[str]]:
    """AmericasNLP 2021, es-quz: JW300 en quechua de Cusco (Testigos de Jehová). Solo léxico de referencia: es prosa
    religiosa y no se graba (P4)."""
    base = RAIZ / CFG["rutas"]["fuentes"] / CFG["archivos_fuente"]["americasnlp_dir"] / "es-quz"
    pe, pq = base / "jw300.es-quz.es", base / "jw300.es-quz.quz"
    if not (pe.exists() and pq.exists()):
        return {"es": [], "qu": []}
    return {"es": _lineas(pe), "qu": _lineas(pq)}


GLOSARIO_PIAS = "MinCul_Glosario_aimara_quechua_PIAS_Puno.pdf"
GLOSARIO_COVID = "MinCul_Glosario_COVID19_VMI.pdf"
# La guía de señalética (MinCul_Guia_senaletica_lenguas_indigenas.pdf) NO se extrae: el ancho de sus columnas cambia en cada
# tabla, las celdas se parten y salía mezclada con aimara; son ~40 letreros y casi ninguno es médico. No vale el riesgo de
# guardar como «oficial» un par equivocado.


def _entradas_columna(segs: list, x_min: float, x_max: float = 9999, salto: float = 16, y_min: float = 50, y_max: float = 495) -> list[tuple[float, str]]:
    """Una columna de una tabla sin líneas: junta en una entrada las líneas seguidas. Devuelve (centro en y, texto)."""
    # misma línea (hasta 4 puntos de diferencia, p. ej. una inicial mayúscula más alta): de izquierda a derecha
    lineas = sorted((s for s in segs if x_min <= s[1] < x_max and y_min <= s[0] <= y_max), key=lambda s: (-round(s[0] / 4), s[1]))
    grupos: list[list] = []
    for s in lineas:
        if grupos and abs(grupos[-1][-1][0] - s[0]) <= salto:
            grupos[-1].append(s)
        else:
            grupos.append([s])
    return [(sum(g[0] for g in gr) / len(gr), " ".join(g[2] for g in gr)) for gr in grupos]


def pares_glosario_pias() -> list[dict]:
    """Glosario multilingüe de la PIAS Lago Titicaca I (Puno): frases de atención. Cada tema son dos páginas seguidas:
    a la izquierda el español y a la derecha aimara y «QUECHUA (Cusco - Collao)», en las mismas alturas."""
    p = dir_collao() / GLOSARIO_PIAS
    if not p.exists():
        return []
    seg = _segmentos_pdf(p)
    pares = []
    for pag_es in range(16, 28, 2):                     # páginas 17 a 28 del PDF
        es_col = _entradas_columna(seg[pag_es], 340)
        qu_col = _entradas_columna(seg[pag_es + 1], 340)
        for y, es in es_col:
            cerca = min(qu_col, key=lambda q: abs(q[0] - y), default=None)
            if cerca is None or abs(cerca[0] - y) > 12:
                continue
            qu = cerca[1]
            a, b = re.split(r"\s+/\s+", es), re.split(r"\s+/\s+", qu)
            for e, q in (zip(a, b) if len(a) == len(b) else [(es, qu)]):
                e = " ".join(e.split()).strip("“”\" ")
                # en la última página, dos frases entre comillas se parten a media línea del español
                e = {"Hasta pronto, que le vaya bien”. No dude": "Hasta pronto, que le vaya bien.",
                     "en contactarnos si necesita algo más.": "No dude en contactarnos si necesita algo más."}.get(e, e)
                q = " ".join(q.split()).replace("“", "").replace("”", "").strip()
                pares.append({"es": e, "qu": q.replace("¡K usisqam", "¡Kusisqam"), "pagina": pag_es + 2})    # letra inicial separada en el PDF
    return pares


def pares_glosario_covid() -> list[dict]:
    """Glosario multilingüe COVID-19 (Viceministerio de Interculturalidad): término en español y su línea
    «quechua Cusco Collao: …». Son términos, no oraciones: van al léxico y al texto paralelo, no a los bloques."""
    p = dir_collao() / GLOSARIO_COVID
    if not p.exists():
        return []
    paginas = [t.replace("\r", "") for t in texto_pdf_ruta(p)]
    txt = "\n".join(paginas)
    inicio_pag = []
    pos = 0
    for t in paginas:
        inicio_pag.append(pos)
        pos += len(t) + 1
    idx = [m.start() for m in re.finditer(r"quechua Cusco Collao:", txt)]
    re_termino = re.compile(r"^(?P<t>[^\n:]{2,90}?),\s*(?:m|f|adj|v|loc|expr|fr|sust|sigla)\b[^\n]*$", re.M)
    pares = []
    for k, i in enumerate(idx):
        trozo = txt[(idx[k - 1] if k else 0):i]
        ms = list(re_termino.finditer(trozo))
        if not ms:
            continue
        m = ms[-1]
        es = m.group("t").strip()
        if "]" in es and "[" not in es:                  # el término ocupa dos líneas: «brote [de una / enfermedad], m.»
            antes = trozo[:m.start()].rstrip().rsplit("\n", 1)[-1]
            es = f"{antes.strip()} {es}"
        crudo = txt[i + len("quechua Cusco Collao:"):i + 400]
        qu = re.split(r"\n(?:shipibo|ticuna|wampis|yanesha|Fuente|awaj|nomatsi)[^\n:]*:", crudo)[0]
        qu = re.sub(r"\s*Glosario\b.*$", "", " ".join(qu.split()))
        es = " ".join(es.replace("[", "").replace("]", "").replace("﻿", "").split())
        # «←» es la página que explica cómo leer el glosario; lo igual al español no enseña nada; «(EPP)» es una sigla partida
        if not qu or "←" in qu or es.startswith("(") or clave_normalizada(es) == clave_normalizada(qu):
            continue
        pagina = next((n + 1 for n in range(len(inicio_pag) - 1, -1, -1) if inicio_pag[n] <= i), 0)
        pares.append({"es": es, "qu": qu, "pagina": pagina})
    return pares


def pares_collao_extra() -> dict[str, list[dict]]:
    """Pares español–quechua de fuentes collao oficiales nuevas (Fuentes/collao/), por fuente. Entran como borrador
    de máxima calidad («fuente collao oficial») y al léxico de referencia."""
    return {"MINSA/MinCul – Palabras clave salud (Cusco)": pares_palabras_clave_salud(),
            "MinCul – Manual justicia Cusco Collao (diálogos)": pares_justicia_collao(),
            "MinCul – Glosario PIAS Lago Titicaca (Puno, frases de atención)": pares_glosario_pias(),
            "MinCul/VMI – Glosario COVID-19 (términos, Cusco Collao)": pares_glosario_covid()}


def textos_collao_sueltos() -> dict[str, list[str]]:
    """Quechua collao oficial que no viene en pares limpios: afiches COVID del MINSA (Cusco Collao). Solo léxico."""
    out = {}
    for p in sorted(dir_collao().glob("MINSA_*.pdf")) if dir_collao().exists() else []:
        out[p.stem] = texto_pdf_ruta(p)
    return out


def forma_del_libro(*columnas: str) -> str:
    """Forma ORIGINAL del libro de Lopera que el unificado guarda en quechua_marshall / kim1 / kim2 con el prefijo
    «Libro:». Si hay alternativas separadas por «||», se toma la primera."""
    for v in columnas:
        v = texto(v)
        if v.startswith("Libro:"):
            return v[len("Libro:"):].split("||")[0].strip()
    return ""


def texto_html_farfan() -> str:
    raw = fuente("web_html").read_bytes()
    try:
        h = raw.decode("utf-8")
        if "�" in h or "Ã" in h:
            raise UnicodeDecodeError("utf-8", b"", 0, 1, "mojibake")
    except UnicodeDecodeError:
        h = raw.decode("cp1252", errors="replace")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", h, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return html_mod.unescape(re.sub(r"\s+", " ", t)).strip()
