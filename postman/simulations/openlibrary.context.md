# Simulación Open Library

## Purpose

Verificar el servicio Axios real de Lumbre frente a las consultas públicas documentadas en `../mocks/openlibrary/default.js`. No simula el backend de Lumbre ni MongoDB.

## Execution

Desde la raíz del proyecto, iniciar `postman simulation run postman/simulations/openlibrary.sim.yaml --port 4901 --output ndjson`. En otra terminal ejecutar `OPENLIBRARY_TEST_URL=http://127.0.0.1:4901/openlibrary npm test`, con el MongoDB de `compose.yaml` encendido. Detener la simulación con Ctrl+C.

## Assumptions

- La descripción de una obra es opcional; la ficha debe funcionar sin ella. Verificado con la respuesta de ejemplo sin descripción. (observed 2026-10-27)
- Se construyó un mock local a partir de la documentación pública de Open Library; no se consultó un workspace del proveedor porque no se estableció una sesión autenticada de Postman. No prueba disponibilidad ni contenido del proveedor real. (reasoned 2026-10-27, default.js)

## Observations

2026-10-28: el miembro openlibrary recibió tráfico de los casos 22–25 de la entrega y de test/external.test.js; ninguno quedó sin tráfico. Se repitieron búsqueda, detalle sin descripción, 404 y 503. La colección completa aprobó 51 solicitudes y 102 aserciones, con el proveedor real reservado a 50–51 en otra instancia.

2026-10-27: el único miembro, `openlibrary`, recibió las cuatro llamadas esperadas: búsqueda y ficha correctas, obra inexistente y proveedor inaccesible. Axios recorrió HTTP real; el backend devolvió 200, 200, 404 y 502. La ejecución de `npm test` terminó con cuatro pruebas aprobadas, ninguna omitida.

## What didn't work

- 2026-10-27: CLI 1.74 rechazó una carpeta como `path` del miembro con `Mock 'file' must point to a file`; se debe señalar `config.yaml`.
- 2026-10-27: el aislamiento del entorno produjo `listen EPERM`; la simulación y el navegador se ejecutaron con autorización fuera del aislamiento.
