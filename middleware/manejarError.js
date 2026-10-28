module.exports = (error, req, res, next) => {
  if (res.headersSent) return next(error);
  if (error.code === 11000) return res.status(409).json({ mensaje: 'Ya existe un género con ese nombre' });
  if (error.name === 'ValidationError' || error.name === 'CastError') {
    return res.status(400).json({ mensaje: 'Los datos enviados no son válidos' });
  }
  const status = error.status || 500;
  const mensaje = error.type === 'entity.parse.failed' ? 'El cuerpo JSON no es válido'
    : status < 500 ? error.message : 'No se pudo completar la solicitud';
  res.status(status).json({ mensaje });
};
