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


import pytest

PAGINAS = ["", "tortas/", "pasteleria/", "nosotras/", "arma-tu-torta/"]
HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")


def _css(nombre):
    return (RAIZ / nombre).read_text(encoding="utf-8")


def test_marca_css_tiene_los_colores_del_logo_y_playfair():
    css = _css("comun/marca.css").lower()
    for valor in ("--marron:#4e2c1e", "--celeste-filete:#7eafd6", "--blanco:#f6f3e9",
                  "font-family:playfair", "playfair-latin.woff2"):
        assert valor in css.replace(" ", ""), valor
    assert "erode" not in css


def _token(css, nombre):
    return re.search(rf"--{nombre}:\s*(#[0-9a-fA-F]{{6}})", css)[1]


def _contraste(a, b):
    def luz(h):
        canales = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        r, g, b_ = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in canales]
        return 0.2126 * r + 0.7152 * g + 0.0722 * b_
    claro, oscuro = sorted((luz(a), luz(b)), reverse=True)
    return (claro + 0.05) / (oscuro + 0.05)


def test_el_color_de_alerta_se_lee_como_texto_sobre_los_fondos_claros():
    """--alerta es funcional (atrasos, avisos que fallaron, precios sin cargar)
    y va como TEXTO: necesita AA (4,5:1) sobre todos los fondos claros."""
    css = _css("comun/marca.css")
    alerta = _token(css, "alerta")
    for fondo in ("blanco", "crema", "crema-suave", "alerta-suave"):
        assert _contraste(alerta, _token(css, fondo)) >= 4.5, fondo


def test_ningun_css_declara_colores_fuera_de_marca():
    for nombre in ["comun/base.css", "comun/ticket.css", "comun/tienda.css", "home.css",
                   "nosotras/nosotras.css", "arma-tu-torta/decoradas.css"]:
        css = re.sub(r"mask(?:-image)?\s*:[^;}]*", "", _css(nombre))
        assert HEX.findall(css) == [], nombre
        assert "rgba(" not in css, nombre


@pytest.mark.parametrize("pagina", PAGINAS)
def test_cada_pagina_carga_marca_antes_que_base_y_nada_de_erode(abrir, pagina):
    pg = abrir(pagina=pagina)
    hrefs = pg.eval_on_selector_all('link[rel="stylesheet"]', "ls => ls.map(l => l.getAttribute('href'))")
    marca = next(i for i, h in enumerate(hrefs) if h.endswith("comun/marca.css"))
    base = next(i for i, h in enumerate(hrefs) if h.endswith("comun/base.css"))
    assert marca < base
    assert "erode" not in pg.content().lower()
    # Ruling del controller: en la home el h1 no lleva .display (el lema es un
    # span.display adentro del h1), así que h1 solo heredaría Montserrat.
    familia = pg.evaluate("getComputedStyle(document.querySelector('h1.display, h1 .display')).fontFamily")
    assert familia.lower().startswith("playfair")
