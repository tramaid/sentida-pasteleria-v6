/* SENTIDA · el pedido de la tienda.
   Guarda lo elegido en el navegador, lo muestra en «Mi pedido» y en los
   tickets de la página, y lo manda en un solo mensaje de WhatsApp a Anto.
   Sin este archivo, cada producto se pide con su propio enlace. */
(function () {
  'use strict';
  var S = window.Sentida, P = window.PedidoMensaje;
  if (!S || !P || !window.JSON) return;
  var CLAVE = 'sentida-pedido-v1';
  var script = document.currentScript;
  var raiz = (script && script.getAttribute('data-raiz')) || '';
  var oyentes = [];
  var modo = 'form';       // 'form', o 'listo' después de mandar
  var volverA = null;
  var estado = leer();

  function leer() {
    try { return P.normalizar(JSON.parse(localStorage.getItem(CLAVE) || 'null'), S.hoyISO()); }
    catch (err) { return P.vacio(); }
  }
  function guardar() {
    try { localStorage.setItem(CLAVE, JSON.stringify(estado)); } catch (err) { /* sin lugar o bloqueado */ }
  }

  var anuncio = document.createElement('p');
  anuncio.className = 'carrito-anuncio';
  anuncio.setAttribute('aria-live', 'polite');
  document.body.appendChild(anuncio);
  function anunciar(t) { anuncio.textContent = t; }

  function icono(id, clase) {
    return '<svg class="ico' + (clase ? ' ' + clase : '') + '" aria-hidden="true" focusable="false"><use href="#' + id + '"/></svg>';
  }

  var dialogo = document.createElement('dialog');
  dialogo.className = 'carrito-dialogo';
  dialogo.id = 'carrito-dialogo';
  dialogo.setAttribute('aria-labelledby', 'carrito-t');
  dialogo.innerHTML =
    '<div class="carrito-in">' +
      '<button type="button" class="carrito-cerrar" data-cerrar aria-label="Cerrar">' + icono('i-cerrar') + '</button>' +
      '<div class="ticket"><div class="papel">' +
        '<div class="ticket-cab"><span>SENTIDA · Pastelería</span><span>Pedido</span></div>' +
        '<p class="ticket-t display" id="carrito-t" tabindex="-1">Tu pedido</p>' +
        '<ul class="carrito-lista" role="list" data-carrito-lista></ul>' +
        '<p class="carrito-vacio" data-carrito-vacio>Todavía no agregaste nada.</p>' +
        '<p class="ticket-fijo">Precio y disponibilidad te los confirmamos por WhatsApp.</p>' +
      '</div></div>' +
      '<p class="carrito-ir botones" data-si-vacio>' +
        '<a class="btn btn-2" href="' + raiz + 'tortas/">Nuestras tortas</a>' +
        '<a class="btn btn-2" href="' + raiz + 'pasteleria/">Pastelería</a>' +
      '</p>' +
      '<form class="carrito-form" novalidate>' +
        '<div class="cf"><label class="cf-t" for="carrito-fecha">¿Para cuándo?</label>' +
          '<input type="date" id="carrito-fecha" name="fecha"></div>' +
        '<fieldset class="cf"><legend class="cf-t">¿Retiro o envío?</legend>' +
          '<label class="cf-op"><input type="radio" name="entrega" value="retiro"> Retiro en Martínez</label>' +
          '<label class="cf-op"><input type="radio" name="entrega" value="envio"> Envío en Zona Norte</label>' +
        '</fieldset>' +
        '<div class="cf"><label class="cf-t" for="carrito-nombre">¿A nombre de quién?</label>' +
          '<input type="text" id="carrito-nombre" name="nombre" autocomplete="name"></div>' +
        '<div class="cf"><label class="cf-t" for="carrito-ademas">¿Algo más?</label>' +
          '<textarea id="carrito-ademas" name="ademas" rows="2"></textarea></div>' +
        '<p class="carrito-falta" data-falta aria-live="assertive"></p>' +
        '<button class="btn btn-1" type="submit">' + icono('i-whatsapp', 'ico-wa') + 'Mandar pedido por WhatsApp a Anto</button>' +
        '<a class="carrito-nadia" data-nadia href="#" target="_blank" rel="noopener" aria-describedby="nueva-pestana">¿Preferís escribirle a Nadia? 11&nbsp;3145&#8209;9646</a>' +
      '</form>' +
      '<div class="carrito-listo" data-listo hidden>' +
        '<p>¿Se abrió WhatsApp con tu pedido? Cuando lo mandes, vaciá el ticket para no repetirlo.</p>' +
        '<p class="botones"><button type="button" class="btn btn-1" data-vaciar>Vaciar el pedido</button>' +
        '<button type="button" class="btn btn-2" data-todavia>Todavía no</button></p>' +
      '</div>' +
      '<p class="carrito-decorada"><a href="' + raiz + 'arma-tu-torta/">¿Querés una torta decorada? Armala acá</a></p>' +
    '</div>';
  document.body.appendChild(dialogo);

  var form = dialogo.querySelector('.carrito-form');
  var falta = dialogo.querySelector('[data-falta]');
  var listo = dialogo.querySelector('[data-listo]');
  var nadia = dialogo.querySelector('[data-nadia]');
  form.elements.fecha.min = S.hoyISO();

  // Los nombres se escriben siempre como texto: nada de lo guardado se interpreta como HTML.
  function contador(i) {
    var c = document.createElement('span');
    c.className = 'contador';
    c.setAttribute('data-slug', i.slug);
    c.setAttribute('data-nombre', i.nombre);
    var menos = document.createElement('button');
    menos.type = 'button';
    menos.setAttribute('data-menos', '');
    menos.setAttribute('aria-label', 'Uno menos de ' + i.nombre);
    menos.textContent = '−';
    var cant = document.createElement('output');
    cant.setAttribute('aria-live', 'off');
    cant.textContent = i.cant;
    var mas = document.createElement('button');
    mas.type = 'button';
    mas.setAttribute('data-mas', '');
    mas.setAttribute('aria-label', 'Uno más de ' + i.nombre);
    mas.textContent = '+';
    mas.disabled = i.cant >= P.MAXIMO;
    c.appendChild(menos);
    c.appendChild(cant);
    c.appendChild(mas);
    return c;
  }

  function pintarLista(ul, nueva) {
    ul.textContent = '';
    estado.items.forEach(function (i) {
      var li = document.createElement('li');
      li.className = 'carrito-item' + (i.slug === nueva ? ' nueva' : '');
      var nombre = document.createElement('span');
      nombre.className = 'carrito-nombre';
      nombre.textContent = i.nombre;
      li.appendChild(nombre);
      li.appendChild(contador(i));
      ul.appendChild(li);
    });
  }

  function pintarCabecera() {
    var n = P.total(estado);
    document.querySelectorAll('[data-mi-pedido]').forEach(function (a) {
      var badge = a.querySelector('.mi-pedido-n');
      if (badge) { badge.textContent = n; badge.hidden = n === 0; }
      a.setAttribute('aria-label', n ? 'Mi pedido, ' + n + (n === 1 ? ' producto' : ' productos') : 'Mi pedido, vacío');
      a.setAttribute('aria-haspopup', 'dialog');
    });
  }

  function pintar(nueva) {
    var hay = estado.items.length > 0;
    if (!hay) modo = 'form';
    document.querySelectorAll('[data-carrito-lista]').forEach(function (ul) { pintarLista(ul, nueva); });
    document.querySelectorAll('[data-carrito-vacio]').forEach(function (p) {
      p.hidden = hay;
      p.textContent = 'Todavía no agregaste nada.';
    });
    document.querySelectorAll('[data-carrito-abrir]').forEach(function (b) { b.hidden = !hay; });
    dialogo.querySelector('[data-si-vacio]').hidden = hay;
    form.hidden = !hay || modo !== 'form';
    listo.hidden = modo !== 'listo';
    nadia.href = P.url(S.NADIA, estado);
    pintarCabecera();
    oyentes.forEach(function (fn) { fn(estado, nueva || null); });
  }

  function llenarFormulario() {
    var f = form.elements;
    f.fecha.value = estado.fecha;
    f.nombre.value = estado.nombre;
    f.ademas.value = estado.ademas;
    form.querySelectorAll('[name="entrega"]').forEach(function (r) { r.checked = r.value === estado.entrega; });
  }
  function leerFormulario() {
    var f = form.elements;
    var entrega = form.querySelector('[name="entrega"]:checked');
    estado.fecha = f.fecha.value;
    estado.nombre = f.nombre.value;
    estado.ademas = f.ademas.value;
    estado.entrega = entrega && entrega.value === 'envio' ? 'envio' : 'retiro';
    guardar();
    nadia.href = P.url(S.NADIA, estado);
    falta.textContent = '';
  }
  form.addEventListener('input', leerFormulario);
  form.addEventListener('change', leerFormulario);

  function cambiar(slug, nombre, delta) {
    var antes = P.cantidad(estado, slug);
    estado = P.cambiar(estado, slug, nombre, delta);
    var ahora = P.cantidad(estado, slug);
    if (ahora === antes) return;
    guardar();
    pintar(ahora > antes ? slug : null);
    anunciar(ahora ? nombre + ': ' + ahora + ' en tu pedido.' : 'Sacaste ' + nombre + ' del pedido.');
  }

  function abrir(desde) {
    if (typeof dialogo.showModal !== 'function') { location.href = raiz + 'tortas/#pedido'; return; }
    volverA = desde || document.activeElement;
    modo = 'form';
    falta.textContent = '';
    llenarFormulario();
    pintar();
    if (!dialogo.open) dialogo.showModal();
    dialogo.querySelector('#carrito-t').focus();
  }
  dialogo.addEventListener('close', function () {
    if (volverA && volverA.focus && document.contains(volverA)) volverA.focus();
    volverA = null;
  });
  dialogo.addEventListener('click', function (ev) {
    if (ev.target === dialogo || ev.target.closest('[data-cerrar]')) dialogo.close();
  });

  document.addEventListener('click', function (ev) {
    var abre = ev.target.closest('[data-mi-pedido], [data-carrito-abrir]');
    if (abre) { ev.preventDefault(); abrir(abre); return; }
    var b = ev.target.closest('.carrito-lista .contador button');
    if (!b) return;
    var c = b.parentNode, lista = c.closest('[data-carrito-lista]');
    var cual = b.hasAttribute('data-mas') ? 'data-mas' : 'data-menos';
    var slug = c.getAttribute('data-slug');
    cambiar(slug, c.getAttribute('data-nombre'), cual === 'data-mas' ? 1 : -1);
    // El foco vuelve al mismo botón o, si el producto salió, al título del ticket.
    var fila = lista.querySelector('.contador[data-slug="' + slug + '"]');
    var destino = fila && (fila.querySelector('[' + cual + ']:not(:disabled)') || fila.querySelector('[data-menos]'));
    (destino || lista.closest('.papel').querySelector('.ticket-t')).focus();
  });

  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    leerFormulario();
    var f = P.falta(estado, S.hoyISO());
    if (f) {
      falta.textContent = P.FALTA[f];
      var campo = form.elements[f === 'pasada' ? 'fecha' : f];
      if (campo) campo.focus();
      return;
    }
    var destino = P.url(S.ANTO, estado);
    var w = window.open(destino, '_blank');
    if (w) { try { w.opener = null; } catch (err) { /* otra ventana */ } }
    else { window.location.href = destino; return; }  // navegador que bloquea pestañas nuevas
    modo = 'listo';
    pintar();
    dialogo.querySelector('[data-vaciar]').focus();
  });
  dialogo.querySelector('[data-vaciar]').addEventListener('click', function () {
    estado = P.vacio();
    guardar();
    modo = 'form';
    pintar();
    anunciar('Vaciamos tu pedido.');
    dialogo.close();
  });
  dialogo.querySelector('[data-todavia]').addEventListener('click', function () {
    modo = 'form';
    pintar();
    form.querySelector('[type="submit"]').focus();
  });

  // Otra pestaña cambió el pedido.
  window.addEventListener('storage', function (ev) {
    if (ev.key !== CLAVE && ev.key !== null) return;
    estado = leer();
    pintar();
  });

  window.Carrito = {
    MAXIMO: P.MAXIMO,
    cantidad: function (slug) { return P.cantidad(estado, slug); },
    total: function () { return P.total(estado); },
    cambiar: cambiar,
    abrir: abrir,
    alCambiar: function (fn) { oyentes.push(fn); fn(estado, null); }
  };
  pintar();
})();
