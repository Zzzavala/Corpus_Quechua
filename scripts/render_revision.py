"""Abre de verdad los .docx/.xlsx generados con LibreOffice (headless), los convierte a PDF y renderiza páginas a PNG
para revisarlos visualmente (F7: «Abrir cada .docx y .xlsx generado y comprobar que se ven bien»).

Uso: python scripts/render_revision.py <archivo> [<archivo> ...] [--paginas 1,2,5]
Salida: 04_reportes/revision_visual/<nombre>.pdf y <nombre>_pNN.png
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pypdfium2 as pdfium

from comun import CFG, RAIZ, asegurar_dir, ruta

SALIDA = asegurar_dir(ruta("reportes") / "revision_visual")


def a_pdf(archivo: Path, salida: Path | None = None) -> Path:
    salida = salida or SALIDA
    soffice = CFG["herramientas"]["libreoffice"]
    with tempfile.TemporaryDirectory() as tmp:
        perfil = Path(tmp) / "perfil"
        cmd = [soffice, f"-env:UserInstallation=file:///{perfil.as_posix()}", "--headless", "--convert-to", "pdf",
               "--outdir", tmp, str(archivo)]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        pdf = Path(tmp) / (archivo.stem + ".pdf")
        if not pdf.exists():
            raise RuntimeError(f"LibreOffice no pudo abrir {archivo}: {r.stdout} {r.stderr}")
        destino = asegurar_dir(salida) / pdf.name
        shutil.copy(pdf, destino)
    return destino


def paginas_png(pdf: Path, paginas: list[int] | None, escala: float = 1.4) -> list[Path]:
    """Las PNG quedan junto al PDF."""
    doc = pdfium.PdfDocument(pdf)
    n = len(doc)
    sel = paginas or list(range(1, n + 1))
    out = []
    for p in sel:
        if 1 <= p <= n:
            img = doc[p - 1].render(scale=escala).to_pil()
            destino = pdf.parent / f"{pdf.stem}_p{p:02d}.png"
            img.save(destino)
            out.append(destino)
    doc.close()
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("archivos", nargs="+")
    ap.add_argument("--paginas", default="")
    ap.add_argument("--salida", help="carpeta para el PDF y las PNG (por defecto 04_reportes/revision_visual)")
    a = ap.parse_args()
    pags = [int(x) for x in a.paginas.split(",") if x.strip()] or None
    for f in a.archivos:
        p = (RAIZ / f) if not Path(f).is_absolute() else Path(f)
        pdf = a_pdf(p, Path(a.salida) if a.salida else None)
        n = len(pdfium.PdfDocument(pdf))
        pngs = paginas_png(pdf, pags)
        print(f"{p.name}: abre bien en LibreOffice → {pdf} ({n} páginas); PNG: {', '.join(x.name for x in pngs)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
