BASE_STYLE = """
<style>
    :root {
        --app-font-family: Arial, Helvetica, sans-serif;
    }
    * { box-sizing: border-box; }
    body {
        font-family: var(--app-font-family);
        margin: 0;
        background: #f4f7fb;
        color: #0f172a;
    }
    input,
    select,
    textarea,
    button,
    table,
    pre {
        font-family: var(--app-font-family);
    }
    .app-nav {
        position: sticky;
        top: 0;
        z-index: 10;
        background: rgba(244, 247, 251, 0.94);
        border-bottom: 1px solid #dbe3ef;
        backdrop-filter: blur(12px);
    }
    .app-nav-inner {
        max-width: 1400px;
        margin: 0 auto;
        padding: 10px 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 18px;
    }
    .app-brand {
        color: #0f172a;
        font-size: 15px;
        font-weight: 800;
        text-decoration: none;
        white-space: nowrap;
    }
    .app-nav-links {
        display: flex;
        gap: 8px;
        align-items: center;
        overflow-x: auto;
        padding-bottom: 2px;
    }
    .app-sub-nav {
        max-width: 1400px;
        margin: -4px auto 0;
        padding: 0 24px 10px;
        display: flex;
        justify-content: flex-end;
        gap: 6px;
        overflow-x: auto;
    }
    .app-sub-nav-link {
        color: #475569;
        text-decoration: none;
        font-size: 12px;
        font-weight: 700;
        padding: 6px 9px;
        border-radius: 8px;
        white-space: nowrap;
    }
    .app-sub-nav-link:hover {
        background: #e0edff;
        color: #1d4ed8;
    }
    .app-sub-nav-link.active {
        background: #dbeafe;
        color: #1d4ed8;
    }
    .app-nav-link {
        color: #475569;
        text-decoration: none;
        font-size: 13px;
        font-weight: 700;
        padding: 8px 10px;
        border-radius: 8px;
        white-space: nowrap;
    }
    .app-nav-link:hover {
        background: #e0edff;
        color: #1d4ed8;
    }
    .app-nav-link.active {
        background: #2563eb;
        color: #fff;
    }
    .container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 24px;
    }
    h1 {
        margin: 0 0 8px 0;
        font-size: 36px;
    }
    .subtitle {
        color: #475569;
        font-size: 17px;
        margin-bottom: 20px;
    }
    .stepbar {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin-bottom: 22px;
    }
    .step {
        background: white;
        border: 1px solid #dbe3ef;
        border-radius: 14px;
        padding: 14px;
        color: #64748b;
        font-weight: bold;
        display: block;
        text-decoration: none;
        cursor: pointer;
        transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;
    }
    .step:hover {
        background: #eff6ff;
        border-color: #bfdbfe;
        color: #1d4ed8;
    }
    .step.active {
        background: #2563eb;
        color: white;
        border-color: #2563eb;
    }
    .step.active:hover {
        background: #2563eb;
        color: white;
        border-color: #2563eb;
    }
    .card {
        background: #fff;
        border-radius: 16px;
        border: 1px solid #dbe3ef;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
        padding: 20px;
        margin-bottom: 18px;
    }
    .section-title {
        font-size: 17px;
        font-weight: bold;
        margin: 20px 0 12px;
        color: #0f172a;
        padding-bottom: 8px;
        border-bottom: 1px solid #e2e8f0;
    }
    label {
        display: block;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 6px;
        color: #334155;
    }
    input[type="text"],
    input[type="number"] {
        width: 100%;
        padding: 10px 12px;
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        font-size: 14px;
        background: #fff;
    }
    input[type="checkbox"] {
        transform: scale(1.1);
        margin-right: 8px;
    }
    .checkbox-row {
        display: flex;
        align-items: center;
        margin-top: 8px;
        margin-bottom: 8px;
        font-size: 14px;
    }
    .grid-2 {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
    }
    .grid-3 {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
    }
    .sub-card {
        border: 1px solid #dbe3ef;
        border-radius: 14px;
        padding: 14px;
        background: #fafcff;
        margin-bottom: 12px;
    }
    .sub-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }
    .sub-card-title {
        font-weight: bold;
        font-size: 14px;
    }
    .btn {
        border: none;
        padding: 11px 16px;
        border-radius: 10px;
        cursor: pointer;
        font-weight: bold;
        font-size: 14px;
        text-decoration: none;
        display: inline-block;
    }
    .btn-primary {
        background: #2563eb;
        color: white;
    }
    .btn-secondary {
        background: #e2e8f0;
        color: #0f172a;
    }
    .btn-danger {
        background: #ef4444;
        color: white;
        padding: 8px 12px;
        font-size: 12px;
    }
    .actions {
        display: flex;
        gap: 10px;
        margin-top: 18px;
        flex-wrap: wrap;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        background: white;
    }
    th, td {
        border: 1px solid #dbe3ef;
        padding: 8px;
        text-align: left;
        vertical-align: top;
    }
    th {
        background: #eff6ff;
        font-weight: bold;
    }
    select {
        width: 100%;
        padding: 8px;
        border-radius: 8px;
        border: 1px solid #cbd5e1;
        font-size: 13px;
        background: #fff;
    }
    .small {
        color: #64748b;
        font-size: 12px;
        margin-top: 4px;
    }
    .error-box {
        display: none;
        margin-top: 12px;
        padding: 12px;
        background: #fef2f2;
        border: 1px solid #fecaca;
        color: #991b1b;
        border-radius: 10px;
        white-space: pre-wrap;
    }
    .success-box {
        display: none;
        margin-top: 12px;
        padding: 12px;
        background: #ecfdf5;
        border: 1px solid #a7f3d0;
        color: #065f46;
        border-radius: 10px;
    }
    .empty-state {
        padding: 30px;
        text-align: center;
        color: #64748b;
        border: 1px dashed #cbd5e1;
        border-radius: 14px;
        background: #f8fafc;
    }
    .summary-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
    }
    .metric {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 14px;
    }
    .metric-label {
        color: #64748b;
        font-size: 13px;
    }
    .metric-value {
        font-size: 22px;
        font-weight: bold;
        margin-top: 6px;
    }
    pre {
        margin: 0;
        white-space: pre-wrap;
        font-size: 12px;
    }
    @media (max-width: 720px) {
        .app-nav-inner {
            align-items: flex-start;
            flex-direction: column;
            gap: 8px;
        }
        .app-nav-links {
            width: 100%;
        }
        .app-sub-nav {
            justify-content: flex-start;
            padding: 0 24px 10px;
        }
    }
</style>
"""


def esc_nav_label(value) -> str:
    return (
        str(value or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render_nav(active: str = "", user: dict | None = None) -> str:
    solution_active = active in {"survey", "calculation", "topology", "quote", "bom"}
    items = [
        ("dashboard", "/dashboard", "Dashboard"),
        ("solution", "/survey", "Gi&#7843;i ph&#225;p"),
        ("model_quote", "/model-quote", "Ch&#7885;n model"),
        ("pricing", "/pricing", "Catalog gi&#225;"),
    ]
    if user and user.get("role") == "admin":
        items.append(("admin", "/admin", "Admin"))
    if user:
        items.append(("account", "/account", esc_nav_label(user.get("full_name") or user.get("username") or "Tài khoản")))
        items.append(("logout", "/logout", "Đăng xuất"))
    links = "".join(
        f'<a class="app-nav-link{" active" if key == active or (key == "solution" and solution_active) else ""}" href="{href}">{label}</a>'
        for key, href, label in items
    )
    solution_items = [
        ("survey", "/survey", "Kh&#7843;o s&#225;t"),
        ("calculation", "/calculation-results", "K&#7871;t qu&#7843; Campus / DC-SDN"),
        ("topology", "/topology", "Topo Campus"),
        ("quote", "/quote", "Model Campus / DC-SDN"),
        ("bom", "/bom", "BOM Campus / DC-SDN"),
    ]
    solution_links = "".join(
        f'<a class="app-sub-nav-link{" active" if key == active else ""}" href="{href}">{label}</a>'
        for key, href, label in solution_items
    )
    sub_nav = f'<div class="app-sub-nav">{solution_links}</div>' if solution_active else ""
    return f"""
<nav class="app-nav">
    <div class="app-nav-inner">
        <a class="app-brand" href="/dashboard">Network Quotation</a>
        <div class="app-nav-links">{links}</div>
    </div>
    {sub_nav}
</nav>
"""
