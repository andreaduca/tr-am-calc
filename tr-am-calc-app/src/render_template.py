import base64, datetime, io, pathlib
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

from src.model import TrofeoAmicizia

TEMPLATE_DIR = pathlib.Path(__file__).parent.parent / "templates"

env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape()
)

def render_chart(chart) -> str:
    try:
        # Plotly: best way is fig.to_image (needs kaleido)
        png_bytes = chart.to_image(format="png", scale=2)
    except AttributeError:
        # Older Plotly or Matplotlib object without to_image
        buf = io.BytesIO()
        try:
            # Plotly figures have write_image (kaleido backend)
            chart.write_image(buf, format="png")  # Plotly with write_image
            png_bytes = buf.getvalue()
        except Exception:
            # Fallback: assume Matplotlib
            chart.savefig(buf, format="png", dpi=150, bbox_inches="tight")
            png_bytes = buf.getvalue()

    return base64.b64encode(png_bytes).decode()

def build_trofeo_amicizia_report(event: TrofeoAmicizia, tornado_fig, *, inputs: dict, primary_kpi: dict, secondary_kpi:dict, rounds) -> tuple[bytes, str]:
    """renders HTML->PDF and returns the PDF in bytes."""
    # convert Plotly (needs kaleido) *or* Matplotlib figure to PNG in‑memory
    # --- convert figure to PNG base64 -----------------------------------
    tornado_b64 = render_chart(tornado_fig)

    logo_path = TEMPLATE_DIR / "vigna-pia-nuovo-logo.png"
    logo_b64 = base64.b64encode(logo_path.read_bytes()).decode()

    tpl = env.get_template("report_trofeo_am.html")
    html_string = tpl.render(
        event_name=event.name,
        rounds=rounds,
        coaches_round = event.coaches_for_round,
        judges_round  = event.judges_for_round,
        today=datetime.date.today().strftime("%d/%m/%Y"),
        tornado_b64=tornado_b64,
        logo_b64=logo_b64,

        inputs=inputs,
        primary_kpi=primary_kpi,
        secondary_kpi=secondary_kpi,
    )

    pdf_bytes = HTML(string=html_string, base_url=".").write_pdf()
    return pdf_bytes, html_string