from urllib.parse import unquote

from fechas import FUTURA, FUTURA_TEXTO

CEL = dict(is_mobile=True, has_touch=True)
CLAVE = "sentida-pedido-v1"
KEY = '[data-producto="key-lime-pie"]'


def test_las_tortas_de_la_casa(abrir):
    pg = abrir()
    assert pg.text_content("h1") == "Nuestras tortas."
    assert pg.locator("[data-producto]").count() == 13
    assert pg.locator('[data-producto="pan-dulce"]').count() == 0
    for fuera in ("cheesecake-dulce-de-leche", "pavlova-dulce-de-leche"):
        assert pg.locator(f'[data-producto="{fuera}"]').count() == 0, fuera
    assert pg.get_attribute('.cab-nav a[aria-current="page"]', "href") == "../tortas/"
    for slug in ("key-lime-pie", "cheesecake-new-york", "marquise", "frutillas-con-crema",
                 "sablee", "pavlova-lima", "choco-oreo"):
        assert pg.locator(f"#{slug}").count() == 1, slug
    sin_foto = pg.locator(".producto .sin-foto").count()
    # Con varias fotos, la tarjeta lleva una galería: se cuenta la primera de cada una.
    con_foto = pg.locator(".producto .producto-foto img:first-child").count()
    assert sin_foto + con_foto == 13
    assert pg.text_content(f"{KEY} .producto-meta span:first-child") == "Las de la casa"
    # Los productos cuelgan del h1 (h2) y la primera fila no espera para cargar.
    assert pg.locator(".producto h3").count() == 0
    primeras = ".producto-foto img:first-child"
    assert pg.eval_on_selector_all(primeras, "is => is.slice(0, 3).map(i => i.loading)") == ["auto"] * 3
    assert pg.eval_on_selector_all(primeras, "is => is.slice(3).every(i => i.loading === 'lazy')")
    # Las fotos extra de las galerías siempre esperan.
    assert pg.eval_on_selector_all(".galeria-tira img:not(:first-child)", "is => is.length > 0 && is.every(i => i.loading === 'lazy')")
    assert pg.get_attribute(f"{KEY} .producto-agregar", "aria-label") == "Agregar al pedido: Key Lime Pie"
    assert pg.errores == []


def test_la_pasteleria_y_la_mesa_dulce(abrir):
    pg = abrir(pagina="pasteleria/")
    assert pg.text_content("h1") == "Pastelería."
    assert pg.locator("[data-producto]").count() == 6
    # Las tres galletas son un solo producto, con tres fotos.
    for fuera in ("galletas-corazon", "galletas-tematicas"):
        assert pg.locator(f'[data-producto="{fuera}"]').count() == 0, fuera
    assert pg.locator('[data-producto="galletas-decoradas"] .galeria-tira img').count() == 3
    assert pg.locator('[data-producto="shots"] .galeria-tira img').count() == 5
    assert pg.locator(".producto .sin-foto").count() == 0
    assert pg.text_content('[data-producto="cuadraditos-dulces"] .producto-tipo') == "Cuadraditos"
    assert pg.text_content('[data-producto="shots"] .producto-tipo') == "Shots"
    assert pg.text_content('[data-producto="shots"] h2') == "Shots"
    assert pg.text_content(".tienda-cab .eti") == "Para regalar y compartir"
    assert "chupito" not in pg.content().lower()
    # La mesa dulce es solo texto: las fotos viven en los productos.
    assert pg.locator(".mesa-dulce img").count() == 0
    assert "vasitos" not in pg.text_content(".mesa-dulce").lower()
    href = pg.get_attribute(".mesa-dulce .enlace", "href")
    assert unquote(href.split("?text=", 1)[1]) == "Hola SENTIDA, quiero consultar por una mesa dulce.\nFecha:\nInvitados:"


def test_agregar_suma_al_ticket_y_a_la_cabecera(abrir):
    pg = abrir()
    assert pg.is_hidden(KEY + " .producto-wa")
    pg.click(KEY + " .producto-agregar")
    assert pg.is_hidden(KEY + " .producto-agregar")
    assert pg.text_content(KEY + " .contador output") == "1"
    assert pg.evaluate("document.activeElement.hasAttribute('data-mas')")
    assert pg.text_content(".tienda-panel .carrito-nombre") == "Key Lime Pie"
    assert pg.is_visible(".tienda-panel .tienda-terminar")
    assert pg.text_content(".cab .mi-pedido-n") == "1"


def test_sumar_y_restar_hasta_sacar(abrir):
    pg = abrir()
    t = '[data-producto="marquise"]'
    pg.click(t + " .producto-agregar")
    pg.click(t + " [data-mas]")
    pg.click(t + " [data-mas]")
    assert pg.text_content(t + " output") == "3"
    assert pg.text_content(".cab .mi-pedido-n") == "3"
    for _ in range(3):
        pg.click(t + " [data-menos]")
    assert pg.is_visible(t + " .producto-agregar")
    assert pg.evaluate("document.activeElement.classList.contains('producto-agregar')")
    assert pg.locator(".tienda-panel .carrito-item").count() == 0
    assert pg.is_hidden(".cab .mi-pedido-n")
    assert pg.is_hidden(".tienda-panel .tienda-terminar")


def test_el_pedido_pasa_de_tortas_a_pasteleria(abrir, sitio):
    pg = abrir()
    pg.click(KEY + " .producto-agregar")
    pg.goto(sitio + "pasteleria/")
    pg.wait_for_load_state("networkidle")
    pg.click('[data-producto="alfajores-maicena"] .producto-agregar')
    assert pg.locator(".tienda-panel .carrito-item").count() == 2
    assert pg.text_content(".cab .mi-pedido-n") == "2"


def test_mi_pedido_en_todas_las_paginas(abrir, sitio):
    pg = abrir()
    pg.click(KEY + " .producto-agregar")
    for ruta in ("", "arma-tu-torta/", "pasteleria/", "tortas/"):
        pg.goto(sitio + ruta)
        pg.wait_for_load_state("networkidle")
        assert pg.text_content(".cab [data-mi-pedido] .mi-pedido-n") == "1", ruta
        pg.click(".cab [data-mi-pedido]")
        assert pg.evaluate("document.getElementById('carrito-dialogo').open"), ruta
        assert pg.text_content("#carrito-dialogo .carrito-nombre") == "Key Lime Pie"
        pg.keyboard.press("Escape")
        assert pg.evaluate("document.activeElement.hasAttribute('data-mi-pedido')"), ruta


def test_el_mensaje_sale_como_la_especificacion(abrir, sitio):
    pg = abrir()
    pg.click(KEY + " .producto-agregar")
    pg.goto(sitio + "pasteleria/")
    pg.wait_for_load_state("networkidle")
    t = '[data-producto="alfajores-maicena"]'
    pg.click(t + " .producto-agregar")
    for _ in range(11):
        pg.click(t + " [data-mas]")
    pg.click(".tienda-panel .tienda-terminar")
    pg.fill("#carrito-fecha", FUTURA)
    pg.fill("#carrito-nombre", "Laura")
    pg.fill("#carrito-ademas", "sin nuez, por favor")
    with pg.context.expect_page() as nueva:
        pg.click("#carrito-dialogo [type=submit]")
    url = nueva.value.url
    assert url.startswith("https://wa.me/5491158300787?text=")
    q = url.split("?text=", 1)[1]
    assert "+" not in q
    assert unquote(q) == "\n".join([
        "Hola SENTIDA, quiero hacer este pedido:",
        "• Key Lime Pie × 1",
        "• Alfajores de maicena × 12",
        f"Para: {FUTURA_TEXTO}",
        "Entrega: retiro en Martínez",
        "A nombre de: Laura",
        "Además: sin nuez, por favor",
        "¿Me confirman precio y disponibilidad?",
    ])


def test_el_contador_de_la_tarjeta_no_pasa_de_99(abrir):
    pg = abrir(init=f"localStorage.setItem('{CLAVE}', JSON.stringify({{items: [{{slug: 'marquise', nombre: 'Marquise', cant: 99}}]}}));")
    assert pg.text_content('[data-producto="marquise"] output') == "99"
    assert pg.is_disabled('[data-producto="marquise"] [data-mas]')


def test_llegar_con_ancla_marca_la_tarjeta(abrir):
    pg = abrir(pagina="tortas/#marquise")
    assert "marcada" in pg.get_attribute('[data-producto="marquise"]', "class")


def test_la_tira_del_celular(abrir):
    pg = abrir(390, 844, **CEL)
    assert pg.is_hidden(".tira-pedido")
    pg.click(KEY + " .producto-agregar")
    assert pg.is_visible(".tira-pedido")
    assert pg.text_content(".tira-pedido-n") == "1 producto"
    pg.click(".tira-pedido button")
    assert pg.evaluate("document.getElementById('carrito-dialogo').open")


def test_sin_js_cada_tarjeta_tiene_su_whatsapp(abrir):
    pg = abrir(java_script_enabled=False)
    n = pg.locator("[data-producto]").count()
    assert n == 13
    assert pg.locator("[data-producto] .producto-wa:visible").count() == n
    assert pg.locator("[data-producto] .producto-agregar:visible").count() == 0
    href = pg.get_attribute(KEY + " .producto-wa", "href")
    assert unquote(href.split("?text=", 1)[1]) == "Hola SENTIDA, quiero pedir: Key Lime Pie.\nPara:\nCantidad:"
    assert "+" not in href
    assert pg.get_attribute(".cab [data-mi-pedido]", "href") == "../tortas/#pedido"
    assert pg.is_visible(".tienda-panel [data-carrito-vacio]")


GAL = '[data-producto="key-lime-pie"] .galeria'


def test_la_galeria_de_la_tarjeta(abrir):
    pg = abrir()
    assert pg.locator(".galeria").count() == 6
    assert pg.locator(f"{GAL} .galeria-tira img").count() == 4
    assert pg.get_attribute(f"{GAL} .galeria-ant", "aria-label") == "Foto anterior"
    assert pg.get_attribute(f"{GAL} .galeria-sig", "aria-label") == "Foto siguiente"
    assert pg.text_content(f"{GAL} .galeria-estado") == "Foto 1 de 4"
    assert pg.locator(f"{GAL} .galeria-puntos span").count() == 4
    # Las flechas aparecen al pasar y miden 44 px.
    pg.hover(GAL)
    caja = pg.locator(f"{GAL} .galeria-sig").bounding_box()
    assert caja["width"] >= 44 and caja["height"] >= 44
    pg.click(f"{GAL} .galeria-sig")
    pg.wait_for_function(f"document.querySelector('{GAL} .galeria-estado').textContent === 'Foto 2 de 4'")
    assert pg.eval_on_selector_all(f"{GAL} .galeria-puntos span", "ss => ss.map(s => s.classList.contains('actual'))") == [False, True, False, False]
    # La anterior desde la primera da la vuelta a la última.
    pg.click(f"{GAL} .galeria-ant")
    pg.wait_for_function(f"document.querySelector('{GAL} .galeria-estado').textContent === 'Foto 1 de 4'")
    pg.click(f"{GAL} .galeria-ant")
    pg.wait_for_function(f"document.querySelector('{GAL} .galeria-estado').textContent === 'Foto 4 de 4'")
    # El «+» sigue andando.
    pg.click(KEY + " .producto-agregar")
    assert pg.text_content(KEY + " .contador output") == "1"
    assert pg.errores == []


def test_la_galeria_se_desliza_en_el_celular(abrir):
    pg = abrir(390, 844, **CEL)
    assert pg.is_hidden(f"{GAL} .galeria-sig") is False  # existe, pero no se ve sin foco
    assert pg.evaluate(f"getComputedStyle(document.querySelector('{GAL} .galeria-sig')).opacity") == "0"
    pg.evaluate(f"(t => t.scrollTo({{left: t.clientWidth}}))(document.querySelector('{GAL} .galeria-tira'))")
    pg.wait_for_function(f"document.querySelector('{GAL} .galeria-estado').textContent === 'Foto 2 de 4'")


def test_la_galeria_sin_js_es_una_tira(abrir):
    pg = abrir(390, 844, java_script_enabled=False, **CEL)
    assert pg.is_hidden(f"{GAL} .galeria-sig")
    assert pg.is_hidden(f"{GAL} .galeria-puntos")
    assert pg.get_attribute(f"{GAL} .galeria-tira", "tabindex") == "0"
    assert pg.evaluate(f"(t => t.scrollWidth > t.clientWidth * 3)(document.querySelector('{GAL} .galeria-tira'))")
    # Una sola foto: la tarjeta queda como siempre.
    assert pg.locator('[data-producto="pavlova-lima"] .galeria').count() == 0
