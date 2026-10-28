const express = require('express');
const router = express.Router();
const verificarToken = require('../middleware/verificarToken');
const {
  crearLibro,
  actualizarLibro,
  eliminarLibro,
  consultarLibroPorId,
  consultarLibros
} = require('../control/libroControl');

// Proteger todas las transacciones del CRUD con el middleware de verificación de token
router.use(verificarToken);

// Rutas del CRUD de libros
router.post('/falta', crearLibro);
router.put('/baja/:id', actualizarLibro);
router.delete('/eliminar/:id', eliminarLibro);
router.get('/obtenerUno/:id', consultarLibroPorId);
router.get('/obtenerVarios', consultarLibros);

module.exports = router;
