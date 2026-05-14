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
        overflow: visible;
        padding-bottom: 2px;
    }
    .app-nav-item {
        position: relative;
    }
    .app-nav-item::after {
        content: "";
        position: absolute;
        left: 0;
        right: 0;
        top: 100%;
        height: 10px;
        display: none;
    }
    .app-nav-item:hover::after,
    .app-nav-item:focus-within::after {
        display: block;
    }
    .app-dropdown,
    .app-flyout {
        position: absolute;
        min-width: 170px;
        display: none;
        flex-direction: column;
        gap: 4px;
        padding: 8px;
        background: #fff;
        border: 1px solid #dbe3ef;
        border-radius: 8px;
        box-shadow: 0 14px 34px rgba(15, 23, 42, 0.14);
        z-index: 30;
    }
    .app-dropdown {
        top: 100%;
        left: 0;
        padding-top: 10px;
    }
    .app-flyout {
        top: -8px;
        left: 100%;
        margin-left: 0;
        padding-left: 14px;
    }
    .app-nav-item:hover > .app-dropdown,
    .app-nav-item:focus-within > .app-dropdown,
    .app-menu-item:hover > .app-flyout,
    .app-menu-item:focus-within > .app-flyout {
        display: flex;
    }
    .app-menu-item {
        position: relative;
    }
    .app-menu-item.has-flyout::after {
        content: "";
        position: absolute;
        top: -8px;
        bottom: -8px;
        left: 100%;
        width: 14px;
        display: none;
    }
    .app-menu-item.has-flyout:hover::after,
    .app-menu-item.has-flyout:focus-within::after {
        display: block;
    }
    .app-menu-link {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        color: #475569;
        text-decoration: none;
        font-size: 13px;
        font-weight: 700;
        padding: 8px 10px;
        border-radius: 8px;
        white-space: nowrap;
    }
    .app-menu-item.has-flyout > .app-menu-link::after {
        content: ">";
        color: #94a3b8;
        font-size: 12px;
    }
    .app-menu-link:hover,
    .app-menu-link.active {
        background: #dbeafe;
        color: #1d4ed8;
    }
    .app-sub-nav {
        max-width: 1400px;
        margin: -4px auto 0;
        padding: 0 24px 8px;
        display: flex;
        justify-content: flex-end;
        gap: 6px;
        overflow-x: auto;
    }
    .app-sub-nav.solution-area-nav {
        justify-content: flex-start;
        border-top: 1px solid #e2e8f0;
        padding-top: 8px;
    }
    .app-sub-nav.solution-step-nav {
        justify-content: flex-start;
        padding-bottom: 12px;
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
    .app-icon-link {
        width: 38px;
        height: 38px;
        padding: 0;
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }
    .app-icon {
        width: 20px;
        height: 20px;
        stroke: currentColor;
        stroke-width: 2;
        stroke-linecap: round;
        stroke-linejoin: round;
        fill: none;
    }
    .app-profile-menu .app-dropdown {
        left: auto;
        right: 0;
        min-width: 190px;
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
            overflow-x: auto;
        }
        .app-dropdown,
        .app-flyout {
            position: static;
            box-shadow: none;
            margin-top: 4px;
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


def render_nav(active: str = "", user: dict | None = None, solution_area: str = "campus") -> str:
    solution_active = active in {"survey", "calculation", "topology", "quote", "bom"}
    area = "dc-sdn" if str(solution_area or "").lower() == "dc-sdn" else "campus"
    items = [
        ("dashboard", "/dashboard", "Dashboard"),
        ("model_quote", "/model-quote", "Ch&#7885;n model"),
        ("pricing", "/pricing", "Catalog gi&#225;"),
    ]
    links = "".join(
        f'<a class="app-nav-link{" active" if key == active or (key == "solution" and solution_active) else ""}" href="{href}">{label}</a>'
        for key, href, label in items
    )
    def step_links(base: str, step_area: str) -> str:
        solution_items = [
            ("survey", f"{base}/survey", "Kh&#7843;o s&#225;t"),
            ("calculation", f"{base}/calculation-results", "K&#7871;t qu&#7843;"),
            ("topology", f"{base}/topology", "Topo"),
            ("quote", f"{base}/quote", "Model"),
            ("bom", f"{base}/bom", "BOM"),
        ]
        return "".join(
            f'<a class="app-menu-link{" active" if key == active and step_area == area else ""}" href="{href}">{label}</a>'
            for key, href, label in solution_items
        )

    solution_menu = f"""
            <div class="app-nav-item">
                <a class="app-nav-link{" active" if solution_active else ""}" href="/{area}/survey">Gi&#7843;i ph&#225;p</a>
                <div class="app-dropdown">
                    <div class="app-menu-item has-flyout">
                        <a class="app-menu-link{" active" if area == "campus" else ""}" href="/campus/survey">Campus</a>
                        <div class="app-flyout">{step_links("/campus", "campus")}</div>
                    </div>
                    <div class="app-menu-item has-flyout">
                        <a class="app-menu-link{" active" if area == "dc-sdn" else ""}" href="/dc-sdn/survey">DC-SDN</a>
                        <div class="app-flyout">{step_links("/dc-sdn", "dc-sdn")}</div>
                    </div>
                </div>
            </div>
    """
    first_link_end = links.find("</a>") + 4
    links = links[:first_link_end] + solution_menu + links[first_link_end:]
    admin_icon = '<svg class="app-icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.7 1.7 0 0 0 .34 1.87l.04.04a2 2 0 1 1-2.83 2.83l-.04-.04a1.7 1.7 0 0 0-1.87-.34 1.7 1.7 0 0 0-1.04 1.56V21a2 2 0 0 1-4 0v-.06a1.7 1.7 0 0 0-1.04-1.56 1.7 1.7 0 0 0-1.87.34l-.04.04a2 2 0 1 1-2.83-2.83l.04-.04A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-1.56-1.04H3a2 2 0 0 1 0-4h.06A1.7 1.7 0 0 0 4.6 8a1.7 1.7 0 0 0-.34-1.87l-.04-.04a2 2 0 1 1 2.83-2.83l.04.04A1.7 1.7 0 0 0 8.96 3.6 1.7 1.7 0 0 0 10 2.04V2a2 2 0 0 1 4 0v.06a1.7 1.7 0 0 0 1.04 1.56 1.7 1.7 0 0 0 1.87-.34l.04-.04a2 2 0 1 1 2.83 2.83l-.04.04A1.7 1.7 0 0 0 19.4 8c.14.37.43.66.8.8.22.09.46.13.72.13H21a2 2 0 0 1 0 4h-.06A1.7 1.7 0 0 0 19.4 15Z"></path></svg>'
    profile_icon = '<svg class="app-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 21a8 8 0 0 0-16 0"></path><circle cx="12" cy="7" r="4"></circle></svg>'
    if user and user.get("role") == "admin":
        links += f'<a class="app-nav-link app-icon-link{" active" if active == "admin" else ""}" href="/admin" title="Qu&#7843;n tr&#7883; h&#7879; th&#7889;ng" aria-label="Qu&#7843;n tr&#7883; h&#7879; th&#7889;ng">{admin_icon}</a>'
    if user:
        user_label = esc_nav_label(user.get("full_name") or user.get("username") or "Tai khoan")
        links += f"""
            <div class="app-nav-item app-profile-menu">
                <a class="app-nav-link app-icon-link{" active" if active == "account" else ""}" href="/account" title="{user_label}" aria-label="{user_label}">{profile_icon}</a>
                <div class="app-dropdown">
                    <a class="app-menu-link" href="/account">Th&#244;ng tin t&#224;i kho&#7843;n</a>
                    <a class="app-menu-link" href="/logout">&#272;&#259;ng xu&#7845;t</a>
                </div>
            </div>
        """
    return f"""
<nav class="app-nav">
    <div class="app-nav-inner">
        <a class="app-brand" href="/dashboard">Network Quotation</a>
        <div class="app-nav-links">{links}</div>
    </div>
</nav>
"""
