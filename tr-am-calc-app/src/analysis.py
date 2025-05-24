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
         "profit": replace(instance, **{param: v}).profit}
        for v in values
    ]
    return pd.DataFrame(records)

def tornado_for_trofeo_amicizia(evento: TrofeoAmicizia, deltas=(0.1, -0.1)):
    """
    Crea un tornado chart di sensitività dell'utile per ciascun parametro numerico.
    """
    params = {
        "participation_price": "Prezzo iscrizione",
        "participants": "Partecipanti",
        "photos_per_atlete": "Foto per atleta",
        "profit_per_photo": "Profitto per foto",
        "gadget_price": "Costo dei gadget",
        "categories": "Categorie",
        "podiums_for_speciality_each_category": "Podii di specialità a cat.",
        "coaches_salary_for_round": "Salario allenatori a turno",
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
        # title="Profit sensitivity (Tornado)",
        color_discrete_map={"+10%": "green", "-10%": "red"},
        template="plotly_white",
    )
    fig.update_layout(
        yaxis_title=None,
    )
    return fig