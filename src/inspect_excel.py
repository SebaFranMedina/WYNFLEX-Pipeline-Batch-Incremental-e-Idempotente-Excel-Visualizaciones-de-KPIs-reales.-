from pathlib import Path
import pandas as pd


DATA_DIR = Path("data/raw")


def inspect_file(file_path):

    print("\n" + "=" * 80)
    print(f"ARCHIVO: {file_path.name}")
    print("=" * 80)

    df = pd.read_excel(file_path)

    # ---------------------------------------------------------
    # FILAS CON TRACKING VÁLIDO
    # ---------------------------------------------------------

    df_valid = df[
        df["numero_tracking"].notna()
    ].copy()

    print(f"\nFilas totales: {len(df)}")
    print(f"Filas con tracking: {len(df_valid)}")

    # ---------------------------------------------------------
    # FECHAS
    # ---------------------------------------------------------

    for column in ["fecha_colecta", "fecha_estado"]:

        if column in df.columns:

            dates = pd.to_datetime(
                df[column],
                format="%d/%m/%Y %H:%M",
                errors="coerce"
            )

            print(f"\n{column}")

            print(
                f"  Desde: {dates.min()}"
            )

            print(
                f"  Hasta: {dates.max()}"
            )

    # ---------------------------------------------------------
    # TRACKINGS
    # ---------------------------------------------------------

    print("\nTRACKINGS")

    total_tracking = len(df_valid)

    unique_tracking = (
        df_valid["numero_tracking"]
        .nunique()
    )

    print(f"  Total: {total_tracking}")
    print(f"  Únicos: {unique_tracking}")

    duplicated_mask = (
        df_valid["numero_tracking"]
        .duplicated(keep=False)
    )

    duplicados = df_valid[
        duplicated_mask
    ].copy()

    print(
        f"  Filas involucradas en duplicados: "
        f"{len(duplicados)}"
    )

    # ---------------------------------------------------------
    # DETALLE DE DUPLICADOS
    # ---------------------------------------------------------

    if not duplicados.empty:

        print(
            "\n!!! TRACKINGS DUPLICADOS !!!"
        )

        columnas = [
            "numero_tracking",
            "fecha_colecta",
            "fecha_estado",
            "estado",
            "direccion",
            "cp",
            "cadete",
        ]

        columnas = [
            c for c in columnas
            if c in duplicados.columns
        ]

        print(
            duplicados[
                columnas
            ].to_string(index=False)
        )

    # ---------------------------------------------------------
    # ESTADOS
    # ---------------------------------------------------------

    print("\nESTADOS")

    print(
        df_valid["estado"]
        .value_counts(
            dropna=False
        )
        .to_string()
    )

    # ---------------------------------------------------------
    # CLIENTES
    # ---------------------------------------------------------

    print("\nCLIENTES")

    print(
        f"  Únicos: "
        f"{df_valid['nombre_fantasia'].nunique()}"
    )

    # ---------------------------------------------------------
    # CODIGOS POSTALES
    # ---------------------------------------------------------

    print("\nCODIGOS POSTALES")

    print(
        f"  Únicos: "
        f"{df_valid['cp'].nunique()}"
    )

    # ---------------------------------------------------------
    # CADETES
    # ---------------------------------------------------------

    print("\nCADETES")

    print(
        df_valid["cadete"]
        .value_counts()
        .to_string()
    )


def main():

    files = sorted(
        DATA_DIR.glob("*.xlsx")
    )

    print(
        f"Archivos encontrados: {len(files)}"
    )

    for file_path in files:

        try:

            inspect_file(file_path)

        except Exception as e:

            print(
                f"\nERROR procesando "
                f"{file_path.name}:"
            )

            print(e)


if __name__ == "__main__":
    main()