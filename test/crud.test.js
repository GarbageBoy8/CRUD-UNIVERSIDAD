const { test, before, after } = require('node:test');
const assert = require('node:assert/strict');
const { randomUUID } = require('node:crypto');
process.env.AUTH_USER = 'prueba';
process.env.AUTH_PASSWORD = 'solo-pruebas';
process.env.JWT_SECRET = randomUUID();
const mongoose = require('mongoose');
const jwt = require('jwt-simple');
const app = require('../app');
let server, base, token;

async function request(path, method = 'GET', body, auth = token) {
  const response = await fetch(base + path, {
    method,
    headers: { 'Content-Type': 'application/json', ...(auth ? { Authorization: `Bearer ${auth}` } : {}) },
    ...(body === undefined ? {} : { body: JSON.stringify(body) })
  });
  return { status: response.status, data: await response.json() };
}
before(async () => {
  // Cada ejecución crea y elimina únicamente su propia base de pruebas.
  await mongoose.connect(process.env.TEST_MONGODB_URI || 'mongodb://127.0.0.1:27018', {
    dbName: `lumbre_test_${randomUUID().replaceAll('-', '')}`, serverSelectionTimeoutMS: 5000
  });
  await mongoose.model('Genero').init();
  server = await new Promise(resolve => {
    const s = app.listen(0, '127.0.0.1', () => resolve(s));
  });
  base = `http://127.0.0.1:${server.address().port}`;
});
after(async () => {
  if (server) await new Promise(resolve => server.close(resolve));
  if (mongoose.connection.readyState === 1) await mongoose.connection.dropDatabase();
  await mongoose.disconnect();
});

test('autenticación: exige credenciales, protege rutas y no incluye contraseña en JWT', async () => {
  assert.equal((await request('/auth/login', 'POST', {})).status, 400);
  assert.equal((await request('/auth/login', 'POST', { usuario: 'prueba', contrasena: 'incorrecta' })).status, 401);
  const login = await request('/auth/login', 'POST', { usuario: 'prueba', contrasena: 'solo-pruebas' });
  assert.equal(login.status, 200);
  token = login.data.token;
  const payload = jwt.decode(token, process.env.JWT_SECRET);
  assert.deepEqual(Object.keys(payload).sort(), ['exp', 'iat', 'usuario']);
  assert.equal(payload.exp - payload.iat, 3600);
  assert.equal((await request('/libros/obtenerVarios', 'GET', undefined, '')).status, 401);
  assert.equal((await request('/libros/obtenerVarios', 'GET', undefined, 'invalido')).status, 401);
  for (const payload of [{ usuario: 'prueba' }, { usuario: 'prueba', iat: 1, exp: '9999999999' }]) {
    const incompleto = jwt.encode(payload, process.env.JWT_SECRET, 'HS256');
    assert.equal((await request('/libros/obtenerVarios', 'GET', undefined, incompleto)).status, 401);
  }
  const otroAlgoritmo = jwt.encode({ usuario: 'prueba', iat: 1, exp: 9999999999 }, process.env.JWT_SECRET, 'HS512');
  assert.equal((await request('/libros/obtenerVarios', 'GET', undefined, otroAlgoritmo)).status, 401);
  const sinBearer = await fetch(base + '/libros/obtenerVarios', { headers: { Authorization: token } });
  assert.equal(sinBearer.status, 401);
  const vencido = jwt.encode({ usuario: 'prueba', exp: 1 }, process.env.JWT_SECRET);
  assert.equal((await request('/generos/obtenerVarios', 'GET', undefined, vencido)).status, 403);
});

test('CRUD completo, relación 1:N y validaciones de libros y géneros', async () => {
  const genre = await request('/generos/falta', 'POST', { nombre: 'Narrativa', descripcion: 'Historias' });
  assert.equal(genre.status, 201);
  const id = genre.data.datos._id;
  assert.equal((await request('/generos/falta', 'POST', { nombre: 'Narrativa' })).status, 400);
  assert.equal((await request('/generos/falta', 'POST', { nombre: 'Otro', descripcion: {} })).status, 400);
  const body = { nombre: 'Pedro Páramo', autor: 'Juan Rulfo', genero: id, ubicacion: 'A-01', ejemplares: 3 };
  for (const cambio of [{ autor: '' }, { ejemplares: -1 }, { ejemplares: 1.5 }, { ejemplares: null }, { genero: {} }]) {
    assert.equal((await request('/libros/falta', 'POST', { ...body, ...cambio })).status, 400);
  }
  const created = await request('/libros/falta', 'POST', body);
  assert.equal(created.status, 201);
  const bookId = created.data.datos._id;
  assert.equal(created.data.datos.genero.nombre, 'Narrativa');
  assert.equal((await request('/libros/obtenerVarios')).data.datos.length, 1);
  assert.equal((await request(`/libros/obtenerUno/${bookId}`)).data.datos.autor, 'Juan Rulfo');
  assert.equal((await request(`/generos/obtenerUno/${id}`)).data.datos.libros.length, 1);
  assert.equal((await request('/generos/obtenerVarios')).data.datos[0].libros.length, 1);
  assert.equal((await request(`/generos/eliminar/${id}`, 'DELETE')).status, 400);
  for (const cambio of [{ ejemplares: 2.5 }, { genero: null }, { nombre: '' }, { autor: 9 }, { otro: true }]) {
    assert.equal((await request(`/libros/baja/${bookId}`, 'PUT', cambio)).status, 400);
  }
  const edit = await request(`/libros/baja/${bookId}`, 'PUT', { nombre: 'Pedro Páramo · edición nueva', ejemplares: 0, genero: 'Narrativa' });
  assert.equal(edit.status, 200);
  assert.equal(edit.data.datos.ejemplares, 0);
  assert.equal((await request(`/generos/baja/${id}`, 'PUT', { nombre: 'Novela' })).status, 200);
  assert.equal((await request(`/libros/obtenerUno/${bookId}`)).data.datos.genero.nombre, 'Novela');
  assert.equal((await request(`/generos/baja/${id}`, 'PUT', { nombre: null })).status, 400);
  assert.equal((await request('/libros/obtenerUno/incorrecto')).status, 400);
  assert.equal((await request('/libros/obtenerUno/000000000000000000000000')).status, 404);
  assert.equal((await request(`/libros/eliminar/${bookId}`, 'DELETE')).status, 200);
  assert.equal((await request(`/libros/obtenerUno/${bookId}`)).status, 404);
  assert.equal((await request(`/generos/eliminar/${id}`, 'DELETE')).status, 200);
  assert.equal((await request('/libros/obtenerVarios')).data.datos.length, 0);
});

test('la interfaz se sirve y las búsquedas externas rechazan entradas inválidas', async () => {
  const response = await fetch(base);
  assert.equal(response.status, 200);
  assert.match(await response.text(), /Lumbre · Biblioteca/);
  assert.equal((await request('/servicios/libros?q=')).status, 400);
  assert.equal((await request('/servicios/libros?q=uno&q=dos')).status, 400);
  assert.equal((await request('/servicios/libros/no-es-una-obra')).status, 400);
});
