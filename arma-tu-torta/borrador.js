/* SENTIDA · la comanda — borrador en el navegador.
   Lo elegido (y el paso en el que quedaste) se guarda en localStorage para
   que una recarga o una interrupción no lo borren. Nada sale del teléfono.
   También marca la referencia que llega desde la home (?ref=petalos). */
(function () {
  'use strict';
  var C = window.Comanda, S = window.Sentida;
  if (!C || !S) return;
  var CLAVE = 'sentida-comanda-v1';
  var REFERENCIAS = ['petalos', 'flores', 'letras', 'mensaje'];
  var paso = null;

  function hay() {
    try { return localStorage.getItem(CLAVE) !== null; } catch (err) { return false; }
  }
  function guardar(e) {
    try {
      var copia = {};
      Object.keys(e).forEach(function (k) { copia[k] = e[k]; });
      copia.paso = paso;
      localStorage.setItem(CLAVE, JSON.stringify(copia));
    } catch (err) { /* sin lugar o bloqueado */ }
  }
  function borrar() { try { localStorage.removeItem(CLAVE); } catch (err) { /* bloqueado */ } }
  function guardado() {
    try {
      var e = JSON.parse(localStorage.getItem(CLAVE) || 'null');
      return e && typeof e === 'object' && !Array.isArray(e) ? e : null;
    } catch (err) { return null; }
  }

  // Solo lo que tiene la forma esperada: un borrador raro no rompe la página.
  function sano(e) {
    var s = function (x) { return typeof x === 'string' ? x : ''; };
    return {
      fecha: s(e.fecha), sinFecha: e.sinFecha === true, tamano: s(e.tamano), bizcochuelo: s(e.bizcochuelo),
      relleno: s(e.relleno),
      agregados: Array.isArray(e.agregados) ? e.agregados.filter(function (a) { return typeof a === 'string'; }) : [],
      relleno2: s(e.relleno2), idea: s(e.idea), referencia: s(e.referencia),
      nombreTorta: s(e.nombreTorta), numero: s(e.numero), ademas: s(e.ademas)
    };
  }
  function pasoSano(p) {
    if (!p || typeof p !== 'object') return null;
    var a = Math.floor(Number(p.alcanzado)), n = Math.floor(Number(p.actual));
    if (!(a >= 1 && a <= 7)) return null;
    return {actual: n >= 1 && n <= a ? n : a, alcanzado: a};
  }

  var e = guardado();
  if (e) {
    paso = pasoSano(e.paso);
    e = sano(e);
    // Una fecha que ya pasó no sirve: se descarta.
    if (/^\d{4}-\d{2}-\d{2}$/.test(e.fecha) && e.fecha < S.hoyISO()) e.fecha = '';
    C.escribir(e);
  }

  C.alCambiar(function (estado, nueva, lineas, motivo) {
    if (motivo === 'reinicio') { paso = null; borrar(); }
    else if (motivo === 'cambio') guardar(estado);
  });

  // La referencia que llega desde la home, si el borrador no tiene otra.
  var ref = (/[?&]ref=([a-z]+)/.exec(location.search) || [])[1];
  if (ref && REFERENCIAS.indexOf(ref) >= 0 && !C.leer().referencia) {
    var radio = document.querySelector('input[name="referencia"][value="' + ref + '"]');
    if (radio) { radio.checked = true; C.render({silencioso: true}); }
  }

  window.ComandaBorrador = {
    paso: function () { return paso; },
    guardarPaso: function (p) {
      paso = p;
      // Con solo haber abierto la página no se crea un borrador.
      if (p.alcanzado > 1 || hay()) guardar(C.leer());
    }
  };
})();
