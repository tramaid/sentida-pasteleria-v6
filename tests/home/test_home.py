from urllib.parse import unquote

CASA = ["key-lime-pie", "cheesecake-new-york", "marquise", "frutillas-con-crema", "sablee", "pavlova-lima", "choco-oreo"]


def hrefs(pg, sel):
    return pg.eval_on_selector_all(sel, "as => as.map(a => a.getAttribute('href'))")


def test_menu_nuevo(abrir):
    pg = abrir()
    assert hrefs(pg, ".cab-nav a") == ["tortas/", "decoradas/", "antojos/", "#nosotras"]
    assert pg.eval_on_selector_all(".cab-nav a", "as => as.map(a => a.textContent)") == \
        ["Nuestras tortas", "Decoradas", "Antojos", "Nosotras"]
    assert hrefs(pg, ".menu nav a") == ["tortas/", "decoradas/", "antojos/", "#nosotras", "#pedido"]
    assert pg.get_attribute(".cab [data-mi-pedido]", "href") == "tortas/#pedido"
    assert pg.locator(".cab-pedido").count() == 0


def test_hero_lleva_a_decoradas_y_a_la_tienda(abrir):
    pg = abrir()
    assert pg.get_attribute(".hero .btn-1", "href") == "decoradas/"
    assert pg.text_content(".hero .btn-1") == "Armá tu torta"
    assert pg.get_attribute(".hero .btn-2", "href") == "tortas/"
    assert pg.text_content(".hero .btn-2") == "Ver nuestras tortas"


def test_las_de_la_casa_van_a_su_torta_en_la_tienda(abrir, sitio):
    pg = abrir()
    assert hrefs(pg, ".carta-fila .plato > a") == [f"tortas/#{s}" for s in CASA]
    assert hrefs(pg, ".carta-otra a") == ["tortas/"]
    assert pg.locator(".carta-fila .plato-cta").first.text_content().strip() == "Ver en la tienda"
    tienda = abrir(pagina="tortas/")
    for s in CASA:
        assert tienda.locator(f'[data-producto="{s}"]').count() == 1, s


def test_las_decoradas_abren_la_comanda_con_su_referencia(abrir):
    pg = abrir()
    assert hrefs(pg, ".deco-mosaico a:not(.btn)") == [
        "decoradas/?ref=petalos", "decoradas/?ref=letras", "decoradas/?ref=letras",
        "decoradas/?ref=mensaje", "decoradas/", "decoradas/?ref=letras"]
    assert pg.get_attribute(".deco-texto .btn", "href") == "decoradas/"
    assert pg.text_content(".deco-texto .btn").strip() == "Armá tu torta"


def test_antojos_en_la_home(abrir):
    pg = abrir()
    assert pg.locator("#mesas").count() == 0
    assert pg.text_content("#mesas-t") == "Antojos,para compartir."
    enlaces = hrefs(pg, "#antojos .mesas-cab a")
    assert enlaces[0] == "antojos/"
    assert unquote(enlaces[1].split("?text=", 1)[1]) == "Hola SENTIDA, quiero consultar por una mesa dulce.\nFecha:\nInvitados:"


def test_como_pedir_tres_caminos(abrir):
    pg = abrir()
    assert pg.locator("#pedido .caminos > .camino").count() == 3
    assert hrefs(pg, "#pedido .camino .btn") == ["tortas/", "antojos/", "decoradas/"]
    wa = hrefs(pg, "#pedido .camino-wa a")
    assert wa[0].startswith("https://wa.me/5491158300787?text=")
    assert wa[1].startswith("https://wa.me/5491131459646?text=")
    assert wa[2] == "https://www.instagram.com/sentidapasteleria/"


def test_el_pie_lleva_a_las_tres_partes(abrir):
    pg = abrir()
    assert hrefs(pg, ".pie-links a")[:3] == ["tortas/", "decoradas/", "antojos/"]


def test_la_home_no_lleva_el_dia_de_la_madre(abrir):
    pg = abrir()
    assert pg.locator("#madre, .madre, .hero .chip").count() == 0
    assert pg.locator('a[href="#madre"]').count() == 0
    assert "Madre" not in pg.text_content("body")


def test_el_pie_no_lleva_el_sentida_gigante(abrir):
    # El pie cierra con el sello y los enlaces, como en el resto del sitio: nada en letra enorme.
    pg = abrir()
    mayor = pg.eval_on_selector_all(".pie *", "es => Math.max(...es.map(e => parseFloat(getComputedStyle(e).fontSize)))")
    assert mayor <= 28


def test_la_barra_del_celular_sigue_siendo_whatsapp(abrir):
    pg = abrir(390, 844, is_mobile=True, has_touch=True)
    assert pg.get_attribute(".barra-pedido", "href").startswith("https://wa.me/5491158300787?text=")


def test_no_queda_nada_de_la_tienda_v3(abrir):
    pg = abrir()
    assert pg.locator("a[href*='tienda-v3']").count() == 0
    assert pg.errores == []


def test_mi_pedido_vacio_en_la_home(abrir):
    # La home no carga base.css: lo que lleva `hidden` tiene que ocultarse igual.
    pg = abrir()
    assert pg.is_hidden(".cab .mi-pedido-n")
    pg.click(".cab [data-mi-pedido]")
    assert pg.is_hidden("#carrito-dialogo .carrito-form")
    assert pg.is_hidden("#carrito-dialogo [data-listo]")
    assert pg.is_visible("#carrito-dialogo [data-si-vacio]")


def test_los_botones_del_pedido_en_la_home_son_de_la_marca(abrir):
    # La home no carga base.css: los botones del diálogo no pueden caer en Arial ni en gris.
    pg = abrir()
    pg.click(".cab [data-mi-pedido]")
    estilo = "e => { const c = getComputedStyle(e); return [c.fontFamily, c.cursor, c.backgroundColor, c.color]; }"
    fuente, cursor, fondo, color = pg.eval_on_selector("#carrito-dialogo [data-si-vacio] .btn-2", estilo)
    assert fuente.startswith("Montserrat")
    assert cursor == "pointer"
    assert fondo == "rgba(0, 0, 0, 0)"
    assert color == "rgb(64, 45, 33)"
    assert pg.eval_on_selector("#carrito-dialogo [type=submit]", estilo)[0].startswith("Montserrat")


def test_en_la_home_no_dice_chupitos(abrir):
    # Se llaman «Shots» en todo el sitio.
    pg = abrir()
    assert "chupito" not in pg.content().lower()
