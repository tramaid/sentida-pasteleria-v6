/* SENTIDA · el pedido de la tienda — el mensaje.
   Funciones puras: ordenan lo guardado, suman y restan productos y arman
   el texto de WhatsApp. Sin DOM, para poder probarlas en Node. */
(function (raiz) {
  'use strict';
  var S = typeof module === 'object' && module.exports ? require('./base.js') : raiz.Sentida;
  var MAXIMO = 99;
  var FALTA = {
    items: 'Todavía no agregaste nada.',
    fecha: 'Elegí para cuándo lo querés.',
    pasada: 'Elegí una fecha de hoy en adelante.',
    nombre: 'Decinos a nombre de quién.'
  };

  function vacio() { return {items: [], fecha: '', entrega: 'retiro', nombre: '', ademas: ''}; }
  function cadena(x, largo) { return typeof x === 'string' ? x.slice(0, largo) : ''; }

  // Todo lo que viene de localStorage pasa por acá: lo que no tiene la forma
  // esperada se descarta sin romper nada.
  function normalizar(e, hoy) {
    var n = vacio();
    if (!e || typeof e !== 'object' || Array.isArray(e)) return n;
    var vistos = {};
    (Array.isArray(e.items) ? e.items : []).forEach(function (i) {
      if (!i || typeof i !== 'object' || typeof i.slug !== 'string') return;
      if (!/^[a-z0-9-]{1,60}$/.test(i.slug) || vistos[i.slug]) return;
      var nombre = S.limpio(cadena(i.nombre, 80));
      var cant = Math.floor(Number(i.cant));
      if (!nombre || !(cant >= 1)) return;
      vistos[i.slug] = true;
      n.items.push({slug: i.slug, nombre: nombre, cant: Math.min(cant, MAXIMO)});
    });
    var f = cadena(e.fecha, 10);
    n.fecha = S.fecha(f) && (!hoy || f >= hoy) ? f : '';
    n.entrega = e.entrega === 'envio' ? 'envio' : 'retiro';
    n.nombre = cadena(e.nombre, 80);
    n.ademas = cadena(e.ademas, 500);
    return n;
  }

  function cantidad(e, slug) {
    for (var i = 0; i < e.items.length; i++) if (e.items[i].slug === slug) return e.items[i].cant;
    return 0;
  }
  function total(e) { return e.items.reduce(function (t, i) { return t + i.cant; }, 0); }

  // Suma (delta > 0) o resta (delta < 0) un producto. Devuelve un estado nuevo.
  function cambiar(e, slug, nombre, delta) {
    var n = normalizar(e);
    var estaba = false;
    n.items = n.items.map(function (i) {
      if (i.slug !== slug) return i;
      estaba = true;
      return {slug: i.slug, nombre: i.nombre, cant: Math.min(i.cant + delta, MAXIMO)};
    }).filter(function (i) { return i.cant > 0; });
    if (!estaba && delta > 0) n.items.push({slug: slug, nombre: S.limpio(nombre), cant: Math.min(delta, MAXIMO)});
    return n;
  }

  function texto(e) {
    var ls = ['Hola SENTIDA, quiero hacer este pedido:'];
    e.items.forEach(function (i) { ls.push('• ' + i.nombre + ' × ' + i.cant); });
    var f = S.fecha(e.fecha);
    if (f) ls.push('Para: ' + f);
    ls.push('Entrega: ' + (e.entrega === 'envio' ? 'envío a domicilio' : 'retiro en Martínez'));
    var nombre = S.limpio(e.nombre), ademas = S.limpio(e.ademas);
    if (nombre) ls.push('A nombre de: ' + nombre);
    if (ademas) ls.push('Además: ' + ademas);
    ls.push('¿Me confirman precio y disponibilidad?');
    return ls.join('\n');
  }

  // Qué falta para poder mandar: '' si nada. Con hoy, una fecha pasada no sirve.
  function falta(e, hoy) {
    if (!e.items.length) return 'items';
    if (!S.fecha(e.fecha)) return 'fecha';
    if (hoy && e.fecha < hoy) return 'pasada';
    if (!S.limpio(e.nombre)) return 'nombre';
    return '';
  }

  function url(numero, e) { return S.whatsapp(numero, texto(e)); }

  var api = {MAXIMO: MAXIMO, FALTA: FALTA, vacio: vacio, normalizar: normalizar, cantidad: cantidad,
             total: total, cambiar: cambiar, texto: texto, falta: falta, url: url};
  if (typeof module === 'object' && module.exports) module.exports = api;
  else raiz.PedidoMensaje = api;
})(typeof window !== 'undefined' ? window : this);
