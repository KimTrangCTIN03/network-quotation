from app.pages.styles import BASE_STYLE, render_nav


def esc_html(value) -> str:
    return (
        str(value or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render_login_page(error: str = "", next_url: str = "/dashboard", message: str = "") -> str:
    error_html = f'<div class="error-box" style="display:block;">{esc_html(error)}</div>' if error else ""
    message_html = f'<div class="success-box" style="display:block;">{esc_html(message)}</div>' if message else ""

    return f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="utf-8" />
    <title>Đăng nhập</title>
    {BASE_STYLE}
    <style>
        .login-shell {{
            min-height: 100vh;
            display: grid;
            place-items: center;
            padding: 24px;
        }}

        .login-card {{
            width: min(420px, 100%);
            background: #fff;
            border: 1px solid #dbe3ef;
            border-radius: 16px;
            box-shadow: 0 18px 44px rgba(15, 23, 42, 0.12);
            padding: 28px;
        }}

        .login-card h1 {{
            font-size: 30px;
            margin-bottom: 8px;
        }}

        .login-card .subtitle {{
            margin-bottom: 22px;
        }}

        .login-actions {{
            margin-top: 18px;
            display: flex;
        }}

        .login-actions .btn {{
            width: 100%;
        }}
    </style>
</head>
<body>
<div class="login-shell">
    <form class="login-card" method="post" action="/login">
        <h1>Đăng nhập</h1>
        <div class="subtitle">Network Quotation</div>
        <input type="hidden" name="next_url" value="{esc_html(next_url)}" />
        <label>Tài khoản</label>
        <input type="text" name="username" autocomplete="username" required />
        <div style="height:12px;"></div>
        <label>Mật khẩu</label>
        <input type="password" name="password" autocomplete="current-password" required />
        {message_html}
        {error_html}
        <div class="login-actions">
            <button class="btn btn-primary" type="submit">Đăng nhập</button>
        </div>
        <div style="margin-top:14px; text-align:center;">
            <a href="/register">Chưa có tài khoản? Đăng ký</a>
        </div>
    </form>
</div>
</body>
</html>
"""


def render_register_page(error: str = "", message: str = "") -> str:
    error_html = f'<div class="error-box" style="display:block;">{esc_html(error)}</div>' if error else ""
    message_html = f'<div class="success-box" style="display:block;">{esc_html(message)}</div>' if message else ""

    return f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="utf-8" />
    <title>Đăng ký</title>
    {BASE_STYLE}
    <style>
        .auth-shell {{
            min-height: 100vh;
            display: grid;
            place-items: center;
            padding: 24px;
        }}

        .auth-card {{
            width: min(520px, 100%);
            background: #fff;
            border: 1px solid #dbe3ef;
            border-radius: 16px;
            box-shadow: 0 18px 44px rgba(15, 23, 42, 0.12);
            padding: 28px;
        }}

        .auth-card h1 {{
            font-size: 30px;
            margin-bottom: 8px;
        }}

        .form-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }}

        .form-grid .full {{
            grid-column: 1 / -1;
        }}

        @media (max-width: 640px) {{
            .form-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
<div class="auth-shell">
    <form class="auth-card" method="post" action="/register">
        <h1>Đăng ký tài khoản</h1>
        {message_html}
        {error_html}
        <div class="form-grid">
            <div>
                <label>Tài khoản</label>
                <input type="text" name="username" autocomplete="username" required />
            </div>
            <div>
                <label>Mật khẩu</label>
                <input type="password" name="password" autocomplete="new-password" required />
            </div>
            <div class="full">
                <label>Họ và tên</label>
                <input type="text" name="full_name" />
            </div>
            <div>
                <label>Email</label>
                <input type="email" name="email" />
            </div>
            <div>
                <label>Số điện thoại</label>
                <input type="text" name="phone" />
            </div>
            <div class="full">
                <label>Phòng ban</label>
                <input type="text" name="department" />
            </div>
        </div>
        <div class="actions">
            <button class="btn btn-primary" type="submit">Tạo tài khoản</button>
            <a class="btn btn-secondary" href="/login">Quay lại đăng nhập</a>
        </div>
    </form>
</div>
</body>
</html>
"""


def render_account_page(current_user, message: str = "", error: str = "") -> str:
    message_html = f'<div class="success-box" style="display:block;">{esc_html(message)}</div>' if message else ""
    error_html = f'<div class="error-box" style="display:block;">{esc_html(error)}</div>' if error else ""

    return f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="utf-8" />
    <title>Tài khoản</title>
    {BASE_STYLE}
    <style>
        .account-grid {{
            display: grid;
            grid-template-columns: minmax(0, 1fr) 320px;
            gap: 18px;
            align-items: start;
        }}

        .profile-form {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }}

        .profile-form .full {{
            grid-column: 1 / -1;
        }}

        .profile-meta {{
            display: grid;
            gap: 10px;
        }}

        .profile-meta div {{
            border: 1px solid #dbe4f0;
            border-radius: 10px;
            padding: 12px;
            background: #f8fafc;
        }}

        @media (max-width: 820px) {{
            .account-grid,
            .profile-form {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
{render_nav("account", current_user)}
<div class="container">
    <h1>Thông tin tài khoản </h1>
    {message_html}
    {error_html}
    <div class="account-grid">
        <div class="card">
            <h2>Hồ sơ người dùng</h2>
            <form class="profile-form" method="post" action="/account">
                <div>
                    <label> Tài khoản</label>
                    <input type="text" value="{esc_html(current_user.get("username"))}" disabled />
                </div>
                <div>
                    <label>Quyền</label>
                    <input type="text" value="{esc_html(current_user.get("role"))}" disabled />
                </div>
                <div class="full">
                    <label>Họ và tên</label>
                    <input type="text" name="full_name" value="{esc_html(current_user.get("full_name"))}" />
                </div>
                <div>
                    <label>Email</label>
                    <input type="email" name="email" value="{esc_html(current_user.get("email"))}" />
                </div>
                <div>
                    <label>Số điện thoại</label>
                    <input type="text" name="phone" value="{esc_html(current_user.get("phone"))}" />
                </div>
                <div class="full">
                    <label>Phòng ban</label>
                    <input type="text" name="department" value="{esc_html(current_user.get("department"))}" />
                </div>
                <div class="full">
                    <label>Mật khẩu mới</label>
                    <input type="password" name="password" autocomplete="new-password" placeholder="Bỏ trống nếu không đổi" />
                </div>
                <div class="actions full">
                    <button class="btn btn-primary" type="submit">Lưu thông tin</button>
                </div>
            </form>
        </div>
    </div>
</div>
</body>
</html>
"""


def render_admin_page(users, current_user, overview=None, activity_logs=None, quote_records=None, message: str = "", error: str = "") -> str:
    overview = overview or {}
    activity_logs = activity_logs or []
    quote_records = quote_records or []

    message_html = f'<div class="success-box" style="display:block;">{esc_html(message)}</div>' if message else ""
    error_html = f'<div class="error-box" style="display:block;">{esc_html(error)}</div>' if error else ""

    module_groups = [
        {
            "group": "Tổng quan hệ thống",
            "items": [
                {
                    "title": "Tài khoản người dùng",
                    "desc": "Quản lý tạo/sửa user, khóa/mở tài khoản.",
                    "value": overview.get("user_count", 0),
                    "label": "users",
                },
                {
                    "title": "Admin",
                    "desc": "Số tài khoản có quyền quản trị hệ thống.",
                    "value": overview.get("admin_count", 0),
                    "label": "admins",
                },
                {
                    "title": "Nhật ký hoạt động",
                    "desc": "Theo dõi các thao tác gần đây trong hệ thống.",
                    "value": len(activity_logs),
                    "label": "logs",
                },
            ],
        },
        {
            "group": "Quản lý báo giá",
            "items": [
                {
                    "title": "Toàn bộ báo giá",
                    "desc": "Theo dõi báo giá của tất cả người dùng.",
                    "value": overview.get("quote_count", 0),
                    "label": "quotes",
                },
                {
                    "title": "Báo giá đã khóa",
                    "desc": "Các báo giá đã duyệt hoặc không cho chỉnh sửa.",
                    "value": overview.get("locked_quote_count", 0),
                    "label": "locked",
                },
                {
                    "title": "Trạng thái báo giá",
                    "desc": "Duyệt, khóa hoặc mở khóa báo giá.",
                    "value": overview.get("status_count", 0),
                    "label": "status",
                },
            ],
        },
        {
            "group": "Dữ liệu báo giá",
            "items": [
                {
                    "title": "Dữ liệu BOM",
                    "desc": "Quản lý dữ liệu thiết bị, license và phụ kiện.",
                    "value": overview.get("bom_count", 0),
                    "label": "lines",
                },
                {
                    "title": "Bảng giá",
                    "desc": "Quản lý List Price, AM Price và bảng giá gốc.",
                    "value": overview.get("am_price_count", 0),
                    "label": "items",
                },
                {
                    "title": "Rule tính tự động",
                    "desc": "Quản lý mapping rule BOM và công thức tính.",
                    "value": overview.get("rule_count", 0),
                    "label": "rules",
                },
            ],
        },
        {
            "group": "Cấu hình hệ thống",
            "items": [
                {
                    "title": "Vendor",
                    "desc": "Quản lý danh sách hãng thiết bị.",
                    "value": overview.get("vendor_count", 0),
                    "label": "vendors",
                },
                {
                    "title": "Phân quyền",
                    "desc": "Gán quyền Admin hoặc User cho tài khoản.",
                    "value": overview.get("role_count", 2),
                    "label": "roles",
                },
                {
                    "title": "Cấu hình chung",
                    "desc": "Quản lý các thiết lập chung của hệ thống.",
                    "value": overview.get("config_count", 0),
                    "label": "configs",
                },
            ],
        },
    ]

    module_cards = "".join(
        f"""
        <section class="admin-overview-section">
            <div class="admin-section-title">
                <h3>{esc_html(group["group"])}</h3>
            </div>

            <div class="admin-module-grid">
                {"".join(
                    f'''
                    <div class="admin-module">
                        <div class="admin-module-top">
                            <div>
                                <h4>{esc_html(item["title"])}</h4>
                                <p>{esc_html(item["desc"])}</p>
                            </div>
                            <div class="admin-stat">
                                <span class="admin-stat-value">{esc_html(item["value"])}</span>
                                <span class="admin-stat-label">{esc_html(item["label"])}</span>
                            </div>
                        </div>
                    </div>
                    '''
                    for item in group["items"]
                )}
            </div>
        </section>
        """
        for group in module_groups
    )

    log_rows = "".join(
        f"""
        <tr>
            <td>{esc_html(log.get("created_at"))}</td>
            <td>{esc_html(log.get("username"))}</td>
            <td>{esc_html(log.get("action"))}</td>
            <td>{esc_html(log.get("entity_type"))}</td>
            <td>{esc_html(log.get("detail"))}</td>
        </tr>
        """
        for log in activity_logs[:40]
    ) or '<tr><td colspan="5" class="muted">Chưa có nhật ký hoạt động.</td></tr>'

    quote_rows = "".join(
        f"""
        <tr>
            <td>{esc_html(quote.get("id"))}</td>
            <td>{esc_html(quote.get("title"))}</td>
            <td>{esc_html(quote.get("owner_username"))}</td>
            <td>{esc_html(quote.get("status"))}</td>
            <td>{esc_html(quote.get("updated_at"))}</td>
            <td>
                <form class="quote-status-form" method="post" action="/admin/quotes/{quote.get("id")}/status">
                    <select name="status">
                        <option value="draft" {"selected" if quote.get("status") == "draft" else ""}>draft</option>
                        <option value="submitted" {"selected" if quote.get("status") == "submitted" else ""}>submitted</option>
                        <option value="approved" {"selected" if quote.get("status") == "approved" else ""}>approved</option>
                        <option value="locked" {"selected" if quote.get("status") == "locked" else ""}>locked</option>
                    </select>
                    <button class="btn btn-secondary" type="submit">Lưu</button>
                </form>
            </td>
        </tr>
        """
        for quote in quote_records[:40]
    ) or '<tr><td colspan="6" class="muted">Chưa có báo giá lưu trên server.</td></tr>'

    rows = "".join(
        f"""
        <tr>
            <td class="cell-id">{user["id"]}</td>

            <td>
                <strong>{esc_html(user["username"])}</strong>
            </td>

            <td>
                <input class="table-input" form="user-form-{user["id"]}" type="text" name="full_name"
                       value="{esc_html(user.get("full_name"))}" placeholder="Họ tên" />
            </td>

            <td>
                <input class="table-input" form="user-form-{user["id"]}" type="email" name="email"
                       value="{esc_html(user.get("email"))}" placeholder="Email" />
            </td>

            <td>
                <input class="table-input" form="user-form-{user["id"]}" type="text" name="department"
                       value="{esc_html(user.get("department"))}" placeholder="Phòng ban" />
            </td>

            <td>
                <input class="table-input" form="user-form-{user["id"]}" type="text" name="phone"
                       value="{esc_html(user.get("phone"))}" placeholder="Điện thoại" />
            </td>

            <td>
                <select class="table-select" form="user-form-{user["id"]}" name="role">
                    <option value="user" {"selected" if user["role"] == "user" else ""}>user</option>
                    <option value="admin" {"selected" if user["role"] == "admin" else ""}>admin</option>
                </select>
            </td>

            <td class="cell-active">
                <label class="active-toggle">
                    <input form="user-form-{user["id"]}" type="checkbox" name="is_active" {"checked" if user["is_active"] else ""} />
                    <span>Active</span>
                </label>
            </td>

            <td>
                <input class="table-input" form="user-form-{user["id"]}" type="password" name="password"
                       placeholder="Mật khẩu mới nếu đổi" />
            </td>

            <td class="cell-action">
                <form id="user-form-{user["id"]}" method="post" action="/admin/users/{user["id"]}/update"></form>
                <button form="user-form-{user["id"]}" class="btn btn-secondary table-save-btn" type="submit">Lưu</button>
            </td>
        </tr>
        """
        for user in users
    )

    return f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="utf-8" />
    <title>Admin</title>
    {BASE_STYLE}
    <style>
        .admin-page {{
            max-width: 100%;
            overflow-x: hidden;
        }}

        .admin-grid {{
            display: grid;
            grid-template-columns: 320px minmax(0, 1fr);
            gap: 18px;
            align-items: start;
        }}

        .admin-grid > .card,
        .card {{
            min-width: 0;
        }}

        .admin-overview-card {{
            padding: 22px;
        }}

        .admin-overview-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 18px;
            margin-bottom: 18px;
        }}

        .admin-overview-header h2 {{
            margin: 0;
            font-size: 24px;
            color: #0f172a;
        }}

        .admin-overview-header p {{
            margin: 6px 0 0;
            color: #64748b;
            font-size: 14px;
            line-height: 1.5;
        }}

        .admin-overview-badge {{
            padding: 8px 12px;
            border-radius: 999px;
            background: #eff6ff;
            color: #1d4ed8;
            font-size: 13px;
            font-weight: 800;
            white-space: nowrap;
        }}

        .admin-overview-section {{
            margin-top: 20px;
        }}

        .admin-section-title {{
            margin-bottom: 10px;
            border-left: 4px solid #2563eb;
            padding-left: 10px;
        }}

        .admin-section-title h3 {{
            margin: 0;
            font-size: 16px;
            color: #0f172a;
        }}

        .admin-module-grid {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 14px;
        }}

        .admin-module {{
            border: 1px solid #dbe4f0;
            border-radius: 14px;
            padding: 16px;
            background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
            min-width: 0;
            transition: 0.18s ease;
        }}

        .admin-module:hover {{
            transform: translateY(-2px);
            box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
            border-color: #bfdbfe;
        }}

        .admin-module-top {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 14px;
        }}

        .admin-module h4 {{
            margin: 0 0 6px;
            font-size: 16px;
            line-height: 1.3;
            color: #0f172a;
        }}

        .admin-module p {{
            margin: 0;
            color: #64748b;
            line-height: 1.45;
            font-size: 13px;
        }}

        .admin-stat {{
            min-width: 68px;
            padding: 8px 10px;
            border-radius: 14px;
            background: #dbeafe;
            color: #1d4ed8;
            text-align: center;
            flex-shrink: 0;
        }}

        .admin-stat-value {{
            display: block;
            font-size: 20px;
            line-height: 1;
            font-weight: 900;
        }}

        .admin-stat-label {{
            display: block;
            margin-top: 4px;
            font-size: 10px;
            line-height: 1;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}

        .table-wrap {{
            width: 100%;
            overflow-x: auto;
            border: 1px solid #dbe4f0;
            border-radius: 14px;
        }}

        .table-wrap table {{
            width: 100%;
            min-width: 1180px;
            table-layout: fixed;
            border-collapse: collapse;
        }}

        .table-wrap th,
        .table-wrap td {{
            vertical-align: middle;
            word-break: break-word;
            white-space: normal;
            border: 1px solid #dbe4f0;
        }}

        .table-wrap th {{
            font-size: 13px;
            font-weight: 800;
            background: #eef4fb;
            color: #0f172a;
            padding: 10px 8px;
            text-align: left;
        }}

        .table-wrap td {{
            padding: 8px;
            background: #ffffff;
        }}

        .cell-id {{
            text-align: center;
            font-weight: 700;
            color: #1d4ed8;
        }}

        .table-input,
        .table-select {{
            width: 100%;
            height: 38px;
            border: 1px solid #cbd5e1;
            border-radius: 10px;
            padding: 8px 10px;
            font-size: 14px;
            background: #ffffff;
            box-sizing: border-box;
        }}

        .table-input:focus,
        .table-select:focus {{
            outline: none;
            border-color: #2563eb;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.14);
        }}

        .cell-active {{
            text-align: center;
        }}

        .active-toggle {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            margin: 0;
            font-size: 13px;
            font-weight: 600;
        }}

        .active-toggle input {{
            width: 16px;
            height: 16px;
        }}

        .cell-action {{
            text-align: center;
        }}

        .table-save-btn {{
            width: 100%;
            height: 38px;
            border-radius: 10px;
            font-weight: 800;
        }}

        .table-wrap th:nth-child(1),
        .table-wrap td:nth-child(1) {{
            width: 55px;
        }}

        .table-wrap th:nth-child(2),
        .table-wrap td:nth-child(2) {{
            width: 130px;
        }}

        .table-wrap th:nth-child(3),
        .table-wrap td:nth-child(3) {{
            width: 160px;
        }}

        .table-wrap th:nth-child(4),
        .table-wrap td:nth-child(4) {{
            width: 210px;
        }}

        .table-wrap th:nth-child(5),
        .table-wrap td:nth-child(5) {{
            width: 150px;
        }}

        .table-wrap th:nth-child(6),
        .table-wrap td:nth-child(6) {{
            width: 140px;
        }}

        .table-wrap th:nth-child(7),
        .table-wrap td:nth-child(7) {{
            width: 110px;
        }}

        .table-wrap th:nth-child(8),
        .table-wrap td:nth-child(8) {{
            width: 110px;
        }}

        .table-wrap th:nth-child(9),
        .table-wrap td:nth-child(9) {{
            width: 190px;
        }}

        .table-wrap th:nth-child(10),
        .table-wrap td:nth-child(10) {{
            width: 90px;
        }}

        .quote-status-form {{
            display: grid;
            grid-template-columns: minmax(120px, 1fr) auto;
            gap: 8px;
            align-items: center;
        }}

        .quote-status-form select,
        .quote-status-form button {{
            width: 100%;
        }}

        @media (max-width: 1180px) {{
            .admin-grid {{
                grid-template-columns: 1fr;
            }}

            .admin-module-grid {{
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }}

            .table-wrap table {{
                min-width: 1080px;
            }}
        }}

        @media (max-width: 720px) {{
            .admin-overview-header {{
                flex-direction: column;
            }}

            .admin-module-grid {{
                grid-template-columns: 1fr;
            }}

            .quote-status-form {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
{render_nav("admin", current_user)}
<div class="container admin-page">
    <h1>Quản trị hệ thống</h1>

    {message_html}
    {error_html}

    <div class="card admin-overview-card">
        <div class="admin-overview-header">
            <div>
                <h2>Trung tâm quản trị</h2>
            
            </div>
        </div>

        {module_cards}
    </div>

    <div class="admin-grid">
        <div class="card">
            <h2>Tạo tài khoản</h2>
            <form method="post" action="/admin/users">
                <label>Tài khoản</label>
                <input type="text" name="username" required />

                <div style="height:10px;"></div>

                <label>Họ tên</label>
                <input type="text" name="full_name" />

                <div style="height:10px;"></div>

                <label>Email</label>
                <input type="email" name="email" />

                <div style="height:10px;"></div>

                <label>Phòng ban</label>
                <input type="text" name="department" />

                <div style="height:10px;"></div>

                <label>Số điện thoại</label>
                <input type="text" name="phone" />

                <div style="height:10px;"></div>

                <label>Mật khẩu</label>
                <input type="password" name="password" required />

                <div style="height:10px;"></div>

                <label>Quyền</label>
                <select name="role">
                    <option value="user">user</option>
                    <option value="admin">admin</option>
                </select>

                <label class="checkbox-row">
                    <input type="checkbox" name="is_active" checked />
                    Kích hoạt
                </label>

                <div class="actions">
                    <button class="btn btn-primary" type="submit">Tạo tài khoản</button>
                </div>
            </form>
        </div>

        <div class="card">
            <h2>Danh sách tài khoản</h2>
            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Tài khoản</th>
                            <th>Họ tên</th>
                            <th>Email</th>
                            <th>Phòng ban</th>
                            <th>Điện thoại</th>
                            <th>Quyền</th>
                            <th>Trạng thái</th>
                            <th>Mật khẩu mới</th>
                            <th>Lưu</th>
                        </tr>
                    </thead>
                    <tbody>{rows}</tbody>
                </table>
            </div>
        </div>
    </div>

    <div class="card">
        <h2>Quản lý toàn bộ báo giá</h2>
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Tiêu đề</th>
                        <th>Chủ sở hữu</th>
                        <th>Trạng thái</th>
                        <th>Cập nhật</th>
                        <th>Duyệt / Khóa</th>
                    </tr>
                </thead>
                <tbody>{quote_rows}</tbody>
            </table>
        </div>
    </div>

    <div class="card">
        <h2>Nhật ký hoạt động</h2>
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>Thời gian</th>
                        <th>User</th>
                        <th>Hành động</th>
                        <th>Đối tượng</th>
                        <th>Chi tiết</th>
                    </tr>
                </thead>
                <tbody>{log_rows}</tbody>
            </table>
        </div>
    </div>
</div>
</body>
</html>
"""
