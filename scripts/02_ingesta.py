"""F2 – Ingesta al maestro: todas las fuentes de bloques en un esquema único (antes de limpiar).

Fuentes que entran (D10, D11): Vocabulario_unificado (médico), Grupo 1 Principito y Grupo 2 (general).
Grupo 3 original, Términos y Corpus_Construido quedan solo como referencia (se usan para cruzar).
Asigna Tipo_borrador, Variedad_fuente, Rol, Etapa_consulta, Escenario y clasifica el Grupo 2 (P6).

Salida: 02_maestro/checkpoints/F2_ingesta_<fecha>.xlsx (hoja Registros).
Uso: python scripts/02_ingesta.py [--forzar]
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter

import pandas as pd
from rapidfuzz import fuzz, process

from comun import RAIZ, CFG, clave_normalizada, guardar_excel, ruta_checkpoint, texto
import fuentes as F
from heuristicas import es_primera_persona, escenario, etapa_b01, etapa_consulta, rol, tipo_oracion

DESTINO = ruta_checkpoint("F2_ingesta")
PRONOMBRES = ("yo ", "tú ", "tu ", "él ", "ella ", "nosotros ", "nosotras ", "ustedes ", "ellos ", "ellas ", "usted ")

ARCH_U = CFG["archivos_fuente"]["unificado"]
ARCH_CE = CFG["archivos_fuente"]["corpus_equipos"]

# Fuente canónica → (Tipo_borrador si hay quechua, Variedad_fuente)
PERFIL_FUENTE = {
    "Lopera Quiroga (2020)": ("normalizado de Lopera", "collao/Puno, normalizado a chanka por reglas"),
    "Allin Kawsay (INS/MINSA)": ("Allin Kawsay (transcripción)", "sin confirmar (web INS/MINSA)"),
    "OPS/OMS Bolivia (2013)": ("ninguno", "boliviano (solo se tomó el español)"),
    "SOCEMURP (corpus original del equipo)": ("SOCEMURP", "chanka (declarada por el manual)"),
    "Kim 1 (pregunta añadida)": ("ninguno", "— (solo español)"),
    "Farfán Cantero (2001), SITUA": ("normalizado de Farfán (cusqueño)", "cusqueño, normalizado a chanka por reglas"),
    "MinCul – manual de justicia (chanka)": ("fuente chanka oficial", "chanka oficial (MinCul)"),
    "YouTube": ("YouTube (transcripción)", "sin confirmar"),
    "Afiche MINSA/MinCul lavado de manos (chanka)": ("fuente chanka oficial", "chanka oficial (MINSA/MinCul)"),
    "MINSA – diabetes (quechua)": ("MINSA (material en quechua)", "sin confirmar (MINSA)"),
    "OMS (2009) – lista de verificación": ("ninguno", "— (solo español)"),
}


def indice_minedu():
    """Textos del diccionario MINEDU para verificar P6: ejemplos del PDF + AmericasNLP minedu (qu y es)."""
    textos, origen = [], []
    for e in F.ejemplos_minedu_pdf():
        textos.append(clave_normalizada(e["texto"]))
        origen.append(f"PDF MINEDU p. {e['pagina']}")
    A = F.americasnlp()
    if "es-quy/minedu" in A:
        for i, (es, qu) in enumerate(zip(A["es-quy/minedu"]["es"], A["es-quy/minedu"]["qu"]), start=1):
            textos += [clave_normalizada(qu), clave_normalizada(es)]
            origen += [f"AmericasNLP minedu l. {i}", f"AmericasNLP minedu l. {i}"]
    return textos, origen


def registros_unificado(construido_claves: set[str]) -> list[dict]:
    U = F.cargar_unificado()
    out = []
    for _, r in U.iterrows():
        fuente = F.fuente_canonica(r["Fuente_original"])
        qu = r["Quechua_final (chanka)"]
        tipo, variedad = PERFIL_FUENTE.get(fuente, ("ninguno", "sin confirmar"))
        if not qu:
            tipo = "ninguno"
        es = r["Español (palabra o frase)"]
        etapa = etapa_consulta(r["Sección"])
        verificado = "No aplica"
        if fuente.startswith("SOCEMURP"):
            verificado = "Sí" if (clave_normalizada(es) in construido_claves or clave_normalizada(qu) in construido_claves) else "No"
        out.append({
            "uid": f"U:{r['Id_unificado']}",
            "Dominio": "Médico",
            "Pool": "medico",
            "Fuente": fuente,
            "Fuente_detalle": r["Fuente_original"],
            "Archivo": ARCH_U,
            "Hoja": "Vocabulario_unificado",
            "Código_original": r["Id_unificado"],
            "Códigos_origen": r["Códigos_origen"],
            "Fila_original": r["Fila_original"],
            "Español": es,
            "Quechua_borrador": qu,
            "Tipo_borrador": tipo,
            "Variedad_fuente": variedad,
            "Origen_verificado": verificado,
            "Estado_unificado": r["Estado"],
            "Observaciones_heredadas": r["Observaciones_finales"],
            "Propuestas_equipo": " | ".join(f"{k}: {r[c]}" for k, c in [("Marshall", "quechua_marshall"), ("Kim 1", "quechua_kim1"), ("Kim 2", "quechua_kim2")] if r[c]),
            "Sección": r["Sección"],
            "Escenario": escenario(r["Sección"]),
            "Etapa_consulta": etapa,
            "Etapa_B01": etapa_b01(r["Sección"], es),
            "Tipo_oración": tipo_oracion(es),
            "Rol": rol(es, "Médico", etapa, r["Sección"]),
            "Evidencia_P6": "",
        })
    return out


def registros_principito() -> list[dict]:
    P = F.cargar_principito()
    out = []
    for _, r in P.iterrows():
        obs = r["Observaciones"]
        if "borrar al usar" in obs:
            obs = ""  # nota de plantilla (§5.2): se ignora
        es = r["Español"]
        out.append({
            "uid": f"P:{r['Código_original']}", "Dominio": "General", "Pool": "principito",
            "Fuente": "Grupo 1 – El Principito", "Fuente_detalle": "Traducción automática Rosettia GSPO-NLLB",
            "Archivo": ARCH_CE, "Hoja": "Grupo 1 - Principito", "Código_original": r["Código_original"], "Códigos_origen": "",
            "Fila_original": r["Fila_original"], "Español": es, "Quechua_borrador": r["Quechua"],
            "Tipo_borrador": "traductor automático Rosettia" if r["Quechua"] else "ninguno",
            "Variedad_fuente": "máquina (NLLB-200 1.3B → quy)", "Origen_verificado": "No aplica",
            "Estado_unificado": "", "Observaciones_heredadas": obs, "Propuestas_equipo": "", "Sección": "",
            "Escenario": "General › El Principito", "Etapa_consulta": "—", "Etapa_B01": "",
            "Tipo_oración": tipo_oracion(es), "Rol": "—", "Evidencia_P6": "",
        })
    return out


def registros_grupo2(idx_textos: list[str], idx_origen: list[str]) -> list[dict]:
    G = F.cargar_grupo2()
    out = []
    vistos = Counter()
    for _, r in G.iterrows():
        cod = r["Código_original"]
        es, qu = r["Español"], r["Quechua"]
        if cod:
            vistos[cod] += 1
            uid = f"G2:{cod}" if vistos[cod] == 1 else f"G2:{cod}#{vistos[cod]}"
        else:
            uid = f"G2:fila{r['Fila_original']}"
        es_ejercicio = bool(es) and (es[:1].islower() or es.lower().startswith(PRONOMBRES))
        pool = "g2_ejercicio" if es_ejercicio else "g2_diccionario"
        # P6: verificar contra el diccionario MINEDU
        evid, verif = "", "No"
        if es or qu:
            mejor = (0.0, "", "")
            for campo in (qu, es):
                if not campo:
                    continue
                m = process.extractOne(clave_normalizada(campo), idx_textos, scorer=fuzz.ratio)
                if m and m[1] > mejor[0]:
                    mejor = (m[1], idx_textos[m[2]], idx_origen[m[2]])
            verif = "Sí" if mejor[0] >= CFG["ingesta"]["p6_umbral_similitud"] else "No"
            evid = f"similitud máx. {mejor[0]:.0f} con «{mejor[1][:70]}» ({mejor[2]})"
        out.append({
            "uid": uid, "Dominio": "General", "Pool": pool,
            "Fuente": "Grupo 2 – Corpus Chanka", "Fuente_detalle": r["Observaciones"].lstrip(": ").strip(),
            "Archivo": ARCH_CE, "Hoja": "Grupo 2 - Corpus Chanka", "Código_original": cod, "Códigos_origen": "",
            "Fila_original": r["Fila_original"], "Español": es, "Quechua_borrador": qu,
            "Tipo_borrador": ("ejercicio generado" if es_ejercicio else "MINEDU") if qu else "ninguno",
            "Variedad_fuente": "chanka (frases del equipo, sin validar)",
            "Origen_verificado": verif,
            "Estado_unificado": "", "Observaciones_heredadas": r["Observaciones"].lstrip(": ").strip(), "Propuestas_equipo": "",
            "Sección": "", "Escenario": "General › " + ("ejercicios de conjugación" if es_ejercicio else "frases variadas"),
            "Etapa_consulta": "—", "Etapa_B01": "", "Tipo_oración": tipo_oracion(es), "Rol": "—", "Evidencia_P6": evid,
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--forzar", action="store_true")
    a = ap.parse_args()
    if DESTINO.exists() and not a.forzar:
        print(f"Ya existe {DESTINO.relative_to(RAIZ)}; usa --forzar.")
        return 0

    C = F.cargar_construido()
    construido_claves = set(C["Español"].map(clave_normalizada)) | set(C["Quechua"].map(clave_normalizada))
    idx_textos, idx_origen = indice_minedu()

    regs = registros_unificado(construido_claves) + registros_principito() + registros_grupo2(idx_textos, idx_origen)
    R = pd.DataFrame(regs)
    assert R["uid"].is_unique, "uid repetido"
    R["Fila_original"] = R["Fila_original"].astype(str)

    resumen = (R.groupby(["Dominio", "Pool", "Tipo_borrador"]).size().reset_index(name="Filas"))
    guardar_excel(DESTINO, {"Registros": R, "Resumen": resumen})

    print(f"OK → {DESTINO.relative_to(RAIZ)}: {len(R)} registros")
    print(resumen.to_string(index=False))
    g2 = R[R["Hoja"] == "Grupo 2 - Corpus Chanka"]
    print("G2 Origen_verificado:", Counter(g2["Origen_verificado"]))
    print("G2 pool:", Counter(g2["Pool"]))
    m = R[R["Dominio"] == "Médico"]
    print("Rol médico:", Counter(m["Rol"]))
    print("Etapa:", Counter(m["Etapa_consulta"]))
    print("Etapa_B01:", Counter(m["Etapa_B01"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
