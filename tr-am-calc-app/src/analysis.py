from dataclasses import replace
import pandas as pd
import plotly.express as px
from src.model import TrofeoAmicizia

def profit_sensitivity(instance, param: str, values) -> pd.DataFrame:
    """
    Clona `instance` variando `field` (nome dell'attributo da cambiare) secondo `values`,
    un Iterable con i valori da usare
    e restituisce un DataFrame (comodo per i plot) con x=valore, profit=utile.
    """
    records = [
        {"x": v,
         "profit": replace(instance, **{param: v}).profit}        #Replace won
        for v in values
    ]
    return pd.DataFrame(records)

def tornado(evento: TrofeoAmicizia, deltas=(0.1, -0.1)):
    """
    Crea un tornado chart di sensitività dell'utile per ciascun parametro numerico.
    """
    params = {
        "participation_price": "Ticket price",
        "participants": "Participants",
        "photos_per_atlete": "Photos each athlete",
        "profit_per_photo": "Profit each photo",
        "gadget_price": "Gadget cost",
        "categories": "Categories",
        "podiums_for_speciality_each_category": "Podiums for speciality each category",
        "workers_salary_for_round": "Workers salary for round",
    }
    records = []
    base_profit = evento.profit
    for field, label in params.items():
        for d in deltas:
            current = getattr(evento, field)
            changed = current * (1 + d)
            clone = replace(evento, **{field: changed})
            delta_profit = clone.profit - base_profit
            records.append(
                {"Parameter": label, "Scenario": f"{d:+.0%}", "ΔProfit": delta_profit}
            )
    df = pd.DataFrame(records)
    fig = px.bar(
        df,
        y="Parameter",
        x="ΔProfit",
        color="Scenario",
        orientation="h",
        title="Profit sensitivity (Tornado)",
    )
    return fig