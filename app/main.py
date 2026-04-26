from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse

from app.bom_engine import build_bom, build_bom_excel
from app.catalog_engine import compare_price_map_with_cisco_tab, debug_catalog_summary
from app.pages import (
    render_bom_page,
    render_calculation_results_page,
    render_dashboard_page,
    render_pricing_page,
    render_quote_page,
    render_survey_page,
)
from app.pricing.catalog import list_price_entries, save_am_price
from app.pricing.storage import check_database
from app.pricing_engine import import_prices_from_bom, quote_bom
from app.quote_engine import build_quote
from app.recommendation_engine import recommend_all
from app.requirement_engine import build_requirements
from app.schemas import AmPricePayload, BomPayload, SurveyPayload, payload_to_dict


app = FastAPI(title="Network Quotation Web")


@app.get("/")
def root():
    return RedirectResponse("/dashboard")


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page():
    return render_dashboard_page()


@app.get("/survey", response_class=HTMLResponse)
def survey_page():
    return render_survey_page()


@app.get("/calculation-results", response_class=HTMLResponse)
def calculation_results_page():
    return render_calculation_results_page()


@app.get("/quote", response_class=HTMLResponse)
def quote_page():
    return render_quote_page()


@app.get("/bom", response_class=HTMLResponse)
def bom_page():
    return render_bom_page()


@app.get("/pricing", response_class=HTMLResponse)
def pricing_page():
    return render_pricing_page()


@app.post("/api/requirements")
def api_requirements(payload: SurveyPayload):
    req = build_requirements(payload_to_dict(payload))
    return req


@app.post("/api/generate-quote")
def api_generate_quote(payload: SurveyPayload):
    print("generate quote called")

    data = payload_to_dict(payload)

    req = build_requirements(data)
    print("requirements:", len(req["requirements"]))
    print("proposal lines:", len(req["proposal_lines"]))

    recs = recommend_all(req["proposal_lines"])
    print("recommendations:", len(recs))

    quote = build_quote(recs)
    print("quote lines:", len(quote["quote_lines"]))

    return {
        "requirements": req,
        "quote": quote,
    }


@app.post("/api/build-bom")
def api_build_bom(payload: BomPayload):
    return build_bom(payload.quote_data)


@app.post("/api/download-bom")
def api_download_bom(payload: BomPayload):
    output = build_bom_excel(payload.quote_data)
    headers = {
        "Content-Disposition": 'attachment; filename="network_bom.xlsx"'
    }

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


@app.post("/api/price-bom")
async def api_price_bom(file: UploadFile = File(...)):
    content = await file.read()
    return quote_bom(content, file.filename or "")


@app.post("/api/import-am-prices")
async def api_import_am_prices(
    file: UploadFile = File(...),
    vendor: str = Form("Cisco"),
    confirm_overwrite: bool = Form(False),
):
    content = await file.read()
    return import_prices_from_bom(content, file.filename or "", vendor, confirm_overwrite)


@app.get("/api/prices")
def api_prices(q: str = "", limit: int = 500, vendor: str = ""):
    return list_price_entries(q, limit, vendor)


@app.post("/api/prices/am")
def api_save_am_price(payload: AmPricePayload):
    return save_am_price(payload.model, payload.price, payload.vendor, payload.list_price)


@app.get("/api/debug-catalog")
def api_debug_catalog():
    return debug_catalog_summary()


@app.get("/api/debug-price-compare")
def api_debug_price_compare():
    return compare_price_map_with_cisco_tab()


@app.get("/api/db-health")
def api_db_health():
    try:
        return check_database()
    except Exception as exc:
        return {
            "status": "error",
            "error_type": type(exc).__name__,
            "message": str(exc),
        }


@app.get("/health")
def health():
    return {"status": "ok"}
