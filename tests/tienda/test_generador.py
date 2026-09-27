import json
import pathlib
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[2]
PAGINAS = [RAIZ / "tortas" / "index.html", RAIZ / "pasteleria" / "index.html",
           RAIZ / "index.html", RAIZ / "nosotras" / "index.html", RAIZ / "arma-tu-torta" / "index.html"]


def test_el_html_generado_esta_al_dia():
    antes = [p.read_bytes() for p in PAGINAS]
    subprocess.run([sys.executable, "herramientas/generar_tienda.py"], cwd=RAIZ, check=True, capture_output=True)
    despues = [p.read_bytes() for p in PAGINAS]
    assert despues == antes, "Corré python herramientas/generar_tienda.py: el HTML de la tienda no está al día"


def test_cada_producto_visible_aparece_una_vez():
    datos = json.loads((RAIZ / "datos" / "catalogo.json").read_text(encoding="utf-8"))
    for seccion, pagina in (("tortas", PAGINAS[0]), ("pasteleria", PAGINAS[1])):
        html = pagina.read_text(encoding="utf-8")
        for p in datos["productos"]:
            veces = html.count(f'data-producto="{p["slug"]}"')
            esperado = 1 if p["seccion"] == seccion and p.get("visible", True) else 0
            assert veces == esperado, (seccion, p["slug"], veces)
