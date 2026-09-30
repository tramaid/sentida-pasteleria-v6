"""Lo legal del sitio (auditoría del 29/09/2026): la franja del pie con los
links y el Botón de arrepentimiento en todas las páginas, la leyenda de la
AAIP, las páginas de Privacidad y Términos, y la línea de consentimiento junto
a cada «Mandar». Los textos salen de legal/, que la tienda copia tal cual."""
import pathlib
import sys

import pytest

from test_sitio import PAGINAS

RAIZ = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "herramientas"))
import generar_tienda  # noqa: E402


@pytest.mark.parametrize("pagina", PAGINAS)
def test_la_franja_legal_del_pie(abrir, sitio, pagina):
    pg = abrir(pagina=pagina)
    links = pg.eval_on_selector_all(".pie-legal-links a", "as => as.map(a => [a.textContent, a.href])")
    assert links == [["Política de privacidad", sitio + "privacidad/"],
                     ["Términos y condiciones", sitio + "terminos/"],
                     ["Botón de arrepentimiento", generar_tienda.TIENDA + "arrepentimiento"]]
    assert pg.locator(".pie-arrepentimiento").is_visible()
    assert "Ley N° 25.326" in pg.text_content(".pie-aaip")


def test_el_boton_de_arrepentimiento_se_ve_desde_la_home_en_el_celular(abrir):
    pg = abrir(390, 844, is_mobile=True, has_touch=True)
    boton = pg.locator(".pie-arrepentimiento")
    boton.scroll_into_view_if_needed()
    b = boton.bounding_box()
    assert boton.is_visible() and b["height"] >= 44 and b["x"] + b["width"] <= 390


@pytest.mark.parametrize("clave,titulo,dice", [
    ("privacidad", "Política de privacidad.", "Ley 25.326"),
    ("terminos", "Términos y condiciones.", "artículo 1116"),
])
def test_las_paginas_legales(abrir, clave, titulo, dice):
    pg = abrir(pagina=f"{clave}/")
    assert pg.text_content("h1") == titulo
    assert dice in pg.text_content(".legal-texto")
    assert pg.get_attribute("meta[name=robots]", "content") == "noindex"
    assert "[[" not in pg.content() and "{{" not in pg.content()


@pytest.mark.parametrize("clave", ["privacidad", "terminos"])
def test_las_paginas_legales_tienen_la_cabecera_completa(abrir, clave):
    """«Mi pedido» vive en comun/ticket.css: sin esa hoja queda sin estilo."""
    pg = abrir(pagina=f"{clave}/")
    assert pg.eval_on_selector(".cab [data-mi-pedido]", "a => getComputedStyle(a).textTransform") == "uppercase"


def test_sin_datos_del_titular_no_se_inventan(abrir):
    """Mientras legal/titular.json esté vacío, el pie no muestra una línea del
    titular a medias: queda el comentario «Pendiente»."""
    pg = abrir()
    assert pg.locator(".pie-titular").count() == 0
    assert "Pendiente: razón social, CUIT" in pg.content()


def test_el_pie_con_los_datos_del_titular():
    titular = {"razon_social": "Ejemplo SRL", "cuit": "30-00000000-0", "domicilio": "Calle 1, Martínez",
               "email": "hola@ejemplo.com", "data_fiscal_html": '<a href="#"><img src="x.png" alt="Data Fiscal"></a>'}
    env, _ = generar_tienda._legal()
    html = env.get_template("pie.html").render(titular=titular, urls={}, wa="", wa_texto="")
    assert "Ejemplo SRL · CUIT 30-00000000-0 · Calle 1, Martínez · <a href=\"mailto:hola@ejemplo.com\">" in html
    assert '<div class="pie-datafiscal"><a href="#"><img src="x.png" alt="Data Fiscal"></a></div>' in html
    assert "Pendiente" not in html


def test_la_comanda_pide_consentimiento(abrir, sitio):
    pg = abrir(pagina="arma-tu-torta/")
    assert pg.get_attribute("#envio .acepto a", "href") == "../privacidad/"


def test_el_carrito_pide_consentimiento(abrir, sitio):
    pg = abrir(pagina="tortas/")
    assert pg.eval_on_selector(".carrito-form .acepto a", "a => a.href") == sitio + "privacidad/"
