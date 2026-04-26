from app.pages.styles import BASE_STYLE


def render_bom_page():
    return f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="utf-8" />
    <title>BOM</title>
    {BASE_STYLE}
    <style>
        .bom-summary {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            margin-bottom: 16px;
        }}

        .stepbar {{
            grid-template-columns: repeat(4, 1fr);
        }}

        .bom-metric {{
            background: #f8fafc;
            border: 1px solid #dbe3ef;
            border-radius: 12px;
            padding: 14px;
        }}

        .bom-metric .label {{
            color: #64748b;
            font-size: 14px;
        }}

        .bom-metric .value {{
            margin-top: 8px;
            font-size: 26px;
            font-weight: 800;
        }}

        .bom-tabs {{
            display: flex;
            gap: 8px;
            margin-bottom: 12px;
            flex-wrap: wrap;
        }}

        .bom-tab {{
            border: 1px solid #cbd5e1;
            background: #fff;
            color: #0f172a;
            padding: 10px 14px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 700;
        }}

        .bom-tab.active {{
            background: #1d4ed8;
            border-color: #1d4ed8;
            color: #fff;
        }}

        .bom-table-wrap {{
            width: 100%;
            overflow: auto;
            border-top: 1px solid #dbe3ef;
        }}

        .bom-table {{
            min-width: 2200px;
            border-collapse: collapse;
            width: 100%;
        }}

        .bom-table th,
        .bom-table td {{
            border: 1px solid #dbe3ef;
            padding: 10px 12px;
            vertical-align: top;
            background: #fff;
            font-size: 14px;
        }}

        .bom-table th {{
            background: #eef5ff;
            font-weight: 800;
            position: sticky;
            top: 0;
            z-index: 1;
        }}

        .num {{
            text-align: right;
            white-space: nowrap;
        }}

        .part {{
            font-weight: 700;
            white-space: nowrap;
        }}
    </style>
</head>
<body>
<div class="container">
    <h1>Xuất BOM</h1>
    <div class="subtitle">Trang 4: Gom các thiết bị đã chọn thành BOM riêng cho từng option.</div>

    <div class="stepbar">
        <div class="step">1. Nhập khảo sát</div>
        <div class="step">2. Kết quả tính toán</div>
        <div class="step">3. Chọn model & báo giá</div>
        <div class="step active">4. Xuất BOM</div>
    </div>

    <div class="actions">
        <button class="btn btn-primary" type="button" onclick="downloadBom()">Download Excel</button>
        <a class="btn btn-secondary" href="/quote">Quay lại chọn model</a>
        <a class="btn btn-secondary" href="/survey">Quay lại khảo sát</a>
    </div>

    <div id="bom_block"></div>
</div>

<script>
let currentBom = null;
let activeOption = "opt1";

function money(v) {{
    return "$" + Number(v || 0).toLocaleString(undefined, {{
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }});
}}

function esc(value) {{
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;");
}}

async function loadBom() {{
    const raw = localStorage.getItem("quoteData");

    if (!raw) {{
        document.getElementById("bom_block").innerHTML = `
            <div class="card">
                <div class="empty-state">Chưa có dữ liệu báo giá để xuất BOM.</div>
            </div>
        `;
        return;
    }}

    const res = await fetch("/api/build-bom", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{ quote_data: JSON.parse(raw) }})
    }});

    if (!res.ok) {{
        const text = await res.text();
        document.getElementById("bom_block").innerHTML = `
            <div class="card">
                <div class="error-box" style="display:block;">Không tạo được BOM: ${{esc(text)}}</div>
            </div>
        `;
        return;
    }}

    currentBom = await res.json();
    renderBom();
}}

function setOption(optionKey) {{
    activeOption = optionKey;
    renderBom();
}}

function renderSummary() {{
    const summary = currentBom.summary || {{}};

    return `
        <div class="bom-summary">
            ${{["opt1", "opt2", "opt3"].map(opt => `
                <div class="bom-metric">
                    <div class="label">${{esc(summary[opt]?.label || opt)}}</div>
                    <div class="value">${{money(summary[opt]?.total || 0)}}</div>
                    <div class="muted">${{summary[opt]?.line_count || 0}} dòng BOM</div>
                </div>
            `).join("")}}
        </div>
    `;
}}

function renderRows(rows) {{
    if (!rows.length) {{
        return `<div class="empty-state">Option này chưa có dòng BOM.</div>`;
    }}

    return `
        <div class="bom-table-wrap">
            <table class="bom-table">
                <thead>
                    <tr>
                        <th>Group</th>
                        <th>Hạng mục</th>
                        <th>Model đã chọn</th>
                        <th>Sheet</th>
                        <th>Line</th>
                        <th>Part Number</th>
                        <th>Description</th>
                        <th>Smart Account</th>
                        <th>Included</th>
                        <th>Qty/unit</th>
                        <th>Quote qty</th>
                        <th>Total qty</th>
                        <th>List Price</th>
                        <th>Extended List</th>
                        <th>Discount %</th>
                        <th>Selling Price</th>
                        <th>Subtotal</th>
                        <th>Service Type</th>
                    </tr>
                </thead>
                <tbody>
                    ${{rows.map(row => `
                        <tr>
                            <td>${{esc(row.group)}}</td>
                            <td>${{esc(row.item_type)}}</td>
                            <td>${{esc(row.selected_model)}}</td>
                            <td>${{esc(row.source_sheet)}}</td>
                            <td>${{esc(row.line_number)}}</td>
                            <td class="part">${{esc(row.part_number)}}</td>
                            <td>${{esc(row.description)}}</td>
                            <td>${{esc(row.smart_account_mandatory)}}</td>
                            <td>${{esc(row.included_item)}}</td>
                            <td class="num">${{Number(row.quantity_per_unit || 0).toLocaleString()}}</td>
                            <td class="num">${{Number(row.quote_quantity || 0).toLocaleString()}}</td>
                            <td class="num">${{Number(row.total_quantity || 0).toLocaleString()}}</td>
                            <td class="num">${{money(row.list_price)}}</td>
                            <td class="num">${{money(row.extended_list_price)}}</td>
                            <td class="num">${{Number(row.discount_percent || 0).toLocaleString()}}</td>
                            <td class="num">${{money(row.selling_price)}}</td>
                            <td class="num"><strong>${{money(row.extended_selling_price)}}</strong></td>
                            <td>${{esc(row.service_type)}}</td>
                        </tr>
                    `).join("")}}
                </tbody>
            </table>
        </div>
    `;
}}

function renderBom() {{
    const options = currentBom.options || {{}};
    const option = options[activeOption] || {{ rows: [], total: 0, label: activeOption }};

    document.getElementById("bom_block").innerHTML = `
        <div class="group-summary-card">
            <h3>Tổng quan BOM</h3>
            ${{renderSummary()}}
        </div>

        <div class="group-summary-card">
            <div class="bom-tabs">
                ${{["opt1", "opt2", "opt3"].map(opt => `
                    <button class="bom-tab ${{activeOption === opt ? "active" : ""}}" type="button" onclick="setOption('${{opt}}')">
                        ${{esc(options[opt]?.label || opt)}}
                    </button>
                `).join("")}}
            </div>
            <h3>${{esc(option.label)}} - ${{money(option.total || 0)}}</h3>
            ${{renderRows(option.rows || [])}}
        </div>
    `;
}}

async function downloadBom() {{
    const raw = localStorage.getItem("quoteData");

    if (!raw) return;

    const res = await fetch("/api/download-bom", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{ quote_data: JSON.parse(raw) }})
    }});

    if (!res.ok) {{
        alert("Không download được BOM.");
        return;
    }}

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "network_bom.xlsx";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
}}

loadBom();
</script>
</body>
</html>
    """
