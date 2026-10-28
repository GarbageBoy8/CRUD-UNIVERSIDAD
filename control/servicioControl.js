const { buscarLibros, obtenerDetalleLibro } = require('../service/libroService');

async function buscar(req, res) {
  const q = req.query.q === undefined ? 'literatura' : req.query.q;
  if (typeof q !== 'string' || !q.trim() || q.length > 200) {
    return res.status(400).json({ mensaje: 'Escribe una búsqueda de entre 1 y 200 caracteres' });
  }
  try {
    const datos = await buscarLibros(q.trim());
    res.json({ datos, total: datos.length });
  } catch {
    res.status(502).json({ mensaje: 'Open Library no está disponible. Vuelve a intentarlo más tarde.' });
  }
}
async function detalle(req, res) {
  if (!/^OL\d+W$/.test(req.params.id)) return res.status(400).json({ mensaje: 'Identificador de obra no válido' });
  try {
    res.json({ datos: await obtenerDetalleLibro(req.params.id) });
  } catch (error) {
    const status = error.response?.status === 404 ? 404 : 502;
    res.status(status).json({ mensaje: status === 404 ? 'Obra no encontrada' : 'No se pudo consultar la obra en Open Library' });
  }
}
module.exports = { buscar, detalle };
