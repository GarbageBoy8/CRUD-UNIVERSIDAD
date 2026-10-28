const $ = (selector) => document.querySelector(selector);
const state = { libros: [], generos: [], vista: 'catalogo', token: sessionStorage.getItem('lumbre-token'), cargado: false };
let edicion = null;
let pendienteEliminar = null;
let discoveryRequest = 0;

const escapeHTML = (value) => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
const normalizar = (value) => String(value).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();

async function api(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(state.token ? { Authorization: `Bearer ${state.token}` } : {}) },
    signal: AbortSignal.timeout(12000)
  });
  const data = await response.json();
  if (!response.ok) {
    if ([401, 403].includes(response.status) && !url.startsWith('/auth')) {
      cerrarSesion();
      $('#login-error').textContent = 'Tu sesión terminó. Inicia sesión de nuevo.';
    }
    throw new Error(data.mensaje || 'No se pudo completar la solicitud');
  }
  return data;
}
const mensajeError = error => error.name === 'TimeoutError' ? 'La solicitud tardó demasiado. Vuelve a intentarlo.' : error instanceof TypeError ? 'No se pudo conectar con la biblioteca. Revisa que el servidor esté encendido.' : error.message;

function avisar(texto) {
  $('#notice').textContent = texto;
  $('#notice').hidden = false;
}
function abrirBiblioteca(usuario) {
  $('#login-screen').hidden = true;
  $('#workspace').hidden = false;
  $('#account-name').textContent = usuario || 'Biblioteca';
}
function cerrarSesion() {
  state.token = null;
  state.libros = [];
  state.generos = [];
  state.cargado = false;
  sessionStorage.removeItem('lumbre-token');
  sessionStorage.removeItem('lumbre-usuario');
  document.querySelectorAll('dialog[open]').forEach(dialog => dialog.close());
  $('#workspace').hidden = true;
  $('#login-screen').hidden = false;
  $('#login-form').reset();
  $('#login-error').textContent = '';
  $('#notice').hidden = true;
  $('#search').value = '';
  $('#genre-filter').value = '';
  cambiarVista('catalogo');
  $('#login-form [name="usuario"]').focus();
}

$('#login-form').addEventListener('submit', async event => {
  event.preventDefault();
  const button = event.submitter;
  button.disabled = true;
  $('#login-error').textContent = '';
  try {
    const body = Object.fromEntries(new FormData(event.currentTarget));
    const data = await api('/auth/login', { method: 'POST', body: JSON.stringify(body) });
    state.token = data.token;
    sessionStorage.setItem('lumbre-token', data.token);
    sessionStorage.setItem('lumbre-usuario', data.usuarioAutenticado);
    event.target.reset();
    abrirBiblioteca(data.usuarioAutenticado);
    await cargarCatalogo();
  } catch (error) { $('#login-error').textContent = mensajeError(error); }
  finally { button.disabled = false; }
});
$('#logout').addEventListener('click', cerrarSesion);

async function cargarCatalogo() {
  $('#retry').disabled = true;
  $('#add-button').disabled = true;
  try {
    const [libros, generos] = await Promise.all([api('/libros/obtenerVarios'), api('/generos/obtenerVarios')]);
    if (!state.token) return;
    state.libros = libros.datos;
    state.generos = generos.datos;
    state.cargado = true;
    $('#load-error').hidden = true;
    const filtro = $('#genre-filter').value;
    const opciones = state.generos.map(g => `<option value="${escapeHTML(g._id)}">${escapeHTML(g.nombre)}</option>`).join('');
    $('#genre-filter').innerHTML = '<option value="">Todos los géneros</option>' + opciones;
    $('#genre-filter').value = state.generos.some(g => g._id === filtro) ? filtro : '';
    $('#stat-books').textContent = state.libros.length;
    $('#stat-copies').textContent = state.libros.reduce((total, libro) => total + libro.ejemplares, 0);
    $('#stat-genres').textContent = state.generos.length;
    $('#nav-count').textContent = state.libros.length;
    renderLibros();
    renderGeneros();
    return true;
  } catch (error) {
    $('#load-error').hidden = false;
    $('#load-error-text').textContent = mensajeError(error);
    return false;
  } finally {
    $('#retry').disabled = false;
    $('#add-button').disabled = !state.cargado;
  }
}
$('#retry').addEventListener('click', cargarCatalogo);

function renderLibros() {
  const texto = normalizar($('#search').value.trim());
  const genero = $('#genre-filter').value;
  const libros = state.libros.filter(libro => normalizar(`${libro.nombre} ${libro.autor}`).includes(texto) && (!genero || libro.genero?._id === genero));
  $('#result-count').textContent = `(${libros.length})`;
  $('#book-list').innerHTML = libros.map((libro, index) => `
    <tr><td><div class="book-cell"><div class="book-cover" data-color="${index % 4}" aria-hidden="true">${escapeHTML(libro.nombre.charAt(0))}</div><div><button class="book-title" data-action="detail" data-id="${escapeHTML(libro._id)}">${escapeHTML(libro.nombre)}</button><span class="book-author">${escapeHTML(libro.autor)}</span></div></div></td>
    <td><span class="tag">${escapeHTML(libro.genero?.nombre || 'Sin género')}</span></td><td>${escapeHTML(libro.ubicacion)}</td>
    <td><span class="copies ${libro.ejemplares === 0 ? 'zero' : ''}">${libro.ejemplares === 0 ? 'Sin ejemplares' : `${libro.ejemplares} en colección`}</span></td>
    <td><div class="row-actions"><button class="text-button" data-action="edit" data-id="${escapeHTML(libro._id)}" aria-label="Editar ${escapeHTML(libro.nombre)}">Editar</button><button class="text-button delete" data-action="delete" data-id="${escapeHTML(libro._id)}" aria-label="Eliminar ${escapeHTML(libro.nombre)}">Eliminar</button></div></td></tr>`).join('');
  $('#empty-books').hidden = libros.length > 0;
  $('#empty-title').textContent = state.libros.length ? 'No encontramos esa historia.' : 'Una colección por comenzar.';
  $('#empty-description').textContent = state.libros.length ? 'Prueba con otro título, autor o género.' : 'Añade un género y registra tu primer libro.';
}
function renderGeneros() {
  $('#genre-list').innerHTML = state.generos.map((genero, index) => `
    <article class="genre-card"><p class="eyebrow">COLECCIÓN / ${String(index + 1).padStart(2, '0')}</p><h3>${escapeHTML(genero.nombre)}</h3><p>${escapeHTML(genero.descripcion || 'Un espacio para nuevas historias.')}</p>
    <div class="card-bottom"><span class="tag">${state.libros.filter(l => l.genero?._id === genero._id).length} títulos</span><div><button class="text-button" data-action="edit" data-id="${escapeHTML(genero._id)}" aria-label="Editar ${escapeHTML(genero.nombre)}">Editar</button><button class="text-button delete" data-action="delete" data-id="${escapeHTML(genero._id)}" aria-label="Eliminar ${escapeHTML(genero.nombre)}">Eliminar</button></div></div></article>`).join('');
  $('#empty-genres').hidden = state.generos.length > 0;
}
$('#search').addEventListener('input', renderLibros);
$('#genre-filter').addEventListener('change', renderLibros);

function cambiarVista(vista) {
  state.vista = vista;
  document.querySelectorAll('[data-view]').forEach(button => {
    const activa = button.dataset.view === vista;
    button.classList.toggle('active', activa);
    if (activa) button.setAttribute('aria-current', 'page'); else button.removeAttribute('aria-current');
  });
  ['catalogo', 'generos', 'descubrir'].forEach(nombre => { $(`#${nombre}-view`).hidden = nombre !== vista; });
  const textos = {
    catalogo: ['Catálogo', 'Tu próxima historia<br>empieza <em>aquí.</em>', 'Todos tus libros, cada uno en su lugar.', '+ Añadir libro'],
    generos: ['Géneros', 'Un lugar para<br>cada <em>historia.</em>', 'Organiza tu colección por géneros literarios.', '+ Añadir género'],
    descubrir: ['Descubrir', 'Abre la puerta<br>a otras <em>ideas.</em>', 'Encuentra tu próxima lectura.', '']
  }[vista];
  $('#breadcrumb').textContent = textos[0];
  $('#page-title').innerHTML = textos[1];
  $('#page-description').textContent = textos[2];
  $('#add-button').textContent = textos[3];
  $('#add-button').hidden = vista === 'descubrir';
  $('#notice').hidden = true;
}
document.querySelectorAll('[data-view]').forEach(button => button.addEventListener('click', () => cambiarVista(button.dataset.view)));

function abrirEditor(tipo, dato = null) {
  if (tipo === 'libros' && !state.generos.length) {
    cambiarVista('generos');
    avisar('Primero crea un género para poder añadir libros.');
    abrirEditor('generos');
    return;
  }
  edicion = { tipo, id: dato?._id };
  const form = $('#editor-form');
  form.reset();
  const libro = tipo === 'libros';
  $('#editor-title').textContent = `${dato ? 'Editar' : 'Añadir'} ${libro ? 'libro' : 'género'}`;
  $('#save-button').textContent = `Guardar ${libro ? 'libro' : 'género'}`;
  $('#name-label').firstChild.textContent = libro ? 'Título' : 'Nombre';
  $('#book-fields').hidden = !libro;
  $('#description-label').hidden = libro;
  $('#editor-error').textContent = '';
  ['autor', 'genero', 'ubicacion', 'ejemplares'].forEach(campo => {
    form.elements[campo].disabled = !libro;
    form.elements[campo].required = libro;
  });
  form.elements.descripcion.disabled = libro;
  form.elements.genero.innerHTML = state.generos.map(g => `<option value="${escapeHTML(g._id)}">${escapeHTML(g.nombre)}</option>`).join('');
  if (dato) {
    for (const campo of ['nombre', 'autor', 'ubicacion', 'ejemplares', 'descripcion']) form.elements[campo].value = dato[campo] ?? '';
    if (libro) form.elements.genero.value = dato.genero?._id || '';
  }
  $('#editor').showModal();
}
$('#add-button').addEventListener('click', () => abrirEditor(state.vista === 'generos' ? 'generos' : 'libros'));
document.querySelectorAll('[data-close]').forEach(button => button.addEventListener('click', () => document.getElementById(button.dataset.close).close()));
$('#editor-form').addEventListener('submit', async event => {
  event.preventDefault();
  const button = $('#save-button');
  button.disabled = true;
  $('#editor-error').textContent = '';
  try {
    const datos = Object.fromEntries(new FormData(event.target));
    if (edicion.tipo === 'libros') datos.ejemplares = Number(datos.ejemplares);
    await api(`/${edicion.tipo}/${edicion.id ? `baja/${edicion.id}` : 'falta'}`, { method: edicion.id ? 'PUT' : 'POST', body: JSON.stringify(datos) });
    $('#editor').close();
    const actualizado = await cargarCatalogo();
    if (state.token) avisar(actualizado ? 'Guardado. Tu colección está al día.' : 'Guardado, pero no pudimos recargar el catálogo. Pulsa «Volver a intentar».');
  } catch (error) { $('#editor-error').textContent = mensajeError(error); }
  finally { button.disabled = false; }
});

async function accionCatalogo(event, tipo) {
  const button = event.target.closest('button[data-action]');
  if (!button) return;
  const dato = state[tipo].find(item => item._id === button.dataset.id);
  if (!dato) return;
  if (button.dataset.action === 'edit') abrirEditor(tipo, dato);
  if (button.dataset.action === 'delete') {
    pendienteEliminar = { tipo, id: dato._id };
    $('#delete-title').textContent = `Eliminar ${tipo === 'libros' ? 'libro' : 'género'}`;
    $('#delete-text').textContent = `Vas a eliminar «${dato.nombre}». Esta acción no se puede deshacer.`;
    $('#delete-error').textContent = '';
    $('#delete-dialog').showModal();
  }
  if (button.dataset.action === 'detail') {
    button.disabled = true;
    try {
      const { datos } = await api(`/libros/obtenerUno/${dato._id}`);
      mostrarDetalle(datos.nombre, `${datos.autor}\n\nGénero: ${datos.genero?.nombre || 'Sin género'}\nEstante: ${datos.ubicacion}\nEjemplares: ${datos.ejemplares}`);
    } catch (error) { if (state.token) avisar(mensajeError(error)); }
    finally { button.disabled = false; }
  }
}
$('#book-list').addEventListener('click', event => accionCatalogo(event, 'libros'));
$('#genre-list').addEventListener('click', event => accionCatalogo(event, 'generos'));
$('#confirm-delete').addEventListener('click', async event => {
  const button = event.currentTarget;
  button.disabled = true;
  try {
    await api(`/${pendienteEliminar.tipo}/eliminar/${pendienteEliminar.id}`, { method: 'DELETE' });
    $('#delete-dialog').close();
    const actualizado = await cargarCatalogo();
    if (state.token) avisar(actualizado ? 'Registro eliminado del catálogo.' : 'Registro eliminado. Pulsa «Volver a intentar» para actualizar el catálogo.');
  } catch (error) { $('#delete-error').textContent = mensajeError(error); }
  finally { button.disabled = false; }
});
function mostrarDetalle(titulo, texto) {
  $('#details-title').textContent = titulo;
  $('#details-text').textContent = texto;
  $('#details').showModal();
}

$('#discovery-form').addEventListener('submit', async event => {
  event.preventDefault();
  const request = ++discoveryRequest;
  const button = event.submitter;
  button.disabled = true;
  $('#discovery-status').textContent = 'Buscando historias en Open Library…';
  $('#discovery-list').replaceChildren();
  try {
    const q = new FormData(event.target).get('q').trim();
    const { datos } = await api(`/servicios/libros?q=${encodeURIComponent(q)}`);
    if (request !== discoveryRequest) return;
    $('#discovery-status').textContent = datos.length ? `${datos.length} obras encontradas · Fuente: Open Library` : 'No hay resultados. Prueba con otro título o autor.';
    $('#discovery-list').innerHTML = datos.map(libro => `<article class="genre-card"><p class="eyebrow">${escapeHTML(libro.anio || 'SIN FECHA')}</p><h3>${escapeHTML(libro.nombre)}</h3><p>${escapeHTML(libro.autor)}</p><div class="card-bottom"><button class="text-button" data-external-id="${escapeHTML(libro.id)}">Leer más ↗</button></div></article>`).join('');
  } catch (error) { $('#discovery-status').textContent = mensajeError(error); }
  finally { button.disabled = false; }
});
$('#discovery-list').addEventListener('click', async event => {
  const button = event.target.closest('[data-external-id]');
  if (!button) return;
  button.disabled = true;
  try {
    const { datos } = await api(`/servicios/libros/${encodeURIComponent(button.dataset.externalId)}`);
    mostrarDetalle(datos.nombre, datos.resumen);
  } catch (error) { $('#discovery-status').textContent = mensajeError(error); }
  finally { button.disabled = false; }
});

if (state.token) {
  abrirBiblioteca(sessionStorage.getItem('lumbre-usuario'));
  cargarCatalogo();
}
