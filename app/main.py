from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, List

from app.requirement_engine import build_requirements
from app.recommendation_engine import recommend_all
from app.quote_engine import build_quote
from app.catalog_engine import debug_catalog_summary
from app.bom_engine import build_bom, build_bom_excel


app = FastAPI(title="Network Quotation Web")


class SurveyPayload(BaseModel):
    hq: Dict[str, Any]
    buildings: List[Dict[str, Any]]
    server_farm: Dict[str, Any]
    wan_sites: List[Dict[str, Any]]


class BomPayload(BaseModel):
    quote_data: Dict[str, Any]


def payload_to_dict(payload: SurveyPayload) -> Dict[str, Any]:
    if hasattr(payload, "model_dump"):
        return payload.model_dump()
    return payload.dict()


BASE_STYLE = """
<style>
    * { box-sizing: border-box; }
    body {
        font-family: Arial, sans-serif;
        margin: 0;
        background: #f4f7fb;
        color: #0f172a;
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
    }
    .step.active {
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
        font-family: Consolas, monospace;
        font-size: 12px;
    }
</style>
"""


@app.get("/")
def root():
    return RedirectResponse("/survey")


@app.get("/survey", response_class=HTMLResponse)
def survey_page():
    return f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="utf-8" />
    <title>Survey - Network Quotation Tool</title>
    {BASE_STYLE}
</head>
<body>
<div class="container">
    <h1>Network Quotation Tool</h1>
    <div class="subtitle">Trang 1: Nhập thông tin khảo sát</div>

    <div class="stepbar">
        <div class="step active">1. Nhập khảo sát</div>
        <div class="step">2. Kết quả tính toán</div>
        <div class="step">3. Chọn model & báo giá</div>
    </div>

    <div class="card">
        <div class="section-title">1. Campus HQ</div>
        <div class="grid-2">
            <div>
                <label>Số user HQ</label>
                <input type="number" id="hq_users" value="1000" />
            </div>
            <div>
                <label>Diện tích outdoor cần phủ WiFi (m²)</label>
                <input type="number" id="outdoor_area" value="5000" />
            </div>
        </div>

        <div class="checkbox-row">
            <input type="checkbox" id="hq_outdoor_wifi" checked />
            <span>Có WiFi outdoor</span>
        </div>

        <div class="section-title">2. Chi tiết mỗi tòa nhà</div>
        <div id="buildings_container"></div>
        <button class="btn btn-secondary" type="button" onclick="addBuilding()">+ Thêm tòa nhà</button>

        <div class="section-title">3. Chi tiết Server Farm</div>
        <div class="checkbox-row">
            <input type="checkbox" id="sf_enabled" checked onchange="toggleServerFarm()" />
            <span>Có Server Farm</span>
        </div>

        <div id="server_farm_fields">
            <div class="grid-2">
                <div>
                    <label>Số rack</label>
                    <input type="number" id="sf_racks" value="2" />
                </div>
                <div>
                    <label>Số server / rack</label>
                    <input type="number" id="sf_servers_per_rack" value="10" />
                </div>
            </div>

            <div class="grid-2" style="margin-top:12px;">
                <div>
                    <label>Số cổng 100GE / server</label>
                    <input type="number" id="sf_100g" value="0" />
                </div>
                <div>
                    <label>Số cổng 10GE SFP / server</label>
                    <input type="number" id="sf_10g_sfp" value="0" />
                </div>
                <div>
                    <label>Số cổng 10GE RJ45 / server</label>
                    <input type="number" id="sf_10g_rj45" value="1" />
                </div>
                <div>
                    <label>Số cổng 1GE SFP / server</label>
                    <input type="number" id="sf_1g_sfp" value="1" />
                </div>
                <div>
                    <label>Số cổng 1GE RJ45 / server</label>
                    <input type="number" id="sf_1g_rj45" value="2" />
                </div>
            </div>
        </div>

        <div class="section-title">4. Chi tiết các điểm WAN</div>
        <div id="wan_container"></div>
        <button class="btn btn-secondary" type="button" onclick="addWan()">+ Thêm WAN site</button>

        <div class="actions">
            <button class="btn btn-primary" type="button" onclick="generateCalculation()">Tạo kết quả tính toán</button>
            <button class="btn btn-secondary" type="button" onclick="loadSample()">Nạp dữ liệu mẫu</button>
        </div>

        <div id="successBox" class="success-box"></div>
        <div id="errorBox" class="error-box"></div>
    </div>
</div>

<script>
let buildingIndex = 0;
let wanIndex = 0;

function showError(message) {{
    const el = document.getElementById("errorBox");
    el.style.display = "block";
    el.innerText = message;
}}

function hideError() {{
    const el = document.getElementById("errorBox");
    el.style.display = "none";
    el.innerText = "";
}}

function showSuccess(message) {{
    const el = document.getElementById("successBox");
    el.style.display = "block";
    el.innerText = message;
}}

function buildingCard(index, data = {{}}) {{
    return `
        <div class="sub-card" id="building_${{index}}">
            <div class="sub-card-header">
                <div class="sub-card-title">Tòa nhà ${{index + 1}}</div>
                <button class="btn btn-danger" type="button" onclick="removeBuilding(${{index}})">Xóa</button>
            </div>

            <div class="grid-2">
                <div>
                    <label>Tên tòa nhà</label>
                    <input type="text" id="building_name_${{index}}" value="${{data.name || "Tòa nhà " + (index + 1)}}" />
                </div>
                <div>
                    <label>Số tầng cần kết nối mạng</label>
                    <input type="number" id="building_floors_${{index}}" value="${{data.floors || 6}}" />
                </div>
                <div>
                    <label>Diện tích trung bình mặt sàn</label>
                    <input type="number" id="building_area_${{index}}" value="${{data.area_per_floor || 1000}}" />
                </div>
                <div>
                    <label>Số phòng trung bình mỗi tầng</label>
                    <input type="number" id="building_rooms_${{index}}" value="${{data.rooms_per_floor || 0}}" />
                </div>
                <div>
                    <label>Số node mạng mỗi tầng</label>
                    <input type="number" id="building_node_${{index}}" value="${{data.node_per_floor || 55}}" />
                </div>
            </div>

            <div class="checkbox-row">
                <input type="checkbox" id="building_wifi_${{index}}" ${{data.has_indoor_wifi !== false ? "checked" : ""}} />
                <span>Có phủ sóng WiFi indoor</span>
            </div>
        </div>
    `;
}}

function wanCard(index, data = {{}}) {{
    return `
        <div class="sub-card" id="wan_${{index}}">
            <div class="sub-card-header">
                <div class="sub-card-title">WAN Site ${{index + 1}}</div>
                <button class="btn btn-danger" type="button" onclick="removeWan(${{index}})">Xóa</button>
            </div>

            <div class="grid-2">
                <div>
                    <label>Tên site</label>
                    <input type="text" id="wan_name_${{index}}" value="${{data.name || "WAN " + (index + 1)}}" />
                </div>
                <div>
                    <label>Số lượng Users</label>
                    <input type="number" id="wan_users_${{index}}" value="${{data.users || 100}}" />
                </div>
                <div>
                    <label>Băng thông WAN (Mbps)</label>
                    <input type="number" id="wan_bandwidth_${{index}}" value="${{data.bandwidth_mbps || 200}}" />
                </div>
                <div>
                    <label>Số lượng node mạng</label>
                    <input type="number" id="wan_node_${{index}}" value="${{data.node_count || 50}}" />
                </div>
                <div>
                    <label>Diện tích phủ sóng WiFi (m²)</label>
                    <input type="number" id="wan_area_${{index}}" value="${{data.wifi_area ?? 200}}" />
                </div>
            </div>

            <div class="checkbox-row">
                <input type="checkbox" id="wan_wifi_${{index}}" ${{data.has_wifi !== false ? "checked" : ""}} />
                <span>Có phủ sóng WiFi</span>
            </div>

            <div class="checkbox-row">
                <input type="checkbox" id="wan_ha_${{index}}" ${{data.has_ha_gateway ? "checked" : ""}} />
                <span>Có thiết kế HA Gateway</span>
            </div>
        </div>
    `;
}}

function addBuilding(data = {{}}) {{
    document.getElementById("buildings_container").insertAdjacentHTML("beforeend", buildingCard(buildingIndex, data));
    buildingIndex++;
}}

function removeBuilding(index) {{
    const el = document.getElementById(`building_${{index}}`);
    if (el) el.remove();
}}

function addWan(data = {{}}) {{
    document.getElementById("wan_container").insertAdjacentHTML("beforeend", wanCard(wanIndex, data));
    wanIndex++;
}}

function removeWan(index) {{
    const el = document.getElementById(`wan_${{index}}`);
    if (el) el.remove();
}}

function toggleServerFarm() {{
    const enabled = document.getElementById("sf_enabled").checked;
    document.getElementById("server_farm_fields").style.display = enabled ? "block" : "none";
}}

function getBuildings() {{
    const buildings = [];

    for (let i = 0; i < buildingIndex; i++) {{
        const el = document.getElementById(`building_${{i}}`);
        if (!el) continue;

        buildings.push({{
            name: document.getElementById(`building_name_${{i}}`).value,
            floors: Number(document.getElementById(`building_floors_${{i}}`).value || 0),
            area_per_floor: Number(document.getElementById(`building_area_${{i}}`).value || 0),
            rooms_per_floor: Number(document.getElementById(`building_rooms_${{i}}`).value || 0),
            node_per_floor: Number(document.getElementById(`building_node_${{i}}`).value || 0),
            has_indoor_wifi: document.getElementById(`building_wifi_${{i}}`).checked
        }});
    }}

    return buildings;
}}

function getWans() {{
    const wans = [];

    for (let i = 0; i < wanIndex; i++) {{
        const el = document.getElementById(`wan_${{i}}`);
        if (!el) continue;

        wans.push({{
            name: document.getElementById(`wan_name_${{i}}`).value,
            users: Number(document.getElementById(`wan_users_${{i}}`).value || 0),
            bandwidth_mbps: Number(document.getElementById(`wan_bandwidth_${{i}}`).value || 0),
            node_count: Number(document.getElementById(`wan_node_${{i}}`).value || 0),
            has_wifi: document.getElementById(`wan_wifi_${{i}}`).checked,
            wifi_area: Number(document.getElementById(`wan_area_${{i}}`).value || 0),
            has_ha_gateway: document.getElementById(`wan_ha_${{i}}`).checked
        }});
    }}

    return wans;
}}

function buildPayload() {{
    const serverFarmEnabled = document.getElementById("sf_enabled").checked;

    return {{
        hq: {{
            users: Number(document.getElementById("hq_users").value || 0),
            has_server_farm: serverFarmEnabled,
            has_outdoor_wifi: document.getElementById("hq_outdoor_wifi").checked,
            outdoor_area: Number(document.getElementById("outdoor_area").value || 0)
        }},
        buildings: getBuildings(),
        server_farm: {{
            enabled: serverFarmEnabled,
            racks: Number(document.getElementById("sf_racks").value || 0),
            servers_per_rack: Number(document.getElementById("sf_servers_per_rack").value || 0),
            port_100g_per_server: Number(document.getElementById("sf_100g").value || 0),
            port_10g_sfp_per_server: Number(document.getElementById("sf_10g_sfp").value || 0),
            port_10g_rj45_per_server: Number(document.getElementById("sf_10g_rj45").value || 0),
            port_1g_sfp_per_server: Number(document.getElementById("sf_1g_sfp").value || 0),
            port_1g_rj45_per_server: Number(document.getElementById("sf_1g_rj45").value || 0)
        }},
        wan_sites: getWans()
    }};
}}

function clearSurveyCollections() {{
    document.getElementById("buildings_container").innerHTML = "";
    document.getElementById("wan_container").innerHTML = "";
    buildingIndex = 0;
    wanIndex = 0;
}}

function fillSurvey(payload) {{
    const hq = payload.hq || {{}};
    const serverFarm = payload.server_farm || {{}};

    document.getElementById("hq_users").value = hq.users ?? 1000;
    document.getElementById("hq_outdoor_wifi").checked = hq.has_outdoor_wifi !== false;
    document.getElementById("outdoor_area").value = hq.outdoor_area ?? 5000;

    document.getElementById("sf_enabled").checked = serverFarm.enabled !== false && hq.has_server_farm !== false;
    toggleServerFarm();

    document.getElementById("sf_racks").value = serverFarm.racks ?? 2;
    document.getElementById("sf_servers_per_rack").value = serverFarm.servers_per_rack ?? 10;
    document.getElementById("sf_100g").value = serverFarm.port_100g_per_server ?? 0;
    document.getElementById("sf_10g_sfp").value = serverFarm.port_10g_sfp_per_server ?? 0;
    document.getElementById("sf_10g_rj45").value = serverFarm.port_10g_rj45_per_server ?? 1;
    document.getElementById("sf_1g_sfp").value = serverFarm.port_1g_sfp_per_server ?? 1;
    document.getElementById("sf_1g_rj45").value = serverFarm.port_1g_rj45_per_server ?? 2;

    clearSurveyCollections();

    (payload.buildings || []).forEach(building => addBuilding(building));
    (payload.wan_sites || []).forEach(wan => addWan(wan));
}}

function restoreSurvey() {{
    const raw = localStorage.getItem("surveyPayload");

    if (!raw) {{
        loadSample(false);
        return;
    }}

    try {{
        fillSurvey(JSON.parse(raw));
    }} catch (e) {{
        loadSample(false);
    }}
}}

function loadSample() {{
    fillSurvey({{
        hq: {{
            users: 1000,
            has_server_farm: true,
            has_outdoor_wifi: true,
            outdoor_area: 5000
        }},
        buildings: [
            {{
                name: "Tòa nhà 1",
                floors: 6,
                area_per_floor: 1000,
                rooms_per_floor: 0,
                node_per_floor: 55,
                has_indoor_wifi: true
            }},
            {{
                name: "Tòa nhà 2",
                floors: 6,
                area_per_floor: 1560,
                rooms_per_floor: 0,
                node_per_floor: 60,
                has_indoor_wifi: true
            }},
            {{
                name: "Tòa nhà 3",
                floors: 12,
                area_per_floor: 800,
                rooms_per_floor: 0,
                node_per_floor: 65,
                has_indoor_wifi: true
            }}
        ],
        server_farm: {{
            enabled: true,
            racks: 2,
            servers_per_rack: 10,
            port_100g_per_server: 0,
            port_10g_sfp_per_server: 0,
            port_10g_rj45_per_server: 1,
            port_1g_sfp_per_server: 1,
            port_1g_rj45_per_server: 2
        }},
        wan_sites: [
            {{
                name: "WAN 1",
                users: 100,
                bandwidth_mbps: 200,
                node_count: 50,
                has_wifi: true,
                wifi_area: 200,
                has_ha_gateway: true
            }}
        ]
    }});
}}

async function generateCalculation() {{
    hideError();

    try {{
        const payload = buildPayload();

        showSuccess("Đang tính toán, vui lòng chờ...");

        const res = await fetch("/api/generate-quote", {{
            method: "POST",
            headers: {{
                "Content-Type": "application/json"
            }},
            body: JSON.stringify(payload)
        }});

        const rawText = await res.text();

        let data;
        try {{
            data = JSON.parse(rawText);
        }} catch (e) {{
            showError("Backend trả về dữ liệu không phải JSON:\\n" + rawText);
            return;
        }}

        if (!res.ok) {{
            showError("Lỗi backend:\\n" + JSON.stringify(data, null, 2));
            return;
        }}

        localStorage.setItem("surveyPayload", JSON.stringify(payload));
        localStorage.setItem("quoteData", JSON.stringify(data));

        window.location.href = "/calculation-results";
    }} catch (e) {{
        showError("Không gọi được API. Kiểm tra uvicorn còn chạy không.\\n" + e);
    }}
}}

restoreSurvey();
</script>
</body>
</html>
    """


@app.get("/calculation-results", response_class=HTMLResponse)
def calculation_results_page():
    return f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="utf-8" />
    <title>Calculation Results</title>
    {BASE_STYLE}
</head>
<body>
<div class="container">
    <h1>Kết quả tính toán</h1>
    <div class="subtitle">Trang 2: Xem demand, số lượng thiết bị và requirement kỹ thuật</div>

    <div class="stepbar">
        <div class="step">1. Nhập khảo sát</div>
        <div class="step active">2. Kết quả tính toán</div>
        <div class="step">3. Chọn model & báo giá</div>
    </div>

    <div id="content"></div>

    <div class="actions">
        <a class="btn btn-secondary" href="/survey">Quay lại khảo sát</a>
        <a class="btn btn-primary" href="/quote">Tiếp tục chọn model & xem báo giá</a>
    </div>
</div>

<script>
function money(v) {{
    return "$" + Number(v || 0).toLocaleString(undefined, {{
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }});
}}

function render() {{
    const raw = localStorage.getItem("quoteData");

    if (!raw) {{
        document.getElementById("content").innerHTML = `
            <div class="card">
                <div class="empty-state">
                    Chưa có dữ liệu tính toán. Hãy quay lại trang khảo sát.
                </div>
            </div>
        `;
        return;
    }}

    const data = JSON.parse(raw);
    const req = data.requirements;
    const requirements = req.requirements || [];
    const buildings = req.building_details || [];
    const wans = req.wan_details || [];

    let html = `
        <div class="card">
            <h2>Tổng quan kết quả</h2>
            <div class="summary-grid">
                <div class="metric">
                    <div class="metric-label">Gateway Demand HQ</div>
                    <div class="metric-value">${{Number(req.gateway_demand_mbps || 0).toFixed(2)}} Mbps</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Server Farm BW</div>
                    <div class="metric-value">${{Number(req.server_farm_bandwidth_gbps || 0).toFixed(2)}} Gbps</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Số tòa nhà</div>
                    <div class="metric-value">${{req.building_count || 0}}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Số WAN site</div>
                    <div class="metric-value">${{req.wan_count || 0}}</div>
                </div>
            </div>
        </div>
    `;

    html += `
        <div class="card">
            <h2>Chi tiết tính toán theo tòa nhà</h2>
            <table>
                <thead>
                    <tr>
                        <th>Tòa nhà</th>
                        <th>Số tầng</th>
                        <th>Diện tích/tầng</th>
                        <th>Node/tầng</th>
                        <th>WiFi</th>
                        <th>Switch đã tính</th>
                        <th>AP indoor</th>
                    </tr>
                </thead>
                <tbody>
    `;

    buildings.forEach(b => {{
        html += `
            <tr>
                <td>${{b.name}}</td>
                <td>${{b.floors}}</td>
                <td>${{b.area_per_floor}}</td>
                <td>${{b.node_per_floor}}</td>
                <td>${{b.has_indoor_wifi ? "Y" : "N"}}</td>
                <td><pre>${{JSON.stringify(b.switches, null, 2)}}</pre></td>
                <td>${{b.indoor_ap}}</td>
            </tr>
        `;
    }});

    html += `
                </tbody>
            </table>
        </div>
    `;

    html += `
        <div class="card">
            <h2>Chi tiết tính toán WAN</h2>
            <table>
                <thead>
                    <tr>
                        <th>WAN Site</th>
                        <th>Users</th>
                        <th>Bandwidth</th>
                        <th>WAN Demand</th>
                        <th>Router Size</th>
                        <th>Node</th>
                        <th>WiFi</th>
                        <th>HA</th>
                        <th>Router đã tính</th>
                        <th>Switch đã tính</th>
                        <th>AP indoor</th>
                        <th>SFP 1G</th>
                    </tr>
                </thead>
                <tbody>
    `;

    wans.forEach(w => {{
        html += `
            <tr>
                <td>${{w.name}}</td>
                <td>${{w.users}}</td>
                <td>${{w.bandwidth_mbps}} Mbps</td>
                <td>${{Number(w.wan_demand_mbps || 0).toFixed(2)}} Mbps</td>
                <td>${{w.router_size}}</td>
                <td>${{w.node_count}}</td>
                <td>${{w.has_wifi ? "Y" : "N"}}</td>
                <td>${{w.has_ha_gateway ? "Y" : "N"}}</td>
                <td><pre>${{JSON.stringify({{
                    router_small: w.router_small_quantity || 0,
                    router_large: w.router_large_quantity || 0
                }}, null, 2)}}</pre></td>
                <td><pre>${{JSON.stringify(w.switches || {{}}, null, 2)}}</pre></td>
                <td>${{w.ap_quantity || 0}}</td>
                <td>${{w.sfp_1g_quantity || 0}}</td>
            </tr>
        `;
    }});

    html += `
                </tbody>
            </table>
        </div>
    `;

    html += `
        <div class="card">
            <h2>Danh sách requirement kỹ thuật</h2>
            <table>
                <thead>
                    <tr>
                        <th>Group</th>
                        <th>Item Type</th>
                        <th>Quantity</th>
                        <th>Requirement</th>
                    </tr>
                </thead>
                <tbody>
    `;

    requirements.forEach(line => {{
        html += `
            <tr>
                <td>${{line.group}}</td>
                <td>${{line.item_type}}</td>
                <td>${{line.quantity}}</td>
                <td><pre>${{JSON.stringify(line.requirement, null, 2)}}</pre></td>
            </tr>
        `;
    }});

    html += `
                </tbody>
            </table>
        </div>
    `;

    document.getElementById("content").innerHTML = html;
}}

render();
</script>
</body>
</html>
    """

@app.get("/quote", response_class=HTMLResponse)
def quote_page():
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
            grid-template-columns: repeat(4, 1fr);
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
<div class="container">
    <div class="page-header">
        <div class="page-header-left">
            <h1>Chọn model và tổng hợp báo giá</h1>
            <div class="subtitle">Trang 3: chọn thiết bị cho từng option và xem tổng giá rõ ràng hơn</div>
        </div>
    </div>

    <div class="stepbar">
        <div class="step">1. Nhập khảo sát</div>
        <div class="step">2. Kết quả tính toán</div>
        <div class="step active">3. Chọn model & báo giá</div>
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
    lines.forEach(line => {{
        ["opt1", "opt2", "opt3"].forEach(opt => {{
            totals[opt] += Number(line.amount && line.amount[opt] ? line.amount[opt] : 0);
        }});
    }});

    document.getElementById("summary_block").innerHTML = `
        <div class="group-summary-card">
            <h3>Tổng quan báo giá</h3>
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
                <div class="quote-metric">
                    <div class="label">Số dòng thiết bị</div>
                    <div class="value">${{lines.length}}</div>
                </div>
            </div>
        </div>
    `;

    return totals;
}}

function renderGroupSummary(lines) {{
    const groupTotals = {{}};

    lines.forEach(line => {{
        if (!groupTotals[line.group]) {{
            groupTotals[line.group] = {{ opt1: 0, opt2: 0, opt3: 0 }};
        }}

        ["opt1", "opt2", "opt3"].forEach(opt => {{
            groupTotals[line.group][opt] += Number(line.amount && line.amount[opt] ? line.amount[opt] : 0);
        }});
    }});

    let rows = "";
    Object.keys(groupTotals).forEach(group => {{
        rows += `
            <tr>
                <td><strong>${{group}}</strong></td>
                <td>${{money(groupTotals[group].opt1)}}</td>
                <td>${{money(groupTotals[group].opt2)}}</td>
                <td>${{money(groupTotals[group].opt3)}}</td>
            </tr>
        `;
    }});

    document.getElementById("group_summary_block").innerHTML = `
        <div class="group-summary-card">
            <h3>Tổng theo nhóm giải pháp</h3>
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
                    ${{rows}}
                </tbody>
            </table>
        </div>
    `;
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
                <p>Mỗi option được tách rõ thành 3 phần: chọn thiết bị, đơn giá và thành tiền.</p>
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


@app.get("/bom", response_class=HTMLResponse)
def bom_page():
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


@app.post("/api/requirements")
def api_requirements(payload: SurveyPayload):
    req = build_requirements(payload_to_dict(payload))
    return req


@app.post("/api/generate-quote")
def api_generate_quote(payload: SurveyPayload):
    print("generate quote called")

    data = payload_to_dict(payload)

    req = build_requirements(data)
    print("requirements:", len(req["requirements"]))
    print("proposal lines:", len(req["proposal_lines"]))

    recs = recommend_all(req["proposal_lines"])
    print("recommendations:", len(recs))

    quote = build_quote(recs)
    print("quote lines:", len(quote["quote_lines"]))

    return {
        "requirements": req,
        "quote": quote
    }


@app.post("/api/build-bom")
def api_build_bom(payload: BomPayload):
    return build_bom(payload.quote_data)


@app.post("/api/download-bom")
def api_download_bom(payload: BomPayload):
    output = build_bom_excel(payload.quote_data)
    headers = {
        "Content-Disposition": 'attachment; filename="network_bom.xlsx"'
    }

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


@app.get("/api/debug-catalog")
def api_debug_catalog():
    return debug_catalog_summary()


@app.get("/health")
def health():
    return {"status": "ok"}
