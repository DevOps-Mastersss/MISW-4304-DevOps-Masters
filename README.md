# MISW-4304 DevOps Masters

Este repositorio contiene el microservicio `blacklist-service` y está preparado para una fase de Integración Continua enfocada en pruebas unitarias y generación de artefactos con AWS CodeBuild.

## CI del repositorio

La configuración de build está en:

```text
buildspec.yml
```

Ese archivo permite que CodeBuild ejecute:

1. instalación de dependencias
2. ejecución de pruebas unitarias con `pytest`
3. generación del artefacto `blacklist-service.zip`

## Comandos equivalentes en local

Desde la raíz del repositorio:

```bash
python3 -m venv .venv
.venv/bin/pip install -r blacklist-service/requirements.txt
.venv/bin/pytest -q blacklist-service/tests
cd blacklist-service
mkdir -p dist
zip -r dist/blacklist-service.zip . -x "dist/*" ".venv/*" "venv/*" "__pycache__/*" ".pytest_cache/*" "tests/*" "postman/*" "app/__pycache__/*" "*.pyc" "*.pyo" ".env" "blacklist-service.zip"
```

## Documentación del microservicio

La guía funcional y de pruebas del servicio está en:

- `blacklist-service/README.md`

---

## Contexto del microservicio

Microservicio Flask para la primera entrega del proyecto universitario de blacklist global de emails. Esta implementación expone los endpoints requeridos para agregar emails a la blacklist y consultar si un email se encuentra bloqueado.

## Estructura del proyecto

```text
blacklist-service/
├── app/
│   ├── __init__.py
│   ├── auth.py
│   ├── config.py
│   ├── models.py
│   ├── resources.py
│   └── schemas.py
├── application.py
├── postman/
│   ├── blacklist-service.postman_collection.json
│   ├── blacklist-service.postman_environment.json
│   └── README.md
├── tests/
│   ├── conftest.py
│   └── test_blacklist_resources.py
├── pytest.ini
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Tecnologías usadas

- Python 3.8 o superior
- Flask 1.1.x
- Flask SQLAlchemy
- Flask RESTful
- Flask Marshmallow
- Flask JWT Extended
- Werkzeug
- PostgreSQL

## Alcance implementado

- App Flask base con factory `create_app`
- Configuración central desde variables de entorno
- Inicialización de Flask RESTful, SQLAlchemy, Marshmallow y JWT Extended
- Conexión a PostgreSQL
- Modelo relacional `blacklist_entries`
- Endpoint protegido `POST /blacklists`
- Endpoint protegido `GET /blacklists/<email>`
- Endpoint técnico `GET /health`
- Suite de pruebas unitarias con `pytest`
- Colección y ambiente de Postman para documentar y probar el API REST
- Utilidad para generar un JWT manual para pruebas locales

## Variables de entorno

1. Copia el archivo de ejemplo:

```bash
cp .env.example .env
```

2. Reemplaza en `.env` los valores de ejemplo por los valores reales de tu máquina local.

El archivo `.env.example` solo contiene placeholders. No se deben usar esas credenciales tal cual en un entorno real.

## Preparar PostgreSQL

Crea la base de datos con un usuario y una contraseña que coincidan con tu archivo `.env`. Un flujo mínimo usando `psql` sería:

```bash
psql -U postgres -h localhost -p 5432 -c "CREATE USER blacklist_user WITH PASSWORD 'blacklist_password';"
psql -U postgres -h localhost -p 5432 -c "CREATE DATABASE blacklist_db OWNER blacklist_user;"
```

Luego ajusta tu `.env` para que `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` y `DB_NAME` coincidan con esos valores reales.

## Instalación y ejecución local

Se recomienda usar Python 3.10 por compatibilidad práctica del stack, aunque la solución está planteada para Python 3.8 o superior.

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
python application.py
```

La aplicación queda disponible en:

```text
http://localhost:8080
```

## Pruebas unitarias

La suite de pruebas backend está hecha con `pytest` y reutiliza la app Flask real con `test_client`. Las pruebas mockean el acceso a base de datos para no depender de PostgreSQL durante la validación local o en CI.

### Ejecutar las pruebas desde la carpeta del microservicio

```bash
cd blacklist-service
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pytest -q
```

### Ejecutar las pruebas desde la raíz del repositorio

Si prefieres quedarte en la raíz del repositorio `MISW-4304-DevOps-Masters`, usa rutas explícitas:

```bash
python3 -m venv .venv
.venv/bin/pip install -r blacklist-service/requirements.txt
.venv/bin/pytest -q blacklist-service/tests
```

### Ejecutar una sola prueba

```bash
.venv/bin/pytest blacklist-service/tests/test_blacklist_resources.py::test_post_blacklists_creates_entry_successfully -q
```

Si ya estás dentro de `blacklist-service/`, el comando equivalente es:

```bash
.venv/bin/pytest tests/test_blacklist_resources.py::test_post_blacklists_creates_entry_successfully -q
```

### Ejecutar solo los casos de un endpoint

```bash
.venv/bin/pytest -k post_blacklists -q
.venv/bin/pytest -k get_blacklists -q
```

### Resultado esperado

Si todo está estable, deberías ver una salida similar a esta:

```text
10 passed in 0.03s
```

Estas pruebas cubren los escenarios principales de:

- `POST /blacklists`: creación exitosa, payload inválido, duplicado, falta de token y token inválido
- `GET /blacklists/<email>`: email existente, email no existente, falta de token y token inválido

## Generar un token JWT para pruebas

No existe login ni endpoint de autenticación. Para pruebas locales se genera un token manual con la utilidad incluida en `app/auth.py`.

```bash
python -m app.auth
```

Ese comando imprimirá un JWT. Úsalo en Postman o `curl` así:

```text
Authorization: Bearer <token>
```

El token se firma usando `JWT_SECRET_KEY`, así que debe generarse después de configurar tu `.env`.

## Endpoints implementados

### POST /blacklists

Protegido con Bearer token usando Flask JWT Extended.

#### Headers requeridos

```text
Content-Type: application/json
Authorization: Bearer <token>
```

#### Body esperado

```json
{
  "email": "user@example.com",
  "app_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "blocked_reason": "Fraude detectado"
}
```

#### Reglas aplicadas

- `email` es obligatorio, válido, único y se guarda en minúsculas
- `app_uuid` es obligatorio y debe ser un UUID válido
- `blocked_reason` es opcional y no puede superar 255 caracteres
- `request_ip` se toma primero de `X-Forwarded-For`; si no existe, se usa `request.remote_addr`
- `created_at` se almacena en UTC

#### Respuesta exitosa

```json
{
  "message": "Email agregado exitosamente a la blacklist"
}
```

Status code: `201 Created`

#### Respuesta por email duplicado

```json
{
  "message": "El email ya se encuentra en la blacklist"
}
```

Status code: `409 Conflict`

#### Respuesta por error de validación

```json
{
  "message": "Datos inválidos",
  "errors": {
    "email": [
      "Not a valid email address."
    ]
  }
}
```

Status code: `400 Bad Request`

#### Respuesta si falta o es inválido el token

Flask JWT Extended devuelve respuestas JSON automáticas. Los casos más comunes son:

- Token faltante:

```json
{
  "msg": "Missing Authorization Header"
}
```

Status code: `401 Unauthorized`

- Token inválido:

```json
{
  "msg": "Not enough segments"
}
```

Status code: `422 Unprocessable Entity`

El mensaje exacto del token inválido puede variar dependiendo de cómo esté mal formado o firmado.

### GET /blacklists/<email>

Protegido con Bearer token usando Flask JWT Extended.

#### Headers requeridos

```text
Authorization: Bearer <token>
```

#### Parámetros de ruta

```text
email: email del cliente a consultar
```

#### Respuesta si el email está bloqueado

```json
{
  "is_blacklisted": true,
  "blocked_reason": "Fraude detectado"
}
```

Status code: `200 OK`

#### Respuesta si el email no está bloqueado

```json
{
  "is_blacklisted": false,
  "blocked_reason": null
}
```

Status code: `200 OK`

### GET /health

Endpoint técnico sin autenticación para validar disponibilidad del servicio y configurar health checks.

```json
{
  "status": "healthy"
}
```

Status code: `200 OK`

## Documentación Postman

Los artefactos para documentar y probar el API REST están en `postman/`:

- `postman/blacklist-service.postman_collection.json`
- `postman/blacklist-service.postman_environment.json`
- `postman/README.md`

Importe la colección y el ambiente en el workspace del equipo en Postman, actualice las variables `base_url` y `bearer_token`, ejecute los escenarios y publique la documentación desde Postman. La URL pública generada debe anexarse al informe de arquitectura de la aplicación.

## Ejemplos de prueba con curl

### Creación exitosa

```bash
curl --location --request POST 'http://localhost:8080/blacklists' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer <token>' \
--data-raw '{
  "email": "USER@Example.com",
  "app_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "blocked_reason": "Fraude detectado"
}'
```

### Duplicado

```bash
curl --location --request POST 'http://localhost:8080/blacklists' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer <token>' \
--data-raw '{
  "email": "user@example.com",
  "app_uuid": "550e8400-e29b-41d4-a716-446655440000"
}'
```

### Datos inválidos

```bash
curl --location --request POST 'http://localhost:8080/blacklists' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer <token>' \
--data-raw '{
  "email": "correo-invalido",
  "app_uuid": "uuid-invalido",
  "blocked_reason": "Motivo de prueba"
}'
```

## Notas de diseño

- No se implementó login
- No se implementaron refresh tokens
- No se agregaron migraciones, Docker ni CI/CD
- La tabla se crea con `db.create_all()` al iniciar la aplicación

## Supuestos realizados

- La creación de tablas en arranque es suficiente para la primera entrega académica
- `app_uuid` se almacena como string para simplificar la persistencia
- El mismo modelo relacional soporta los endpoints de creación y consulta de blacklist

## Test WebHook