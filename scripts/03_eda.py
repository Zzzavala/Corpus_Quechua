"""F3 – EDA: describe el corpus con números ANTES de limpiar (§9.1).

Entrada: checkpoint F2. Salidas: 04_reportes/EDA.md, figuras en 04_reportes/fig/, checkpoint F3 (registros + medidas).
Uso: python scripts/03_eda.py [--forzar]
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter

import numpy as np
import pandas as pd

from comun import CFG, RAIZ, asegurar_dir, cargar_checkpoint, clave_normalizada, escribir_texto, guardar_excel, guardar_seguro, n_palabras, ruta, ruta_checkpoint, sin_tildes
from dedup import grupos_casi_duplicados
import graficos as G
from graficos import plt
import quechua as Q
from qa import revisar_fila

DESTINO = ruta("reportes") / "EDA.md"
FIG = asegurar_dir(ruta("figuras"))
CK = ruta_checkpoint("F3_eda")

NOMBRE_POOL = {"principito": "Principito (G1)", "g2_diccionario": "G2 frases variadas", "g2_ejercicio": "G2 ejercicios",
               "medico": "Médico (unificado)"}
TEMAS = {
    "fiebre": r"fiebre|calentura", "tos": r"\btos\b|toses|flema|esputo", "vómito/náusea": r"vomit|vómit|náusea|nausea|arcada",
    "diarrea/deposiciones": r"diarrea|deposici|heces|estreñ|caca", "dolor de cabeza": r"dolor de cabeza|duele (la|mi) cabeza",
    "dolor de estómago/barriga": r"estómago|estomago|barriga|abdomen|vientre", "orina": r"orin|pis\b",
    "respirar/falta de aire": r"respir|ahog|falta de aire|aire", "alergias": r"alerg", "medicamentos/dosis": r"medicament|pastilla|remedio|dosis|tableta|jarabe|cada \w+ horas",
    "embarazo": r"embaraz|gestant|parto", "niños": r"niñ[oa]|bebé|bebe\b|hij[oa]|wawa", "sangrado": r"sangr",
    "desmayo/convulsión": r"desmay|convuls|conocimiento", "deshidratación": r"deshidrat|sed\b|boca seca",
    "volver/control": r"regres|vuelv|volver|control|cita", "¿entendió?": r"entend",
    "tranquilizar": r"tranquil|no se preocupe|no te preocupes|calma",
}


def guardar_fig(fig, nombre):
    destino = FIG / nombre
    guardar_seguro(destino, lambda tmp: fig.savefig(tmp, format="png"))
    plt.close(fig)
    return f"fig/{nombre}"


def tabla(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    out = ["| " + " | ".join(str(c) for c in cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        out.append("| " + " | ".join(re.sub(r"\s+", " ", str(v)).replace("|", "/") for v in r.values) + " |")
    return "\n".join(out)


def conteo(serie: pd.Series, nombre: str) -> pd.DataFrame:
    c = serie.replace("", "(vacío)").value_counts()
    return pd.DataFrame({nombre: c.index, "Filas": c.values, "%": (100 * c.values / c.values.sum()).round(1)})


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--forzar", action="store_true")
    a = ap.parse_args()
    if DESTINO.exists() and CK.exists() and not a.forzar:
        print(f"Ya existe {DESTINO.relative_to(RAIZ)}; usa --forzar.")
        return 0

    R = cargar_checkpoint("F2_ingesta")["Registros"]
    R["Pool_n"] = R["Pool"].map(NOMBRE_POOL)
    con_texto = R[(R["Español"] != "")].copy()

    # ---------------------------------------------------------------- medidas por fila
    R["pal_es"] = R["Español"].map(n_palabras)
    R["car_es"] = R["Español"].str.len()
    R["pal_qu"] = R["Quechua_borrador"].map(lambda s: len(Q.tokens_qu(s)))
    R["car_qu"] = R["Quechua_borrador"].str.len()
    R["ratio_qu_es"] = np.where((R["car_es"] > 0) & (R["car_qu"] > 0), R["car_qu"] / R["car_es"].clip(lower=1), np.nan)
    avisos = []
    sufs = []
    for _, r in R.iterrows():
        oficial = r["Tipo_borrador"] == "fuente chanka oficial"
        av = revisar_fila(r["Español"], r["Quechua_borrador"], r["Dominio"], oficial, r["Estado_unificado"], r["Observaciones_heredadas"])
        avisos.append(av)
        sufs.append(sorted(Q.unidades_cobertura(r["Quechua_borrador"])["sufijo"]) if r["Quechua_borrador"] else [])
    R["avisos"] = avisos
    R["sufijos"] = sufs
    for tipo in ["ORTO", "VARIEDAD", "PRESTAMO", "ALINEACION", "SENTIDO", "TRANSCRIPCION", "OOV"]:
        R[f"av_{tipo}"] = R["avisos"].map(lambda av, t=tipo: any(x[0] == t and (t != "PRESTAMO" or x[1] == "ALTA") for x in av))
    R["glotal"] = R["avisos"].map(lambda av: any("glotalizada" in d for t, s, d in av))
    R["vocal_eo"] = R["avisos"].map(lambda av: any("vocal e/o" in d for t, s, d in av))
    R["castellana"] = R["avisos"].map(lambda av: any("castellana" in d or "fuera del alfabeto" in d for t, s, d in av))
    R["clave_es"] = R["Español"].map(clave_normalizada)
    R["clave_qu"] = R["Quechua_borrador"].map(clave_normalizada)

    md = ["# EDA del corpus (F3) — antes de limpiar", "",
          f"Generado por `scripts/03_eda.py` desde el checkpoint F2 ({CFG['fecha_generacion']}). "
          "Todo se mide **antes** de la limpieza (F4). Las cifras de rasgos del quechua son **sospechas automáticas**: "
          "Claude no es hablante de chanka.", ""]

    # ---------------------------------------------------------------- 1. conteos
    md += ["## 1. Cuántas filas hay y de dónde salen", ""]
    t = R.groupby(["Dominio", "Pool_n"]).size().reset_index(name="Filas").rename(columns={"Pool_n": "Pool"})
    md += [tabla(t), "",
           "- **General** = Principito (traducción automática) + Grupo 2. **Médico** = vocabulario unificado (1 528 filas).",
           "- Grupo 2 incluye 4 filas que no son oraciones (F-0517 vacía y 3 de bibliografía); se descartan en F4.", ""]
    for col, titulo_ in [("Fuente", "Fuente"), ("Variedad_fuente", "Variedad de la fuente"), ("Tipo_borrador", "Tipo de borrador"),
                         ("Estado_unificado", "Estado en el unificado (solo médico)")]:
        datos = R[col] if col != "Estado_unificado" else R.loc[R["Dominio"] == "Médico", col]
        md += [f"### {titulo_}", "", tabla(conteo(datos, titulo_)), ""]
    m = R[R["Dominio"] == "Médico"]
    md += ["### Etapa de la consulta (médico, mapeo §11.3)", "", tabla(conteo(m["Etapa_consulta"], "Etapa")), "",
           "### Rol (médico, heurística)", "", tabla(conteo(m["Rol"], "Rol")), "",
           "> «—» = palabra suelta o léxico (no tiene hablante). Rol se decide por el español: preguntas y órdenes → Médico; "
           "1.ª persona («me duele», «tengo», «sí, …») → Paciente. Ver `scripts/heuristicas.py`.", ""]
    esc = m["Escenario"].str.split(" › ").str[0].value_counts().head(30)
    md += ["### Secciones del unificado (las 30 más grandes)", "",
           tabla(pd.DataFrame({"Sección": esc.index, "Filas": esc.values})), ""]

    fu = R["Fuente"].value_counts()
    fig, ax = plt.subplots(figsize=(8, 5.2))
    G.barras_h(ax, list(fu.index), list(fu.values))
    ax.set_xlabel("Filas")
    top = G.titulo(fig, "Filas por fuente (antes de limpiar)", "Médico: Lopera y Allin Kawsay dominan; general: Grupo 2 > Principito")
    fig.tight_layout(rect=(0, 0, 1, top))
    md += [f"![Filas por fuente]({guardar_fig(fig, 'f01_filas_por_fuente.png')})", ""]

    # ---------------------------------------------------------------- 2. longitudes
    md += ["## 2. Longitudes (palabras y caracteres)", ""]
    filas = []
    for pool, g in R[R["Español"] != ""].groupby("Pool_n"):
        for lado, c_pal, c_car in [("español", "pal_es", "car_es"), ("quechua", "pal_qu", "car_qu")]:
            x = g.loc[g[c_car] > 0, c_pal]
            y = g.loc[g[c_car] > 0, c_car]
            if len(x) == 0:
                continue
            filas.append([pool, lado, len(x), int(x.min()), round(float(x.median()), 1), round(float(x.quantile(0.9)), 1), int(x.max()),
                          round(float(y.median()), 1), int(y.max())])
    md += [tabla(pd.DataFrame(filas, columns=["Pool", "Lado", "Filas", "Mín. pal.", "Mediana pal.", "P90 pal.", "Máx. pal.", "Mediana car.", "Máx. car."])), ""]
    largas = R[R["pal_es"] > CFG["limpieza"]["max_palabras_sin_partir"]].sort_values("pal_es", ascending=False)
    md += [f"- Oraciones con más de {CFG['limpieza']['max_palabras_sin_partir']} palabras en español: **{len(largas)}** "
           f"({', '.join(f'{k}: {v}' for k, v in largas['Pool_n'].value_counts().items())}). Las 5 más largas:", ""]
    for _, r in largas.head(5).iterrows():
        md.append(f"  - `{r['Código_original']}` ({r['pal_es']} pal.): «{r['Español'][:160]}{'…' if len(r['Español']) > 160 else ''}»")
    md.append("")
    fig, axs = plt.subplots(1, 4, figsize=(11, 3.2), sharey=False)
    for ax, (pool, g) in zip(axs, R[R["Español"] != ""].groupby("Pool_n")):
        ax.hist(g["pal_es"].clip(upper=30), bins=range(1, 32), color=G.SERIES[0], rwidth=0.8)
        ax.set_title(pool, fontsize=9.5)
        ax.set_xlabel("palabras (español; 30 = 30+)")
        ax.axvline(CFG["limpieza"]["max_palabras_sin_partir"] + 0.5, color=G.APAGADO, lw=1)
    axs[0].set_ylabel("Filas")
    top = G.titulo(fig, "Longitud del español por pool", "La línea gris marca 20 palabras (más largo → partir o descartar)")
    fig.tight_layout(rect=(0, 0, 1, top))
    md += [f"![Longitud del español]({guardar_fig(fig, 'f02_longitud_espanol.png')})", ""]

    # ---------------------------------------------------------------- 3. tipo de oración
    md += ["## 3. Palabras sueltas vs. frases; preguntas, afirmaciones y órdenes", ""]
    t = pd.crosstab(R.loc[R["Español"] != "", "Pool_n"], R.loc[R["Español"] != "", "Tipo_oración"])
    md += [tabla(t.reset_index().rename(columns={"Pool_n": "Pool"})), "",
           f"- Palabras sueltas (1 palabra) en el médico: **{int((m['Tipo_oración'] == 'palabra').sum())}** → no se graban solas (§10.2): van a `Lexico`.",
           f"- Frases de 2–3 palabras en el médico: **{int(((m['pal_es'] >= 2) & (m['pal_es'] <= 3)).sum())}** (muchas son términos: «dolor de cabeza»).", ""]

    # ---------------------------------------------------------------- 4. duplicados
    md += ["## 4. Duplicados exactos y casi duplicados", ""]
    filas = []
    sim_resumen = {}
    for pool, g in R[R["Español"] != ""].groupby("Pool_n"):
        dup_es = int(g["clave_es"].duplicated().sum())
        gq = g[g["clave_qu"] != ""]
        dup_qu = int(gq["clave_qu"].duplicated().sum())
        unicos = g.drop_duplicates("clave_es")
        res = grupos_casi_duplicados(list(unicos["Español"]), CFG["limpieza"]["similitud_casi_duplicado"], CFG["limpieza"]["max_parafrasis"],
                                     list(unicos["Quechua_borrador"]))
        n_grupos_multi = sum(1 for gi, cnt in Counter(x[0] for x in res).items() if cnt > 1)
        sobran = sum(1 for x in res if x[1] is not None)
        sim_resumen[pool] = (len(g), dup_es, sobran)
        filas.append([pool, len(g), dup_es, dup_qu, n_grupos_multi, sobran])
    md += [tabla(pd.DataFrame(filas, columns=["Pool", "Filas", "Español repetido (exacto)", "Quechua repetido (exacto)",
                                              "Grupos de casi duplicados (≥90)", "Sobrarían (>2 por grupo)"])), "",
           "- «Exacto» = igual tras normalizar (minúsculas, sin tildes ni signos).",
           f"- Casi duplicado = similitud del español ≥ {CFG['limpieza']['similitud_casi_duplicado']} **y** misma polaridad (sí/no) **y** mismos números "
           "(decisión propia: «ellos bajan al río» y «ellos no bajan al río» no son paráfrasis). Se conservan hasta 2 por grupo, "
           "salvo que tengan el **mismo borrador quechua** (entonces queda 1: grabar dos veces lo mismo no aporta).",
           "- Quechua repetido con español distinto es típico de los ejercicios del Grupo 2 («ellos/ellas bajan al río» → «Paykuna mayuman uraykunku»).", ""]
    ej = R[(R["Pool"] == "g2_ejercicio") & R.duplicated("clave_qu", keep=False) & (R["clave_qu"] != "")].sort_values("clave_qu").head(6)
    for _, r in ej.iterrows():
        md.append(f"  - `{r['Código_original']}` «{r['Español']}» → «{r['Quechua_borrador']}»")
    md.append("")

    # ---------------------------------------------------------------- 5. rasgos no chanka
    md += ["## 5. Rasgos no chanka y letras fuera de la convención, por fuente", ""]
    cq = R[R["Quechua_borrador"] != ""]
    filas = []
    for fuente, g in cq.groupby("Fuente"):
        n = len(g)
        filas.append([fuente, n, f"{100 * g['glotal'].mean():.0f} %", f"{100 * g['vocal_eo'].mean():.0f} %", f"{100 * g['castellana'].mean():.0f} %",
                      f"{100 * g['av_VARIEDAD'].mean():.0f} %", f"{100 * g['av_PRESTAMO'].mean():.0f} %", f"{100 * g['av_TRANSCRIPCION'].mean():.0f} %"])
    t = pd.DataFrame(filas, columns=["Fuente", "Filas con quechua", "Glotal./aspir.", "Vocal e/o", "c/qu/j/hu o letra ajena",
                                     "Rasgo de otra variedad", "Préstamo sin adaptar", "Posible transcripción de oído"])
    md += [tabla(t.sort_values("Filas con quechua", ascending=False)), "",
           "- Glotalizadas/aspiradas, e/o y escritura castellana se **corrigen mecánicamente** en F4 (§10.3, registradas en `Cambios`). "
           "Lo demás (variedad, préstamos, transcripción) **solo se marca** en `QA` para el traductor.",
           "- El unificado ya había normalizado casi todo: lo que queda allí es poco. Los ejercicios y frases del Grupo 2 están limpios en ortografía; "
           "el Principito concentra los préstamos (traducción automática).", ""]
    tipos = ["av_VARIEDAD", "av_PRESTAMO", "av_TRANSCRIPCION"]
    nombres = ["Rasgo de otra variedad", "Préstamo sin adaptar", "Posible transcripción de oído"]
    fu_orden = cq["Fuente"].value_counts().index[:9]
    fig, ax = plt.subplots(figsize=(8.5, 5.4))
    alto = 0.25
    for k, (tcol, nom) in enumerate(zip(tipos, nombres)):
        vals = [100 * cq.loc[cq["Fuente"] == f, tcol].mean() for f in fu_orden]
        G.barras_h(ax, list(fu_orden), vals, color=G.SERIES[k], alto=alto, offset=(k - 1) * (alto + 0.03), fmt="{:.0f} %", label=nom)
    ax.set_xlabel("% de filas con quechua de esa fuente")
    ax.legend(loc="lower right", fontsize=8.5)
    top = G.titulo(fig, "Sospechas en el quechua por fuente", "Solo avisos para el traductor; no son correcciones")
    fig.tight_layout(rect=(0, 0, 1, top))
    md += [f"![Rasgos por fuente]({guardar_fig(fig, 'f03_rasgos_por_fuente.png')})", ""]

    # ---------------------------------------------------------------- 6. alineación
    md += ["## 6. Relación de longitud quechua/español (alineación)", ""]
    rr = R["ratio_qu_es"].dropna()
    lo, hi = CFG["qa"]["ratio_longitud_min"], CFG["qa"]["ratio_longitud_max"]
    fuera = R[(R["ratio_qu_es"] < lo) | (R["ratio_qu_es"] > hi)]
    md += [f"- Relación en caracteres (quechua ÷ español): mediana **{rr.median():.2f}**, P5 {rr.quantile(0.05):.2f}, P95 {rr.quantile(0.95):.2f}.",
           f"- Fuera de [{lo}, {hi}]: **{len(fuera)}** filas ({', '.join(f'{k}: {v}' for k, v in fuera['Pool_n'].value_counts().items())}). "
           "Casi todas son palabras sueltas o frases muy cortas, donde la relación es inestable. Ejemplos de frases:", ""]
    for _, r in fuera[fuera["pal_es"] >= 4].sort_values("ratio_qu_es").head(6).iterrows():
        md.append(f"  - {r['ratio_qu_es']:.2f} · `{r['Código_original']}` «{r['Español'][:70]}» ↔ «{r['Quechua_borrador'][:70]}»")
    md.append("")
    md += [f"- Números que no coinciden español↔quechua: **{int(R['avisos'].map(lambda av: any('números' in d for t, s, d in av)).sum())}** filas; "
           f"sospechas de sentido (tipo *pisi*/*achka*, *wata*/*killa*, negación): **{int(R['av_SENTIDO'].sum())}** filas.", ""]
    fig, ax = plt.subplots(figsize=(8, 3.2))
    ax.hist(rr.clip(upper=3), bins=np.arange(0, 3.05, 0.1), color=G.SERIES[0], rwidth=0.85)
    ax.axvspan(lo, hi, color=G.SECUENCIAL[1], alpha=0.5, lw=0)
    ax.set_xlabel("caracteres quechua ÷ caracteres español (3 = 3 o más)")
    ax.set_ylabel("Filas")
    top = G.titulo(fig, "Alineación por longitud", f"Banda celeste = rango esperado [{lo}, {hi}]")
    fig.tight_layout(rect=(0, 0, 1, top))
    md += [f"![Relación de longitud]({guardar_fig(fig, 'f04_relacion_longitud.png')})", ""]

    # ---------------------------------------------------------------- 7. vocabulario
    md += ["## 7. Vocabulario del quechua", ""]
    filas = []
    todas = Counter()
    for pool, g in cq.groupby("Pool_n"):
        toks = [Q.norm_ñ(t) for s in g["Quechua_borrador"] for t in Q.tokens_qu(s)]
        todas.update(toks)
        tipos_ = set(toks)
        no_lx = [t for t in tipos_ if len(t) >= 3 and not Q.es_prestamo_o_propio(t)[0] and not Q.conocida(t)]
        filas.append([pool, len(toks), len(tipos_), f"{100 * len(no_lx) / max(len(tipos_), 1):.0f} %", ", ".join(sorted(no_lx)[:8])])
    md += [tabla(pd.DataFrame(filas, columns=["Pool", "Palabras (tokens)", "Palabras distintas", "Distintas no halladas en AmericasNLP/diccionarios", "Ejemplos"])), "",
           "- Léxico de referencia: JW300 quy (palabras que aparecen 2+ veces), diccionario MINEDU (PDF y AmericasNLP), Dict_misc, manual MinCul, afiche y "
           "material de diabetes en quechua; se consideran solo formas escritas con el alfabeto chanka. Una palabra cuenta como hallada si ella o su raíz "
           "(quitando sufijos) aparece. «No hallada» no significa error: el léxico médico casi no está en esos textos.", "",
           "**Las 25 palabras quechuas más frecuentes:** " + ", ".join(f"{w} ({n})" for w, n in todas.most_common(25)), ""]

    # ---------------------------------------------------------------- 8. sufijos
    md += ["## 8. Cobertura de sufijos (§11.1): qué enseña cada pool", ""]
    lista = [f"-{s}" for s in sorted({s for v in Q.SUFIJOS_CATEGORIA.values() for s in v})]
    pools = [p for p in NOMBRE_POOL.values() if p in set(cq["Pool_n"])]
    mat = np.zeros((len(pools), len(lista)))
    for i, p in enumerate(pools):
        g = cq[cq["Pool_n"] == p]
        c = Counter(s for lst in g["sufijos"] for s in lst)
        for j, s in enumerate(lista):
            mat[i, j] = 100 * c.get(s, 0) / max(len(g), 1)
    filas = []
    for i, p in enumerate(pools):
        presentes = [lista[j] for j in range(len(lista)) if mat[i, j] > 0]
        ausentes = [lista[j] for j in range(len(lista)) if mat[i, j] == 0]
        filas.append([p, f"{len(presentes)} de {len(lista)}", ", ".join(ausentes) or "—"])
    md += [tabla(pd.DataFrame(filas, columns=["Pool", "Sufijos presentes", "Ausentes"])), "",
           "> Segmentación **heurística** (quita sufijos desde el final, el más largo primero, hasta una raíz del diccionario). "
           "Es aproximada: confunde homófonos (-n persona/posesivo, -y imperativo/posesivo, -pa genitivo/derivativo). Sirve para comparar pools, no como análisis morfológico.", ""]
    fig, ax = plt.subplots(figsize=(12, 2.9))
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("azul", G.SECUENCIAL)
    im = ax.imshow(np.minimum(mat, 40), aspect="auto", cmap=cmap, vmin=0, vmax=40)
    ax.set_yticks(range(len(pools)))
    ax.set_yticklabels(pools)
    ax.set_xticks(range(len(lista)))
    ax.set_xticklabels(lista, rotation=90, fontsize=7.5)
    ax.grid(False)
    cb = fig.colorbar(im, ax=ax, fraction=0.02, pad=0.01)
    cb.set_label("% de frases (40 = 40 %+)", color=G.TINTA_2, fontsize=8)
    cb.outline.set_visible(False)
    top = G.titulo(fig, "Cobertura de sufijos por pool", "Celda blanca = el pool no trae ese sufijo")
    fig.tight_layout(rect=(0, 0, 1, top))
    md += [f"![Cobertura de sufijos]({guardar_fig(fig, 'f05_cobertura_sufijos.png')})", ""]

    # ---------------------------------------------------------------- 9. cobertura clínica
    md += ["## 9. Cobertura clínica", ""]
    mm = m[(m["Etapa_consulta"] != "Léxico") & (m["Rol"] != "—") & (m["Estado_unificado"] != "Pendiente – no usar (ver observación)")]
    t = pd.crosstab(mm["Etapa_consulta"], mm["Rol"]).reset_index().rename(columns={"Etapa_consulta": "Etapa"})
    md += ["### Frases por etapa y rol (sin léxico)", "", tabla(t), ""]
    t2 = pd.crosstab(mm.loc[mm["Etapa_B01"] != "", "Etapa_B01"], mm.loc[mm["Etapa_B01"] != "", "Rol"])
    orden_b01 = [e["etapa"] for e in CFG["medico"]["b01_etapas"]]
    t2 = t2.reindex([e for e in orden_b01 if e in t2.index]).reset_index().rename(columns={"Etapa_B01": "Etapa (B01)"})
    md += ["### Material para la consulta completa de B01 (§11.2)", "", tabla(t2), ""]
    pac_esc = mm[mm["Rol"] == "Paciente"]["Escenario"].value_counts()
    esc_sin_pac = sorted(set(mm["Escenario"]) - set(pac_esc.index))
    md += [f"- Frases del **paciente** en todo el unificado: **{int((mm['Rol'] == 'Paciente').sum())}** frente a **{int((mm['Rol'] == 'Médico').sum())}** del médico.",
           f"- Escenarios **sin ninguna frase del paciente**: {len(esc_sin_pac)} de {mm['Escenario'].nunique()}. Los que sí tienen:", ""]
    md += [tabla(pd.DataFrame({"Escenario": pac_esc.index, "Frases del paciente": pac_esc.values})), ""]
    filas = []
    for tema, pat in TEMAS.items():
        sel = mm[mm["Español"].map(lambda s, p=pat: bool(re.search(p, s, re.I)))]
        filas.append([tema, len(sel), int((sel["Rol"] == "Médico").sum()), int((sel["Rol"] == "Paciente").sum())])
    md += ["### Temas clave (búsqueda por palabras en el español)", "",
           tabla(pd.DataFrame(filas, columns=["Tema", "Frases", "Médico", "Paciente"])), ""]

    fig, ax = plt.subplots(figsize=(8, 3.6))
    et = [e for e in ["Inicio", "Recolección de información", "Examen físico", "Explicación y plan", "Relación", "Sensible"]]
    vm = [int(((mm["Etapa_consulta"] == e) & (mm["Rol"] == "Médico")).sum()) for e in et]
    vp = [int(((mm["Etapa_consulta"] == e) & (mm["Rol"] == "Paciente")).sum()) for e in et]
    G.barras_h(ax, et, vm, color=G.SERIES[0], alto=0.35, offset=-0.19, label="Médico")
    G.barras_h(ax, et, vp, color=G.SERIES[1], alto=0.35, offset=0.19, label="Paciente")
    ax.legend(loc="lower right")
    ax.set_xlabel("Frases (sin léxico)")
    top = G.titulo(fig, "Frases del médico y del paciente por etapa", "El paciente casi no tiene voz en el material actual")
    fig.tight_layout(rect=(0, 0, 1, top))
    md += [f"![Etapas y rol]({guardar_fig(fig, 'f06_etapas_rol.png')})", ""]

    # ---------------------------------------------------------------- 10. EDA previo
    md += ["## 10. EDA previo de un compañero (solo precedente)", "",
           "Existe un EDA anterior (`Fuentes/Trabajo - Otro Compañero/[Vibe]EDA_Corpus_NLP.ipynb` + `Corpus_Recopilado.xlsx`). No se usó como fuente "
           "de datos ni de alertas. Diferencias principales: usaba la hoja médica antigua del Grupo 3 (no el unificado), y preseleccionaba 100 + 100 + 100 "
           "frases por cobertura de palabras del **español** de unas flashcards. Aquí se usa el unificado (D10), la proporción 70/30 por bloque (D1), "
           "cobertura de **sufijos del quechua** para la parte general (§11.1) y el flujo de consulta para la parte médica (§11.2).", ""]

    # ---------------------------------------------------------------- 11. conclusiones
    gen = R[(R["Dominio"] == "General") & (R["Español"] != "")]
    gen_unicos = {p: sim_resumen.get(NOMBRE_POOL[p], (0, 0, 0)) for p in ["principito", "g2_diccionario", "g2_ejercicio"]}
    gen_util = sum(n - d - s for n, d, s in gen_unicos.values())
    med_frases = mm.drop_duplicates("clave_es")
    med_util = len(med_frases[med_frases["pal_es"] <= CFG["limpieza"]["max_palabras_sin_partir"]])
    n_bloques_gen = gen_util // CFG["bloque"]["generales"]
    n_bloques_med = med_util // CFG["bloque"]["medicas"]
    md += ["## 11. Conclusiones (en simple)", "",
           "**Qué se descarta (estimado; F4 da la cifra exacta):**",
           f"- 11 filas «Pendiente – no usar» del unificado (títulos), la fila vacía F-0517 y las 3 filas de bibliografía del Grupo 2.",
           f"- Repetidos exactos: general {sum(d for n, d, s in gen_unicos.values())}, médico {sim_resumen.get('Médico (unificado)', (0, 0, 0))[1]}.",
           f"- Casi duplicados que pasan de 2 por significado: general {sum(s for n, d, s in gen_unicos.values())} (sobre todo ejercicios del Grupo 2), "
           f"médico {sim_resumen.get('Médico (unificado)', (0, 0, 0))[2]}.",
           f"- Oraciones de más de 20 palabras que no sean listas partibles ({len(largas)} candidatas).",
           f"- Las {int((m['Tipo_oración'] == 'palabra').sum())} palabras sueltas del médico no se descartan: pasan a `Lexico`; las prioritarias vuelven como frases portadoras (F5).", "",
           "**Qué falta:**",
           f"- **Voz del paciente.** Hay ~{int((mm['Rol'] == 'Paciente').sum())} frases del paciente para todo el corpus; cada bloque necesita ~30. "
           "F5 debe redactar en español las respuestas del paciente a las preguntas de los bloques planificados.",
           "- Temas con poco o nada: ver la tabla de temas clave (alergias, deshidratación, niños, embarazo con sangrado, «¿entendió?»).",
           "- Quechua confiable: ninguna fila es gold. El Principito es traducción automática con préstamos; el médico viene en gran parte de Lopera (collao) normalizado por reglas.",
           "- Los ejercicios del Grupo 2 son muy repetitivos: tras quitar casi duplicados quedan bastantes menos.", "",
           "**Cuántos bloques caben (estimado):**",
           f"- Parte general utilizable ≈ **{gen_util}** oraciones → **{n_bloques_gen} bloques** de 140.",
           f"- Parte médica utilizable (frases ≤ 20 palabras, sin léxico ni repetidos) ≈ **{med_util}** → alcanzaría para {n_bloques_med} bloques de 60, "
           "pero la mitad debe ser del paciente, así que el límite real lo pone lo que se redacte en F5.",
           f"- **La parte general es la que limita: ~{n_bloques_gen} bloques** con el material actual. Para más, habría que decidir P4 (AmericasNLP) con Juan.",
           "- El diccionario MINEDU en PDF tiene texto y se usó para P6: las frases del Grupo 2 **no** aparecen como ejemplos del diccionario "
           f"(solo {int((R['Origen_verificado'] == 'Sí').sum() - int((R['Fuente'].str.startswith('SOCEMURP') & (R['Origen_verificado'] == 'Sí')).sum()))} coinciden). "
           "Son frases del equipo con vocabulario chanka; se usan igual, con `Origen_verificado = No`.", ""]

    escribir_texto(DESTINO, "\n".join(md))
    S = R.drop(columns=["avisos"]).copy()
    S["sufijos"] = S["sufijos"].map(lambda l: " ".join(l))
    S["avisos_raw"] = R["avisos"].map(lambda av: " | ".join(f"{t}/{s}: {d}" for t, s, d in av))
    guardar_excel(CK, {"Registros": S})
    print(f"OK → {DESTINO.relative_to(RAIZ)}, {CK.relative_to(RAIZ)}; general utilizable ≈ {gen_util} ({n_bloques_gen} bloques), médico ≈ {med_util}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
