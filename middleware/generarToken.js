const jwt = require('jwt-simple');

const crearToken = (usuario) => {
  if (!process.env.JWT_SECRET) throw new Error('Configura JWT_SECRET en .env');
  const ahora = Math.floor(Date.now() / 1000);
  return jwt.encode({ usuario, iat: ahora, exp: ahora + 3600 }, process.env.JWT_SECRET, 'HS256');
};

const generarTokenMiddleware = (req, res) => {
  const { usuario, contrasena } = req.body || {};
  if (!process.env.AUTH_USER || !process.env.AUTH_PASSWORD || !process.env.JWT_SECRET) {
    return res.status(503).json({ mensaje: 'Falta configurar el acceso a la biblioteca' });
  }
  if (typeof usuario !== 'string' || typeof contrasena !== 'string' || !usuario || !contrasena) {
    return res.status(400).json({ mensaje: 'Escribe tu usuario y contraseña' });
  }
  if (usuario !== process.env.AUTH_USER || contrasena !== process.env.AUTH_PASSWORD) {
    return res.status(401).json({ mensaje: 'Usuario o contraseña incorrectos' });
  }
  return res.json({ token: crearToken(usuario), usuarioAutenticado: usuario, duracion: '1 hora' });
};
module.exports = { crearToken, generarTokenMiddleware };
