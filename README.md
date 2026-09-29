# Servicio de Pacientes - Diálisis

Microservicio para la gestión de pacientes en centros de diálisis, desarrollado con **Python y FastAPI**, siguiendo los principios de **Arquitectura Hexagonal (Puertos y Adaptadores)** y **Clean Architecture**.

Forma parte del ecosistema de microservicios de Diálisis y es responsable de la creación, consulta, actualización y eliminación de pacientes, con persistencia en PostgreSQL y autorización integrada con Auth0, Users y Roles.

---

## 📋 Tabla de Contenido

* [Tecnologías Utilizadas](#-tecnologías-utilizadas)
* [Arquitectura del Proyecto](#-arquitectura-del-proyecto)
* [Integración con Otros Microservicios](#-integración-con-otros-microservicios)
* [Autenticación y Autorización](#-autenticación-y-autorización)
* [Modelo de Datos](#-modelo-de-datos)
* [Requisitos Previos](#-requisitos-previos)
* [Puesta en Marcha Local](#-puesta-en-marcha-local)
* [Ejecución con Docker](#-ejecución-con-docker)
* [Documentación de la API](#-documentación-de-la-api)
* [Variables de Entorno](#-variables-de-entorno)
* [Pruebas Automatizadas](#-pruebas-automatizadas)
* [Calidad de Código](#-calidad-de-código)

---

## 🛠 Tecnologías Utilizadas

| Tecnología        | Descripción                                            |
| ----------------- | ------------------------------------------------------ |
| Python 3.13+      | Lenguaje de programación                               |
| FastAPI           | Framework para la construcción de APIs REST            |
| SQLAlchemy 2.0    | ORM y abstracción de acceso a datos                    |
| PostgreSQL        | Sistema de gestión de bases de datos relacional        |
| Alembic           | Control de versiones y migraciones de base de datos    |
| Pydantic          | Validación y serialización de datos                    |
| Pydantic Settings | Gestión de configuración mediante variables de entorno |
| Auth0             | Autenticación y validación de tokens JWT               |
| HTTPX             | Comunicación HTTP entre microservicios                 |
| uv                | Gestión de dependencias y entornos Python              |
| Docker            | Contenerización y despliegue del servicio              |
| Pytest            | Pruebas unitarias y de integración                     |
| Ruff              | Análisis estático y formateo de código                 |

---

## 🏛 Arquitectura del Proyecto

El servicio sigue una arquitectura hexagonal, separando la lógica del negocio de los detalles de infraestructura, persistencia y comunicación HTTP.

```text
dialisis-patients/
├── migrations/                  # Migraciones de Alembic
│   └── versions/
├── src/
│   └── patients/
│       ├── domain/              # Capa de dominio
│       │   └── entities/
│       │       └── patient.py
│       │
│       ├── application/         # Capa de aplicación
│       │   ├── dtos/            # Objetos de transferencia de datos
│       │   ├── exceptions/      # Excepciones de aplicación
│       │   ├── ports/           # Interfaces y contratos
│       │   └── use_cases/       # Casos de uso
│       │
│       ├── adapters/            # Puertos y adaptadores
│       │   ├── inbound/         # Adaptadores de entrada
│       │   │   └── http/
│       │   │       ├── dependencies/
│       │   │       ├── exceptions/
│       │   │       ├── routes/
│       │   │       └── schemas/
│       │   │
│       │   └── outbound/        # Adaptadores de salida
│       │       ├── database/    # Persistencia PostgreSQL
│       │       └── users/       # Cliente HTTP de Users
│       │
│       ├── infrastructure/      # Configuración e infraestructura
│       │   └── config/
│       │       └── settings.py
│       │
│       └── main.py              # Punto de entrada de FastAPI
│
├── tests/
│   ├── unit/                    # Pruebas unitarias
│   │   └── fakes/
│   └── integration/             # Pruebas de endpoints HTTP
│
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── pyproject.toml
├── uv.lock
└── README.md
```

### Responsabilidades de las capas

**Domain**

Contiene las entidades y reglas fundamentales del negocio. No depende de FastAPI, SQLAlchemy ni de servicios externos.

**Application**

Implementa los casos de uso del sistema, los DTOs, las excepciones y los puertos que definen los contratos de acceso a datos y servicios externos.

**Adapters**

Conecta la aplicación con el mundo exterior:

* Inbound: expone los endpoints HTTP mediante FastAPI, valida las solicitudes y transforma las respuestas.
* Outbound: implementa el acceso a PostgreSQL y la comunicación HTTP con otros microservicios.

**Infrastructure**

Contiene la configuración técnica del servicio y la carga de variables de entorno.

---

## 🔗 Integración con Otros Microservicios

El servicio de pacientes forma parte de una arquitectura distribuida compuesta por varios microservicios independientes.

| Microservicio | Responsabilidad                                                  |
| ------------- | ---------------------------------------------------------------- |
| Auth          | Autenticación de usuarios mediante Auth0                         |
| Users         | Gestión de usuarios y consulta de información de autorización    |
| Roles         | Administración de roles, permisos y validación de autorizaciones |
| Patients      | Gestión y persistencia de pacientes                              |

### Flujo de autorización

Cuando un usuario consulta los pacientes, el servicio realiza las validaciones correspondientes:

1. Recibe el token Bearer enviado por el cliente.
2. Valida el token JWT utilizando las claves públicas de Auth0.
3. Consulta el microservicio Users para obtener la información de autorización del usuario.
4. Obtiene el rol asignado al usuario.
5. Consulta el microservicio Roles para verificar el permiso requerido.
6. Si las validaciones son satisfactorias, ejecuta la operación solicitada sobre la base de datos de pacientes.

La comunicación entre microservicios se realiza mediante HTTP y las URLs se configuran a través de variables de entorno.

El servicio de pacientes mantiene su propia lógica y persistencia, sin acceder directamente a las tablas de Users o Roles.

---

## 🔐 Autenticación y Autorización

La autenticación se realiza mediante Auth0 y tokens JWT de tipo Bearer.

Las solicitudes a los endpoints protegidos deben incluir el encabezado:

```http
Authorization: Bearer <access_token>
```

El servicio valida los tokens utilizando el algoritmo RS256, la audiencia configurada y el emisor correspondiente al tenant de Auth0.

La autorización se basa en los roles y permisos administrados por el microservicio Roles.

### Permisos

| Permiso         | Descripción                             |
| --------------- | --------------------------------------- |
| `patients.read` | Permite consultar la lista de pacientes |

El endpoint `GET /patients` requiere el permiso `patients.read`.

Las operaciones que requieren autenticación deben ejecutarse con un token válido. Los permisos adicionales deben corresponder a las dependencias de autorización implementadas en cada endpoint.

---

## 🗄 Modelo de Datos

La información de pacientes se almacena en PostgreSQL, dentro del esquema dedicado `patients`.

### Tabla `patients.patients`

| Campo              | Tipo / descripción                          |
| ------------------ | ------------------------------------------- |
| `id`               | Identificador único del paciente            |
| `user_id`          | Identificador opcional del usuario asociado |
| `tipo_documento`   | Tipo de documento de identidad              |
| `numero_documento` | Número de documento único                   |
| `full_name`        | Nombre completo del paciente                |
| `fecha_nacimiento` | Fecha de nacimiento                         |
| `telefono`         | Número de teléfono opcional                 |
| `email`            | Correo electrónico opcional                 |
| `direccion`        | Dirección opcional                          |
| `is_active`        | Estado del paciente                         |
| `created_at`       | Fecha de creación                           |
| `updated_at`       | Fecha de última actualización               |

El campo `user_id` permite asociar un paciente con un usuario del sistema. Esta relación es lógica y no implica una clave foránea hacia la base de datos de Users.

Las migraciones de esquema se administran mediante Alembic.

---

## 🚀 Puesta en Marcha Local

### 1. Requisitos Previos

Antes de ejecutar el servicio localmente, asegúrate de contar con:

* Python 3.13 o superior.
* [uv](https://docs.astral.sh/uv/).
* PostgreSQL en ejecución.
* Acceso a un tenant de Auth0.
* Microservicios Users y Roles disponibles para las operaciones que requieren autorización.

### 2. Clonar el repositorio

```bash
git clone https://github.com/JuanRiArangoT/dialisis-patients.git
cd dialisis-patients
```

### 3. Configurar variables de entorno

Copia el archivo de ejemplo:

```bash
cp .env.example .env
```

En Windows PowerShell puedes utilizar:

```powershell
Copy-Item .env.example .env
```

Configura los valores correspondientes a tu entorno local. Consulta la sección [Variables de Entorno](#-variables-de-entorno).

No compartas ni subas el archivo `.env` con credenciales reales al repositorio.

### 4. Instalar dependencias

```bash
uv sync
```

Este comando instala las dependencias declaradas en `pyproject.toml` y utiliza `uv.lock` para mantener versiones reproducibles.

### 5. Ejecutar migraciones

Aplica las migraciones pendientes:

```bash
uv run alembic upgrade head
```

Este comando lleva la base de datos a la última revisión disponible y crea las estructuras definidas por las migraciones.

### 6. Iniciar el servidor

```bash
uv run uvicorn patients.main:app --reload --port 8000
```

La API estará disponible en:

* API: http://localhost:8000
* Swagger UI: http://localhost:8000/docs
* ReDoc: http://localhost:8000/redoc

---

## 🐳 Ejecución con Docker

El proyecto incluye un `Dockerfile` y un archivo `docker-compose.yml` para construir y ejecutar el microservicio en un contenedor.

### 1. Requisitos

* Docker Desktop o Docker Engine.
* Red Docker `dialisis-network` creada.
* Microservicios dependientes disponibles en la red cuando se necesiten operaciones que requieran autorización.

Si la red todavía no existe, puedes crearla con:

```bash
docker network create dialisis-network
```

Si ya existe, no es necesario volver a crearla.

### 2. Configurar el entorno

Crea y configura el archivo `.env` a partir de `.env.example`.

Para la comunicación entre contenedores, las URLs deben utilizar los nombres de los contenedores y el puerto interno `8000`.

Ejemplo:

```env
USERS_SERVICE_URL=http://dialisis-users:8000
ROLES_SERVICE_URL=http://dialisis-roles:8000
```

La URL de PostgreSQL debe utilizar el hostname y puerto accesibles desde el contenedor de pacientes.

### 3. Construir y levantar el servicio

```bash
docker compose up -d --build
```

El servicio queda disponible en el puerto `8003` del host:

http://localhost:8003

### 4. Ejecutar las migraciones dentro del contenedor

```bash
docker exec -it dialisis-patients uv run alembic upgrade head
```

Este comando ejecuta las migraciones utilizando la configuración del contenedor.

### 5. Consultar los logs

```bash
docker compose logs -f patients
```

### 6. Detener el servicio

```bash
docker compose down
```

Para volver a construir la imagen después de modificar el código:

```bash
docker compose up -d --build
```

---

## 📖 Documentación de la API

La documentación interactiva es generada automáticamente por FastAPI.

| Recurso    | URL local                   | URL Docker                  |
| ---------- | --------------------------- | --------------------------- |
| Swagger UI | http://localhost:8000/docs  | http://localhost:8003/docs  |
| ReDoc      | http://localhost:8000/redoc | http://localhost:8003/redoc |

### Endpoints principales

| Método   | Endpoint                 | Descripción                              |
| -------- | ------------------------ | ---------------------------------------- |
| `GET`    | `/health`                | Verificar el estado del servicio         |
| `POST`   | `/patients`              | Crear un paciente                        |
| `GET`    | `/patients`              | Listar pacientes                         |
| `GET`    | `/patients/{patient_id}` | Consultar un paciente por identificador  |
| `PUT`    | `/patients/{patient_id}` | Actualizar la información de un paciente |
| `DELETE` | `/patients/{patient_id}` | Eliminar un paciente                     |

Los endpoints protegidos requieren autenticación mediante un token Bearer válido. Las autorizaciones adicionales se aplican de acuerdo con las dependencias configuradas en cada ruta.

### Ejemplo de creación de paciente

Solicitud:

```http
POST /patients
Content-Type: application/json
Authorization: Bearer <access_token>
```

Cuerpo:

```json
{
  "user_id": null,
  "tipo_documento": "CC",
  "numero_documento": "1234567891",
  "full_name": "Paciente Prueba",
  "fecha_nacimiento": "1990-01-15",
  "telefono": "3001234567",
  "email": "paciente@example.com",
  "direccion": "Medellín"
}
```

Respuesta de ejemplo:

```json
{
  "patient_id": "9590a6a7-1f23-4d5b-8bd9-e3e8055e52f5",
  "user_id": null,
  "tipo_documento": "CC",
  "numero_documento": "1234567891",
  "full_name": "Paciente Prueba",
  "fecha_nacimiento": "1990-01-15",
  "telefono": "3001234567",
  "email": "paciente@example.com",
  "direccion": "Medellín",
  "is_active": true
}
```

El identificador `patient_id` es generado por el servicio.

Los valores de documento y correo del ejemplo son ilustrativos y deben reemplazarse por datos de prueba únicos al realizar nuevas solicitudes.

### Ejemplo de listado paginado y búsqueda

Solicitud:

```http
GET /patients?page=1&page_size=20&search=Prueba&is_active=true
Authorization: Bearer <access_token>
```

Parámetros opcionales:
- `page`: Número de página (entero >= 1, por defecto `1`).
- `page_size`: Cantidad de resultados por página (entero entre 1 y 100, por defecto `20`).
- `search`: Búsqueda insensible a mayúsculas/minúsculas sobre el nombre completo (`full_name`) o documento (`numero_documento`).
- `is_active`: Filtrar pacientes activos (`true`) o inactivos (`false`).

Respuesta de ejemplo:

```json
{
  "items": [
    {
      "patient_id": "9590a6a7-1f23-4d5b-8bd9-e3e8055e52f5",
      "user_id": null,
      "tipo_documento": "CC",
      "numero_documento": "1234567891",
      "full_name": "Paciente Prueba",
      "fecha_nacimiento": "1990-01-15",
      "telefono": "3001234567",
      "email": "paciente@example.com",
      "direccion": "Medellín",
      "is_active": true
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

---

## ⚙️ Variables de Entorno

La aplicación utiliza Pydantic Settings para cargar la configuración desde variables de entorno.

Las siguientes variables corresponden a la configuración utilizada por el servicio:

| Variable             | Descripción                                  |
| -------------------- | -------------------------------------------- |
| `DATABASE_URL`       | Cadena de conexión a PostgreSQL              |
| `AUTH0_DOMAIN`       | Dominio del tenant de Auth0                  |
| `AUTH0_API_AUDIENCE` | Audiencia esperada para validar el token JWT |
| `USERS_SERVICE_URL`  | URL base del microservicio Users             |
| `ROLES_SERVICE_URL`  | URL base del microservicio Roles             |

Ejemplo de configuración local:

```env
DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/dialisis

AUTH0_DOMAIN=tu-tenant.us.auth0.com
AUTH0_API_AUDIENCE=https://tu-api/

USERS_SERVICE_URL=http://localhost:8001
ROLES_SERVICE_URL=http://localhost:8002
```

En Docker, las URLs de los microservicios deben utilizar los nombres de los contenedores y sus puertos internos.

**Importante:** los valores anteriores son ejemplos. Utiliza los nombres y valores definidos en tu archivo `.env.example` y en la configuración real del proyecto. No publiques secretos, contraseñas ni tokens de acceso.

---

## 🧪 Pruebas Automatizadas

El proyecto utiliza Pytest para validar la lógica de negocio y el comportamiento de los endpoints.

La suite incluye:

* Pruebas unitarias de casos de uso utilizando repositorios falsos en memoria.
* Pruebas de integración de endpoints HTTP mediante `TestClient`.

### Ejecutar todas las pruebas

```bash
uv run python -m pytest
```

### Ejecutar pruebas unitarias

```bash
uv run python -m pytest tests/unit
```

### Ejecutar pruebas de integración

```bash
uv run python -m pytest tests/integration
```

Las pruebas de integración utilizan las dependencias de prueba definidas en `tests/conftest.py` y no deben confundirse con pruebas contra servicios externos o bases de datos de producción.

---

## 🧹 Formato y Calidad de Código

El proyecto utiliza Ruff para revisar y formatear el código Python.

### Revisar errores y buenas prácticas

```bash
uv run ruff check .
```

### Formatear el código

```bash
uv run ruff format .
```

Se recomienda ejecutar las pruebas y las verificaciones de Ruff antes de realizar un commit.

---

## 📌 Estado del Proyecto

El microservicio cuenta con:

* Arquitectura hexagonal y separación de responsabilidades.
* API REST para gestión de pacientes.
* Persistencia en PostgreSQL.
* Migraciones versionadas con Alembic.
* Validación de tokens JWT mediante Auth0.
* Integración de autorización con Users y Roles.
* Contenerización con Docker.
* Pruebas unitarias y de integración.

---

## 👨‍💻 Autor

**Juan Ricardo Arango Tangarife**

Proyecto Diálisis — Microservicio de Pacientes.

Repositorio: [JuanRiArangoT/dialisis-patients](https://github.com/JuanRiArangoT/dialisis-patients)
