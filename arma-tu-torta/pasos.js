/* SENTIDA · la comanda — un paso por vez.
   Muestra una sola pregunta, con Volver y Siguiente al pie. Siguiente pide
   que el paso tenga respuesta y, si falta, lo dice; Enter en un campo
   avanza; el botón atrás del navegador vuelve un paso; cada línea del
   ticket lleva a su paso. Sin este archivo, los pasos se ven uno abajo del
   otro. */
(function () {
  'use strict';
  var C = window.Comanda, M = window.ComandaMensaje, B = window.ComandaBorrador;
  var comanda = document.getElementById('comanda');
  var armado = document.getElementById('armado');
  var nav = document.getElementById('pasos-nav');
  if (!C || !M || !comanda || !armado || !nav || !(window.history && history.pushState)) return;

  var CIERRE = 7;
  var hoy = window.Sentida ? window.Sentida.hoyISO() : '';
  // Línea del ticket -> paso donde se elige.
  var PASO_DE = {fecha: 1, tamano: 2, bizcochuelo: 3, relleno: 4, relleno2: 5,
                 decoracion: 6, nombre: 6, numero: 6, ademas: 7};
  var doc = document.documentElement;
  var pasos = {};
  document.querySelectorAll('.paso[data-n], #cierre[data-n]').forEach(function (p) {
    pasos[+p.getAttribute('data-n')] = p;
  });
  var volver = document.getElementById('volver');
  var siguiente = document.getElementById('siguiente');
  var siguienteT = document.getElementById('siguiente-t');
  var falta = document.getElementById('pasos-falta');
  var avance = document.getElementById('avance');
  var empezar = document.getElementById('empezar');
  var oyentes = [];
  var guardado = (B && B.paso()) || {actual: 1, alcanzado: 1};
  var actual = 0;
  var alcanzado = guardado.alcanzado;

  function titulo(n) { return pasos[n].querySelector('.paso-t, .cierre-t'); }

  function pasoDelHash() {
    if (location.hash === '#cierre') return CIERRE;
    var m = /^#paso-([1-6])$/.exec(location.hash);
    return m ? +m[1] : 0;
  }

  // Siguiente se ve inactivo mientras el paso no tenga lo que hace falta.
  function estadoSiguiente() {
    if (!actual) return;
    if (M.falta(actual, C.leer(), hoy)) siguiente.setAttribute('aria-disabled', 'true');
    else { siguiente.removeAttribute('aria-disabled'); falta.textContent = ''; }
  }

  // Solo se puede saltar a los pasos que ya se alcanzaron.
  function pintarTicket() {
    document.querySelectorAll('[data-ticket] [data-clave] .ticket-ir').forEach(function (b) {
      var n = PASO_DE[b.closest('[data-clave]').getAttribute('data-clave')];
      b.disabled = !n || n > alcanzado;
    });
  }

  function mostrar(n, direccion) {
    Object.keys(pasos).forEach(function (k) {
      pasos[k].hidden = +k !== n;
      pasos[k].classList.remove('entra', 'entra-atras');
    });
    if (direccion) {
      void pasos[n].offsetWidth;  // para que la animación arranque de nuevo
      pasos[n].classList.add(direccion > 0 ? 'entra' : 'entra-atras');
    }
    armado.hidden = n === CIERRE;  // en el cierre, el formulario vacío no ocupa lugar
    volver.hidden = n === 1;
    siguiente.hidden = n === CIERRE;
    siguienteT.textContent = n === 6 ? 'Ver mi comanda' : 'Siguiente';
    if (avance) avance.setAttribute('data-paso', n);
  }

  function ir(n, opts) {
    opts = opts || {};
    n = Math.min(Math.max(Math.floor(n) || 1, 1), CIERRE);
    var aviso = '';
    // Al cierre se llega con los pasos obligatorios completos.
    if (n === CIERRE) {
      var p = M.primerIncompleto(C.leer(), hoy);
      if (p < CIERRE) { n = p; aviso = M.falta(p, C.leer(), hoy); }
    }
    var anterior = actual;
    var direccion = actual && doc.classList.contains('mov') ? n - actual : 0;
    actual = n;
    alcanzado = Math.max(alcanzado, n);
    mostrar(n, direccion);
    falta.textContent = aviso;
    estadoSiguiente();
    if (!opts.sinHistoria) {
      var hash = n === CIERRE ? '#cierre' : '#paso-' + n;
      if (opts.reemplazar) history.replaceState({paso: n}, '', hash);
      else if (location.hash !== hash) {
        // La entrada que se deja (la portada, #comanda, ?ref=…) recuerda qué
        // paso mostraba, para que el botón atrás vuelva a ese paso.
        if (anterior && !(history.state && history.state.paso)) history.replaceState({paso: anterior}, '');
        history.pushState({paso: n}, '', hash);
      }
    }
    if (!opts.sinScroll) {
      var margen = parseFloat(getComputedStyle(doc).scrollPaddingTop) || 0;
      if (Math.abs(comanda.getBoundingClientRect().top - margen) > 2) {
        comanda.scrollIntoView({behavior: 'instant', block: 'start'});
      }
    }
    if (opts.foco !== false) titulo(n).focus({preventScroll: true});
    if (B) B.guardarPaso({actual: actual, alcanzado: alcanzado});
    pintarTicket();
    oyentes.forEach(function (fn) { fn(n); });
  }

  siguiente.addEventListener('click', function () {
    var f = M.falta(actual, C.leer(), hoy);
    if (!f) { ir(actual + 1); return; }
    falta.textContent = f;
    var primero = pasos[actual].querySelector('input');
    if (primero) primero.focus();
  });
  volver.addEventListener('click', function () { ir(actual - 1); });

  // Enter en un campo (no en un área de texto ni en una casilla) avanza.
  armado.addEventListener('keydown', function (ev) {
    var t = ev.target;
    if (ev.key !== 'Enter' || t.tagName !== 'INPUT' || t.type === 'checkbox') return;
    ev.preventDefault();
    siguiente.click();
  });

  // Cada línea del ticket lleva a su paso. Desde el diálogo del celular,
  // primero se cierra (y devuelve el foco a la tira) y después se va.
  document.addEventListener('click', function (ev) {
    var b = ev.target.closest('[data-ticket] .ticket-ir');
    if (!b || b.disabled) return;
    var n = PASO_DE[b.closest('[data-clave]').getAttribute('data-clave')];
    var dlg = b.closest('dialog');
    if (dlg && dlg.open) {
      dlg.addEventListener('close', function () { ir(n); }, {once: true});
      dlg.close();
    } else ir(n);
  });

  // El botón atrás (y adelante) del navegador.
  window.addEventListener('popstate', function (ev) {
    var n = (ev.state && ev.state.paso) || pasoDelHash();
    // Sin #paso en la dirección (la portada, #comanda), el navegador ya
    // devuelve el scroll a donde estaba: no se lo pisa.
    if (n) ir(n, {sinHistoria: true, sinScroll: !pasoDelHash()});
  });

  C.alCambiar(function (estado, nueva, lineas, motivo) {
    if (motivo === 'reinicio') {
      alcanzado = 1;
      if (empezar) empezar.textContent = 'Empezar mi comanda';
      ir(1, {foco: false});
      return;
    }
    estadoSiguiente();
    pintarTicket();
  });

  // Arranque: el paso del #hash, o el guardado, sin saltear pasos que falten.
  doc.classList.add('en-pasos');
  nav.hidden = false;
  if (avance) avance.hidden = false;
  var desdeHash = pasoDelHash();
  var inicial = Math.min(desdeHash || guardado.actual || 1, M.primerIncompleto(C.leer(), hoy));
  alcanzado = Math.max(alcanzado, inicial);
  if (empezar && alcanzado > 1) empezar.textContent = 'Seguir mi comanda';
  ir(inicial, {sinHistoria: !desdeHash, reemplazar: true, sinScroll: true, foco: false});

  window.ComandaPasos = {
    ir: ir,
    actual: function () { return actual; },
    siguiente: function () { siguiente.click(); },
    alCambiar: function (fn) { oyentes.push(fn); if (actual) fn(actual); }
  };
})();
