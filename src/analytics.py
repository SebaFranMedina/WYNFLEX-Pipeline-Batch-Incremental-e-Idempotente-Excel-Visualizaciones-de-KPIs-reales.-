import pandas as pd
from sqlalchemy import create_engine


DATABASE_URL = "postgresql+psycopg2://wynflex:wynflex@localhost:5432/wynflex"

engine = create_engine(DATABASE_URL)


def get_deliveries_by_day():
    query = """
        SELECT
            fecha_estado::date AS fecha,
            COUNT(*) AS total_entregas
        FROM deliveries
        WHERE LOWER(estado) = 'entregado'
        GROUP BY fecha_estado::date
        ORDER BY fecha;
    """

    return pd.read_sql_query(query, engine)


def get_deliveries_by_status():
    query = """
        SELECT
            estado,
            COUNT(*) AS total_entregas
        FROM deliveries
        GROUP BY estado
        ORDER BY total_entregas DESC;
    """

    return pd.read_sql_query(query, engine)


def get_same_day_kpi():
    query = """
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
    """

    return pd.read_sql_query(query, engine)


def get_delay_by_postal_code():
    query = """
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
    """

    return pd.read_sql_query(query, engine)


def get_deliveries_by_client():
    query = """
        SELECT
            nombre_fantasia,
            COUNT(*) AS total_entregas
        FROM deliveries
        WHERE nombre_fantasia IS NOT NULL
        GROUP BY nombre_fantasia
        ORDER BY total_entregas DESC;
    """

    return pd.read_sql_query(query, engine)


if __name__ == "__main__":

    print("\n=== KPI SAME DAY ===")
    print(get_same_day_kpi())

    print("\n=== ENTREGAS POR ESTADO ===")
    print(get_deliveries_by_status())

    print("\n=== ENTREGAS POR DÍA ===")
    print(get_deliveries_by_day())

    print("\n=== DEMORA POR CP ===")
    print(get_delay_by_postal_code())