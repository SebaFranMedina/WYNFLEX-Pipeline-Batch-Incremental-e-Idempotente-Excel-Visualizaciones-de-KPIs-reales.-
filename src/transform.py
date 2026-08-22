from pathlib import Path
import pandas as pd


RAW_DIR = Path("data/raw")
SILVER_DIR = Path("data/silver")


SUMMARY_ROWS = [
    "Resumen de Envíos",
    "Total de envíos",
    "Monto bruto",
    "Descuento (%)",
    "Neto final a cobrar"
]


def transform_file(file_path):
    print(f"\nTransformando: {file_path.name}")

    df = pd.read_excel(file_path)

    # Eliminar filas completamente vacías
    df = df.dropna(how="all")

    # Eliminar filas sin número de tracking
    df = df.dropna(subset=["numero_tracking"])

    # Eliminar filas de resumen del Excel
    df = df[~df["numero_tracking"].isin(SUMMARY_ROWS)]

    # Convertir fechas
    df["fecha_colecta"] = pd.to_datetime(
        df["fecha_colecta"],
        format="%d/%m/%Y %H:%M",
        errors="coerce"
    )

    df["fecha_estado"] = pd.to_datetime(
        df["fecha_estado"],
        format="%d/%m/%Y %H:%M",
        errors="coerce"
    )

    # Normalizar texto
    text_columns = [
        "nombre_fantasia",
        "direccion",
        "estado",
        "cadete",
        "zona"
    ]

    for column in text_columns:
        if column in df.columns:
            df[column] = (
                df[column]
                .astype("string")
                .str.strip()
            )

    # Normalizar código postal
    if "cp" in df.columns:
        df["cp"] = df["cp"].astype("Int64")

    # Eliminar duplicados de tracking dentro de cada archivo
    df = df.drop_duplicates(
        subset=["numero_tracking"],
        keep="first"
    )

    print(f"  Filas finales: {len(df):,}")

    return df


def main():
    files = sorted(RAW_DIR.glob("*.xlsx"))

    if not files:
        print(f"No se encontraron archivos en: {RAW_DIR}")
        return

    SILVER_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Archivos encontrados: {len(files)}")

    for file_path in files:
        df = transform_file(file_path)

        output_name = file_path.stem + ".parquet"
        output_path = SILVER_DIR / output_name

        df.to_parquet(
            output_path,
            index=False
        )

        print(f"  Guardado: {output_path}")


if __name__ == "__main__":
    main()
