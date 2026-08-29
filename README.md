# WYNFLEX — Data Engineering & Analytics Pipeline

Pipeline de Data Engineering desarrollado a partir de archivos Excel de una operación logística.

El proyecto implementa un flujo ETL batch que transforma reportes semanales de Excel en Parquet, carga los datos en PostgreSQL y construye un modelo dimensional basado en **Star Schema**.

Actualmente incorpora:

* Docker y Docker Compose
* PostgreSQL
* Python + Pandas
* Parquet
* Modelo dimensional
* pytest
* GitHub Actions
* Ingesta incremental e idempotente
* Análisis de datos con Plotly
* Enriquecimiento geográfico mediante geocoding

---

## 🏗️ Arquitectura

```text
Excel
  ↓
RAW
  ↓
Extract
  ↓
Transform
  ↓
SILVER (Parquet)
  ↓
PostgreSQL
  ↓
Star Schema
  ↓
Analytics
  ↓
Reporting / Visualización
```

### Enriquecimiento geográfico

```text
Dirección
    ↓
Normalización
    ↓
Geocoding
    ↓
Latitud + Longitud
    ↓
Barrio
    ↓
Analytics geográfico
```

---

## 🔄 Flujo ETL

### Extract

Los archivos Excel representan reportes semanales de la operación logística.

Los archivos originales se almacenan en:

```text
data/raw/
```

El proceso detecta automáticamente los archivos Excel disponibles para su procesamiento.

---

### Transform

La transformación se realiza utilizando **Python + Pandas**.

Se realizan tareas como:

* Limpieza de datos
* Eliminación de filas inválidas
* Eliminación de filas de resumen
* Normalización de fechas
* Normalización de texto
* Conversión de tipos
* Normalización de códigos postales
* Eliminación de duplicados por número de tracking
* Generación de archivos Parquet

Los archivos transformados se almacenan en:

```text
data/silver/
```

Los archivos Excel procesados correctamente se mueven a:

```text
data/processed/
```

---

### Load

Los archivos Parquet son cargados en PostgreSQL.

La tabla principal utilizada para la carga es:

```text
deliveries
```

La carga utiliza `source_file` para identificar los archivos ya procesados.

Esto permite una ingesta:

* **Incremental:** solamente se cargan archivos nuevos.
* **Idempotente:** ejecutar nuevamente el pipeline no duplica archivos ya cargados.

Ejemplo:

```text
Archivo nuevo      → cargar ✅
Archivo ya cargado → omitir  ⏭️
```

---

## ⭐ Modelo dimensional

A partir de `deliveries` se construye un modelo dimensional basado en Star Schema.

### Fact table

```text
fact_entregas
```

### Dimensions

```text
dim_cliente
dim_cadete
dim_estado
dim_zona
dim_fecha
```

---

## 📊 Analytics

El proyecto incluye un notebook de análisis:

```text
notebooks/01_wynflex_analytics.ipynb
```

Actualmente incorpora análisis como:

* KPI de entregas
* Entregas por estado
* Entregas por día
* Cantidad de pedidos por barrio
* Análisis geográfico
* Visualizaciones interactivas con Plotly

---

## 🗺️ Enriquecimiento geográfico

Las direcciones de entrega son normalizadas y geocodificadas para obtener información geográfica adicional.

El proceso puede obtener:

```text
dirección
barrio
latitud
longitud
código postal geocodificado
```

Los resultados se almacenan en una caché para evitar volver a geocodificar direcciones ya procesadas.

Esto permite reutilizar una misma ubicación cuando una dirección aparece en múltiples entregas o en diferentes semanas.

---

## 🛠️ Tecnologías

### Data Engineering

* Python
* Pandas
* PostgreSQL
* SQL
* Parquet
* Star Schema

### Analytics

* Jupyter Notebook
* Plotly

### DevOps

* Docker
* Docker Compose
* Git
* GitHub
* GitHub Actions
* pytest

### Geospatial

* Geocoding
* OpenStreetMap / Nominatim

---

## 📁 Estructura del proyecto

```text
.github/
└── workflows/
    └── ci.yml

data/
├── raw/
├── processed/
├── silver/
└── gold/

notebooks/
├── 01_wynflex_analytics.ipynb
└── geocoding_cache.csv

sql/
├── analytics.sql
└── create_dimensional_model.sql

src/
├── extract.py
├── transform.py
├── load.py
├── model.py
├── analytics.py
├── visualizations.py
├── inspect_excel.py
└── test_geocoding.py

tests/
└── test_transform.py

Dockerfile
docker-compose.yml
pytest.ini
requirements.txt
README.md
```

---

## 🧪 Tests

El proyecto utiliza **pytest** para realizar tests automatizados.

El test actual verifica el comportamiento de la transformación de los archivos de entrada.

---

## ⚙️ Continuous Integration

GitHub Actions ejecuta automáticamente el workflow ante cada push a `master` y ante Pull Requests.

El CI realiza:

```text
Checkout
   ↓
Python
   ↓
Dependencies
   ↓
Syntax Check
   ↓
pytest
   ↓
Docker Build
```

Estado actual:

```text
Success ✅
```

---

## 📈 Datos procesados

El pipeline actualmente fue probado con:

* **8 archivos** de reportes semanales
* **1.254 entregas** cargadas en PostgreSQL
* múltiples estados operativos de entrega

Estados encontrados incluyen:

```text
Entregado
Entregado 2DA visita
En camino al destinatario
En camino reprogramado
Nadie
```

---

## 🔄 Procesamiento incremental

El pipeline permite incorporar nuevos reportes semanales sin recargar nuevamente los archivos ya procesados.

Ejemplo:

```text
Semanas anteriores
      ↓
919 entregas
      ↓
Nueva semana
      ↓
+135
      ↓
Nueva semana
      ↓
+200
      ↓
1254 entregas
```

Si el pipeline vuelve a ejecutarse con los mismos archivos:

```text
1254
 ↓
0 nuevos archivos
 ↓
1254
```

Esto garantiza un comportamiento **idempotente**.

---

## 🗺️ Roadmap

### Implementado

* [x] Extracción de archivos Excel
* [x] Transformación de datos
* [x] Conversión a Parquet
* [x] PostgreSQL
* [x] Modelo dimensional
* [x] Dockerización
* [x] Tests
* [x] GitHub Actions CI
* [x] Procesamiento incremental
* [x] Carga idempotente
* [x] Analytics con Plotly
* [x] Geocoding y enriquecimiento geográfico

### Próximas etapas

* [ ] Azure Data Lake Storage Gen2
* [ ] Capa Gold
* [ ] Integración con Power BI
* [ ] Logging
* [ ] Monitoreo
* [ ] Mejoras de calidad y validación de direcciones
* [ ] Automatización completa del pipeline

---

## 🎯 Objetivo

Construir progresivamente un pipeline de datos reproducible, escalable y orientado a producción, aplicando buenas prácticas de:

* Data Engineering
* ETL
* Data Warehousing
* Analytics
* Docker
* Testing
* CI/CD
* Cloud Computing

El proyecto busca además transformar datos operativos de una empresa logística en **información útil para reporting y toma de decisiones**.
