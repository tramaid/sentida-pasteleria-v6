/* SENTIDA · la cabecera: el menú del celular y la pausa de la cinta.
   El menú es un <details>: funciona solo. Acá se cierra al elegir un
   enlace, con Escape, al tocar afuera o cuando el foco se va a otra parte.
   La cinta se mueve sola: su botón la pausa y la página lo recuerda. */
(function () {
  'use strict';
  var menu = document.querySelector('.menu');
  if (!menu) return;
  var cerrar = function () { menu.open = false; };
  menu.addEventListener('click', function (ev) { if (ev.target.closest('nav a')) cerrar(); });
  menu.addEventListener('focusout', function (ev) {
    if (menu.open && ev.relatedTarget && !menu.contains(ev.relatedTarget)) cerrar();
  });
  document.addEventListener('keydown', function (ev) {
    if (ev.key === 'Escape' && menu.open) { cerrar(); menu.querySelector('summary').focus(); }
  });
  document.addEventListener('click', function (ev) { if (menu.open && !menu.contains(ev.target)) cerrar(); });
})();

(function () {
  'use strict';
  var cinta = document.querySelector('.marquesina');
  var boton = cinta && cinta.querySelector('.marquesina-pausa');
  if (!boton) return;
  var CLAVE = 'sentida-cinta-pausada';
  function poner(pausada) {
    cinta.classList.toggle('pausada', pausada);
    boton.setAttribute('aria-pressed', pausada ? 'true' : 'false');
    boton.setAttribute('aria-label', pausada ? 'Mover la cinta' : 'Pausar la cinta');
  }
  var guardada = false;
  try { guardada = localStorage.getItem(CLAVE) === '1'; } catch (err) { /* bloqueado */ }
  poner(guardada);
  boton.addEventListener('click', function () {
    var pausada = !cinta.classList.contains('pausada');
    poner(pausada);
    try { localStorage.setItem(CLAVE, pausada ? '1' : '0'); } catch (err) { /* bloqueado */ }
  });
})();
