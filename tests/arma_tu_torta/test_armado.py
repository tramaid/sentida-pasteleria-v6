from urllib.parse import unquote

from ayuda_decoradas import armar
from fechas import FUTURA, FUTURA_TEXTO

ESPERADO = "\n".join([
    "Hola SENTIDA, les paso mi comanda:",
    f"Fecha: {FUTURA_TEXTO}",
    "Tamaño: mediana (15 a 25 porciones)",
    "Bizcochuelo: vainilla",
    "Relleno: dulce de leche con chips y nuez",
    "Segundo relleno: frutos rojos",
    "Decoración: flores naturales en tonos pastel (como la de flores naturales)",
    "Nombre: Mamá",
    "Número: 60",
])


def texto_de(url):
    assert url.startswith("https://wa.me/5491158300787?text=")
    q = url.split("?text=", 1)[1]
    assert "+" not in q
    return unquote(q)


def test_ticket_y_mensaje_en_vivo(abrir):
    pg = abrir()
    assert pg.inner_text('.panel [data-clave="tamano"] dd') == "…"
    armar(pg)
    assert pg.input_value("#mensaje") == ESPERADO
    assert pg.inner_text('.panel [data-clave="relleno"] dd') == "dulce de leche con chips y nuez"
    assert pg.inner_text('.panel [data-clave="nombre"] dd') == "Mamá"
    assert pg.errores == []


def test_mandar_abre_whatsapp_con_el_mensaje(abrir):
    pg = abrir()
    armar(pg)
    with pg.context.expect_page() as nueva:
        pg.click("#envio button[type=submit]")
    assert texto_de(nueva.value.url) == ESPERADO


def test_no_hay_lo_charlamos(abrir):
    pg = abrir()
    assert pg.locator("input[value=charlamos]").count() == 0
    assert "charlamos" not in pg.text_content("#armado").lower()


def test_algo_mas_va_al_ticket_y_al_mensaje(abrir):
    pg = abrir()
    armar(pg)
    pg.fill("#ademas", "sin nuez, por favor")
    pg.keyboard.press("Tab")
    assert pg.text_content('.panel [data-clave="ademas"] dd') == "sin nuez, por favor"
    assert pg.input_value("#mensaje").endswith("\nAdemás: sin nuez, por favor")
    assert pg.text_content("#anuncio") == "Además: sin nuez, por favor"


def test_algo_mas_no_se_ve_sin_javascript(abrir):
    pg = abrir(java_script_enabled=False)
    assert pg.is_hidden("#campo-ademas")


def test_sin_fecha_limpia_la_fecha(abrir):
    pg = abrir()
    pg.fill("#fecha", FUTURA)
    pg.check("#sin-fecha")
    assert pg.input_value("#fecha") == ""
    assert "Fecha: a definir" in pg.input_value("#mensaje")
    pg.fill("#fecha", FUTURA)
    assert not pg.is_checked("#sin-fecha")


def test_mensaje_editado_a_mano_no_se_pisa(abrir):
    pg = abrir()
    armar(pg)
    pg.fill("#mensaje", "Hola, quiero algo especial")
    pg.click('.panel [data-clave="bizcochuelo"] .ticket-ir')
    pg.check("input[name=bizcochuelo][value=chocolate]")
    pg.evaluate("ComandaPasos.ir(7)")
    assert pg.input_value("#mensaje") == "Hola, quiero algo especial"
    assert pg.is_visible("#reescribir")
    pg.click("#reescribir")
    assert "Bizcochuelo: chocolate" in pg.input_value("#mensaje")
    assert pg.is_hidden("#reescribir")


def test_caracteres_raros_llegan_enteros(abrir):
    pg = abrir()
    armar(pg, hasta=6)
    pg.fill("#idea", 'rosa & dorado #1, "vintage" 🌸')
    pg.click("#siguiente")
    with pg.context.expect_page() as nueva:
        pg.click("#envio button[type=submit]")
    assert 'Decoración: rosa & dorado #1, "vintage" 🌸' in texto_de(nueva.value.url)


def test_fecha_minima_es_hoy(abrir):
    pg = abrir()
    assert pg.get_attribute("#fecha", "min") == pg.evaluate(
        "(()=>{const d=new Date();return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')})()")
