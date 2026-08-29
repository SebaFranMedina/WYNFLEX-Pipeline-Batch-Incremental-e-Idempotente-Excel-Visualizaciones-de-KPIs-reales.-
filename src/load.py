from pathlib import Path
import os

import pandas as pd
from sqlalchemy import create_engine, text


SILVER_DIR = Path("data/silver")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "wynflex")
DB_USER = os.getenv("DB_USER", "wynflex")
DB_PASSWORD = os.getenv("DB_PASSWORD", "wynflex")

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

TABLE_NAME = "deliveries"


def create_table(engine):
    """Crea la tabla si todavía no existe."""

    query = text(
        f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            delivery_id SERIAL PRIMARY KEY,
            numero_tracking VARCHAR(100),
            fecha_colecta TIMESTAMP,
            nombre_fantasia VARCHAR(255),
            fecha_estado TIMESTAMP,
            direccion VARCHAR(500),
            cp INTEGER,
            estado VARCHAR(100),
            cadete VARCHAR(255),
            total NUMERIC,
            zona VARCHAR(100),
            precio_chofer NUMERIC,
            porcentaje_chofer NUMERIC,
            source_file VARCHAR(255)
        );
        """
    )

    with engine.begin() as connection:
        connection.execute(query)


def get_loaded_files(engine):
    """Obtiene los archivos que ya fueron cargados en PostgreSQL."""

    query = text(
        f"""
        SELECT DISTINCT source_file
        FROM {TABLE_NAME}
        WHERE source_file IS NOT NULL;
        """
    )

    with engine.connect() as connection:
        return {
            row[0]
            for row in connection.execute(query)
        }


def load_file(file_path, engine):
    """Carga un Parquet nuevo en PostgreSQL."""

    print(f"\nCargando: {file_path.name}")

    df = pd.read_parquet(file_path)

    # Guardamos el archivo de origen para trazabilidad
    df["source_file"] = file_path.name

    with engine.begin() as connection:
        df.to_sql(
            TABLE_NAME,
            connection,
            if_exists="append",
            index=False,
        )

    print(f"  Filas cargadas: {len(df):,}")


def main():
    files = sorted(SILVER_DIR.glob("*.parquet"))

    if not files:
        print(
            f"No se encontraron archivos Parquet en: "
            f"{SILVER_DIR}"
        )
        return

    print(
        f"Conectando a PostgreSQL en: "
        f"{DB_HOST}:{DB_PORT}"
    )

    engine = create_engine(DATABASE_URL)

    create_table(engine)

    loaded_files = get_loaded_files(engine)

    print(f"\nArchivos ya cargados: {len(loaded_files)}")
    print(f"Archivos encontrados en Silver: {len(files)}")

    new_files = []

    for file_path in files:
        if file_path.name in loaded_files:
            print(f"⏭️  Ya cargado: {file_path.name}")
        else:
            new_files.append(file_path)

    print(f"\nArchivos nuevos para cargar: {len(new_files)}")

    for file_path in new_files:
        load_file(file_path, engine)

    print("\nCarga incremental finalizada.")


if __name__ == "__main__":
    main()