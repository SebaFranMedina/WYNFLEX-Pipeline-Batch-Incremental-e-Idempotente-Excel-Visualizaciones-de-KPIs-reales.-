-- ============================================
-- WYNFLEX - MODELO DIMENSIONAL
-- Star Schema
-- ============================================

-- ============================================
-- DIMENSION: CLIENTE
-- ============================================

CREATE TABLE IF NOT EXISTS dim_cliente (
    cliente_key SERIAL PRIMARY KEY,
    nombre_fantasia VARCHAR(255) NOT NULL UNIQUE
);


-- ============================================
-- DIMENSION: CADETE
-- ============================================

CREATE TABLE IF NOT EXISTS dim_cadete (
    cadete_key SERIAL PRIMARY KEY,
    nombre_cadete VARCHAR(255) NOT NULL UNIQUE
);


-- ============================================
-- DIMENSION: ESTADO
-- ============================================

CREATE TABLE IF NOT EXISTS dim_estado (
    estado_key SERIAL PRIMARY KEY,
    estado VARCHAR(100) NOT NULL UNIQUE
);


-- ============================================
-- DIMENSION: ZONA
-- ============================================

CREATE TABLE IF NOT EXISTS dim_zona (
    zona_key SERIAL PRIMARY KEY,
    zona VARCHAR(100) NOT NULL UNIQUE
);


-- ============================================
-- DIMENSION: FECHA
-- ============================================

CREATE TABLE IF NOT EXISTS dim_fecha (
    fecha_key INTEGER PRIMARY KEY,
    fecha DATE NOT NULL UNIQUE,
    dia INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    nombre_mes VARCHAR(20) NOT NULL,
    trimestre INTEGER NOT NULL,
    año INTEGER NOT NULL,
    dia_semana INTEGER NOT NULL,
    nombre_dia VARCHAR(20) NOT NULL
);


-- ============================================
-- FACT TABLE: ENTREGAS
-- ============================================

CREATE TABLE IF NOT EXISTS fact_entregas (
    entrega_key BIGSERIAL PRIMARY KEY,

    tracking VARCHAR(100) NOT NULL,

    fecha_colecta_key INTEGER NOT NULL,
    fecha_estado_key INTEGER NOT NULL,

    cliente_key INTEGER NOT NULL,
    cadete_key INTEGER NOT NULL,
    estado_key INTEGER NOT NULL,
    zona_key INTEGER NOT NULL,

    codigo_postal INTEGER,

    precio_chofer NUMERIC(12, 2),
    porcentaje_chofer NUMERIC(5, 2),

    CONSTRAINT fk_fecha_colecta
        FOREIGN KEY (fecha_colecta_key)
        REFERENCES dim_fecha(fecha_key),

    CONSTRAINT fk_fecha_estado
        FOREIGN KEY (fecha_estado_key)
        REFERENCES dim_fecha(fecha_key),

    CONSTRAINT fk_cliente
        FOREIGN KEY (cliente_key)
        REFERENCES dim_cliente(cliente_key),

    CONSTRAINT fk_cadete
        FOREIGN KEY (cadete_key)
        REFERENCES dim_cadete(cadete_key),

    CONSTRAINT fk_estado
        FOREIGN KEY (estado_key)
        REFERENCES dim_estado(estado_key),

    CONSTRAINT fk_zona
        FOREIGN KEY (zona_key)
        REFERENCES dim_zona(zona_key)
);


-- ============================================
-- INDICES
-- ============================================

CREATE INDEX IF NOT EXISTS idx_fact_entregas_tracking
    ON fact_entregas(tracking);

CREATE INDEX IF NOT EXISTS idx_fact_entregas_fecha_colecta
    ON fact_entregas(fecha_colecta_key);

CREATE INDEX IF NOT EXISTS idx_fact_entregas_fecha_estado
    ON fact_entregas(fecha_estado_key);

CREATE INDEX IF NOT EXISTS idx_fact_entregas_cliente
    ON fact_entregas(cliente_key);

CREATE INDEX IF NOT EXISTS idx_fact_entregas_cadete
    ON fact_entregas(cadete_key);

CREATE INDEX IF NOT EXISTS idx_fact_entregas_estado
    ON fact_entregas(estado_key);

CREATE INDEX IF NOT EXISTS idx_fact_entregas_zona
    ON fact_entregas(zona_key);
