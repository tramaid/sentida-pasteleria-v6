def test_sin_js_se_ve_todo(abrir):
    pg = abrir(1440, 900, java_script_enabled=False)
    assert pg.evaluate("document.documentElement.className") == "sin-js"
    assert pg.locator(".paso").count() == 6
    for n in range(1, 7):
        assert pg.locator(f'.paso[data-n="{n}"]').is_visible()
    assert pg.locator("#cierre").is_visible()
    for oculto in ("#tira", "#pasos-nav", "#avance", "#campo-ademas"):
        assert pg.is_hidden(oculto), oculto
    assert pg.is_visible(".solo-sin-js")
    assert pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth") == 0


def test_sin_js_el_envio_solo_manda_el_texto(abrir):
    pg = abrir(390, 844, java_script_enabled=False, is_mobile=True, has_touch=True)
    envio = pg.locator("#envio")
    assert envio.get_attribute("action") == "https://wa.me/5491158300787"
    assert envio.get_attribute("method") == "get"
    assert pg.evaluate("[...document.querySelectorAll('#envio [name]')].map(e => e.name)") == ["text"]
    assert pg.input_value("#mensaje").startswith("Hola SENTIDA, les paso mi comanda:\nFecha:")
    pg.fill("#mensaje", "Hola SENTIDA, quiero una torta")
    with pg.context.expect_page() as nueva:
        pg.click("#envio button[type=submit]")
    url = nueva.value.url
    assert url.startswith("https://wa.me/5491158300787?text=")
    assert "torta" in url
    assert pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth") == 0
