const { test } = require('node:test');
const assert = require('node:assert/strict');

test('Axios consulta Open Library a través de la simulación y maneja 404/503', {
  skip: !process.env.OPENLIBRARY_TEST_URL && 'Inicia la simulación Postman y define OPENLIBRARY_TEST_URL'
}, async () => {
  process.env.OPENLIBRARY_API_URL = process.env.OPENLIBRARY_TEST_URL;
  const app = require('../app');
  const server = await new Promise(resolve => {
    const s = app.listen(0, '127.0.0.1', () => resolve(s));
  });
  const base = `http://127.0.0.1:${server.address().port}/servicios/libros`;
  try {
    const search = await fetch(`${base}?q=fox`);
    assert.equal(search.status, 200);
    const data = await search.json();
    assert.equal(data.datos[0].nombre, 'Fantastic Mr. Fox');
    assert.equal(data.datos[0].autor, 'Roald Dahl');
    assert.equal(data.datos[0].id, 'OL45804W');
    const detail = await fetch(`${base}/OL45804W`);
    assert.equal(detail.status, 200);
    assert.match((await detail.json()).datos.resumen, /no tiene una descripción/);
    assert.equal((await fetch(`${base}/OL999999W`)).status, 404);
    const failure = await fetch(`${base}?q=upstream-error`);
    assert.equal(failure.status, 502);
    assert.match((await failure.json()).mensaje, /no está disponible/);
  } finally {
    await new Promise(resolve => server.close(resolve));
  }
});
