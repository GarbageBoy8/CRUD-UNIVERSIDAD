const servicio = require('../service/catalogoService');

async function crearGenero(req, res) {
  const datos = await servicio.crearGenero(req.body);
  res.status(201).json({ mensaje: 'Género creado exitosamente', datos });
}
async function consultarGeneros(req, res) {
  const datos = await servicio.consultarGeneros();
  res.status(200).json({ mensaje: 'Listado obtenido exitosamente', datos });
}
async function consultarGeneroPorId(req, res) {
  const datos = await servicio.consultarGeneroPorId(req.params.id);
  res.status(200).json({ mensaje: 'Género obtenido exitosamente', datos });
}
async function actualizarGenero(req, res) {
  const datos = await servicio.actualizarGenero(req.params.id, req.body);
  res.status(200).json({ mensaje: 'Género actualizado exitosamente', datos });
}
async function eliminarGenero(req, res) {
  const datos = await servicio.eliminarGenero(req.params.id);
  res.status(200).json({ mensaje: 'Género eliminado exitosamente', datos });
}
module.exports = { crearGenero, consultarGeneros, consultarGeneroPorId, actualizarGenero, eliminarGenero };
