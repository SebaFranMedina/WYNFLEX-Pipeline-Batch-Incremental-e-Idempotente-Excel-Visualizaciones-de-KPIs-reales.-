from datetime import datetime
import psycopg2


DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "wynflex",
    "user": "wynflex",
    "password": "wynflex",
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def populate_dimensions(conn):
    cursor = conn.cursor()

    print("Poblando dim_cliente...")
    cursor.execute("""
        INSERT INTO dim_cliente (nombre_fantasia)
        SELECT DISTINCT nombre_fantasia
        FROM deliveries
        WHERE nombre_fantasia IS NOT NULL
        ON CONFLICT (nombre_fantasia) DO NOTHING;
    """)

    print("Poblando dim_cadete...")
    cursor.execute("""
        INSERT INTO dim_cadete (nombre_cadete)
        SELECT DISTINCT cadete
        FROM deliveries
        WHERE cadete IS NOT NULL
        ON CONFLICT (nombre_cadete) DO NOTHING;
    """)

    print("Poblando dim_estado...")
    cursor.execute("""
        INSERT INTO dim_estado (estado)
        SELECT DISTINCT COALESCE(estado, 'Sin estado')
        FROM deliveries
        ON CONFLICT (estado) DO NOTHING;
    """)

    print("Poblando dim_zona...")
    cursor.execute("""
        INSERT INTO dim_zona (zona)
        SELECT DISTINCT zona
        FROM deliveries
        WHERE zona IS NOT NULL
        ON CONFLICT (zona) DO NOTHING;
    """)

    conn.commit()

    cursor.close()


def populate_dates(conn):
    cursor = conn.cursor()

    print("Poblando dim_fecha...")

    cursor.execute("""
        SELECT fecha_colecta
        FROM deliveries
        WHERE fecha_colecta IS NOT NULL

        UNION

        SELECT fecha_estado
        FROM deliveries
        WHERE fecha_estado IS NOT NULL;
    """)

    rows = cursor.fetchall()

    dates = set()

    for row in rows:
        value = row[0]

        if value is None:
            continue

        if isinstance(value, datetime):
            dates.add(value.date())
        else:
            dates.add(value)

    for date_value in dates:
        fecha_key = int(date_value.strftime("%Y%m%d"))

        cursor.execute(
            """
            INSERT INTO dim_fecha (
                fecha_key,
                fecha,
                dia,
                mes,
                nombre_mes,
                trimestre,
                año,
                dia_semana,
                nombre_dia
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (fecha_key) DO NOTHING;
            """,
            (
                fecha_key,
                date_value,
                date_value.day,
                date_value.month,
                date_value.strftime("%B"),
                (date_value.month - 1) // 3 + 1,
                date_value.year,
                date_value.isoweekday(),
                date_value.strftime("%A"),
            ),
        )

    conn.commit()

    cursor.close()


def populate_fact_table(conn):
    cursor = conn.cursor()

    print("Poblando fact_entregas...")

    cursor.execute("TRUNCATE TABLE fact_entregas RESTART IDENTITY;")

    cursor.execute("""
        SELECT
            d.numero_tracking,
            d.fecha_colecta,
            d.fecha_estado,
            d.nombre_fantasia,
            d.cadete,
            d.estado,
            d.zona,
            d.cp,
            d.precio_chofer,
            d.porcentaje_chofer
        FROM deliveries d;
    """)

    rows = cursor.fetchall()

    for row in rows:
        (
            tracking,
            fecha_colecta,
            fecha_estado,
            nombre_fantasia,
            cadete,
            estado,
            zona,
            codigo_postal,
            precio_chofer,
            porcentaje_chofer,
        ) = row

        if tracking is None:
            continue

        if fecha_colecta is None or fecha_estado is None:
            continue

        fecha_colecta_key = int(fecha_colecta.strftime("%Y%m%d"))
        fecha_estado_key = int(fecha_estado.strftime("%Y%m%d"))

        estado = estado if estado is not None else "Sin estado"

        cursor.execute(
            """
            INSERT INTO fact_entregas (
                tracking,
                fecha_colecta_key,
                fecha_estado_key,
                cliente_key,
                cadete_key,
                estado_key,
                zona_key,
                codigo_postal,
                precio_chofer,
                porcentaje_chofer
            )
            VALUES (
                %s,
                %s,
                %s,
                (SELECT cliente_key
                 FROM dim_cliente
                 WHERE nombre_fantasia = %s),

                (SELECT cadete_key
                 FROM dim_cadete
                 WHERE nombre_cadete = %s),

                (SELECT estado_key
                 FROM dim_estado
                 WHERE estado = %s),

                (SELECT zona_key
                 FROM dim_zona
                 WHERE zona = %s),

                %s,
                %s,
                %s
            );
            """,
            (
                tracking,
                fecha_colecta_key,
                fecha_estado_key,
                nombre_fantasia,
                cadete,
                estado,
                zona,
                codigo_postal,
                precio_chofer,
                porcentaje_chofer,
            ),
        )

    conn.commit()

    cursor.close()

    print(f"  Filas insertadas en fact_entregas: {len(rows)}")


def show_results(conn):
    cursor = conn.cursor()

    print("\n" + "=" * 50)
    print("RESULTADO DEL MODELO DIMENSIONAL")
    print("=" * 50)

    tables = [
        "dim_cliente",
        "dim_cadete",
        "dim_estado",
        "dim_zona",
        "dim_fecha",
        "fact_entregas",
    ]

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        count = cursor.fetchone()[0]

        print(f"{table}: {count}")

    cursor.close()


def main():
    print("Conectando a PostgreSQL...")

    conn = get_connection()

    try:
        populate_dimensions(conn)
        populate_dates(conn)
        populate_fact_table(conn)
        show_results(conn)

        print("\nModelo dimensional creado correctamente.")

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    main()
