# Lumbre · Biblioteca

Copia independiente de `empresa`, adaptada de un cine a una biblioteca. Mantiene Express, Mongoose, JWT, Axios y la organización por modelos, controles, routers y servicios. La interfaz está en `public/`, sin dependencias adicionales.

## Iniciar

Después de clonar el repositorio, entra en su carpeta y prepara la configuración:

```sh
npm ci
cp -n .env.example .env
```

Configura `JWT_SECRET` en `.env` con una clave aleatoria y cambia las credenciales de ejemplo antes de compartir el acceso. Después:

```sh
docker compose up -d
npm run seed
npm start
```

Abre **http://localhost:8021**.

- Usuario local: `biblioteca`
- Contraseña local: `LumbreLocal2026!`
- Si se copia el proyecto a otro equipo: ejecuta `npm ci`, copia `.env.example` a `.env` y reemplaza `JWT_SECRET` por una clave aleatoria.
- `.env` y `node_modules` están excluidos de Git. `npm run seed` añade los ejemplos que falten sin sobrescribir registros existentes.

MongoDB usa el puerto local **27018**, la base **lumbre_biblioteca** y el volumen Docker **lumbre-biblioteca_lumbre-data**. `config/db.js` fija el nombre de la base para separarla del cine. Si prefieres otro servidor MongoDB, cambia `MONGODB_URI` en `.env`. No es necesario Docker si ya tienes otro MongoDB disponible.

Para detener la app pulsa `Ctrl+C`. Para detener MongoDB conservando los datos:

```sh
docker compose stop
```

## Uso

1. Inicia sesión y abre **Géneros** para crear o editar las clasificaciones.
2. En **Catálogo**, añade libros con título, autor, género, estante y número de ejemplares.
3. Busca por título o autor, filtra por género y pulsa un título para ver su ficha.
4. Edita o elimina registros. El borrado pide confirmación; un género con libros asociados no puede eliminarse.
5. **Descubrir** consulta obras en Open Library. Los resultados externos no se guardan automáticamente en la biblioteca.

La interfaz incluye diseño móvil, navegación con teclado, mensajes de error, estados vacíos y formularios accesibles. La sesión dura una hora y se conserva en la pestaña; el token no contiene la contraseña.

## API

Resumen en `GET /api`. `POST /auth/login` recibe `{ "usuario": "...", "contrasena": "..." }` y devuelve `token`. El CRUD requiere `Authorization: Bearer <token>`.

| Operación | Libros | Géneros |
| --- | --- | --- |
| Crear | `POST /libros/falta` | `POST /generos/falta` |
| Listar | `GET /libros/obtenerVarios` | `GET /generos/obtenerVarios` |
| Consultar uno | `GET /libros/obtenerUno/:id` | `GET /generos/obtenerUno/:id` |
| Actualizar | `PUT /libros/baja/:id` | `PUT /generos/baja/:id` |
| Eliminar | `DELETE /libros/eliminar/:id` | `DELETE /generos/eliminar/:id` |

Se conservan los sufijos de las rutas del ejercicio original. Un género tiene muchos libros; al consultar se incluyen las referencias relacionadas.

Libro:

```json
{ "nombre": "Pedro Páramo", "autor": "Juan Rulfo", "genero": "Narrativa", "ubicacion": "A-01", "ejemplares": 4 }
```

`genero` acepta el nombre de un género existente o su ObjectId. `ejemplares` debe ser un entero mayor o igual a cero. Género: `{ "nombre": "Narrativa", "descripcion": "Historias para habitar otras vidas" }`.

Las respuestas del CRUD usan `{ mensaje, datos }`. Los datos inválidos producen 400; las referencias inexistentes al consultar, 404; un nombre de género duplicado en una actualización, 409; MongoDB inaccesible, 503. El acceso sin token devuelve 401 y el token vencido, 403.

Consultas externas con Axios:

- `GET /servicios/libros?q=termino`
- `GET /servicios/libros/OL45804W`

Usan los contratos públicos de [búsqueda](https://openlibrary.org/dev/docs/api/search) y [obras](https://openlibrary.org/dev/docs/api/books) de Open Library. La descripción es opcional. El servicio devuelve 502 si el proveedor falla y 404 si no encuentra la obra.

## Verificación

Con MongoDB local encendido:

```sh
npm test
```

Las pruebas crean y eliminan una base temporal aleatoria, sin modificar la biblioteca. Cubren autenticación, expiración, CRUD completo, relación 1:N y entradas inválidas. `TEST_MONGODB_URI` permite señalar otro MongoDB para pruebas.

Para incluir las comprobaciones de Axios frente a una simulación de Open Library, con Postman CLI instalado, ejecuta en una terminal:

```sh
postman simulation run postman/simulations/openlibrary.sim.yaml --port 4901 --output ndjson
```

Y en otra:

```sh
OPENLIBRARY_TEST_URL=http://127.0.0.1:4901/openlibrary npm test
```

Sin esa variable se omite únicamente la prueba del proveedor externo. La simulación verifica búsquedas, fichas sin descripción y respuestas de error; no garantiza disponibilidad del proveedor real.

Verificado durante la adaptación: cuatro pruebas automatizadas con MongoDB real y proveedor simulado, más recorrido de navegador con altas, edición, borrados, búsqueda, ficha, escape HTML, bloqueo de géneros con libros y presentación móvil. El Atlas original no aceptó la conexión; esta copia quedó configurada con MongoDB local.

## Entrega de laboratorio SDD

El reporte final sigue los ocho criterios en orden y excluye la UI/UX de Lumbre.
La especificación de la iteración está en `docs/ESPECIFICACION-SDD.md`: se redactó
antes de reorganizar las capas y reforzar la verificación JWT, partiendo de una
versión existente. Las reglas de ambos recursos se centralizan ahora en
`service/catalogoService.js`; los controladores se ocupan de HTTP. El middleware
acepta exclusivamente Bearer HS256 con usuario, iat y exp válidos.

Ver `reporte/LEEME.txt`: 51 solicitudes / 102 aserciones Postman, cuatro capturas
Desktop, 51 capturas CLI y resultados JSON. Solo los casos 22–25 simulan el
proveedor; 50–51 consultan Open Library público. Los tokens activos están ocultos.
La colección conserva las aserciones efectivamente ejecutadas y ejemplos de
respuesta. No hace falta publicar un workspace para ejecutar el archivo local.

Limitaciones: administrador local único, listados sin paginación y comprobación
secuencial de referencias. Antes de admitir escritores concurrentes se necesitan
transacciones para la integridad entre colecciones; esta práctica no afirma
haber validado concurrencia ni un despliegue público.
