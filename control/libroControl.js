const servicio = require('../service/catalogoService');

async function crearLibro(req, res) {
  const datos = await servicio.crearLibro(req.body);
  res.status(201).json({ mensaje: 'Libro creado exitosamente', datos });
}
async function consultarLibros(req, res) {
  const datos = await servicio.consultarLibros();
  res.status(200).json({ mensaje: 'Listado obtenido exitosamente', datos });
}
async function consultarLibroPorId(req, res) {
  const datos = await servicio.consultarLibroPorId(req.params.id);
  res.status(200).json({ mensaje: 'Libro obtenido exitosamente', datos });
}
async function actualizarLibro(req, res) {
  const datos = await servicio.actualizarLibro(req.params.id, req.body);
  res.status(200).json({ mensaje: 'Libro actualizado exitosamente', datos });
}
async function eliminarLibro(req, res) {
  const datos = await servicio.eliminarLibro(req.params.id);
  res.status(200).json({ mensaje: 'Libro eliminado exitosamente', datos });
}
module.exports = { crearLibro, consultarLibros, consultarLibroPorId, actualizarLibro, eliminarLibro };
