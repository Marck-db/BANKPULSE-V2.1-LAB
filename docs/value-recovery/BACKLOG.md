# Product Backlog BANKPULSE

INC-BP-01: incepción 1.1 del PDF inicial. TEC-BP-01/02/03: análisis documental, escenarios y prototipado de sus secciones 1.2/1.3/1.4. Los hallazgos BP/LP mantienen los IDs del documento del equipo.

MoSCoW: Must obligatorio, Should importante, Could ampliación. Puntos relativos: 1 simple, 2 varios casos, 3 integración/recuperación. No equivalen a horas. Código base existente significa revisión estática, no prueba ejecutada.

## HU-BP-01
Como usuario, quiero registrar un pago con cuenta, monto y moneda, para conservar mi operación.

Aceptación: POST /api/payments con X-Idempotency-Key nuevo: 200, id y estado ACCEPTED; datos consultables.
Origen: BP-01; prioridad Must; 2 puntos; depende de —. Estado: Código base existente; prueba pendiente.

## HU-BP-02
Como usuario, quiero rechazar datos inválidos, para evitar pagos incorrectos.

Aceptación: Cuenta vacía, amount < 0.01 o currency que no tenga tres letras: 400, sin nuevo pago.
Origen: BP-02; prioridad Must; 1 puntos; depende de 01. Estado: Código base existente; prueba pendiente.

## HU-BP-03
Como usuario, quiero reintentar el mismo pago, para recuperar su respuesta sin duplicarlo.

Aceptación: Misma clave y mismos datos, enviados consecutivamente: 200 y mismo id; un solo registro.
Origen: BP-03; prioridad Must; 2 puntos; depende de 01. Estado: Código base existente; prueba pendiente.

## HU-BP-04
Como usuario, quiero consultar pagos recientes, para revisar mi historial.

Aceptación: GET /api/payments: 200; arreglo con máximo 50 pagos en orden descendente de createdAt.
Origen: BP-04; prioridad Must; 1 puntos; depende de 01. Estado: Código base existente; consulta en PDF.

## HU-BP-05
Como auditor, quiero guardar el evento junto al pago, para conservar su origen.

Aceptación: La transacción guarda Payment y OutboxEvent PAYMENT_CREATED juntos; si falla, no confirma cambios parciales.
Origen: BP-05; prioridad Should; 2 puntos; depende de 01. Estado: Código base existente; prueba pendiente.

## HU-BP-06
Como auditor, quiero recibir el evento de pago, para consultar evidencia de la operación.

Aceptación: Con servicios disponibles, outbox queda sin pendientes y /api/audit contiene el evento con aggregateId del pago.
Origen: BP-06; prioridad Should; 2 puntos; depende de 05. Estado: Código base existente; prueba pendiente.

## HU-BP-07
Como usuario, quiero una confirmación con id y datos, para reconocer el pago registrado.

Aceptación: La Vista muestra id, cuenta, monto, moneda y estado después de confirmar el registro.
Origen: BP-07; prioridad Should; 1 puntos; depende de 01. Estado: Propuesto; la Vista debe ampliarse.

## HU-BP-08
Como usuario, quiero errores que indiquen el dato inválido, para corregir mi solicitud.

Aceptación: Un error de validación se presenta junto al dato afectado; no se confunde con un fallo de comunicación.
Origen: BP-08; prioridad Should; 1 puntos; depende de 02. Estado: Propuesto; prueba UI pendiente.

## HU-BP-09
Como usuario, quiero un listado completo, para distinguir operaciones similares.

Aceptación: La Vista muestra id, cuenta, monto, moneda, estado y fecha por cada pago; vacío y error se distinguen.
Origen: BP-14 / BP-10; prioridad Could; 2 puntos; depende de 04. Estado: Propuesto; la Vista actual muestra menos campos.

## HU-BP-10
Como usuario, quiero detectar una clave usada con otros datos, para no confundir pagos.

Aceptación: La misma clave con datos distintos devuelve 409 y no modifica el pago original.
Origen: BP-11; prioridad Could; 2 puntos; depende de 03. Estado: Pendiente; el código base no compara datos.

## SPR-BP-01
Demostrar creación, validación, reintento idempotente y consulta de un pago ficticio.
Historias: HU-BP-01, HU-BP-02, HU-BP-03, HU-BP-04; 6 puntos. Duración: una semana. Capacidad propuesta: 18 horas por proyecto, 36 horas entre ambos; tres integrantes con 12 horas disponibles cada uno. Confirmar disponibilidad.
Roles propuestos: PO Martín Endara; SM Antonio Muñoz; desarrollo Martín, Antonio y Marco Bonilla.
Definition of Done: criterios verificados en el stack original, evidencia guardada, README y matriz actualizados, PR revisado/comentado por otro integrante y fusionado, sin secretos. El código heredado se distingue del aporte nuevo.

## Tareas técnicas
- Martín: backlog, MVC y matriz (5 h).
- Marco: comprobar reglas y ejecutar pruebas contra Docker (5 h).
- Antonio: README, capturas y revisión cruzada (5 h).
- Los tres: PR, correcciones y ensayo (3 h de trabajo total).