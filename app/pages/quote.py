from app.pages.styles import BASE_STYLE, render_nav


def render_quote_page(user=None, solution_area: str = "campus"):
    solution_base = "/dc-sdn" if str(solution_area or "").lower() == "dc-sdn" else "/campus"
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
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 14px;
        }}

        .quote-metric {{
            background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
            border: 1px solid #dbeafe;
            border-radius: 12px;
            padding: 18px 20px;
            min-height: 126px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}

        .quote-metric .label {{
            font-size: 12px;
            color: #64748b;
            margin-bottom: 6px;
        }}

        .quote-metric .value {{
            font-size: 30px;
            font-weight: 800;
            color: #0f172a;
            line-height: 1.1;
        }}

        .quote-metric.dc-metric {{
            background: linear-gradient(180deg, #fff7ed 0%, #fffaf4 100%);
            border-color: #fed7aa;
        }}

        .quote-metric.dc-metric .label {{
            color: #9a3412;
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

        #quote_block > .table-card:first-child {{
            margin-top: 28px;
        }}

        .table-card-header {{
            padding: 18px 20px 10px;
            border-bottom: 1px solid #e2e8f0;
        }}

        .table-card-header h2 {{
            margin: 0;
            font-size: 22px;
        }}

        .solution-label {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 10px;
            border-radius: 999px;
            background: #eff6ff;
            color: #1d4ed8;
            font-size: 12px;
            font-weight: 800;
            margin-bottom: 10px;
        }}

        .solution-label.dc {{
            background: #fff7ed;
            color: #9a3412;
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

        .quote-table tbody td:nth-child(4),
        .quote-table tbody td:nth-child(5),
        .quote-table tbody td:nth-child(6) {{
            background: #f8fbff;
        }}

        .quote-table tbody td:nth-child(7),
        .quote-table tbody td:nth-child(8),
        .quote-table tbody td:nth-child(9) {{
            background: #f1fcfd;
        }}

        .quote-table tbody td:nth-child(10),
        .quote-table tbody td:nth-child(11),
        .quote-table tbody td:nth-child(12) {{
            background: #faf7ff;
        }}

        .quote-table tbody tr:hover td:nth-child(4),
        .quote-table tbody tr:hover td:nth-child(5),
        .quote-table tbody tr:hover td:nth-child(6) {{
            background: #eef6ff;
        }}

        .quote-table tbody tr:hover td:nth-child(7),
        .quote-table tbody tr:hover td:nth-child(8),
        .quote-table tbody tr:hover td:nth-child(9) {{
            background: #e6fbfd;
        }}

        .quote-table tbody tr:hover td:nth-child(10),
        .quote-table tbody tr:hover td:nth-child(11),
        .quote-table tbody tr:hover td:nth-child(12) {{
            background: #f4edff;
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

        .quote-table tbody tr.group-campus td:nth-child(-n+3) {{
            background: #eff6ff;
            border-color: #bfdbfe;
        }}

        .quote-table tbody tr.group-server td:nth-child(-n+3) {{
            background: #f5f3ff;
            border-color: #ddd6fe;
        }}

        .quote-table tbody tr.group-wan td:nth-child(-n+3) {{
            background: #ecfdf5;
            border-color: #bbf7d0;
        }}

        .quote-table tbody tr.group-campus:hover td:nth-child(-n+3) {{
            background: #dbeafe;
        }}

        .quote-table tbody tr.group-server:hover td:nth-child(-n+3) {{
            background: #ede9fe;
        }}

        .quote-table tbody tr.group-wan:hover td:nth-child(-n+3) {{
            background: #d1fae5;
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

        .check-dc-button {{
            display: block;
            border: 1px solid #fed7aa;
            background: #fff7ed;
            color: #9a3412;
            border-radius: 10px;
            padding: 9px 12px;
            font-weight: 800;
            cursor: pointer;
            width: 100%;
            text-align: center;
            text-decoration: none;
        }}

        .check-dc-button:hover {{
            background: #ffedd5;
        }}

        .dc-quote-card {{
            border-color: #fed7aa;
            background: #fff7ed;
            margin-top: 28px;
        }}

        .dc-quote-card .table-card-header {{
            background: linear-gradient(90deg, #fff7ed 0, #ffffff 48%);
        }}

        .dc-quote-table {{
            min-width: 980px;
        }}

        .dc-quote-table th {{
            background: #ffedd5 !important;
        }}

        .dc-quote-table td {{
            background: #fffaf4 !important;
        }}

        .dc-quote-table tbody tr:hover td {{
            background: #fff3e6 !important;
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

        .group-summary-table .dc-summary-row td {{
            background: #fff7ed;
            border-top-color: #fed7aa;
            border-bottom-color: #fed7aa;
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
<body class="solution-{solution_area}">
{render_nav("quote", user, solution_area)}
<div class="container">
    <div class="page-header">
        <div class="page-header-left">
            <h1>Chọn model giải pháp</h1>
            <div class="subtitle"></div>
        </div>
    </div>
    <div id="summary_block"></div>
    <div id="quote_block"></div>
    <div id="group_summary_block"></div>

    <div class="actions">
        <a class="btn btn-primary" href="{solution_base}/bom">Xuất BOM</a>
        <a class="btn btn-secondary" href="{solution_base}/calculation-results">Quay lại kết quả tính toán</a>
        <a class="btn btn-secondary" href="{solution_base}/survey">Quay lại khảo sát</a>
    </div>
</div>

<script>
const SOLUTION_AREA = "{solution_area}";
let currentQuote = null;

function money(v) {{
    return "$" + Number(v || 0).toLocaleString(undefined, {{
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }});
}}

function isDcSdnLine(line) {{
    return String(line && line.group ? line.group : "").trim().toLowerCase() === "dc-sdn";
}}

function scrollToDcSdnQuote() {{
    const target = document.getElementById("dc_sdn_quote_block");
    if (!target) {{
        window.location.href = "/dc-sdn/quote";
        return;
    }}
    target.scrollIntoView({{ behavior: "smooth", block: "start" }});
}}

function choiceSortKey(choice) {{
    const model = String(choice && choice.model ? choice.model : "");
    const price = Number(choice && choice.price ? choice.price : 0);

    if (model.trim().toLowerCase() === "check dc-sdn") return [0, 0, model];
    if (price > 0) return [1, price, model];
    return [2, price, model];
}}

function compareChoicesByPrice(a, b) {{
    const ak = choiceSortKey(a);
    const bk = choiceSortKey(b);

    for (let i = 0; i < ak.length; i += 1) {{
        if (ak[i] < bk[i]) return -1;
        if (ak[i] > bk[i]) return 1;
    }}

    return 0;
}}

function sameChoice(a, b) {{
    return Boolean(a && b)
        && String(a.model || "") === String(b.model || "")
        && Number(a.price || 0) === Number(b.price || 0);
}}

function lineQuantity(line) {{
    const quantity = Number(line && line.quantity !== undefined ? line.quantity : 0);
    return Number.isFinite(quantity) ? quantity : 0;
}}

function selectedAmount(line, opt) {{
    const quantity = lineQuantity(line);
    if (quantity <= 0) return 0;

    const selected = line.selected && line.selected[opt] ? line.selected[opt] : null;
    return quantity * Number(selected && selected.price ? selected.price : 0);
}}

function normalizeLineChoiceOrder(line) {{
    if (!line.options) line.options = {{}};
    if (!line.user_selected) line.user_selected = {{}};

    ["opt1", "opt2", "opt3"].forEach(opt => {{
        const choices = (line.options && line.options[opt]) ? [...line.options[opt]] : [];
        line.options[opt] = choices.sort(compareChoicesByPrice);

        if (line.options[opt].length && !line.user_selected[opt]) {{
            line.selected[opt] = line.options[opt][0];
        }}
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

    normalizeLineChoiceOrder(line);

    ["opt1", "opt2", "opt3"].forEach(opt => {{
        const choices = (line.options && line.options[opt]) ? line.options[opt] : [];
        if (!line.selected[opt] && choices.length > 0) {{
            line.selected[opt] = choices[0];
        }}
        if (line.selected[opt]) {{
            line.amount[opt] = selectedAmount(line, opt);
        }} else {{
            line.amount[opt] = 0;
        }}
    }});

    if (isDcSdnLine(line)) {{
        const selected = line.selected.opt1 || line.selected.opt2 || line.selected.opt3;
        if (selected) {{
            ["opt1", "opt2", "opt3"].forEach(opt => {{
                line.selected[opt] = selected;
                line.amount[opt] = selectedAmount(line, opt);
            }});
        }}
    }}
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
    const selected = choices[selectedIndex];

    if (selected && String(selected.model || "").trim().toLowerCase() === "check dc-sdn") {{
        return `
            <a class="check-dc-button" href="/dc-sdn/quote">
                Check DC-SDN
            </a>
            <div class="device-meta">Bấm để chọn thiết bị DC-SDN riêng.</div>
        `;
    }}

    let html = `<select class="device-select" onchange="changeModel(${{index}}, '${{opt}}', this.value)">`;
    choices.forEach((c, i) => {{
        html += `<option value="${{i}}" ${{i === selectedIndex ? "selected" : ""}}>${{c.model}}</option>`;
    }});
    html += `</select>`;

    return html;
}}

function renderPrice(line, opt) {{
    const selected = line.selected && line.selected[opt] ? line.selected[opt] : null;
    if (!selected) return `<span class="muted">-</span>`;
    return money(selected.price || 0);
}}

function renderAmount(line, opt) {{
    return money(selectedAmount(line, opt));
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
    if (!line.user_selected) line.user_selected = {{}};
    line.user_selected[opt] = true;
    line.amount[opt] = selectedAmount(line, opt);

    localStorage.setItem("quoteData", JSON.stringify(currentQuote));
    renderQuote(scrollState);
}}

function changeDcSdnModel(index, choiceIndex) {{
    const scrollState = getQuoteScrollState();
    const line = currentQuote.quote.quote_lines[index];
    const choices = (line.options && line.options.opt1) ? line.options.opt1 : [];
    const choice = choices[Number(choiceIndex)];

    if (!choice) return;

    if (!line.user_selected) line.user_selected = {{}};
    ["opt1", "opt2", "opt3"].forEach(opt => {{
        line.selected[opt] = choice;
        line.user_selected[opt] = true;
        line.amount[opt] = selectedAmount(line, opt);
    }});

    localStorage.setItem("quoteData", JSON.stringify(currentQuote));
    renderQuote(scrollState);
}}

function canonicalGroupName(group) {{
    const raw = String(group || "").trim();
    const key = raw.toLowerCase();

    if (key.includes("dc-sdn")) return "DC-SDN";
    if (key.includes("server farm")) return "Server Farm";
    if (key.includes("wan")) return "WAN";
    if (key.includes("campus")) return "Campus - Trụ sở chính";
    return raw || "Khác";
}}

function groupRowClass(group) {{
    const normalized = canonicalGroupName(group).toLowerCase();
    if (normalized.includes("campus")) return "group-campus";
    if (normalized.includes("server farm")) return "group-server";
    if (normalized.includes("wan")) return "group-wan";
    return "";
}}
function renderSummary(lines) {{
    const totals = {{ opt1: 0, opt2: 0, opt3: 0 }};
    const groupTotals = {{}};

    lines.forEach(line => {{
        const group = canonicalGroupName(line.group);

        if (!groupTotals[group]) {{
            groupTotals[group] = {{ opt1: 0, opt2: 0, opt3: 0 }};
        }}

        ["opt1", "opt2", "opt3"].forEach(opt => {{
            const amount = selectedAmount(line, opt);
            if (!line.amount) line.amount = {{}};
            line.amount[opt] = amount;
            totals[opt] += amount;
            groupTotals[group][opt] += amount;
        }});
    }});

    let dcSingleTotal = 0;
    if (groupTotals["DC-SDN"]) {{
        dcSingleTotal = groupTotals["DC-SDN"].opt1 || groupTotals["DC-SDN"].opt2 || groupTotals["DC-SDN"].opt3 || 0;
        ["opt1", "opt2", "opt3"].forEach(opt => {{
            totals[opt] = totals[opt] - groupTotals["DC-SDN"][opt] + dcSingleTotal;
            groupTotals["DC-SDN"][opt] = dcSingleTotal;
        }});
    }}

    if (SOLUTION_AREA === "dc-sdn") {{
        document.getElementById("summary_block").innerHTML = `
            <div class="group-summary-card">
                <div class="summary-grid-quote">
                    <div class="quote-metric dc-metric">
                        <div class="label">Giải pháp DC-SDN</div>
                        <div class="value">${{money(dcSingleTotal)}}</div>
                    </div>
                </div>
            </div>
        `;
        return totals;
    }}

    const campusTotals = {{
        opt1: totals.opt1 - dcSingleTotal,
        opt2: totals.opt2 - dcSingleTotal,
        opt3: totals.opt3 - dcSingleTotal
    }};

    let groupRows = "";
    const preferredOrder = ["Campus - Trụ sở chính", "Server Farm", "WAN", "DC-SDN"];
    const orderedGroups = [
        ...preferredOrder.filter(group => groupTotals[group]),
        ...Object.keys(groupTotals).filter(group => !preferredOrder.includes(group)).sort()
    ];

    orderedGroups.forEach(group => {{
        if (group === "DC-SDN") {{
            return;
        }}

        groupRows += `
            <tr class="${{groupRowClass(group)}}">
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
                    <div class="label">Giải pháp Campus - Option 1</div>
                    <div class="value">${{money(campusTotals.opt1)}}</div>
                </div>
                <div class="quote-metric">
                    <div class="label">Giải pháp Campus - Option 2</div>
                    <div class="value">${{money(campusTotals.opt2)}}</div>
                </div>
                <div class="quote-metric">
                    <div class="label">Giải pháp Campus - Option 3</div>
                    <div class="value">${{money(campusTotals.opt3)}}</div>
                </div>
                ${{dcSingleTotal > 0 ? `
                    <div class="quote-metric dc-metric">
                        <div class="label">Giải pháp DC-SDN</div>
                        <div class="value">${{money(dcSingleTotal)}}</div>
                    </div>
                ` : ""}}
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

function renderDcSdnSelector(index, line) {{
    const choices = (line.options && line.options.opt1) ? line.options.opt1 : [];

    if (!choices.length) {{
        return `<span class="empty-option">chưa có model phù hợp</span>`;
    }}

    const selectedIndex = getSelectedIndex(line, "opt1");
    let html = `<select class="device-select" onchange="changeDcSdnModel(${{index}}, this.value)">`;
    choices.forEach((c, i) => {{
        html += `<option value="${{i}}" ${{i === selectedIndex ? "selected" : ""}}>${{c.model}}</option>`;
    }});
    html += `</select>`;

    return html;
}}

function renderDcSdnQuoteTable(entries) {{
    if (!entries.length) return "";

    let rows = "";
    entries.forEach(entry => {{
        const line = entry.line;
        rows += `
            <tr class="${{groupRowClass(line.group)}}">
                <td class="left-col item-cell">${{line.item_type}}</td>
                <td class="left-col qty-cell">${{line.quantity}}</td>
                <td>${{renderDcSdnSelector(entry.index, line)}}</td>
                <td class="price-cell">${{renderPrice(line, "opt1")}}</td>
                <td class="amount-cell">${{renderAmount(line, "opt1")}}</td>
            </tr>
        `;
    }});

    return `
        <div class="table-card dc-quote-card" id="dc_sdn_quote_block">
            <div class="table-card-header">
                <div class="solution-label dc">Giải pháp DC-SDN</div>
                <h2>Chọn thiết bị DC-SDN</h2>
            </div>
            <div class="table-wrap">
                <table class="quote-table dc-quote-table">
                    <thead>
                        <tr>
                            <th class="left-col">Hạng mục DC-SDN</th>
                            <th class="left-col">SL</th>
                            <th>Chọn thiết bị</th>
                            <th>Đơn giá</th>
                            <th>Thành tiền</th>
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

function renderQuoteTable(lines) {{
    let rows = "";

    const entries = lines.map((line, index) => ({{ line, index }}));
    const systemEntries = entries.filter(entry => !isDcSdnLine(entry.line));
    const dcEntries = entries.filter(entry => isDcSdnLine(entry.line));

    if (SOLUTION_AREA === "dc-sdn") {{
        document.getElementById("quote_block").innerHTML = renderDcSdnQuoteTable(dcEntries) || `
            <div class="card"><div class="empty-state">Không có line DC-SDN.</div></div>
        `;
        return;
    }}

    systemEntries.forEach(entry => {{
        const line = entry.line;
        const index = entry.index;
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
                <div class="solution-label">Giải pháp Campus</div>
                <h2>Bảng chọn model Campus / Server Farm / WAN</h2>
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

    const visibleLines = SOLUTION_AREA === "dc-sdn"
        ? lines.filter(line => isDcSdnLine(line))
        : lines.filter(line => !isDcSdnLine(line));

    renderSummary(visibleLines);
    renderQuoteTable(lines);
    renderGroupSummary(lines);
    restoreQuoteScrollState(scrollState);
}}

renderQuote();
</script>
</body>
</html>
    """
