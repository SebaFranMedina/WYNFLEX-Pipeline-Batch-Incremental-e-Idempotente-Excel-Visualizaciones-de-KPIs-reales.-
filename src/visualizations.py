import plotly.express as px

from analytics import get_deliveries_by_day


def plot_deliveries_by_day():
    df = get_deliveries_by_day()

    fig = px.line(
        df,
        x="fecha",
        y="total_entregas",
        markers=True,
        title="Entregas realizadas por día",
        labels={
            "fecha": "Fecha",
            "total_entregas": "Entregas",
        },
    )

    fig.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Cantidad de entregas",
        hovermode="x unified",
    )

    output_file = "data/deliveries_by_day.html"

    fig.write_html(output_file)

    print(f"Gráfico generado: {output_file}")


if __name__ == "__main__":
    plot_deliveries_by_day()