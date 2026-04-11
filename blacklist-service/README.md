# Blacklist Service

Microservicio Flask para la primera entrega del proyecto universitario de blacklist global de emails. Esta implementación cubre exclusivamente el alcance de Persona 1: base técnica compartida del backend y endpoint `POST /blacklists`.

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
├── run.py
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
python run.py
```

La aplicación queda disponible en:

```text
http://localhost:5000
```

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

## Endpoint implementado

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

## Ejemplos de prueba con curl

### Creación exitosa

```bash
curl --location --request POST 'http://localhost:5000/blacklists' \
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
curl --location --request POST 'http://localhost:5000/blacklists' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer <token>' \
--data-raw '{
  "email": "user@example.com",
  "app_uuid": "550e8400-e29b-41d4-a716-446655440000"
}'
```

### Datos inválidos

```bash
curl --location --request POST 'http://localhost:5000/blacklists' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer <token>' \
--data-raw '{
  "email": "correo-invalido",
  "app_uuid": "uuid-invalido",
  "blocked_reason": "Motivo de prueba"
}'
```

## Notas de diseño

- No se implementó `GET /blacklists/<email>`
- No se implementó login
- No se implementaron refresh tokens
- No se agregaron tests, migraciones, Docker ni CI/CD
- La tabla se crea con `db.create_all()` al iniciar la aplicación

## Supuestos realizados

- La creación de tablas en arranque es suficiente para la primera entrega académica
- `app_uuid` se almacena como string para simplificar la persistencia
- El endpoint futuro `GET /blacklists/<email>` podrá reutilizar el mismo modelo, configuración y esquema sin reorganizar la base
