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

        .group-row td {{
            background: #1d4ed8;
            color: #fff;
            font-weight: 900;
            font-size: 15px;
        }}

        .subtotal-row td {{
            background: #fff7d6;
            font-weight: 900;
        }}

        .estimate-total-row td {{
            background: #e0f2fe;
            color: #0000ff;
            font-weight: 900;
        }}

        .bom-loading-card {{
            background: #fff;
            border: 1px solid #dbe3ef;
            border-radius: 16px;
            padding: 28px;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
            display: flex;
            align-items: center;
            gap: 14px;
            color: #0f172a;
            font-weight: 700;
        }}

        .bom-spinner {{
            width: 24px;
            height: 24px;
            border: 3px solid #dbeafe;
            border-top-color: #1d4ed8;
            border-radius: 999px;
            animation: bomSpin 0.8s linear infinite;
            flex: 0 0 auto;
        }}

        .bom-loading-text {{
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}

        .bom-loading-text span {{
            color: #64748b;
            font-size: 13px;
            font-weight: 500;
        }}

        @keyframes bomSpin {{
            to {{
                transform: rotate(360deg);
            }}
        }}

        .btn:disabled {{
            opacity: 0.65;
            cursor: not-allowed;
        }}
    </style>
</head>
<body>
<div class="container">
    <h1>Xuất BOM</h1>

    <div class="stepbar">
        <a class="step" href="/survey">1. Nhập khảo sát</a>
        <a class="step" href="/calculation-results">2. Kết quả tính toán</a>
        <a class="step" href="/quote">3. Chọn model & báo giá</a>
        <a class="step active" href="/bom">4. Xuất BOM</a>
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

function showBomLoading(message, subMessage) {{
    document.getElementById("bom_block").innerHTML = `
        <div class="bom-loading-card">
            <div class="bom-spinner"></div>
            <div class="bom-loading-text">
                <div>${{esc(message || "Đang xuất BOM, vui lòng đợi...")}}</div>
                <span>${{esc(subMessage || "Hệ thống đang tổng hợp dữ liệu BOM.")}}</span>
            </div>
        </div>
    `;
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

    showBomLoading("Đang xuất BOM, vui lòng đợi...", "Hệ thống đang tạo bảng BOM từ dữ liệu báo giá.");

    try {{
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
    }} catch (error) {{
        document.getElementById("bom_block").innerHTML = `
            <div class="card">
                <div class="error-box" style="display:block;">Không tạo được BOM. Vui lòng thử lại.</div>
            </div>
        `;
    }}
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
                </div>
            `).join("")}}
        </div>
    `;
}}

function renderRows(rows) {{
    if (!rows.length) {{
        return `<div class="empty-state">Option này chưa có BOM.</div>`;
    }}

    return `
        <div class="bom-table-wrap">
            <table class="bom-table">
                <thead>
                    <tr>
                        <th>Line Number</th>
                        <th>Item Name</th>
                        <th>Smart Account Mandatory</th>
                        <th>Description</th>
                        <th>Group Name</th>
                        <th>Service Duration (Months)</th>
                        <th>Estimated Lead Time (Days)</th>
                        <th>Included Item</th>
                        <th>Quantity</th>
                        <th>Pricing Term</th>
                        <th>ListPrice</th>
                        <th>Extended ListPrice</th>
                        <th>Discount %</th>
                        <th>Selling Price</th>
                        <th>Service Type</th>
                    </tr>
                </thead>
                <tbody>
                    ${{rows.map(row => `
                        ${{row.is_group_header ? `
                            <tr class="group-row">
                                <td colspan="15">${{esc(row.group || row.description)}}</td>
                            </tr>
                        ` : row.is_subtotal ? `
                            <tr class="subtotal-row">
                                <td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
                                <td></td><td></td><td></td>
                                <td class="num">${{money(row.extended_list_price)}}</td>
                                <td>SubTotal</td>
                                <td class="num">${{money(row.extended_selling_price)}}</td>
                                <td></td>
                            </tr>
                        ` : row.is_estimate_total ? `
                            <tr class="estimate-total-row">
                                <td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td>
                                <td></td><td></td><td></td><td></td>
                                <td>Estimate Total</td>
                                <td class="num">${{money(row.extended_selling_price)}}</td>
                                <td></td>
                            </tr>
                        ` : `
                        <tr>
                            <td>${{esc(row.line_number)}}</td>
                            <td class="part">${{esc(row.part_number)}}</td>
                            <td>${{esc(row.smart_account_mandatory)}}</td>
                            <td>${{esc(row.description)}}</td>
                            <td>${{esc(row.group_name)}}</td>
                            <td>${{esc(row.service_duration_months)}}</td>
                            <td>${{esc(row.estimated_lead_time_days)}}</td>
                            <td>${{esc(row.included_item)}}</td>
                            <td class="num">${{Number(row.total_quantity || 0).toLocaleString()}}</td>
                            <td>${{esc(row.pricing_term)}}</td>
                            <td class="num">${{money(row.list_price)}}</td>
                            <td class="num">${{money(row.extended_list_price)}}</td>
                            <td class="num">${{Number(row.discount_percent || 0).toLocaleString()}}</td>
                            <td class="num"><strong>${{money(row.extended_selling_price)}}</strong></td>
                            <td>${{esc(row.service_type)}}</td>
                        </tr>
                        `}}
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
            <div style="display:flex; justify-content:space-between; align-items:center; gap:12px; flex-wrap:wrap;">
                <h3>${{esc(option.label)}} - ${{money(option.total || 0)}}</h3>
                <button id="downloadBomBtn" class="btn btn-primary" type="button" onclick="downloadBom()">Download BOM</button>
            </div>
            ${{renderRows(option.rows || [])}}
        </div>
    `;
}}

async function downloadBom() {{
    const raw = localStorage.getItem("quoteData");
    const optionKey = activeOption;
    const btn = document.getElementById("downloadBomBtn");

    if (!raw) return;

    if (btn) {{
        btn.disabled = true;
        btn.innerText = "Đang xuất BOM...";
    }}

    try {{
        const res = await fetch("/api/download-bom", {{
            method: "POST",
            headers: {{ "Content-Type": "application/json" }},
            body: JSON.stringify({{ quote_data: JSON.parse(raw), option_key: optionKey }})
        }});

        if (!res.ok) {{
            alert("Không download được BOM.");
            return;
        }}

        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `network_bom_${{optionKey || "all"}}.xlsx`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
    }} catch (error) {{
        alert("Không download được BOM. Vui lòng thử lại.");
    }} finally {{
        if (btn) {{
            btn.disabled = false;
            btn.innerText = "Download BOM";
        }}
    }}
}}

loadBom();
</script>
</body>
</html>
    """