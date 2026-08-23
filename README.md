WYNFLEX — Data Engineering Pipeline

Pipeline de Data Engineering desarrollado a partir de archivos Excel de una operación logística.

El proyecto implementa un flujo ETL batch que transforma archivos Excel en formato Parquet, carga los datos en PostgreSQL y construye un modelo dimensional basado en Star Schema.

Actualmente incorpora Docker, pytest y CI mediante GitHub Actions.

🏗️ Arquitectura

Excel → RAW → Transform → SILVER → PostgreSQL → Star Schema

Modelo dimensional

Fact table

fact_entregas

Dimensions

dim_cliente
dim_cadete
dim_estado
dim_zona
dim_fecha
🔄 Flujo ETL
Extract

Los archivos Excel representan reportes semanales de la operación logística.

Los archivos originales se almacenan en:

data/raw/

Transform

La transformación se realiza utilizando Python + Pandas.

Se realizan tareas como:

Limpieza de datos.
Eliminación de filas inválidas.
Normalización de fechas y texto.
Conversión de tipos.
Eliminación de duplicados.
Generación de archivos Parquet.

Los archivos transformados se almacenan en:

data/silver/

Load

Los archivos Parquet son cargados en PostgreSQL.

La tabla utilizada para la carga es:

deliveries

A partir de esta tabla se construye el modelo dimensional.

🛠️ Tecnologías
Data Engineering
Python
Pandas
Parquet
PostgreSQL
SQL
Star Schema
DevOps
Docker
Docker Compose
Git
GitHub
GitHub Actions
pytest
📁 Estructura del proyecto
.github/workflows/ci.yml
data/raw/
data/silver/
data/processed/
data/gold/
sql/
src/
tests/
.gitignore
docker-compose.yml
Dockerfile
pytest.ini
requirements.txt
README.md
🧪 Tests

El proyecto utiliza pytest para realizar tests automatizados.

Resultado actual:

1 passed

El test actual verifica el comportamiento de la transformación de los archivos de entrada.

⚙️ Continuous Integration

GitHub Actions ejecuta automáticamente el workflow ante cada push a master y ante Pull Requests.

El CI realiza:

Checkout → Python → Dependencies → Syntax Check → pytest → Docker Build

Estado actual: Success

📊 Datos procesados

El pipeline fue probado con 6 archivos Excel correspondientes a reportes semanales.

Resultado después de la transformación:

919 registros

Estados encontrados:

Entregado
Entregado 2DA visita
En camino al destinatario
En camino reprogramado
Nadie
🗺️ Roadmap
 Extracción de archivos Excel
 Transformación de datos
 Conversión a Parquet
 PostgreSQL
 Modelo dimensional
 Dockerización
 Tests
 GitHub Actions CI
 Azure Data Lake Storage Gen2
 Capa Gold
 Power BI
 Procesamiento incremental
 Logging y monitoreo
🎯 Objetivo

Construir progresivamente un pipeline de datos reproducible, escalable y orientado a producción, aplicando buenas prácticas de Data Engineering, Data Warehousing, Docker, Testing, CI/CD y Cloud Computing.