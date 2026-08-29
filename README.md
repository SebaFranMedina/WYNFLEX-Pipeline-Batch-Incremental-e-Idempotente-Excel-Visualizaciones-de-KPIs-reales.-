# WYNFLEX — Data Engineering & Analytics Pipeline

Pipeline de **Data Engineering y Analytics** desarrollado a partir de archivos Excel provenientes de una operación logística real.

El proyecto transforma reportes operativos semanales en un flujo de datos reproducible para consolidar entregas, realizar análisis operativos y generar información útil para reporting y toma de decisiones.

Actualmente implementa:

* ETL batch con Python y Pandas.
* Conversión de Excel a Apache Parquet.
* PostgreSQL como base de datos operacional.
* Carga incremental e idempotente.
* Modelo dimensional basado en Star Schema.
* Docker y Docker Compose.
* Tests automatizados con pytest.
* Continuous Integration mediante GitHub Actions.
* Analytics mediante SQL, Pandas y Plotly.
* Normalización y geocoding de direcciones.
* Construcción de un dataset geográfico reutilizable de WYNFLEX.

---

# 🏗️ Arquitectura actual

```text
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
                   analytics.ipynb
```

## Enriquecimiento geográfico

```text
Direcciones de entregas
          │
          ▼
Normalización
          │
          ▼
Geocoding
          │
          ├── Latitud
          ├── Longitud
          ├── Barrio
          └── Código postal
                  │
                  ▼
       Dataset geográfico WYNFLEX
                  │
                  ▼
              Analytics
```

---

# 🔄 Flujo ETL

## 1. Extract — `src/extract.py`

Los archivos Excel representan reportes semanales de la operación logística.

Entrada:

```text
data/raw/*.xlsx
```

El proceso:

* detecta automáticamente archivos Excel;
* lee los archivos utilizando Pandas;
* informa cantidad de filas y columnas;
* genera los DataFrames de entrada para las siguientes etapas.

---

## 2. Transform — `src/transform.py`

La transformación se realiza individualmente sobre cada archivo.

Procesos implementados:

* eliminación de filas completamente vacías;
* eliminación de registros sin número de tracking;
* eliminación de filas de resumen;
* conversión de fechas;
* normalización de texto;
* conversión de códigos postales;
* eliminación de duplicados por `numero_tracking`;
* generación de archivos Parquet;
* movimiento del Excel procesado a `data/processed/`.

Entrada:

```text
data/raw/*.xlsx
```

Salida:

```text
data/silver/*.parquet
```

Archivos originales procesados correctamente:

```text
data/processed/*.xlsx
```

---

# 📥 Carga incremental e idempotente — `src/load.py`

Los archivos Parquet son cargados en PostgreSQL mediante la tabla:

```text
deliveries
```

Cada registro conserva el archivo de origen mediante:

```text
source_file
```

Esto permite identificar qué reportes ya fueron cargados.

## Procesamiento incremental

El loader compara los archivos existentes en `data/silver/` con los valores de `source_file` almacenados en PostgreSQL.

```text
Parquet nuevo
     │
     ▼
¿source_file existe?
   │           │
  NO          SÍ
   │           │
   ▼           ▼
 cargar      omitir
```

Por lo tanto:

* los archivos nuevos son incorporados;
* los archivos ya procesados no vuelven a cargarse;
* no es necesario realizar un `TRUNCATE` de `deliveries`.

## Idempotencia

La ejecución repetida del pipeline con los mismos archivos no genera duplicados.

Ejemplo real:

```text
Carga existente:
919 entregas

20-08-2026:
+135

27-08-2026:
+200

Total:
1254 entregas
```

Al ejecutar nuevamente con los mismos archivos:

```text
Archivos nuevos:
0

Total:
1254
```

Esto permite incorporar nuevas semanas manteniendo la información histórica existente.

---

# ⭐ Modelo dimensional — `src/model.py`

A partir de `deliveries` se construye un modelo dimensional basado en **Star Schema**.

## Fact table

```text
fact_entregas
```

## Dimensions

```text
dim_cliente
dim_cadete
dim_estado
dim_zona
dim_fecha
```

### `dim_fecha`

La dimensión de fechas contiene atributos derivados:

```text
fecha_key
fecha
dia
mes
nombre_mes
trimestre
año
dia_semana
nombre_dia
```

El modelo permite separar los datos operativos del modelo utilizado para análisis y reporting.

---

# 🗺️ Dataset geográfico de WYNFLEX

Una de las capacidades desarrolladas durante el proyecto fue la creación de un **dataset geográfico propio de las direcciones de entrega**.

En lugar de consultar el servicio de geocoding cada vez que una dirección aparece en una nueva entrega, las direcciones se almacenan en un cache reutilizable.

Archivo actual:

```text
notebooks/geocoding_cache.csv
```

Cada dirección puede contener información como:

```text
direccion_original
direccion_limpia
lat
lon
barrio
cp_geocodificado
display_name
geocoding_status
```

## Ventaja del dataset

Las entregas pueden repetirse durante diferentes días o semanas.

Por ejemplo:

```text
Dirección A
   │
   ├── entrega 01/07
   ├── entrega 08/07
   ├── entrega 15/07
   └── entrega 22/07
```

La dirección se geocodifica una sola vez y luego el resultado se reutiliza.

Esto permite separar:

```text
Entregas
```

de:

```text
Ubicaciones geográficas
```

y evita consultas y procesamiento duplicados.

## Estrategia de geocoding

El proceso utiliza búsquedas progresivas:

```text
1. Dirección completa
        │
        ├── encontrada → guardar
        │
        └── no encontrada
                ↓

2. Última palabra + altura + CP
        │
        ├── encontrada → guardar
        │
        └── no encontrada
                ↓

3. Intersección + CP
        │
        ├── encontrada → guardar
        │
        └── no encontrada
                ↓

              not_found
```

Las intersecciones se tratan específicamente para casos como:

```text
Riestra y Portela
Riestra y Mariano Acosta
```

## Validación geográfica

Además del resultado del geocoder, se utiliza el código postal original de la operación como una segunda capa de validación.

```text
CP del Excel
      │
      ▼
CP devuelto por geocoder
      │
      ├── coincide → ✅
      └── diferente → ⚠️ revisar
```

El código postal se utiliza como mecanismo de **reafirmación de calidad**, no como único criterio para aceptar o rechazar una coordenada.

## Estado del dataset geográfico

Actualmente se procesaron:

```text
1.338 direcciones únicas
```

Resultado:

```text
found             928
found_palabra     393
found_v2            1
not_found          16
----------------------
Total            1338
```

Direcciones encontradas:

```text
1322 / 1338
≈ 98,8 %
```

Esto permitió enriquecer las entregas con información de barrio y coordenadas.

---

# 📊 Analytics — `src/analytics.py`

Las funciones de analytics consultan PostgreSQL y preparan información para el notebook.

Actualmente incluye análisis relacionados con:

```text
get_same_day_kpi()
get_deliveries_by_status()
get_deliveries_by_day()
get_deliveries_by_client()
```

El proyecto utiliza SQL y Pandas para generar indicadores y agregaciones.

---

# 📓 Notebook — `notebooks/01_wynflex_analytics.ipynb`

El notebook funciona como capa de **Analytics y Reporting**.

Actualmente incluye:

## KPI

Indicador de entregas same-day.

## Entregas por estado

Cantidad de entregas agrupadas por estado y porcentaje de eficiencia del cadete.

La eficiencia se calcula como:

```text
Entregadas / Total de entregas × 100
```

## Entregas por día

Visualización de la evolución diaria de entregas mediante barras verticales.

## Entregas por cliente

Ranking de los **Top 30 clientes** por cantidad de entregas.

## Pedidos por barrio

Ranking de los **Top 20 barrios** por cantidad de pedidos.

Todos los gráficos incluyen el período de días analizados para contextualizar los resultados.

---

# 📈 Datos actuales

El pipeline fue evolucionando mediante la incorporación de reportes semanales.

Actualmente PostgreSQL contiene:

```text
1.254 entregas
```

Luego se incorporaron nuevas cargas para continuar la evolución del dataset.

Durante el procesamiento geográfico actual se identificaron:

```text
1.338 direcciones únicas
```

La cantidad de direcciones puede ser mayor al número de archivos debido a que una misma dirección puede aparecer en distintas entregas y semanas.

Estados operativos encontrados:

```text
Entregado
Entregado 2DA visita
En camino al destinatario
En camino reprogramado
Nadie
```

---

# 🧪 Testing

El proyecto utiliza `pytest` para realizar pruebas automatizadas.

Test principal:

```text
tests/test_transform.py
```

El test verifica el comportamiento de la transformación de los archivos de entrada.

Estado actual:

```text
1 passed
```

También existe:

```text
src/test_geocoding.py
```

para pruebas relacionadas con el proceso de geocoding.

---

# ⚙️ Continuous Integration

GitHub Actions ejecuta automáticamente el proceso de integración continua ante:

```text
push → master
Pull Request
```

El workflow realiza:

```text
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
```

Estado actual:

```text
CI → Success ✅
```

---

# 🐳 Docker

El proyecto está dockerizado mediante:

```text
Dockerfile
docker-compose.yml
```

PostgreSQL se ejecuta mediante Docker Compose.

El entorno de desarrollo utiliza:

```text
WSL
Python virtual environment
VS Code
Docker
PostgreSQL
```

---

# 🛠️ Tecnologías

## Data Engineering

* Python
* Pandas
* SQL
* PostgreSQL
* Apache Parquet
* Star Schema

## Analytics

* Jupyter Notebook
* Pandas
* Plotly

## Geospatial

* OpenStreetMap
* Nominatim
* Geocoding
* Address normalization
* Geographic enrichment
* Dataset geográfico reutilizable

## DevOps

* Docker
* Docker Compose
* Git
* GitHub
* GitHub Actions
* pytest

---

# 📁 Estructura del proyecto

```text
WYNFLEX/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── silver/
│   └── gold/
│
├── notebooks/
│   ├── 01_wynflex_analytics.ipynb
│   └── geocoding_cache.csv
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
│   ├── visualizations.py
│   └── test_geocoding.py
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
```

---

# ✅ Implementado

* [x] Extracción de archivos Excel
* [x] Limpieza y transformación de datos
* [x] Conversión a Parquet
* [x] Separación RAW / SILVER / PROCESSED
* [x] PostgreSQL
* [x] Carga desde Parquet
* [x] Trazabilidad mediante `source_file`
* [x] Procesamiento incremental
* [x] Carga idempotente
* [x] Star Schema
* [x] Dimensiones de cliente, cadete, estado, zona y fecha
* [x] Docker
* [x] Docker Compose
* [x] pytest
* [x] GitHub Actions
* [x] Continuous Integration
* [x] Analytics con SQL + Pandas
* [x] Visualizaciones con Plotly
* [x] Normalización de direcciones
* [x] Geocoding
* [x] Cache de direcciones
* [x] Dataset geográfico de WYNFLEX
* [x] Enriquecimiento con barrio y coordenadas
* [x] Análisis de pedidos por barrio
* [x] Analytics por cliente
* [x] Analytics por día
* [x] KPI operativo

---

# 🚧 Roadmap

## Próximas etapas

* [ ] Mejorar la resolución de direcciones restantes
* [ ] Mover el cache geográfico desde `notebooks/` hacia una ubicación de datos dedicada
* [ ] Incorporar formalmente una capa GOLD
* [ ] Azure Data Lake Storage Gen2
* [ ] Integración con Power BI
* [ ] Dashboard orientado a reporting operativo
* [ ] Logging estructurado
* [ ] Monitoreo
* [ ] Alertas
* [ ] **Continuous Deployment (CD)**
* [ ] Automatización completa del pipeline
* [ ] Evaluar Spark cuando el volumen de datos lo justifique

---

# 🎯 Objetivo

Construir progresivamente un pipeline de datos **reproducible, incremental, idempotente y orientado a producción**, aplicando buenas prácticas de:

* Data Engineering
* ETL
* Data Warehousing
* Analytics
* Data Quality
* Geospatial Data
* Docker
* Testing
* Continuous Integration
* Continuous Deployment
* Cloud Computing

El proyecto busca transformar datos operativos de una empresa logística en **información útil para reporting, análisis de la operación y toma de decisiones**.

La evolución prevista es:

```text
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
```
