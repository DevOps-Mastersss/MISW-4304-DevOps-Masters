# Postman API Documentation

Esta carpeta contiene los artefactos para documentar y probar el API REST de la entrega.

## Archivos

- `blacklist-service.postman_collection.json`: coleccion de Postman con los endpoints y escenarios de ejemplo.
- `blacklist-service.postman_environment.json`: ambiente con variables reutilizables para ejecutar la coleccion.

## Variables requeridas

- `base_url`: URL base del servicio. Para local puede ser `http://localhost:8080`; para AWS Beanstalk debe ser la URL publica del ambiente.
- `bearer_token`: token JWT generado con la misma `JWT_SECRET_KEY` configurada en el servicio.
- `email`: email usado para el escenario de creacion y consulta positiva.
- `email_not_found`: email usado para el escenario de consulta negativa.
- `app_uuid`: identificador UUID obligatorio de la aplicacion cliente.
- `blocked_reason`: motivo opcional por el que se agrega el email a la blacklist.

## Escenarios incluidos

- `GET /health - Verificar disponibilidad del servicio`
- `POST /blacklists - Agregar email a la blacklist`
- `POST /blacklists - Validar datos invalidos`
- `GET /blacklists/:email - Consultar email bloqueado`
- `GET /blacklists/:email - Consultar email no bloqueado`

## Publicacion de la documentacion

1. Crear o abrir el workspace del equipo en Postman.
2. Importar `blacklist-service.postman_collection.json`.
3. Importar `blacklist-service.postman_environment.json`.
4. Seleccionar el ambiente importado y reemplazar `base_url` y `bearer_token` con los valores reales.
5. Ejecutar los escenarios de la coleccion y guardar las respuestas de ejemplo si Postman lo solicita.
6. En Postman, abrir la coleccion, seleccionar `View Documentation` y luego `Publish`.
7. Copiar la URL publica de la documentacion publicada y anexarla al informe de arquitectura de la aplicacion.

## Generacion del token

El proyecto no tiene endpoint de login. Para pruebas se puede generar un JWT desde el servicio:

```bash
python -m app.auth
```

Ese token debe usarse en la variable `bearer_token` del ambiente de Postman.
