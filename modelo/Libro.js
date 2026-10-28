const mongoose = require('mongoose');

const libroEsquema = new mongoose.Schema({
  nombre: {
    type: String,
    required: [true, 'El campo nombre es obligatorio'],
    trim: true
  },
  autor: { type: String, required: [true, 'El autor es obligatorio'], trim: true },
  genero: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Genero',
    required: [true, 'El campo genero es obligatorio (referencia ObjectId a Genero)']
  },
  ubicacion: {
    type: String,
    required: [true, 'El campo ubicacion es obligatorio'],
    trim: true
  },
  ejemplares: {
    type: Number,
    required: [true, 'El campo ejemplares es obligatorio'],
    min: [0, 'Los ejemplares no pueden ser negativos'],
    validate: { validator: Number.isInteger, message: 'Los ejemplares deben ser un número entero' }
  },
  fechaCreacion: {
    type: Date,
    default: Date.now
  }
});

const Libro = mongoose.model('Libro', libroEsquema);

module.exports = Libro;
