import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require = createRequire(import.meta.url);
const M = require('../../arma-tu-torta/mensaje.js');

const COMPLETO = {
  fecha: '2026-11-07', sinFecha: false, tamano: 'mediana', bizcochuelo: 'vainilla',
  relleno: 'ddl', agregados: ['chips', 'nuez'], relleno2: 'frutos-rojos',
  idea: 'flores naturales en tonos pastel', referencia: 'flores', nombreTorta: 'Mamá', numero: '60'
};

test('fecha en palabras', () => {
  assert.equal(M.fecha('2026-11-07'), 'sábado 7/11');
  assert.equal(M.fecha('2026-02-30'), '');
});

test('lista con «y»', () => {
  assert.equal(M.lista([]), '');
  assert.equal(M.lista(['nuez']), 'nuez');
  assert.equal(M.lista(['bombón', 'chips', 'nuez']), 'bombón, chips y nuez');
});

test('estado vacío: seis líneas «a definir» marcadas vacías', () => {
  const ls = M.lineas({});
  assert.deepEqual(ls.map(l => l.clave), ['fecha', 'tamano', 'bizcochuelo', 'relleno', 'relleno2', 'decoracion']);
  assert.ok(ls.every(l => l.vacio && l.valor === 'a definir'));
});

test('mensaje completo, tal cual la especificación', () => {
  assert.equal(M.texto(COMPLETO), [
    'Hola SENTIDA, les paso mi comanda:',
    'Fecha: sábado 7/11',
    'Tamaño: mediana (15 a 25 porciones)',
    'Bizcochuelo: vainilla',
    'Relleno: dulce de leche con chips y nuez',
    'Segundo relleno: frutos rojos',
    'Decoración: flores naturales en tonos pastel (como la de flores naturales)',
    'Nombre: Mamá',
    'Número: 60'
  ].join('\n'));
});

test('«Además» va al final, solo si tiene texto', () => {
  assert.equal(M.texto({...COMPLETO, ademas: '  sin nuez,   por favor '}).split('\n').pop(), 'Además: sin nuez, por favor');
  assert.ok(!M.texto({...COMPLETO, ademas: '   '}).includes('Además'));
  const l = M.lineas({ademas: 'x'}).pop();
  assert.deepEqual([l.clave, l.etiqueta, l.vacio], ['ademas', 'Además', false]);
});

test('«Todavía no sé» la fecha', () => {
  const l = M.lineas({fecha: '2026-11-07', sinFecha: true})[0];
  assert.deepEqual([l.valor, l.vacio], ['a definir', false]);
});

test('fecha escrita a mano se respeta', () => {
  assert.equal(M.lineas({fecha: '7 de noviembre'})[0].valor, '7 de noviembre');
});

test('agregados sin relleno elegido', () => {
  const l = M.lineas({agregados: ['nuez']}).find(x => x.clave === 'relleno');
  assert.equal(l.valor, 'a definir, con nuez');
  assert.equal(l.vacio, false);
});

test('decoración solo con referencia, e idea con espacios de más', () => {
  assert.equal(M.lineas({referencia: 'petalos'})[5].valor, 'como la de pétalos');
  assert.equal(M.lineas({idea: '  rosa   y  dorado '})[5].valor, 'rosa y dorado');
});

test('nombre y número solo si se completaron', () => {
  assert.equal(M.lineas({nombreTorta: '  ', numero: ''}).length, 6);
  assert.deepEqual(M.lineas({nombreTorta: 'Lu', numero: '5'}).slice(6).map(l => l.valor), ['Lu', '5']);
});

test('qué falta en cada paso', () => {
  assert.equal(M.falta(1, {}), 'Elegí una fecha o marcá «Todavía no sé».');
  assert.equal(M.falta(1, {sinFecha: true}), '');
  assert.equal(M.falta(1, {fecha: '7 de noviembre'}), '');
  assert.equal(M.falta(2, {}), 'Elegí un tamaño para seguir.');
  assert.equal(M.falta(3, {}), 'Elegí un bizcochuelo para seguir.');
  assert.equal(M.falta(4, {agregados: ['nuez']}), 'Elegí un relleno para seguir.');
  assert.equal(M.falta(5, {}), 'Elegí el segundo relleno para seguir.');
  assert.equal(M.falta(6, {}), '');
  assert.equal(M.falta(7, {}), '');
  assert.equal(M.falta(2, COMPLETO), '');
});

test('el primer paso incompleto', () => {
  assert.equal(M.primerIncompleto({}), 1);
  assert.equal(M.primerIncompleto({sinFecha: true, tamano: 'chica'}), 3);
  assert.equal(M.primerIncompleto(COMPLETO), 7);
  assert.equal(M.primerIncompleto({...COMPLETO, idea: '', referencia: ''}), 7);
});

test('url de WhatsApp codificada', () => {
  const u = M.url('5491158300787', 'Hola & chau\nrosa');
  assert.equal(decodeURIComponent(u.split('?text=')[1]), 'Hola & chau\nrosa');
});

test('la fecha del paso 1 no puede ser anterior a hoy', () => {
  assert.equal(M.falta(1, {fecha: '2026-09-23'}, '2026-09-24'), 'Elegí una fecha de hoy en adelante.');
  assert.equal(M.falta(1, {fecha: '2026-09-24'}, '2026-09-24'), '');
  assert.equal(M.falta(1, {fecha: '2026-09-23', sinFecha: true}, '2026-09-24'), '');
  assert.equal(M.primerIncompleto({...COMPLETO, fecha: '2020-01-01'}, '2026-09-24'), 1);
});

test('los dos rellenos tienen agregados', () => {
  const ls = M.lineas({relleno: 'kinder', agregados: ['nuez'], relleno2: 'ddl', agregados2: ['bombon', 'mani']});
  assert.equal(ls.find(x => x.clave === 'relleno').valor, 'crema Kinder con nuez');
  assert.equal(ls.find(x => x.clave === 'relleno2').valor, 'dulce de leche con bombón y maní');
});
