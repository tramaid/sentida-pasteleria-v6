/* SENTIDA · la comanda — núcleo.
   Lee el formulario, pinta los tickets, escribe el mensaje y lo manda.
   Sin este archivo la página funciona igual: el mensaje se escribe a mano. */
(function () {
  'use strict';
  var M = window.ComandaMensaje, S = window.Sentida;
  var armado = document.getElementById('armado');
  var envio = document.getElementById('envio');
  var mensaje = document.getElementById('mensaje');
  var anuncio = document.getElementById('anuncio');
  var reiniciarBtn = document.getElementById('reiniciar');
  var reescribirBtn = document.getElementById('reescribir');
  var campoAdemas = document.getElementById('campo-ademas');
  if (!M || !S || !armado || !envio || !mensaje) return;

  var NUMERO = envio.getAttribute('data-numero');
  var oyentes = [];
  var anterior = {};
  var editado = false;
  var ultimo = {estado: null, lineas: []};
  // Campos de texto -> la línea del ticket que les corresponde.
  var CLAVES = {fecha: 'fecha', idea: 'decoracion', 'nombre-torta': 'nombre', numero: 'numero', ademas: 'ademas'};

  function marcado(nombre) {
    var el = armado.querySelector('[name="' + nombre + '"]:checked');
    return el ? el.value : '';
  }

  function leer() {
    var f = armado.elements;
    return {
      fecha: f.fecha.value,
      sinFecha: f['sin-fecha'].checked,
      tamano: marcado('tamano'),
      bizcochuelo: marcado('bizcochuelo'),
      relleno: marcado('relleno'),
      agregados: Array.prototype.map.call(armado.querySelectorAll('[name="agregado"]:checked'),
        function (c) { return c.value; }),
      relleno2: marcado('relleno2'),
      idea: f.idea.value,
      referencia: marcado('referencia'),
      nombreTorta: f['nombre-torta'].value,
      numero: f.numero.value,
      ademas: f.ademas ? f.ademas.value : ''
    };
  }

  function escribir(e) {
    e = e || {};
    var f = armado.elements;
    f.fecha.value = e.fecha || '';
    f['sin-fecha'].checked = !!e.sinFecha;
    ['tamano', 'bizcochuelo', 'relleno', 'relleno2', 'referencia'].forEach(function (n) {
      armado.querySelectorAll('[name="' + n + '"]').forEach(function (r) { r.checked = r.value === (e[n] || ''); });
    });
    armado.querySelectorAll('[name="agregado"]').forEach(function (c) {
      c.checked = (e.agregados || []).indexOf(c.value) >= 0;
    });
    f.idea.value = e.idea || '';
    f['nombre-torta'].value = e.nombreTorta || '';
    f.numero.value = e.numero || '';
    if (f.ademas) f.ademas.value = e.ademas || '';
    render({silencioso: true, motivo: 'restaurado'});
  }

  function pintarTicket(dl, ls, nueva) {
    dl.textContent = '';
    ls.forEach(function (l) {
      var fila = document.createElement('div');
      fila.setAttribute('data-clave', l.clave);
      if (nueva && nueva.clave === l.clave) fila.className = 'nueva';
      var dt = document.createElement('dt');
      // Cada línea lleva a su paso: pasos.js decide si ya se puede ir.
      var ir = document.createElement('button');
      ir.type = 'button';
      ir.className = 'ticket-ir';
      ir.textContent = l.etiqueta;
      ir.setAttribute('aria-label', 'Cambiar: ' + l.etiqueta);
      dt.appendChild(ir);
      var dd = document.createElement('dd');
      dd.textContent = l.vacio ? '…' : l.valor;
      if (l.vacio) dd.className = 'vacio';
      fila.appendChild(dt);
      fila.appendChild(dd);
      dl.appendChild(fila);
    });
  }

  function render(opts) {
    opts = opts || {};
    var e = leer();
    var ls = M.lineas(e);
    var nueva = null;
    if (opts.anunciar) {
      ls.forEach(function (l) { if (l.clave === opts.anunciar && !l.vacio) nueva = l; });
    } else if (!opts.silencioso) {
      ls.forEach(function (l) { if (!l.vacio && anterior[l.clave] !== l.valor) nueva = l; });
    }
    anterior = {};
    ls.forEach(function (l) { anterior[l.clave] = l.vacio ? null : l.valor; });

    document.querySelectorAll('[data-ticket] .ticket-lineas').forEach(function (dl) { pintarTicket(dl, ls, nueva); });
    if (!editado) mensaje.value = M.texto(e);
    if (nueva && anuncio) anuncio.textContent = nueva.etiqueta + ': ' + nueva.valor;
    if (reiniciarBtn) reiniciarBtn.hidden = !editado && !ls.some(function (l) { return !l.vacio; });

    ultimo = {estado: e, lineas: ls};
    var motivo = opts.motivo || 'cambio';
    oyentes.forEach(function (fn) { fn(e, nueva, ls, motivo); });
  }

  function reiniciar() {
    armado.reset();
    editado = false;
    if (reescribirBtn) reescribirBtn.hidden = true;
    anterior = {};
    render({silencioso: true, motivo: 'reinicio'});
  }

  function urlWhatsApp() { return M.url(NUMERO, mensaje.value); }

  // La fecha no puede ser anterior a hoy.
  armado.elements.fecha.min = S.hoyISO();
  // «¿Algo más?» solo sirve con JavaScript: sin él, el mensaje se escribe a mano.
  if (campoAdemas) campoAdemas.hidden = false;

  // Los campos del armado avisan por el documento: «¿Algo más?» está en el
  // cierre, fuera del <form>, pero le pertenece (form="armado").
  function delArmado(t) { return !!t && t.form === armado; }
  document.addEventListener('change', function (ev) {
    var t = ev.target;
    if (!delArmado(t)) return;
    if (t.name === 'sin-fecha' && t.checked) armado.elements.fecha.value = '';
    if (t.name === 'fecha' && t.value) armado.elements['sin-fecha'].checked = false;
    // Al terminar de escribir (change), se imprime y se anuncia una sola vez.
    if (t.type === 'text' || t.tagName === 'TEXTAREA') render({anunciar: CLAVES[t.name]});
    else render();
  });
  document.addEventListener('input', function (ev) {
    var t = ev.target;
    // Mientras se escribe: ticket y mensaje al día, sin animación ni anuncio por letra.
    if (delArmado(t) && (t.type === 'text' || t.tagName === 'TEXTAREA')) render({silencioso: true});
  });
  // Enter en un campo de texto no recarga la página: avanza un paso.
  armado.addEventListener('submit', function (ev) {
    ev.preventDefault();
    if (window.ComandaPasos) window.ComandaPasos.siguiente();
    else document.getElementById('cierre').scrollIntoView();
  });

  mensaje.addEventListener('input', function () {
    editado = true;
    if (reescribirBtn) reescribirBtn.hidden = false;
    if (reiniciarBtn) reiniciarBtn.hidden = false;
  });
  if (reescribirBtn) reescribirBtn.addEventListener('click', function () {
    editado = false;
    reescribirBtn.hidden = true;
    render({silencioso: true});
    mensaje.focus();
  });
  if (reiniciarBtn) reiniciarBtn.addEventListener('click', function () {
    reiniciar();
    armado.elements.fecha.focus();
  });

  envio.addEventListener('submit', function (ev) {
    ev.preventDefault();
    var destino = urlWhatsApp();
    var w = window.open(destino, '_blank');
    if (w) { try { w.opener = null; } catch (err) { /* otra ventana */ } }
    else window.location.href = destino;  // navegador que bloquea pestañas nuevas
  });

  window.Comanda = {
    leer: leer,
    escribir: escribir,
    render: render,
    reiniciar: reiniciar,
    urlWhatsApp: urlWhatsApp,
    editado: function () { return editado; },
    alCambiar: function (fn) {
      oyentes.push(fn);
      fn(ultimo.estado, null, ultimo.lineas, 'inicial');
    }
  };
  render({silencioso: true, motivo: 'inicial'});
})();
