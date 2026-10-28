const express = require('express');
const path = require('node:path');
require('dotenv').config({ path: path.join(__dirname, '.env'), quiet: true });
const mongoose = require('mongoose');
const conectar = require('./config/db');
const app = express();

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));
app.get('/api', (req, res) => res.json({
  sistema: 'Lumbre · Biblioteca',
  relacion: 'Un género tiene muchos libros',
  auth: 'POST /auth/login { usuario, contrasena }',
  recursos: ['/libros', '/generos'],
  operaciones: ['POST /falta', 'GET /obtenerVarios', 'GET /obtenerUno/:id', 'PUT /baja/:id', 'DELETE /eliminar/:id'],
  servicios: ['GET /servicios/libros?q=termino', 'GET /servicios/libros/:id']
}));
app.use('/auth', require('./routers/authRouter'));
app.use(['/libros', '/generos'], (req, res, next) => {
  if (mongoose.connection.readyState !== 1) {
    return res.status(503).json({ mensaje: 'La biblioteca no puede conectar con su base de datos. Intenta de nuevo en unos momentos.' });
  }
  next();
});
app.use('/libros', require('./routers/libroRouter'));
app.use('/generos', require('./routers/generoRouter'));
app.use('/servicios', require('./routers/servicioRouter'));
app.use(require('./middleware/manejarError'));

if (require.main === module) {
  const port = Number(process.env.PORT) || 8021;
  app.listen(port, '127.0.0.1', () => console.log(`Lumbre: http://localhost:${port}`));
  conectar().catch(() => console.warn('Revisa MONGODB_URI y el acceso a MongoDB para habilitar el catálogo.'));
}
module.exports = app;
