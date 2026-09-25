def test_empezar_lleva_al_paso_y_enfoca_su_titulo(abrir):
    pg = abrir()
    pg.click("#empezar")
    pg.wait_for_timeout(80)
    assert pg.evaluate("document.activeElement.id") == "paso-1-t"
    assert pg.url.endswith("#paso-1")
    assert pg.evaluate("document.querySelector('.panel .ticket').getAnimations().length") == 1
    # Queda justo debajo de la cabecera fija (scroll-padding-top), no tapada por ella.
    margen = pg.evaluate("parseFloat(getComputedStyle(document.documentElement).scrollPaddingTop)")
    assert abs(pg.evaluate("document.getElementById('comanda').getBoundingClientRect().top") - margen) < 2
    pg.wait_for_timeout(900)
    assert pg.evaluate("document.getAnimations().filter(a => a.playState === 'running').length") == 0


def test_doble_toque_una_sola_animacion(abrir):
    pg = abrir()
    pg.click("#empezar")
    pg.evaluate("document.getElementById('empezar').click()")
    assert pg.evaluate("document.querySelector('.panel .ticket').getAnimations().length") == 1
    assert pg.errores == []


def test_empezar_en_celular_anima_la_tira(abrir):
    pg = abrir(390, 844, is_mobile=True, has_touch=True)
    pg.click("#empezar")
    pg.wait_for_timeout(80)
    assert pg.evaluate("document.getElementById('tira').getAnimations().length") == 1
    assert pg.evaluate("document.activeElement.id") == "paso-1-t"


def test_sin_movimiento_no_anima(abrir):
    pg = abrir(reduced_motion="reduce")
    assert "mov" not in pg.evaluate("document.documentElement.className").split()
    pg.click("#empezar")
    pg.wait_for_timeout(50)
    assert pg.evaluate("document.querySelector('.panel .ticket').getAnimations().length") == 0
    assert pg.evaluate("document.activeElement.id") == "paso-1-t"


def test_la_linea_nueva_se_imprime(abrir):
    pg = abrir()
    pg.check("#sin-fecha")
    assert pg.get_attribute('.panel [data-clave="fecha"]', "class") == "nueva"


def test_menu_se_cierra_al_elegir_y_con_escape(abrir):
    pg = abrir(390, 844, is_mobile=True, has_touch=True)
    pg.click(".menu summary")
    assert pg.evaluate("document.querySelector('.menu').open")
    pg.keyboard.press("Escape")
    assert not pg.evaluate("document.querySelector('.menu').open")
    assert pg.evaluate("document.activeElement.tagName") == "SUMMARY"
    pg.click(".menu summary")
    # Elegir un enlace cierra el menú (acá no se navega para poder mirarlo).
    pg.evaluate("document.querySelector('.menu nav a').addEventListener('click', e => e.preventDefault())")
    pg.click(".menu nav a")
    assert not pg.evaluate("document.querySelector('.menu').open")
    pg.click(".menu summary")
    pg.mouse.click(5, 600)  # el margen de la portada: afuera del menú y sin enlaces
    assert not pg.evaluate("document.querySelector('.menu').open")
