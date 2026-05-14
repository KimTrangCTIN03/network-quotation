from app.pages.styles import BASE_STYLE, render_nav


def render_model_quote_page(user=None):
    return f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="utf-8" />
    <title>Chọn model & tổng hợp báo giá</title>
    {BASE_STYLE}
    <style>
        .page-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 20px;
            margin-bottom: 14px;
        }}

        .device-tools {{
            display: grid;
            grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
            gap: 16px;
            margin-bottom: 18px;
        }}

        .device-tools.single {{
            grid-template-columns: 1fr;
        }}

        .model-tabs {{
            display: flex;
            gap: 8px;
            margin-bottom: 12px;
            border-bottom: 1px solid #cbd5e1;
        }}

        .model-tab {{
            border: 1px solid transparent;
            background: transparent;
            padding: 8px 12px;
            font-weight: 800;
            color: #475569;
            cursor: pointer;
            border-radius: 8px 8px 0 0;
            font-size: 13px;
        }}

        .model-tab.active {{
            background: #fff;
            color: #1d4ed8;
            border-color: #cbd5e1;
            border-bottom-color: #fff;
            margin-bottom: -1px;
        }}

        .model-section {{
            display: none;
        }}

        .model-section.active {{
            display: block;
        }}

        .tool-panel {{
            background: #fff;
            border: 1px solid #dbe3ef;
            border-radius: 10px;
            padding: 12px;
            box-shadow: 0 8px 20px rgba(15, 23, 42, 0.04);
        }}

        .tool-panel h2 {{
            font-size: 16px;
            margin: 0 0 10px;
        }}

        .tool-grid {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 10px;
        }}

        .spec-blocks {{
            display: grid;
            grid-template-columns: repeat(6, minmax(0, 1fr));
            gap: 6px;
            margin-bottom: 10px;
        }}

        .spec-block {{
            border: 1px solid #cbd5e1;
            background: #f8fafc;
            border-radius: 8px;
            padding: 8px 10px;
            cursor: pointer;
            font-weight: 700;
            color: #334155;
            font-size: 13px;
        }}

        .spec-block.active {{
            border-color: #2563eb;
            background: #eff6ff;
            color: #1d4ed8;
        }}

        .criteria-field {{
            display: none;
        }}

        .criteria-field.active {{
            display: block;
        }}

        .tool-panel textarea {{
            width: 100%;
            min-height: 162px;
            padding: 10px 12px;
            border: 1px solid #cbd5e1;
            border-radius: 10px;
            font-size: 13px;
            resize: vertical;
        }}

        .sheet-table {{
            min-width: 720px;
            table-layout: fixed;
        }}

        .sheet-table th {{
            background: #dbeafe;
            text-align: center;
            font-size: 15px;
        }}

        .sheet-table td {{
            padding: 0;
        }}

        .sheet-table input {{
            border: none;
            border-radius: 0;
            height: 34px;
            font-size: 14px;
        }}

        .sheet-table input:focus {{
            outline: 2px solid #2563eb;
            outline-offset: -2px;
            background: #eff6ff;
        }}

        .sheet-table .price-cell,
        .sheet-table .total-cell {{
            padding: 8px;
            text-align: right;
            white-space: nowrap;
        }}

        .sheet-table .total-cell {{
            color: #dc2626;
            font-weight: 800;
            font-size: 16px;
        }}

        .quote-summary {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 12px;
            margin-bottom: 14px;
        }}

        .quote-metric {{
            background: #fff;
            border: 1px solid #dbe3ef;
            border-radius: 12px;
            padding: 16px;
        }}

        .quote-metric .label {{
            color: #64748b;
            font-size: 13px;
            margin-bottom: 8px;
        }}

        .quote-metric .value {{
            font-size: 24px;
            font-weight: 800;
        }}

        .quote-table-wrap {{
            overflow-x: auto;
            background: #fff;
            border: 1px solid #dbe3ef;
            border-radius: 12px;
        }}

        .quote-table {{
            min-width: 1180px;
        }}

        .quote-table th {{
            background: #f8fafc;
        }}

        .quote-table select {{
            min-width: 190px;
        }}

        .spec-sheet-wrap {{
            border-radius: 10px;
            border-color: #cbd5e1;
            background-color: #f8fafc;
        }}

        .spec-result-table {{
            min-width: 1180px;
            table-layout: fixed;
            border-collapse: collapse;
            background: #fff;
            font-size: 12.5px;
        }}

        .spec-result-table th,
        .spec-result-table td {{
            height: 28px;
            padding: 3px 5px;
            border: 1px solid #d6dee9;
            text-align: center;
            vertical-align: middle;
            background: #fff;
        }}

        .spec-result-table th {{
            font-size: 13px;
            font-weight: 800;
        }}

        .spec-result-table .cyan-head {{
            background: #dbeafe;
            color: #0f172a;
            border-color: #93c5fd;
        }}

        .spec-result-table .section-head {{
            background: #e8f2ff;
            color: #0f172a;
            border-color: #93c5fd;
        }}

        .spec-result-table .yellow-cell {{
            background: #fff7cc;
            border-color: #f4d35e;
        }}

        .spec-result-table .sheet-input,
        .spec-result-table .sheet-select {{
            width: 100%;
            height: 26px;
            border: none;
            border-radius: 0;
            background: #fff7cc;
            text-align: center;
            font-size: 12.5px;
            padding: 3px;
        }}

        .spec-result-table .sheet-input:focus,
        .spec-result-table .sheet-select:focus {{
            outline: 2px solid #2563eb;
            outline-offset: -2px;
        }}

        .spec-result-table .left-block {{
            border-color: #cbd5e1;
        }}

        .spec-result-table .param-cell {{
            text-align: left;
            white-space: nowrap;
            color: #1e293b;
        }}

        .spec-result-table .best-col {{
            background: #f8fbff;
            border-left: 2px solid #2563eb;
            border-right: 2px solid #2563eb;
            border-top-color: #93c5fd;
            border-bottom-color: #93c5fd;
        }}

        .spec-result-table .freeze-gap {{
            width: 6px;
            padding: 0;
            background: #cbd5e1;
            border-left: 0;
            border-right: 0;
        }}

        .spec-result-table .blank-gap {{
            background: #fff;
        }}

        .spec-result-table .option-head {{
            background: #e0f2fe;
            color: #0f172a;
            text-align: left;
        }}

        .spec-result-table .option-label {{
            text-align: right;
            font-weight: 700;
            background: #f8fafc;
        }}

        .spec-result-table .btn {{
            padding: 7px 10px;
            border-radius: 8px;
            font-size: 12px;
            white-space: nowrap;
        }}

        .price-note {{
            color: #64748b;
            font-size: 12px;
            margin-top: 4px;
        }}

        @media (max-width: 1024px) {{
            .device-tools,
            .quote-summary,
            .spec-blocks {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
{render_nav("model_quote", user)}
<div class="container">
    <div class="page-header">
        <div>
            <h1>Chọn model & tổng hợp báo giá</h1>
            
        </div>
    </div>

    <div class="model-tabs">
        <button class="model-tab active" type="button" data-tab="recommend" onclick="setModelTab('recommend')">Chọn thiết bị</button>
        <button class="model-tab" type="button" data-tab="list" onclick="setModelTab('list')">Export BoQ on-demand</button>
    </div>

    <div id="recommendSection" class="model-section active">
    <div class="device-tools single">
        <div class="tool-panel">
            <h2>Đề xuất thiết bị theo yêu cầu</h2>
            <div class="spec-blocks">
                <button class="spec-block active" type="button" data-sheet="SwitchCampus" onclick="setSpecBlock('SwitchCampus')">SwitchCampus</button>
                <button class="spec-block" type="button" data-sheet="Router" onclick="setSpecBlock('Router')">Router</button>
                <button class="spec-block" type="button" data-sheet="ModularSwitch" onclick="setSpecBlock('ModularSwitch')">ModularSwitch</button>
                <button class="spec-block" type="button" data-sheet="NexusSwitch" onclick="setSpecBlock('NexusSwitch')">NexusSwitch</button>
                <button class="spec-block" type="button" data-sheet="WiFi" onclick="setSpecBlock('WiFi')">WiFi</button>
                <button class="spec-block" type="button" data-sheet="SFP" onclick="setSpecBlock('SFP')">SFP</button>
            </div>
            <div id="specInputBlock"></div>
            <div class="actions">
                <button class="btn btn-primary" type="button" onclick="recommendManualDevice()">Đề xuất</button>
            </div>
            <div id="manualRecommendMessage" class="success-box"></div>
        </div>
    </div>
    <div id="summaryBlock"></div>
    <div id="quoteBlock"></div>
    </div>

    <div id="listSection" class="model-section">
    <div class="device-tools single">
        <div class="tool-panel">
            <h2>Nhập list thiết bị</h2>
            <div class="quote-table-wrap">
                <table class="sheet-table">
                    <thead>
                        <tr>
                            <th>P/N</th>
                            <th>Số lượng</th>
                            <th id="manualTotalCell" class="total-cell">$0.00</th>
                            <th><button class="btn btn-secondary" type="button" onclick="exportManualBom()">Export BOM</button></th>
                        </tr>
                    </thead>
                    <tbody id="manualSheetBody"></tbody>
                </table>
            </div>
            <div class="actions">
                <button class="btn btn-primary" type="button" onclick="buildQuoteFromDeviceList(false)">Tổng hợp báo giá</button>
                <button class="btn btn-secondary" type="button" onclick="clearManualSheet()">Xóa bảng</button>
            </div>
            <div id="manualListMessage" class="error-box"></div>
        </div>
    </div>
    </div>

    <div class="actions">
        <button class="btn btn-primary" type="button" onclick="saveCurrentQuote()">Lưu bảng báo giá</button>
        <a class="btn btn-secondary" href="/model-bom">Xuất BOM</a>
        <a class="btn btn-secondary" href="/dashboard">Về Dashboard</a>
    </div>

</div>

<script>
let currentQuote = null;
let currentSpecsResult = null;
const MIN_MANUAL_ROWS = 1;
let manualRows = Array.from({{ length: MIN_MANUAL_ROWS }}, () => ({{ model: "", quantity: "", price: 0 }}));
let currentSpecSheet = "SwitchCampus";
let manualPriceTimer = null;
let stateSaveTimer = null;
let activeModelTab = "recommend";
let savedSpecRequirement = null;
let savedSpecQuantity = 1;
let restoringModelState = false;
let specStateBySheet = {{}};
const MODEL_QUOTE_PRICE_VERSION = "bom-price-v2";
const MODEL_STATE_KEY = "modelQuoteState:bom-price-v2";

const SPEC_SHEET_FIELDS = {{
    Router: [
        ["Throughput (Mbps)", "throughput_mbps"],
        ["Số lượng cổng WAN 1GE", "min_wan_1g"],
        ["Số lượng cổng WAN 10GE", "min_wan_10g"],
        ["Số lượng cổng LAN 1GE", "min_lan_1g"],
        ["Số lượng cổng LAN 10GE", "min_lan_10g"]
    ],
    SwitchCampus: [
        ["Switching Bandwidth - Full Duplex (Gbps)", "switching_bandwidth_gbps"],
        ["Forwarding Capacity (Mpps)", "forwarding_mpps"],
        ["Số lượng cổng 1GE đồng", "min_1g_rj45"],
        ["Số lượng cổng 1GE SFP", "min_1g_sfp"],
        ["Số lượng cổng 10GE đồng", "min_10g_rj45"],
        ["Số lượng cổng 10GE quang", "min_10g_sfp"],
        ["Số lượng cổng 100GE", "min_100g"],
        ["Stacking (Y/N)", "stacking"],
        ["PoE (Y/N)", "poe"]
    ],
    ModularSwitch: [
        ["Switching Bandwidth - Full Duplex (Gbps)", "switching_bandwidth_gbps"],
        ["Forwarding Capacity (Mpps)", "forwarding_mpps"],
        ["Số lượng cổng 1GE đồng", "min_1g_rj45"],
        ["Số lượng cổng 1GE SFP", "min_1g_sfp"],
        ["Số lượng cổng 10GE đồng", "min_10g_rj45"],
        ["Số lượng cổng 10GE quang", "min_10g_sfp"],
        ["Số lượng cổng 100GE", "min_100g"],
        ["Stacking (Y/N)", "stacking"],
        ["PoE (Y/N)", "poe"]
    ],
    NexusSwitch: [
        ["Switching Bandwidth - Full Duplex (Gbps)", "switching_bandwidth_gbps"],
        ["Forwarding Capacity (Mpps)", "forwarding_mpps"],
        ["Số lượng cổng 1GE đồng", "min_1g_rj45"],
        ["Số lượng cổng 1GE SFP", "min_1g_sfp"],
        ["Số lượng cổng 10GE đồng", "min_10g_rj45"],
        ["Số lượng cổng 10GE quang", "min_10g_sfp"],
        ["Số lượng cổng 100GE", "min_100g"]
    ],
    WiFi: [
        ["Loại Access Point (indoor/outdoor)", "ap_type"],
        ["Công nghệ WiFi (WiFi6/WiFi7)", "wifi_technology"],
        ["Số lượng người dùng trong phạm vi phủ sóng 1 AP", "wifi_users_per_ap"],
        ["Bán kính phủ sóng (m)", "wifi_radius_m"],
        ["Antenna Type (Omni or Directional)", "antenna_type"]
    ],
    SFP: [
        ["Tốc độ (1G/10G/100G)", "speed"],
        ["Khoảng cách truyền (km)", "distance"]
    ]
}};

const SPEC_LABEL_ALIASES = {{
    "Tốc độ (1G/10G/100G)": "speed",
    "Khoảng cách truyền (km)": "distance"
}};

function setModelTab(tabName) {{
    activeModelTab = tabName;
    document.querySelectorAll(".model-tab").forEach(button => {{
        button.classList.toggle("active", button.dataset.tab === tabName);
    }});
    document.getElementById("recommendSection").classList.toggle("active", tabName === "recommend");
    document.getElementById("listSection").classList.toggle("active", tabName === "list");
    scheduleModelStateSave();
}}

function setSpecBlock(sheetName) {{
    captureCurrentSpecState();
    currentSpecSheet = sheetName;
    document.querySelectorAll(".spec-block").forEach(button => {{
        button.classList.toggle("active", button.dataset.sheet === sheetName);
    }});

    const activeGroups = {{
        Router: ["criteria-router"],
        SwitchCampus: ["criteria-switch"],
        ModularSwitch: ["criteria-switch"],
        NexusSwitch: ["criteria-switch"],
        WiFi: ["criteria-wifi"],
        SFP: ["criteria-sfp"]
    }}[sheetName] || [];

    document.querySelectorAll(".criteria-field").forEach(field => {{
        field.classList.toggle("active", activeGroups.some(group => field.classList.contains(group)));
    }});
    const sheetState = specStateBySheet[sheetName] || {{}};
    currentSpecsResult = sheetState.result || null;
    savedSpecRequirement = sheetState.requirement || null;
    savedSpecQuantity = Number(sheetState.quantity || 1);
    renderSpecInputSheet(currentSpecsResult);
    document.getElementById("summaryBlock").innerHTML = "";
    document.getElementById("quoteBlock").innerHTML = currentSpecsResult ? renderSpecsQuoteTable(currentSpecsResult) : "";
    scheduleModelStateSave();

}}

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

function numberInput(id) {{
    const value = Number(document.getElementById(id).value || 0);
    return Number.isFinite(value) ? value : 0;
}}

function selectInput(id) {{
    return String(document.getElementById(id).value || "").trim();
}}

function selectedAmount(line, opt) {{
    const qty = Number(line.quantity || 0);
    const selected = line.selected && line.selected[opt] ? line.selected[opt] : {{}};
    return qty * Number(selected.price || 0);
}}

function fieldInputHtml(key, value = "") {{
    const safeValue = esc(value || "");
    if (["stacking", "poe"].includes(key)) {{
        return `
            <select class="sheet-select" id="req_${{key}}" onchange="scheduleModelStateSave()">
                <option value=""></option>
                <option value="Y" ${{safeValue === "Y" ? "selected" : ""}}>Y</option>
                <option value="N" ${{safeValue === "N" ? "selected" : ""}}>N</option>
            </select>
        `;
    }}
    if (key === "ap_type") {{
        return `
            <select class="sheet-select" id="req_${{key}}" onchange="scheduleModelStateSave()">
                <option value=""></option>
                <option value="indoor" ${{safeValue === "indoor" ? "selected" : ""}}>indoor</option>
                <option value="outdoor" ${{safeValue === "outdoor" ? "selected" : ""}}>outdoor</option>
            </select>
        `;
    }}
    if (key === "wifi_technology") {{
        return `
            <select class="sheet-select" id="req_${{key}}" onchange="scheduleModelStateSave()">
                <option value=""></option>
                <option value="WiFi6" ${{safeValue === "WiFi6" ? "selected" : ""}}>WiFi6</option>
                <option value="WiFi6E" ${{safeValue === "WiFi6E" ? "selected" : ""}}>WiFi6E</option>
                <option value="WiFi7" ${{safeValue === "WiFi7" ? "selected" : ""}}>WiFi7</option>
            </select>
        `;
    }}
    if (key === "antenna_type") {{
        return `
            <select class="sheet-select" id="req_${{key}}" onchange="scheduleModelStateSave()">
                <option value=""></option>
                <option value="Omni" ${{safeValue === "Omni" ? "selected" : ""}}>Omni</option>
                <option value="Directional" ${{safeValue === "Directional" ? "selected" : ""}}>Directional</option>
            </select>
        `;
    }}
    return `<input class="sheet-input" id="req_${{key}}" value="${{safeValue}}" oninput="scheduleModelStateSave()" />`;
}}

function collectSheetRequirement() {{
    const requirement = {{ device_spec_sheet: currentSpecSheet }};
    (SPEC_SHEET_FIELDS[currentSpecSheet] || []).forEach(([_label, key]) => {{
        const el = document.getElementById(`req_${{key}}`);
        if (!el) return;
        const raw = String(el.value || "").trim();
        if (!raw) return;
        const numeric = Number(raw);
        requirement[key] = Number.isFinite(numeric) && raw !== "" && !Number.isNaN(numeric) ? numeric : raw;
    }});
    return requirement;
}}

function currentDeviceQuantity() {{
    const el = document.getElementById("req_quantity");
    const value = el ? Number(el.value || 1) : 1;
    return Number.isFinite(value) && value > 0 ? value : 1;
}}

function captureCurrentSpecState() {{
    if (!currentSpecSheet) return;
    const hasRenderedSheet = !!document.getElementById("req_quantity");
    specStateBySheet[currentSpecSheet] = {{
        requirement: hasRenderedSheet ? collectSheetRequirement() : (savedSpecRequirement || {{ device_spec_sheet: currentSpecSheet }}),
        quantity: hasRenderedSheet ? currentDeviceQuantity() : (savedSpecQuantity || 1),
        result: currentSpecsResult || null
    }};
}}

function manualRowsText() {{
    return manualRows
        .filter(row => String(row.model || "").trim())
        .map(row => `${{row.model}}, ${{Number(row.quantity || 1)}}`)
        .join("\\n");
}}

function ensureManualRowCount() {{
    while (manualRows.length < MIN_MANUAL_ROWS) {{
        manualRows.push({{ model: "", quantity: "", price: 0 }});
    }}
}}

function renderManualSheet() {{
    ensureManualRowCount();
    const body = document.getElementById("manualSheetBody");
    const total = manualRows.reduce((sum, row) => sum + Number(row.quantity || 0) * Number(row.price || 0), 0);
    document.getElementById("manualTotalCell").textContent = money(total);
    body.innerHTML = manualRows.map((row, index) => `
        <tr>
            <td><input id="manual_model_${{index}}" value="${{esc(row.model || "")}}" oninput="updateManualRow(${{index}}, 'model', this.value)" onkeydown="manualCellKeydown(event, ${{index}}, 'model')" onpaste="pasteManualRows(event, ${{index}})" /></td>
            <td><input id="manual_qty_${{index}}" type="number" min="1" value="${{esc(row.quantity || "")}}" oninput="updateManualRow(${{index}}, 'quantity', this.value)" onkeydown="manualCellKeydown(event, ${{index}}, 'quantity')" onpaste="pasteManualRows(event, ${{index}})" /></td>
            <td class="price-cell">${{money(row.price || 0)}}</td>
            <td class="price-cell"></td>
        </tr>
    `).join("");
}}

function updateManualRow(index, key, value) {{
    if (!manualRows[index]) return;
    manualRows[index][key] = key === "quantity" ? value : value.trim();
    if (key === "model") manualRows[index].price = 0;
    updateManualTotal();
    scheduleManualPriceRefresh();
    scheduleModelStateSave();
}}

function updateManualTotal() {{
    const total = manualRows.reduce((sum, row) => sum + Number(row.quantity || 0) * Number(row.price || 0), 0);
    document.getElementById("manualTotalCell").textContent = money(total);
}}

function manualCellKeydown(event, index, key) {{
    if (event.key !== "Enter") return;
    event.preventDefault();
    const nextIndex = index + 1;
    while (manualRows.length <= nextIndex) {{
        manualRows.push({{ model: "", quantity: "", price: 0 }});
    }}
    renderManualSheet();
    scheduleModelStateSave();
    requestAnimationFrame(() => {{
        const next = document.getElementById(key === "quantity" ? `manual_qty_${{nextIndex}}` : `manual_model_${{nextIndex}}`);
        if (next) next.focus();
    }});
}}

function pasteManualRows(event, startIndex) {{
    const text = event.clipboardData ? event.clipboardData.getData("text") : "";
    if (!text || (!text.includes("\\n") && !text.includes("\\t"))) return;

    event.preventDefault();
    const rows = text
        .split(/\\r?\\n/)
        .map(line => line.trim())
        .filter(Boolean)
        .map(line => line.split(/\\t|,/).map(part => part.trim()));

    rows.forEach((cols, offset) => {{
        const targetIndex = startIndex + offset;
        while (manualRows.length <= targetIndex) {{
            manualRows.push({{ model: "", quantity: "", price: 0 }});
        }}
        manualRows[targetIndex] = {{
            model: cols[0] || "",
            quantity: cols[1] || 1,
            price: 0
        }};
    }});
    renderManualSheet();
    scheduleManualPriceRefresh();
    scheduleModelStateSave();
}}

function scheduleManualPriceRefresh() {{
    clearTimeout(manualPriceTimer);
    manualPriceTimer = setTimeout(refreshManualPrices, 450);
}}

async function refreshManualPrices() {{
    const text = manualRowsText();
    if (!text) {{
        updateManualTotal();
        return;
    }}

    try {{
        const res = await fetch("/api/device-list-quote", {{
            method: "POST",
            headers: {{ "Content-Type": "application/json" }},
            body: JSON.stringify({{ text }})
        }});
        if (!res.ok) return;

        const data = await res.json();
        const quoteLines = (((data || {{}}).quote || {{}}).quote_lines || []);
        const priceByModel = new Map();
        quoteLines.forEach(line => {{
            const model = String(line.item_type || (((line.selected || {{}}).opt1 || {{}}).model || "")).trim().toUpperCase();
            const selected = ((line.selected || {{}}).opt1 || {{}});
            if (model) priceByModel.set(model, Number(selected.price || 0));
            if (selected.model) priceByModel.set(String(selected.model).trim().toUpperCase(), Number(selected.price || 0));
        }});

        manualRows.forEach(row => {{
            const key = String(row.model || "").trim().toUpperCase();
            if (key && priceByModel.has(key)) row.price = priceByModel.get(key);
        }});
        renderManualSheet();
        saveModelState();
    }} catch (e) {{}}
}}

function clearManualSheet() {{
    manualRows = Array.from({{ length: MIN_MANUAL_ROWS }}, () => ({{ model: "", quantity: "", price: 0 }}));
    currentQuote = null;
    document.getElementById("summaryBlock").innerHTML = "";
    document.getElementById("quoteBlock").innerHTML = `<div class="empty-state">Chưa có bảng báo giá.</div>`;
    renderManualSheet();
    saveModelState();
}}

function manualRequirementPayload() {{
    return {{
        quantity: currentDeviceQuantity(),
        requirement: collectSheetRequirement()
    }};
}}

function normalizeQuote(quoteData) {{
    if (quoteData) quoteData.price_version = MODEL_QUOTE_PRICE_VERSION;
    const lines = (((quoteData || {{}}).quote || {{}}).quote_lines || []);
    lines.forEach(line => {{
        if (!line.selected) line.selected = {{}};
        if (!line.amount) line.amount = {{}};
        ["opt1", "opt2", "opt3"].forEach(opt => {{
            const choices = line.options && line.options[opt] ? line.options[opt] : [];
            if (!line.selected[opt] && choices.length) line.selected[opt] = choices[0];
            line.amount[opt] = selectedAmount(line, opt);
        }});
    }});
    return quoteData;
}}

function totalsFor(lines) {{
    const totals = {{ opt1: 0, opt2: 0, opt3: 0 }};
    lines.forEach(line => {{
        ["opt1", "opt2", "opt3"].forEach(opt => {{
            totals[opt] += selectedAmount(line, opt);
        }});
    }});
    return totals;
}}

function getSelectedIndex(line, opt) {{
    const choices = line.options && line.options[opt] ? line.options[opt] : [];
    const selected = line.selected && line.selected[opt] ? line.selected[opt] : null;
    const idx = choices.findIndex(c => selected && c.model === selected.model && Number(c.price || 0) === Number(selected.price || 0));
    return idx >= 0 ? idx : 0;
}}

function renderOptionSelect(lineIndex, opt, line) {{
    const choices = line.options && line.options[opt] ? line.options[opt] : [];
    if (!choices.length) return `<span class="small">Chưa có model phù hợp</span>`;
    const selectedIndex = getSelectedIndex(line, opt);
    let html = `<select onchange="changeModel(${{lineIndex}}, '${{opt}}', this.value)">`;
    choices.forEach((choice, index) => {{
        html += `<option value="${{index}}" ${{index === selectedIndex ? "selected" : ""}}>${{esc(choice.model || "")}}</option>`;
    }});
    html += `</select><div class="price-note">${{money((line.selected[opt] || {{}}).price || 0)}} / ${{
        money(selectedAmount(line, opt))
    }}</div>`;
    return html;
}}

function specsValue(device, label) {{
    if (!device || !device.specs) return "";
    const alias = SPEC_LABEL_ALIASES[label] || label;
    const value = device.specs[label] ?? device.specs[alias] ?? "";
    return value === null || value === undefined ? "" : value;
}}

function renderSpecInputSheet(data = null) {{
    const devices = data ? (data.devices || []) : [];
    const best = data ? (data.best || devices[0] || null) : null;
    const fields = SPEC_SHEET_FIELDS[currentSpecSheet] || [];
    const requirement = data ? (data.requirement || {{}}) : (savedSpecRequirement || collectSheetRequirement());
    const quantity = data ? Number(data.quantity || 1) : (savedSpecQuantity || currentDeviceQuantity());

    document.getElementById("specInputBlock").innerHTML = `
        <div class="quote-table-wrap spec-sheet-wrap">
            <table class="spec-result-table">
                <colgroup>
                    <col style="width:300px" />
                    <col style="width:150px" />
                    <col style="width:110px" />
                    <col style="width:190px" />
                </colgroup>
                <thead>
                    <tr>
                        <th class="cyan-head" colspan="2">Nhập yêu cầu</th>
                        <th class="cyan-head">Số lượng</th>
                        <th class="cyan-head best-col">Thiết bị dự kiến</th>
                        <th class="option-head" colspan="${{Math.max(1, alternatives.length)}}">Các option khác có thể xem xét</th>
                    </tr>
                    <tr>
                        <th class="section-head left-block param-cell">Thông số</th>
                        <th class="yellow-cell left-block">Yêu cầu</th>
                        <th class="yellow-cell left-block"><input class="sheet-input" id="req_quantity" value="${{esc(quantity || 1)}}" oninput="scheduleModelStateSave()" /></th>
                        <th class="section-head best-col">${{esc((best || {{}}).model || "")}}</th>
                        <th class="freeze-gap"></th>
                        <th class="blank-gap"></th>
                        ${{alternatives.map(device => `<th>${{esc(device.model || "")}}</th>`).join("") || `<th></th>`}}
                    </tr>
                </thead>
                <tbody>
                    ${{fields.map(([label, key]) => `
                        <tr>
                            <td class="left-block param-cell">${{esc(label)}}</td>
                            <td class="yellow-cell left-block">${{fieldInputHtml(key, requestValue(requirement, key))}}</td>
                            <td class="yellow-cell left-block"></td>
                            <td class="best-col">${{esc(specsValue(best, label))}}</td>
                            <td class="freeze-gap"></td>
                            <td class="blank-gap"></td>
                            ${{alternatives.map(device => `<td>${{esc(specsValue(device, label))}}</td>`).join("") || "<td></td>"}}
                        </tr>
                    `).join("")}}
                    <tr>
                        <td class="left-block"></td>
                        <td class="yellow-cell left-block"></td>
                        <td class="yellow-cell left-block"></td>
                        <td class="best-col"></td>
                        <td class="freeze-gap"></td>
                        <td class="blank-gap"></td>
                        ${{alternatives.map(() => `<td></td>`).join("") || "<td></td>"}}
                    </tr>
                    <tr>
                        <td class="param-cell">Đơn giá</td>
                        <td></td>
                        <td></td>
                        <td class="best-col">${{best ? money(best.price || 0) : ""}}</td>
                        <td class="freeze-gap"></td>
                        <td class="option-label">Đơn giá</td>
                        ${{alternatives.map(device => `<td>${{money(device.price || 0)}}</td>`).join("") || "<td></td>"}}
                    </tr>
                    <tr>
                        <td class="param-cell"><strong>Thành tiền</strong></td>
                        <td></td>
                        <td></td>
                        <td class="best-col"><strong>${{best ? money((best.price || 0) * Number(quantity || 1)) : ""}}</strong></td>
                        <td class="freeze-gap"></td>
                        <td class="option-label"><strong>Thành tiền</strong></td>
                        ${{alternatives.map(device => `<td>${{money((device.price || 0) * Number(quantity || 1))}}</td>`).join("") || "<td></td>"}}
                    </tr>
                    <tr>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td class="best-col">${{best ? `<button class="btn btn-primary" type="button" onclick="useSpecsModelByIndex(0)">Chọn model</button>` : ""}}</td>
                        <td class="freeze-gap"></td>
                        <td></td>
                        ${{alternatives.map((_device, index) => `<td><button class="btn btn-secondary" type="button" onclick="useSpecsModelByIndex(${{index + 1}})">Chọn</button></td>`).join("") || "<td></td>"}}
                    </tr>
                </tbody>
            </table>
        </div>
    `;
}}

function renderSpecInputSheet(data = null) {{
    const devices = data ? (data.devices || []) : [];
    const best = data ? (data.best || devices[0] || null) : null;
    const fields = SPEC_SHEET_FIELDS[currentSpecSheet] || [];
    const requirement = data ? (data.requirement || {{}}) : (savedSpecRequirement || collectSheetRequirement());
    const quantity = data ? Number(data.quantity || 1) : (savedSpecQuantity || currentDeviceQuantity());

    document.getElementById("specInputBlock").innerHTML = `
        <div class="quote-table-wrap spec-sheet-wrap">
            <table class="spec-result-table">
                <colgroup>
                    <col style="width:300px" />
                    <col style="width:150px" />
                    <col style="width:110px" />
                    <col style="width:190px" />
                </colgroup>
                <thead>
                    <tr>
                        <th class="cyan-head" colspan="2">Nháº­p yÃªu cáº§u</th>
                        <th class="cyan-head">Sá»‘ lÆ°á»£ng</th>
                        <th class="cyan-head best-col">Thiáº¿t bá»‹ dá»± kiáº¿n</th>
                    </tr>
                    <tr>
                        <th class="section-head left-block param-cell">ThÃ´ng sá»‘</th>
                        <th class="yellow-cell left-block">YÃªu cáº§u</th>
                        <th class="yellow-cell left-block"><input class="sheet-input" id="req_quantity" value="${{esc(quantity || 1)}}" oninput="scheduleModelStateSave()" /></th>
                        <th class="section-head best-col">${{esc((best || {{}}).model || "")}}</th>
                    </tr>
                </thead>
                <tbody>
                    ${{fields.map(([label, key]) => `
                        <tr>
                            <td class="left-block param-cell">${{esc(label)}}</td>
                            <td class="yellow-cell left-block">${{fieldInputHtml(key, requestValue(requirement, key))}}</td>
                            <td class="yellow-cell left-block"></td>
                            <td class="best-col">${{esc(specsValue(best, label))}}</td>
                        </tr>
                    `).join("")}}
                    <tr>
                        <td class="left-block"></td>
                        <td class="yellow-cell left-block"></td>
                        <td class="yellow-cell left-block"></td>
                        <td class="best-col"></td>
                    </tr>
                    <tr>
                        <td class="param-cell">ÄÆ¡n giÃ¡</td>
                        <td></td>
                        <td></td>
                        <td class="best-col">${{best ? money(best.price || 0) : ""}}</td>
                    </tr>
                    <tr>
                        <td class="param-cell"><strong>ThÃ nh tiá»n</strong></td>
                        <td></td>
                        <td></td>
                        <td class="best-col"><strong>${{best ? money((best.price || 0) * Number(quantity || 1)) : ""}}</strong></td>
                    </tr>
                </tbody>
            </table>
        </div>
    `;
}}

function renderSpecsQuoteTable(data) {{
    const devices = data && data.devices ? data.devices : [];
    const quantity = Number((data || {{}}).quantity || 1);
    if (!devices.length) return "";

    return `
        <div class="quote-summary">
            <div class="quote-metric"><div class="label">Thiáº¿t bá»‹ Ä‘Ã¡p á»©ng</div><div class="value">${{devices.length}}</div></div>
            <div class="quote-metric"><div class="label">Sá»‘ lÆ°á»£ng</div><div class="value">${{quantity}}</div></div>
            <div class="quote-metric"><div class="label">Model Ä‘á» xuáº¥t</div><div class="value">${{esc(devices[0].model || "")}}</div></div>
        </div>
        <div class="quote-table-wrap">
            <table class="quote-table">
                <thead>
                    <tr>
                        <th>Model</th>
                        <th>Sheet</th>
                        <th>Class</th>
                        <th>ÄÆ¡n giÃ¡</th>
                        <th>Sá»‘ lÆ°á»£ng</th>
                        <th>ThÃ nh tiá»n</th>
                    </tr>
                </thead>
                <tbody>
                    ${{devices.map((device) => `
                        <tr>
                            <td><strong>${{esc(device.model || "")}}</strong></td>
                            <td>${{esc(device.sheet || "")}}</td>
                            <td>${{esc(device.class || "")}}</td>
                            <td>${{money(device.price || 0)}}</td>
                            <td>${{quantity}}</td>
                            <td>${{money((device.price || 0) * quantity)}}</td>
                            <td><button class="btn ${{index === 0 ? "btn-primary" : "btn-secondary"}}" type="button" onclick="useSpecsModelByIndex(${{index}})">Chá»n model</button></td>
                        </tr>
                    `).join("")}}
                </tbody>
            </table>
        </div>
    `;
}}

function renderSpecsQuoteTable(data) {{
    const devices = data && data.devices ? data.devices : [];
    const quantity = Number((data || {{}}).quantity || 1);
    if (!devices.length) return "";

    return `
        <div class="quote-summary">
            <div class="quote-metric"><div class="label">Thiáº¿t bá»‹ Ä‘Ã¡p á»©ng</div><div class="value">${{devices.length}}</div></div>
            <div class="quote-metric"><div class="label">Sá»‘ lÆ°á»£ng</div><div class="value">${{quantity}}</div></div>
            <div class="quote-metric"><div class="label">Model Ä‘á» xuáº¥t</div><div class="value">${{esc(devices[0].model || "")}}</div></div>
        </div>
        <div class="quote-table-wrap">
            <table class="quote-table">
                <thead>
                    <tr>
                        <th>Model</th>
                        <th>Sheet</th>
                        <th>Class</th>
                        <th>ÄÆ¡n giÃ¡</th>
                        <th>Sá»‘ lÆ°á»£ng</th>
                        <th>ThÃ nh tiá»n</th>
                    </tr>
                </thead>
                <tbody>
                    ${{devices.map((device) => `
                        <tr>
                            <td><strong>${{esc(device.model || "")}}</strong></td>
                            <td>${{esc(device.sheet || "")}}</td>
                            <td>${{esc(device.class || "")}}</td>
                            <td>${{money(device.price || 0)}}</td>
                            <td>${{quantity}}</td>
                            <td>${{money((device.price || 0) * quantity)}}</td>
                        </tr>
                    `).join("")}}
                </tbody>
            </table>
        </div>
    `;
}}

function renderSpecInputSheet(data = null) {{
    const devices = data ? (data.devices || []) : [];
    const best = data ? (data.best || devices[0] || null) : null;
    const fields = SPEC_SHEET_FIELDS[currentSpecSheet] || [];
    const requirement = data ? (data.requirement || {{}}) : (savedSpecRequirement || collectSheetRequirement());
    const quantity = data ? Number(data.quantity || 1) : (savedSpecQuantity || currentDeviceQuantity());

    document.getElementById("specInputBlock").innerHTML = `
        <div class="quote-table-wrap spec-sheet-wrap">
            <table class="spec-result-table">
                <colgroup>
                    <col style="width:300px" />
                    <col style="width:150px" />
                    <col style="width:110px" />
                    <col style="width:190px" />
                </colgroup>
                <thead>
                    <tr>
                        <th class="cyan-head" colspan="2">Nhập yêu cầu</th>
                        <th class="cyan-head">Số lượng</th>
                        <th class="cyan-head best-col">Thiết bị dự kiến</th>
                    </tr>
                    <tr>
                        <th class="section-head left-block param-cell">Thông số</th>
                        <th class="yellow-cell left-block">Yêu cầu</th>
                        <th class="yellow-cell left-block"><input class="sheet-input" id="req_quantity" value="${{esc(quantity || 1)}}" oninput="scheduleModelStateSave()" /></th>
                        <th class="section-head best-col">${{esc((best || {{}}).model || "")}}</th>
                    </tr>
                </thead>
                <tbody>
                    ${{fields.map(([label, key]) => `
                        <tr>
                            <td class="left-block param-cell">${{esc(label)}}</td>
                            <td class="yellow-cell left-block">${{fieldInputHtml(key, requestValue(requirement, key))}}</td>
                            <td class="yellow-cell left-block"></td>
                            <td class="best-col">${{esc(specsValue(best, label))}}</td>
                        </tr>
                    `).join("")}}
                    <tr>
                        <td class="left-block"></td>
                        <td class="yellow-cell left-block"></td>
                        <td class="yellow-cell left-block"></td>
                        <td class="best-col"></td>
                    </tr>
                    <tr>
                        <td class="param-cell">Đơn giá</td>
                        <td></td>
                        <td></td>
                        <td class="best-col">${{best ? money(best.price || 0) : ""}}</td>
                    </tr>
                    <tr>
                        <td class="param-cell"><strong>Thành tiền</strong></td>
                        <td></td>
                        <td></td>
                        <td class="best-col"><strong>${{best ? money((best.price || 0) * Number(quantity || 1)) : ""}}</strong></td>
                    </tr>
                </tbody>
            </table>
        </div>
    `;
}}

function renderSpecsQuoteTable(data) {{
    const devices = data && data.devices ? data.devices : [];
    const quantity = Number((data || {{}}).quantity || 1);
    if (!devices.length) return "";

    return `
        <div class="quote-summary">
            <div class="quote-metric"><div class="label">Thiết bị đáp ứng</div><div class="value">${{devices.length}}</div></div>
            <div class="quote-metric"><div class="label">Số lượng</div><div class="value">${{quantity}}</div></div>
            <div class="quote-metric"><div class="label">Model đề xuất</div><div class="value">${{esc(devices[0].model || "")}}</div></div>
        </div>
        <div class="quote-table-wrap">
            <table class="quote-table">
                <thead>
                    <tr>
                        <th>Model</th>
                        <th>Sheet</th>
                        <th>Class</th>
                        <th>Đơn giá</th>
                        <th>Số lượng</th>
                        <th>Thành tiền</th>
                    </tr>
                </thead>
                <tbody>
                    ${{devices.map((device) => `
                        <tr>
                            <td><strong>${{esc(device.model || "")}}</strong></td>
                            <td>${{esc(device.sheet || "")}}</td>
                            <td>${{esc(device.class || "")}}</td>
                            <td>${{money(device.price || 0)}}</td>
                            <td>${{quantity}}</td>
                            <td>${{money((device.price || 0) * quantity)}}</td>
                        </tr>
                    `).join("")}}
                </tbody>
            </table>
        </div>
    `;
}}

function requestValue(requirement, key) {{
    const value = requirement && requirement[key] !== undefined ? requirement[key] : "";
    return value === null || value === undefined || value === 0 ? "" : value;
}}

function renderSpecsResult(data) {{
    currentSpecsResult = data;
    savedSpecRequirement = data.requirement || collectSheetRequirement();
    savedSpecQuantity = Number(data.quantity || currentDeviceQuantity());
    specStateBySheet[currentSpecSheet] = {{
        requirement: savedSpecRequirement,
        quantity: savedSpecQuantity,
        result: currentSpecsResult
    }};
    currentQuote = null;
    localStorage.removeItem("modelQuoteData");
    document.getElementById("summaryBlock").innerHTML = "";
    document.getElementById("quoteBlock").innerHTML = renderSpecsQuoteTable(data);
    renderSpecInputSheet(data);

    if (!(data.devices || []).length) {{
        const message = document.getElementById("manualRecommendMessage");
        message.className = "error-box";
        message.style.display = "block";
        message.textContent = "Không có thiết bị đáp ứng yêu cầu.";
    }}
    return;

    const devices = data.devices || [];
    const best = data.best || devices[0] || null;
    const alternatives = devices.slice(1, 4);
    const fields = SPEC_SHEET_FIELDS[data.sheet] || [];
    const requirement = data.requirement || {{}};
    document.getElementById("summaryBlock").innerHTML = "";

    if (!devices.length) {{
        document.getElementById("quoteBlock").innerHTML = `<div class="empty-state">Không có thiết bị đáp ứng yêu cầu.</div>`;
        return;
    }}

    document.getElementById("quoteBlock").innerHTML = `
        <div class="quote-table-wrap spec-sheet-wrap">
            <table class="spec-result-table">
                <colgroup>
                    <col style="width:380px" />
                    <col style="width:150px" />
                    <col style="width:140px" />
                    <col style="width:255px" />
                    <col style="width:8px" />
                    <col style="width:150px" />
                    ${{alternatives.map(() => `<col style="width:200px" />`).join("") || `<col style="width:200px" />`}}
                </colgroup>
                <thead>
                    <tr>
                        <th class="cyan-head" colspan="2">Nhập yêu cầu</th>
                        <th class="cyan-head">Số lượng</th>
                        <th class="cyan-head best-col">Thiết bị dự kiến</th>
                        <th class="freeze-gap"></th>
                        <th class="blank-gap"></th>
                        <th class="option-head" colspan="${{Math.max(1, alternatives.length)}}">Các option khác có thể xem xét</th>
                    </tr>
                    <tr>
                        <th class="section-head left-block param-cell">Thông số</th>
                        <th class="yellow-cell left-block">Yêu cầu</th>
                        <th class="yellow-cell left-block">${{esc(data.quantity || 1)}}</th>
                        <th class="section-head best-col">${{esc((best || {{}}).model || "")}}</th>
                        <th class="freeze-gap"></th>
                        <th class="blank-gap"></th>
                        ${{alternatives.map(device => `<th>${{esc(device.model || "")}}</th>`).join("") || `<th></th>`}}
                    </tr>
                </thead>
                <tbody>
                    ${{fields.map(([label, key]) => `
                        <tr>
                            <td class="left-block param-cell">${{esc(label)}}</td>
                            <td class="yellow-cell left-block">${{esc(requestValue(requirement, key))}}</td>
                            <td class="yellow-cell left-block"></td>
                            <td class="best-col">${{esc(specsValue(best, label))}}</td>
                            <td class="freeze-gap"></td>
                            <td class="blank-gap"></td>
                            ${{alternatives.map(device => `<td>${{esc(specsValue(device, label))}}</td>`).join("") || "<td></td>"}}
                        </tr>
                    `).join("")}}
                    <tr>
                        <td class="left-block"></td>
                        <td class="yellow-cell left-block"></td>
                        <td class="yellow-cell left-block"></td>
                        <td class="best-col"></td>
                        <td class="freeze-gap"></td>
                        <td class="blank-gap"></td>
                        ${{alternatives.map(() => `<td></td>`).join("") || "<td></td>"}}
                    </tr>
                    <tr>
                        <td class="param-cell">Đơn giá</td>
                        <td></td>
                        <td></td>
                        <td class="best-col">${{money((best || {{}}).price || 0)}}</td>
                        <td class="freeze-gap"></td>
                        <td class="option-label">Đơn giá</td>
                        ${{alternatives.map(device => `<td>${{money(device.price || 0)}}</td>`).join("") || "<td></td>"}}
                    </tr>
                    <tr>
                        <td class="param-cell"><strong>Thành tiền</strong></td>
                        <td></td>
                        <td></td>
                        <td class="best-col"><strong>${{money(((best || {{}}).price || 0) * Number(data.quantity || 1))}}</strong></td>
                        <td class="freeze-gap"></td>
                        <td class="option-label"><strong>Thành tiền</strong></td>
                        ${{alternatives.map(device => `<td>${{money((device.price || 0) * Number(data.quantity || 1))}}</td>`).join("") || "<td></td>"}}
                    </tr>
                    <tr>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td class="best-col"><button class="btn btn-primary" type="button" onclick="useSpecsModelByIndex(0)">Chọn model</button></td>
                        <td class="freeze-gap"></td>
                        <td></td>
                        ${{alternatives.map((_device, index) => `<td><button class="btn btn-secondary" type="button" onclick="useSpecsModelByIndex(${{index + 1}})">Chọn</button></td>`).join("") || "<td></td>"}}
                    </tr>
                </tbody>
            </table>
        </div>
    `;
}}

function renderQuote() {{
    if (!currentQuote) {{
        document.getElementById("summaryBlock").innerHTML = "";
        document.getElementById("quoteBlock").innerHTML = `<div class="empty-state">Chưa có bảng báo giá.</div>`;
        return;
    }}

    normalizeQuote(currentQuote);
    localStorage.setItem("modelQuoteData", JSON.stringify(currentQuote));

    const lines = currentQuote.quote.quote_lines || [];
    const total = lines.reduce((sum, line) => sum + selectedAmount(line, "opt1"), 0);
    document.getElementById("summaryBlock").innerHTML = `
        <div class="quote-summary">
            <div class="quote-metric"><div class="label">Tổng báo giá</div><div class="value">${{money(total)}}</div></div>
        </div>
    `;

    document.getElementById("quoteBlock").innerHTML = `
        <div class="quote-table-wrap">
            <table class="quote-table">
                <thead>
                    <tr>
                        <th>Nhóm</th>
                        <th>Hạng mục</th>
                        <th>SL</th>
                        <th>Model</th>
                        <th>Đơn giá</th>
                        <th>Thành tiền</th>
                    </tr>
                </thead>
                <tbody>
                    ${{lines.map((line, index) => `
                        <tr>
                            <td>${{esc(line.group || "")}}</td>
                            <td>${{esc(line.item_type || "")}}</td>
                            <td>${{esc(line.quantity || 0)}}</td>
                            <td>${{esc(((line.selected || {{}}).opt1 || {{}}).model || "")}}</td>
                            <td>${{money((((line.selected || {{}}).opt1 || {{}}).price || 0))}}</td>
                            <td>${{money(selectedAmount(line, "opt1"))}}</td>
                        </tr>
                    `).join("")}}
                </tbody>
            </table>
        </div>
    `;
}}

function changeModel(lineIndex, opt, choiceIndex) {{
    const line = currentQuote.quote.quote_lines[lineIndex];
    const choices = line.options && line.options[opt] ? line.options[opt] : [];
    const choice = choices[Number(choiceIndex)];
    if (!choice) return;
    line.selected[opt] = choice;
    line.amount[opt] = selectedAmount(line, opt);
    renderQuote();
}}

async function recommendManualDevice() {{
    const message = document.getElementById("manualRecommendMessage");
    message.style.display = "block";
    message.textContent = "Đang tìm thiết bị...";

    const payload = manualRequirementPayload();
    const res = await fetch("/api/recommend-device-specs", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{
            sheet: currentSpecSheet,
            quantity: payload.quantity,
            requirement: payload.requirement
        }})
    }});

    if (!res.ok) {{
        message.className = "error-box";
        message.style.display = "block";
        message.textContent = "Không tìm được thiết bị đáp ứng.";
        return;
    }}

    const data = await res.json();
    message.className = "success-box";
    message.style.display = "block";
    message.textContent = "Đã tìm thiết bị đáp ứng theo Device Specs.";
    renderSpecsResult(data);
    saveModelState();
}}

async function buildQuoteFromDeviceList(openBom) {{
    const message = document.getElementById("manualListMessage");
    message.style.display = "block";
    message.textContent = "Đang xử lý danh sách thiết bị...";

    const res = await fetch("/api/device-list-quote", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{ text: manualRowsText() }})
    }});

    if (!res.ok) {{
        message.className = "error-box";
        message.style.display = "block";
        message.textContent = "Không xử lý được danh sách thiết bị.";
        return;
    }}

    const data = await res.json();
    currentQuote = data;
    const quoteLines = (((data || {{}}).quote || {{}}).quote_lines || []);
    manualRows = quoteLines.map(line => ({{
        model: line.item_type || (((line.selected || {{}}).opt1 || {{}}).model || ""),
        quantity: line.quantity || 1,
        price: (((line.selected || {{}}).opt1 || {{}}).price || 0)
    }}));
    ensureManualRowCount();
    message.className = data.warnings && data.warnings.length ? "error-box" : "success-box";
    message.style.display = "block";
    message.textContent = data.warnings && data.warnings.length ? data.warnings.join("\\n") : "Đã tổng hợp báo giá.";
    renderQuote();
    renderManualSheet();
    saveModelState();

    if (openBom) {{
        localStorage.setItem("modelBomQuoteData", JSON.stringify(currentQuote));
        window.location.href = "/model-bom";
    }}
}}

async function exportManualBom() {{
    await buildQuoteFromDeviceList(false);
    if (currentQuote) {{
        localStorage.setItem("modelBomQuoteData", JSON.stringify(currentQuote));
        window.location.href = "/model-bom";
    }}
}}

function useSpecsModelByIndex(index) {{
    const devices = currentSpecsResult && currentSpecsResult.devices ? currentSpecsResult.devices : [];
    const device = devices[index];
    if (!device || !device.model) return;
    manualRows = [{{
        model: device.model,
        quantity: Number(currentSpecsResult.quantity || currentDeviceQuantity() || 1),
        price: Number(device.price || 0)
    }}];
    ensureManualRowCount();
    renderManualSheet();
    setModelTab("list");
}}

function saveCurrentQuote() {{
    if (!currentQuote) return;
    normalizeQuote(currentQuote);
    localStorage.setItem("modelQuoteData", JSON.stringify(currentQuote));
    renderQuote();
}}

function scheduleModelStateSave() {{
    if (restoringModelState) return;
    clearTimeout(stateSaveTimer);
    stateSaveTimer = setTimeout(saveModelState, 120);
}}

function saveModelState() {{
    if (restoringModelState) return;
    captureCurrentSpecState();
    savedSpecRequirement = collectSheetRequirement();
    savedSpecQuantity = currentDeviceQuantity();
    const state = {{
        active_tab: activeModelTab,
        spec_sheet: currentSpecSheet,
        spec_states: specStateBySheet,
        manual_rows: manualRows,
        current_quote: currentQuote
    }};
    localStorage.setItem(MODEL_STATE_KEY, JSON.stringify(state));
}}

function readModelState() {{
    try {{
        return JSON.parse(localStorage.getItem(MODEL_STATE_KEY) || "null") || null;
    }} catch (e) {{
        return null;
    }}
}}

function restoreModelState() {{
    const state = readModelState();
    if (!state) return false;
    restoringModelState = true;
    activeModelTab = state.active_tab || "recommend";
    currentSpecSheet = state.spec_sheet || "SwitchCampus";
    specStateBySheet = state.spec_states || {{}};
    if (!state.spec_states) {{
        specStateBySheet[currentSpecSheet] = {{
            requirement: state.spec_requirement || null,
            quantity: Number(state.spec_quantity || 1),
            result: state.specs_result || null
        }};
    }}
    const sheetState = specStateBySheet[currentSpecSheet] || {{}};
    savedSpecRequirement = sheetState.requirement || null;
    savedSpecQuantity = Number(sheetState.quantity || 1);
    currentSpecsResult = sheetState.result || null;
    currentQuote = state.current_quote && state.current_quote.price_version === MODEL_QUOTE_PRICE_VERSION
        ? state.current_quote
        : null;
    if (Array.isArray(state.manual_rows) && state.manual_rows.length) {{
        manualRows = state.manual_rows;
    }}
    setSpecBlock(currentSpecSheet);
    renderManualSheet();
    setModelTab(activeModelTab);
    restoringModelState = false;
    return true;
}}

window.addEventListener("load", () => {{
    if (restoreModelState()) {{
        return;
    }}

    setSpecBlock(currentSpecSheet);
    renderManualSheet();
    const saved = localStorage.getItem("modelQuoteData");
    if (saved) {{
        try {{
            const parsed = JSON.parse(saved);
            if (parsed.price_version === MODEL_QUOTE_PRICE_VERSION && (((parsed.quote || {{}}).quote_lines || []).length)) {{
                currentQuote = parsed;
                renderQuote();
            }}
        }} catch (e) {{}}
    }} else {{
        renderQuote();
    }}
    saveModelState();
}});
</script>
</body>
</html>
    """
