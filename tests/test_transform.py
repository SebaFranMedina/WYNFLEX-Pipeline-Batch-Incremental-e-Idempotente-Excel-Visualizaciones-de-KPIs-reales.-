import pandas as pd

from src.transform import transform_file


def test_transform_removes_summary_rows(tmp_path):
    data = {
        "numero_tracking": [
            "123456",
            "Resumen de Envíos",
            "Total de envíos",
            None,
        ],
        "fecha_colecta": [
            "02/07/2026 08:00",
            None,
            None,
            None,
        ],
        "nombre_fantasia": [
            "Cliente A",
            None,
            None,
            None,
        ],
        "fecha_estado": [
            "02/07/2026 12:00",
            None,
            None,
            None,
        ],
        "direccion": [
            "Calle 123",
            None,
            None,
            None,
        ],
        "cp": [
            1704,
            None,
            None,
            None,
        ],
        "estado": [
            "Entregado",
            None,
            None,
            None,
        ],
        "cadete": [
            "Sebastian",
            None,
            None,
            None,
        ],
        "total": [
            1000,
            None,
            None,
            None,
        ],
        "zona": [
            "Zona 1",
            None,
            None,
            None,
        ],
        "precio_chofer": [
            500,
            None,
            None,
            None,
        ],
        "porcentaje_chofer": [
            50,
            None,
            None,
            None,
        ],
    }

    input_file = tmp_path / "test.xlsx"

    pd.DataFrame(data).to_excel(
        input_file,
        index=False
    )

    result = transform_file(input_file)

    assert len(result) == 1
    assert result.iloc[0]["numero_tracking"] == "123456"
    assert result.iloc[0]["estado"] == "Entregado"
