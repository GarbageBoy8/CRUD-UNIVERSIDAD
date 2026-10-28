const path = require('node:path');
const { randomUUID } = require('node:crypto');
const fs = require('node:fs');
const root = path.resolve(__dirname, '../..');
process.env.AUTH_USER = 'practica';
process.env.AUTH_PASSWORD = 'PracticaCRUD2026!';
process.env.JWT_SECRET = randomUUID();
const mongoose = require(path.join(root, 'node_modules/mongoose'));
const jwt = require(path.join(root, 'node_modules/jwt-simple'));
const app = require(path.join(root, 'app'));
const dbName = `lumbre_reporte_${randomUUID().replaceAll('-', '')}`;
let server;
async function stop() {
  if (server) await new Promise(resolve => server.close(resolve));
  if (mongoose.connection.readyState === 1) await mongoose.connection.dropDatabase();
  await mongoose.disconnect();
  process.exit();
}
process.on('SIGINT', stop);
process.on('SIGTERM', stop);
(async () => {
  await mongoose.connect('mongodb://127.0.0.1:27018', { dbName, serverSelectionTimeoutMS: 5000 });
  await mongoose.model('Genero').init();
  const port = Number(process.env.REPORTE_PORT) || 8031;
  fs.writeFileSync(`/tmp/lumbre-reporte-expirado-${port}.txt`, jwt.encode({ usuario: 'practica', exp: 1 }, process.env.JWT_SECRET), { mode: 0o600 });
  server = app.listen(port, '127.0.0.1', () => console.log(`API original de Lumbre en http://127.0.0.1:${port}; base temporal independiente.`));
})().catch(error => { console.error(error.name); process.exit(1); });
