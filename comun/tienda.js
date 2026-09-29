/* SENTIDA · la tienda (Nuestras tortas y Antojos).
   Con JavaScript, cada tarjeta suma al pedido con un contador y, en el
   celular, aparece la tira «Tu pedido». Sin JavaScript, cada tarjeta
   tiene su enlace de WhatsApp. */
(function () {
  'use strict';
  var C = window.Carrito;
  if (!C) return;
  var tarjetas = Array.prototype.slice.call(document.querySelectorAll('[data-producto]'));
  var tira = document.querySelector('.tira-pedido');
  var tiraN = tira && tira.querySelector('.tira-pedido-n');

  tarjetas.forEach(function (t) {
    var slug = t.getAttribute('data-producto'), nombre = t.getAttribute('data-nombre');
    var agregar = t.querySelector('.producto-agregar'), cont = t.querySelector('.contador');
    t.querySelector('.producto-wa').hidden = true;
    agregar.addEventListener('click', function () {
      C.cambiar(slug, nombre, 1);
      cont.querySelector('[data-mas]').focus();
    });
    cont.addEventListener('click', function (ev) {
      var b = ev.target.closest('button');
      if (!b) return;
      C.cambiar(slug, nombre, b.hasAttribute('data-mas') ? 1 : -1);
      if (!C.cantidad(slug)) agregar.focus();
    });
  });

  C.alCambiar(function () {
    tarjetas.forEach(function (t) {
      var n = C.cantidad(t.getAttribute('data-producto'));
      var cont = t.querySelector('.contador');
      t.querySelector('.producto-agregar').hidden = n > 0;
      cont.hidden = n === 0;
      cont.querySelector('output').textContent = n;
      cont.querySelector('[data-mas]').disabled = n >= C.MAXIMO;
      t.classList.toggle('en-pedido', n > 0);
    });
    if (tira) {
      var total = C.total();
      tira.hidden = total === 0;
      tiraN.textContent = total === 1 ? '1 producto' : total + ' productos';
    }
  });

  // Llegar con #slug (desde la home): la tarjeta se marca.
  function marcar() {
    var id = decodeURIComponent(location.hash.slice(1));
    var t = id && document.getElementById(id);
    if (!t || !t.hasAttribute('data-producto')) return;
    t.classList.remove('marcada');
    void t.offsetWidth;
    t.classList.add('marcada');
  }
  window.addEventListener('hashchange', marcar);
  marcar();
})();

/* Las tarjetas con varias fotos. Sin JavaScript la tira igual se desliza;
   acá se prenden las flechas (dan la vuelta), los puntos y el aviso
   «Foto n de N», que siguen a la foto que se ve. */
(function () {
  'use strict';
  var mov = document.documentElement.classList.contains('mov');
  Array.prototype.forEach.call(document.querySelectorAll('[data-galeria]'), function (g) {
    var tira = g.querySelector('.galeria-tira');
    var fotos = tira.querySelectorAll('img');
    var puntos = g.querySelectorAll('.galeria-puntos span');
    var estado = g.querySelector('.galeria-estado');
    var n = fotos.length, actual = 0, cuadro = 0;
    // Las flechas reemplazan al foco de la tira. Sacar el tabindex no alcanza:
    // Chrome y Firefox igual enfocan un contenedor con scroll; -1 sí lo saca del Tab.
    tira.tabIndex = -1;
    g.querySelector('.galeria-ant').hidden = false;
    g.querySelector('.galeria-sig').hidden = false;
    g.querySelector('.galeria-puntos').hidden = false;

    // Las fotos extra esperan (lazy); si la persona se acerca a la tarjeta, que carguen ya.
    function traer() {
      Array.prototype.forEach.call(fotos, function (f) { f.loading = 'eager'; });
      ['pointerenter', 'focusin', 'touchstart'].forEach(function (ev) { g.removeEventListener(ev, traer); });
    }
    ['pointerenter', 'focusin', 'touchstart'].forEach(function (ev) { g.addEventListener(ev, traer, {passive: true}); });

    function poner(i) {
      if (i === actual) return;
      puntos[actual].classList.remove('actual');
      puntos[i].classList.add('actual');
      actual = i;
      estado.textContent = 'Foto ' + (i + 1) + ' de ' + n;
    }
    function ir(i) {
      i = (i + n) % n;
      tira.scrollTo({left: i * tira.clientWidth, behavior: mov ? 'smooth' : 'auto'});
    }
    g.querySelector('.galeria-ant').addEventListener('click', function () { ir(actual - 1); });
    g.querySelector('.galeria-sig').addEventListener('click', function () { ir(actual + 1); });
    tira.addEventListener('scroll', function () {
      cancelAnimationFrame(cuadro);
      cuadro = requestAnimationFrame(function () {
        var i = Math.round(tira.scrollLeft / (tira.clientWidth || 1));
        poner(Math.max(0, Math.min(n - 1, i)));
      });
    }, {passive: true});
  });
})();
