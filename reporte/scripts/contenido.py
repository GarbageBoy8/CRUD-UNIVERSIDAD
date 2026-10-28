"""Contenido académico del reporte; las respuestas y capturas se leen de las pruebas reales."""
INTRO = [
('1. INTRODUCCIÓN Y OBJETIVO.', [
('h2','¿Qué se desarrolló?'),
('p','En esta práctica trabajé con el backend de Lumbre, una biblioteca que permite administrar libros y géneros literarios. El proyecto se encuentra en la carpeta Ejercicio CRUD y conserva la organización del ejercicio empresa: modelos, controladores, rutas, middleware y servicios. El contexto se adaptó para registrar títulos, autores, estantes y cantidades de ejemplares.'),
('h2','¿Qué es un CRUD?'),
('p','CRUD reúne cuatro operaciones: crear, consultar, actualizar y eliminar información. En esta API, POST registra nuevos documentos; GET consulta los existentes; PUT modifica campos de un registro y DELETE lo elimina. Cada solicitud devuelve un código de estado HTTP y una respuesta JSON que permiten comprobar lo que ocurrió.'),
('h2','Objetivo general.'),
('p','Comprobar paso a paso el funcionamiento de la API de la biblioteca mediante peticiones HTTP realizadas con Postman CLI, verificando la persistencia en MongoDB, la relación entre géneros y libros, el acceso mediante JWT y las respuestas ante datos incorrectos.'),
('h2','Alcance de la práctica.'),
('list',['Autenticar al usuario y obtener un token de acceso con duración de una hora.','Ejecutar altas, consultas, modificaciones y bajas de los dos recursos.','Comprobar que no se elimine un género mientras tenga libros asociados.','Evaluar el servicio Axios con un proveedor externo simulado y respuestas controladas.']),
('p','Las evidencias se concentran en el backend. No se utilizan pantallas del catálogo, formularios de la aplicación ni elementos de diseño de su interfaz.')]),
('2. HERRAMIENTAS UTILIZADAS.', [
('h2','Node.js, Express y npm.'),
('p','Node.js ejecuta el código JavaScript del servidor. Express recibe las solicitudes, interpreta el cuerpo JSON mediante express.json() y dirige cada petición hacia el router correspondiente. npm administra las dependencias declaradas en package.json y permite ejecutar comandos como npm start y npm test.'),
('h2','MongoDB y Mongoose.'),
('p','MongoDB conserva la información en documentos. Mongoose define los esquemas de Libro y Genero, valida sus campos y realiza las consultas. Para estas pruebas utilicé un MongoDB local en Docker, accesible en el puerto 27018. Cada instancia del reporte utiliza una base temporal con nombre único.'),
('h2','Postman CLI.'),
('p','Es el cliente de línea de comandos de Postman. Permite enviar métodos HTTP, cabeceras, cuerpos JSON y tokens, además de ejecutar aserciones con pm.test. Se utilizó la versión 1.74.0 para obtener respuestas reales del servidor y exportarlas a archivos JSON.'),
('h2','JWT, dotenv y Axios.'),
('p','jwt-simple genera y verifica los tokens de autenticación. dotenv carga las variables de configuración desde .env. Axios realiza las solicitudes HTTP hacia Open Library; su comportamiento se comprobó mediante una simulación local del proveedor, sin reemplazar el código de la API de Lumbre.'),
('h2','¿Cómo se obtuvieron las capturas?'),
('p','Las capturas muestran una ventana real de Kitty ejecutando las pruebas con Postman CLI. El script presenta la respuesta exportada, con el JSON formateado para facilitar su lectura, junto con las aserciones evaluadas. Se ocultan los tokens de acceso; los códigos HTTP, identificadores y resultados corresponden a las ejecuciones guardadas.')]),
('3. ESTRUCTURA Y MODELO DE DATOS.', [
('h2','Organización del backend.'),
('table',(['Archivo o carpeta','Responsabilidad'],[
['app.js','Configura Express y monta las rutas de la API.'],['config/db.js','Conecta la aplicación habitual a MongoDB.'],['modelo/','Define los esquemas Libro y Genero.'],['control/','Procesa las operaciones del CRUD y sus validaciones.'],['routers/','Asocia cada método y ruta con su controlador.'],['middleware/','Genera y verifica los tokens JWT.'],['service/libroService.js','Consulta y adapta las respuestas de Open Library.'],['reporte/scripts/','Ejecuta las instancias y capturas de esta práctica.']])),
('h2','Campos de los documentos.'),
('p','Genero contiene nombre, descripcion y fechaCreacion. El nombre es obligatorio y único. Libro contiene nombre, autor, genero, ubicacion, ejemplares y fechaCreacion. El título, autor, género y ubicación son obligatorios; ejemplares debe ser un número entero mayor o igual a cero.'),
('h2','Relación de uno a muchos (1:N).'),
('p','Un género puede estar relacionado con varios libros. El campo genero de Libro almacena el ObjectId del documento Genero. Al consultar libros, populate("genero") incorpora los datos del género. En el otro sentido, el virtual libros del modelo Genero permite consultar los títulos que apuntan a ese género.'),
('p','Antes de eliminar un género, el controlador cuenta sus libros asociados. Si existe al menos uno, responde 400 y conserva el documento. Esta validación protege la relación y evita que un libro conserve una referencia al género que se intenta borrar.')]),
('4. PREPARACIÓN Y METODOLOGÍA.', [
('h2','1. Preparar la base de datos.'),
('p','Desde Ejercicio CRUD inicié MongoDB con docker compose up -d. El servidor del reporte importa directamente app.js y los modelos existentes. Crea una base temporal lumbre_reporte_ seguida de un identificador único; no copia ni simula los controladores del CRUD.'),
('h2','2. Ejecutar la instancia de pruebas.'),
('code','node reporte/scripts/servidor-pruebas.cjs'),
('p','La API de pruebas escucha en http://127.0.0.1:8031. El usuario es practica y la contraseña de este entorno es PracticaCRUD2026!. El script genera una clave JWT temporal. La aplicación habitual conserva su puerto 8021 y sus propios datos.'),
('h2','3. Configurar las peticiones.'),
('p','Las altas y modificaciones envían JSON con Content-Type: application/json. Después del inicio de sesión, las rutas protegidas reciben Authorization: Bearer seguido del token obtenido. En este reporte, {idGenero} y {idLibro} representan los valores _id devueltos al crear cada registro.'),
('h2','4. Evaluar y registrar los resultados.'),
('p','Cada petición verifica el estado esperado y una segunda condición sobre el contenido o su formato JSON. Se conserva el resultado exportado y se captura la terminal. Los rechazos 400, 401, 403 y 404 son resultados correctos cuando la prueba envía intencionalmente datos inválidos o consulta un documento eliminado.'),
('p','Las capturas mantienen sus fechas reales de ejecución. La fecha de entrega en portada corresponde a la indicada para la práctica. Los registros de ejemplo son ficticios y se eliminan durante el recorrido; al cerrar la instancia también se elimina su base temporal.')])
]

# Cada entrada contiene tres pasos concretos y una interpretación del resultado.
CASES = {
1:('5.1. CONSULTAR LOS RECURSOS DE LA API.',[
'Envié GET a /api, sin cuerpo ni token, para comprobar que Express estaba disponible.',
'Revisé el nombre del sistema y las rutas de autenticación, libros, géneros y servicios que devolvió el servidor.',
'Verifiqué el estado 200 y la cabecera Content-Type con formato JSON.'
],'La API respondió 200 OK y mostró el resumen de rutas. Esta prueba confirma que la instancia de Express atendió la petición; las operaciones posteriores comprueban el acceso a MongoDB.'),
2:('5.2. RECHAZAR CREDENCIALES INCORRECTAS.',[
'Envié POST a /auth/login con el usuario practica y una contraseña incorrecta.',
'El middleware comparó los valores recibidos con las credenciales configuradas para las pruebas.',
'Comprobé que la respuesta fuera 401 y que no se entregara un token para continuar.'
],'Se obtuvo 401 Unauthorized con el mensaje Usuario o contraseña incorrectos. El rechazo es el resultado esperado de esta prueba negativa.'),
3:('5.3. OBTENER EL TOKEN JWT.',[
'Envié las credenciales válidas mediante POST a /auth/login.',
'El servidor generó un token firmado que contiene usuario, iat y exp. La expiración se establece una hora después de la emisión; la contraseña no se incluye en su contenido.',
'Guardé el token para las siguientes peticiones y comprobé que la respuesta incluyera una cadena en el campo token.'
],'La autenticación devolvió 200 OK. La captura oculta parte del token, pero conserva usuarioAutenticado y la duración informada por la API.'),
4:('5.4. CONSULTAR SIN TOKEN.',[
'Intenté consultar GET /libros/obtenerVarios sin enviar la cabecera Authorization.',
'El router ejecutó verificarToken antes de llegar al controlador que consulta los libros.',
'Esperé un estado 401 y comprobé que la respuesta estuviera en formato JSON.'
],'La API respondió 401 con token no existente. No se devolvió el catálogo a una petición que carecía de credenciales de acceso.'),
5:('5.5. UTILIZAR UN TOKEN VENCIDO.',[
'El entorno de pruebas preparó un JWT firmado con su misma clave temporal y con exp establecido en una fecha pasada.',
'Envié ese token como Bearer en GET /generos/obtenerVarios.',
'Verifiqué que el middleware identificara la expiración y devolviera 403.'
],'Se recibió 403 Forbidden y el mensaje token expirado. Así se distinguió un token vencido de una petición que simplemente no envía token.'),
6:('6.1. CREAR UN GÉNERO.',[
'Con el token válido, envié POST a /generos/falta con nombre Tecnología y la descripción Libros sobre programación y sistemas.',
'El controlador validó el nombre, verificó que no estuviera registrado y guardó un documento Genero.',
'Comprobé el estado 201 y conservé el _id de la respuesta como idGenero para las consultas y modificaciones posteriores.'
],'Se creó el género en MongoDB y se devolvió 201 Created. La respuesta contiene los datos almacenados y el identificador generado.'),
7:('6.2. CONSULTAR TODOS LOS GÉNEROS.',[
'Envié GET a /generos/obtenerVarios con el token de acceso.',
'El controlador ejecutó la consulta de géneros e incluyó la relación virtual libros.',
'Comprobé que datos fuera una lista con un registro, porque la base temporal inició vacía y se había creado un solo género.'
],'La respuesta 200 OK contiene Tecnología. En este momento libros está vacío porque todavía no se había registrado ningún título asociado.'),
8:('6.3. CONSULTAR UN GÉNERO POR ID.',[
'Sustituí {idGenero} por el _id recibido en el alta y envié GET a /generos/obtenerUno/{idGenero}.',
'El controlador validó el formato ObjectId y buscó el documento correspondiente.',
'Comprobé el estado 200 y el nombre Tecnología en los datos devueltos.'
],'Se recuperó un documento concreto. Esta consulta usa un identificador único, mientras que obtenerVarios devuelve una lista de registros.'),
9:('6.4. ACTUALIZAR UN GÉNERO.',[
'Envié PUT a /generos/baja/{idGenero} con el nombre Informática y la descripción Programación, bases de datos y redes.',
'El controlador aceptó los campos permitidos y aplicó la actualización con validaciones de Mongoose.',
'Comprobé el estado 200 y que el nombre devuelto cambiara a Informática, conservando el mismo _id.'
],'El género se actualizó correctamente. Aunque la ruta heredada contiene baja, aquí el método PUT modifica el documento; la eliminación se realiza en /eliminar/:id.'),
10:('7.1. CREAR UN LIBRO.',[
'Envié POST a /libros/falta con el título Fundamentos de APIs REST, autor Ana Torres, estante A-01, tres ejemplares y el idGenero obtenido.',
'El controlador comprobó los campos obligatorios y que el género existiera antes de guardar el libro.',
'Verifiqué el estado 201 y el género Informática en la respuesta; guardé el nuevo _id como idLibro.'
],'El libro quedó almacenado y vinculado al género. La respuesta incorpora el documento del género mediante populate, lo que permite revisar la relación creada.'),
11:('7.2. CONSULTAR EL CATÁLOGO DE LIBROS.',[
'Envié GET a /libros/obtenerVarios utilizando el token válido.',
'El controlador consultó Libro.find() y pobló la referencia genero de cada resultado.',
'Comprobé que la lista incluyera exactamente un libro y que su información coincidiera con el alta anterior.'
],'La API devolvió 200 OK con el libro de prueba. La consulta posterior al alta confirma que el registro puede recuperarse desde MongoDB.'),
12:('7.3. CONSULTAR UN LIBRO POR ID.',[
'Envié GET a /libros/obtenerUno/{idLibro}, sustituyendo el parámetro con el identificador devuelto al crear el libro.',
'El controlador validó el ObjectId y buscó el documento con su género relacionado.',
'Verifiqué el estado 200 y que el campo autor contuviera Ana Torres.'
],'La respuesta devuelve el título, autor, género, ubicación y ejemplares del libro solicitado. El identificador permite seleccionar un registro sin depender de su nombre.'),
13:('7.4. ACTUALIZAR UN LIBRO.',[
'Envié PUT a /libros/baja/{idLibro} con ubicacion B-02 y ejemplares igual a 5.',
'El controlador revisó los campos permitidos y validó que la cantidad fuera un entero no negativo.',
'Comprobé en la respuesta tanto el nuevo estante como los cinco ejemplares; el identificador del libro se mantuvo.'
],'La actualización respondió 200 OK. El título y el autor se conservaron porque el cuerpo de la petición solo modificó ubicación y ejemplares.'),
14:('8.1. PROTEGER LA RELACIÓN 1:N.',[
'Intenté DELETE /generos/eliminar/{idGenero} mientras el libro de prueba todavía apuntaba a ese género.',
'El controlador contó los libros asociados antes de ejecutar la eliminación.',
'Comprobé el estado 400 y que el mensaje explicara que existe un libro asociado.'
],'El género no se eliminó. La validación impidió borrar un documento que aún participa en la relación; más adelante se repite la baja después de eliminar el libro.'),
15:('8.2. VALIDAR LA CANTIDAD DE EJEMPLARES.',[
'Envié PUT a /libros/baja/{idLibro} con ejemplares igual a -2.',
'El controlador detectó que el valor era negativo y detuvo la actualización.',
'Verifiqué el estado 400 y el mensaje que exige un entero no negativo. El registro eliminado en la prueba 17 permite observar que se conservaron cinco ejemplares.'
],'La petición inválida no cambió la cantidad almacenada. La validación evita registrar existencias negativas dentro de la biblioteca.'),
16:('8.3. VALIDAR EL FORMATO DEL ID.',[
'Envié GET a /libros/obtenerUno/id-invalido para probar un parámetro que no es un ObjectId.',
'El controlador revisó el formato antes de realizar la búsqueda del libro.',
'Comprobé que la API respondiera 400 y explicara que el identificador no era válido.'
],'Se obtuvo un error de entrada controlado. Este caso se diferencia del 404: aquí el formato del identificador es incorrecto, no se trata de un documento válido que dejó de existir.'),
17:('9.1. ELIMINAR EL LIBRO.',[
'Envié DELETE a /libros/eliminar/{idLibro} con el token válido.',
'El controlador localizó y eliminó el documento mediante findByIdAndDelete.',
'Verifiqué el estado 200 y el título del registro devuelto. La respuesta también conserva B-02 y cinco ejemplares como últimos valores guardados.'
],'El libro de prueba fue eliminado. La respuesta permite identificar qué documento se borró; la siguiente consulta comprueba que ya no puede recuperarse.'),
18:('9.2. COMPROBAR QUE EL LIBRO NO EXISTE.',[
'Repetí GET /libros/obtenerUno/{idLibro} utilizando exactamente el identificador del libro eliminado.',
'El formato del ID siguió siendo válido, pero la consulta ya no encontró un documento asociado.',
'Verifiqué el estado 404 y la respuesta JSON del servidor.'
],'La API devolvió 404 Not Found. Esta lectura posterior a DELETE confirma la eliminación del registro en la base temporal.'),
19:('9.3. ELIMINAR EL GÉNERO.',[
'Repetí DELETE /generos/eliminar/{idGenero} después de eliminar el libro.',
'El controlador volvió a contar las referencias y esta vez no encontró libros asociados.',
'Comprobé el estado 200 y los datos del género eliminado.'
],'Ahora la eliminación fue permitida. La comparación con la prueba 14 muestra que el resultado depende de si existen libros vinculados al género.'),
20:('9.4. COMPROBAR EL CATÁLOGO VACÍO.',[
'Consulté GET /libros/obtenerVarios una vez concluida la eliminación.',
'Revisé la propiedad datos y comprobé mediante una aserción que su longitud fuera cero.',
'Verifiqué que la API respondiera 200, porque consultar una colección vacía es una operación válida.'
],'La respuesta contiene datos: []. La ausencia de libros no es un error del servidor; es el estado esperado del catálogo al terminar este recorrido de pruebas.'),
21:('9.5. COMPROBAR LA ELIMINACIÓN DEL GÉNERO.',[
'Envié GET a /generos/obtenerUno/{idGenero} usando el identificador del género eliminado.',
'El controlador no encontró el documento y generó la respuesta correspondiente.',
'Comprobé el estado 404. Con esta consulta se cerró el ciclo de crear, leer, actualizar y eliminar el género.'
],'La respuesta 404 confirma que el género dejó de estar disponible. Los dos registros creados para la práctica fueron eliminados sin modificar el catálogo habitual.'),
22:('10.1. BUSCAR OBRAS CON AXIOS.',[
'En la instancia del puerto 8032 configuré OPENLIBRARY_API_URL para apuntar a la simulación local de Postman.',
'Envié GET /servicios/libros?q=fox. El backend ejecutó Axios contra /search.json y transformó docs al formato de la biblioteca.',
'Comprobé el estado 200 y el título Fantastic Mr. Fox que devuelve el escenario simulado.'
],'La ruta local y el cliente Axios se ejecutaron realmente. La respuesta de Open Library fue simulada; esta prueba no demuestra disponibilidad del proveedor en Internet.'),
23:('10.2. CONSULTAR LA FICHA EXTERNA.',[
'Envié GET a /servicios/libros/OL45804W en la instancia conectada a la simulación.',
'Axios consultó /works/OL45804W.json. El escenario devuelve el título sin el campo description.',
'Comprobé el estado 200 y el mensaje alternativo que utiliza el servicio cuando falta una descripción.'
],'El backend respondió sin fallar por la ausencia de un campo opcional. La prueba muestra cómo el servicio adapta la ficha externa antes de entregarla al cliente.'),
24:('10.3. MANEJAR UNA OBRA EXTERNA INEXISTENTE.',[
'Envié GET a /servicios/libros/OL999999W, un identificador con formato válido que el proveedor simulado no encuentra.',
'La simulación respondió 404 a la petición de Axios.',
'Verifiqué que el router local conservara el estado 404 y devolviera el mensaje Obra no encontrada.'
],'El error del proveedor se presentó como una respuesta controlada de la API. Se comprobó el manejo de una obra inexistente sin depender del catálogo real de Open Library.'),
25:('10.4. MANEJAR UNA FALLA DEL PROVEEDOR.',[
'Envié GET /servicios/libros?q=upstream-error. Ese término activa deliberadamente una respuesta 503 en la simulación.',
'Axios recibió el error y el router de Lumbre ejecutó su bloque de manejo de excepciones.',
'Comprobé que la API local respondiera 502 y un mensaje comprensible sobre la indisponibilidad del proveedor.'
],'El backend mantuvo una respuesta JSON controlada ante la falla externa. El 503 pertenece al proveedor simulado; el cliente de Lumbre recibió 502 Bad Gateway.')
}
