const mongoose = require('mongoose');
require('dotenv').config({ path: require('node:path').join(__dirname, '../.env'), quiet: true });

module.exports = async () => {
  if (!process.env.MONGODB_URI) throw new Error('Configura MONGODB_URI en .env');
  // La copia nunca utiliza la base del proyecto original, aunque comparta servidor.
  await mongoose.connect(process.env.MONGODB_URI, {
    dbName: 'lumbre_biblioteca', serverSelectionTimeoutMS: 5000
  });
  console.log('Biblioteca conectada a MongoDB');
};
