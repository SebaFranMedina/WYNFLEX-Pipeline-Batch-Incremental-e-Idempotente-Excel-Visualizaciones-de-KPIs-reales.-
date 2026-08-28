-- WYNFLEX - Analytics
-- Consultas analíticas sobre el modelo dimensional

-- 1. Entregas por estado
SELECT
    e.estado,
    COUNT(*) AS total_entregas
FROM fact_entregas f
JOIN dim_estado e
    ON f.estado_key = e.estado_key
GROUP BY e.estado
ORDER BY total_entregas DESC;


-- 2. Entregas por día
SELECT
    d.fecha,
    COUNT(*) AS total_entregas
FROM fact_entregas f
JOIN dim_fecha d
    ON f.fecha_estado_key = d.fecha_key
GROUP BY d.fecha
ORDER BY d.fecha;


-- 3. Entregas por cadete
SELECT
    c.nombre_cadete,
    COUNT(*) AS total_entregas
FROM fact_entregas f
JOIN dim_cadete c
    ON f.cadete_key = c.cadete_key
GROUP BY c.nombre_cadete
ORDER BY total_entregas DESC;


-- 4. Entregas por cliente
SELECT
    c.nombre_fantasia,
    COUNT(*) AS total_entregas
FROM fact_entregas f
JOIN dim_cliente c
    ON f.cliente_key = c.cliente_key
GROUP BY c.nombre_fantasia
ORDER BY total_entregas DESC;


-- 5. Entregas por código postal
SELECT
    f.cp,
    COUNT(*) AS total_entregas
FROM fact_entregas f
GROUP BY f.cp
ORDER BY total_entregas DESC;


-- 6. KPI: cumplimiento en el mismo día
SELECT
    COUNT(*) AS total_entregadas,
    COUNT(*) FILTER (
        WHERE fecha_colecta::date = fecha_estado::date
    ) AS entregadas_mismo_dia,
    COUNT(*) FILTER (
        WHERE fecha_estado::date > fecha_colecta::date
    ) AS entregadas_despues,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE fecha_colecta::date = fecha_estado::date
        ) / COUNT(*),
        2
    ) AS same_day_rate_pct
FROM deliveries
WHERE LOWER(estado) = 'entregado';


-- 7. Demora por días
SELECT
    (fecha_estado::date - fecha_colecta::date) AS dias_demora,
    COUNT(*) AS entregas
FROM deliveries
WHERE LOWER(estado) = 'entregado'
  AND fecha_estado::date > fecha_colecta::date
GROUP BY dias_demora
ORDER BY dias_demora;


-- 8. Tasa de demora por cliente
SELECT
    nombre_fantasia,
    COUNT(*) AS total_entregadas,
    COUNT(*) FILTER (
        WHERE fecha_estado::date > fecha_colecta::date
    ) AS entregas_demoradas,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE fecha_estado::date > fecha_colecta::date
        ) / COUNT(*),
        2
    ) AS tasa_demora_pct
FROM deliveries
WHERE LOWER(estado) = 'entregado'
GROUP BY nombre_fantasia
HAVING COUNT(*) >= 10
ORDER BY tasa_demora_pct DESC;


-- 9. Tasa de demora por código postal
SELECT
    cp,
    COUNT(*) AS total_entregadas,
    COUNT(*) FILTER (
        WHERE fecha_estado::date > fecha_colecta::date
    ) AS entregas_demoradas,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE fecha_estado::date > fecha_colecta::date
        ) / COUNT(*),
        2
    ) AS tasa_demora_pct
FROM deliveries
WHERE LOWER(estado) = 'entregado'
  AND cp IS NOT NULL
GROUP BY cp
HAVING COUNT(*) >= 10
ORDER BY tasa_demora_pct DESC;


-- 10. Demora promedio y máxima por código postal
SELECT
    cp,
    COUNT(*) FILTER (
        WHERE fecha_estado::date > fecha_colecta::date
    ) AS entregas_demoradas,
    ROUND(
        AVG(
            fecha_estado::date - fecha_colecta::date
        ) FILTER (
            WHERE fecha_estado::date > fecha_colecta::date
        ),
        2
    ) AS demora_promedio_dias,
    MAX(
        fecha_estado::date - fecha_colecta::date
    ) FILTER (
        WHERE fecha_estado::date > fecha_colecta::date
    ) AS demora_maxima_dias
FROM deliveries
WHERE LOWER(estado) = 'entregado'
  AND cp IS NOT NULL
GROUP BY cp
HAVING COUNT(*) FILTER (
    WHERE fecha_estado::date > fecha_colecta::date
) > 0
ORDER BY demora_promedio_dias DESC;