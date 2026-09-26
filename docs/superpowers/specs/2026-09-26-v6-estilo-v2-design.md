# v6: el estilo de sentida-v2 sobre el sitio que funciona

26/09/2026. A las dueñas les gustó la propuesta `tramaid/sentida-v2`
(https://tramaid.github.io/sentida-v2/), pero es una sola página de muestra: la
consulta se copia al portapapeles, no hay comanda, ni carrito, ni páginas por
sección, ni tests. La v5 (rama `v5`) tiene todo eso funcionando. La v6 le pone a
la v5 la cara de sentida-v2.

## Qué se toma de sentida-v2

- **Cabecera** con la marca en texto («SENTIDA» y un punto celeste) y, debajo,
  una **cinta celeste en marquesina** con el lema, «Pastelería artesanal»,
  «Tortas a medida» y «Hecho a mano».
- **Hero** en crema: una línea con filete celeste arriba («Pastelería
  artesanal»), SENTIDA grande espaciado, «Lo soñás, lo creamos.», una bajada, el
  botón oscuro y un enlace subrayado. A la derecha, **fotos en círculo** con un
  filete celeste claro, una chica encimada y el sello.
- **«Elegí por dónde empezar»**: tarjetas con la foto en círculo, número y
  categoría en versalitas, título en serif y flecha.
- **«Lo que más nos piden»**: productos con foto 4:4,5, botón redondo «+» sobre
  la foto, una línea de categoría y número, título en serif y «Precio a
  consultar».
- **«Todo empieza con una idea»** con tres pasos numerados, **«Somos Anto y
  Nadia»** con dos fotos encimadas, una **banda celeste** con una frase grande y
  el **cierre** centrado con el sello.
- **Pie** marrón con la marca en texto, columnas con etiqueta celeste y el sello.
- **Detalles del sistema:** los acentos de los títulos en celeste profundo (sin
  itálica), un nuevo celeste de filete `#8FB1C9`, títulos en serif de peso 400
  con el interletrado cerrado y botones con flecha que suben 3 px al pasar el
  mouse.

## Qué se conserva de la v5

La comanda de Armá tu torta, que termina en WhatsApp. El carrito compartido de
Nuestras tortas y Pastelería. «Mi pedido» en todas las páginas. Las direcciones
y las redirecciones. La página de Nosotras. El generador de la tienda desde
`datos/catalogo.json` y toda la suite de tests.

## Decisiones

1. **Tipografía de títulos: Erode, peso 400.** sentida-v2 usa una serif del
   sistema porque no tenía Erode, así que las dueñas la vieron en Palatino. La
   v6 vuelve a Erode, que es la tipografía de la marca, está alojada en el sitio
   y se ve igual en todas las máquinas. Antes de ejecutar se muestran las dos,
   una al lado de la otra, para confirmar.
2. **Puertas: son tres, las reales.** Armá tu torta, Nuestras tortas y
   Pastelería. Las cuatro categorías de sentida-v2 («De estación», «Pequeños
   regalos») no existen como secciones.
3. **Orden de la home: el de sentida-v2** (hero y después las puertas), que es
   lo que aprobaron. Las puertas quedan en la segunda pantalla. El hero tiene su
   botón «Armá tu torta» y el enlace «Ver lo que hacemos», que baja a las
   puertas.
4. **La marca en texto hasta que esté el logo nuevo.** «SENTIDA» con el punto
   celeste, sin «PASTELERÍA». Cuando esté el vector, se reemplaza.
5. **«Lo que más nos piden» sale del catálogo.** Los productos llevan
   `"destacado": true` en `datos/catalogo.json`, y el generador arma ese bloque
   en `index.html`. El «+» suma al mismo carrito que la tienda.
6. **El pedido se abre como panel lateral** (drawer), como en sentida-v2. Es el
   mismo `<dialog>` de hoy con otro estilo.
7. **Dónde se publica:** en un repo nuevo, `tramaid/sentida-pasteleria-v6`, con
   su propio GitHub Pages. No se pisa sentida-v2 ni la v5. Se confirma antes de
   subir.

## Reglas que no cambian

- Paleta: `#FEFAF8`, `#F8EADE`, `#CFB59E`, `#402D21`, `#6C4D38`, `#46627A` y
  `#DDE6ED`, este último solo como relleno. El nuevo `#8FB1C9` va solo en
  filetes, puntos y aros; nunca como texto que haya que leer.
- Nada de texto por debajo de 11 px: donde sentida-v2 usa 9 o 10 px, va a 11.
  Contraste AA.
- Sin itálicas: los `<em>` de sentida-v2 pasan a `<span class="acento">`.
- Voseo rioplatense, «Nosotras», PASTELERÍA con tilde, «Shots» (nunca
  «chupitos»). No se inventan precios: «Precio a consultar».
- La página se ve completa sin JavaScript, y el movimiento va solo bajo `.mov`:
  la marquesina queda quieta con «reducir movimiento».
- Las páginas de la tienda no se editan a mano: se cambia el generador.

## Fuera de esta versión

Los rellenos con una sola lista, la venta por media docena y docena, el logo en
vector y la tienda sobre PepperLabs.
