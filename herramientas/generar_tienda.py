"""Genera las páginas de la tienda, tortas/index.html y pasteleria/index.html,
a partir de datos/catalogo.json.

Uso, desde sentida-site/:
    python herramientas/generar_tienda.py

El HTML generado se sube al repo y GitHub Pages lo sirve tal cual: no hay
build. Esas páginas no se editan a mano: se cambia el catálogo (o se suma
una foto con preparar_foto.py) y se vuelve a correr esto.
"""
import html
import json
import pathlib
from urllib.parse import quote

from PIL import Image

RAIZ = pathlib.Path(__file__).resolve().parents[1]
FOTOS = RAIZ / "assets" / "fotos"
SITIO = "https://tramaid.github.io/sentida-pasteleria/"
ANTO = "5491158300787"
TAMANOS_TARJETA = "(max-width: 1099px) 45vw, 24vw"
TAMANOS_MESA = "(max-width: 899px) 45vw, 18vw"

MENU = [
    ("tortas", "Nuestras tortas", "../tortas/"),
    ("arma-tu-torta", "Armá tu torta", "../arma-tu-torta/"),
    ("pasteleria", "Pastelería", "../pasteleria/"),
    ("nosotras", "Nosotras", "../nosotras/"),
]

# La mesa dulce de Pastelería: (foto, epígrafe, texto alternativo).
MESA = [
    ("vasitos-flores", "Vasitos con flores", "Vasitos de postre con crema y flores comestibles"),
    ("carrot-mini", "Carrot cake en cuadraditos", "Cuadraditos de carrot cake con rosetas de frosting"),
    ("vasitos-frutillas", "Vasitos de frutillas", "Vasitos con frutillas, crema y merengue"),
    ("vasitos-maracuya", "Vasitos de maracuyá", "Vasitos de maracuyá con chocolate blanco"),
]

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

PIE = """<footer class="pie">
  <div class="pie-in envoltorio">
    <div class="pie-marca">
      <img src="../assets/SENTIDASELLO.svg" alt="" width="88" height="88" loading="lazy">
      <p class="display">Lo soñás,<br>lo creamos.</p>
    </div>
    <nav class="pie-links" aria-label="Pie">
      <ul role="list">
        <li><a href="../tortas/">Nuestras tortas</a></li>
        <li><a href="../arma-tu-torta/">Armá tu torta</a></li>
        <li><a href="../pasteleria/">Pastelería</a></li>
        <li><a href="../nosotras/">Nosotras</a></li>
      </ul>
      <ul role="list">
        <li><a href="https://wa.me/5491158300787?text=Hola%20SENTIDA%2C%20quiero%20hacer%20un%20pedido." target="_blank" rel="noopener" aria-describedby="nueva-pestana">WhatsApp</a></li>
        <li><a href="https://www.instagram.com/sentidapasteleria/" target="_blank" rel="noopener" aria-describedby="nueva-pestana">@sentidapasteleria</a></li>
      </ul>
      <p>Martínez, San Isidro<br>Solo por encargo</p>
    </nav>
  </div>
  <div class="pie-fin envoltorio"><span>© 2026 SENTIDA Pastelería</span><span>Propuesta de TRAMA</span></div>
</footer>"""

TIRA = """<div class="tira-pedido" hidden>
  <span class="tira-pedido-t">Tu pedido</span>
  <span class="tira-pedido-n">0 productos</span>
  <button type="button" data-carrito-abrir aria-label="Ver tu pedido">Ver</button>
</div>"""


def esc(texto):
    return html.escape(texto, quote=True)


def wa(texto):
    return f"https://wa.me/{ANTO}?text={quote(texto, safe='')}"


def img(nombre, alt, sizes):
    """<img> con las variantes que existan de assets/fotos/<nombre>.webp; '' si no hay foto."""
    base = FOTOS / f"{nombre}.webp"
    if not base.exists():
        return ""
    with Image.open(base) as im:
        ancho, alto = im.size
    srcset = [f"../assets/fotos/{nombre}-{w}.webp {w}w" for w in (480, 800)
              if w < ancho and (FOTOS / f"{nombre}-{w}.webp").exists()]
    srcset.append(f"../assets/fotos/{nombre}.webp {ancho}w")
    src = srcset[0].split(" ")[0]
    return (f'<img src="{src}" srcset="{", ".join(srcset)}" sizes="{sizes}" '
            f'width="{ancho}" height="{alto}" alt="{esc(alt)}" loading="lazy" decoding="async">')


def enlaces(actual, ancho):
    out = []
    for clave, texto, href in MENU:
        extra = ' aria-current="page"' if clave == actual else ""
        if ancho and clave == "nosotras":
            extra += ' class="solo-ancho"'
        out.append(f'<a href="{href}"{extra}>{texto}</a>')
    return out


def cabecera(actual):
    nav = "".join(enlaces(actual, ancho=True))
    menu = "\n          ".join(enlaces(actual, ancho=False))
    return f"""<header class="cab">
  <div class="cab-in">
    <nav class="cab-nav" aria-label="Secciones">
      {nav}
    </nav>
    <a class="cab-marca" href="../" aria-label="SENTIDA Pastelería, inicio"><img src="../assets/logo-sentida.svg" alt="SENTIDA Pastelería" width="116" height="44"></a>
    <div class="cab-acc">
      <a class="mi-pedido" href="../tortas/#pedido" data-mi-pedido><svg class="ico" aria-hidden="true" focusable="false"><use href="#i-bolsa"/></svg><span class="mi-pedido-t">Mi pedido</span><span class="mi-pedido-n" hidden>0</span></a>
      <details class="menu">
        <summary><span class="menu-abrir">Menú</span><span class="menu-cerrar">Cerrar</span><svg class="ico menu-i-abrir" aria-hidden="true" focusable="false"><use href="#i-menu"/></svg><svg class="ico menu-i-cerrar" aria-hidden="true" focusable="false"><use href="#i-cerrar"/></svg></summary>
        <nav aria-label="Menú">
          {menu}
        </nav>
      </details>
    </div>
  </div>
</header>"""


def tarjeta(p, tipos):
    nombre = esc(p["nombre"])
    foto = img(p.get("foto") or p["slug"], "", TAMANOS_TARJETA)
    if foto:
        partes = [f'<div class="producto-foto">{foto}</div>']
    else:
        partes = [f'<div class="producto-foto sin-foto" aria-hidden="true"><span class="display">{nombre}</span></div>']
    if p.get("tipo"):
        partes.append(f'<p class="producto-tipo">{esc(tipos[p["tipo"]])}</p>')
    partes.append(f'<h3 class="display">{nombre}</h3>')
    if p.get("descripcion"):
        partes.append(f'<p class="producto-desc">{esc(p["descripcion"])}</p>')
    pedir = wa(f"Hola SENTIDA, quiero pedir: {p['nombre']}.\nPara:\nCantidad:")
    partes.append(f"""<div class="producto-acc">
          <a class="enlace producto-wa" href="{pedir}" target="_blank" rel="noopener" aria-describedby="nueva-pestana">Pedir por WhatsApp <svg class="ico" aria-hidden="true" focusable="false"><use href="#i-diagonal"/></svg></a>
          <button type="button" class="btn btn-1 producto-agregar" aria-label="Agregar al pedido: {nombre}" hidden>Agregar al pedido</button>
          <span class="contador" hidden><button type="button" data-menos aria-label="Uno menos de {nombre}">−</button><output aria-live="off">0</output><button type="button" data-mas aria-label="Uno más de {nombre}">+</button></span>
        </div>""")
    cuerpo = "\n        ".join(partes)
    return f"""      <li class="producto" id="{p['slug']}" data-producto="{p['slug']}" data-nombre="{nombre}">
        {cuerpo}
      </li>"""


def mesa_dulce():
    fotos = "\n".join(
        f'          <li><figure><div class="foto">{img(nombre, alt, TAMANOS_MESA)}</div>'
        f'<figcaption>{esc(epigrafe)}</figcaption></figure></li>'
        for nombre, epigrafe, alt in MESA)
    consulta = wa("Hola SENTIDA, quiero consultar por una mesa dulce.\nFecha:\nInvitados:")
    return f"""
      <section class="mesa-dulce" aria-labelledby="mesa-t">
        <h2 class="display" id="mesa-t">¿Es para una<br>mesa dulce?</h2>
        <div class="mesa-dulce-txt">
          <p>Vasitos, carrot cake en cuadraditos, galletas con tu mensaje y alfajores. Armamos la mesa con vos, según los invitados.</p>
          <a class="enlace" href="{consulta}" target="_blank" rel="noopener" aria-describedby="nueva-pestana">Consultar por una mesa dulce <svg class="ico" aria-hidden="true" focusable="false"><use href="#i-diagonal"/></svg></a>
        </div>
        <ul class="mesa-fotos" role="list">
{fotos}
        </ul>
      </section>"""


def pagina(clave, datos):
    sec = datos["secciones"][clave]
    productos = [p for p in datos["productos"] if p["seccion"] == clave and p.get("visible", True)]
    tarjetas = "\n".join(tarjeta(p, datos["tipos"]) for p in productos)
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
<meta name="theme-color" content="#FEFAF8">
<link rel="canonical" href="{SITIO}{clave}/">
<link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="../assets/apple-touch-icon.png">
<link rel="preload" href="../assets/fuentes/erode-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="../assets/fuentes/montserrat-latin.woff2" as="font" type="font/woff2" crossorigin>
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

{cabecera(clave)}

<main id="contenido">
<section class="tienda" aria-labelledby="tienda-t">
  <div class="tienda-in">
    <div class="tienda-col">
      <div class="tienda-cab">
        <h1 class="display" id="tienda-t">{esc(sec["titulo"])}</h1>
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

{PIE}

{TIRA}
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


if __name__ == "__main__":
    main()
