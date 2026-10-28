const mongoose = require('mongoose');

const generoEsquema = new mongoose.Schema({
  nombre: {
    type: String,
    required: [true, 'El campo nombre del género es obligatorio'],
    trim: true,
    unique: true
  },
  descripcion: {
    type: String,
    trim: true,
    default: ''
  },
  fechaCreacion: {
    type: Date,
    default: Date.now
  }
}, {
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// Relación virtual 1:N (Un género tiene N libros en Mongoose)
generoEsquema.virtual('libros', {
  ref: 'Libro',
  localField: '_id',
  foreignField: 'genero'
});

const Genero = mongoose.model('Genero', generoEsquema);

module.exports = Genero;
