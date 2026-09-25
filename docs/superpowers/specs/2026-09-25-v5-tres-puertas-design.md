# v5: la home con tres puertas

25/09/2026. Parte del audio de la clienta y de la charla con el usuario.

## Qué pidió la clienta

Que al entrar se elija primero qué se busca: una torta a medida, una torta de la
casa o pastelería. Hoy el sitio lleva a todos hacia el armado de la decorada, y
el que solo quería un cheesecake se pierde.

## Decisiones

- **Menú:** Nuestras tortas · Armá tu torta · Pastelería · Nosotras. «Decoradas»
  pasa a llamarse «Armá tu torta» y «Antojos», «Pastelería».
- **Direcciones:** `/arma-tu-torta/`, `/pasteleria/` y `/nosotras/`. Las viejas
  (`/decoradas/`, `/antojos/`, `/comanda/`) redirigen y conservan `?ref=` y el `#`.
- **Home:** el lema, las tres puertas a sangre con foto (opción A, «tríptico»,
  de los bocetos), una línea que lleva a Nosotras, «Cómo pedir» en tres pasos y
  el pie. Nada que repita lo que ya está en cada sección.
- **Nosotras** pasa a su propia página, con lo que antes estaba en la home:
  quiénes son, el manifiesto y «Hecho a mano».
- **Armá tu torta termina en WhatsApp.** Es fijo, aun cuando la tienda pase a
  PepperLabs.
- El Día de la Madre ya no está en la home.

## Fuera de esta versión

- **Armá tu torta:** los dos rellenos salen de una sola lista y se pueden
  repetir. Falta que la clienta confirme la lista: la «crema de avarilloche», los
  agregados del dulce de leche y los adicionales.
- **Pastelería:** todo se vende por media docena o docena, nunca menos. Falta
  aplicarlo al carrito y saber si los shots se mezclan en una caja.
- **Logo nuevo:** entra cuando esté en vector. En el nav y el header va sin
  «PASTELERÍA». La curva de la S en celeste va a ser el rasgo gráfico del sitio.
- **La tienda sobre PepperLabs:** es un proyecto aparte (ver el handoff para Pepper).

## Pruebas

`python -m pytest tests`: la home (tres puertas en la primera pantalla, nada
repetido), Nosotras, las redirecciones, y las reglas de todo el sitio (desborde,
texto chico, celeste en texto, itálicas, contraste AA, sin JavaScript) en las
cinco páginas.
