# SENTIDA — réplica funcional del home

Sitio estático, responsive y sin proceso de compilación.

## Abrir

Ejecutar un servidor local desde esta carpeta, por ejemplo:

```bash
python -m http.server 8080
```

Luego visitar `http://localhost:8080`.

## Estructura

- `index.html`, `home.css`, `home.js`: la home (v4).
- `decoradas/`, `tortas/`, `antojos/` y `comun/`: el resto del sitio (ver «El sitio en tres partes», más abajo).
- `datos/catalogo.json` y `herramientas/`: el catálogo de la tienda y los scripts que arman sus páginas y sus fotos.
- `assets/`: logo, fuentes y fotografías (`assets/fotos/`, cada una en 480, 800 y tamaño completo).
- `home-v1.html`, `styles.css` y `app.js`: la home anterior, de referencia.

## Datos de contacto

SENTIDA elabora en Martínez, Buenos Aires, y no tiene local a la calle. Los pedidos se toman por WhatsApp:

- Anto: `https://wa.me/5491158300787` (11 5830-0787)
- Nadia: `https://wa.me/5491131459646` (11 3145-9646)
- Instagram: `https://www.instagram.com/sentidapasteleria/`

El prefijo `54 9` es obligatorio para que WhatsApp resuelva móviles argentinos; no quitarlo al editar.

## Pendientes comerciales

- Varias fotos del banco llevan el sello de la marca anterior y dos tarjetas muestran un producto distinto al de su título (ver `QA.md`).
- No hay definición sobre precios, detalle por producto ni zona de entrega.

## Marca (28/09/2026)

El logo nuevo, el sello y la tipografía Playfair. Spec en
`docs/superpowers/specs/2026-09-28-marca-tienda-ficha-design.md`.

- Los colores del logo y las fuentes (Playfair en los títulos, Montserrat en el
  texto) viven en `comun/marca.css`. Cada página lo carga antes que `base.css`.
- Los logos, el sello y el favicon están en `assets/marca/`, y las fuentes en
  `assets/fuentes/`.
- Los SVG que llegan de Illustrator se pasan por `herramientas/limpiar_svg.py`
  antes de guardarlos. El script saca el `<style>` interno y los ids, y deja el
  `fill` directo. Ejemplo: `python herramientas/limpiar_svg.py origen.svg assets/marca/sello.svg`.
- La tienda (`../sentida-tienda`) usa una copia de todo esto. Después de cambiar
  la marca, correr esto en la tienda:
  `SECRET_KEY=dev python -m flask --app app sincronizar-marca ../sentida-site`.
  Su test `tests/test_marca.py` avisa si la copia quedó vieja.

## v6: el estilo de sentida-v2 (27/09/2026)

Rama `v6`. La cara de la propuesta `tramaid/sentida-v2`, que les gustó a las
dueñas, sobre el sitio que funciona de la v5. Spec en
`docs/superpowers/specs/2026-09-26-v6-estilo-v2-design.md`; plan en
`docs/superpowers/plans/2026-09-26-v6-estilo-v2.md`.

- `herramientas/generar_tienda.py` ahora arma también la cabecera, la marquesina
  y el pie de `index.html`, `nosotras/` y `arma-tu-torta/`, y el bloque «Lo que
  más nos piden» de la home (productos con `"destacado": true`). Después de
  tocar el catálogo o esas partes, correrlo.
- El pedido se abre como panel lateral. Los títulos iban en Erode 400; desde el 28/09 van en Playfair (ver «Marca»).

## v5: la home con tres puertas (25/09/2026)

Rama `v5`. Pedido de la clienta: al entrar, elegir primero qué se busca. Spec en
`docs/superpowers/specs/2026-09-25-v5-tres-puertas-design.md`.

| Menú | Dirección | Qué hay |
| --- | --- | --- |
| Nuestras tortas | `/tortas/` | Las tortas de la casa, con carrito a WhatsApp |
| Armá tu torta | `/arma-tu-torta/` | La comanda de la torta decorada; termina en WhatsApp |
| Pastelería | `/pasteleria/` | Shots, cookies, alfajores, cupcakes y la mesa dulce |
| Nosotras | `/nosotras/` | Quiénes son, el manifiesto y «Hecho a mano» |

- **La home** (`index.html`, `home.css`) tiene el lema, las tres puertas a
  sangre, una línea que lleva a Nosotras y «Cómo pedir» en tres pasos. Usa
  `comun/base.css` como el resto del sitio.
- **Direcciones viejas:** `/decoradas/`, `/antojos/` y `/comanda/` redirigen a
  las nuevas y conservan la búsqueda (`?…`) y el `#`.
- **Fotos de referencia** (paso 6 de Armá tu torta, `fotos.js`): hasta 6,
  en memoria (no van al borrador). Un enlace `wa.me` solo lleva texto: en
  pantallas táctiles con `navigator.share` las fotos salen con el mensaje por
  la hoja de compartir; si no, el mensaje dice «te las mando en el chat» y una
  nota junto a «Mandar» lo explica. Sin JavaScript el campo no aparece.
- Lo que sigue: los rellenos de Armá tu torta con una sola lista, la venta por
  media docena y docena en Pastelería, y el logo nuevo cuando esté en vector.

La sección de abajo describe la v4.

## El sitio en tres partes (24/09/2026)

Propuesta para las dueñas: queda así hasta que ellas la revisen. Spec en
`docs/superpowers/specs/2026-09-24-sitio-tres-partes-design.md`; plan en
`docs/superpowers/plans/2026-09-24-sitio-tres-partes.md`.

| Menú | Dirección | Qué hay | Cómo se pide |
| --- | --- | --- | --- |
| Nuestras tortas | `/tortas/` | Las tortas de la casa | Carrito que termina en un WhatsApp |
| Decoradas | `/decoradas/` | La comanda, un paso por vez | Presupuesto por WhatsApp |
| Antojos | `/antojos/` | Alfajores, galletas, cupcakes, shots y la mesa dulce | Carrito; la mesa dulce, por WhatsApp |
| Nosotras | `/#nosotras` | La sección de la home | — |

- **La home** (`index.html`, `home.css`, `home.js`) es la v4. Su hero lleva a
  Decoradas y a Nuestras tortas; «Las de la casa» lleva a cada torta en la
  tienda; las fotos de decoradas abren la comanda; «Cómo pedir» ofrece la tienda, Decoradas y WhatsApp directo. La
  barra de WhatsApp del celular sigue igual. La home no lleva el Día de la
  Madre (se sacó el 25/09/2026).
- **El hero de la home** tiene el texto quieto y cinco fotos que se turnan
  (`hero.js`): Key Lime, cheesecake New York, carrot, la torta con letra y el
  cheesecake Marroc, a sangre y fundidas con el crema. Para cambiar una foto,
  pasar la nueva (JPEG, PNG o WebP; 2048 x 3072 va bien) por
  `python herramientas/preparar_foto.py --hero <archivo> hero-key-lime` (o
  `hero-cheesecake`, `hero-carrot`, `hero-letra-f`, `hero-marroc`): borra los
  tamaños anteriores y arma los nuevos. Si la nueva tiene otro ancho, hay que
  corregir en `index.html` el `srcset` (y el preload, si es la Key Lime), el
  `width` y el `height` de esa foto. El encuadre de cada una se ajusta con
  `--pos` (escritorio) y `--pos-m` (celular) en su `style`.
- **La tienda** se genera: `python herramientas/generar_tienda.py` arma
  `tortas/index.html` y `antojos/index.html` desde `datos/catalogo.json`.
  No se editan a mano. Una foto nueva se prepara con
  `python herramientas/preparar_foto.py <archivo> <slug>` y se vuelve a
  generar. El brief para generar fotos con GPT está en
  `docs/fotos/brief-fotos.html`.
- **El pedido** (`comun/carrito.js`) se guarda en el navegador y se ve en
  «Mi pedido» desde cualquier página. Sin JavaScript, cada producto se pide
  con su propio enlace de WhatsApp.
- **Decoradas** (`decoradas/`) es la comanda: un paso por vez con Volver y
  Siguiente, sin «Lo charlamos»; lo especial va en «¿Algo más que tengamos
  que saber?». `/comanda/` redirige ahí. Sin JavaScript se ven los seis
  pasos juntos y el mensaje se escribe a mano.
- **Lo común** vive en `comun/`: `base.css` (tokens, cabecera y pie),
  `ticket.css`, `tienda.css`, `base.js`, `menu.js`, `pedido-mensaje.js`,
  `carrito.js` y `tienda.js`.
- `/tienda-v3/` se borró el 24/09/2026 (queda en el historial de git).
- Las páginas nuevas van en `noindex` hasta que las dueñas aprueben.

**Pruebas** (desde esta carpeta):

```bash
node --test "tests/**/*.test.mjs"
python -m pytest tests -q -p no:cacheprovider
```

**Para confirmar con las dueñas:** los tamaños de las tortas de la casa (hoy
se piden por cantidad); cuántos shots trae cada caja y cómo se
vende cada antojo; los precios y la plataforma de pago; que la Marquise es el
«Brownie con dulce de leche y frutos rojos» de su lista; que la Torta Matilda
es la de chocolate de la foto; «Sin conservantes ni aditivos» (convive con la
Choco Oreo); las porciones que se superponen (Mediana 15 a 25, Grande 20 a
30); y quién atiende los pedidos entre Anto y Nadia.

**Para probar en un teléfono real:** el envío sin JavaScript (un formulario
GET manda los espacios como `+`), el selector de fecha en iPhone y el
navegador interno de Instagram.

**Para después:** el logo de la cabecera se pierde; la idea es una animación
en bucle «SENTIDA» → «Pastelería» → «Lo soñás, lo creamos».

Falsos positivos conocidos del detector de Impeccable: `cramped-padding` (el
motor estático no lee `padding-block` ni `clamp()`),
`clipped-overflow-container` en `html`/`body` (es el `overflow-x:clip` que
evita el desborde) y `overused-font` / `cream-palette` (Montserrat y `#FEFAF8`
son de marca).

La home anterior (v1) quedó en `home-v1.html`, en `noindex`, como referencia.
