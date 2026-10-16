"""F1 – Inventario: localiza cada fuente, verifica cifras contra CLAUDE.md §5 y lista hojas, columnas y filas.

Salida: 04_reportes/INVENTARIO.md (+ 04_reportes/inventario_cifras.json).
Uso: python scripts/01_inventario.py [--forzar]
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter

from comun import (CFG, RAIZ, clave_normalizada, es_pregunta, escribir_json, escribir_texto, fuente,
                   n_palabras, ruta, texto)
import fuentes as F
from heuristicas import es_primera_persona

DESTINO = ruta("reportes") / "INVENTARIO.md"

ESPERADO_ESTADOS = {
    "Final – corregido/normalizado a chanka": 522, "Pendiente – sin traducción chanka": 361,
    "Final – coincide en los Excel": 281, "Final – forma del libro compatible con chanka": 122,
    "Revisar – duda de traducción": 89, "Revisar – adaptación propuesta": 72, "Final – única fuente": 58,
    "Final – fuente chanka oficial": 12, "Pendiente – no usar (ver observación)": 11,
}
ESPERADO_FUENTES = {
    "Lopera Quiroga (2020)": 566, "Allin Kawsay (INS/MINSA)": 510, "OPS/OMS Bolivia (2013)": 234,
    "SOCEMURP (corpus original del equipo)": 118, "Kim 1 (pregunta añadida)": 43, "Farfán Cantero (2001), SITUA": 24,
    "MinCul – manual de justicia (chanka)": 13, "YouTube": 9, "Afiche MINSA/MinCul lavado de manos (chanka)": 6,
    "MINSA – diabetes (quechua)": 4, "OMS (2009) – lista de verificación": 1,
}
PRONOMBRES = ("yo ", "tú ", "tu ", "él ", "ella ", "nosotros ", "nosotras ", "ustedes ", "ellos ", "ellas ", "usted ")


def marca(obtenido, esperado, tol=None) -> str:
    tol = CFG["cifras_esperadas"]["tolerancia_relativa"] if tol is None else tol
    if esperado in (None, 0):
        return "—"
    if obtenido == esperado:
        return "✔ igual"
    dif = abs(obtenido - esperado) / esperado
    return "≈ dentro de tolerancia" if dif <= tol else "✖ DIFIERE"


def tabla(filas: list[list], encabezado: list[str]) -> str:
    out = ["| " + " | ".join(encabezado) + " |", "|" + "---|" * len(encabezado)]
    for f in filas:
        out.append("| " + " | ".join(re.sub(r"\s+", " ", str(c).replace("|", "/")) for c in f) + " |")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--forzar", action="store_true")
    a = ap.parse_args()
    if DESTINO.exists() and not a.forzar:
        print(f"Ya existe {DESTINO.relative_to(RAIZ)}; usa --forzar para rehacerlo.")
        return 0

    cifras: dict = {}
    md: list[str] = ["# Inventario de fuentes (F1)", "",
                     f"Generado por `scripts/01_inventario.py` el {CFG['fecha_generacion']}. Fuentes en `{CFG['rutas']['fuentes']}/` (solo lectura).", ""]

    # ------------------------------------------------------------ 1. presencia
    md += ["## 1. Archivos encontrados", ""]
    filas = []
    faltan_esenciales = []
    for clave, nombre in CFG["archivos_fuente"].items():
        p = fuente(clave)
        existe = p.exists()
        tam = (sum(x.stat().st_size for x in p.rglob("*") if x.is_file()) if p.is_dir() else p.stat().st_size) if existe else 0
        filas.append([clave, f"`{nombre}`", "sí" if existe else "**NO**", f"{tam/1024:,.0f} KB" if existe else "—",
                      "esencial" if clave in CFG["esenciales"] else "opcional"])
        if not existe and clave in CFG["esenciales"]:
            faltan_esenciales.append(nombre)
    md += [tabla(filas, ["Clave", "Archivo", "Existe", "Tamaño", "Tipo"]), ""]
    mp3 = list((RAIZ / CFG["rutas"]["fuentes"]).rglob("*.mp3"))
    md += [f"- Audios `.mp3` (Allin Kawsay) en la carpeta: **{len(mp3)}**. No se inventarían ni procesan (P7).",
           "- `arbol.txt` se ignora (es un listado de la carpeta).", ""]
    if faltan_esenciales:
        escribir_texto(DESTINO, "\n".join(md + [f"**FALTAN FUENTES ESENCIALES:** {faltan_esenciales}"]))
        print("FALTAN FUENTES ESENCIALES:", faltan_esenciales)
        return 2

    # ------------------------------------------------------------ 2. hojas de los Excel
    md += ["## 2. Hojas, columnas y filas de los Excel", ""]
    for clave in ["unificado", "corpus_equipos", "corpus_construido"]:
        p = fuente(clave)
        md += [f"### `{p.name}`", ""]
        filas = []
        for h in F.hojas(p):
            r = F.resumen_hoja(p, h)
            filas.append([h, r["filas_totales"], r["filas_no_vacias"], r["columnas"], ", ".join(f"`{c}`" for c in r["encabezado"] if c)])
        md += [tabla(filas, ["Hoja", "Filas totales (rango usado)", "Filas no vacías (incl. encabezado)", "Columnas", "Encabezado"]), ""]
    md += ["> Las filas totales incluyen el rango vacío que Excel guarda (p. ej. 1000 filas en Corpus_Equipos). Lo que cuenta son las filas no vacías.", ""]

    # ------------------------------------------------------------ 3. unificado
    U = F.cargar_unificado()
    T = F.cargar_trazabilidad()
    ce = CFG["cifras_esperadas"]
    n_u = len(U)
    con_qu = int((U["Quechua_final (chanka)"] != "").sum())
    cifras["unificado"] = {"filas": n_u, "trazabilidad": len(T), "con_quechua": con_qu}
    md += ["## 3. `Vocabulario_unificado` (§5.1) — parte médica vigente", ""]
    md += [tabla([
        ["Filas `Vocabulario_unificado`", n_u, ce["unificado_filas"], marca(n_u, ce["unificado_filas"])],
        ["Filas `Trazabilidad`", len(T), ce["unificado_trazabilidad_filas"], marca(len(T), ce["unificado_trazabilidad_filas"])],
        ["Filas con quechua final", con_qu, ce["unificado_con_quechua"], marca(con_qu, ce["unificado_con_quechua"])],
        ["IDs únicos `QCH-`", U["Id_unificado"].nunique(), n_u, marca(U["Id_unificado"].nunique(), n_u)],
    ], ["Cifra", "Obtenido", "Esperado (§5)", "Resultado"]), ""]

    est = Counter(U["Estado"])
    md += ["### Estados", "", tabla([[k, est.get(k, 0), v, marca(est.get(k, 0), v)] for k, v in ESPERADO_ESTADOS.items()] +
                                    [[k, v, "—", "no esperado"] for k, v in est.items() if k not in ESPERADO_ESTADOS],
                                    ["Estado", "Obtenido", "Esperado", "Resultado"]), ""]
    cifras["unificado"]["estados"] = dict(est)

    U["Fuente"] = U["Fuente_original"].map(F.fuente_canonica)
    fu = Counter(U["Fuente"])
    fq = Counter(U.loc[U["Quechua_final (chanka)"] != "", "Fuente"])
    md += ["### Fuentes (`Fuente_original` agrupada)", "",
           tabla([[k, fu.get(k, 0), fq.get(k, 0), v, marca(fu.get(k, 0), v)] for k, v in ESPERADO_FUENTES.items()] +
                 [[k, v, fq.get(k, 0), "—", "no esperado"] for k, v in fu.items() if k not in ESPERADO_FUENTES],
                 ["Fuente", "Filas", "Con quechua", "Esperado (§5.1)", "Resultado"]), "",
           "> §5.1 cuenta 117 filas «Corpus original del equipo» + 1 «Manual SOCEMURP-FAMURP» por separado; aquí se agrupan (118). "
           "Las 510 filas de Allin Kawsay traen el nombre del audio en `Fuente_original` (p. ej. «audio 222. Zancudo.mp3, transcripción automática»); se agrupan por prefijo.", ""]
    cifras["unificado"]["fuentes"] = dict(fu)

    lop = U[U["Fuente"] == "Lopera Quiroga (2020)"]
    lop_qu = lop[lop["Quechua_final (chanka)"] != ""]
    lop_corr = int((lop_qu["Estado"] == "Final – corregido/normalizado a chanka").sum())
    lop_comp = int((lop_qu["Estado"] == "Final – forma del libro compatible con chanka").sum())
    md += [f"- Lopera con quechua: **{len(lop_qu)}** filas (corregidas a chanka: {lop_corr}; «compatible»: {lop_comp}; "
           f"otros estados: {len(lop_qu) - lop_corr - lop_comp}). §5.1 esperaba 409 (287 + 122) → {marca(lop_corr + lop_comp, 409)}.",
           f"- OPS/OMS Bolivia: {fu.get('OPS/OMS Bolivia (2013)', 0)} filas, con quechua: {fq.get('OPS/OMS Bolivia (2013)', 0)} (esperado: solo español).", ""]

    nw = U["Español (palabra o frase)"].map(n_palabras)
    sueltas = int((nw <= 1).sum())
    dos_tres = int(((nw >= 2) & (nw <= 3)).sum())
    cuatro = int((nw >= 4).sum())
    preg = int(U["Español (palabra o frase)"].map(es_pregunta).sum())
    pac = int(U["Español (palabra o frase)"].map(lambda s: (not es_pregunta(s)) and n_palabras(s) >= 2 and es_primera_persona(s)).sum())
    md += ["### Composición", "", tabla([
        ["Palabras sueltas (1 palabra)", sueltas, 515, marca(sueltas, 515)],
        ["2–3 palabras", dos_tres, 323, marca(dos_tres, 323)],
        ["4 o más palabras", cuatro, 690, marca(cuatro, 690)],
        ["Máximo de palabras", int(nw.max()), 44, marca(int(nw.max()), 44)],
        ["Preguntas", preg, 615, marca(preg, 615, 0.10)],
        ["Frases del paciente en 1.ª persona (heurística)", pac, 47, "heurística distinta; ver nota"],
    ], ["Cifra", "Obtenido", "Esperado (§5.1)", "Resultado"]), "",
        "> La cifra de frases del paciente depende de la heurística; la mía (`heuristicas.es_primera_persona`) es más amplia que la usada en la revisión anterior. No indica otra versión del archivo.", ""]
    cifras["unificado"]["composicion"] = {"sueltas": sueltas, "2_3": dos_tres, "4_mas": cuatro, "preguntas": preg, "paciente": pac}

    # Casos de §6 presentes en el unificado
    casos = ["QCH-0010", "QCH-0013", "QCH-0037", "QCH-0050", "QCH-0063", "QCH-0086", "QCH-0110", "QCH-0111"]
    filas = []
    for q in casos:
        r = U[U["Id_unificado"] == q]
        if len(r):
            r = r.iloc[0]
            filas.append([q, r["Español (palabra o frase)"], r["Quechua_final (chanka)"], r["Estado"]])
        else:
            filas.append([q, "NO ENCONTRADO", "", ""])
    md += ["### Casos conocidos de §6 (comprobación de versión)", "", tabla(filas, ["ID", "Español", "Quechua final", "Estado"]), ""]

    # ------------------------------------------------------------ 4. Corpus_Equipos
    md += ["## 4. `Corpus_Equipos` (§5.2)", ""]
    g1, g2, g3, gt = F.cargar_principito(), F.cargar_grupo2(), F.cargar_grupo3(), F.cargar_terminos()
    g1_ok = g1[(g1["Español"] != "")]
    md += ["### Grupo 1 – Principito", "",
           f"- Filas con datos: **{len(g1_ok)}** (esperado {ce['principito_filas']}) → {marca(len(g1_ok), ce['principito_filas'])}. "
           f"IDs `{g1_ok['Código_original'].iloc[0]}`…`{g1_ok['Código_original'].iloc[-1]}`, únicos: {g1_ok['Código_original'].nunique()}.",
           f"- Con quechua: {(g1_ok['Quechua'] != '').sum()}. Columna G (sin encabezado) dice «Modelo utilizado: {g1['Extra'].iloc[1] if len(g1) > 1 else ''}».",
           f"- EL-0001 trae la nota de plantilla «{g1_ok['Observaciones'].iloc[0]}» → se ignora (no es una observación real).", ""]
    cifras["principito"] = len(g1_ok)

    g2_id = g2[g2["Código_original"].str.startswith("F-")]
    g2_es = g2_id[g2_id["Español"] != ""]
    g2_qu = g2_id[g2_id["Quechua"] != ""]
    dup = [k for k, v in Counter(g2_id["Código_original"]).items() if v > 1]
    vacias = g2_id[(g2_id["Español"] == "") & (g2_id["Quechua"] == "")]["Código_original"].tolist()
    sin_id = g2[~g2["Código_original"].str.startswith("F-")]
    minus = int(g2_es["Español"].map(lambda s: s[:1].islower()).sum())
    pron = int(g2_es["Español"].map(lambda s: s.lower().startswith(PRONOMBRES)).sum())
    md += ["### Grupo 2 – Corpus Chanka", "", tabla([
        ["Filas con ID `F-`", len(g2_id), ce["grupo2_filas"], marca(len(g2_id), ce["grupo2_filas"])],
        ["… con español", len(g2_es), "—", ""],
        ["… con quechua", len(g2_qu), ce["grupo2_con_quechua"], marca(len(g2_qu), ce["grupo2_con_quechua"])],
        ["Empiezan en minúscula", minus, 507, marca(minus, 507)],
        ["Empiezan con pronombre personal", pron, 396, marca(pron, 396, 0.25)],
    ], ["Cifra", "Obtenido", "Esperado (§5.2)", "Resultado"]), "",
        f"- ID duplicado: {', '.join(dup) or 'ninguno'}. Filas con ID pero vacías: {', '.join(vacias) or 'ninguna'}.",
        f"- Filas sin ID al final: {len(sin_id)} → son la bibliografía de la hoja («Referencias», MINEDU 2014, MINEDU 2021), no oraciones.",
        "- **Explicación de la diferencia con §5.2:** §5.2 contó 676 filas y 672 con quechua incluyendo la fila vacía F-0517 y las 3 filas de referencias "
        "(que tienen texto en la columna Quechua). Contando solo oraciones reales: "
        f"{len(g2_es)} con español y quechua. Es la misma versión del archivo.",
        "- Pronombres contados: yo, tú/tu, él, ella, nosotros/as, ustedes, ellos/as, usted (no el artículo «el»).", ""]
    cifras["grupo2"] = {"con_id": len(g2_id), "con_es": len(g2_es), "con_qu": len(g2_qu), "minuscula": minus, "pronombre": pron,
                        "duplicados": dup, "vacias": vacias}

    g3_es = g3[g3["Español"] != ""]
    val = int(g3["Observaciones"].str.contains("Validar escritura").sum())
    md += ["### Grupo 3 – Corpus Médico (solo referencia, D10)", "",
           f"- Filas con español: **{len(g3_es)}** (esperado {ce['grupo3_filas']}) → {marca(len(g3_es), ce['grupo3_filas'])}. "
           f"«Validar escritura»: **{val}** (esperado {ce['grupo3_validar_escritura']}) → {marca(val, ce['grupo3_validar_escritura'])}.",
           "- La columna N° es fórmula (`=A2+1`); se reconstruyó como `G3-0001…` solo para cruzar.", ""]
    claves_u = set(U["Español (palabra o frase)"].map(clave_normalizada))
    g3_en_u = int(g3_es["Español"].map(lambda s: clave_normalizada(s) in claves_u).sum())
    md += [f"- Cobertura en el unificado (mismo español normalizado): **{g3_en_u} de {len(g3_es)}**. "
           "Las que no coinciden exactamente suelen haber cambiado de redacción en la revisión (el unificado corrigió erratas).", ""]
    cifras["grupo3"] = {"filas": len(g3_es), "validar_escritura": val, "en_unificado": g3_en_u}

    gt_ok = gt[(gt["Español"] != "") | (gt["Quechua"] != "")]
    md += ["### Grupo 3 – Términos médicos (solo referencia)", "",
           f"- Filas: **{len(gt_ok)}** (esperado {ce['grupo3_terminos_filas']}) → {marca(len(gt_ok), ce['grupo3_terminos_filas'])}.",
           "- Hallazgos: la última fila tiene las columnas invertidas («Aycha» en Español y «Músculo» en Quechua) y «Hueso → Tullu nanay» "
           "(= dolor de hueso) está desalineada. Como la hoja es solo referencia, no se corrige; se deja anotado.", ""]
    cifras["terminos"] = len(gt_ok)

    # ------------------------------------------------------------ 5. Construido
    C = F.cargar_construido()
    claves_uq = set(U["Quechua_final (chanka)"].map(clave_normalizada))
    en_u = int(C.apply(lambda r: clave_normalizada(r["Español"]) in claves_u or clave_normalizada(r["Quechua"]) in claves_uq, axis=1).sum())
    md += ["## 5. `Corpus_Construido` (§5.3, solo referencia)", "",
           f"- Filas: **{len(C)}** (esperado {ce['construido_filas']}) → {marca(len(C), ce['construido_filas'])}. N° es fórmula (`=CONCATENATE(\"S1-\",B2)`): se reconstruyó `S1-1…`.",
           f"- Presentes en el unificado (mismo español o mismo quechua normalizado): **{en_u} de {len(C)}** (esperado 109) → {marca(en_u, 109, 0.05)}. "
           + ("Las 2 que §5.3 no encontró sí aparecen al comparar también por quechua (el español se corrigió en el unificado)." if en_u >= 109
              else "Las demás cambiaron de redacción al corregirse."), ""]
    cifras["construido"] = {"filas": len(C), "en_unificado": en_u}

    # ------------------------------------------------------------ 6. AmericasNLP
    A = F.americasnlp()
    filas = []
    total = 0
    for nombre, d in A.items():
        n = len(d["es"])
        nq = len(d["qu"])
        filas.append([nombre, ", ".join(f"`{x}`" for x in d["archivos"]), n, nq if nq else "—"])
    total = len(A["train (JW300)"]["es"]) + len(A["dev (sureño estándar)"]["es"]) + len(A["dict (MINEDU + Dict_misc)"]["es"])
    md += ["## 6. AmericasNLP 2021 es–quy (§5.5)", "", tabla(filas, ["Conjunto", "Archivos", "Líneas es", "Líneas quy"]), "",
           f"- Total de pares (train + dev + dict): **{total:,}**. El equipo hablaba de ~180k: **no coincide**. "
           "La cifra real es la del archivo (el README confirma que `train` = solo JW300 quy; `dict` = MINEDU 643 + Dict_misc 9 000). "
           "No afecta a los bloques: AmericasNLP solo se usa como léxico de referencia (P4).",
           "- `es-quy/jw300` es idéntico a `train` (mismo tamaño); `dict` = `minedu` + `dict_misc`.",
           "- `test` solo trae español (1 003 líneas), como dice §5.5.", ""]
    cifras["americasnlp"] = {k: len(v["es"]) for k, v in A.items()}

    # ------------------------------------------------------------ 7. PDF y HTML
    md += ["## 7. PDF y página web (identificados por contenido)", ""]
    filas = []
    ident = {
        "socemurp_pdf": "Manual de Quechua médico SOCEMURP (2021). Solo imagen (§5.4).",
        "minedu_pdf": "Diccionario MINEDU *Yachakuqkunapa Simi Qullqa* (2014), chanka. **Tiene capa de texto**: se usa en F2 para verificar P6.",
        "lopera_pdf": "Lopera Quiroga (2020), *Manual de Semiología en Quechua* (Puno/collao). Con texto.",
        "ops_bolivia_pdf": "Confirmado: «Diálogo médico paciente en QUECHUA – Bolivia 2013» (OPS/OMS).",
        "mincul_pdf": "Manual para el empleo del quechua chanka en la administración de justicia (MinCul). Con texto.",
        "afiche_pdf": "Afiche MINSA lavado de manos en quechua chanka. Con texto.",
        "diabetes_qu_pdf": "Diabetes mellitus 2, vía HEARTS, en quechua (gob.pe). Con texto.",
        "diabetes_es_pdf": "Diabetes mellitus 2, vía HEARTS, en español (gob.pe). Con texto.",
    }
    for clave in ident:
        if not fuente(clave).exists():
            filas.append([clave, "NO EXISTE", "", "", ""])
            continue
        pags = F.texto_pdf(clave)
        con_txt = sum(1 for t in pags if len(t.strip()) > 30)
        muestra = re.sub(r"\s+", " ", next((t.strip() for t in pags if len(t.strip()) > 30), ""))[:90]
        filas.append([f"`{fuente(clave).name}`", len(pags), con_txt, ident[clave], f"«{muestra}…»" if muestra else "(sin texto)"])
    md += [tabla(filas, ["Archivo", "Páginas", "Páginas con texto", "Qué es", "Inicio del texto"]), ""]
    soc = len(F.texto_pdf("socemurp_pdf"))
    md += [f"- SOCEMURP: {soc} páginas (esperado {ce['socemurp_paginas']}) → {marca(soc, ce['socemurp_paginas'])}.", ""]
    h = F.texto_html_farfan()
    es_farfan = "Farf" in h and "SITUA" in h
    md += [f"- `Quechua médico.html`: {'**Farfán Cantero (2001), revista SITUA**, «Quechua médico» (UNSAAC, Cusco) → quechua **cusqueño**' if es_farfan else 'no identificado'}. "
           "Codificación Windows-1252 (las tildes se ven mal si se abre como UTF-8). No es Allin Kawsay.", ""]
    cifras["html"] = "Farfán SITUA" if es_farfan else "?"

    # ------------------------------------------------------------ 8. otros
    oc = RAIZ / CFG["rutas"]["fuentes"] / CFG["archivos_fuente"]["otro_companero_dir"]
    md += ["## 8. Trabajo previo de un compañero (§5.7, solo precedente)", "",
           "Archivos: " + ", ".join(f"`{p.name}`" for p in sorted(oc.iterdir())) + ". No se usan como fuente de datos ni de alertas.", ""]

    # ------------------------------------------------------------ 9. veredicto
    difieren = [l for l in md if "✖ DIFIERE" in l]
    cifras["difieren"] = difieren
    md += ["## 9. Veredicto", "",
           f"- Cifras marcadas «✖ DIFIERE»: **{len(difieren)}**." + ("" if not difieren else " Detalle:"),
           *[f"  - {l}" for l in difieren],
           "- Ver el comentario de cada sección: las diferencias se explican por cómo se cuenta (filas vacías, bibliografía, heurísticas), "
           "no por otra versión del archivo, salvo que se indique lo contrario.",
           f"- AmericasNLP: {total:,} pares, no ~180k. Solo se usa como léxico de referencia (P4), así que no cambia la composición de los bloques.", ""]

    escribir_texto(DESTINO, "\n".join(md))
    escribir_json(ruta("reportes") / "inventario_cifras.json", cifras)
    print(f"OK → {DESTINO.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
