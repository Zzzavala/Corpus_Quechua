"""Manifest del dataset de un bloque (§8.7): 06_dataset/manifest_BXX.csv y revisión de los audios.

Columnas: id, bloque, sublote, split, dominio, rol, es, qu, audio_es, audio_qu, dur_es, dur_qu, qa_audio.
Revisa que existan {ID}_es.wav y {ID}_qu.wav (en cualquier subcarpeta de 05_audio), su formato (P5: WAV 16 kHz,
mono, 16 bits) y que la duración sea razonable. Usa solo la biblioteca estándar (módulo wave).

Uso:
    python scripts/08_manifest.py B01
    python scripts/08_manifest.py B01 --maestro RUTA --audio-dir RUTA --salida RUTA
"""
from __future__ import annotations

import argparse
import csv
import sys
import wave
from pathlib import Path

from comun import CFG, RAIZ, asegurar_dir, guardar_seguro, n_palabras, ruta
import planilla as P

A = CFG["audio"]


def revisar_wav(p: Path, texto_frase: str) -> tuple[float | None, list[str]]:
    problemas = []
    try:
        with wave.open(str(p), "rb") as w:
            fr, ch, sw, nf = w.getframerate(), w.getnchannels(), w.getsampwidth(), w.getnframes()
    except (wave.Error, EOFError) as e:
        return None, [f"no es WAV PCM válido ({e})"]
    dur = nf / fr if fr else 0.0
    if fr != A["frecuencia_hz"]:
        problemas.append(f"{fr} Hz (debe ser {A['frecuencia_hz']})")
    if ch != A["canales"]:
        problemas.append(f"{ch} canales (debe ser mono)")
    if sw * 8 != A["bits"]:
        problemas.append(f"{sw * 8} bits (debe ser {A['bits']})")
    if dur < A["duracion_min_s"]:
        problemas.append(f"muy corto ({dur:.2f} s)")
    if dur > A["duracion_max_s"]:
        problemas.append(f"muy largo ({dur:.1f} s)")
    n = max(1, n_palabras(texto_frase))
    if dur / n > A["segundos_por_palabra_max"] and dur > A["ritmo_desde_s"]:
        problemas.append(f"demasiado lento o con silencio largo ({dur / n:.1f} s por palabra)")
    return round(dur, 2), problemas


def ruta_arg(valor, defecto: Path) -> Path:
    """Rutas relativas: desde la raíz del proyecto (igual que 06 y 07)."""
    if not valor:
        return defecto
    p = Path(valor)
    return p if p.is_absolute() else RAIZ / p


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("bloque")
    ap.add_argument("--maestro")
    ap.add_argument("--audio-dir")
    ap.add_argument("--salida")
    a = ap.parse_args()
    b = a.bloque.upper()
    if A["formato"].lower() != "wav":
        print(f"config.audio.formato = {A['formato']}: este script solo sabe revisar WAV (módulo wave).")
        return 2
    p_maestro = ruta_arg(a.maestro, RAIZ / CFG["rutas"]["maestro"])
    d_audio = ruta_arg(a.audio_dir, ruta("audio"))
    p_salida = ruta_arg(a.salida, ruta("dataset") / f"manifest_{b}.csv")
    filas = [r for r in P.leer(P.abrir(p_maestro)["Corpus"]) if r["Bloque"] == b]
    filas.sort(key=lambda r: int(r["N_bloque"]))
    # índice por nombre en minúsculas (CLI-0011_ES.WAV = cli-0011_es.wav); se avisan los nombres repetidos en subcarpetas
    indice: dict[str, list[Path]] = {}
    if d_audio.exists():
        for p in sorted(d_audio.rglob("*")):
            if p.is_file() and p.suffix.lower() == f".{A['formato'].lower()}":
                indice.setdefault(p.name.lower(), []).append(p)
    salida = []
    resumen = {"OK": 0, "con problemas": 0}
    for r in filas:
        qa = []
        reg = {"id": r["ID"], "bloque": b, "sublote": r["Sublote"], "split": r["Split"], "dominio": r["Dominio"], "rol": r["Rol"],
               "es": r["Español"], "qu": r["Quechua_validado"], "audio_es": "", "audio_qu": "", "dur_es": "", "dur_qu": ""}
        if not r["Quechua_validado"]:
            qa.append("SIN_VALIDAR: falta el quechua validado")
        for lado, txt in (("es", r["Español"]), ("qu", r["Quechua_validado"] or r["Quechua_borrador"])):
            nombre = f"{r['ID']}_{lado}.{A['formato']}".lower()
            ps = indice.get(nombre, [])
            if not ps:
                qa.append(f"FALTA_{lado.upper()}")
                continue
            p = ps[0]
            if len(ps) > 1:
                qa.append(f"AUDIO_REPETIDO_{lado.upper()}: {len(ps)} archivos con ese nombre "
                          f"({', '.join(x.relative_to(d_audio).as_posix() for x in ps)}); se usó el primero")
            reg[f"audio_{lado}"] = p.relative_to(d_audio).as_posix() if p.is_relative_to(d_audio) else str(p)
            dur, probs = revisar_wav(p, txt)
            reg[f"dur_{lado}"] = "" if dur is None else dur
            qa += [f"{lado.upper()}: {x}" for x in probs]
        reg["qa_audio"] = "OK" if not qa else " | ".join(qa)
        resumen["OK" if not qa else "con problemas"] += 1
        salida.append(reg)
    asegurar_dir(p_salida.parent)
    campos = ["id", "bloque", "sublote", "split", "dominio", "rol", "es", "qu", "audio_es", "audio_qu", "dur_es", "dur_qu", "qa_audio"]

    def _g(tmp):
        with open(tmp, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=campos)
            w.writeheader()
            w.writerows(salida)

    guardar_seguro(p_salida, _g)
    print(f"OK → {p_salida}: {len(salida)} filas; OK {resumen['OK']}, con problemas {resumen['con problemas']} "
          f"(audios encontrados en {d_audio}: {sum(len(v) for v in indice.values())})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
