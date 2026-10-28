const axios = require('axios');
const cliente = axios.create({
  baseURL: process.env.OPENLIBRARY_API_URL || 'https://openlibrary.org',
  timeout: 8000,
  headers: { Accept: 'application/json' }
});

const buscarLibros = async (termino = 'literatura') => {
  const { data } = await cliente.get('/search.json', {
    params: { q: termino, limit: 12, fields: 'key,title,author_name,first_publish_year' }
  });
  return (data.docs || []).map(libro => ({
    id: libro.key.replace('/works/', ''), nombre: libro.title,
    autor: (libro.author_name || []).join(', ') || 'Autor sin registrar',
    anio: libro.first_publish_year || null
  }));
};

const obtenerDetalleLibro = async (id) => {
  const { data } = await cliente.get(`/works/${id}.json`);
  return {
    id, nombre: data.title,
    resumen: typeof data.description === 'string' ? data.description : data.description?.value || 'Esta obra no tiene una descripción disponible.'
  };
};
module.exports = { buscarLibros, obtenerDetalleLibro };
