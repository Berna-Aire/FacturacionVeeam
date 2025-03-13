# 🚀 Veeam API - Sistema de gestión de datos

Este repositorio contiene un sistema dockerizado para la gestión de datos de Veeam, compuesto por una API REST desarrollada con FastAPI y una base de datos MariaDB. El sistema permite administrar información sobre revendedores (resellers), empresas y su uso de productos.

> ℹ️ **Nota**: Opcional usar NPM (Nginx Proxy Manager) para redirección de URL por peticiones HTTPS

## 📁 Estructura del proyecto

```
.
├── appAPI/
│   ├── main.py                # Código principal de la API FastAPI
│   └── requirements.txt       # Dependencias de Python para la API
├── scriptsAPI/
│   └── cronjob.sh             # Script para tareas programadas
├── scriptsBD/
│   ├── crearBD.py             # Script para crear las tablas en la BD
│   ├── datosprueba.json       # Datos de ejemplo para cargar en la BD
│   ├── entrypoint.sh          # Script de entrada para el contenedor de BD
│   ├── init.sql               # SQL inicial para configurar permisos
│   ├── insertardatosBD.py     # Script para insertar datos en la BD
│   ├── requirements.txt       # Dependencias de Python para los scripts de BD
│   └── setup-db.sh            # Script para configurar la BD después de inicializar
├── docker-compose.yaml        # Configuración de Docker Compose
├── dockerfileBD               # Dockerfile para el contenedor de BD
├── dockerfileFastAPI          # Dockerfile para el contenedor de FastAPI
└── wait-for-db.sh             # Script para esperar a que la BD esté lista
```

## ⚙️ Requisitos previos

- Docker
- Docker Compose

## 🔧 Instalación y ejecución

1. Clona este repositorio:
   ```bash
   git clone https://github.com/Berna-Aire/FacturacionVeeam.git
   cd FacturacionVeeam/FactVeeamFinal
   ```

2. Construye e inicia los contenedores:
   ```bash
   docker-compose build
   docker-compose up -d
   ```
   ⚠️ En caso de encontrar el error
     ```bash
      ERROR: for fastapi  Container "<id_container>" is unhealthy.
      ERROR: Encountered errors while bringing up the project.
      ```
   Volver a levantar los contenedores 
   ```bash
      docker-compose up -d
      ```

3. Verifica que los contenedores estén funcionando:
   ```bash
   docker-compose ps
   ```

## 📊 Modelo de datos

El sistema utiliza SQLAlchemy para definir y manejar el siguiente modelo de datos:

### 🔹 Resellers

Información sobre los revendedores.
| Campo | Descripción |
|-------|-------------|
| `reseller_uid` | ID único del revendedor (clave primaria) |
| `reseller_name` | Nombre del revendedor |
| `circuit_code` | Código de circuito |
| `company_uid` | ID de compañía relacionada |

### 🔹 Companies

Información sobre las empresas asociadas a revendedores.
| Campo | Descripción |
|-------|-------------|
| `reseller_uid` | ID del revendedor (clave foránea, parte de la clave primaria) |
| `company_uid` | ID de la empresa (parte de la clave primaria) |
| `company_name` | Nombre de la empresa |

### 🔹 Company_Usage

Uso de productos por parte de las empresas. (Pendiente de implementar)
| Campo | Descripción |
|-------|-------------|
| `id` | ID único (clave primaria) |
| `company_uid` | ID de la empresa (clave foránea) |
| `product_type` | Tipo de producto |
| `license_type` | Tipo de licencia |
| `usage` | Nivel de uso |
| `date` | Fecha del registro |

## 🌐 API Endpoints

La API proporciona los siguientes endpoints:

### 🔸 Resellers

- `GET /resellers/`: Obtiene todos los revendedores
  ```
  http://localhost:8001/resellers/
  ```

- `GET /resellers/{reseller_uid}`: Obtiene un revendedor específico
  ```
  http://localhost:8001/resellers/<id_reseller>
  ```

### 🔸 Companies

- `GET /companies/`: Obtiene todas las empresas
  ```
  http://localhost:8001/companies/
  ```

- `GET /companies/{company_uid}`: Obtiene una empresa específica
  ```
  http://localhost:8001/companies/<id_company>
  ```

### 🔸 Usages

- `GET /usages/`: Obtiene todos los registros de uso
  ```
  http://localhost:8001/usages/
  ```

- `GET /companies/{company_uid}/usages`: Obtiene los usos de una empresa específica
  ```
  http://localhost:8001/companies/<id_company>/usages
  ```

## 🔍 Parámetros de consulta

Puedes utilizar los siguientes parámetros en las consultas a la API:

- `skip`: Número de registros a omitir (para paginación)
- `limit`: Número máximo de registros a devolver

Ejemplo:
```
http://localhost:8001/resellers/?skip=5&limit=10
```

## 📝 Documentación de la API

FastAPI genera automáticamente documentación para la API. Accede a:

- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## 🧪 Pruebas

Para probar la API puedes usar herramientas como:

- Navegador web (para solicitudes GET)
- curl
- Postman
- Python con la biblioteca requests

Ejemplo con curl:
```bash
curl -X GET "http://localhost:8001/resellers/"
```

## 💻 Desarrollo

### 🔧 Tecnologías utilizadas

- **FastAPI**: Framework para desarrollo de APIs en Python
- **SQLAlchemy**: ORM para Python
- **MariaDB**: Sistema de gestión de bases de datos
- **Docker**: Contenedorización del sistema

### 🔄 Modificar el modelo de datos

Si necesitas modificar el modelo de datos:

1. Edita las clases en `scriptsBD/crearBD.py` y `appAPI/main.py`
2. Reconstruye los contenedores:
   ```bash
   docker-compose down -v
   docker-compose build
   docker-compose up -d
   ```
   
> ⚠️ **Importante**: Se recomienda eliminar volúmenes e imágenes anteriores instaladas 
```bash
docker-compose down --rmi all -v \
docker volume prune -f
```

## ❓ Resolución de problemas

Si encuentras problemas al iniciar los contenedores:

- Verifica los logs:
  ```bash
  docker-compose logs
  ```

- Asegúrate de que los puertos no estén en uso por otras aplicaciones:
  - 3306 (MariaDB)
  - 8001 (FastAPI)

- Si la base de datos no se inicializa correctamente, puedes intentar:
  ```bash
  docker-compose down -v  # Elimina los volúmenes
  docker-compose up -d    # Reinicia los contenedores
  ```

## 👥 Contribuir

1. Haz un fork del repositorio
2. Crea una nueva rama (`git checkout -b feature/nueva-caracteristica`)
3. Realiza tus cambios
4. Haz commit de tus cambios (`git commit -am 'Añade nueva característica'`)
5. Haz push a la rama (`git push origin feature/nueva-caracteristica`)
6. Crea un nuevo Pull Request

## 📄 Licencia

[MIT](LICENSE)
