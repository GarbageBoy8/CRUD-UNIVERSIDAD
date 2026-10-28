const mongoose = require('mongoose');
const conectar = require('./config/db');
const Genero = require('./modelo/Genero');
const Libro = require('./modelo/Libro');

const generos = [
  { nombre: 'Narrativa', descripcion: 'Historias para habitar otras vidas.' },
  { nombre: 'Poesía', descripcion: 'El mundo, verso a verso.' },
  { nombre: 'Ciencia', descripcion: 'Preguntas que abren nuevos caminos.' },
  { nombre: 'Ensayo', descripcion: 'Ideas para mirar de otra manera.' }
];
const libros = [
  { nombre: 'Pedro Páramo', autor: 'Juan Rulfo', genero: 'Narrativa', ubicacion: 'A-01', ejemplares: 4 },
  { nombre: 'Cien años de soledad', autor: 'Gabriel García Márquez', genero: 'Narrativa', ubicacion: 'A-02', ejemplares: 3 },
  { nombre: 'La casa de los espíritus', autor: 'Isabel Allende', genero: 'Narrativa', ubicacion: 'A-03', ejemplares: 2 },
  { nombre: 'Piedra de sol', autor: 'Octavio Paz', genero: 'Poesía', ubicacion: 'B-01', ejemplares: 2 },
  { nombre: 'Desolación', autor: 'Gabriela Mistral', genero: 'Poesía', ubicacion: 'B-02', ejemplares: 0 },
  { nombre: 'Cosmos', autor: 'Carl Sagan', genero: 'Ciencia', ubicacion: 'C-01', ejemplares: 3 },
  { nombre: 'Una habitación propia', autor: 'Virginia Woolf', genero: 'Ensayo', ubicacion: 'D-01', ejemplares: 2 },
  { nombre: 'El laberinto de la soledad', autor: 'Octavio Paz', genero: 'Ensayo', ubicacion: 'D-02', ejemplares: 1 }
];

async function cargarDatos() {
  try {
    await conectar();
    const ids = {};
    for (const genero of generos) {
      const dato = await Genero.findOneAndUpdate({ nombre: genero.nombre }, { $setOnInsert: genero }, { upsert: true, new: true });
      ids[genero.nombre] = dato._id;
    }
    for (const libro of libros) {
      await Libro.updateOne({ nombre: libro.nombre, autor: libro.autor }, {
        $setOnInsert: { ...libro, genero: ids[libro.genero] }
      }, { upsert: true, runValidators: true });
    }
    console.log('Catálogo inicial listo: 4 géneros y 8 libros. Los registros existentes se conservan.');
  } catch {
    console.error('No se pudo cargar el catálogo. Revisa la conexión y los permisos de MongoDB.');
    process.exitCode = 1;
  } finally {
    await mongoose.disconnect();
  }
}
if (require.main === module) cargarDatos();
module.exports = { generos, libros };
