from app.pages.styles import BASE_STYLE


def render_dashboard_page():
    return f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="utf-8" />
    <title>Dashboard - Network Quotation</title>
    {BASE_STYLE}
    <style>
        body {{
            background: #eef3f8;
        }}

        .dashboard-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 24px;
            margin-bottom: 20px;
        }}

        .dashboard-title {{
            max-width: 820px;
        }}

        .dashboard-title h1 {{
            font-size: 34px;
            margin-bottom: 8px;
        }}

        .status-pill {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            border-radius: 999px;
            background: #e0f2fe;
            color: #075985;
            font-weight: 700;
            font-size: 13px;
            white-space: nowrap;
        }}

        .module-grid {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 18px;
            margin-top: 18px;
        }}

        .module-card {{
            background: #fff;
            border: 1px solid #dbe3ef;
            border-radius: 14px;
            padding: 22px;
            box-shadow: 0 8px 22px rgba(15, 23, 42, 0.06);
        }}

        .module-kicker {{
            color: #2563eb;
            font-weight: 800;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 10px;
        }}

        .module-card h2 {{
            margin: 0 0 8px;
            font-size: 24px;
        }}

        .module-card p {{
            margin: 0;
            color: #475569;
            line-height: 1.55;
        }}

        .module-actions {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 20px;
        }}

        .workflow {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
        }}

        .workflow-step {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 14px;
        }}

        .workflow-step strong {{
            display: block;
            margin-bottom: 6px;
        }}

        .workflow-step span {{
            color: #64748b;
            font-size: 13px;
            line-height: 1.45;
        }}

        @media (max-width: 900px) {{
            .dashboard-header,
            .module-grid,
            .workflow {{
                grid-template-columns: 1fr;
                display: grid;
            }}
        }}
    </style>
</head>
<body>
<div class="container">
    <div class="dashboard-header">
        <div class="dashboard-title">
            <h1>Network Quotation Tool</h1>
            <div class="subtitle"></div>
        </div>
        <div class="status-pill"></div>
    </div>

    <div class="module-grid">
        <div class="module-card">
            <div class="module-kicker"></div>
            <h2>Tính toán giải pháp</h2>
            <p>Nhập thông tin khảo sát campus, server farm và WAN để hệ thống tính demand, số lượng thiết bị, requirement kỹ thuật, sau đó đề xuất option Low / Mid / High.</p>
            <div class="module-actions">
                <a class="btn btn-primary" href="/survey">Bắt đầu</a>
            </div>
        </div>

        <div class="module-card">
            <div class="module-kicker"></div>
            <h2>Báo giá & cập nhật giá</h2>
            <p>AM upload file BOM để hệ thống lấy giá theo logic catalog hiện có. Nếu BOM có cột giá AM, hệ thống có thể lưu thành giá override cho các lần báo giá sau.</p>
            <div class="module-actions">
                <a class="btn btn-primary" href="/pricing">Mở báo giá BOM</a>
            </div>
        </div>
    </div>

    
</div>
</body>
</html>
    """
