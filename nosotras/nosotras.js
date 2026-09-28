/* SENTIDA · Nosotras — las flechas de «Algunos de nuestros trabajos».
   Sin JS la tira se desliza igual (scroll con el dedo, la rueda o el teclado). */
(function () {
  'use strict';
  var tira = document.getElementById('trab-tira');
  if (!tira) return;
  var ant = document.querySelector('.trab-ant'), sig = document.querySelector('.trab-sig');
  function paso() { return Math.max(tira.clientWidth * 0.8, 240); }
  function estado() {
    var max = tira.scrollWidth - tira.clientWidth - 2;
    if (ant) ant.disabled = tira.scrollLeft <= 2;
    if (sig) sig.disabled = tira.scrollLeft >= max;
  }
  if (ant) ant.addEventListener('click', function () { tira.scrollBy({left: -paso()}); });
  if (sig) sig.addEventListener('click', function () { tira.scrollBy({left: paso()}); });
  tira.addEventListener('scroll', estado, {passive: true});
  window.addEventListener('resize', estado);
  estado();
})();
