/* SENTIDA · la comanda — el mensaje.
   Funciones puras: del estado del formulario a las líneas del ticket, al
   texto de WhatsApp y a lo que le falta a cada paso. Sin DOM, para poder
   probarlas en Node. */
(function (raiz) {
  'use strict';
  var S = typeof module === 'object' && module.exports ? require('../comun/base.js') : raiz.Sentida;
  var A_DEFINIR = 'a definir';
  var TAMANOS = {
    chica: 'chica (10 a 12 porciones)',
    mediana: 'mediana (15 a 25 porciones)',
    grande: 'grande (20 a 30 porciones)'
  };
  var NOMBRES = {
    vainilla: 'vainilla', chocolate: 'chocolate',
    ddl: 'dulce de leche', 'butter-choco': 'butter choco',
    'frutos-rojos': 'frutos rojos', oreo: 'crema Oreo', bonobon: 'crema Bon o Bon',
    chocotorta: 'crema Chocotorta', kinder: 'crema Kinder',
    bombon: 'bombón', merenguitos: 'merenguitos', chips: 'chips', nuez: 'nuez', mani: 'maní'
  };
  var REFERENCIAS = {
    petalos: 'la de pétalos', flores: 'la de flores naturales',
    letras: 'las de letras y números', mensaje: 'la del mensaje'
  };
  // Lo que se muestra si se toca Siguiente sin haber elegido.
  var FALTA = {
    1: 'Elegí una fecha o marcá «Todavía no sé».',
    2: 'Elegí un tamaño para seguir.',
    3: 'Elegí un bizcochuelo para seguir.',
    4: 'Elegí un relleno para seguir.',
    5: 'Elegí el segundo relleno para seguir.'
  };
  var FECHA_PASADA = 'Elegí una fecha de hoy en adelante.';
  var CIERRE = 7;

  function lista(items) {
    if (items.length < 2) return items.join('');
    return items.slice(0, -1).join(', ') + ' y ' + items[items.length - 1];
  }

  // Una opción sin tocar queda «a definir» y vacía.
  function opcion(v, dic) {
    if (!v) return {valor: A_DEFINIR, vacio: true};
    return {valor: dic[v] || v, vacio: false};
  }

  function lineas(e) {
    e = e || {};
    var out = [];
    function push(clave, etiqueta, r) {
      out.push({clave: clave, etiqueta: etiqueta, valor: r.valor, vacio: r.vacio});
    }

    var f = S.fecha(e.fecha), escrita = S.limpio(e.fecha);
    push('fecha', 'Fecha',
      e.sinFecha ? {valor: A_DEFINIR, vacio: false}
      : f ? {valor: f, vacio: false}
      : escrita ? {valor: escrita, vacio: false}
      : {valor: A_DEFINIR, vacio: true});
    push('tamano', 'Tamaño', opcion(e.tamano, TAMANOS));
    push('bizcochuelo', 'Bizcochuelo', opcion(e.bizcochuelo, NOMBRES));

    var rel = opcion(e.relleno, NOMBRES);
    var ag = (e.agregados || []).map(function (a) { return NOMBRES[a] || a; });
    if (ag.length) {
      rel = {valor: (rel.vacio ? A_DEFINIR + ', con ' : rel.valor + ' con ') + lista(ag), vacio: false};
    }
    push('relleno', 'Relleno', rel);
    push('relleno2', 'Segundo relleno', opcion(e.relleno2, NOMBRES));

    var idea = S.limpio(e.idea), ref = REFERENCIAS[e.referencia] || '';
    var deco = idea && ref ? idea + ' (como ' + ref + ')' : idea || (ref ? 'como ' + ref : '');
    push('decoracion', 'Decoración', deco ? {valor: deco, vacio: false} : {valor: A_DEFINIR, vacio: true});

    var nombre = S.limpio(e.nombreTorta);
    if (nombre) push('nombre', 'Nombre', {valor: nombre, vacio: false});
    var numero = S.limpio(e.numero);
    if (numero) push('numero', 'Número', {valor: numero, vacio: false});
    var ademas = S.limpio(e.ademas);
    if (ademas) push('ademas', 'Además', {valor: ademas, vacio: false});
    return out;
  }

  function texto(e) {
    return 'Hola SENTIDA, les paso mi comanda:\n' +
      lineas(e).map(function (l) { return l.etiqueta + ': ' + l.valor; }).join('\n');
  }

  // Qué le falta al paso n para poder pasar ('' si nada). 6 y 7 no piden nada.
  // Con hoy (AAAA-MM-DD), una fecha elegida que ya pasó no sirve.
  function falta(n, e, hoy) {
    e = e || {};
    if (n === 1 && !e.sinFecha && hoy && S.fecha(e.fecha) && e.fecha < hoy) return FECHA_PASADA;
    var listo = {
      1: !!(e.sinFecha || S.limpio(e.fecha)),
      2: !!e.tamano, 3: !!e.bizcochuelo, 4: !!e.relleno, 5: !!e.relleno2
    }[n];
    return listo === false ? FALTA[n] : '';
  }

  // El primer paso obligatorio sin completar; el cierre (7) si están todos.
  function primerIncompleto(e, hoy) {
    for (var n = 1; n <= 5; n++) if (falta(n, e, hoy)) return n;
    return CIERRE;
  }

  function url(numero, t) { return S.whatsapp(numero, t); }

  var api = {A_DEFINIR: A_DEFINIR, fecha: S.fecha, lista: lista, lineas: lineas, texto: texto,
             falta: falta, primerIncompleto: primerIncompleto, url: url};
  if (typeof module === 'object' && module.exports) module.exports = api;
  else raiz.ComandaMensaje = api;
})(typeof window !== 'undefined' ? window : this);
