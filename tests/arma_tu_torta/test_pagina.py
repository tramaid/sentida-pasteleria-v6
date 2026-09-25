MENU = ["Nuestras tortas", "Armá tu torta", "Pastelería", "Nosotras"]


def test_cabecera_del_sitio(abrir, sitio):
    pg = abrir()
    nav = pg.eval_on_selector_all(".cab-nav a", "as => as.map(a => [a.textContent, a.href])")
    assert nav == [["Nuestras tortas", sitio + "tortas/"], ["Armá tu torta", sitio + "arma-tu-torta/"],
                   ["Pastelería", sitio + "pasteleria/"], ["Nosotras", sitio + "nosotras/"]]
    assert pg.get_attribute('.cab-nav a[aria-current="page"]', "href") == "../arma-tu-torta/"
    assert pg.get_attribute(".cab-marca", "href") == "../"
    assert pg.get_attribute(".cab [data-mi-pedido]", "href") == "../tortas/#pedido"
    assert pg.eval_on_selector_all(".menu nav a", "as => as.map(a => a.textContent)") == MENU


def test_la_pagina_es_solo_la_comanda(abrir):
    pg = abrir()
    for fuera in ("#carta", "#mesas", "#nosotras"):
        assert pg.locator(fuera).count() == 0, fuera
    assert pg.text_content(".ticket-portada h1") == "Armá tu torta."
    assert pg.text_content(".portada-sub") == "En seis pasos, y te la cotizamos por WhatsApp."
    assert pg.get_attribute(".ticket-portada .btn-2", "href") == "../tortas/"
    assert pg.text_content(".ticket-portada .btn-2") == "Ver nuestras tortas"
    assert pg.eval_on_selector_all(".pie-links a[href^='../']", "as => as.map(a => a.getAttribute('href'))") == \
        ["../tortas/", "../arma-tu-torta/", "../pasteleria/", "../nosotras/"]


def test_los_pasos_tienen_su_ancla_y_titulo_enfocable(abrir):
    pg = abrir()
    for n in range(1, 7):
        assert pg.get_attribute(f"#paso-{n} .paso-t", "tabindex") == "-1"
    assert pg.get_attribute("#cierre .cierre-t", "tabindex") == "-1"
    sin_js = abrir(java_script_enabled=False)
    assert sin_js.is_hidden("#pasos-nav")
    assert sin_js.is_hidden("#avance")


def test_en_1100_el_menu_pasa_al_boton(abrir):
    pg = abrir(1000, 800)
    assert pg.is_hidden(".cab-nav")
    assert pg.is_visible(".menu summary")
    ancho = abrir(1440, 900)
    assert ancho.is_visible(".cab-nav")
    assert ancho.is_hidden(".menu summary")
