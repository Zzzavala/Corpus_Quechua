"""Heurísticas de clasificación del español: rol, tipo de oración, etapa de consulta y escenario.

Son aproximadas y están documentadas en DECISIONES_TOMADAS.md. Se aplican sobre el español (no sobre el quechua).
"""
from __future__ import annotations

import re

from comun import es_pregunta, n_palabras, sin_tildes, texto

# ----------------------------------------------------------------- tipo de oración

IMPERATIVOS = {
    "abra", "abre", "abrir", "cierre", "cierra", "respire", "respira", "tome", "toma", "tomen", "siéntese", "siéntate",
    "sientate", "sientese", "acuéstese", "acuéstate", "echese", "échese", "échate", "echate", "levante", "levanta",
    "levántese", "levántate", "saque", "saca", "sáquese", "sácate", "diga", "di", "dime", "dígame", "mire", "mira",
    "camine", "camina", "tosa", "tose", "trague", "traga", "muestre", "muestra", "muéstreme", "muéstrame", "enseñe",
    "enseñame", "enséñame", "enséñeme", "baje", "baja", "suba", "sube", "voltee", "voltea", "voltéese", "voltéate",
    "gire", "gira", "doble", "dobla", "estire", "estira", "apriete", "aprieta", "suelte", "suelta", "relaje", "relaja",
    "relájese", "relájate", "quítese", "quítate", "póngase", "ponte", "pónte", "vuelva", "vuelve", "regrese", "regresa",
    "venga", "ven", "vaya", "ve", "anda", "lávese", "lávate", "lave", "lava", "coma", "come", "beba", "bebe",
    "evite", "evita", "no", "descanse", "descansa", "use", "usa", "cuide", "cuida", "cuídese", "cuídate", "espere",
    "espera", "escuche", "escucha", "sople", "sopla", "empuje", "empuja", "jale", "jala", "toque", "toca", "señale",
    "señala", "cuente", "cuenta", "repita", "repite", "lea", "lee", "orine", "orina", "puje", "puja", "sigua", "siga",
    "sigue", "deje", "deja", "hágase", "hazte", "haga", "haz", "lleve", "lleva", "traiga", "trae", "acérquese",
    "acércate", "pase", "pasa", "entre", "entra", "procure", "procura", "recuerde", "recuerda", "olvide", "permita",
    "permíteme", "permítame", "desvístase", "desvístete", "vístase", "vístete", "inclínese", "inclínate", "agáchese",
    "agáchate", "párese", "párate", "pare", "para", "mantenga", "mantén", "aguante", "aguanta", "hable", "habla",
    "prepárese", "prepárate", "ayúdeme", "ayúdame", "bañe", "báñese", "báñate", "duerma", "duerme", "vacune",
    "vacúnese", "aliméntese", "aliméntate", "dele", "dale", "denle", "acuda", "acude", "busque", "busca",
    "protégete", "protéjase", "lávate", "lávense", "cubra", "cubre", "tápese", "tápate", "quédate", "quédese",
    "enjuágate", "enjuáguese", "péinate", "anda", "bota", "botar", "chupa", "chupe",
}
# Comienzos típicos de lo que dice el paciente (se comparan sin tildes, salvo "sí", que se mira aparte).
PRIMERA_PERSONA_INICIO = (
    "me ", "mi ", "mis ", "tengo", "estoy", "siento", "no puedo", "no tengo", "no estoy", "no me", "no se ",
    "yo ", "no,", "no.", "he ", "hace ", "estuve", "fui ", "comi", "vivo", "soy ", "nada he", "no he ",
    "trabajo ", "vine", "vengo", "quiero", "puedo", "tome ", "tomo ", "ayer ", "anoche", "a veces", "nunca", "siempre ",
    "desde hace", "desde ayer", "desde anoche", "un poco", "mas o menos", "nos ", "nosotros",
    "duermo", "orino", "toso", "vomito", "veo ", "oigo", "camino", "creo", "pienso", "sangro", "entendi",
    "gracias", "de acuerdo", "cuando como", "cuando camino", "se me ", "le tengo", "perdi", "baje ",
    "subi ", "tuve", "estaba",
)
PISTAS_PACIENTE = ("doctor", "doctora", "señorita enfermera")
# Frases en 1.ª persona que dice el profesional, no el paciente
MEDICO_PRIMERA = re.compile(r"^(yo )?(le|lo|la|te|les) (voy|vamos) a|^(yo )?voy a (examinar|revisar|tomar|poner|auscultar|preguntar|explicar|lavar)|"
                            r"^quiero (preguntar|examinar|hablar|ver|revisar|saber|explicar)|"
                            r"^yo soy (el|la) (doctor|doctora|medic|enfermer|obstetr)|^(ahora )?vamos a|estoy escribiendo")
SECCIONES_PROFESIONAL = ("presentacion del profesional", "acceso linguistico")


def tipo_oracion(es: str) -> str:
    s = texto(es)
    if not s:
        return "vacía"
    if n_palabras(s) <= 1 and not es_pregunta(s):
        return "palabra"
    if es_pregunta(s):
        return "pregunta"
    limpio = re.sub(r"^[¡¿\"'«(\-–\s]+", "", s)
    if re.match(r"^dé\s", limpio.lower()):
        return "orden"
    primera = sin_tildes(limpio.split(" ")[0].lower().strip(",.;:!"))
    if primera in {sin_tildes(x) for x in IMPERATIVOS} or re.search(r"^(no\s+)?\w+(ese|ate|ete|alo|elo|ela|ala|selo|melo)\b", sin_tildes(s.lower())):
        if primera != "no" or re.match(r"^no\s+(debe|coma|tome|beba|haga|use|se|olvide|deje|fume|cargue|levante|toque|salga|camine|comas|tomes|bebas|hagas|uses|olvides|dejes|fumes|toques|salgas|camines|debes)\b", sin_tildes(s.lower())):
            return "orden"
    return "afirmación"


def es_primera_persona(es: str) -> bool:
    con_tilde = re.sub(r"^[¡¿\"'«(\-–\s]+", "", texto(es)).lower()
    if re.match(r"^sí\b", con_tilde):          # "Sí, ..." (respuesta); "Si ..." sin tilde es condicional
        return True
    s = sin_tildes(con_tilde)
    if MEDICO_PRIMERA.search(s):
        return False
    if s.startswith(PRIMERA_PERSONA_INICIO):
        return True
    return bool(re.search(r"\b(me duele|me arde|me pica|tengo|estoy|siento|me siento|no puedo|me da|me dio|me falta|"
                          r"vine|vivo|naci|comi|tome|duermo|orino|toso|vomito|vomite|fui|estuve|tuve|entendi|mi nombre es)\b", s))


def rol(es: str, dominio: str, etapa: str = "", seccion: str = "") -> str:
    """Médico / Paciente / — (solo en el dominio médico)."""
    s = texto(es)
    if dominio != "Médico" or not s:
        return "—"
    if n_palabras(s) <= 1 and not es_pregunta(s):
        return "—"
    if etapa == "Léxico" and n_palabras(s) <= 3 and not es_pregunta(s):
        return "—"
    baja = sin_tildes(s.lower())
    if any(x in sin_tildes(texto(seccion).lower()) for x in SECCIONES_PROFESIONAL):
        return "Médico"
    if es_pregunta(s):
        if any(p in baja for p in PISTAS_PACIENTE):
            return "Paciente"
        return "Médico"
    if tipo_oracion(s) == "orden":
        return "Médico"
    if es_primera_persona(s):
        return "Paciente"
    return "Médico"


# ----------------------------------------------------------------- tiempo verbal (sobre el español; aproximado)

_PROG = re.compile(r"\b(estoy|estás|está|estamos|están|estaba|estabas|estábamos|estaban|estuve|estuvo|sigue|sigues|siguen)\s+\w+(ando|iendo|yendo)\b")
_FUT = re.compile(r"\b\w{2,}(ré|rás|rá|remos|rán)\b")
_IR_A = re.compile(r"\b(voy|vas|va|vamos|van)\s+a\s+\w+(ar|er|ir)\b")
_COND = re.compile(r"\b\w{2,}(ría|rías|ríamos|rían)\b|\b(quisiera|quisieras|quisiéramos|quisieran)\b")
_PERF = re.compile(r"\b(he|has|ha|hemos|han|había|habías|habíamos|habían|hube|hubo)\s+\w+(ado|ido|to|cho|so)\b")
_PRET = re.compile(r"\b\w{2,}(é|ó|aste|iste|aron|ieron)\b")
_IMPF = re.compile(r"\b\w{2,}(aba|abas|ábamos|aban|ía|ías|íamos|ían)\b")
_NO_VERBO = {"qué", "sé", "dé", "té", "bebé", "café", "josé", "también", "día", "días", "tía", "tías", "mía", "mías", "policía",
             "alegría", "maría", "energía", "compañía", "todavía", "sandía", "vía", "garantía", "lejía", "cirugía", "anemia",
             "historia", "farmacia", "dosis", "economía", "cortesía", "panadería", "tienda", "sabía", "ahí", "aquí", "allí"}


def tiempo_es(es: str) -> str:
    """Tiempo o modo principal de una oración en español: presente, pasado, futuro, progresivo, condicional o imperativo.
    Heurística por terminaciones (aproximada; sirve para comparar bloques, no para análisis gramatical)."""
    s = texto(es).lower()
    palabras_ = [p for p in re.findall(r"[a-záéíóúñü]+", s) if p not in _NO_VERBO]
    s2 = " ".join(palabras_)
    if _PROG.search(s2):
        return "progresivo"
    if _FUT.search(s2):
        return "futuro"
    if _COND.search(s2):
        return "condicional"
    if _PERF.search(s2) or _PRET.search(s2) or _IMPF.search(s2):
        return "pasado"
    if tipo_oracion(es) == "orden" or re.match(r"^[¡¿]?\s*(que|vamos|vengan|sigan|cantemos|saquemos)\b", s):
        return "imperativo"
    if _IR_A.search(s2):
        return "futuro"
    return "presente"


# ----------------------------------------------------------------- secciones → etapas (§11.3)


def separar_seccion(seccion: str) -> tuple[str, str]:
    s = texto(seccion).replace("\n", " / ")
    if "›" in s:
        a, b = s.split("›", 1)
        return a.strip(), b.strip()
    return s, ""


def _num(seccion: str) -> tuple[str, int | None]:
    """('principal'|'kim'|'otro', número)."""
    m = re.match(r"^(\d{2})\.\s", seccion)
    if m:
        return "kim", int(m.group(1))
    m = re.match(r"^(\d{2})\s", seccion)
    if m:
        return "principal", int(m.group(1))
    return "otro", None


ETAPAS = ["Inicio", "Recolección de información", "Examen físico", "Explicación y plan", "Relación",
          "Sensible", "Léxico", "Sin sección"]


def etapa_consulta(seccion: str) -> str:
    sec, _ = separar_seccion(seccion)
    sistema, n = _num(sec)
    if sistema == "principal":
        if n in (1, 2):
            return "Inicio"
        if n in (5, 18):
            return "Examen físico"
        if n in (17, 19, 20, 23):
            return "Explicación y plan"
        if n == 21:
            return "Relación"
        if n in (11, 22):
            return "Sensible"
        if n == 24:
            return "Léxico"
        if n in (3, 4, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16):
            return "Recolección de información"
    if sistema == "kim":
        if n in (1, 2):
            return "Inicio"
        if n in (13, 15):
            return "Examen físico"
        if n in (16, 18, 19):          # 16. Hospital, procedimientos y evolución → plan (decisión propia)
            return "Explicación y plan"
        if n == 20:
            return "Léxico"
        if n in (3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14):   # 14. Puericultura → recolección (decisión propia)
            return "Recolección de información"
    if sec.startswith("Lopera") or sec.startswith("Vocabulario (Allin Kawsay)"):
        return "Léxico"
    return "Sin sección"


def escenario(seccion: str) -> str:
    sec, sub = separar_seccion(seccion)
    nombre = re.sub(r"^\d{2}\.?\s+", "", sec)
    return f"{nombre} › {sub}" if sub else nombre


# Sub-etapas de la consulta completa de B01 (§11.2)
B01_MOTIVO = re.compile(r"por qu[eé] (viniste|vino|has venido|ha venido)|qu[eé] te (pasa|trae)|qu[eé] le (pasa|trae)|"
                        r"en qu[eé] (te|le) (puedo )?ayud|motivo|qu[eé] tienes|qu[eé] tiene usted|c[oó]mo te sientes|"
                        r"c[oó]mo se siente|desde cu[aá]ndo est[aá]s? enferm|qu[eé] te duele|qu[eé] le duele", re.I)


def etapa_b01(seccion: str, es: str) -> str:
    """Etapa fina usada para armar la consulta completa de B01 (vacío si no aplica)."""
    sec, sub = separar_seccion(seccion)
    sistema, n = _num(sec)
    s = texto(es)
    subl = sin_tildes(sub.lower())
    if sistema == "principal":
        if n in (1, 2):
            return "Inicio"
        if n == 3:
            return "Motivo de consulta"
        if n == 6:
            return "Caracterizar el síntoma"
        if n == 7:
            if subl.startswith("dolor"):
                return "Caracterizar el síntoma"
            if subl.startswith(("fiebre", "mareos", "peso", "sueno")):
                return "Síntomas asociados"
            return ""
        if n == 8 and subl.startswith(("tos", "dificultad")):
            return "Síntomas asociados"
        if n == 9 and subl.startswith(("nauseas", "deposiciones", "dolor de estomago")):
            return "Síntomas asociados"
        if n == 5 and subl.startswith(("preparacion", "boca", "torax", "abdomen")):
            return "Examen físico"
        if n in (17, 21):
            return "Explicación, plan y cierre"
        if n == 19 and subl.startswith(("medicamentos", "dieta", "referencia")):
            return "Explicación, plan y cierre"
    if sistema == "kim":
        if n in (1, 2):
            return "Inicio"
        if n == 4:
            return "Motivo de consulta" if B01_MOTIVO.search(s) else "Caracterizar el síntoma"
        if n == 13:
            return "Examen físico"
        if n == 19:
            return "Explicación, plan y cierre"
    if B01_MOTIVO.search(s) and n in (7, 3):
        return "Motivo de consulta"
    return ""
