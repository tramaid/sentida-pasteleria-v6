from urllib.parse import unquote


def test_la_pagina_de_nosotras(abrir, sitio):
    pg = abrir()
    assert pg.text_content("h1") == "Somos dos, y hacemos todo nosotras."
    assert pg.get_attribute('.cab-nav a[aria-current="page"]', "href") == "../nosotras/"
    assert pg.locator(".nos-foto img").count() == 2
    assert pg.errores == []


def test_cada_una_con_su_whatsapp(abrir):
    pg = abrir()
    wa = pg.eval_on_selector_all(".nos-foto figcaption a", "as => as.map(a => a.getAttribute('href'))")
    assert wa[0].startswith("https://wa.me/5491158300787?text=")
    assert wa[1].startswith("https://wa.me/5491131459646?text=")
    assert unquote(wa[0].split("?text=", 1)[1]).startswith("Hola SENTIDA")


def test_cierra_con_las_tres_puertas(abrir):
    pg = abrir()
    assert pg.eval_on_selector_all(".nos-puertas a", "as => as.map(a => a.getAttribute('href'))") == \
        ["../tortas/", "../arma-tu-torta/", "../pasteleria/"]
