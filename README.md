WYNFLEX — Data Engineering & Analytics Pipeline

Pipeline de Data Engineering y Analytics creado desde cero a partir de los conocimientos adquiridos durante mi formación en Data Engineering, aplicado a un caso real de una operación logística.

El proyecto transforma reportes operativos semanales en Excel en un flujo de datos reproducible para consolidar entregas, realizar análisis operativos y generar información útil para reporting y toma de decisiones.

Actualmente implementa:

ETL batch con Python y Pandas.
Conversión de Excel a Apache Parquet.
PostgreSQL como base de datos operacional.
Carga incremental e idempotente.
Modelo dimensional basado en Star Schema.
Docker y Docker Compose.
Tests automatizados con pytest.
Continuous Integration mediante GitHub Actions.
Analytics mediante SQL y Pandas.
Visualizaciones mediante Matplotlib.
Normalización y geocoding de direcciones.
Construcción de un dataset geográfico reutilizable de WYNFLEX.
🏗️ Arquitectura actual
                         WYNFLEX
                            │
                    Reportes Excel
                            │
                            ▼
                     ┌─────────────┐
                     │    RAW      │
                     │ data/raw/   │
                     └──────┬──────┘
                            │
                            ▼
                       extract.py
                            │
                            ▼
                      transform.py
                            │
                            ▼
                     ┌─────────────┐
                     │   SILVER    │
                     │   Parquet   │
                     │ data/silver │
                     └──────┬──────┘
                            │
                            ▼
                         load.py
                            │
                            ▼
                     ┌─────────────┐
                     │ PostgreSQL  │
                     │ deliveries  │
                     └──────┬──────┘
                            │
                            ▼
                         model.py
                            │
                            ▼
                  ┌─────────────────────┐
                  │     Star Schema     │
                  │                     │
                  │ fact_entregas       │
                  │ dim_cliente         │
                  │ dim_cadete          │
                  │ dim_estado          │
                  │ dim_zona            │
                  │ dim_fecha           │
                  └──────────┬──────────┘
                             │
                             ▼
                       analytics.py
                             │
                             ▼
              01_wynflex_analytics.ipynb
                             │
                             ▼
                    KPIs + Matplotlib
🔄 Flujo ETL
1. Extract — src/extract.py

Los archivos Excel representan reportes semanales reales de la operación logística.

Entrada:

data/raw/*.xlsx

El proceso detecta automáticamente los archivos Excel y prepara los datos para las siguientes etapas del pipeline.

2. Transform — src/transform.py

Cada archivo es procesado individualmente.

Procesos implementados:

Eliminación de filas completamente vacías.
Eliminación de registros sin número de tracking.
Eliminación de filas de resumen.
Conversión y normalización de fechas.
Normalización de texto.
Conversión de códigos postales.
Eliminación de duplicados por numero_tracking.
Generación de archivos Parquet.
Movimiento del Excel procesado a data/processed/.

Entrada:

data/raw/*.xlsx

Salida:

data/silver/*.parquet

Archivos originales procesados:

data/processed/*.xlsx
📥 Carga incremental e idempotente — src/load.py

Los archivos Parquet son cargados en PostgreSQL mediante la tabla:

deliveries

Cada registro conserva el archivo de origen mediante:

source_file

Esto permite identificar qué reportes ya fueron cargados.

Procesamiento incremental

El loader compara los archivos existentes en data/silver/ con los valores de source_file almacenados en PostgreSQL.

Parquet nuevo
     │
     ▼
¿source_file existe?
   │           │
  NO          SÍ
   │           │
   ▼           ▼
 cargar      omitir

Los archivos nuevos son incorporados y los que ya fueron procesados no vuelven a cargarse.

Idempotencia

La ejecución repetida del pipeline con los mismos archivos no genera nuevas cargas.

En otras palabras:

Mismos archivos
      ↓
Mismo resultado

Si se incorpora una nueva semana:

Datos existentes
      +
Nuevo Excel
      ↓
Solo se incorpora el nuevo archivo
⭐ Modelo dimensional — src/model.py

A partir de deliveries se construye un modelo dimensional basado en Star Schema.

Fact table
fact_entregas
Dimensions
dim_cliente
dim_cadete
dim_estado
dim_zona
dim_fecha

La dimensión de fechas contiene atributos derivados como:

fecha_key
fecha
dia
mes
nombre_mes
trimestre
año
dia_semana
nombre_dia

Este modelo separa los datos operativos de las estructuras utilizadas para análisis y reporting.

🗺️ Dataset geográfico de WYNFLEX

Durante el proyecto se desarrolló un dataset geográfico reutilizable para las direcciones de entrega.

El proceso normaliza las direcciones y utiliza geocoding para obtener información como:

direccion_original
direccion_limpia
lat
lon
barrio
cp_geocodificado
display_name
geocoding_status

Las direcciones se almacenan en un cache reutilizable para evitar repetir consultas sobre ubicaciones ya procesadas.

Actualmente se procesaron:

1.338 direcciones únicas

Resultado:

found             928
found_palabra     393
found_v2            1
not_found          16
----------------------
Total            1338

Esto permitió enriquecer los datos de las entregas con información geográfica como barrio y coordenadas.

📊 Analytics — src/analytics.py

Las funciones de Analytics consultan PostgreSQL y preparan los datos utilizados por el notebook.

Actualmente incluye funciones para analizar:

get_same_day_kpi()
get_deliveries_by_status()
get_deliveries_by_day()
get_deliveries_by_client()

El análisis combina SQL y Pandas para generar KPIs y agregaciones operativas.

📓 Notebook — notebooks/01_wynflex_analytics.ipynb

El notebook funciona como capa de Analytics y Reporting del proyecto.

A partir del modelo almacenado en PostgreSQL se generan KPIs y visualizaciones con Matplotlib.

KPI de eficiencia

Se calcula la eficiencia de entregas como:

Entregadas / Total de entregas × 100
Entregas por estado

Permite analizar la distribución de las entregas según su estado y visualizar la eficiencia del período analizado.

Entregas por día

Muestra la evolución diaria del volumen de entregas.

Top 30 clientes

Ranking de los principales clientes según cantidad de entregas.

Top 15 barrios

Distribución de pedidos entregados según los barrios geocodificados.

Flujo diario de los Top 3 clientes

Analiza la variación diaria del volumen de pedidos recibido por los tres principales clientes.

📈 Visualizaciones

Las visualizaciones se generan mediante Matplotlib y se almacenan en:

outputs/visualizaciones/
Entregas por estado




Entregas realizadas por día




Top 30 clientes




Top 15 barrios




Flujo diario — Top 3 clientes










🧪 Testing

El proyecto utiliza pytest para realizar pruebas automatizadas.

Test principal:

tests/test_transform.py

También existen pruebas relacionadas con el proceso de geocoding.

⚙️ Continuous Integration

GitHub Actions ejecuta automáticamente el proceso de integración continua ante:

push → master
Pull Request

El workflow realiza:

Checkout
   ↓
Setup Python
   ↓
Install Dependencies
   ↓
Syntax Check
   ↓
pytest
   ↓
Docker Build
🐳 Docker

El proyecto está dockerizado mediante:

Dockerfile
docker-compose.yml

PostgreSQL se ejecuta mediante Docker Compose.

Entorno utilizado:

WSL
Python virtual environment
VS Code
Docker
PostgreSQL
🛠️ Tecnologías
Data Engineering
Python
Pandas
SQL
PostgreSQL
Apache Parquet
Star Schema
Analytics
Jupyter Notebook
Pandas
Matplotlib
Geospatial
OpenStreetMap
Nominatim
Geocoding
Address normalization
Geographic enrichment
Dataset geográfico reutilizable
DevOps
Docker
Docker Compose
Git
GitHub
GitHub Actions
pytest
📁 Estructura del proyecto
WYNFLEX/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── silver/
│
├── notebooks/
│   ├── 01_wynflex_analytics.ipynb
│   └── geocoding_cache.csv
│
├── outputs/
│   └── visualizaciones/
│       ├── 01_entregas_por_estado.png
│       ├── 02_entregas_por_dia.png
│       ├── 03_top_30_clientes.png
│       ├── 04_top_15_barrios.png
│       ├── 05_cliente_top_1.png
│       ├── 05_cliente_top_2.png
│       └── 05_cliente_top_3.png
│
├── sql/
│   ├── analytics.sql
│   └── create_dimensional_model.sql
│
├── src/
│   ├── __init__.py
│   ├── extract.py
│   ├── inspect_excel.py
│   ├── transform.py
│   ├── load.py
│   ├── model.py
│   ├── analytics.py
│   └── visualizations.py
│
├── tests/
│   └── test_transform.py
│
├── Dockerfile
├── docker-compose.yml
├── pytest.ini
├── requirements.txt
├── .gitignore
└── README.md
✅ Implementado

Extracción de archivos Excel

Limpieza y transformación de datos

Conversión a Parquet

Separación RAW / SILVER / PROCESSED

PostgreSQL

Trazabilidad mediante source_file

Procesamiento incremental

Carga idempotente

Star Schema

Dimensiones de cliente, cadete, estado, zona y fecha

Docker

Docker Compose

pytest

GitHub Actions

Continuous Integration

Analytics con SQL + Pandas

Visualizaciones con Matplotlib

Normalización de direcciones

Geocoding

Cache de direcciones

Dataset geográfico de WYNFLEX

Enriquecimiento con barrio y coordenadas

Análisis de pedidos por barrio

Analytics por cliente

Analytics por día

KPI operativo

🚧 Roadmap

Mejorar la resolución de direcciones restantes.

Mover el cache geográfico hacia una ubicación de datos dedicada.

Incorporar formalmente una capa GOLD.

Migrar parte de la arquitectura a Azure Data Lake Storage Gen2.

Integración con Power BI.

Dashboard orientado a reporting operativo.

Logging estructurado.

Monitoreo.

Alertas.

Continuous Deployment (CD).

Automatización completa del pipeline.

Evaluar Spark cuando el volumen de datos lo justifique.

🎯 Objetivo

Construir progresivamente un pipeline de datos reproducible, incremental, idempotente y orientado a producción, aplicando buenas prácticas de:

Data Engineering
ETL
Data Warehousing
Analytics
Data Quality
Geospatial Data
Docker
Testing
Continuous Integration
Continuous Deployment
Cloud Computing

WYNFLEX nació a partir de una necesidad real de la operación logística y busca transformar datos operativos en información útil para reporting, análisis del rendimiento y toma de decisiones.

La evolución prevista es:

Excel
  ↓
ETL
  ↓
Parquet
  ↓
PostgreSQL
  ↓
Star Schema
  ↓
Analytics
  ↓
Dataset Geográfico
  ↓
Power BI
  ↓
Azure
  ↓
Automatización / CD
