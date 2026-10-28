const express = require('express');
const router = express.Router();
const verificarToken = require('../middleware/verificarToken');
const {
  crearGenero,
  consultarGeneros,
  consultarGeneroPorId,
  actualizarGenero,
  eliminarGenero
} = require('../control/generoControl');

// Proteger todas las transacciones del CRUD con el middleware de verificación de token
router.use(verificarToken);

// Rutas del CRUD de Géneros (1:N)
router.post('/falta', crearGenero);
router.put('/baja/:id', actualizarGenero);
router.delete('/eliminar/:id', eliminarGenero);
router.get('/obtenerUno/:id', consultarGeneroPorId);
router.get('/obtenerVarios', consultarGeneros);

module.exports = router;
