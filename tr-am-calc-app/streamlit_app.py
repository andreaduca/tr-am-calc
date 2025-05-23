from src.analysis import tornado_for_trofeo_amicizia
from src.model import TrofeoAmicizia
import json
from src.render_template import build_trofeo_amicizia_report
import streamlit as st

st.set_page_config(page_title="Trofeo Amicizia – simulatore", page_icon="🏆")
st.title("Simulatore economico – Trofeo Amicizia")

# --- 1. INPUT -------------------------------------------------------------
st.header("Parametri generali")
participants = st.number_input("Partecipanti", min_value=1, value=205, step=1)
participation_price = st.number_input("Prezzo iscrizione (€)", min_value=5.0, value=10.0, step=1.0)

st.header("Premiazioni & gadget")
participation_medal_price = st.number_input("Costo di una medaglia di partecipazione (€)", 0.0, value=1.4, step=0.05)
gadget_price = st.number_input("Costo gadget (€)", 0.0, value=1.2, step=0.05)

categories = st.number_input("Categorie, da premiare con le coppe (Gym Magic J, Gym Magic A, Gym Star J, ...)", 1, value=11, step=1)
podiums_speciality_each_category = st.number_input("Podii per le specialità per ogni categoria (CL, VT, ...)", 0, value=5, step=1)
avg_podium_medal_price = st.number_input("Prezzo medio di una medaglia per il podio (€)", 0.0, value=1.85, step=0.05)
avg_cup_price = st.number_input("Prezzo medio di una coppa (€)", 0.0, value=8.5, step=0.1)

st.header("Personale")
available_coaches = st.number_input("Allenatori disponibili", 0, value=13, step=1)
coaches_salary_for_round = st.number_input("Compenso di un allenatore per un turno (€)", 0.0, value=8.0, step=1.0)
judges = st.number_input("Giudici esterni ", 0, value=1, step=1)
judges_salary_for_round = st.number_input("Compenso di un giudice esterno per un turno (€)", 0.0, value=10.0, step=1.0)

# Inserisci i dizionari come JSON semplice
workers_json = st.text_area("Lavoratori per turno (JSON)", '{"turno1": 12, "turno2": 12, "turno3": 11, "turno4": 12, "turno5": 12, "turno6": 0}')
judges_json = st.text_area("Giudici esterni per turno, non inclusi fra i lavoratori considerati prima (JSON)", '{"turno1": 0, "turno2": 0, "turno3": 0, "turno4": 1, "turno5": 0, "turno6": 0}')

st.header("Altri costi / ricavi")
food_cost = st.number_input("Costi per il cibo (€)", 0.0, value=25.0, step=1.0)
photos_per_athlete = st.number_input("Stima della percentuale di foto vendute per ogni iscritto", 0.0, value=0.55, step=0.01)
profit_per_photo = st.number_input("Guadagno per foto (€)", 0.0, value=1.5, step=0.1)

# --- 2. ELABORAZIONE ------------------------------------------------------
# Parsing dei dizionari (con fallback vuoto se JSON non valido)
def parse_dict(txt):
    try:
        d = json.loads(txt)
        if not isinstance(d, dict):
            raise ValueError
        return d
    except (json.JSONDecodeError, ValueError):
        st.warning("⚠️  Formato JSON non valido, uso dizionario vuoto")
        return {}

workers_for_round = parse_dict(workers_json)
judges_for_round = parse_dict(judges_json)

# Crea l'istanza della dataclass
evento = TrofeoAmicizia(
    participants=participants,
    participation_price=participation_price,
    participation_medal_price=participation_medal_price,
    gadget_price=gadget_price,
    categories=categories,
    podiums_for_speciality_each_category=podiums_speciality_each_category,
    average_podium_medal_price=avg_podium_medal_price,
    average_cup_price=avg_cup_price,
    available_coaches=available_coaches,
    coaches_for_round=workers_for_round,
    coaches_salary_for_round=coaches_salary_for_round,
    judges_for_round=judges_for_round,
    judges_salary_for_round=judges_salary_for_round,
    food_cost=food_cost,
    photos_per_atlete=photos_per_athlete,
    profit_per_photo=profit_per_photo,
)

# --- 3. OUTPUT ------------------------------------------------------------
tornado_chart = tornado_for_trofeo_amicizia(evento)

inputs = {
    "Partecipanti": evento.participants,
    "Prezzo iscrizione (€)": evento.participation_price,
    "Costo medaglia partecipazione (€)": evento.participation_medal_price,
    "Costo gadget (€)": evento.gadget_price,
    "Categorie": evento.categories,
    "Podii di specialità": evento.podiums_for_speciality_each_category,
    "Prezzo medaglia podio (€)": evento.average_podium_medal_price,
    "Prezzo coppa (€)": evento.average_cup_price,
    "Allenatori disponibili": evento.available_coaches,
    "Giudici esterni": judges,
    "Costo allenatore / turno (€)": evento.coaches_salary_for_round,
    "Costo giudice / turno (€)": evento.judges_salary_for_round,
    "Costo cibo (€)": evento.food_cost,
    "Foto per atleta": evento.photos_per_atlete,
    "Profitto per foto (€)": evento.profit_per_photo,
}

primary_kpi = {
    "Fatturato": f"{evento.revenue:,.2f} €",
    "Costi totali": f"{evento.total_costs:,.2f} €",
    "Utile": f"{evento.profit:,.2f} €",
    "Profit margin": f"{evento.profit_margin_pct():.2%}",
}

secondary_kpi = {
    "ΔProfit / atleta": f"{evento.dprofit_dparticipants():,.2f} €",
    "Δ²Profit / atleta": f"{evento.d2profit_dparticipants2():,.2f} €",
    "Break-even iscritti": evento.break_even_participants(),
    "ARPP": f"{evento.average_revenue_per_participant():,.2f} €",
    "CPP": f"{evento.cost_per_participant():,.2f} €",
    "Margine di contribuzione / atleta": f"{evento.contribution_margin_per_participant():,.2f} €",
    "Variable / Fixed ratio": f"{evento.variable_to_fixed_ratio():.2f}",
    "Photo revenue ratio": f"{evento.photo_revenue_ratio():.2%}",
}

rounds = sorted(
    set(evento.coaches_for_round.keys()) |
    set(evento.judges_for_round.keys())
)                      # es. ['turno1', 'turno2', …]


with st.sidebar:

    # === bottone per generare il report ===
    if st.button("Scarica report PDF"):
        # TODO: rimuovere l'anteprima
        pdf_bytes, html_preview = build_trofeo_amicizia_report(evento, tornado_chart, inputs=inputs, primary_kpi=primary_kpi, secondary_kpi=secondary_kpi, rounds=rounds)
        st.download_button(
            "Download PDF",
            data=pdf_bytes,
            file_name="report_evento.pdf",
            mime="application/pdf"
        )

        with st.expander("Anteprima HTML"):
            st.components.v1.html(html_preview, height=600, scrolling=True)

    st.header("Risultati")
    st.metric("Fatturato", f"€{evento.revenue:,.2f}")
    st.metric("Costi", f"€{evento.total_costs:,.2f}")
    st.metric("Utile", f"€{evento.profit:,.2f}")

    st.markdown("### Redditività")
    st.metric("Profit margin", f"{evento.profit_margin_pct():.1%}")
    with st.expander("Cosa significa?"):
        st.caption(
            "Percentuale di utile sul fatturato totale. Indica quanto “trattieni” di ogni euro incassato dopo tutti i costi."
            " Perché serve: confronta la redditività di edizioni diverse o con eventi simili, a prescindere dalla scala."
        )
    st.metric("ARPP (Average Revenue Per Participant)", f"€{evento.average_revenue_per_participant():,.2f}")
    with st.expander("Cosa significa?"):
        st.caption(
            "Spesa media di un atleta (biglietto + foto + altri extra). Fatturato per ogni iscritto. "
            "Perché serve: misura la tua capacità di monetizzare ciascun iscritto; sale con up-selling o aumenti di prezzo.")

    st.metric("CPP (Average total cost per athlete)", f"€{evento.cost_per_participant():,.2f}")
    with st.expander("Cosa significa?"):
        st.caption(
            " Costi totali divisi per gli iscritti, costo medio di ogni iscritto."
            " Perché serve: insieme ad ARPP mostra se guadagni (ARPP > CPP) o perdi (ARPP < CPP) su base unitaria.")

    st.metric("ΔProfit / atleta", f"€{evento.dprofit_dparticipants():,.2f}")
    with st.expander("Cosa significa?"):
        st.caption("Variazione dell’utile totale se iscrivi una persona in più."
                   "Perché serve: dice se puntare sul volume è ancora redditizio.")

    st.metric("Δ²Profit / atleta", f"€{evento.d2profit_dparticipants2():,.2f}")
    with st.expander("Cosa significa?"):
        st.caption("Variazione del marginal profit all’aumentare di un atleta (seconda differenza discreta)."
                   " Perché serve: rileva economie di scala (> 0) o rendimenti decrescenti (< 0)."
                   " es: −0,25 € → il guadagno marginale sta calando: ogni nuovo atleta aggiunge meno utile del precedente (stai saturando le risorse)."
                   "Come sfruttare l'economia di scala? Si ha bisogno di ricavi extra o costi unitari calino man mano che superi determinate soglie di partecipanti: "
                   "Sponsorship scalate e paganti per soglie di partecipanti, sconti quantità su medaglie, coppe, widget e servizi ad alto margine con costi quasi fissi.")

    st.markdown("### Pareggio")
    break_even= evento.break_even_participants()
    delta_break_even = evento.participants - break_even if break_even > 0 else None
    break_even_label = f"{break_even:,}" if break_even > 0 else "∞"
    st.metric(
        "Break-even iscritti",
        break_even_label,
        delta=None if break_even < 0 else f"{delta_break_even:+,}"
    )

st.plotly_chart(tornado_chart)

st.subheader("Metriche di dettaglio")

kpi_dettaglio = {
    "Contribution margin / iscritti: contributo per la copertura dei costi fissi per iscritto": f"€{evento.contribution_margin_per_participant():,.2f}",
    "Variable / Fixed ratio: 1+ significa che i costi variabili dominano (rischio più basso se cala la partecipazione). <1 indica una struttura a costi fissi elevata; i profitti allora oscilleranno fortemente al variare del numero di partecipanti.": f"{evento.variable_to_fixed_ratio():.2f}",
    "Photo revenue ratio:  Valori vicini a 1 (100%) indicano che le foto rappresentano la principale fonte di ricavo": f"{evento.photo_revenue_ratio():.2%}",
}
for k, v in kpi_dettaglio.items():
    st.markdown(f"{v} -> {k}")

st.subheader("Costi")
st.write(
    {
        "Costi variabili": evento.variable_costs,
        "Costi fissi": evento.total_workers_cost,
    }
)

st.subheader("Dettaglio costi")
st.write(
    {
        "Spesa per le medaglie di partecipazione": evento._participation_medals_cost,
        "Spesa per dei gadget": evento._gadget_cost,
        "Spesa per tutti i podii": evento.total_podium_cost,
        "Costo di tutti i lavoratori": evento.total_workers_cost,
    }
)

st.subheader("Dettaglio ricavi")
st.write(
    {
        "Iscrizioni": evento._registration_sales,
        "Foto": evento._photo_sales,
    }
)