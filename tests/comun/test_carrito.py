import json
from urllib.parse import unquote

from fechas import FUTURA, FUTURA_TEXTO

CLAVE = "sentida-pedido-v1"


def guardado(items, **mas):
    """Script de init que deja un pedido guardado antes de que cargue la página."""
    return f"localStorage.setItem('{CLAVE}', {json.dumps(json.dumps({'items': items, **mas}))});"


UNO = guardado([{"slug": "key-lime-pie", "nombre": "Key Lime Pie", "cant": 1}])


def abrir_pedido(pg):
    pg.click(".cab [data-mi-pedido]")
    assert pg.evaluate("document.getElementById('carrito-dialogo').open")


def mandar(pg):
    pg.fill("#carrito-fecha", FUTURA)
    pg.fill("#carrito-nombre", "Laura")
    with pg.context.expect_page() as nueva:
        pg.click("#carrito-dialogo [type=submit]")
    return nueva.value.url


def test_mi_pedido_vacio(abrir):
    pg = abrir()
    assert pg.is_hidden(".cab .mi-pedido-n")
    assert pg.get_attribute(".cab [data-mi-pedido]", "aria-label") == "Mi pedido, vacío"
    abrir_pedido(pg)
    assert pg.is_visible("#carrito-dialogo [data-carrito-vacio]")
    assert pg.is_hidden("#carrito-dialogo .carrito-form")
    assert pg.eval_on_selector_all("#carrito-dialogo [data-si-vacio] a",
                                   "as => as.map(a => a.getAttribute('href'))") == ["../tortas/", "../pasteleria/"]
    assert pg.evaluate("document.activeElement.id") == "carrito-t"
    pg.keyboard.press("Escape")
    assert pg.evaluate("document.activeElement.hasAttribute('data-mi-pedido')")


def test_mi_pedido_con_un_producto(abrir):
    pg = abrir(init=UNO)
    assert pg.text_content(".cab .mi-pedido-n") == "1"
    assert pg.get_attribute(".cab [data-mi-pedido]", "aria-label") == "Mi pedido, 1 producto"
    abrir_pedido(pg)
    assert pg.text_content("#carrito-dialogo .carrito-nombre") == "Key Lime Pie"
    assert pg.is_visible("#carrito-dialogo .carrito-form")
    assert pg.get_attribute("#carrito-dialogo .carrito-decorada a", "href") == "../arma-tu-torta/"


def test_sumar_y_restar_desde_el_ticket(abrir):
    pg = abrir(init=UNO)
    abrir_pedido(pg)
    pg.click("#carrito-dialogo [data-mas]")
    assert pg.text_content("#carrito-dialogo .contador output") == "2"
    assert pg.text_content(".cab .mi-pedido-n") == "2"
    assert pg.evaluate("document.activeElement.hasAttribute('data-mas')")
    pg.click("#carrito-dialogo [data-menos]")
    pg.click("#carrito-dialogo [data-menos]")
    assert pg.locator("#carrito-dialogo .carrito-item").count() == 0
    assert pg.is_visible("#carrito-dialogo [data-carrito-vacio]")
    assert pg.evaluate("document.activeElement.id") == "carrito-t"
    assert pg.evaluate(f"JSON.parse(localStorage.getItem('{CLAVE}')).items") == []
    assert pg.text_content(".carrito-anuncio") == "Sacaste Key Lime Pie del pedido."


def test_pide_fecha_y_nombre(abrir):
    pg = abrir(init=UNO)
    abrir_pedido(pg)
    pg.click("#carrito-dialogo [type=submit]")
    assert pg.text_content("#carrito-dialogo [data-falta]") == "Elegí para cuándo lo querés."
    assert pg.evaluate("document.activeElement.id") == "carrito-fecha"
    pg.fill("#carrito-fecha", FUTURA)
    pg.click("#carrito-dialogo [type=submit]")
    assert pg.text_content("#carrito-dialogo [data-falta]") == "Decinos a nombre de quién."
    assert pg.evaluate("document.activeElement.id") == "carrito-nombre"


def test_el_mensaje_con_envio_y_algo_mas(abrir):
    pg = abrir(init=guardado([{"slug": "key-lime-pie", "nombre": "Key Lime Pie", "cant": 1},
                              {"slug": "alfajores-maicena", "nombre": "Alfajores de maicena", "cant": 12}]))
    abrir_pedido(pg)
    pg.check("#carrito-dialogo input[name=entrega][value=envio]")
    pg.fill("#carrito-ademas", "sin nuez, por favor")
    url = mandar(pg)
    assert url.startswith("https://wa.me/5491158300787?text=")
    q = url.split("?text=", 1)[1]
    assert "+" not in q
    assert unquote(q) == "\n".join([
        "Hola SENTIDA, quiero hacer este pedido:",
        "• Key Lime Pie × 1",
        "• Alfajores de maicena × 12",
        f"Para: {FUTURA_TEXTO}",
        "Entrega: envío a domicilio",
        "A nombre de: Laura",
        "Además: sin nuez, por favor",
        "¿Me confirman precio y disponibilidad?",
    ])
    assert pg.is_visible("#carrito-dialogo [data-listo]")
    assert pg.is_hidden("#carrito-dialogo .carrito-form")
    assert pg.evaluate("document.activeElement.hasAttribute('data-vaciar')")


def test_lo_escrito_queda_guardado(abrir, sitio):
    pg = abrir()
    pg.evaluate("Carrito.cambiar('marquise', 'Marquise', 1)")
    abrir_pedido(pg)
    pg.fill("#carrito-nombre", "Laura")
    pg.check("#carrito-dialogo input[name=entrega][value=envio]")
    pg.goto(sitio + "arma-tu-torta/")
    pg.wait_for_load_state("networkidle")
    abrir_pedido(pg)
    assert pg.input_value("#carrito-nombre") == "Laura"
    assert pg.is_checked("#carrito-dialogo input[name=entrega][value=envio]")


def test_vaciar_despues_de_mandar(abrir):
    pg = abrir(init=UNO)
    abrir_pedido(pg)
    mandar(pg)
    pg.click("#carrito-dialogo [data-vaciar]")
    assert not pg.evaluate("document.getElementById('carrito-dialogo').open")
    assert pg.is_hidden(".cab .mi-pedido-n")
    assert pg.evaluate(f"JSON.parse(localStorage.getItem('{CLAVE}')).items") == []


def test_todavia_no_vuelve_al_formulario(abrir):
    pg = abrir(init=UNO)
    abrir_pedido(pg)
    mandar(pg)
    pg.click("#carrito-dialogo [data-todavia]")
    assert pg.is_visible("#carrito-dialogo .carrito-form")
    assert pg.is_hidden("#carrito-dialogo [data-listo]")
    assert pg.text_content(".cab .mi-pedido-n") == "1"


def test_pestana_bloqueada_va_en_la_misma(abrir):
    pg = abrir(init=UNO + " window.open = () => null;")
    abrir_pedido(pg)
    pg.fill("#carrito-fecha", FUTURA)
    pg.fill("#carrito-nombre", "Laura")
    with pg.expect_navigation():
        pg.click("#carrito-dialogo [type=submit]")
    assert pg.url.startswith("https://wa.me/5491158300787?text=")


def test_datos_raros_no_se_interpretan(abrir):
    raros = guardado([{"slug": "x", "nombre": "<img src=x onerror=window.__roto=1>", "cant": 2},
                      {"slug": "<b>", "nombre": "Mal", "cant": 1},
                      {"slug": "marquise", "nombre": "Marquise", "cant": "3"}], fecha="2020-01-01")
    pg = abrir(init=raros)
    abrir_pedido(pg)
    assert pg.evaluate("window.__roto") is None
    assert pg.locator("#carrito-dialogo .carrito-lista img").count() == 0
    assert pg.eval_on_selector_all("#carrito-dialogo .carrito-nombre", "es => es.map(e => e.textContent)") == \
        ["<img src=x onerror=window.__roto=1>", "Marquise"]
    assert pg.text_content(".cab .mi-pedido-n") == "5"
    assert pg.input_value("#carrito-fecha") == ""
    assert pg.errores == []


def test_guardado_roto_no_rompe(abrir):
    pg = abrir(init=f"localStorage.setItem('{CLAVE}', '{{roto');")
    assert pg.errores == []
    assert pg.is_hidden(".cab .mi-pedido-n")


def test_dos_pestanas_se_sincronizan(abrir, sitio):
    pg = abrir()
    otra = pg.context.new_page()
    otra.goto(sitio + "arma-tu-torta/")
    otra.wait_for_load_state("networkidle")
    pg.evaluate("Carrito.cambiar('marquise', 'Marquise', 2)")
    otra.wait_for_function("document.querySelector('.cab .mi-pedido-n').textContent === '2'")


def test_no_pasa_de_99(abrir):
    pg = abrir(init=guardado([{"slug": "shots", "nombre": "Shots", "cant": 99}]))
    abrir_pedido(pg)
    assert pg.is_disabled("#carrito-dialogo [data-mas]")
    pg.evaluate("Carrito.cambiar('shots', 'Shots', 1)")
    assert pg.text_content(".cab .mi-pedido-n") == "99"


def test_nadia_lleva_el_mismo_pedido(abrir):
    pg = abrir(init=UNO)
    abrir_pedido(pg)
    href = pg.get_attribute("#carrito-dialogo [data-nadia]", "href")
    assert href.startswith("https://wa.me/5491131459646?text=")
    assert "• Key Lime Pie × 1" in unquote(href.split("?text=", 1)[1])


def test_el_boton_cerrar_no_tapa_el_ticket(abrir):
    pg = abrir(390, 844, init=UNO, is_mobile=True, has_touch=True)
    abrir_pedido(pg)
    x = pg.locator("#carrito-dialogo .carrito-cerrar").bounding_box()
    t = pg.locator("#carrito-dialogo .ticket-cab").bounding_box()
    se_pisan = x["x"] < t["x"] + t["width"] and t["x"] < x["x"] + x["width"] and \
        x["y"] < t["y"] + t["height"] and t["y"] < x["y"] + x["height"]
    assert not se_pisan


def test_una_fecha_pasada_no_se_manda(abrir):
    pg = abrir(init=UNO)
    abrir_pedido(pg)
    pg.fill("#carrito-fecha", "2020-01-01")
    pg.fill("#carrito-nombre", "Laura")
    pg.click("#carrito-dialogo [type=submit]")
    assert pg.text_content("#carrito-dialogo [data-falta]") == "Elegí una fecha de hoy en adelante."
    assert pg.evaluate("document.activeElement.id") == "carrito-fecha"
    assert len(pg.context.pages) == 1


def test_el_pedido_es_un_panel_a_la_derecha(abrir):
    pg = abrir(init=UNO)
    abrir_pedido(pg)
    # Espera a que termine la entrada desde la derecha.
    pg.wait_for_function("document.getElementById('carrito-dialogo').getAnimations().every(a => a.playState === 'finished')")
    r = pg.evaluate("(() => { const b = document.getElementById('carrito-dialogo').getBoundingClientRect();"
                    " return [Math.round(b.right), Math.round(b.top), Math.round(b.height), Math.round(b.width)]; })()")
    assert r == [1440, 0, 900, 480]


def test_en_el_celular_acostado_se_llega_a_mandar(abrir):
    pg = abrir(844, 390, init=UNO, is_mobile=True, has_touch=True)
    abrir_pedido(pg)
    enviar = pg.locator("#carrito-dialogo [type=submit]")
    enviar.scroll_into_view_if_needed()
    assert enviar.is_visible()
    caja = enviar.bounding_box()
    assert caja["y"] >= 0 and caja["y"] + caja["height"] <= 390
