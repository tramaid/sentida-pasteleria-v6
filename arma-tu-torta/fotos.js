/* SENTIDA · la comanda — fotos de referencia (paso 6).
   Las fotos quedan en memoria, en una lista: se pueden sumar en varias
   tandas y quitar de a una. No se guardan en el borrador (pesan demasiado).
   Un enlace de WhatsApp solo lleva texto: «Mandar» abre el chat de Anto y el
   mensaje avisa que las fotos van en el chat. En el celular, «Mandar las
   fotos» las comparte después (la hoja no deja elegir el contacto por link).
   Sin JavaScript el campo queda oculto: no habría cómo mandarlas. */
(function () {
  'use strict';
  var C = window.Comanda;
  var campo = document.getElementById('campo-fotos');
  var input = document.getElementById('fotos');
  var boton = document.getElementById('fotos-adjuntar');
  var lista = document.getElementById('fotos-lista');
  var aviso = document.getElementById('fotos-aviso');
  var mini = document.getElementById('fotos-mini');
  var anuncio = document.getElementById('anuncio');
  if (!C || !campo || !input || !boton || !lista) return;

  var MAX = 6;
  var fotos = [];  // {archivo, url}
  var NOTA_CHAT = 'WhatsApp no deja adjuntar fotos desde la web: cuando se abra el chat, mandá las fotos ahí.';
  var NOTA_COMPARTIR = 'Primero mandá la comanda: se abre el chat de Anto. Después volvé acá y tocá «Mandar las fotos»: su chat va a aparecer primero.';

  function anunciar(t) { if (anuncio) anuncio.textContent = t; }
  function avisar(t) { if (aviso) aviso.textContent = t; }
  function cuantas(n) { return n === 1 ? '1 foto' : n + ' fotos'; }

  function pintar() {
    lista.textContent = '';
    fotos.forEach(function (f, i) {
      var li = document.createElement('li');
      var img = document.createElement('img');
      img.src = f.url;
      img.alt = 'Foto de referencia ' + (i + 1);
      var quitar = document.createElement('button');
      quitar.type = 'button';
      quitar.className = 'foto-quitar';
      quitar.setAttribute('data-i', i);
      quitar.setAttribute('aria-label', 'Quitar foto ' + (i + 1));
      quitar.innerHTML = '<svg class="ico" aria-hidden="true" focusable="false"><use href="#i-cerrar"/></svg>';
      li.appendChild(img);
      li.appendChild(quitar);
      lista.appendChild(li);
    });
    lista.hidden = !fotos.length;
    // En el cierre, chiquitas junto a la nota: para acordarse de cuáles mandar.
    if (mini) {
      mini.textContent = '';
      fotos.forEach(function (f, i) {
        var li = document.createElement('li');
        var img = document.createElement('img');
        img.src = f.url;
        img.alt = 'Foto de referencia ' + (i + 1);
        li.appendChild(img);
        mini.appendChild(li);
      });
    }
  }

  function vaciar() {
    fotos.forEach(function (f) { URL.revokeObjectURL(f.url); });
    fotos = [];
    avisar('');
    pintar();
  }

  boton.addEventListener('click', function () { input.click(); });

  input.addEventListener('change', function (ev) {
    // Lo maneja este archivo (con su propio anuncio), no el oyente general.
    ev.stopPropagation();
    var elegidas = Array.prototype.filter.call(input.files || [], function (a) {
      return /^image\//.test(a.type);
    });
    input.value = '';  // para poder volver a elegir la misma foto
    if (!elegidas.length) return;
    var lugar = MAX - fotos.length;
    if (lugar <= 0) {
      var lleno = 'Ya tenés 6 fotos, que es el máximo. Quitá una para sumar otra.';
      avisar(lleno);
      anunciar(lleno);
      return;
    }
    var suman = elegidas.slice(0, lugar);
    suman.forEach(function (a) { fotos.push({archivo: a, url: URL.createObjectURL(a)}); });
    var sobra = elegidas.length - suman.length;
    avisar(sobra ? 'Entran hasta 6 fotos: sumamos las primeras ' + suman.length + ' y quedaron afuera ' + sobra + '.' : '');
    pintar();
    C.render({silencioso: true, motivo: 'fotos'});
    anunciar((suman.length === 1 ? 'Foto agregada. ' : cuantas(suman.length) + ' agregadas. ') +
      'Tenés ' + cuantas(fotos.length) + ' de referencia.' + (sobra ? ' Entran hasta 6.' : ''));
  });

  lista.addEventListener('click', function (ev) {
    var b = ev.target.closest('.foto-quitar');
    if (!b) return;
    var i = Number(b.getAttribute('data-i'));
    var f = fotos[i];
    if (!f) return;
    URL.revokeObjectURL(f.url);
    fotos.splice(i, 1);
    avisar('');
    pintar();
    C.render({silencioso: true, motivo: 'fotos'});
    anunciar('Foto ' + (i + 1) + ' quitada. ' + (fotos.length ? 'Quedan ' + cuantas(fotos.length) + '.' : 'No quedan fotos.'));
    // El foco sigue en la lista, o vuelve al botón si ya no hay fotos.
    var sig = lista.querySelectorAll('.foto-quitar')[Math.min(i, fotos.length - 1)];
    (sig || boton).focus();
  });

  // La nota junto a «Mandar»: cómo viajan las fotos.
  var notas = document.querySelectorAll('[data-nota-fotos]');
  var compartir = document.getElementById('compartir-fotos');
  if (compartir) compartir.addEventListener('click', function () { C.compartirFotos(); });
  C.alCambiar(function (estado) {
    var n = estado ? estado.fotos : 0;
    var hoja = n > 0 && C.puedeCompartirFotos();
    Array.prototype.forEach.call(notas, function (nota) {
      nota.hidden = !n;
      var t = nota.querySelector('[data-nota-texto]') || nota;
      t.textContent = hoja ? NOTA_COMPARTIR : NOTA_CHAT;
    });
    if (compartir) compartir.hidden = !hoja;
  });

  campo.hidden = false;
  pintar();
  window.ComandaFotos = {
    archivos: function () { return fotos.map(function (f) { return f.archivo; }); },
    vaciar: vaciar  // «Empezar de nuevo»
  };
})();
