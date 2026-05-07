from pathlib import Path
from urllib.parse import urlencode

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from app.auth import (
    SESSION_COOKIE,
    admin_overview,
    authenticate_user,
    create_session,
    create_quote_record,
    create_user,
    delete_session,
    ensure_default_admin,
    get_current_user,
    list_activity_logs,
    list_quote_records,
    list_users,
    log_activity,
    update_quote_status,
    update_profile,
    update_user,
)
from app.bom_engine import build_bom, build_bom_excel
from app.catalog_engine import compare_price_map_with_cisco_tab, debug_catalog_summary
from app.pages import (
    render_account_page,
    render_admin_page,
    render_bom_page,
    render_calculation_results_page,
    render_dashboard_page,
    render_login_page,
    render_pricing_page,
    render_quote_page,
    render_register_page,
    render_survey_page,
    render_topology_page,
)
from app.pricing.catalog import list_price_entries, save_am_price
from app.pricing.storage import check_database
from app.pricing_engine import import_prices_from_bom, quote_bom
from app.quote_engine import build_quote
from app.recommendation_engine import recommend_all
from app.requirement_engine import build_requirements
from app.schemas import AmPricePayload, BomPayload, QuoteRecordPayload, SurveyPayload, payload_to_dict


app = FastAPI(title="Network Quotation Web")
ICON_DIR = Path(__file__).resolve().parent.parent / "icon-library" / "project-topology-icons"
app.mount("/icons", StaticFiles(directory=ICON_DIR), name="icons")


def login_redirect(request: Request) -> RedirectResponse:
    next_url = request.url.path
    if request.url.query:
        next_url = f"{next_url}?{request.url.query}"
    return RedirectResponse(f"/login?{urlencode({'next_url': next_url})}", status_code=303)


def safe_next_url(next_url: str) -> str:
    next_url = (next_url or "/dashboard").strip()
    if not next_url.startswith("/") or next_url.startswith("//"):
        return "/dashboard"
    if next_url.startswith("/login") or next_url.startswith("/register"):
        return "/dashboard"
    return next_url


def page_user(request: Request):
    user = get_current_user(request)
    if not user:
        return None
    return user


def require_api_user(request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Login required")
    return user


def require_admin_user(request: Request):
    user = require_api_user(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin permission required")
    return user


@app.on_event("startup")
def startup_auth():
    ensure_default_admin()


@app.get("/")
def root():
    return RedirectResponse("/dashboard")


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request, next_url: str = "/dashboard"):
    if get_current_user(request):
        return RedirectResponse(safe_next_url(next_url), status_code=303)
    return render_login_page(next_url=safe_next_url(next_url))


@app.post("/login")
def login_action(
    username: str = Form(...),
    password: str = Form(...),
    next_url: str = Form("/dashboard"),
):
    user = authenticate_user(username, password)
    if not user:
        return HTMLResponse(render_login_page("Sai tài khoản hoặc mật khẩu.", next_url), status_code=401)

    response = RedirectResponse(safe_next_url(next_url), status_code=303)
    response.set_cookie(
        SESSION_COOKIE,
        create_session(user["id"]),
        httponly=True,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
    )
    log_activity(user, "login", "auth", user["id"], "Dang nhap he thong")
    return response


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    if get_current_user(request):
        return RedirectResponse("/dashboard", status_code=303)
    return render_register_page()


@app.post("/register")
def register_action(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(""),
    email: str = Form(""),
    department: str = Form(""),
    phone: str = Form(""),
):
    if get_current_user(request):
        return RedirectResponse("/dashboard", status_code=303)

    try:
        create_user(username, password, "user", True, full_name, email, department, phone)
        user = authenticate_user(username, password)
        if not user:
            return HTMLResponse(render_register_page(message="Da tao tai khoan. Hay dang nhap."), status_code=201)

        response = RedirectResponse("/dashboard", status_code=303)
        response.set_cookie(
            SESSION_COOKIE,
            create_session(user["id"]),
            httponly=True,
            samesite="lax",
            max_age=7 * 24 * 60 * 60,
        )
        log_activity(user, "register", "user", user["id"], "Nguoi dung tu dang ky")
        return response
    except Exception as exc:
        return HTMLResponse(render_register_page(error=f"{type(exc).__name__}: {exc}"), status_code=400)


@app.get("/logout")
def logout(request: Request):
    user = get_current_user(request)
    delete_session(request.cookies.get(SESSION_COOKIE, ""))
    log_activity(user, "logout", "auth", user.get("id") if user else "", "Dang xuat he thong")
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie(SESSION_COOKIE)
    return response


@app.get("/account", response_class=HTMLResponse)
def account_page(request: Request, message: str = "", error: str = ""):
    user = page_user(request)
    if not user:
        return login_redirect(request)
    return render_account_page(user, message, error)


@app.post("/account")
def account_update(
    request: Request,
    full_name: str = Form(""),
    email: str = Form(""),
    department: str = Form(""),
    phone: str = Form(""),
    password: str = Form(""),
):
    user = page_user(request)
    if not user:
        return login_redirect(request)

    try:
        update_profile(user["id"], full_name, email, department, phone, password)
        log_activity(user, "update_profile", "user", user["id"], "Cap nhat thong tin ca nhan")
        return RedirectResponse("/account?message=Da cap nhat thong tin", status_code=303)
    except Exception as exc:
        return RedirectResponse(f"/account?{urlencode({'error': f'{type(exc).__name__}: {exc}'})}", status_code=303)


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request):
    user = page_user(request)
    if not user:
        return login_redirect(request)
    return render_dashboard_page(user)


@app.get("/survey", response_class=HTMLResponse)
def survey_page(request: Request):
    user = page_user(request)
    if not user:
        return login_redirect(request)
    return render_survey_page(user)


@app.get("/calculation-results", response_class=HTMLResponse)
def calculation_results_page(request: Request):
    user = page_user(request)
    if not user:
        return login_redirect(request)
    return render_calculation_results_page(user)


@app.get("/quote", response_class=HTMLResponse)
def quote_page(request: Request):
    user = page_user(request)
    if not user:
        return login_redirect(request)
    return render_quote_page(user)


@app.get("/topology", response_class=HTMLResponse)
def topology_page(request: Request):
    user = page_user(request)
    if not user:
        return login_redirect(request)
    return render_topology_page(user)


@app.get("/bom", response_class=HTMLResponse)
def bom_page(request: Request):
    user = page_user(request)
    if not user:
        return login_redirect(request)
    return render_bom_page(user)


@app.get("/pricing", response_class=HTMLResponse)
def pricing_page(request: Request):
    user = page_user(request)
    if not user:
        return login_redirect(request)
    return render_pricing_page(user)


@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request, message: str = "", error: str = ""):
    user = page_user(request)
    if not user:
        return login_redirect(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin permission required")
    return render_admin_page(list_users(), user, admin_overview(), list_activity_logs(), list_quote_records(user), message, error)


@app.post("/admin/users")
def admin_create_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(""),
    email: str = Form(""),
    department: str = Form(""),
    phone: str = Form(""),
    role: str = Form("user"),
    is_active: str | None = Form(None),
):
    admin = require_admin_user(request)
    try:
        create_user(username, password, role, is_active is not None, full_name, email, department, phone)
        log_activity(admin, "admin_create_user", "user", username, f"role={role}")
        return RedirectResponse("/admin?message=Đã tạo tài khoản", status_code=303)
    except Exception as exc:
        return RedirectResponse(f"/admin?error={type(exc).__name__}: {exc}", status_code=303)


@app.post("/admin/users/{user_id}/update")
def admin_update_user(
    request: Request,
    user_id: int,
    full_name: str = Form(""),
    email: str = Form(""),
    department: str = Form(""),
    phone: str = Form(""),
    role: str = Form("user"),
    is_active: str | None = Form(None),
    password: str = Form(""),
):
    admin = require_admin_user(request)
    try:
        update_user(user_id, role, is_active is not None, password, full_name, email, department, phone)
        log_activity(admin, "admin_update_user", "user", user_id, f"role={role}; active={is_active is not None}")
        return RedirectResponse("/admin?message=Đã cập nhật tài khoản", status_code=303)
    except Exception as exc:
        return RedirectResponse(f"/admin?error={type(exc).__name__}: {exc}", status_code=303)


@app.post("/api/requirements")
def api_requirements(payload: SurveyPayload, _user=Depends(require_api_user)):
    return build_requirements(payload_to_dict(payload))


@app.post("/api/generate-quote")
def api_generate_quote(payload: SurveyPayload, _user=Depends(require_api_user)):
    data = payload_to_dict(payload)
    req = build_requirements(data)
    recs = recommend_all(req["proposal_lines"])
    quote = build_quote(recs)
    log_activity(_user, "generate_quote", "quote", "", "Chay tinh toan bao gia")

    return {
        "requirements": req,
        "quote": quote,
    }


@app.post("/api/build-bom")
def api_build_bom(payload: BomPayload, _user=Depends(require_api_user)):
    log_activity(_user, "build_bom", "bom", payload.option_key or "", str(payload.group_filter or ""))
    return build_bom(payload.quote_data, payload.group_filter)


@app.post("/api/download-bom")
def api_download_bom(payload: BomPayload, _user=Depends(require_api_user)):
    output = build_bom_excel(payload.quote_data, payload.option_key, payload.group_filter)
    suffix = f"_{payload.option_key}" if payload.option_key else ""
    scope = "_dc_sdn" if str(payload.group_filter or "").strip().lower() == "dc-sdn" else ""
    headers = {
        "Content-Disposition": f'attachment; filename="network_bom{scope}{suffix}.xlsx"'
    }
    log_activity(_user, "download_bom", "bom", payload.option_key or "all", str(payload.group_filter or ""))

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


@app.get("/api/quotes")
def api_list_quotes(_user=Depends(require_api_user)):
    return {"rows": list_quote_records(_user)}


@app.post("/api/quotes")
def api_create_quote(payload: QuoteRecordPayload, _user=Depends(require_api_user)):
    quote = create_quote_record(_user, payload.title, payload.quote_data, payload.status)
    log_activity(_user, "save_quote", "quote", quote["id"], quote["title"])
    return quote


@app.post("/admin/quotes/{quote_id}/status")
def admin_update_quote_status(
    request: Request,
    quote_id: int,
    status: str = Form(...),
):
    admin = require_admin_user(request)
    quote = update_quote_status(admin, quote_id, status)
    log_activity(admin, "update_quote_status", "quote", quote_id, quote["status"])
    return RedirectResponse("/admin?message=Da cap nhat trang thai bao gia", status_code=303)


@app.post("/api/price-bom")
async def api_price_bom(file: UploadFile = File(...), _user=Depends(require_admin_user)):
    content = await file.read()
    return quote_bom(content, file.filename or "")


@app.post("/api/import-am-prices")
async def api_import_am_prices(
    file: UploadFile = File(...),
    vendor: str = Form("Cisco"),
    confirm_overwrite: bool = Form(False),
    _user=Depends(require_admin_user),
):
    content = await file.read()
    result = import_prices_from_bom(content, file.filename or "", vendor, confirm_overwrite)
    log_activity(_user, "import_price_file", "price", vendor, file.filename or "")
    return result


@app.get("/api/prices")
def api_prices(q: str = "", limit: int = 500, vendor: str = "", _user=Depends(require_api_user)):
    return list_price_entries(q, limit, vendor)


@app.post("/api/prices/am")
def api_save_am_price(payload: AmPricePayload, _user=Depends(require_api_user)):
    list_price = payload.list_price if _user.get("role") == "admin" else None
    result = save_am_price(payload.model, payload.price, payload.vendor, list_price)
    log_activity(_user, "save_am_price", "price", payload.model, f"vendor={payload.vendor}")
    return result


@app.get("/api/debug-catalog")
def api_debug_catalog(_user=Depends(require_admin_user)):
    return debug_catalog_summary()


@app.get("/api/debug-price-compare")
def api_debug_price_compare(_user=Depends(require_admin_user)):
    return compare_price_map_with_cisco_tab()


@app.get("/api/db-health")
def api_db_health(_user=Depends(require_admin_user)):
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
