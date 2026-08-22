from pathlib import Path
import pandas as pd


DATA_DIR = Path("data/raw")


def extract_files():
    files = sorted(DATA_DIR.glob("*.xlsx"))

    if not files:
        print(f"No se encontraron archivos Excel en: {DATA_DIR}")
        return []

    print(f"Archivos encontrados: {len(files)}")

    dataframes = []

    for file_path in files:
        print(f"\nExtrayendo: {file_path.name}")

        df = pd.read_excel(file_path)

        print(f"  Filas: {len(df):,}")
        print(f"  Columnas: {len(df.columns)}")

        dataframes.append(df)

    return dataframes


def main():
    dataframes = extract_files()

    print(f"\nDataFrames extraídos: {len(dataframes)}")


if __name__ == "__main__":
    main()
