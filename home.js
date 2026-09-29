/* SENTIDA · home: las fotos del hero se turnan dentro del círculo.
   La primera es la de siempre y carga ya. Las demás esperan en un <template>
   y entran de a una, un turno antes de mostrarse: así no se bajan las ocho
   juntas (unos 850 KB en el celular) y cada una tiene 5 s para llegar.
   Con movimiento reducido (sin «mov») queda solo la primera. El botón pausa
   y sigue (WCAG 2.2.2), con el mismo dibujo que la pausa de la cinta. */
(function () {
  'use strict';
  var caja = document.querySelector('[data-hero-fotos]');
  var mas = caja && caja.querySelector('template[data-hero-mas]');
  var boton = caja && caja.querySelector('.hero-pausa');
  if (!mas || !boton || !document.documentElement.classList.contains('mov')) return;
  var PASO = 5000;
  var fotos = [], cola = [], actual = 0, reloj = 0, pausada = false;

  function lista(f) { return f.complete && f.naturalWidth > 0; }
  function mostrar(i) {
    fotos[actual].classList.remove('visible');
    fotos[actual].setAttribute('aria-hidden', 'true');
    fotos[i].classList.add('visible');
    fotos[i].removeAttribute('aria-hidden');
    actual = i;
  }
  // Pone en la página la próxima foto del <template>: el navegador la baja recién ahí.
  function traer() {
    var f = cola.shift();
    if (!f) return;
    f.setAttribute('aria-hidden', 'true');
    caja.insertBefore(f, boton);
    fotos.push(f);
  }
  function siguiente() {
    var i = (actual + 1) % fotos.length;
    if (!lista(fotos[i])) return;      // si todavía no llegó, espera a la vuelta que viene
    mostrar(i);
    traer();
  }
  function andar() {
    clearInterval(reloj);
    if (!pausada) reloj = setInterval(siguiente, PASO);
  }
  function poner(p) {
    pausada = p;
    caja.classList.toggle('pausada', p);
    boton.setAttribute('aria-pressed', p ? 'true' : 'false');
    boton.setAttribute('aria-label', p ? 'Seguir con las fotos' : 'Pausar las fotos');
    andar();
  }

  function empezar() {
    cola = Array.prototype.slice.call(mas.content.cloneNode(true).querySelectorAll('img'));
    mas.remove();
    fotos = Array.prototype.slice.call(caja.querySelectorAll('img'));
    traer();
    boton.hidden = false;
    boton.addEventListener('click', function () { poner(!pausada); });
    andar();
  }
  if (document.readyState === 'complete') empezar();
  else window.addEventListener('load', empezar);
})();
