"""F5 – Llenar huecos (§9, F5): respuestas del paciente, frases portadoras y oraciones generales, SOLO en español.

1. Arma el plan médico de los bloques planificados (B01 curado + B02… por tema, ver plan_medico.py).
2. A cada pregunta del médico le agrega las respuestas del paciente redactadas por Claude
   (scripts/datos/respuestas_paciente.yaml).
3. Agrega las frases portadoras de palabras prioritarias del léxico (scripts/datos/frases_portadoras.yaml).
4. Agrega las oraciones generales en distintos tiempos (scripts/datos/oraciones_generales.yaml) — pedido de Juan.
5. Informa en 04_reportes/F5_huecos.md qué preguntas aún no tienen respuesta.

Nunca se redacta quechua: las filas nuevas quedan sin borrador, con Tipo_borrador = "redactado por Claude (solo español)"
y Estado = Revisar_Juan. El uid de cada fila nueva lleva una huella del TEXTO (no su posición en el YAML): si alguien
edita, inserta o borra una frase, las demás conservan su ID y una frase cambiada recibe un ID nuevo (nunca hereda la
traducción de otra).
Salida: 02_maestro/checkpoints/F5_huecos_<fecha>.xlsx
Uso: python scripts/05_huecos.py [--forzar] [--estricto]
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter

import pandas as pd
import yaml

from comun import (CFG, RAIZ, cargar_checkpoint, clave_normalizada, escribir_texto, es_pregunta, guardar_excel, guardar_seguro,
                   hash_corto, ruta, ruta_checkpoint)
from heuristicas import tipo_oracion
from plan_medico import TEMAS, elegir_medico

DESTINO = ruta_checkpoint("F5_huecos")
REPORTE = ruta("reportes") / "F5_huecos.md"
REGISTRO_IDS = RAIZ / "02_maestro" / "ids.csv"
DATOS = RAIZ / CFG["rutas"]["datos_redactados"]
TIPO_CLAUDE = "redactado por Claude (solo español)"
ETAPA_GENERAL = {"Inicio": "Inicio", "Motivo de consulta": "Recolección de información",
                 "Caracterizar el síntoma": "Recolección de información", "Síntomas asociados": "Recolección de información",
                 "Examen físico": "Examen físico", "Explicación, plan y cierre": "Explicación y plan"}


def yaml_de(nombre):
    p = DATOS / nombre
    return (yaml.safe_load(p.read_text(encoding="utf-8")) or {}) if p.exists() else {}


def clave_codigo(r) -> str:
    """Código original + número de parte si la fila salió de partir una oración (QCH-0768/2)."""
    if "/" in r["uid"]:
        return r["Código_original"] + "/" + r["uid"].split("/")[1].split("-")[0]
    return r["Código_original"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--forzar", action="store_true")
    ap.add_argument("--estricto", action="store_true", help="falla (sin escribir nada) si queda alguna pregunta sin respuesta "
                    "o alguna frase nueva repite otra")
    a = ap.parse_args()
    if DESTINO.exists() and not a.forzar:
        print(f"Ya existe {DESTINO.relative_to(RAIZ)}; usa --forzar.")
        return 0

    H = cargar_checkpoint("F4_limpio")
    C = H["Corpus"].copy()
    L = H["Lexico"].copy()
    origen = H["Origen"].copy()
    reg = pd.read_csv(REGISTRO_IDS, dtype=str, keep_default_na=False)
    registro = dict(zip(reg["uid"], reg["ID"]))
    sig = {"CLI": max(int(v.split("-")[1]) for v in registro.values() if v.startswith("CLI-")) + 1,
           "GEN": max(int(v.split("-")[1]) for v in registro.values() if v.startswith("GEN-")) + 1}

    C["Clave"] = C.apply(clave_codigo, axis=1)
    por_clave = {k: i for k, i in zip(C["Clave"], C["ID"])}
    fila_de = {i: r for i, r in zip(C["ID"], C.to_dict("records"))}
    plan_b01 = yaml_de("plan_b01.yaml")
    respuestas = yaml_de("respuestas_paciente.yaml")
    portadoras = yaml_de("frases_portadoras.yaml")
    generales = yaml_de("oraciones_generales.yaml")

    nuevas: list[dict] = []
    plan: list[dict] = []            # filas del plan: ID, Bloque, Unidad, Orden, Tema, Responde_a
    uids_vistos: set[str] = set()

    def asignar_id(uid: str, prefijo: str) -> str:
        if uid in uids_vistos:
            raise ValueError(f"Frase redactada repetida (mismo texto y misma clave): {uid}. Cambia el texto en scripts/datos/.")
        uids_vistos.add(uid)
        if uid in registro:
            return registro[uid]
        idn = f"{prefijo}-{sig[prefijo]:04d}"
        registro[uid] = idn
        sig[prefijo] += 1
        return idn

    def nueva_fila(uid, es, rol, escenario, etapa, archivo, codigo, posicion, etapa_b01="", lexico=""):
        idn = asignar_id(uid, "CLI")
        f = {c: "" for c in C.columns}
        f.update({"uid": uid, "ID": idn, "Dominio": "Médico", "Pool": "medico", "Fuente": "Redactado por Claude (F5)",
                  "Fuente_detalle": "Español redactado por Claude para llenar huecos; el quechua lo pone el traductor",
                  "Archivo": f"scripts/datos/{archivo}", "Hoja": "", "Código_original": codigo, "Fila_original": str(posicion),
                  "Español": es, "Quechua_borrador": "", "Tipo_borrador": TIPO_CLAUDE, "Variedad_fuente": "—",
                  "Origen_verificado": "No aplica", "Escenario": escenario, "Etapa_consulta": etapa, "Etapa_B01": etapa_b01,
                  "Tipo_oración": tipo_oracion(es), "Rol": rol, "Revisar_Juan": "Español redactado por Claude (F5)", "Calidad": "7",
                  "Estado": "Revisar_Juan", "Split": "train", "Clave": uid, "Parte_de": "", "Grupo_parafrasis": ""})
        if lexico:
            f["Observaciones_heredadas"] = f"Frase portadora del léxico {lexico}"
        nuevas.append(f)
        fila_de[idn] = f
        return idn

    def nueva_general(uid, es, cat, rasgo, posicion):
        idn = asignar_id(uid, "GEN")
        f = {c: "" for c in C.columns}
        f.update({"uid": uid, "ID": idn, "Dominio": "General", "Pool": "g_claude", "Fuente": "Redactado por Claude (F5)",
                  "Fuente_detalle": "Oración general en español redactada por Claude para enseñar tiempos y sufijos; el quechua lo pone el traductor",
                  "Archivo": "scripts/datos/oraciones_generales.yaml", "Hoja": "", "Código_original": f"{cat}#{posicion}",
                  "Fila_original": str(posicion), "Español": es, "Quechua_borrador": "", "Tipo_borrador": TIPO_CLAUDE,
                  "Variedad_fuente": "—", "Origen_verificado": "No aplica", "Escenario": f"General › redactada por Claude › {rasgo}",
                  "Etapa_consulta": "—", "Etapa_B01": "", "Tipo_oración": tipo_oracion(es), "Rol": "—",
                  "Revisar_Juan": "Español redactado por Claude (F5, oraciones generales)", "Calidad": "4", "Estado": "Revisar_Juan",
                  "Split": "train", "Clave": uid, "Parte_de": "", "Grupo_parafrasis": ""})
        nuevas.append(f)
        fila_de[idn] = f
        return idn

    # ---------------------------------------------------------- B01 (curado)
    usados: set[str] = set()
    orden = 0
    u = 0
    faltan_codigos = []
    etapa_plan: dict[str, str] = {}      # en B01 la etapa la fija el guion, no la heurística (p. ej. QCH-0008)
    for etapa in plan_b01:
        for unidad in etapa["unidades"]:
            u += 1
            ultimo_medico = ""
            for k, item in enumerate(unidad):
                orden += 1
                if "cod" in item:
                    idx = por_clave.get(item["cod"])
                    if not idx:
                        faltan_codigos.append(item["cod"])
                        continue
                    etapa_plan[idx] = etapa["etapa"]
                else:
                    idx = nueva_fila(f"F5:B01:{item['rol']}:{hash_corto(item['nuevo'])}", item["nuevo"], item["rol"],
                                     f"Consulta completa (B01) › {etapa['etapa']}", ETAPA_GENERAL[etapa["etapa"]], "plan_b01.yaml",
                                     f"plan_b01.yaml › {etapa['etapa']}", orden, etapa["etapa"])
                rol = fila_de[idx]["Rol"]
                responde = ultimo_medico if rol == "Paciente" else ""
                if rol == "Médico":
                    ultimo_medico = idx
                plan.append({"ID": idx, "Bloque": "B01", "Unidad": f"B01-U{u:02d}", "Orden": orden, "Tema": etapa["etapa"],
                             "Responde_a": responde})
                usados.add(idx)
    if faltan_codigos:
        print("ERROR: códigos de plan_b01.yaml que no están en el corpus limpio:", faltan_codigos)
        return 2

    # ---------------------------------------------------------- B02… (por tema)
    sin_respuesta: list[dict] = []
    bloques = list(TEMAS.keys())

    def agregar_respuestas(b, u, tema, r, idx, lista):
        nonlocal orden
        for texto_resp in (lista if isinstance(lista, list) else [lista]):
            orden += 1
            nid = nueva_fila(f"F5:resp:{r['Clave']}:{hash_corto(texto_resp)}", texto_resp, "Paciente", r["Escenario"],
                             r["Etapa_consulta"], "respuestas_paciente.yaml", f"respuesta a {r['Clave']}", orden)
            plan.append({"ID": nid, "Bloque": b, "Unidad": f"{b}-U{u:02d}", "Orden": orden, "Tema": tema, "Responde_a": idx})
            usados.add(nid)

    for b in bloques:
        elegidos = elegir_medico(C, b, usados)
        orden = 0
        u = 0
        for idx, tema in elegidos:
            u += 1
            orden += 1
            r = fila_de[idx]
            plan.append({"ID": idx, "Bloque": b, "Unidad": f"{b}-U{u:02d}", "Orden": orden, "Tema": tema, "Responde_a": ""})
            usados.add(idx)
            if es_pregunta(r["Español"]) and not respuestas.get(r["Clave"]):
                sin_respuesta.append({"Bloque": b, "Tema": tema, "ID": idx, "Clave": r["Clave"], "Español": r["Español"]})
            elif r["Clave"] in respuestas:          # respuesta a una pregunta, o respuesta opcional a una indicación
                agregar_respuestas(b, u, tema, r, idx, respuestas[r["Clave"]])
        # frases portadoras del bloque (cada una es su propia unidad, al final de su tema)
        for pt in portadoras.get(b, []) or []:
            u += 1
            orden += 1
            lex = L[L["Código_original"] == pt["lexico"]]
            esc = lex["Categoría"].iloc[0] if len(lex) else "Léxico"
            nid = nueva_fila(f"F5:port:{pt['lexico']}:{hash_corto(pt['es'])}", pt["es"], pt.get("rol", "Paciente"),
                             f"Frase portadora › {esc}", "Recolección de información", "frases_portadoras.yaml",
                             f"portadora de {pt['lexico']}", orden, lexico=pt["lexico"])
            plan.append({"ID": nid, "Bloque": b, "Unidad": f"{b}-U{u:02d}", "Orden": orden, "Tema": pt.get("tema", "Frases portadoras"), "Responde_a": ""})
            usados.add(nid)
            if len(lex):
                L.loc[L["Código_original"] == pt["lexico"], "Frase_portadora"] = nid

    # frases portadoras que quedan en el corpus para bloques futuros
    for k, pt in enumerate(portadoras.get("sin_bloque", []) or [], 1):
        lex = L[L["Código_original"] == pt["lexico"]]
        esc = lex["Categoría"].iloc[0] if len(lex) else "Léxico"
        nid = nueva_fila(f"F5:port:{pt['lexico']}:{hash_corto(pt['es'])}", pt["es"], pt.get("rol", "Paciente"),
                         f"Frase portadora › {esc}", "Recolección de información", "frases_portadoras.yaml",
                         f"portadora de {pt['lexico']}", k, lexico=pt["lexico"])
        if len(lex):
            L.loc[L["Código_original"] == pt["lexico"], "Frase_portadora"] = nid

    # oraciones generales redactadas por Claude (solo español) para variedad de tiempos
    for cat, datos in generales.items():
        for k, es in enumerate(datos["frases"], 1):
            nueva_general(f"F5:gen:{cat}:{hash_corto(es)}", es, cat, datos["rasgo"], k)

    # ---------------------------------------------------------- control: ninguna frase nueva repite otra (§10.4)
    claves_corpus = {}
    for i, s in zip(C["ID"], C["Español"]):
        claves_corpus.setdefault(clave_normalizada(s), i)
    repetidas = []
    vistas = dict(claves_corpus)
    for n in nuevas:
        cl = clave_normalizada(n["Español"])
        if cl in vistas:
            repetidas.append((n["ID"], n["Español"], vistas[cl]))
        else:
            vistas[cl] = n["ID"]

    # ---------------------------------------------------------- salida
    if a.estricto and (sin_respuesta or repetidas):
        for s in sin_respuesta:
            print(f"  FALTA {s['Bloque']} | {s['Tema']} | {s['Clave']} | {s['Español']}")
        for i, es, otra in repetidas:
            print(f"  REPETIDA {i} «{es}» = {otra}")
        print("No se escribió nada (--estricto). Completa scripts/datos/ y vuelve a correr.")
        return 3

    N = pd.DataFrame(nuevas)
    C2 = pd.concat([C, N[C.columns]], ignore_index=True)
    P = pd.DataFrame(plan)
    C2 = C2.merge(P.rename(columns={"Bloque": "Plan_bloque", "Unidad": "Plan_unidad", "Orden": "Plan_orden", "Tema": "Plan_tema"}),
                  on="ID", how="left")
    for c in ["Plan_bloque", "Plan_unidad", "Plan_tema", "Responde_a"]:
        C2[c] = C2[c].fillna("")
    C2["Plan_orden"] = C2["Plan_orden"].fillna(0).astype(int)
    C2["Etapa_B01"] = [etapa_plan.get(i, e) for i, e in zip(C2["ID"], C2["Etapa_B01"])]
    o_nuevo = N[["ID", "Fuente", "Archivo", "Hoja", "Código_original", "Fila_original", "Tipo_borrador", "Variedad_fuente",
                 "Origen_verificado", "Estado_unificado", "Observaciones_heredadas", "Códigos_origen", "Códigos_unidos",
                 "Otros_borradores", "Propuestas_equipo", "Parte_de", "Evidencia_P6", "Fuente_detalle", "uid"]]
    origen2 = pd.concat([origen, o_nuevo], ignore_index=True)

    df_reg = pd.DataFrame(sorted(registro.items(), key=lambda x: x[1]), columns=["uid", "ID"])
    guardar_seguro(REGISTRO_IDS, lambda tmp: df_reg.to_csv(tmp, index=False, encoding="utf-8"))
    hojas = dict(H)
    hojas.update({"Corpus": C2, "Origen": origen2, "Lexico": L})
    guardar_excel(DESTINO, hojas)

    # ---------------------------------------------------------- reporte
    md = ["# F5 – Llenar huecos (español redactado por Claude)", "",
          f"Generado por `scripts/05_huecos.py` ({CFG['fecha_generacion']}). Todo lo de aquí es **español redactado por Claude** "
          "para que Juan lo revise; el quechua lo pone el traductor.", ""]
    resumen = []
    for b in ["B01"] + bloques:
        pb = P[P["Bloque"] == b]
        roles = Counter(fila_de[i]["Rol"] for i in pb["ID"])
        nuevas_b = sum(1 for i in pb["ID"] if fila_de[i]["Tipo_borrador"] == TIPO_CLAUDE)
        resumen.append([b, len(pb), roles.get("Médico", 0), roles.get("Paciente", 0), nuevas_b])
    md += ["## Plan médico por bloque", "", "| Bloque | Frases | Médico | Paciente | Redactadas por Claude |", "|---|---|---|---|---|"]
    md += [f"| {' | '.join(str(x) for x in f)} |" for f in resumen]
    cuenta = Counter(n["uid"].split(":")[1] for n in nuevas)
    md += ["", f"Filas nuevas en total: **{len(N)}** (B01: {cuenta.get('B01', 0)}; respuestas del paciente: {cuenta.get('resp', 0)}; "
           f"frases portadoras: {cuenta.get('port', 0)}; oraciones generales para variedad de tiempos: {cuenta.get('gen', 0)}).", ""]
    if repetidas:
        md += [f"## Frases nuevas que repiten otra: {len(repetidas)}", ""] + [f"- `{i}` «{es}» = `{otra}`" for i, es, otra in repetidas] + [""]
    if sin_respuesta:
        md += [f"## Preguntas aún sin respuesta: {len(sin_respuesta)}", "", "| Bloque | Tema | ID | Clave | Español |", "|---|---|---|---|---|"]
        md += [f"| {s['Bloque']} | {s['Tema']} | {s['ID']} | {s['Clave']} | {s['Español']} |" for s in sin_respuesta]
        md.append("")
    md += ["## Detalle del plan (pregunta → respuestas)", ""]
    for b in ["B01"] + bloques:
        md += [f"### {b}", ""]
        for _, p in P[P["Bloque"] == b].sort_values("Orden").iterrows():
            f = fila_de[p["ID"]]
            marca = " *(Claude)*" if f["Tipo_borrador"] == TIPO_CLAUDE else ""
            sangria = "    - " if p["Responde_a"] else "- "
            md.append(f"{sangria}`{p['ID']}` [{f['Rol']}] {f['Español']}{marca}")
        md.append("")
    escribir_texto(REPORTE, "\n".join(md))

    print(f"OK → {DESTINO.relative_to(RAIZ)}; nuevas: {len(N)} ({dict(cuenta)}); sin respuesta: {len(sin_respuesta)}; "
          f"repetidas: {len(repetidas)}")
    for f in resumen:
        print("  ", f)
    for s in sin_respuesta:
        print(f"  FALTA {s['Bloque']} | {s['Tema']} | {s['Clave']} | {s['Español']}")
    for i, es, otra in repetidas:
        print(f"  REPETIDA {i} «{es}» = {otra}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
