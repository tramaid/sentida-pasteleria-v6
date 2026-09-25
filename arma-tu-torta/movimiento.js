/* SENTIDA · la comanda — el gesto de entrada.
   Al empezar, la comanda de la portada viaja a su lugar (el panel en
   escritorio, la tira en celular) y se muestra el paso donde quedaste. */
(function () {
  'use strict';
  var doc = document.documentElement;
  var mm = function (q) { return window.matchMedia ? window.matchMedia(q) : {matches: false}; };
  var quieto = mm('(prefers-reduced-motion: reduce)');
  var celular = mm('(max-width: 899px)');
  function actualizarMov() { doc.classList.toggle('mov', !quieto.matches); }
  if (quieto.addEventListener) quieto.addEventListener('change', actualizarMov);
  actualizarMov();

  var empezar = document.getElementById('empezar');
  var origen = document.querySelector('.ticket-portada .papel');
  var comanda = document.getElementById('comanda');
  var fecha = document.getElementById('fecha');
  if (!empezar || !origen || !comanda) return;

  empezar.addEventListener('click', function (ev) {
    ev.preventDefault();
    var desde = origen.getBoundingClientRect();
    var P = window.ComandaPasos;
    if (P) P.ir(P.actual() || 1);
    else {
      comanda.scrollIntoView({behavior: 'instant', block: 'start'});
      if (fecha) fecha.focus({preventScroll: true});
    }
    if (celular.matches) doc.classList.add('en-comanda');
    if (!doc.classList.contains('mov')) return;
    var destino = celular.matches ? document.getElementById('tira') : document.querySelector('.panel .ticket');
    if (!destino || !destino.animate) return;
    destino.getAnimations().forEach(function (a) { a.cancel(); });
    var hasta = destino.getBoundingClientRect();
    if (!hasta.width) return;
    var dx = desde.left - hasta.left, dy = desde.top - hasta.top, s = desde.width / hasta.width;
    destino.animate([
      {transform: 'translate(' + dx + 'px,' + dy + 'px) scale(' + s + ')', transformOrigin: 'top left'},
      {transform: 'none', transformOrigin: 'top left'}
    ], {duration: 700, easing: 'cubic-bezier(.16,1,.3,1)'});
  });
})();
