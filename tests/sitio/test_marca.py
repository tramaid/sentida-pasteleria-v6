# tests/sitio/test_marca.py
"""La marca del sitio: logos, sello, favicon y fuentes. Es la fuente de verdad
que la tienda copia (sentida-tienda: flask sincronizar-marca)."""
import pathlib
import re

RAIZ = pathlib.Path(__file__).resolve().parents[2]
MARCA = RAIZ / "assets" / "marca"
SVGS = ["logo.svg", "logo-pasteleria.svg", "logo-claro.svg", "sello.svg", "favicon.svg"]


def test_estan_los_cinco_svg_limpios():
    for nombre in SVGS:
        texto = (MARCA / nombre).read_text(encoding="utf-8")
        assert texto.startswith("<svg"), nombre
        assert "Illustrator" not in texto and "<?xml" not in texto, nombre
        assert 'id="Capa_1"' not in texto, nombre
        assert re.search(r'viewBox="[\d. ]+"', texto), nombre


def test_los_colores_son_los_del_logo():
    assert "#4e2c1e" in (MARCA / "logo.svg").read_text(encoding="utf-8").lower()
    pasteleria = (MARCA / "logo-pasteleria.svg").read_text(encoding="utf-8").lower()
    assert "#4e2c1e" in pasteleria and "#7eafd6" in pasteleria
    claro = (MARCA / "logo-claro.svg").read_text(encoding="utf-8").lower()
    assert "#fcf9f2" in claro and "#4e2c1e" not in claro


def test_playfair_esta_y_erode_no():
    fuentes = RAIZ / "assets" / "fuentes"
    assert (fuentes / "playfair-latin.woff2").stat().st_size > 20_000
    assert (fuentes / "playfair-latin-ext.woff2").stat().st_size > 20_000
    assert not list(fuentes.glob("erode*"))
