"""F2 – Ingesta al maestro: todas las fuentes de bloques en un esquema único (antes de limpiar).

Corpus en QUECHUA COLLAO (desde el 5-nov-2026). Fuentes que entran:
- médico: Vocabulario_unificado (su ESPAÑOL; el «Quechua_final (chanka)» ya no se usa) + las frases de la tabla de
  Farfán (2001) que el unificado no había tomado;
- general: Grupo 1 Principito y Grupo 2 (solo su español: su quechua era chanka o de traductor automático quy).
El borrador quechua sale SOLO de fuentes collao, tomado de su forma ORIGINAL:
- Lopera (2020): la forma del libro que el unificado guarda como «Libro: …» en las columnas de Marshall/Kim;
- Farfán (2001): la tabla del HTML (cusqueño);
- OPS/OMS Bolivia (2013): el quechua sureño boliviano del PDF, emparejado por el español.
Grupo 3 original, Términos y Corpus_Construido quedan solo como referencia.

Salida: 02_maestro/checkpoints/F2_ingesta_<fecha>.xlsx (hoja Registros).
Uso: python scripts/02_ingesta.py [--forzar]
"""
from __future__ import annotations

import argparse
import re
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
SOLO_ES = "— (solo español; su quechua era chanka y no se usa)"

# Fuente canónica → (de dónde sale el borrador collao, Tipo_borrador, Variedad_fuente)
PERFIL_FUENTE = {
    "Lopera Quiroga (2020)": ("libro", "Lopera (libro, collao)", "collao (Puno/Cusco), forma original del libro"),
    "Farfán Cantero (2001), SITUA": ("farfan", "Farfán (cusqueño, original)", "collao cusqueño, forma original"),
    "OPS/OMS Bolivia (2013)": ("ops", "OPS/OMS Bolivia (sureño boliviano)", "quechua sureño boliviano (familia collao)"),
    "Allin Kawsay (INS/MINSA)": ("", "ninguno", "— (solo español; su quechua era chanka de Huancavelica, transcrito de oído)"),
    "SOCEMURP (corpus original del equipo)": ("", "ninguno", SOLO_ES),
    "Kim 1 (pregunta añadida)": ("", "ninguno", "— (solo español)"),
    "MinCul – manual de justicia (chanka)": ("", "ninguno", SOLO_ES),
    "YouTube": ("", "ninguno", SOLO_ES),
    "Afiche MINSA/MinCul lavado de manos (chanka)": ("", "ninguno", SOLO_ES),
    "MINSA – diabetes (quechua)": ("", "ninguno", SOLO_ES),
    "OMS (2009) – lista de verificación": ("", "ninguno", "— (solo español)"),
}
FUENTE_FARFAN = "Farfán Cantero (2001), SITUA"


def _clave_es(s: str) -> str:
    """Español para emparejar: sin notas entre paréntesis («(hablando de otra persona)»)."""
    return clave_normalizada(re.sub(r"\([^()]*\)", " ", texto(s)))


class Emparejador:
    """Busca, por el español, el par (español, quechua original) de una fuente collao."""

    def __init__(self, pares: list[dict], umbral: float, nombre: str):
        self.pares, self.umbral, self.nombre = pares, umbral, nombre
        self.claves = [_clave_es(p["es"]) for p in pares]
        self.usados: set[int] = set()

    def buscar(self, es: str) -> tuple[str, str]:
        if not self.claves:
            return "", ""
        m = process.extractOne(_clave_es(es), self.claves, scorer=fuzz.ratio)
        if m and m[1] >= self.umbral:
            self.usados.add(m[2])
            p = self.pares[m[2]]
            donde = f"p. {p['pagina']}" if "pagina" in p else f"par {p.get('pos', m[2] + 1)}"
            return p["qu"], f"{self.nombre}, {donde}: «{p['es']}» (similitud {m[1]:.0f})"
        return "", (f"sin par en {self.nombre} (mejor similitud {m[1]:.0f})" if m else "")


def registros_unificado(construido_claves: set[str], farfan: Emparejador, ops: Emparejador) -> list[dict]:
    U = F.cargar_unificado()
    out = []
    for _, r in U.iterrows():
        fuente = F.fuente_canonica(r["Fuente_original"])
        origen, tipo, variedad = PERFIL_FUENTE.get(fuente, ("", "ninguno", "sin confirmar"))
        es = r["Español (palabra o frase)"]
        qu, evid = "", ""
        if origen == "libro":
            qu = F.forma_del_libro(r["quechua_marshall"], r["quechua_kim1"], r["quechua_kim2"])
            evid = "forma del libro (columna «Libro:» del unificado)" if qu else "el unificado no guarda la forma del libro"
        elif origen == "farfan":
            qu, evid = farfan.buscar(es)
        elif origen == "ops":
            qu, evid = ops.buscar(es)
        if not qu:
            tipo = "ninguno"
        etapa = etapa_consulta(r["Sección"])
        verificado = "No aplica"
        if fuente.startswith("SOCEMURP"):
            verificado = "Sí" if clave_normalizada(es) in construido_claves else "No"
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
            "Evidencia_borrador": evid,
        })
    return out


# Sección para las frases de Farfán que el unificado no tenía (la tabla no trae secciones): por palabras clave.
SECCION_FARFAN = [
    (r"buenos días|llamas|años tienes|vives|de dónde eres|leer|trabajas|qué deseas|qué quieres|por qué vives", "02 Filiación › Datos personales"),
    (r"embarazada", "11 Salud sexual y reproductiva › Embarazo y parto"),
    (r"ves bien", "12 Ojos › Visión y molestias de los ojos"),
    (r"escuchas", "14 Oídos › Oídos y audición"),
    (r"respirar|tos\b", "08 Sistema cardiorrespiratorio › Tos y flema"),
    (r"fiebre|frío", "07 Síntomas generales › Fiebre, escalofríos y sudor"),
    (r"vómito|comid|comido|estreñ|cólico|hambre|sed\b|defecad", "09 Sistema digestivo › Náuseas y vómitos"),
    (r"abre la boca|lávate|enjuágate|peínate", "05 Examen físico: indicaciones › Indicaciones al paciente"),
    (r"curar|médico|verdad|hablar de tu enfermedad", "19 Tratamiento e indicaciones › Indicaciones"),
    (r"duele|dolor", "07 Síntomas generales › Dolor: inicio, irradiación y evolución"),
    (r"enferm|cómo estás|hoy|mustia|primera vez", "03 Motivo de consulta › Motivo de consulta"),
]


def registros_farfan_extra(farfan: Emparejador) -> list[dict]:
    """Frases de la tabla de Farfán (cusqueño original) que el unificado no había tomado."""
    out = []
    for i, p in enumerate(farfan.pares):
        if i in farfan.usados:
            continue
        es = p["es"]
        seccion = next((s for pat, s in SECCION_FARFAN if re.search(pat, es, re.I)), "03 Motivo de consulta › Motivo de consulta")
        etapa = etapa_consulta(seccion)
        out.append({
            "uid": f"FA:{p['pos']:02d}", "Dominio": "Médico", "Pool": "medico", "Fuente": FUENTE_FARFAN,
            "Fuente_detalle": "Farfán Cantero (2001), «Quechua médico», revista SITUA (UNSAAC) – tabla completa",
            "Archivo": CFG["archivos_fuente"]["web_html"], "Hoja": "tabla HTML", "Código_original": f"FA-{p['pos']:02d}",
            "Códigos_origen": "", "Fila_original": p["pos"], "Español": es, "Quechua_borrador": p["qu"],
            "Tipo_borrador": "Farfán (cusqueño, original)", "Variedad_fuente": "collao cusqueño, forma original",
            "Origen_verificado": "No aplica", "Estado_unificado": "", "Observaciones_heredadas": "",
            "Propuestas_equipo": "", "Sección": seccion, "Escenario": escenario(seccion), "Etapa_consulta": etapa,
            "Etapa_B01": etapa_b01(seccion, es), "Tipo_oración": tipo_oracion(es), "Rol": rol(es, "Médico", etapa, seccion),
            "Evidencia_borrador": f"tabla de Farfán, par {p['pos']} (no estaba en el unificado)",
        })
    return out


# Fuentes collao OFICIALES (Fuentes/collao/): traducidas por el MINSA/Ministerio de Cultura al quechua de Cusco.
# Sección según el contenido (para que el plan médico las encuentre por tema).
SECCION_OFICIAL = [
    (r"(?i)tranquil|preocupe|llore|todo va a estar bien|ayúdeme|ayudar[éel]", "21 Tranquilizar al paciente › Tranquilizar al paciente"),
    (r"(?i)quechua|castellano", "01 Presentación y saludo › Acceso lingüístico"),
    (r"(?i)buenos días|buenas tardes|buenas noches|adelante|asiento|siént|gracias|de qué|cómo est[áa]n?\b|^bien,", "01 Presentación y saludo › Saludo y trato"),
    (r"(?i)vive|calle|manzana|número|nombre|llama|años tiene|años tienes|edad|de dónde", "02 Filiación › Datos personales"),
    (r"(?i)casad|esposo|esposa|marido|pareja|convivi|soltera|viud|separad|divorciad|abandonad|hij[oa]s?\b", "04 Antecedentes › Familia"),
    (r"(?i)violen|golpe|pegó|peg[aó]|maltrat|amenaz|forz", "22 Violencia › Preguntas sobre violencia"),
    (r"(?i)anticonc|píldora|pildora|condón|preservativo|inyectable|ampolla|ligadura|vasectom|método|planificación|T de cobre|implante", "23 Métodos anticonceptivos › Planificación familiar"),
    (r"(?i)regla|menstrua|menopaus", "11 Salud sexual y reproductiva › Menstruación y menopausia"),
    (r"(?i)lactan|mamar|leche materna|pecho al bebé", "11 Salud sexual y reproductiva › Lactancia"),
    (r"(?i)flujo|descenso|ITS|sífilis|VIH|SIDA|gonorrea|infección vaginal|picaz", "11 Salud sexual y reproductiva › Flujo, molestias e infecciones"),
    (r"(?i)embaraz|gestante|parto|bebé|feto|control prenatal|dar a luz|contracci|aborto|placenta|cesárea|puerperio", "11 Salud sexual y reproductiva › Embarazo y parto"),
    (r"(?i)pastilla|tableta|tome|tomar|dosis|medicamento|jarabe|efecto|náusea|mareo|vómito|dolor de cabeza", "19 Tratamiento e indicaciones › Medicamentos y dosis"),
    (r"(?i)duele|dolor", "07 Síntomas generales › Dolor: inicio, irradiación y evolución"),
    (r"(?i)análisis|examen|muestra|ecografía|laboratorio", "18 Exámenes auxiliares › Pedir exámenes"),
]
SECCION_POR_CAPITULO = {
    "I.": "01 Presentación y saludo › Saludo y trato",
    "II.": "24 Vocabulario médico (palabras sueltas) › Cuerpo humano",
    "III.": "11 Salud sexual y reproductiva › Embarazo y parto",
    # el capítulo IV también trae ejercicios de números y fechas: a Tratamiento solo va lo que habla de medicinas (SECCION_OFICIAL)
    "IV.": "03 Motivo de consulta › Motivo de consulta",
}


def registros_collao_oficial() -> list[dict]:
    """Frases de las fuentes collao oficiales nuevas, como filas médicas con borrador «fuente collao oficial»
    (la mejor calidad: lo tradujo el Estado al quechua de Cusco). No son gold todavía (D8): el traductor las confirma
    y se graban; pero casi no deberían necesitar cambios."""
    out = []
    fuentes_ = [
        ("PCS", "MINSA (s. f.), Palabras clave para la atención en salud – Quechua Cusco (difundido por el Ministerio de Cultura)",
         F.PALABRAS_CLAVE_SALUD, F.pares_palabras_clave_salud()),
        ("MJC", "Ministerio de Cultura (2015), Manual para el empleo del quechua Cusco Collao en la administración de justicia",
         F.MANUAL_JUSTICIA_COLLAO, F.pares_justicia_collao()),
        ("PIA", "Ministerio de Cultura, Glosario multilingüe de la PIAS Lago Titicaca I (aimara y quechua Cusco Collao, Puno)",
         F.GLOSARIO_PIAS, [p for p in F.pares_glosario_pias() if "…" not in p["es"]]),     # «Mi nombre es (…)» no se puede grabar
    ]
    for prefijo, nombre, archivo, pares in fuentes_:
        por_pagina: Counter = Counter()
        for p in pares:
            por_pagina[p["pagina"]] += 1
            cod = f"{prefijo}-{p['pagina']:03d}-{por_pagina[p['pagina']]:02d}"
            es, qu = p["es"], p["qu"]
            cap = p.get("capitulo", "")
            seccion = next((s for pat, s in SECCION_OFICIAL if re.search(pat, es)), None) or \
                SECCION_POR_CAPITULO.get(cap.split(" ")[0], "03 Motivo de consulta › Motivo de consulta")
            etapa = etapa_consulta(seccion)
            out.append({
                "uid": f"{prefijo}:{clave_normalizada(es)[:60]}:{clave_normalizada(qu)[:40]}", "Dominio": "Médico", "Pool": "medico",
                "Fuente": nombre, "Fuente_detalle": f"{nombre} – p. {p['pagina']} del PDF" + (f" ({cap})" if cap else ""),
                "Archivo": f"collao/{archivo}", "Hoja": "", "Código_original": cod, "Códigos_origen": "",
                "Fila_original": p["pagina"], "Español": es, "Quechua_borrador": qu,
                "Tipo_borrador": "fuente collao oficial", "Variedad_fuente": "collao cusqueño, oficial (traducción del Estado)",
                "Origen_verificado": "Sí (fuente oficial)", "Estado_unificado": "", "Observaciones_heredadas": "",
                "Propuestas_equipo": "", "Sección": seccion, "Escenario": escenario(seccion), "Etapa_consulta": etapa,
                "Etapa_B01": etapa_b01(seccion, es), "Tipo_oración": tipo_oracion(es),
                "Rol": p.get("rol") or rol(es, "Médico", etapa, seccion), "Rol_fijo": "Sí" if p.get("rol") else "",
                "Evidencia_borrador": f"{archivo}, p. {p['pagina']} del PDF",
            })
    # el mismo par (español + quechua) repetido en la fuente cuenta una vez
    vistos = set()
    unicos = []
    for r in out:
        if r["uid"] not in vistos:
            vistos.add(r["uid"])
            unicos.append(r)
    return unicos


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
            "Fila_original": r["Fila_original"], "Español": es, "Quechua_borrador": "",
            "Tipo_borrador": "ninguno",
            "Variedad_fuente": "— (solo español; su quechua era de traductor automático chanka quy)", "Origen_verificado": "No aplica",
            "Estado_unificado": "", "Observaciones_heredadas": obs, "Propuestas_equipo": "", "Sección": "",
            "Escenario": "General › El Principito", "Etapa_consulta": "—", "Etapa_B01": "",
            "Tipo_oración": tipo_oracion(es), "Rol": "—", "Evidencia_borrador": "",
        })
    return out


def registros_grupo2() -> list[dict]:
    """Grupo 2: solo el español (frases variadas y ejercicios de conjugación). Su quechua era chanka."""
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
        out.append({
            "uid": uid, "Dominio": "General", "Pool": pool,
            "Fuente": "Grupo 2 – Corpus Chanka", "Fuente_detalle": r["Observaciones"].lstrip(": ").strip(),
            "Archivo": ARCH_CE, "Hoja": "Grupo 2 - Corpus Chanka", "Código_original": cod, "Códigos_origen": "",
            "Fila_original": r["Fila_original"], "Español": es, "Quechua_borrador": "",
            "Tipo_borrador": "ninguno",
            "Variedad_fuente": SOLO_ES,
            "Origen_verificado": "No aplica",
            "Estado_unificado": "", "Observaciones_heredadas": r["Observaciones"].lstrip(": ").strip(), "Propuestas_equipo": "",
            "Sección": "", "Escenario": "General › " + ("ejercicios de conjugación" if es_ejercicio else "frases variadas"),
            "Etapa_consulta": "—", "Etapa_B01": "", "Tipo_oración": tipo_oracion(es), "Rol": "—", "Evidencia_borrador": "",
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
    construido_claves = set(C["Español"].map(clave_normalizada))
    farfan = Emparejador(F.pares_farfan(), CFG["ingesta"]["farfan_umbral_similitud"], "tabla de Farfán")
    ops = Emparejador(F.pares_ops_bolivia(), CFG["ingesta"]["ops_umbral_similitud"], "PDF OPS/OMS Bolivia")

    regs = registros_unificado(construido_claves, farfan, ops)
    regs += registros_farfan_extra(farfan) + registros_collao_oficial() + registros_principito() + registros_grupo2()
    R = pd.DataFrame(regs)
    assert R["uid"].is_unique, "uid repetido"
    R["Fila_original"] = R["Fila_original"].astype(str)

    resumen = (R.groupby(["Dominio", "Pool", "Tipo_borrador"]).size().reset_index(name="Filas"))
    guardar_excel(DESTINO, {"Registros": R, "Resumen": resumen})

    print(f"OK → {DESTINO.relative_to(RAIZ)}: {len(R)} registros")
    print(resumen.to_string(index=False))
    print(f"OPS/OMS Bolivia: {len(ops.usados)} de {len(ops.pares)} pares del PDF emparejados con el unificado; "
          f"Farfán: {len(farfan.usados)} de {len(farfan.pares)} (el resto entra como filas nuevas)")
    g2 = R[R["Hoja"] == "Grupo 2 - Corpus Chanka"]
    print("G2 pool:", Counter(g2["Pool"]))
    m = R[R["Dominio"] == "Médico"]
    print("Rol médico:", Counter(m["Rol"]))
    print("Etapa:", Counter(m["Etapa_consulta"]))
    print("Etapa_B01:", Counter(m["Etapa_B01"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
