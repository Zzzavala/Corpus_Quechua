"""F4 – Limpieza (§10) y revisión automática (§12).

Entrada: último checkpoint F3. Datos revisados a mano en scripts/datos/ (erratas, adaptaciones, particiones).
Salida: 02_maestro/checkpoints/F4_limpio_<fecha>.xlsx con Corpus, Origen, Cambios, Descartes, Lexico y QA.
IDs: GEN-/CLI-/LEX- con registro persistente 02_maestro/ids.csv (un uid nunca cambia de ID).
Uso: python scripts/04_limpieza.py [--forzar]
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict

import pandas as pd
import yaml

from comun import (CFG, RAIZ, cargar_checkpoint, clave_normalizada, es_pregunta, guardar_excel, guardar_seguro, hash_corto, hoy,
                   n_palabras, ruta, ruta_checkpoint, texto)
from dedup import grupos_casi_duplicados
from heuristicas import etapa_b01, rol, tipo_oracion
import quechua as Q
from qa import detectar_dup, ordenar, revisar_fila

DESTINO = ruta_checkpoint("F4_limpio")
REGISTRO_IDS = RAIZ / "02_maestro" / "ids.csv"
DATOS = RAIZ / CFG["rutas"]["datos_redactados"]

COLS_F2 = ["uid", "Dominio", "Pool", "Fuente", "Fuente_detalle", "Archivo", "Hoja", "Código_original", "Códigos_origen",
           "Fila_original", "Español", "Quechua_borrador", "Tipo_borrador", "Variedad_fuente", "Origen_verificado",
           "Estado_unificado", "Observaciones_heredadas", "Propuestas_equipo", "Sección", "Escenario", "Etapa_consulta",
           "Etapa_B01", "Tipo_oración", "Rol", "Evidencia_P6"]
SECCIONES_LEX_PRIORITARIAS = ("Signos y síntomas", "Cuerpo humano", "Enfermedades, lesiones y condiciones",
                              "Fluidos, secreciones y excretas", "Funciones y procesos del cuerpo")


def cargar_yaml(nombre: str) -> dict:
    p = DATOS / nombre
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {} if p.exists() else {}


def calidad(r: dict) -> int:
    """§11.2: 1 = mejor borrador … 7 = solo español. En lo general: Principito > frases variadas > ejercicios."""
    if r["Dominio"] == "General":
        return {"principito": 1, "g2_diccionario": 2, "g2_ejercicio": 3}.get(r["Pool"], 3)
    if not r["Quechua_borrador"]:
        return 7
    if r["Tipo_borrador"] == "fuente chanka oficial":
        return 1
    return int(CFG["medico"]["calidad_borrador"].get(r["Estado_unificado"], 6))


# ------------------------------------------------------------------ normalización del español

def _con_mayus(original: str, nuevo: str) -> str:
    if nuevo[:1].isupper():
        return nuevo
    return nuevo[:1].upper() + nuevo[1:] if original[:1].isupper() else nuevo


def aplicar_erratas(s: str, erratas: dict) -> str:
    for a, b in (erratas.get("frases") or {}).items():
        s = s.replace(a, b)
    for a, b in (erratas.get("palabras") or {}).items():
        s = re.sub(rf"(?<![\wÁÉÍÓÚáéíóúÑñ]){re.escape(a)}(?![\wÁÉÍÓÚáéíóúÑñ])", lambda m: _con_mayus(m.group(0), b), s, flags=re.I)
    return s


def quitar_parentesis(s: str) -> str:
    return re.sub(r"\s*\([^()]*\)", "", s).strip()


def signos_y_espacios(s: str, es_espanol: bool = True) -> str:
    s = texto(s)
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"([¿¡«])\s+", r"\1", s)
    s = re.sub(r"\s+([?!,.;:»])", r"\1", s)
    s = s.replace("“", "«").replace("”", "»").replace('"', "")
    # pares de signos ¿? ¡!
    if "?" in s and "¿" not in s:
        partes = re.split(r"(?<=[.!])\s+", s)
        partes[-1] = "¿" + partes[-1] if partes[-1].endswith("?") else partes[-1]
        s = " ".join(partes)
    if "¿" in s and "?" not in s:
        s = s.rstrip(".") + "?"
    if "!" in s and "¡" not in s and es_espanol:
        partes = re.split(r"(?<=[.?])\s+", s)
        partes[-1] = "¡" + partes[-1] if partes[-1].endswith("!") else partes[-1]
        s = " ".join(partes)
    if "¡" in s and "!" not in s:
        s = s.rstrip(".") + "!"
    return s


def mayuscula_y_punto(s: str) -> str:
    m = re.search(r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü]", s)
    if m and s[m.start()].islower():
        s = s[:m.start()] + s[m.start()].upper() + s[m.start() + 1:]
    # nueva pregunta tras «?»: «¿Orina en las noches? ¿cuántas veces?» → «¿Cuántas veces?»
    s = re.sub(r"([?!.]\s+[¿¡])([a-záéíóúñ])", lambda m: m.group(1) + m.group(2).upper(), s)
    if n_palabras(s) >= 2 and not re.search(r"[.?!…:»]$", s):
        s += "."
    return s


# ------------------------------------------------------------------ IDs


def cargar_registro() -> dict[str, str]:
    if REGISTRO_IDS.exists():
        df = pd.read_csv(REGISTRO_IDS, dtype=str, keep_default_na=False)
        return dict(zip(df["uid"], df["ID"]))
    return {}


def asignar_ids(uids_ordenados: list[str], prefijo: str, registro: dict[str, str]) -> dict[str, str]:
    usados = [int(v.split("-")[1]) for v in registro.values() if v.startswith(prefijo + "-")]
    sig = max(usados, default=0) + 1
    out = {}
    for u in uids_ordenados:
        if u in registro:
            out[u] = registro[u]
        else:
            out[u] = f"{prefijo}-{sig:04d}"
            registro[u] = out[u]
            sig += 1
    return out


# ------------------------------------------------------------------ principal


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--forzar", action="store_true")
    a = ap.parse_args()
    if DESTINO.exists() and not a.forzar:
        print(f"Ya existe {DESTINO.relative_to(RAIZ)}; usa --forzar.")
        return 0

    R = cargar_checkpoint("F3_eda")["Registros"][COLS_F2].copy()
    erratas = cargar_yaml("erratas_es.yaml")
    adapt = cargar_yaml("adaptaciones_es.yaml")
    parts = cargar_yaml("particiones_es.yaml")
    desc_manuales = cargar_yaml("descartes_es.yaml")
    fecha = hoy()

    cambios: list[dict] = []
    descartes: list[dict] = []

    def cambio(uid, campo, antes, despues, regla):
        if antes != despues:
            cambios.append({"uid": uid, "Campo": campo, "Antes": antes, "Después": despues, "Regla": regla, "Fecha": fecha})

    def descartar(r, motivo, reemplazo_uid=""):
        descartes.append({"uid": r["uid"], "Fuente": r["Fuente"], "Hoja": r["Hoja"], "Código_original": r["Código_original"],
                          "Fila_original": r["Fila_original"], "Español": r["Español"], "Quechua_borrador": r["Quechua_borrador"],
                          "Motivo": motivo, "Reemplazado_por_uid": reemplazo_uid})

    # ---------------------------------------------------------- 1. descartes iniciales y particiones
    filas: list[dict] = []
    for r in R.to_dict("records"):
        r["Por_revisar"] = ""
        r["Parte_de"] = ""
        r["Códigos_unidos"] = ""
        r["Otros_borradores"] = ""
        cod = r["Código_original"]
        if r["Estado_unificado"].startswith("Pendiente – no usar"):
            descartar(r, "Pendiente – no usar (según el unificado: título u observación de Kim 2)")
        elif r["Hoja"].startswith("Grupo 2") and not cod:
            descartar(r, "bibliografía de la hoja (no es una oración)")
        elif not r["Español"] and not r["Quechua_borrador"]:
            descartar(r, "fila vacía")
        elif not r["Español"]:
            descartar(r, "fila sin español")
        elif cod in desc_manuales:
            descartar(r, desc_manuales[cod])
        elif cod in parts and r["Dominio"] == "Médico":
            p = parts[cod]
            if isinstance(p, dict) and "descartar" in p:
                descartar(r, p["descartar"])
                continue
            uids = []
            for k, pieza in enumerate(p, 1):
                n = dict(r)
                # el uid lleva una huella del texto: si se edita la pieza, cambia de ID (nunca hereda otra traducción)
                n["uid"] = f"{r['uid']}/{k}-{hash_corto(pieza['es'])}"
                n["Español"] = pieza["es"]
                if n_palabras(pieza["es"]) > CFG["limpieza"]["max_palabras_unidad"]:
                    raise ValueError(f"particiones_es.yaml: la pieza {cod}/{k} tiene más de {CFG['limpieza']['max_palabras_unidad']} palabras")
                qu = pieza.get("qu", "") or ""
                if qu and qu not in r["Quechua_borrador"]:
                    raise ValueError(f"particiones_es.yaml: el quechua de {cod}/{k} no es un trozo literal del borrador")
                n["Quechua_borrador"] = qu
                if not qu:
                    n["Tipo_borrador"] = "ninguno"
                n["Por_revisar"] = "Español partido por Claude"
                n["Parte_de"] = cod
                cambio(n["uid"], "Español", r["Español"], pieza["es"], f"partir oración larga ({k}/{len(p)}) – Por_revisar")
                if r["Quechua_borrador"] and qu != r["Quechua_borrador"]:
                    cambio(n["uid"], "Quechua_borrador", r["Quechua_borrador"], qu,
                           "partir: trozo literal del borrador" if qu else "partir: el borrador no se puede partir con seguridad → sin borrador")
                filas.append(n)
                uids.append(n["uid"])
            descartar(r, f"larga: partida en {len(p)} unidades", ";".join(uids))
        else:
            filas.append(r)

    # ---------------------------------------------------------- 2. español
    for r in filas:
        s0 = r["Español"]
        s = s0
        if r["Código_original"] in adapt and not r["Parte_de"]:
            ad = adapt[r["Código_original"]]
            s = ad["es"]
            cambio(r["uid"], "Español", s0, s, f"adaptación ({ad['motivo']}) – Por_revisar")
            r["Por_revisar"] = "Español adaptado por Claude"
        antes = s
        s = aplicar_erratas(s, erratas)
        cambio(r["uid"], "Español", antes, s, "errata evidente")
        antes = s
        sin_coletilla = re.sub(r"\s*[,.;]?\s*¿?\s*[Ss][ií],?\s+o\s+no\s*[?.]?\s*$", "", s)
        if sin_coletilla != s and n_palabras(sin_coletilla) >= 2:
            s = sin_coletilla if re.search(r"[?.!]$", sin_coletilla) else sin_coletilla + ("?" if "¿" in sin_coletilla else ".")
            cambio(r["uid"], "Español", antes, s, "quitar coletilla «¿sí o no?» (indicación al entrevistador)")
        antes = s
        # En el léxico («Adolescente (varón)» / «Adolescente (mujer)») el paréntesis distingue entradas: se conserva.
        if "(" in s and n_palabras(quitar_parentesis(s)) > 1:
            s = quitar_parentesis(s)
            cambio(r["uid"], "Español", antes, s, "quitar aclaración entre paréntesis (no se lee en voz alta)")
        antes = s
        s = signos_y_espacios(s)
        cambio(r["uid"], "Español", antes, s, "espacios y signos ¿? ¡!")
        antes = s
        s = mayuscula_y_punto(s)
        cambio(r["uid"], "Español", antes, s, "mayúscula inicial y punto final")
        r["Español"] = s

    # ---------------------------------------------------------- 3. quechua (solo ortografía mecánica §10.3)
    for r in filas:
        q0 = r["Quechua_borrador"]
        if not q0:
            continue
        q = signos_y_espacios(q0, es_espanol=False)
        cambio(r["uid"], "Quechua_borrador", q0, q, "espacios y signos")
        if r["Tipo_borrador"] == "fuente chanka oficial":
            r["Quechua_borrador"] = q
            continue
        q2, reglas = Q.normalizar_ortografia(q)
        cambio(r["uid"], "Quechua_borrador", q, q2, "ortografía mecánica §10.3: " + ", ".join(reglas))
        r["Quechua_borrador"] = q2

    # ---------------------------------------------------------- 4. reclasificar con el texto limpio
    for r in filas:
        r["Tipo_oración"] = tipo_oracion(r["Español"])
        if r["Dominio"] == "Médico":
            r["Rol"] = rol(r["Español"], "Médico", r["Etapa_consulta"], r["Sección"])
            r["Etapa_B01"] = etapa_b01(r["Sección"], r["Español"])
        r["Calidad"] = calidad(r)

    # ---------------------------------------------------------- 5. léxico (palabras sueltas, §10.2)
    corpus, lexico = [], []
    for r in filas:
        es_lex = r["Dominio"] == "Médico" and not es_pregunta(r["Español"]) and (
            r["Tipo_oración"] == "palabra" or (r["Etapa_consulta"] == "Léxico" and n_palabras(r["Español"]) <= 3))
        (lexico if es_lex else corpus).append(r)
    # léxico: quitar repetidos exactos
    vistos: dict[str, dict] = {}
    lex_final = []
    for r in sorted(lexico, key=lambda x: (x["Calidad"], int(x["Fila_original"]))):
        k = clave_normalizada(r["Español"])
        if k in vistos:
            descartar(r, f"duplicado exacto en el léxico de {vistos[k]['Código_original']}", vistos[k]["uid"])
            vistos[k]["Códigos_unidos"] = ";".join(x for x in [vistos[k]["Códigos_unidos"], r["Código_original"]] if x)
            if r["Quechua_borrador"] and clave_normalizada(r["Quechua_borrador"]) != clave_normalizada(vistos[k]["Quechua_borrador"]):
                vistos[k]["Otros_borradores"] = "; ".join(x for x in [vistos[k]["Otros_borradores"], f"«{r['Quechua_borrador']}» ({r['Código_original']})"] if x)
            continue
        vistos[k] = r
        lex_final.append(r)

    # ---------------------------------------------------------- 6. duplicados exactos y casi duplicados (§10.4)
    # Entre dominios gana el médico: «Buenos días» o «¿Cuántos años tienes?» hacen falta en la consulta.
    orden_pool = {"principito": 0, "g2_diccionario": 1, "g2_ejercicio": 2, "medico": 3}
    corpus.sort(key=lambda x: (0 if x["Dominio"] == "Médico" else 1, x["Calidad"], orden_pool[x["Pool"]], int(x["Fila_original"]), x["uid"]))
    vistos = {}
    unicos = []
    for r in corpus:
        k = clave_normalizada(r["Español"])
        if k in vistos:
            g = vistos[k]
            descartar(r, f"duplicado exacto (mismo español) de {g['Código_original']}", g["uid"])
            g["Códigos_unidos"] = ";".join(x for x in [g["Códigos_unidos"], r["Código_original"]] if x)
            if r["Quechua_borrador"] and clave_normalizada(r["Quechua_borrador"]) != clave_normalizada(g["Quechua_borrador"]):
                g["Otros_borradores"] = "; ".join(x for x in [g["Otros_borradores"], f"«{r['Quechua_borrador']}» ({r['Código_original']})"] if x)
            continue
        vistos[k] = r
        unicos.append(r)
    final = []
    for dominio in ["General", "Médico"]:
        grupo = [r for r in unicos if r["Dominio"] == dominio]
        res = grupos_casi_duplicados([r["Español"] for r in grupo], CFG["limpieza"]["similitud_casi_duplicado"],
                                     CFG["limpieza"]["max_parafrasis"], [r["Quechua_borrador"] for r in grupo])
        for r, (gi, reemplazo) in zip(grupo, res):
            if reemplazo is None:
                final.append(r)
                r["Grupo_parafrasis"] = grupo[gi]["uid"] if gi is not None else ""
            else:
                rep = grupo[reemplazo]
                mismo_qu = r["Quechua_borrador"] and clave_normalizada(r["Quechua_borrador"]) == clave_normalizada(rep["Quechua_borrador"])
                motivo = (f"casi duplicado de {rep['Código_original']} con el mismo borrador quechua" if mismo_qu
                          else f"casi duplicado (similitud ≥ {CFG['limpieza']['similitud_casi_duplicado']}): ya hay 2 paráfrasis; grupo de {rep['Código_original']}")
                descartar(r, motivo, rep["uid"])
        # marcar grupo solo si tiene 2 miembros conservados
    cnt_grupo = Counter(r["Grupo_parafrasis"] for r in final)
    for r in final:
        if cnt_grupo[r["Grupo_parafrasis"]] < 2:
            r["Grupo_parafrasis"] = ""

    # ---------------------------------------------------------- 7. IDs (orden determinista: por fuente y orden original)
    registro = cargar_registro()

    def clave_orden(r):
        hoja = {"Grupo 1 - Principito": 0, "Grupo 2 - Corpus Chanka": 1}.get(r["Hoja"], 2)
        parte = int(r["uid"].split("/")[1].split("-")[0]) if "/" in r["uid"] else 0
        return (hoja, int(r["Fila_original"]), parte, r["uid"])

    gen = sorted([r for r in final if r["Dominio"] == "General"], key=clave_orden)
    med = sorted([r for r in final if r["Dominio"] == "Médico"], key=clave_orden)
    lex = sorted(lex_final, key=clave_orden)
    ids = {}
    ids.update(asignar_ids([r["uid"] for r in gen], "GEN", registro))
    ids.update(asignar_ids([r["uid"] for r in med], "CLI", registro))
    ids.update(asignar_ids([r["uid"] for r in lex], "LEX", registro))
    df_reg = pd.DataFrame(sorted(registro.items(), key=lambda x: x[1]), columns=["uid", "ID"])
    guardar_seguro(REGISTRO_IDS, lambda tmp: df_reg.to_csv(tmp, index=False, encoding="utf-8"))

    # ---------------------------------------------------------- 8. tablas de salida
    corpus_rows = []
    for r in gen + med:
        r["ID"] = ids[r["uid"]]
        if r["Por_revisar"]:
            estado = "Por_revisar"
        elif r["Quechua_borrador"]:
            estado = "Borrador"
        else:
            estado = "Sin borrador"
        r["Estado"] = estado
        corpus_rows.append(r)
    C = pd.DataFrame(corpus_rows)
    C["Quechua_validado"] = ""
    C["Prioridad"] = ""
    C["Bloque"] = ""
    C["Sublote"] = ""
    C["Split"] = "train"
    C["Test_sugerido"] = ""
    C["Etapa_consulta"] = C.apply(lambda r: r["Etapa_consulta"] if r["Dominio"] == "Médico" else "—", axis=1)

    origen = C[["ID", "Fuente", "Archivo", "Hoja", "Código_original", "Fila_original", "Tipo_borrador", "Variedad_fuente",
                "Origen_verificado", "Estado_unificado", "Observaciones_heredadas", "Códigos_origen", "Códigos_unidos",
                "Otros_borradores", "Propuestas_equipo", "Parte_de", "Evidencia_P6", "Fuente_detalle", "uid"]].copy()

    L = pd.DataFrame(lex)
    L["ID"] = L["uid"].map(ids)
    L["Prioritaria"] = L.apply(lambda r: "Sí" if any(r["Escenario"].endswith(x) or x in r["Escenario"] for x in SECCIONES_LEX_PRIORITARIAS) else "No", axis=1)
    L["Categoría"] = L["Escenario"]
    L["Frase_portadora"] = ""
    lexico_out = L[["ID", "Español", "Quechua_borrador", "Categoría", "Prioritaria", "Frase_portadora", "Fuente", "Código_original",
                    "Tipo_borrador", "Estado_unificado", "Códigos_unidos", "Otros_borradores", "uid"]]

    D = pd.DataFrame(descartes)
    D["Reemplazado_por"] = D["Reemplazado_por_uid"].map(lambda u: ";".join(ids.get(x, x) for x in u.split(";")) if u else "")

    CB = pd.DataFrame(cambios)
    uid_a_cod = dict(zip(R["uid"], R["Código_original"]))
    CB["ID"] = CB["uid"].map(lambda u: ids.get(u, ""))
    CB["Código_original"] = CB["uid"].map(lambda u: uid_a_cod.get(u.split("/")[0], ""))
    CB = CB[["ID", "Código_original", "Campo", "Antes", "Después", "Regla", "Fecha", "uid"]]

    # ---------------------------------------------------------- 9. QA (§12) sobre el corpus limpio
    qa_rows = []
    avisos_man = cargar_yaml("avisos_manuales.yaml")
    for _, r in C.iterrows():
        am = avisos_man.get(r["Código_original"]) if r["Quechua_borrador"] else None
        if am:                                   # primero el aviso puesto a mano: es el que llega al Word
            qa_rows.append({"ID": r["ID"], "Tipo": am["tipo"], "Severidad": am["severidad"], "Detalle": am["detalle"]})
        for t, s, d in revisar_fila(r["Español"], r["Quechua_borrador"], r["Dominio"], r["Tipo_borrador"] == "fuente chanka oficial",
                                    r["Estado_unificado"], r["Observaciones_heredadas"]):
            qa_rows.append({"ID": r["ID"], "Tipo": t, "Severidad": s, "Detalle": d})
        if r["Otros_borradores"]:
            qa_rows.append({"ID": r["ID"], "Tipo": "DUP", "Severidad": "BAJA", "Detalle": f"había otro borrador para el mismo español: {r['Otros_borradores']}"})
    for i, t, s, d in detectar_dup(C, "ID"):
        qa_rows.append({"ID": i, "Tipo": t, "Severidad": s, "Detalle": d})
    QA = ordenar(pd.DataFrame(qa_rows))

    guardar_excel(DESTINO, {"Corpus": C, "Origen": origen, "Cambios": CB, "Descartes": D, "Lexico": lexico_out, "QA": QA})

    print(f"OK → {DESTINO.relative_to(RAIZ)}")
    print(f"Corpus: {len(C)} (General {int((C.Dominio == 'General').sum())}, Médico {int((C.Dominio == 'Médico').sum())}); "
          f"Léxico: {len(L)}; Descartes: {len(D)}; Cambios: {len(CB)}; QA: {len(QA)}")
    print("Descartes por motivo:", Counter(D["Motivo"].str.split(":").str[0].str.split("(").str[0].str.strip()).most_common(12))
    print("Estado:", Counter(C["Estado"]))
    print("Pool:", Counter(C["Pool"]))
    print("Rol médico:", Counter(C.loc[C.Dominio == "Médico", "Rol"]))
    print("QA:", Counter(zip(QA["Tipo"], QA["Severidad"])).most_common(25))
    print("Cambios por regla:", Counter(CB["Regla"].str.split(":").str[0].str.split("(").str[0].str.strip()).most_common(15))
    return 0


if __name__ == "__main__":
    sys.exit(main())
