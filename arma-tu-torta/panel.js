/* SENTIDA · la comanda — lo que acompaña al armado.
   Escritorio: la foto del panel cambia según el paso.
   Celular: mientras la comanda está en pantalla, la cabecera se esconde y
   arriba queda la tira del ticket; al tocarla se abre la comanda entera. */
(function () {
  'use strict';
  var C = window.Comanda, P = window.ComandaPasos;
  var doc = document.documentElement;
  var comanda = document.getElementById('comanda');
  var foto = document.querySelector('.panel-foto');
  var pie = document.getElementById('panel-pie');
  var tira = document.getElementById('tira');
  var tiraLinea = document.getElementById('tira-linea');
  var ver = document.querySelector('.tira-ver');
  var dialogo = document.getElementById('comanda-dialogo');
  var cerrar = document.getElementById('dialogo-cerrar');
  var mensaje = document.getElementById('mensaje');
  if (!C || !comanda) return;

  // Paso actual -> foto y pie del panel.
  if (foto && P) {
    P.alCambiar(function (n) {
      foto.setAttribute('data-activo', n);
      var img = foto.querySelector('[data-foto="' + n + '"]');
      if (img && pie) pie.textContent = 'Hecha por nosotras · ' + img.getAttribute('data-pie');
    });
  }

  // Celular: la tira reemplaza a la cabecera mientras se arma.
  if (tira && 'IntersectionObserver' in window) {
    tira.hidden = false;
    new IntersectionObserver(function (es) {
      es.forEach(function (e) { doc.classList.toggle('en-comanda', e.isIntersecting); });
    }, {rootMargin: '-45% 0px -45% 0px'}).observe(comanda);
  }

  var tiraEt = tiraLinea && tiraLinea.querySelector('.tira-et');
  var tiraVal = tiraLinea && tiraLinea.querySelector('.tira-val');
  C.alCambiar(function (estado, nueva, lineas) {
    if (!tiraEt || !tiraVal) return;
    var hechas = (lineas || []).filter(function (l) { return !l.vacio; });
    var l = nueva || hechas[hechas.length - 1];
    tiraEt.textContent = l ? l.etiqueta : 'Paso 1';
    tiraVal.textContent = l ? l.valor : 'Empezá por la fecha';
  });

  // La comanda entera en un diálogo nativo: foco atrapado y Escape.
  if (dialogo && ver && typeof dialogo.showModal === 'function') {
    var focoAlCerrar = null;
    ver.addEventListener('click', function () {
      // Si el mensaje se editó a mano, el diálogo no manda: avisa y lleva a revisarlo.
      dialogo.classList.toggle('editado', !!(C.editado && C.editado()));
      dialogo.showModal();
      ver.setAttribute('aria-expanded', 'true');
    });
    dialogo.addEventListener('close', function () {
      ver.setAttribute('aria-expanded', 'false');
      (focoAlCerrar || ver).focus();
      focoAlCerrar = null;
    });
    // «Revisar mi mensaje»: se cierra el diálogo y se va al cierre, con el foco en el mensaje.
    var revisar = dialogo.querySelector('.dialogo-revisar');
    if (revisar) revisar.addEventListener('click', function (ev) {
      ev.preventDefault();
      // Se hace todo ya, sin esperar el evento «close» (que llega después):
      // el foco termina en el mensaje, no en la tira.
      if (P) P.ir(7, {foco: false});
      focoAlCerrar = mensaje;
      dialogo.close();
      if (mensaje) mensaje.focus();
    });
    if (cerrar) cerrar.addEventListener('click', function () { dialogo.close(); });
    dialogo.addEventListener('click', function (ev) { if (ev.target === dialogo) dialogo.close(); });
  }
})();
