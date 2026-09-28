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


CATALOGO = pathlib.Path(__file__).resolve().parents[2] / "datos" / "catalogo.json"


def test_el_catalogo_trae_medidas_y_anticipacion():
    d = json.loads(CATALOGO.read_text(encoding="utf-8"))
    tortas, past = d["secciones"]["tortas"], d["secciones"]["pasteleria"]
    assert [m["nombre"] for m in tortas["medidas"]] == ["20 a 22 cm", "Más grande"]
    assert tortas["medidas"][1]["nota"] == "Tamaño y precio a consultar por WhatsApp"
    assert [m["nombre"] for m in past["medidas"]] == ["½ docena", "Docena"]
    assert (tortas["anticipacion_horas"], past["anticipacion_horas"]) == (48, 96)
    assert tortas["anticipacion_texto"] == "Pedila con 48 h"
    assert past["anticipacion_texto"] == "De 4 a 7 días, según el trabajo"


def test_cada_producto_visible_tiene_descripcion_larga():
    d = json.loads(CATALOGO.read_text(encoding="utf-8"))
    for p in d["productos"]:
        if p.get("visible", True):
            assert len(p.get("descripcion_larga", "")) > 40, p["slug"]
            assert p.get("texto_provisorio") is True, p["slug"]


def test_los_sabores_son_solo_los_que_se_ven():
    d = json.loads(CATALOGO.read_text(encoding="utf-8"))
    sabores = {p["slug"]: [v["nombre"] for v in p.get("variantes", [])] for p in d["productos"]}
    assert sabores["shots"] == ["Con flores", "De frutillas", "De maracuyá"]
    assert sabores["cuadraditos-dulces"] == ["Carrot cake"]
    assert all(not v for s, v in sabores.items() if s not in ("shots", "cuadraditos-dulces"))
