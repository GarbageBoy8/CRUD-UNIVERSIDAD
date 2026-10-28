# Especificación SDD — Lumbre, iteración de entrega

Versión 1.1. Especificación registrada el 28 de octubre de 2026, antes de implementar la reorganización de capas y el endurecimiento JWT de esta iteración. La portada conserva la fecha de entrega solicitada; no representa la fecha de ejecución.

## Contexto y secuencia de trabajo

El punto de partida es una aplicación existente, adaptada del ejercicio `empresa`. No hay evidencia de que se redactaran especificaciones antes de esa primera implementación. Esta iteración aplica SDD de forma explícita: (1) definir este contrato y criterios de aceptación, (2) implementar los cambios contra el contrato, (3) probar con MongoDB real y Postman, (4) contrastar resultados y documentar límites. No se atribuye una cronología inexistente al trabajo anterior.

## Requerimientos funcionales y aceptación

- RF01: login válido entrega JWT HS256, usuario, iat y exp de 3600 segundos; no contraseña. Credenciales ausentes: 400; incorrectas: 401.
- RF02: toda operación de libros y géneros exige Authorization: Bearer <token>. Firma incorrecta, formato incorrecto o claims incompletos: 401; expirado: 403. Ningún rechazo debe ejecutar una escritura.
- RF03: altas, consultas generales y por ID, cambios y bajas de géneros. Éxito: 201 al crear y 200 en las demás. Nombre único, no vacío; descripción opcional de texto.
- RF04: las mismas cinco operaciones para libros. Nombre, autor, género, ubicación y ejemplares son obligatorios al crear. Ejemplares es entero >= 0.
- RF05: cada libro referencia exactamente un género existente; un género puede tener cero o varios libros. Consulta de libros puebla género y consulta de géneros puebla libros.
- RF06: no eliminar géneros que tengan libros, respuesta 400. Borrar primero los libros permite eliminar su género.
- RF07: servicio Axios consulta Open Library, adapta búsqueda y detalle; 404 externo se propaga en detalle, otros fallos se traducen a 502. No se importan automáticamente obras externas a MongoDB.
- RF08: entrada JSON inválida devuelve 400; ObjectId mal formado 400; ID válido inexistente 404. Actualización vacía o con campos desconocidos: 400.

## Reglas de negocio

RN01: nombre de género se recorta y es único, sensible a mayúsculas. Alta duplicada detectada antes del insert: 400; conflicto de índice o renombrado duplicado: 409.
RN02: género de libro admite ObjectId de 24 dígitos hexadecimales o nombre existente; referencia inexistente: 400.
RN03: cambios conservan _id y fechaCreacion; solo permiten los campos editables. PUT conserva la semántica parcial heredada, expresamente documentada para no romper clientes.
RN04: DELETE es físico y devuelve el registro eliminado. Repetirlo devuelve 404.
RN05: catálogo vacío es 200 con datos: []. Consulta general no tiene parámetros, filtros ni paginación.
RN06: sistema académico local de un administrador, sin registro de usuarios ni roles. MongoDB standalone; verificación de relación en aplicación, sin transacción distribuida. No garantiza integridad bajo escrituras concurrentes adversarias; para varios operadores se requiere replica set y transacciones antes de producción.

## Estructura de datos

Genero: _id ObjectId generado; nombre string requerido trim unique; descripcion string trim default ''; fechaCreacion Date default Date.now. Colección MongoDB: generos. `libros` es virtual inverso (no array persistido), ref Libro, localField _id, foreignField genero.
Libro: _id ObjectId generado; nombre, autor y ubicacion string requeridos trim; genero ObjectId requerido ref Genero; ejemplares Number entero min 0; fechaCreacion Date default Date.now. Colección: libros. Relación Genero 1 -> N Libro. __v es metadato de Mongoose.

## Contrato HTTP

Base habitual http://127.0.0.1:8021. Pruebas: 8031 (real) y 8032 (proveedor simulado). Cuerpos de POST/PUT: Content-Type: application/json. Respuestas: application/json. Token Bearer en los diez endpoints CRUD. Auth y consultas externas son públicas.

| Método y ruta | Parámetros/cuerpo | Éxito | Errores de negocio |
|---|---|---|---|
| GET /api | sin parámetros ni cuerpo | 200 resumen | 500 |
| POST /auth/login | usuario:string, contrasena:string requeridos | 200 token,usuarioAutenticado,duracion | 400/401/503 |
| POST /auth/token | alias de login, mismo cuerpo | 200 | 400/401/503 |
| POST /generos/falta | nombre requerido, descripcion opcional | 201 {mensaje,datos:Genero} | 400/409 |
| GET /generos/obtenerVarios | sin cuerpo | 200 {mensaje,datos:Genero[]} | autenticación/conexión |
| GET /generos/obtenerUno/:id | id ObjectId requerido en path | 200 {mensaje,datos:Genero} | 400/404 |
| PUT /generos/baja/:id | id; al menos nombre o descripcion | 200 {mensaje,datos:Genero} | 400/404/409 |
| DELETE /generos/eliminar/:id | id; sin cuerpo | 200 {mensaje,datos:Genero} | 400/404 |
| POST /libros/falta | nombre,autor,genero,ubicacion,ejemplares requeridos | 201 {mensaje,datos:Libro} | 400 |
| GET /libros/obtenerVarios | sin cuerpo | 200 {mensaje,datos:Libro[]} | autenticación/conexión |
| GET /libros/obtenerUno/:id | id ObjectId requerido en path | 200 {mensaje,datos:Libro} | 400/404 |
| PUT /libros/baja/:id | id; al menos un campo editable de Libro | 200 {mensaje,datos:Libro} | 400/404 |
| DELETE /libros/eliminar/:id | id; sin cuerpo | 200 {mensaje,datos:Libro} | 400/404 |
| GET /servicios/libros | q:string opcional, default literatura; 1..200 caracteres | 200 {datos:[{id,nombre,autor,anio}],total} | 400/502 |
| GET /servicios/libros/:id | id con patrón OL[0-9]+W | 200 {datos:{id,nombre,resumen}} | 400/404/502 |

Todos los CRUD pueden devolver 401/403 por autenticación, 503 si MongoDB no está conectado, 500 por fallo interno. Los errores llevan {mensaje:string}; no se expone la pila ni secretos.
Ejemplo alta género: {"nombre":"Narrativa","descripcion":"Novelas"}.
Ejemplo alta libro: {"nombre":"Pedro Páramo","autor":"Juan Rulfo","genero":"Narrativa","ubicacion":"A-01","ejemplares":3}.
Ejemplo cambio: {"ejemplares":5,"ubicacion":"B-02"}.
Ejemplo error: {"mensaje":"Los ejemplares deben ser un entero no negativo"}.

## Arquitectura prevista antes del cambio

Router: verbo/path/middleware. Controlador: extrae body/params y establece estado JSON; delega reglas al servicio. Servicio: validaciones del dominio, consultas Mongoose, relación y adaptación externa. Modelo: esquema y persistencia. Middleware: JWT y error HTTP común. El servicio no recibe req/res. Se conservan rutas, respuestas y clientes existentes. Las verificaciones de negocio de los controladores se trasladarán a catalogoService.js; HTTP externo a servicioControl.js. Firmar y verificar HS256 explícitamente y rechazar esquema distinto de Bearer o claims incompletos.

## Validación prevista

Recorrido reproducible Postman: login, crear género, crear libro, consultas, actualizar ambos, rechazar borrado de género ocupado, borrar libro y género, confirmar 404 y lista vacía. Añadir negativos de altas, cambios, consultas y bajas para ambos recursos; verificar token inválido, faltante, expirado y datos faltantes. Pruebas Node comprueban regresión y JWT manipulado. Servicio externo: búsqueda/detalle reales y simulación separada para 404/502. Capturas deben provenir de ejecuciones reales con estado, tiempo y respuesta; conservar resultados y colección importable.
