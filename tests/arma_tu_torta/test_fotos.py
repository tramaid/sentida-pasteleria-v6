"""Paso 6: fotos de referencia. Van en memoria; un enlace de WhatsApp solo
lleva texto: «Mandar» abre el chat de Anto y, en el celular, «Mandar las
fotos» las comparte aparte."""
import struct
import zlib
from urllib.parse import unquote

from ayuda_decoradas import armar, completar, siguiente

CEL = dict(is_mobile=True, has_touch=True)
CHAT = "Fotos de referencia: te las mando en el chat"
NOTA_CHAT = "WhatsApp no deja adjuntar fotos desde la web: cuando se abra el chat, mandá las fotos ahí."

# Sin hoja de compartir (como en muchas computadoras).
SIN_COMPARTIR = "delete Navigator.prototype.canShare; delete Navigator.prototype.share;"
# Una hoja de compartir de mentira: guarda lo que recibe.
COMPARTIR = """
window.__compartido = [];
window.__abiertas = 0;
window.__falla = null;
Object.defineProperty(Navigator.prototype, 'canShare', {configurable: true,
  value: function (d) { return !!(d && d.files && d.files.length); }});
Object.defineProperty(Navigator.prototype, 'share', {configurable: true, value: function (d) {
  window.__compartido.push({n: d.files.length, nombres: d.files.map(f => f.name), tipos: d.files.map(f => f.type), texto: d.text});
  if (window.__falla) { var e = new Error('x'); e.name = window.__falla; return Promise.reject(e); }
  return Promise.resolve();
}});
var abrir = window.open;
window.open = function () { window.__abiertas++; return abrir.apply(window, arguments); };
"""


def png(color=(200, 120, 90)):
    """Un PNG de 4x4 de un color."""
    fila = b"\x00" + bytes(color) * 4
    def trozo(tipo, datos):
        return struct.pack(">I", len(datos)) + tipo + datos + struct.pack(">I", zlib.crc32(tipo + datos))
    return (b"\x89PNG\r\n\x1a\n" + trozo(b"IHDR", struct.pack(">IIBBBBB", 4, 4, 8, 2, 0, 0, 0))
            + trozo(b"IDAT", zlib.compress(fila * 4)) + trozo(b"IEND", b""))


def fotos(n, desde=1):
    return [{"name": f"idea-{i}.png", "mimeType": "image/png", "buffer": png((40 * i % 255, 120, 90))}
            for i in range(desde, desde + n)]


def miniaturas(pg):
    return pg.locator("#fotos-lista li").count()


def en_el_paso_6(pg):
    armar(pg, hasta=6)
    completar(pg, 6)


def test_adjuntar_y_quitar(abrir):
    pg = abrir(init=SIN_COMPARTIR)
    en_el_paso_6(pg)
    assert pg.is_visible("#fotos-adjuntar")
    assert pg.text_content("#fotos-adjuntar").strip() == "Adjuntar fotos"
    pg.set_input_files("#fotos", fotos(2))
    assert miniaturas(pg) == 2
    assert pg.get_attribute("#fotos-lista li:nth-child(2) img", "alt") == "Foto de referencia 2"
    assert pg.evaluate("document.querySelector('#fotos-lista img').src").startswith("blob:")
    assert "2 fotos agregadas" in pg.text_content("#anuncio")
    assert pg.inner_text('.panel [data-clave="fotos"] dd') == "2 de referencia"
    assert f"{CHAT} (2)" in pg.input_value("#mensaje")

    # Se suman en otra tanda.
    pg.set_input_files("#fotos", fotos(1, desde=3))
    assert miniaturas(pg) == 3
    assert pg.inner_text('.panel [data-clave="fotos"] dd') == "3 de referencia"

    pg.click("[aria-label='Quitar foto 1']")
    assert miniaturas(pg) == 2
    assert "Foto 1 quitada. Quedan 2 fotos." == pg.text_content("#anuncio")
    assert pg.evaluate("document.activeElement.getAttribute('aria-label')") == "Quitar foto 1"
    pg.click("[aria-label='Quitar foto 2']")
    pg.click("[aria-label='Quitar foto 1']")
    assert miniaturas(pg) == 0
    assert pg.evaluate("document.activeElement.id") == "fotos-adjuntar"
    assert pg.locator('.panel [data-clave="fotos"]').count() == 0
    assert "Fotos" not in pg.input_value("#mensaje")
    assert pg.errores == []


def test_hasta_seis(abrir):
    pg = abrir(init=SIN_COMPARTIR)
    en_el_paso_6(pg)
    pg.set_input_files("#fotos", fotos(8))
    assert miniaturas(pg) == 6
    assert pg.is_visible("#fotos-aviso")
    assert pg.text_content("#fotos-aviso") == "Entran hasta 6 fotos: sumamos las primeras 6 y quedaron afuera 2."
    pg.set_input_files("#fotos", fotos(1, desde=9))
    assert miniaturas(pg) == 6
    assert "máximo" in pg.text_content("#fotos-aviso")
    # Quitar una deja lugar y borra el aviso.
    pg.click("[aria-label='Quitar foto 6']")
    assert pg.is_hidden("#fotos-aviso")
    pg.set_input_files("#fotos", fotos(1, desde=9))
    assert miniaturas(pg) == 6
    assert pg.errores == []


def test_sin_hoja_de_compartir_abre_el_chat_y_avisa(abrir):
    pg = abrir(init=SIN_COMPARTIR)
    en_el_paso_6(pg)
    assert pg.is_hidden("#nota-fotos")
    pg.set_input_files("#fotos", fotos(2))
    siguiente(pg)
    assert pg.is_visible("#nota-fotos")
    assert pg.text_content("#nota-fotos [data-nota-texto]") == NOTA_CHAT
    assert pg.is_hidden("#compartir-fotos")
    assert pg.locator("#fotos-mini img:visible").count() == 2
    with pg.context.expect_page() as nueva:
        pg.click("#envio button[type=submit]")
    texto = unquote(nueva.value.url.split("?text=", 1)[1])
    assert texto.startswith("Hola SENTIDA, les paso mi comanda:")
    assert f"\n{CHAT} (2)\n" in texto
    # Las miniaturas siguen, para acordarse de cuáles mandar.
    assert miniaturas(pg) == 2
    assert pg.is_visible("#nota-fotos")
    assert pg.errores == []


def test_sin_fotos_no_hay_nota_ni_linea(abrir):
    pg = abrir(init=SIN_COMPARTIR)
    armar(pg)
    assert pg.is_hidden("#nota-fotos")
    with pg.context.expect_page() as nueva:
        pg.click("#envio button[type=submit]")
    assert "Fotos" not in unquote(nueva.value.url)


def test_en_el_celular_mandar_abre_el_chat_de_anto_y_las_fotos_van_despues(abrir):
    pg = abrir(390, 844, init=COMPARTIR, **CEL)
    en_el_paso_6(pg)
    pg.set_input_files("#fotos", fotos(2))
    siguiente(pg)
    assert "Mandar las fotos" in pg.text_content("#nota-fotos [data-nota-texto]")
    assert pg.is_visible("#compartir-fotos")
    # «Mandar» va directo al chat de Anto (el número, no la hoja de compartir).
    with pg.context.expect_page() as nueva:
        pg.click("#envio button[type=submit]")
    url = nueva.value.url
    assert url.startswith("https://wa.me/5491158300787") or "5491158300787" in url
    assert f"\n{CHAT} (2)\n" in unquote(url.split("?text=", 1)[1])
    assert pg.evaluate("window.__compartido.length") == 0
    # Después, solo las fotos.
    pg.click("#compartir-fotos")
    pg.wait_for_function("window.__compartido.length === 1")
    c = pg.evaluate("window.__compartido[0]")
    assert c["n"] == 2 and c["nombres"] == ["idea-1.png", "idea-2.png"] and c.get("texto") is None
    assert pg.errores == []


def test_en_el_celular_cancelar_las_fotos_no_abre_nada(abrir):
    pg = abrir(390, 844, init=COMPARTIR, **CEL)
    en_el_paso_6(pg)
    pg.set_input_files("#fotos", fotos(1))
    siguiente(pg)
    pg.evaluate("window.__falla = 'AbortError'")
    pg.click("#compartir-fotos")
    pg.wait_for_function("window.__compartido.length === 1")
    pg.wait_for_timeout(200)
    assert pg.evaluate("window.__abiertas") == 0
    assert pg.errores == []


def test_el_enlace_de_nadia_sigue_siendo_solo_texto(abrir):
    pg = abrir(init=SIN_COMPARTIR)
    en_el_paso_6(pg)
    pg.set_input_files("#fotos", fotos(2))
    siguiente(pg)
    assert pg.get_attribute(".cierre-nadia a", "href") == \
        "https://wa.me/5491131459646?text=Hola%20SENTIDA%2C%20quiero%20hacer%20un%20pedido."


def test_empezar_de_nuevo_saca_las_fotos_y_el_borrador_no_las_guarda(abrir, sitio):
    pg = abrir(init=SIN_COMPARTIR)
    en_el_paso_6(pg)
    pg.set_input_files("#fotos", fotos(2))
    pg.fill("#idea", "rosa y dorado")
    pg.locator("#idea").dispatch_event("change")
    guardado = pg.evaluate("localStorage.getItem('sentida-comanda-v1')")
    assert "fotos" not in guardado and "rosa y dorado" in guardado
    siguiente(pg)
    pg.click("#reiniciar")
    assert miniaturas(pg) == 0
    assert pg.is_hidden("#nota-fotos")
    assert "Fotos" not in pg.input_value("#mensaje")
    assert pg.errores == []
