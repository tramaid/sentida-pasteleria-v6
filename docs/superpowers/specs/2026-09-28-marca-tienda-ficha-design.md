# Marca nueva, la tienda con la cara de la v6 y la ficha de producto

Fecha: 28/09/2026 · Repos: `sentida-site` (rama `v6`) y `sentida-tienda` (`main`, más la rama `preview-render` para Render).

## Para qué

Las dueñas aprobaron la cara de la v6 del sitio y ahora hay un logo nuevo. El objetivo es:

- que el sitio y la tienda usen la misma marca;
- que la tienda Flask (`sentida-tienda`), que va a reemplazar a las páginas estáticas de Nuestras tortas y Pastelería, se vea como la v6;
- que la tienda tenga una ficha de producto donde se elige el sabor y la medida.

Se considera cumplido cuando:

- el sitio y la tienda comparten logo, colores y tipografías sin copias que puedan quedar desparejas sin que un test lo marque;
- la tienda entra directo al catálogo y se ve como la v6;
- en la ficha se elige sabor y medida, y el pedido lleva la combinación elegida;
- el calendario de retiro respeta la anticipación de cada categoría.

## Decisiones tomadas (27 y 28/09)

- **Logo:** los tres SVG del usuario en `E:\E descargas\SENTIDA-sitio-web\`: `solo-sentida-nuevo.svg`, `logo-sentida-nuevo-01.svg` (con PASTELERÍA) y `SELLO-SENTIDA-NUEVO-01.svg`.
- **Colores:** siguen al logo. Marrón `#4E2C1E` (antes `#402D21`), celeste de filetes `#7EAFD6` (antes `#8FB1C9`) y blanco crema `#FCF9F2` (antes `#FEFAF8`).
- **Hero de la home** (lo pidieron las chicas el 28/09): una sola foto, la de la torta, con el sello. Se saca el círculo chico de la masa de galletas; en el celular, el círculo grande va centrado. Ya está hecho en la rama `v6`.
- **Tipografías:** los títulos pasan de Erode a **Playfair** (Google Fonts, OFL, variable). El texto sigue en **Montserrat**. La comparación está en `E:\E descargas\SENTIDA-sitio-web\comparacion-tipografias\index.html`.
- **La ficha** toma la estructura de la ficha de CARVAN del usuario (`E:\CARVAN\carvan-tienda\templates\publico\_ficha_*`), que ya vive en la tienda: tocar la tarjeta abre un popup sobre la grilla, hay una página propia por producto y una galería ampliable.
- **La tienda no tiene home:** `/` va a `/catalogo`.
- **El menú del sitio no cambia todavía:** Nuestras tortas y Pastelería siguen yendo a las páginas estáticas hasta el deploy real. La tienda se muestra con su link aparte (https://sentida-tienda.onrender.com).
- **Precios:** quedan sin definir («A consultar»). Los cargan las chicas desde el panel.
- **Pago online:** lo activan las chicas cuando lo tengan (Mercado Pago o similar). La tienda ya trae el interruptor `pago_online_habilitado`; este trabajo no lo toca.
- **Anticipación** (la pasó Nadia): 48 h las tortas. En pastelería, mínimo 4 o 5 días, a veces una semana, según el trabajo.
- **Tamaño de las tortas:** 20 a 22 cm en general, más la opción de consultar por uno más grande.
- **Pastelería** se vende por ½ docena o por docena, y la cantidad cuenta cajas.
- **Sabores y descripciones:** no los hay todavía. Los escribo yo a partir de las fotos y en el tono de las chicas (voseo, «nosotras», frases cortas), y quedan marcados como provisorios. No se inventan sabores que no se vean en las fotos.

## Parte 1. La marca compartida

`sentida-site` es la fuente de la marca y `sentida-tienda` guarda una copia sincronizada.

**En `sentida-site`:**

- `comun/marca.css` (nuevo) tiene:
  - los `@font-face` de Playfair y Montserrat, con sus respaldos de métrica ajustada;
  - todos los tokens de color de `:root`.

  `base.css` deja de declararlos y se queda con los componentes. Todas las páginas, las escritas a mano y las generadas, cargan `marca.css` antes de `base.css`.
- `assets/marca/` (nuevo) tiene:
  - `logo.svg`: «Sentida» sin PASTELERÍA, para la cabecera;
  - `logo-pasteleria.svg`: con PASTELERÍA, para el hero de la home;
  - `logo-claro.svg`: el mismo logo en crema, para el pie marrón;
  - `sello.svg`: reemplaza a `SENTIDASELLO.svg` en el hero, el cierre y el pie;
  - `favicon.svg`: la S del sello.

  Los SVG se limpian: sin comentarios de Illustrator, con `viewBox` y con el color en `fill`.
- **Fuentes:** se borran `erode-400.woff2` y `erode-500.woff2`. Playfair entra como un solo archivo variable, recortado a latín y latín extendido.
- **Tokens:** se revisa el contraste de todos los pares texto sobre fondo con los colores nuevos. El mínimo es 4,5:1 para texto chico y 3:1 para texto grande. El celeste de filetes sigue sin usarse nunca en texto.
- **Qué cambia a la vista:**
  - La cabecera muestra el logo dibujado en lugar de «SENTIDA.» en texto. El enlace mantiene el nombre accesible «SENTIDA Pastelería, inicio».
  - En el hero de la home, el «SENTIDA» grande pasa a ser `logo-pasteleria.svg` dentro del `h1`, con `alt="Sentida"`, así que el título sigue leyéndose «Sentida. Lo soñás, lo creamos.».
  - Todos los títulos van en Playfair.
  - El pie usa el logo claro y el sello nuevo.
- `herramientas/generar_tienda.py` arma la cabecera y el pie con el logo, y enlaza `marca.css` en las páginas que genera.

**En `sentida-tienda`:**

- **Comando nuevo:** `python -m flask --app app sincronizar-marca <ruta a sentida-site>` copia `comun/marca.css` a `static/marca.css`, y las fuentes y los logos a `static/fuentes/` y `static/logos/`. Borra lo que ya no está en el sitio (Erode, el logo viejo).
- **Test nuevo:** compara byte por byte la copia con el sitio. Si `../sentida-site` no existe (por ejemplo, en Render), el test se saltea.

## Parte 2. La tienda con la cara de la v6

- **Sin home:** `/` redirige (302) a `/catalogo`. Se borran `templates/themes/sentida/home.html`, sus imágenes (`static/img/hero.webp`, `idea.webp`, `tortas-decoradas.webp`) y los banners del home en la parte pública. El panel de banners queda como está, sin uso.
- **Cabecera:** el mismo marcado que el sitio (`.cab`):
  - el logo lleva a `SITIO_URL`;
  - el menú es Nuestras tortas (`/catalogo?cat=tortas`) · Armá tu torta (sitio) · Pastelería (`/catalogo?cat=pasteleria`) · Nosotras (sitio);
  - a la derecha, «Ingresar» (o el nombre del cliente) y «Mi pedido» con su contador;
  - en el celular, el menú desplegable con los mismos enlaces más Contacto y «Volver a SENTIDA»;
  - se sacan «Catálogo», «Decoradas» e «Inicio de la tienda».
- **La cinta celeste:** el mismo marcado y el mismo comportamiento que el sitio, con el botón de pausa y la pausa recordada.
- **El pie:** el de la v6 con el logo claro y el sello nuevo. Mantiene WhatsApp, Instagram, Contacto, «Mis pedidos» o «Ingresar», y «Volver a SENTIDA».
- **Catálogo:**
  - Arriba, la cabecera de la v6: la etiqueta con línea («Las de la casa» o «Para regalar y compartir»; sin categoría, «Todo lo que hacemos») y el título en Playfair («Nuestras tortas.», «Pastelería.» o «Catálogo.»), con la bajada del catálogo del sitio.
  - Las tarjetas son las `.producto` de la v6: foto 4:4,5, categoría, nombre, descripción corta, «Precio a consultar» (o el precio, si lo hay) y el «+» sobre la foto. Si el producto obliga a elegir un sabor, el «+» abre la ficha. Si no, suma la presentación que viene marcada.
  - El ticket «Tu pedido» va al costado y en el celular pasa a ser la tira de abajo.
  - La búsqueda y el orden se quedan, en una línea discreta. Se sacan «Solo ofertas» y el cambio grilla/lista; el código de las ofertas sigue en el panel.
- **Las demás páginas** (carrito, reserva, confirmación, ingresar, registro, mis pedidos, contacto) usan los componentes de la v6: títulos en Playfair, `.eti`, `.btn-1` y `.btn-2`, campos como `.cf` y el ticket de papel. El comportamiento no cambia.
- **Estilos:** hoy el tema vive en un `<style>` dentro de `base.html` (545 líneas). Pasa a `static/tema.css`, que carga después de `static/marca.css`. El `<style>` del template desaparece.

## Parte 3. La ficha y lo que se elige

**Datos**

- Cada combinación es una presentación (`productos`) del mismo ítem (`catalogo_items`), con su SKU, su precio (NULL = «A consultar») y su disponibilidad. Hoy la tienda ya funciona así.
- Se suman dos columnas a `productos`: `sabor TEXT` y `medida TEXT`, las dos pueden quedar vacías. `etiqueta` se sigue llenando con el texto completo («De frutillas · ½ docena»), así `pedidos_items.etiqueta` congela la combinación sin cambios.
- `categorias` suma `anticipacion_horas INTEGER`: 48 para Tortas y 96 para Pastelería (4 días). La nota «a veces hasta una semana, según el trabajo» va en el sello y no en la regla.
- En `sentida-site/datos/catalogo.json` se amplía el formato:
  - `secciones.<clave>.medidas`: una lista de `{"nombre", "a_consultar"?}`. Tortas: «20 a 22 cm» y «Más grande» (a consultar). Pastelería: «½ docena» y «Docena».
  - `productos[].variantes`: ya existe; son los sabores, con su foto.
  - `productos[].descripcion_larga`.

  `generar_tienda.py` ignora estos campos.
- `importar-catalogo` arma una presentación por cada combinación sabor × medida. Es idempotente, por slug del ítem más sabor y medida. Al crear, deja `publicado` como corresponde y el precio en NULL. No pisa lo que el panel haya cambiado.

**La ficha** (el mismo parcial para el popup y para la página propia)

- **Galería:** foto grande que se amplía y miniaturas. Al elegir un sabor, la foto grande pasa a la de ese sabor.
- **Categoría, nombre en Playfair y descripción corta y larga.** Las descripciones provisorias llevan una marca en el panel («Texto provisorio, revisalo»), no en la tienda.
- **«Elegí el sabor»:** radios con miniatura. Solo aparece si el ítem tiene sabores. Hoy: Shots (con flores, de frutillas, de maracuyá) y Cuadraditos dulces (carrot cake).
- **La medida:** radios. En tortas, «20 a 22 cm» viene marcada, y «Más grande» dice «Tamaño y precio a consultar por WhatsApp». En pastelería viene marcada «½ docena».
- **Cantidad** (cuenta tortas o cajas), **«Agregar a mi pedido»** sin salir, y después el aviso «Ver mi pedido».
- **Combinaciones:** el script elige la presentación que coincide con el sabor y la medida marcados. Si una combinación no está disponible, esa opción queda deshabilitada y lo dice.
- **Tres sellos:**
  - **Anticipación:** «Pedila con 48 h» o «De 4 a 7 días, según el trabajo».
  - **Retiro y pago:** salen de `txt_envio` y `txt_pago`, como hoy.
  - **Precio:** «A consultar: te lo confirmamos por WhatsApp» mientras no haya precio cargado.
- **Sin JavaScript:** en vez de los dos grupos, una sola lista de radios con todas las combinaciones, que manda el formulario al carrito como hoy.

**Reserva**

- El primer día de retiro que se ofrece es `ahora + máx(anticipacion_horas de las categorías del pedido)`, redondeado al día siguiente con franjas.
- `DIAS_A_OFRECER` pasa de 7 a 14, para que con 4 días de anticipación siga habiendo una semana para elegir.
- El texto de la reserva explica por qué los primeros días no aparecen.

## Fuera de alcance

- Los precios reales y el pago online: los activan las chicas desde el panel.
- El horario de retiro real: `horarios.py` todavía trae el de CARVAN y queda pendiente de que lo pasen Anto y Nadia.
- El deploy de producción y el cambio del menú del sitio hacia la tienda.
- Armá tu torta dentro de la tienda.

## Pruebas

**Sitio:**

- Ninguna página referencia Erode.
- Ningún color queda fuera de `marca.css`, salvo las máscaras.
- La cabecera y el pie usan el logo, y el `h1` de la home se lee «Sentida».
- Los tests actuales se actualizan donde buscaban «SENTIDA.» en texto.

**Tienda:**

- La copia de la marca es igual a la del sitio.
- `/` redirige a `/catalogo`.
- La cabecera, la cinta y el pie son los de la v6.
- Elegir sabor y medida agrega la combinación correcta, y la línea del pedido dice «Shots — De frutillas · ½ docena».
- Una combinación no disponible queda deshabilitada.
- «Más grande» entra a cotizar.
- Sin JavaScript se puede pedir igual.
- El popup y la página propia muestran lo mismo.
- El calendario no ofrece días antes de la anticipación.
- El importador es idempotente con las combinaciones.

**Capturas:** cada página de la tienda y las del sitio que cambian, en 1440 y 390.

**Preview:** después de pasar `main` a `preview-render`, rehacer la semilla y revisar en vivo en Render.
