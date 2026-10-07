"""Genera las páginas de la tienda, tortas/index.html y pasteleria/index.html,
a partir de datos/catalogo.json; las páginas legales, privacidad/ y terminos/,
a partir de legal/; y la cabecera y el pie de las páginas escritas a mano
(index, nosotras, arma-tu-torta).

Uso, desde sentida-site/:
    python herramientas/generar_tienda.py

El HTML generado se sube al repo y GitHub Pages lo sirve tal cual: no hay
build. Esas páginas no se editan a mano: se cambia el catálogo (o se suma
una foto con preparar_foto.py) y se vuelve a correr esto.
"""
import html
import re
import json
import pathlib
from urllib.parse import quote

from jinja2 import Environment, FileSystemLoader
from PIL import Image

RAIZ = pathlib.Path(__file__).resolve().parents[1]
FOTOS = RAIZ / "assets" / "fotos"
SITIO = "https://tramaid.github.io/sentida-pasteleria/"
ANTO = "5491158300787"
# La tienda (sentida-tienda): ahí vive el formulario del Botón de arrepentimiento,
# porque el sitio no tiene servidor. Hoy, la vista previa en Render; en
# producción la tienda cuelga del mismo dominio, en /tienda/.
TIENDA = "https://sentida-tienda.onrender.com/"
# Los textos legales y los datos del titular: una sola fuente para el sitio y
# la tienda (que los copia con `flask sincronizar-marca`).
LEGAL = RAIZ / "legal"
PAGINAS_LEGALES = {
    "privacidad": ("Política de privacidad", "Cómo cuidamos tus datos personales: qué recolectamos, para qué y cómo ejercer tus derechos."),
    "terminos": ("Términos y condiciones", "Cómo se hace un pedido, precios, pago, retiro y envíos, cambios y el derecho de arrepentimiento."),
}
TAMANOS_TARJETA = "(max-width: 1099px) 45vw, 24vw"

MENU = [
    ("tortas", "Nuestras tortas", "tortas/"),
    ("arma-tu-torta", "Armá tu torta", "arma-tu-torta/"),
    ("pasteleria", "Pastelería", "pasteleria/"),
    ("nosotras", "Nosotras", "nosotras/"),
]
SECCION_ETI = {"tortas": "Las de la casa", "pasteleria": "Pastelería", "temporada": "De temporada"}
# La etiqueta sobre el título de cada página (no repite el título).
ETI_PAGINA = {"tortas": "Las de la casa", "pasteleria": "Para regalar y compartir"}
# Las tarjetas de la primera fila se ven al entrar: cargan sin esperar.
PRIMERA_FILA = 3
DESTACADOS_INICIO = "<!-- destacados:inicio -->"
DESTACADOS_FIN = "<!-- destacados:fin -->"
MARQUESINA_TEXTO = ["Lo soñás, lo creamos", "Pastelería artesanal", "Tortas a medida", "Hecho a mano"]

ICONOS = """<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">
  <symbol id="i-flecha" viewBox="0 0 24 24"><path d="M4 12h15M13.5 6.5 19 12l-5.5 5.5"/></symbol>
  <symbol id="i-izq" viewBox="0 0 24 24"><path d="M20 12H5M10.5 6.5 5 12l5.5 5.5"/></symbol>
  <symbol id="i-diagonal" viewBox="0 0 24 24"><path d="M7 17 17 7M9 7h8v8"/></symbol>
  <symbol id="i-menu" viewBox="0 0 24 24"><path d="M4 7h16M4 12h16M4 17h16"/></symbol>
  <symbol id="i-cerrar" viewBox="0 0 24 24"><path d="m6 6 12 12M18 6 6 18"/></symbol>
  <symbol id="i-bolsa" viewBox="0 0 24 24"><path d="M5 8h14l-1.2 12.5H6.2L5 8Z"/><path d="M9 10V6.5a3 3 0 0 1 6 0V10"/></symbol>
  <symbol id="i-whatsapp" viewBox="0 0 24 24"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.46 1.32 4.96L2 22l5.25-1.38a9.87 9.87 0 0 0 4.79 1.22c5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.82 9.82 0 0 0 12.04 2Zm0 18.13a8.2 8.2 0 0 1-4.19-1.15l-.3-.18-3.11.82.83-3.04-.2-.31a8.17 8.17 0 0 1-1.26-4.36c0-4.54 3.7-8.23 8.24-8.23 2.2 0 4.27.86 5.82 2.41a8.18 8.18 0 0 1 2.41 5.83c0 4.54-3.7 8.23-8.24 8.23Zm4.52-6.17c-.25-.12-1.46-.72-1.69-.8-.22-.09-.39-.13-.55.12-.17.25-.63.8-.78.96-.14.17-.29.19-.54.06-.25-.12-1.05-.38-2-1.23-.74-.66-1.24-1.47-1.38-1.72-.15-.25-.02-.39.11-.51.11-.11.25-.29.37-.44.13-.14.17-.25.25-.41.09-.17.04-.31-.02-.44-.06-.12-.55-1.34-.76-1.83-.2-.48-.4-.41-.55-.42h-.47c-.17 0-.43.06-.66.31-.22.25-.86.84-.86 2.06s.89 2.39 1.01 2.56c.13.16 1.74 2.66 4.22 3.73.59.25 1.05.4 1.41.52.59.19 1.13.16 1.56.1.47-.07 1.46-.6 1.67-1.18.2-.57.2-1.07.14-1.17-.06-.11-.22-.17-.47-.29Z"/></symbol>
</svg>"""

PANEL = """    <aside class="tienda-panel" id="pedido" aria-labelledby="pedido-t">
      <div class="ticket">
        <div class="papel">
          <div class="ticket-cab"><span>SENTIDA · Pastelería</span><span>Pedido</span></div>
          <h2 class="ticket-t display" id="pedido-t" tabindex="-1">Tu pedido</h2>
          <ul class="carrito-lista" role="list" data-carrito-lista></ul>
          <p class="carrito-vacio" data-carrito-vacio>Para juntar todo en un solo pedido hace falta JavaScript. Mientras, pedí cada producto con su enlace de WhatsApp.</p>
          <p class="ticket-fijo">Precio y disponibilidad te los confirmamos por WhatsApp.</p>
          <p class="ticket-pie"><a href="../arma-tu-torta/">¿Querés una torta decorada? Armala acá</a></p>
        </div>
      </div>
      <button type="button" class="btn btn-1 tienda-terminar" data-carrito-abrir hidden>Terminar pedido</button>
    </aside>"""

TIRA = """<div class="tira-pedido" hidden>
  <span class="tira-pedido-t">Tu pedido</span>
  <span class="tira-pedido-n">0 productos</span>
  <button type="button" data-carrito-abrir aria-label="Ver tu pedido">Ver</button>
</div>"""


def esc(texto):
    return html.escape(texto, quote=True)


def wa(texto):
    return f"https://wa.me/{ANTO}?text={quote(texto, safe='')}"


def img(nombre, alt, sizes, raiz="../", diferida=True):
    """<img> con las variantes que existan de assets/fotos/<nombre>.webp; '' si no hay foto."""
    base = FOTOS / f"{nombre}.webp"
    if not base.exists():
        return ""
    with Image.open(base) as im:
        ancho, alto = im.size
    srcset = [f"{raiz}assets/fotos/{nombre}-{w}.webp {w}w" for w in (480, 800)
              if w < ancho and (FOTOS / f"{nombre}-{w}.webp").exists()]
    srcset.append(f"{raiz}assets/fotos/{nombre}.webp {ancho}w")
    src = srcset[0].split(" ")[0]
    return (f'<img src="{src}" srcset="{", ".join(srcset)}" sizes="{sizes}" '
            f'width="{ancho}" height="{alto}" alt="{esc(alt)}"{' loading="lazy"' if diferida else ''} decoding="async">')


def enlaces(actual, ancho, raiz):
    out = []
    for clave, texto, href in MENU:
        extra = ' aria-current="page"' if clave == actual else ""
        if ancho and clave == "nosotras":
            extra += ' class="solo-ancho"'
        out.append(f'<a href="{raiz}{href}"{extra}>{texto}</a>')
    return out


def marquesina():
    """La cinta es decorativa (aria-hidden); la pausa no, porque la cinta se mueve sola."""
    tramo = " <i></i> ".join(MARQUESINA_TEXTO) + " <i></i>"
    pausa = ('<button type="button" class="marquesina-pausa" aria-pressed="false" aria-label="Pausar la cinta">'
             '<svg class="ico ico-pausar" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M9 6v12M15 6v12"/></svg>'
             '<svg class="ico ico-seguir" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M8 5.5v13l10-6.5-10-6.5Z"/></svg>'
             '</button>')
    return (f'<div class="marquesina"><div class="marquesina-pista" aria-hidden="true">'
            f'<span>{tramo}</span><span>{tramo}</span></div>{pausa}</div><!-- /marquesina -->')


def cabecera(actual, raiz="../"):
    nav = "".join(enlaces(actual, True, raiz))
    menu = "\n          ".join(enlaces(actual, False, raiz))
    inicio = raiz or "./"
    return f"""<header class="cab">
  <div class="cab-in">
    <a class="cab-marca" href="{inicio}" aria-label="SENTIDA Pastelería, inicio"><img class="marca-logo" src="{raiz}assets/marca/logo.svg" alt="SENTIDA" width="132" height="36"></a>
    <nav class="cab-nav" aria-label="Secciones">
      {nav}
    </nav>
    <div class="cab-acc">
      <a class="mi-pedido" href="{raiz}tortas/#pedido" data-mi-pedido><svg class="ico" aria-hidden="true" focusable="false"><use href="#i-bolsa"/></svg><span class="mi-pedido-t">Mi pedido</span><span class="mi-pedido-n" hidden>0</span></a>
      <details class="menu">
        <summary><span class="menu-abrir">Menú</span><span class="menu-cerrar">Cerrar</span><svg class="ico menu-i-abrir" aria-hidden="true" focusable="false"><use href="#i-menu"/></svg><svg class="ico menu-i-cerrar" aria-hidden="true" focusable="false"><use href="#i-cerrar"/></svg></summary>
        <nav aria-label="Menú">
          {menu}
        </nav>
      </details>
    </div>
  </div>
</header>
{marquesina()}"""


WA_PIE = ICONOS.split('<symbol id="i-whatsapp" viewBox="0 0 24 24">', 1)[1].split("</symbol>", 1)[0]
# Los íconos del pie viajan con el pie: las páginas escritas a mano no tienen
# todas el mismo sprite.
ICONOS_PIE = f"""<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">
    <symbol id="pie-wa" viewBox="0 0 24 24">{WA_PIE}</symbol>
    <symbol id="pie-ig" viewBox="0 0 24 24"><rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/><path d="M17.2 6.8h.01"/></symbol>
    <symbol id="pie-lugar" viewBox="0 0 24 24"><path d="M12 21s-6.5-5.6-6.5-11a6.5 6.5 0 0 1 13 0c0 5.4-6.5 11-6.5 11Z"/><circle cx="12" cy="10" r="2.3"/></symbol>
  </svg>"""


def ico_pie(cual):
    clase = "ico ico-wa" if cual == "wa" else "ico"
    return f'<svg class="{clase}" aria-hidden="true" focusable="false"><use href="#pie-{cual}"/></svg>'


def saber(raiz="../"):
    """La banda «Antes de pedir», arriba del pie: tres <details> que se abren
    sin JavaScript. Cada uno se abre por su cuenta."""
    consulta = wa("Hola SENTIDA, tengo una consulta.")
    return f"""<aside class="saber" aria-labelledby="saber-t">
  <div class="saber-in envoltorio">
    <div class="saber-cab">
      <p class="eti con-linea">Antes de pedir</p>
      <h2 class="display" id="saber-t">Lo que tenés <span class="acento">que saber.</span></h2>
      <p>¿Te queda otra duda? <a href="{consulta}" target="_blank" rel="noopener" aria-describedby="nueva-pestana">Escribinos por WhatsApp</a>.</p>
    </div>
    <div class="saber-lista">
      <details class="saber-item">
        <summary><span class="saber-n" aria-hidden="true">01</span><span class="saber-t">Pedidos y anticipación</span><span class="saber-mas" aria-hidden="true"></span></summary>
        <div class="saber-cuerpo">
          <ul role="list">
            <li>Trabajamos por encargo y con cupo por día: cuanto antes nos escribas, mejor.</li>
            <li>Nuestras tortas: pedilas con 48 h.</li>
            <li>Pastelería: de 4 a 7 días, según el trabajo.</li>
            <li>Tortas decoradas: armala en <a href="{raiz}arma-tu-torta/">Armá tu torta</a> y te confirmamos fecha y presupuesto por WhatsApp.</li>
          </ul>
        </div>
      </details>
      <details class="saber-item">
        <summary><span class="saber-n" aria-hidden="true">02</span><span class="saber-t">Retiro y envíos</span><span class="saber-mas" aria-hidden="true"></span></summary>
        <!-- Pendiente: Anto y Nadia confirman los horarios de retiro y hasta dónde llega el envío (las zonas: hoy, lo que entendemos, Vicente López y San Isidro). -->
        <div class="saber-cuerpo saber-dos">
          <div>
            <h3 class="saber-sub">Retiro en Martínez, San Isidro</h3>
            <ul role="list"><li>Coordinamos el día y el horario por WhatsApp.</li></ul>
          </div>
          <div>
            <h3 class="saber-sub">Envíos a Vicente López y San Isidro</h3>
            <ul role="list"><li>Te pasamos el costo por WhatsApp. Si estás en otra zona, consultanos.</li></ul>
          </div>
        </div>
      </details>
      <details class="saber-item">
        <summary><span class="saber-n" aria-hidden="true">03</span><span class="saber-t">Cambios y cancelaciones</span><span class="saber-mas" aria-hidden="true"></span></summary>
        <!-- Provisorio: los plazos de cambios y cancelaciones esperan la confirmación de Anto y Nadia. -->
        <div class="saber-cuerpo">
          <ul role="list">
            <li>Si necesitás cambiar la fecha, avisanos con al menos 7 días. La nueva fecha queda sujeta a nuestra disponibilidad y el presupuesto puede actualizarse.</li>
            <li>Para cancelar, avisanos con al menos 7 días.</li>
          </ul>
        </div>
      </details>
    </div>
  </div>
</aside>"""


def _legal():
    """El entorno de Jinja de legal/ y el contexto que esperan sus plantillas."""
    env = Environment(loader=FileSystemLoader(LEGAL), autoescape=True)
    titular = json.loads((LEGAL / "titular.json").read_text(encoding="utf-8"))
    return env, titular


def legal(plantilla, raiz="../"):
    """Una plantilla de legal/ (el pie o un texto), con las rutas del sitio."""
    env, titular = _legal()
    urls = {"privacidad": f"{raiz}privacidad/", "terminos": f"{raiz}terminos/",
            "arrepentimiento": f"{TIENDA}arrepentimiento"}
    return env.get_template(plantilla).render(
        titular=titular, urls=urls, wa=ANTO, wa_texto=f"11 {ANTO[5:9]}-{ANTO[9:]}").strip()


def pie(raiz="../"):
    """La banda «Antes de pedir» y el pie: marca · Explorá · Escribinos · el
    sello, y la franja legal (legal/pie.html)."""
    wa_anto = wa("Hola SENTIDA, quiero hacer un pedido.")
    wa_nadia = f"https://wa.me/5491131459646?text={quote('Hola SENTIDA, quiero hacer un pedido.', safe='')}"
    secciones = "\n".join(f'          <li><a href="{raiz}{href}">{texto}</a></li>' for _, texto, href in MENU)
    nueva = 'target="_blank" rel="noopener" aria-describedby="nueva-pestana"'
    return f"""{saber(raiz)}

<footer class="pie">
  {ICONOS_PIE}
  <div class="pie-in envoltorio">
    <div class="pie-marca">
      <img class="pie-logo" src="{raiz}assets/marca/logo-claro.svg" alt="SENTIDA" width="150" height="41" loading="lazy">
      <p class="pie-lema display">Lo soñás, lo creamos.</p>
    </div>
    <nav class="pie-links" aria-label="Pie">
      <div>
        <p class="pie-eti">Explorá</p>
        <ul role="list">
{secciones}
        </ul>
      </div>
      <div class="pie-contacto">
        <p class="pie-eti">Escribinos</p>
        <ul role="list">
          <li><a href="{wa_anto}" {nueva}>{ico_pie("wa")}WhatsApp de Anto</a></li>
          <li><a href="{wa_nadia}" {nueva}>{ico_pie("wa")}WhatsApp de Nadia</a></li>
          <li><a href="https://www.instagram.com/sentidapasteleria/" {nueva}>{ico_pie("ig")}@sentidapasteleria</a></li>
        </ul>
        <p class="pie-lugar">{ico_pie("lugar")}<span>Martínez, San Isidro<br>Solo por encargo</span></p>
      </div>
    </nav>
    <img class="pie-sello" src="{raiz}assets/marca/sello.svg" alt="" width="164" height="164" loading="lazy">
  </div>
  {legal("pie.html", raiz)}
  <div class="pie-fin envoltorio"><span>© 2026 SENTIDA Pastelería · Hecho a mano</span><a class="pie-trama" href="https://tramaid.com.ar" {nueva}>Diseño <img src="{raiz}assets/marca/trama.svg" alt="TRAMA" width="78" height="15" loading="lazy"></a></div>
</footer>"""


BLOQUE_CAB = re.compile(r'<header class="cab">.*?</header>(?:\n<div class="marquesina".*?<!-- /marquesina -->)?', re.S)
BLOQUE_PIE = re.compile(r'(?:<aside class="saber".*?</aside>\n\n)?<footer class="pie">.*?</footer>', re.S)
A_MANO = [("index.html", None, ""), ("nosotras/index.html", "nosotras", "../"),
          ("arma-tu-torta/index.html", "arma-tu-torta", "../")]


def comunes(html_pagina, actual, raiz):
    assert BLOQUE_CAB.search(html_pagina) and BLOQUE_PIE.search(html_pagina), "falta la cabecera o el pie"
    html_pagina = BLOQUE_CAB.sub(lambda m: cabecera(actual, raiz), html_pagina, count=1)
    return BLOQUE_PIE.sub(lambda m: pie(raiz), html_pagina, count=1)


FLECHA_ANT = '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M14.5 6 8.5 12l6 6"/></svg>'
FLECHA_SIG = '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="m9.5 6 6 6-6 6"/></svg>'


def galeria(nombre, fotos, agregar):
    """Varias fotos en la tarjeta: una tira que se desliza (con o sin JavaScript).
    Las flechas, los puntos y el aviso «Foto n de N» los prende comun/tienda.js."""
    total = len(fotos)
    puntos = '<span class="actual"></span>' + "<span></span>" * (total - 1)
    return (f'<div class="producto-foto galeria" data-galeria>'
            f'<div class="galeria-tira" tabindex="0" role="group" aria-label="Fotos de {esc(nombre)}">{"".join(fotos)}</div>'
            f'<button type="button" class="galeria-flecha galeria-ant" aria-label="Foto anterior" hidden>{FLECHA_ANT}</button>'
            f'<button type="button" class="galeria-flecha galeria-sig" aria-label="Foto siguiente" hidden>{FLECHA_SIG}</button>'
            f'<span class="galeria-puntos" aria-hidden="true" hidden>{puntos}</span>'
            f'<span class="galeria-estado sr" aria-live="polite">Foto 1 de {total}</span>'
            f'{agregar}</div>')


def tarjeta(p, tipos, n, total, raiz="../", nivel=3):
    nombre = esc(p["nombre"])
    agregar = f'<button type="button" class="producto-agregar" aria-label="Agregar al pedido: {nombre}" hidden>+</button>'
    principal = img(p.get("foto") or p["slug"], "", TAMANOS_TARJETA, raiz,
                    diferida=not (nivel == 2 and n <= PRIMERA_FILA))
    extras = [f for f in (img(nombre, "", TAMANOS_TARJETA, raiz) for nombre in p.get("fotos", [])) if f]
    if principal and extras:
        partes = [galeria(p["nombre"], [principal] + extras, agregar)]
    elif principal:
        partes = [f'<div class="producto-foto">{principal}{agregar}</div>']
    else:
        partes = [f'<div class="producto-foto sin-foto"><span class="display" aria-hidden="true">{nombre}</span>{agregar}</div>']
    categoria = esc(tipos[p["tipo"]]) if p.get("tipo") else SECCION_ETI.get(p["seccion"], "")
    partes.append(f'<p class="producto-meta"><span class="producto-tipo">{categoria}</span><span>{n:02d} / {total:02d}</span></p>')
    partes.append(f'<h{nivel} class="display">{nombre}</h{nivel}>')
    if p.get("descripcion"):
        partes.append(f'<p class="producto-desc">{esc(p["descripcion"])}</p>')
    partes.append('<p class="producto-precio">Precio a consultar</p>')
    pedir = wa(f"Hola SENTIDA, quiero pedir: {p['nombre']}.\nPara:\nCantidad:")
    partes.append(f"""<div class="producto-acc">
          <a class="enlace producto-wa" href="{pedir}" target="_blank" rel="noopener" aria-describedby="nueva-pestana">Pedir por WhatsApp <svg class="ico" aria-hidden="true" focusable="false"><use href="#i-diagonal"/></svg></a>
          <span class="contador" hidden><button type="button" data-menos aria-label="Uno menos de {nombre}">−</button><output aria-live="off">0</output><button type="button" data-mas aria-label="Uno más de {nombre}">+</button></span>
        </div>""")
    cuerpo = "\n        ".join(partes)
    return f"""      <li class="producto" id="{p['slug']}" data-producto="{p['slug']}" data-nombre="{nombre}">
        {cuerpo}
      </li>"""


def destacados(datos):
    lista = [p for p in datos["productos"] if p.get("destacado") and p.get("visible", True)]
    return "\n".join(tarjeta(p, datos["tipos"], i + 1, len(lista), raiz="") for i, p in enumerate(lista))


def con_destacados(html_home, bloque):
    a = html_home.index(DESTACADOS_INICIO) + len(DESTACADOS_INICIO)
    b = html_home.index(DESTACADOS_FIN)
    return html_home[:a] + "\n" + bloque + "\n" + html_home[b:]


def mesa_dulce():
    """El cierre de Pastelería: solo el texto; las fotos están en los productos."""
    consulta = wa("Hola SENTIDA, quiero consultar por una mesa dulce.\nFecha:\nInvitados:")
    return f"""
      <section class="mesa-dulce" aria-labelledby="mesa-t">
        <h2 class="display" id="mesa-t">¿Es para una<br>mesa dulce?</h2>
        <div class="mesa-dulce-txt">
          <p>Shots, cuadraditos dulces, galletas con tu mensaje y alfajores. Armamos la mesa con vos, según los invitados.</p>
          <a class="enlace" href="{consulta}" target="_blank" rel="noopener" aria-describedby="nueva-pestana">Consultar por una mesa dulce <svg class="ico" aria-hidden="true" focusable="false"><use href="#i-diagonal"/></svg></a>
        </div>
      </section>"""


def pagina(clave, datos):
    sec = datos["secciones"][clave]
    productos = [p for p in datos["productos"] if p["seccion"] == clave and p.get("visible", True)]
    # En la tienda los productos cuelgan directo del h1: van en h2.
    tarjetas = "\n".join(tarjeta(p, datos["tipos"], i + 1, len(productos), nivel=2)
                         for i, p in enumerate(productos))
    extra = mesa_dulce() if clave == "pasteleria" else ""
    return f"""<!doctype html>
<!-- Generada por herramientas/generar_tienda.py desde datos/catalogo.json: no editar a mano. -->
<html lang="es-AR" class="sin-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<meta name="robots" content="noindex">
<title>{esc(sec["title"])}</title>
<meta name="description" content="{esc(sec["descripcion"])}">
<meta name="theme-color" content="#F6F3E9">
<link rel="canonical" href="{SITIO}{clave}/">
<link rel="icon" href="../assets/marca/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="../assets/apple-touch-icon.png">
<link rel="preload" href="../assets/fuentes/playfair-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="../assets/fuentes/montserrat-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="../comun/marca.css">
<link rel="stylesheet" href="../comun/base.css">
<link rel="stylesheet" href="../comun/ticket.css">
<link rel="stylesheet" href="../comun/tienda.css">
<script>
/* Sin JavaScript la página se ve completa: cada producto se pide con su
   enlace de WhatsApp. «js» habilita el pedido; «mov», el movimiento. */
(function (r) {{
  r.classList.remove('sin-js'); r.classList.add('js');
  if (!(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches)) r.classList.add('mov');
}})(document.documentElement);
</script>
<script src="../comun/base.js" defer></script>
<script src="../comun/menu.js" defer></script>
<script src="../comun/pedido-mensaje.js" defer></script>
<script src="../comun/carrito.js" data-raiz="../" defer></script>
<script src="../comun/tienda.js" defer></script>
</head>
<body>
{ICONOS}
<a class="saltar" href="#contenido">Saltar al contenido</a>
<p id="nueva-pestana" hidden>Se abre WhatsApp o Instagram en otra pestaña.</p>

{cabecera(clave, "../")}

<main id="contenido">
<section class="tienda" aria-labelledby="tienda-t">
  <div class="tienda-in">
    <div class="tienda-col">
      <div class="tienda-cab">
        <div><p class="eti con-linea">{esc(ETI_PAGINA.get(clave, ""))}</p>
        <h1 class="display" id="tienda-t">{esc(sec["titulo"])}</h1></div>
        <p>{esc(sec["bajada"])}</p>
      </div>
      <ul class="productos" role="list">
{tarjetas}
      </ul>{extra}
    </div>
{PANEL}
  </div>
</section>
</main>

{pie("../")}

{TIRA}
</body>
</html>
"""


def pagina_legal(clave):
    """privacidad/ o terminos/: el texto de legal/, con la cabecera y el pie
    del sitio. En noindex, como las demás páginas nuevas."""
    titulo, descripcion = PAGINAS_LEGALES[clave]
    return f"""<!doctype html>
<!-- Generada por herramientas/generar_tienda.py desde legal/{clave}.html: no editar a mano. -->
<html lang="es-AR" class="sin-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<meta name="robots" content="noindex">
<title>{titulo} · SENTIDA Pastelería</title>
<meta name="description" content="{esc(descripcion)}">
<meta name="theme-color" content="#F6F3E9">
<link rel="canonical" href="{SITIO}{clave}/">
<link rel="icon" href="../assets/marca/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="../assets/apple-touch-icon.png">
<link rel="preload" href="../assets/fuentes/playfair-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="../assets/fuentes/montserrat-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="../comun/marca.css">
<link rel="stylesheet" href="../comun/base.css">
<link rel="stylesheet" href="../comun/ticket.css">
<script>
(function (r) {{
  r.classList.remove('sin-js'); r.classList.add('js');
  if (!(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches)) r.classList.add('mov');
}})(document.documentElement);
</script>
<script src="../comun/base.js" defer></script>
<script src="../comun/menu.js" defer></script>
<script src="../comun/pedido-mensaje.js" defer></script>
<script src="../comun/carrito.js" data-raiz="../" defer></script>
</head>
<body>
{ICONOS}
<a class="saltar" href="#contenido">Saltar al contenido</a>
<p id="nueva-pestana" hidden>Se abre WhatsApp o Instagram en otra pestaña.</p>

{cabecera(clave, "../")}

<main id="contenido">
<article class="legal envoltorio" aria-labelledby="legal-t">
  <div class="legal-cab">
    <p class="eti con-linea">Información legal</p>
    <h1 class="display" id="legal-t">{titulo}.</h1>
  </div>
  <div class="legal-texto">
{legal(f"{clave}.html")}
  </div>
</article>
</main>

{pie("../")}
</body>
</html>
"""


def main():
    datos = json.loads((RAIZ / "datos" / "catalogo.json").read_text(encoding="utf-8"))
    for clave in ("tortas", "pasteleria"):
        destino = RAIZ / clave / "index.html"
        destino.parent.mkdir(exist_ok=True)
        destino.write_text(pagina(clave, datos), encoding="utf-8", newline="\n")
        print(destino.relative_to(RAIZ).as_posix())
    for clave in PAGINAS_LEGALES:
        destino = RAIZ / clave / "index.html"
        destino.parent.mkdir(exist_ok=True)
        destino.write_text(pagina_legal(clave), encoding="utf-8", newline="\n")
        print(destino.relative_to(RAIZ).as_posix())
    home = RAIZ / "index.html"
    home.write_text(con_destacados(home.read_text(encoding="utf-8"), destacados(datos)), encoding="utf-8", newline="\n")
    for ruta, actual, raiz in A_MANO:
        destino = RAIZ / ruta
        destino.write_text(comunes(destino.read_text(encoding="utf-8"), actual, raiz), encoding="utf-8", newline="\n")
        print(ruta)


if __name__ == "__main__":
    main()
