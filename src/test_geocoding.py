import time
import requests

addresses = [
    "Calle Cachi 1269, Buenos Aires, Argentina",
    "Avenida 27 de Febrero 6201, Buenos Aires, Argentina",
    "Avenida Lafuente 3196, Buenos Aires, Argentina",
    "Pasaje Primavera, Buenos Aires, Argentina",
    "Avenida Amancio Alcorta 3000, Buenos Aires, Argentina",
    "Av. Olivera 630, Buenos Aires, Argentina",
    "Av Olivera 1561, Buenos Aires, Argentina",
    "Acosta Ñu 1950, Buenos Aires, Argentina",
    "Calle Corrales 3277, Buenos Aires, Argentina",
    "Calle Traful 3826, Buenos Aires, Argentina",
]

url = "https://nominatim.openstreetmap.org/search"

headers = {
    "User-Agent": "WYNFLEX-analytics/1.0"
}

for address in addresses:
    params = {
        "q": address,
        "format": "json",
        "addressdetails": 1,
        "limit": 1,
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=10,
    )

    response.raise_for_status()

    results = response.json()

    print(f"\nDirección: {address}")

    if results:
        result = results[0]

        print("Resultado:", result.get("display_name"))
        print("Latitud:", result.get("lat"))
        print("Longitud:", result.get("lon"))
        print("Barrio:", result.get("address", {}).get("neighbourhood"))
        print("Suburbio:", result.get("address", {}).get("suburb"))
    else:
        print("No encontrado")

    time.sleep(1)