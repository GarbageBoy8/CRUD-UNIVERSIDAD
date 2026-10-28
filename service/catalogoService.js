const mongoose = require('mongoose');
const Genero = require('../modelo/Genero');
const Libro = require('../modelo/Libro');

function rechazar(status, mensaje) {
  throw Object.assign(new Error(mensaje), { status });
}
function validarId(id) {
  if (!mongoose.isObjectIdOrHexString(id)) rechazar(400, 'El ID proporcionado no es un ObjectId válido');
}
function encontrado(documento, recurso) {
  if (!documento) rechazar(404, `${recurso} no encontrado con el ID proporcionado`);
  return documento;
}
function validarCambios(datos, permitidos) {
  const campos = Object.keys(datos || {});
  if (!campos.length || campos.some(campo => !permitidos.includes(campo))) {
    rechazar(400, 'Envía al menos un campo editable válido para actualizar');
  }
}
function validarTexto(datos, campos, obligatorio) {
  for (const campo of campos) {
    if ((obligatorio || campo in datos) && (typeof datos[campo] !== 'string' || !datos[campo].trim())) {
      rechazar(400, `El campo ${campo} debe ser texto no vacío`);
    }
  }
}
async function resolverGenero(valor) {
  const genero = mongoose.isObjectIdOrHexString(valor)
    ? await Genero.findById(valor) : await Genero.findOne({ nombre: valor.trim() });
  if (!genero) rechazar(400, 'El género indicado no existe; crea primero el género');
  return genero._id;
}
function validarGenero(datos, obligatorio) {
  validarTexto(datos, ['nombre'], obligatorio);
  if ('descripcion' in datos && typeof datos.descripcion !== 'string') rechazar(400, 'La descripción debe ser texto');
}
async function crearGenero(datos = {}) {
  validarGenero(datos, true);
  if (await Genero.exists({ nombre: datos.nombre.trim() })) rechazar(400, 'El género ya existe');
  return Genero.create({ nombre: datos.nombre, descripcion: datos.descripcion });
}
async function consultarGeneros() { return Genero.find().populate('libros'); }
async function consultarGeneroPorId(id) {
  validarId(id);
  return encontrado(await Genero.findById(id).populate('libros'), 'Género');
}
async function actualizarGenero(id, datos = {}) {
  validarId(id);
  validarCambios(datos, ['nombre', 'descripcion']);
  validarGenero(datos, false);
  return encontrado(await Genero.findByIdAndUpdate(id, { $set: datos }, { new: true, runValidators: true }), 'Género');
}
async function eliminarGenero(id) {
  validarId(id);
  // shortcut: comprobación secuencial local, usar transacciones antes de admitir escritores concurrentes.
  const cantidad = await Libro.countDocuments({ genero: id });
  if (cantidad) rechazar(400, `No se puede eliminar el género porque tiene ${cantidad} libro(s) asociado(s)`);
  return encontrado(await Genero.findByIdAndDelete(id), 'Género');
}
function validarLibro(datos, obligatorio) {
  validarTexto(datos, ['nombre', 'autor', 'genero', 'ubicacion'], obligatorio);
  if ((obligatorio || 'ejemplares' in datos) && (!Number.isInteger(datos.ejemplares) || datos.ejemplares < 0)) {
    rechazar(400, 'Los ejemplares deben ser un entero no negativo');
  }
}
async function crearLibro(datos = {}) {
  validarLibro(datos, true);
  const { nombre, autor, ubicacion, ejemplares } = datos;
  const genero = await resolverGenero(datos.genero);
  const libro = await Libro.create({ nombre, autor, ubicacion, ejemplares, genero });
  return libro.populate('genero');
}
async function consultarLibros() { return Libro.find().populate('genero'); }
async function consultarLibroPorId(id) {
  validarId(id);
  return encontrado(await Libro.findById(id).populate('genero'), 'Libro');
}
async function actualizarLibro(id, datos = {}) {
  validarId(id);
  validarCambios(datos, ['nombre', 'autor', 'genero', 'ubicacion', 'ejemplares']);
  validarLibro(datos, false);
  const cambios = { ...datos };
  if ('genero' in cambios) cambios.genero = await resolverGenero(cambios.genero);
  return encontrado(await Libro.findByIdAndUpdate(id, { $set: cambios }, {
    new: true, runValidators: true
  }).populate('genero'), 'Libro');
}
async function eliminarLibro(id) {
  validarId(id);
  return encontrado(await Libro.findByIdAndDelete(id), 'Libro');
}
module.exports = { crearGenero, consultarGeneros, consultarGeneroPorId, actualizarGenero, eliminarGenero,
  crearLibro, consultarLibros, consultarLibroPorId, actualizarLibro, eliminarLibro };
