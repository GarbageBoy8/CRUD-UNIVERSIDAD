const router = require('express').Router();
const { buscar, detalle } = require('../control/servicioControl');
router.get('/libros', buscar);
router.get('/libros/:id', detalle);
module.exports = router;
