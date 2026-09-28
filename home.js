/* SENTIDA · home: las fotos del hero se turnan dentro del círculo.
   La primera es la de siempre y carga ya. Las demás esperan en un <template>
   hasta después del load (para no demorar la primera) y se funden cada 5 s.
   Con movimiento reducido (sin «mov») queda solo la primera. El botón pausa
   y sigue (WCAG 2.2.2), con el mismo dibujo que la pausa de la cinta. */
(function () {
  'use strict';
  var caja = document.querySelector('[data-hero-fotos]');
  var mas = caja && caja.querySelector('template[data-hero-mas]');
  var boton = caja && caja.querySelector('.hero-pausa');
  if (!mas || !boton || !document.documentElement.classList.contains('mov')) return;
  var PASO = 5000;
  var fotos = [], actual = 0, reloj = 0, pausada = false;

  function lista(f) { return f.complete && f.naturalWidth > 0; }
  function mostrar(i) {
    fotos[actual].classList.remove('visible');
    fotos[actual].setAttribute('aria-hidden', 'true');
    fotos[i].classList.add('visible');
    fotos[i].removeAttribute('aria-hidden');
    actual = i;
  }
  function siguiente() {
    var i = (actual + 1) % fotos.length;
    if (lista(fotos[i])) mostrar(i);   // si todavía no llegó, espera a la vuelta que viene
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
    var nuevas = mas.content.cloneNode(true).querySelectorAll('img');
    Array.prototype.forEach.call(nuevas, function (f) {
      f.setAttribute('aria-hidden', 'true');
      caja.insertBefore(f, boton);
    });
    mas.remove();
    fotos = Array.prototype.slice.call(caja.querySelectorAll('img'));
    boton.hidden = false;
    boton.addEventListener('click', function () { poner(!pausada); });
    andar();
  }
  if (document.readyState === 'complete') empezar();
  else window.addEventListener('load', empezar);
})();
