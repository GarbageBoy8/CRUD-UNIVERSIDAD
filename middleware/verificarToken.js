const jwt = require('jwt-simple');

module.exports = (req, res, next) => {
  if (!process.env.JWT_SECRET) return res.status(500).json({ mensaje: 'Falta configurar JWT_SECRET' });
  const coincidencia = /^Bearer\s+(\S+)$/i.exec(req.get('Authorization') || '');
  if (!coincidencia) return res.status(401).json({ mensaje: 'Envía Authorization: Bearer <token>' });
  try {
    const payload = jwt.decode(coincidencia[1], process.env.JWT_SECRET, false, 'HS256');
    if (typeof payload.usuario !== 'string' || !payload.usuario || !Number.isInteger(payload.iat) ||
        !Number.isInteger(payload.exp) || payload.exp <= payload.iat) {
      return res.status(401).json({ mensaje: 'El token no contiene los datos de sesión requeridos' });
    }
    if (payload.exp <= Math.floor(Date.now() / 1000)) return res.status(403).json({ mensaje: 'token expirado' });
    req.usuario = payload;
    next();
  } catch (error) {
    const expirado = error.message === 'Token expired';
    res.status(expirado ? 403 : 401).json({ mensaje: expirado ? 'token expirado' : 'Token inválido' });
  }
};
