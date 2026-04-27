from app.pages.styles import BASE_STYLE, render_nav


def render_quote_page():
    return f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="utf-8" />
    <title>Quote</title>
    {BASE_STYLE}
    <style>
        .page-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 20px;
            margin-bottom: 18px;
        }}

        .page-header-left h1 {{
            margin-bottom: 6px;
        }}

        .page-header-right {{
            min-width: 260px;
        }}

        .sticky-summary {{
            position: sticky;
            top: 16px;
        }}

        .summary-grid-quote {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
        }}

        .quote-metric {{
            background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
            border: 1px solid #dbeafe;
            border-radius: 14px;
            padding: 14px;
        }}

        .quote-metric .label {{
            font-size: 12px;
            color: #64748b;
            margin-bottom: 6px;
        }}

        .quote-metric .value {{
            font-size: 24px;
            font-weight: 800;
            color: #0f172a;
        }}

        .quote-layout {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 18px;
        }}

        .table-card {{
            background: #fff;
            border-radius: 16px;
            border: 1px solid #dbe3ef;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
            overflow: hidden;
        }}

        .table-card-header {{
            padding: 18px 20px 10px;
            border-bottom: 1px solid #e2e8f0;
        }}

        .table-card-header h2 {{
            margin: 0;
            font-size: 22px;
        }}

        .table-card-header p {{
            margin: 8px 0 0;
            color: #64748b;
            font-size: 14px;
        }}

        .table-wrap {{
            overflow-x: auto;
        }}

        .quote-table {{
            width: 100%;
            min-width: 1680px;
            border-collapse: separate;
            border-spacing: 0;
            font-size: 13px;
        }}

        .quote-table th,
        .quote-table td {{
            border-right: 1px solid #e2e8f0;
            border-bottom: 1px solid #e2e8f0;
            padding: 10px 10px;
            vertical-align: top;
            background: #fff;
        }}

        .quote-table th:last-child,
        .quote-table td:last-child {{
            border-right: none;
        }}

        .quote-table thead tr:first-child th {{
            text-align: center;
            font-size: 13px;
            font-weight: 800;
            color: #0f172a;
            position: sticky;
            top: 0;
            z-index: 3;
        }}

        .quote-table thead tr:nth-child(2) th {{
            position: sticky;
            top: 42px;
            z-index: 3;
            background: #f8fafc;
        }}

        .quote-table thead th {{
            background: #f8fafc;
        }}

        .quote-table tbody tr:hover td {{
            background: #fafcff;
        }}

        .quote-table .left-col {{
            background: #fcfdff;
            font-weight: 600;
        }}

        .quote-table .group-cell {{
            font-weight: 700;
            color: #0f172a;
            min-width: 150px;
        }}

        .quote-table .item-cell {{
            min-width: 250px;
        }}

        .quote-table .qty-cell {{
            text-align: center;
            font-weight: 700;
            min-width: 70px;
        }}

        .opt-head-1 {{
            background: #eff6ff !important;
            color: #1d4ed8 !important;
        }}

        .opt-head-2 {{
            background: #ecfeff !important;
            color: #0f766e !important;
        }}

        .opt-head-3 {{
            background: #f5f3ff !important;
            color: #6d28d9 !important;
        }}

        .opt-subhead-1 {{
            background: #f8fbff !important;
        }}

        .opt-subhead-2 {{
            background: #f3feff !important;
        }}

        .opt-subhead-3 {{
            background: #faf7ff !important;
        }}

        .device-select {{
            width: 100%;
            min-width: 240px;
            padding: 9px 10px;
            border-radius: 10px;
            border: 1px solid #cbd5e1;
            background: #fff;
            font-size: 13px;
        }}

        .price-cell {{
            min-width: 120px;
            white-space: nowrap;
            text-align: right;
            font-weight: 700;
            color: #0f172a;
        }}

        .amount-cell {{
            min-width: 130px;
            white-space: nowrap;
            text-align: right;
            font-weight: 800;
            color: #0f172a;
        }}

        .muted {{
            color: #94a3b8;
        }}

        .empty-option {{
            display: inline-block;
            padding: 6px 10px;
            border-radius: 999px;
            background: #f8fafc;
            border: 1px dashed #cbd5e1;
            color: #64748b;
            font-size: 12px;
            white-space: nowrap;
        }}

        .device-meta {{
            margin-top: 6px;
            font-size: 12px;
            color: #64748b;
            line-height: 1.4;
        }}

        .group-summary-card {{
            background: #fff;
            border-radius: 16px;
            border: 1px solid #dbe3ef;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
            padding: 18px 20px;
        }}

        .group-summary-card h3 {{
            margin: 0 0 14px 0;
            font-size: 20px;
        }}

        .group-summary-table {{
            width: 100%;
            border-collapse: collapse;
        }}

        .group-summary-table th,
        .group-summary-table td {{
            border: 1px solid #e2e8f0;
            padding: 10px;
            text-align: left;
        }}

        .group-summary-table th {{
            background: #f8fafc;
        }}

        @media (max-width: 1024px) {{
            .summary-grid-quote {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}

        @media (max-width: 640px) {{
            .summary-grid-quote {{
                grid-template-columns: 1fr;
            }}

            .page-header {{
                flex-direction: column;
            }}
        }}
    </style>
</head>
<body>
{render_nav("quote")}
<div class="container">
    <div class="page-header">
        <div class="page-header-left">
            <h1>Chọn model và tổng hợp báo giá</h1>
            <div class="subtitle"></div>
        </div>
    </div>
    <div id="summary_block"></div>
    <div id="quote_block"></div>
    <div id="group_summary_block"></div>

    <div class="actions">
        <a class="btn btn-primary" href="/bom">Xuất BOM</a>
        <a class="btn btn-secondary" href="/calculation-results">Quay lại kết quả tính toán</a>
        <a class="btn btn-secondary" href="/survey">Quay lại khảo sát</a>
    </div>
</div>

<script>
let currentQuote = null;

function money(v) {{
    return "$" + Number(v || 0).toLocaleString(undefined, {{
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }});
}}

function ensureLineDefaults(line) {{
    if (!line.selected) {{
        line.selected = {{
            opt1: null,
            opt2: null,
            opt3: null
        }};
    }}

    if (!line.amount) {{
        line.amount = {{
            opt1: 0,
            opt2: 0,
            opt3: 0
        }};
    }}

    ["opt1", "opt2", "opt3"].forEach(opt => {{
        const choices = (line.options && line.options[opt]) ? line.options[opt] : [];
        if (!line.selected[opt] && choices.length > 0) {{
            line.selected[opt] = choices[0];
        }}
        if (line.selected[opt]) {{
            line.amount[opt] = Number(line.quantity || 0) * Number(line.selected[opt].price || 0);
        }} else {{
            line.amount[opt] = 0;
        }}
    }});
}}

function getSelectedIndex(line, opt) {{
    const choices = (line.options && line.options[opt]) ? line.options[opt] : [];
    const selected = line.selected && line.selected[opt] ? line.selected[opt] : null;
    if (!selected) return 0;

    const idx = choices.findIndex(c => c.model === selected.model && Number(c.price || 0) === Number(selected.price || 0));
    return idx >= 0 ? idx : 0;
}}

function renderDeviceSelector(index, opt, line) {{
    const choices = (line.options && line.options[opt]) ? line.options[opt] : [];

    if (!choices.length) {{
        return `<span class="empty-option">chưa có model phù hợp</span>`;
    }}

    const selectedIndex = getSelectedIndex(line, opt);

    let html = `<select class="device-select" onchange="changeModel(${{index}}, '${{opt}}', this.value)">`;
    choices.forEach((c, i) => {{
        const cls = c.class ? ` | ${{c.class}}` : "";
        html += `<option value="${{i}}" ${{i === selectedIndex ? "selected" : ""}}>${{c.model}}${{cls}}</option>`;
    }});
    html += `</select>`;

    const selected = choices[selectedIndex];
    html += `
        <div class="device-meta">
            <div><strong>sheet:</strong> ${{selected.sheet || "-"}}</div>
            <div><strong>class:</strong> ${{selected.class || "-"}}</div>
        </div>
    `;
    return html;
}}

function renderPrice(line, opt) {{
    const selected = line.selected && line.selected[opt] ? line.selected[opt] : null;
    if (!selected) return `<span class="muted">-</span>`;
    return money(selected.price || 0);
}}

function renderAmount(line, opt) {{
    return money(line.amount && line.amount[opt] ? line.amount[opt] : 0);
}}

function getQuoteScrollState() {{
    const tableWrap = document.querySelector("#quote_block .table-wrap");

    return {{
        tableLeft: tableWrap ? tableWrap.scrollLeft : 0,
        tableTop: tableWrap ? tableWrap.scrollTop : 0,
        windowX: window.scrollX,
        windowY: window.scrollY
    }};
}}

function restoreQuoteScrollState(state) {{
    if (!state) return;

    requestAnimationFrame(() => {{
        const tableWrap = document.querySelector("#quote_block .table-wrap");

        if (tableWrap) {{
            tableWrap.scrollLeft = state.tableLeft || 0;
            tableWrap.scrollTop = state.tableTop || 0;
        }}

        window.scrollTo(state.windowX || 0, state.windowY || 0);
    }});
}}

function changeModel(index, opt, choiceIndex) {{
    const scrollState = getQuoteScrollState();
    const line = currentQuote.quote.quote_lines[index];
    const choices = (line.options && line.options[opt]) ? line.options[opt] : [];
    const choice = choices[Number(choiceIndex)];

    if (!choice) return;

    line.selected[opt] = choice;
    line.amount[opt] = Number(line.quantity || 0) * Number(choice.price || 0);

    localStorage.setItem("quoteData", JSON.stringify(currentQuote));
    renderQuote(scrollState);
}}

function renderSummary(lines) {{
    const totals = {{ opt1: 0, opt2: 0, opt3: 0 }};
    const groupTotals = {{}};

    lines.forEach(line => {{
        if (!groupTotals[line.group]) {{
            groupTotals[line.group] = {{ opt1: 0, opt2: 0, opt3: 0 }};
        }}

        ["opt1", "opt2", "opt3"].forEach(opt => {{
            const amount = Number(line.amount && line.amount[opt] ? line.amount[opt] : 0);
            totals[opt] += amount;
            groupTotals[line.group][opt] += amount;
        }});
    }});

    let groupRows = "";
    Object.keys(groupTotals).forEach(group => {{
        groupRows += `
            <tr>
                <td><strong>${{group}}</strong></td>
                <td>${{money(groupTotals[group].opt1)}}</td>
                <td>${{money(groupTotals[group].opt2)}}</td>
                <td>${{money(groupTotals[group].opt3)}}</td>
            </tr>
        `;
    }});

    document.getElementById("summary_block").innerHTML = `
        <div class="group-summary-card">
            <div class="summary-grid-quote">
                <div class="quote-metric">
                    <div class="label">Option 1 - Low End</div>
                    <div class="value">${{money(totals.opt1)}}</div>
                </div>
                <div class="quote-metric">
                    <div class="label">Option 2 - Mid Range</div>
                    <div class="value">${{money(totals.opt2)}}</div>
                </div>
                <div class="quote-metric">
                    <div class="label">Option 3 - High End</div>
                    <div class="value">${{money(totals.opt3)}}</div>
                </div>
            </div>

            <div style="height:14px;"></div>

            <table class="group-summary-table">
                <thead>
                    <tr>
                        <th>Nhóm</th>
                        <th>Option 1</th>
                        <th>Option 2</th>
                        <th>Option 3</th>
                    </tr>
                </thead>
                <tbody>
                    ${{groupRows}}
                </tbody>
            </table>
        </div>
    `;

    return totals;
}}

function renderGroupSummary(lines) {{
    document.getElementById("group_summary_block").innerHTML = "";
}}

function renderQuoteTable(lines) {{
    let rows = "";

    lines.forEach((line, index) => {{
        rows += `
            <tr>
                <td class="left-col group-cell">${{line.group}}</td>
                <td class="left-col item-cell">${{line.item_type}}</td>
                <td class="left-col qty-cell">${{line.quantity}}</td>

                <td>${{renderDeviceSelector(index, "opt1", line)}}</td>
                <td class="price-cell">${{renderPrice(line, "opt1")}}</td>
                <td class="amount-cell">${{renderAmount(line, "opt1")}}</td>

                <td>${{renderDeviceSelector(index, "opt2", line)}}</td>
                <td class="price-cell">${{renderPrice(line, "opt2")}}</td>
                <td class="amount-cell">${{renderAmount(line, "opt2")}}</td>

                <td>${{renderDeviceSelector(index, "opt3", line)}}</td>
                <td class="price-cell">${{renderPrice(line, "opt3")}}</td>
                <td class="amount-cell">${{renderAmount(line, "opt3")}}</td>
            </tr>
        `;
    }});

    document.getElementById("quote_block").innerHTML = `
        <div class="table-card">
            <div class="table-card-header">
                <h2>Bảng chọn model theo từng option</h2>
                
            </div>

            <div class="table-wrap">
                <table class="quote-table">
                    <thead>
                        <tr>
                            <th rowspan="2" class="left-col">Nhóm</th>
                            <th rowspan="2" class="left-col">Hạng mục</th>
                            <th rowspan="2" class="left-col">SL</th>

                            <th colspan="3" class="opt-head-1">Option 1 - Low End</th>
                            <th colspan="3" class="opt-head-2">Option 2 - Mid Range</th>
                            <th colspan="3" class="opt-head-3">Option 3 - High End</th>
                        </tr>
                        <tr>
                            <th class="opt-subhead-1">Chọn thiết bị</th>
                            <th class="opt-subhead-1">Đơn giá</th>
                            <th class="opt-subhead-1">Thành tiền</th>

                            <th class="opt-subhead-2">Chọn thiết bị</th>
                            <th class="opt-subhead-2">Đơn giá</th>
                            <th class="opt-subhead-2">Thành tiền</th>

                            <th class="opt-subhead-3">Chọn thiết bị</th>
                            <th class="opt-subhead-3">Đơn giá</th>
                            <th class="opt-subhead-3">Thành tiền</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${{rows}}
                    </tbody>
                </table>
            </div>
        </div>
    `;
}}

function renderQuote(scrollState = null) {{
    const raw = localStorage.getItem("quoteData");

    if (!raw) {{
        document.getElementById("summary_block").innerHTML = "";
        document.getElementById("quote_block").innerHTML = `
            <div class="card">
                <div class="empty-state">
                    Chưa có dữ liệu báo giá. Hãy quay lại trang khảo sát.
                </div>
            </div>
        `;
        document.getElementById("group_summary_block").innerHTML = "";
        return;
    }}

    currentQuote = JSON.parse(raw);

    const lines = (currentQuote.quote && currentQuote.quote.quote_lines)
        ? currentQuote.quote.quote_lines
        : [];

    lines.forEach(line => ensureLineDefaults(line));
    localStorage.setItem("quoteData", JSON.stringify(currentQuote));

    renderSummary(lines);
    renderQuoteTable(lines);
    renderGroupSummary(lines);
    restoreQuoteScrollState(scrollState);
}}

renderQuote();
</script>
</body>
</html>
    """
