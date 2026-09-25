from ayuda_decoradas import armar, completar, siguiente

CEL = dict(is_mobile=True, has_touch=True)


def test_foto_del_panel_sigue_al_paso(abrir):
    pg = abrir()
    assert pg.get_attribute(".panel-foto", "data-activo") == "1"
    armar(pg, hasta=4)
    assert pg.get_attribute(".panel-foto", "data-activo") == "4"
    for n in (4, 5):
        completar(pg, n)
        siguiente(pg)
    assert pg.get_attribute(".panel-foto", "data-activo") == "6"
    assert pg.text_content("#panel-pie") == "Hecha por nosotras · torta de pétalos"
    caja = pg.locator(".panel .ticket").bounding_box()
    assert caja["y"] >= 0 and caja["y"] + caja["height"] <= 900
    pg.click("#volver")
    assert pg.get_attribute(".panel-foto", "data-activo") == "5"


def test_tira_reemplaza_la_cabecera(abrir):
    pg = abrir(390, 844, **CEL)
    assert pg.locator("#tira").is_hidden()
    pg.click("#empezar")
    assert pg.locator("#tira").is_visible()
    assert pg.evaluate("getComputedStyle(document.querySelector('.cab')).visibility") == "hidden"
    completar(pg, 1)
    siguiente(pg)
    pg.check("input[name=tamano][value=chica]")
    assert pg.text_content(".tira-et") == "Tamaño"
    assert pg.text_content(".tira-val") == "chica (10 a 12 porciones)"
    pg.evaluate("document.querySelector('.pie').scrollIntoView({behavior: 'instant'})")
    pg.wait_for_timeout(500)
    assert pg.locator("#tira").is_hidden()


def test_dialogo_de_la_comanda(abrir):
    pg = abrir(390, 844, **CEL)
    pg.click("#empezar")
    armar(pg, hasta=3)
    pg.check("input[name=bizcochuelo][value=chocolate]")
    pg.click(".tira-ver")
    assert pg.evaluate("document.getElementById('comanda-dialogo').open")
    assert pg.get_attribute(".tira-ver", "aria-expanded") == "true"
    assert pg.inner_text('#comanda-dialogo [data-clave="bizcochuelo"] dd') == "chocolate"
    pg.keyboard.press("Escape")
    assert not pg.evaluate("document.getElementById('comanda-dialogo').open")
    assert pg.evaluate("document.activeElement.classList.contains('tira-ver')")


def test_mandar_desde_el_dialogo(abrir):
    pg = abrir(390, 844, **CEL)
    pg.click("#empezar")
    armar(pg, hasta=3)
    pg.check("input[name=bizcochuelo][value=vainilla]")
    pg.click(".tira-ver")
    with pg.context.expect_page() as nueva:
        pg.click("#comanda-dialogo button[type=submit]")
    assert "Bizcochuelo%3A%20vainilla" in nueva.value.url
