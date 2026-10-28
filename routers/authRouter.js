const express = require('express');
const router = express.Router();
const { generarTokenMiddleware } = require('../middleware/generarToken');

// Endpoint para generar el token con usuario y contraseña (iat y exp de 1 hora con DATE)
router.post('/login', generarTokenMiddleware);
router.post('/token', generarTokenMiddleware);

module.exports = router;
