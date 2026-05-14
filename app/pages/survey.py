from app.pages.styles import BASE_STYLE, render_nav


def render_survey_page(user=None, solution_area: str = "campus"):
    solution_base = "/dc-sdn" if str(solution_area or "").lower() == "dc-sdn" else "/campus"
    return f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="utf-8" />
    <title>Survey - Network Quotation Tool</title>
    {BASE_STYLE}
    <style>
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 12px;
            margin-top: 12px;
        }}

        .summary-item {{
            border: 1px solid #dbe3ef;
            border-radius: 10px;
            padding: 12px;
            background: #f8fafc;
        }}

        .summary-title {{
            font-weight: 800;
            margin-bottom: 6px;
        }}

        .summary-meta {{
            color: #64748b;
            font-size: 13px;
            line-height: 1.45;
        }}

        .summary-list {{
            display: grid;
            gap: 6px;
            margin-top: 10px;
            color: #334155;
            font-size: 13px;
        }}

        .summary-row {{
            display: flex;
            justify-content: space-between;
            gap: 14px;
            border-top: 1px solid #e5edf7;
            padding-top: 6px;
        }}

        .summary-row span:first-child {{
            color: #64748b;
        }}

        .summary-row span:last-child {{
            font-weight: 700;
            text-align: right;
        }}

        .modal-backdrop {{
            display: none;
            position: fixed;
            inset: 0;
            z-index: 20;
            background: rgba(15, 23, 42, 0.42);
            padding: 24px;
            overflow: auto;
        }}

        .modal {{
            width: min(760px, 100%);
            margin: 48px auto;
            background: #fff;
            border-radius: 12px;
            border: 1px solid #dbe3ef;
            box-shadow: 0 24px 80px rgba(15, 23, 42, 0.24);
            padding: 22px;
        }}

        .modal-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 16px;
            margin-bottom: 16px;
        }}

        .modal-title {{
            font-size: 22px;
            font-weight: 900;
        }}

        .modal-actions {{
            display: flex;
            justify-content: space-between;
            gap: 12px;
            margin-top: 18px;
        }}

        .modal-actions .left,
        .modal-actions .right {{
            display: flex;
            gap: 10px;
        }}

        @media (max-width: 700px) {{
            .modal {{
                margin: 12px auto;
                padding: 16px;
            }}

            .modal-actions,
            .modal-actions .left,
            .modal-actions .right {{
                display: grid;
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body class="solution-{solution_area}">
{render_nav("survey", user, solution_area)}
<div class="container">
    <h1>Network Quotation Tool</h1>
    <div class="subtitle"></div>
    <div class="card">
        <div class="section-title">1. Thông tin khảo sát Campus</div>
        <div class="grid-2">
            <div>
                <label>Số user HQ</label>
                <input type="number" id="hq_users" value="1000" />
            </div>
            <div>
                <label>Diện tích outdoor cần phủ WiFi (m²)</label>
                <input type="number" id="outdoor_area" value="5000" />
            </div>
            <div>
                <label>Số tòa nhà</label>
                <input type="number" id="building_count" min="0" value="3" onchange="handleBuildingCountChanged()" />
            </div>
            <div>
                <label>Số WAN site</label>
                <input type="number" id="wan_count" min="0" value="1" onchange="handleWanCountChanged()" />
            </div>
        </div>

        <div class="checkbox-row">
            <input type="checkbox" id="hq_outdoor_wifi" checked />
            <span>Có WiFi outdoor</span>
        </div>

        <div class="section-title">2. Thông tin từng tòa nhà</div>
        <div class="actions" style="margin-top:0;">
            <button class="btn btn-secondary" type="button" onclick="openBuildingDialog(0)">Nhập / sửa thông tin tòa nhà</button>
        </div>
        <div id="buildings_summary" class="summary-grid"></div>

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

        <div class="section-title">4. Chi tiết DC-SDN</div>
        <div class="checkbox-row">
            <input type="checkbox" id="dc_sdn_enabled" onchange="toggleDcSdn()" />
            <span>Có DC-SDN</span>
        </div>

        <div id="dc_sdn_fields" style="display:none;">
            <div class="grid-2">
                <div>
                    <label>Số rack DC-SDN</label>
                    <input type="number" id="dc_sdn_racks" value="2" />
                </div>
                <div>
                    <label>Số server / rack DC-SDN</label>
                    <input type="number" id="dc_sdn_servers_per_rack" value="10" />
                </div>
            </div>

            <div class="grid-2" style="margin-top:12px;">
                <div>
                    <label>Số cổng 100GE / server</label>
                    <input type="number" id="dc_sdn_100g" value="1" />
                </div>
                <div>
                    <label>Số cổng 10GE SFP / server</label>
                    <input type="number" id="dc_sdn_10g_sfp" value="0" />
                </div>
                <div>
                    <label>Số cổng 10GE RJ45 / server</label>
                    <input type="number" id="dc_sdn_10g_rj45" value="0" />
                </div>
                <div>
                    <label>Số cổng 1GE SFP / server</label>
                    <input type="number" id="dc_sdn_1g_sfp" value="0" />
                </div>
                <div>
                    <label>Số cổng 1GE RJ45 / server</label>
                    <input type="number" id="dc_sdn_1g_rj45" value="0" />
                </div>
            </div>
        </div>

        <div class="section-title">5. Thông tin từng WAN site</div>
        <div class="actions" style="margin-top:0;">
            <button class="btn btn-secondary" type="button" onclick="openWanDialog(0)">Nhập / sửa thông tin WAN</button>
        </div>
        <div id="wan_summary" class="summary-grid"></div>

        <div class="actions">
            <button class="btn btn-primary" type="button" onclick="generateCalculation()">Tạo kết quả tính toán</button>
            <button class="btn btn-secondary" type="button" onclick="loadSample()">Nạp dữ liệu mẫu</button>
        </div>

        <div id="successBox" class="success-box"></div>
        <div id="errorBox" class="error-box"></div>
    </div>
</div>

<div id="building_modal" class="modal-backdrop">
    <div class="modal">
        <div class="modal-header">
            <div id="building_modal_title" class="modal-title">Tòa nhà</div>
            <button class="btn btn-secondary" type="button" onclick="closeBuildingDialog()">Đóng</button>
        </div>
        <div class="grid-2">
            <div>
                <label>Tên tòa nhà</label>
                <input type="text" id="modal_building_name" />
            </div>
            <div>
                <label>Số tầng cần kết nối mạng</label>
                <input type="number" id="modal_building_floors" />
            </div>
            <div>
                <label>Diện tích trung bình mặt sàn</label>
                <input type="number" id="modal_building_area" />
            </div>
            <div>
                <label>Số phòng trung bình mỗi tầng</label>
                <input type="number" id="modal_building_rooms" />
            </div>
            <div>
                <label>Số node mạng mỗi tầng</label>
                <input type="number" id="modal_building_node" />
            </div>
        </div>
        <div class="checkbox-row">
            <input type="checkbox" id="modal_building_wifi" />
            <span>Có phủ sóng WiFi indoor</span>
        </div>
        <div class="modal-actions">
            <div class="left">
                <button id="building_prev_btn" class="btn btn-secondary" type="button" onclick="previousBuilding()">Quay lại</button>
            </div>
            <div class="right">
                <button class="btn btn-secondary" type="button" onclick="closeBuildingDialog()">Lưu & đóng</button>
                <button id="building_next_btn" class="btn btn-primary" type="button" onclick="nextBuilding()">Tiếp</button>
            </div>
        </div>
    </div>
</div>

<div id="wan_modal" class="modal-backdrop">
    <div class="modal">
        <div class="modal-header">
            <div id="wan_modal_title" class="modal-title">WAN Site</div>
            <button class="btn btn-secondary" type="button" onclick="closeWanDialog()">Đóng</button>
        </div>
        <div class="grid-2">
            <div>
                <label>Tên site</label>
                <input type="text" id="modal_wan_name" />
            </div>
            <div>
                <label>Số lượng Users</label>
                <input type="number" id="modal_wan_users" />
            </div>
            <div>
                <label>Băng thông WAN (Mbps)</label>
                <input type="number" id="modal_wan_bandwidth" />
            </div>
            <div>
                <label>Số lượng node mạng</label>
                <input type="number" id="modal_wan_node" />
            </div>
            <div>
                <label>Diện tích phủ sóng WiFi (m²)</label>
                <input type="number" id="modal_wan_area" />
            </div>
        </div>
        <div class="checkbox-row">
            <input type="checkbox" id="modal_wan_wifi" />
            <span>Có phủ sóng WiFi</span>
        </div>
        <div class="checkbox-row">
            <input type="checkbox" id="modal_wan_ha" />
            <span>Có thiết kế HA Gateway</span>
        </div>
        <div class="modal-actions">
            <div class="left">
                <button id="wan_prev_btn" class="btn btn-secondary" type="button" onclick="previousWan()">Quay lại</button>
            </div>
            <div class="right">
                <button class="btn btn-secondary" type="button" onclick="closeWanDialog()">Lưu & đóng</button>
                <button id="wan_next_btn" class="btn btn-primary" type="button" onclick="nextWan()">Tiếp</button>
            </div>
        </div>
    </div>
</div>

<script>
const SOLUTION_AREA = "{solution_area}";
let surveyBuildings = [];
let surveyWans = [];
let buildingEditIndex = 0;
let wanEditIndex = 0;

function numberValue(id, fallback = 0) {{
    const value = Number(document.getElementById(id).value || fallback);
    return Number.isFinite(value) ? value : fallback;
}}

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

function defaultBuilding(index) {{
    return {{
        name: "Tòa nhà " + (index + 1),
        floors: 6,
        area_per_floor: 1000,
        rooms_per_floor: 0,
        node_per_floor: 55,
        has_indoor_wifi: true
    }};
}}

function defaultWan(index) {{
    return {{
        name: "WAN " + (index + 1),
        users: 100,
        bandwidth_mbps: 200,
        node_count: 50,
        has_wifi: true,
        wifi_area: 200,
        has_ha_gateway: false
    }};
}}

function resizeBuildings() {{
    const targetCount = Math.max(0, numberValue("building_count", 0));

    while (surveyBuildings.length < targetCount) {{
        surveyBuildings.push(defaultBuilding(surveyBuildings.length));
    }}

    if (surveyBuildings.length > targetCount) {{
        surveyBuildings = surveyBuildings.slice(0, targetCount);
    }}

    renderBuildingSummary();
}}

function resizeWans() {{
    const targetCount = Math.max(0, numberValue("wan_count", 0));

    while (surveyWans.length < targetCount) {{
        surveyWans.push(defaultWan(surveyWans.length));
    }}

    if (surveyWans.length > targetCount) {{
        surveyWans = surveyWans.slice(0, targetCount);
    }}

    renderWanSummary();
}}

function handleBuildingCountChanged() {{
    resizeBuildings();
    if (surveyBuildings.length > 0) {{
        openBuildingDialog(0);
    }}
}}

function handleWanCountChanged() {{
    resizeWans();
    if (surveyWans.length > 0) {{
        openWanDialog(0);
    }}
}}

function renderBuildingSummary() {{
    const container = document.getElementById("buildings_summary");

    if (!surveyBuildings.length) {{
        container.innerHTML = `<div class="empty-state">Chưa có tòa nhà nào.</div>`;
        return;
    }}

    container.innerHTML = surveyBuildings.map((building, index) => `
        <div class="summary-item">
            <div class="summary-title">${{building.name || "Tòa nhà " + (index + 1)}}</div>
            <div class="summary-list">
                <div class="summary-row"><span>Số tầng</span><span>${{building.floors || 0}}</span></div>
                <div class="summary-row"><span>Diện tích trung bình mặt sàn</span><span>${{building.area_per_floor || 0}} m²</span></div>
                <div class="summary-row"><span>Số phòng trung bình mỗi tầng</span><span>${{building.rooms_per_floor || 0}}</span></div>
                <div class="summary-row"><span>Số node mạng mỗi tầng</span><span>${{building.node_per_floor || 0}}</span></div>
                <div class="summary-row"><span>WiFi indoor</span><span>${{building.has_indoor_wifi ? "Có" : "Không"}}</span></div>
            </div>
            <div class="actions" style="margin-top:10px;">
                <button class="btn btn-secondary" type="button" onclick="openBuildingDialog(${{index}})">Sửa</button>
            </div>
        </div>
    `).join("");
}}

function renderWanSummary() {{
    const container = document.getElementById("wan_summary");

    if (!surveyWans.length) {{
        container.innerHTML = `<div class="empty-state">Chưa có WAN site nào.</div>`;
        return;
    }}

    container.innerHTML = surveyWans.map((wan, index) => `
        <div class="summary-item">
            <div class="summary-title">${{wan.name || "WAN " + (index + 1)}}</div>
            <div class="summary-list">
                <div class="summary-row"><span>Số lượng Users</span><span>${{wan.users || 0}}</span></div>
                <div class="summary-row"><span>Băng thông WAN</span><span>${{wan.bandwidth_mbps || 0}} Mbps</span></div>
                <div class="summary-row"><span>Số lượng node mạng</span><span>${{wan.node_count || 0}}</span></div>
                <div class="summary-row"><span>Diện tích phủ sóng WiFi</span><span>${{wan.wifi_area || 0}} m²</span></div>
                <div class="summary-row"><span>WiFi</span><span>${{wan.has_wifi ? "Có" : "Không"}}</span></div>
                <div class="summary-row"><span>HA Gateway</span><span>${{wan.has_ha_gateway ? "Có" : "Không"}}</span></div>
            </div>
            <div class="actions" style="margin-top:10px;">
                <button class="btn btn-secondary" type="button" onclick="openWanDialog(${{index}})">Sửa</button>
            </div>
        </div>
    `).join("");
}}

function openBuildingDialog(index = 0) {{
    resizeBuildings();

    if (!surveyBuildings.length) {{
        showError("Vui lòng nhập số tòa nhà lớn hơn 0.");
        return;
    }}

    hideError();
    buildingEditIndex = Math.min(Math.max(index, 0), surveyBuildings.length - 1);
    fillBuildingDialog();
    document.getElementById("building_modal").style.display = "block";
}}

function fillBuildingDialog() {{
    const building = surveyBuildings[buildingEditIndex] || defaultBuilding(buildingEditIndex);
    document.getElementById("building_modal_title").innerText = `Tòa nhà ${{buildingEditIndex + 1}} / ${{surveyBuildings.length}}`;
    document.getElementById("modal_building_name").value = building.name || "";
    document.getElementById("modal_building_floors").value = building.floors ?? 6;
    document.getElementById("modal_building_area").value = building.area_per_floor ?? 1000;
    document.getElementById("modal_building_rooms").value = building.rooms_per_floor ?? 0;
    document.getElementById("modal_building_node").value = building.node_per_floor ?? 55;
    document.getElementById("modal_building_wifi").checked = building.has_indoor_wifi !== false;
    document.getElementById("building_prev_btn").disabled = buildingEditIndex === 0;
    document.getElementById("building_next_btn").innerText = buildingEditIndex === surveyBuildings.length - 1 ? "Hoàn tất" : "Tiếp";
}}

function saveBuildingDialog() {{
    if (!surveyBuildings.length) return;

    surveyBuildings[buildingEditIndex] = {{
        name: document.getElementById("modal_building_name").value,
        floors: numberValue("modal_building_floors", 0),
        area_per_floor: numberValue("modal_building_area", 0),
        rooms_per_floor: numberValue("modal_building_rooms", 0),
        node_per_floor: numberValue("modal_building_node", 0),
        has_indoor_wifi: document.getElementById("modal_building_wifi").checked
    }};
}}

function nextBuilding() {{
    saveBuildingDialog();

    if (buildingEditIndex < surveyBuildings.length - 1) {{
        buildingEditIndex++;
        fillBuildingDialog();
        return;
    }}

    closeBuildingDialog();
}}

function previousBuilding() {{
    saveBuildingDialog();

    if (buildingEditIndex > 0) {{
        buildingEditIndex--;
        fillBuildingDialog();
    }}
}}

function closeBuildingDialog() {{
    saveBuildingDialog();
    document.getElementById("building_modal").style.display = "none";
    renderBuildingSummary();
}}

function openWanDialog(index = 0) {{
    resizeWans();

    if (!surveyWans.length) {{
        showError("Vui lòng nhập số WAN site lớn hơn 0.");
        return;
    }}

    hideError();
    wanEditIndex = Math.min(Math.max(index, 0), surveyWans.length - 1);
    fillWanDialog();
    document.getElementById("wan_modal").style.display = "block";
}}

function fillWanDialog() {{
    const wan = surveyWans[wanEditIndex] || defaultWan(wanEditIndex);
    document.getElementById("wan_modal_title").innerText = `WAN Site ${{wanEditIndex + 1}} / ${{surveyWans.length}}`;
    document.getElementById("modal_wan_name").value = wan.name || "";
    document.getElementById("modal_wan_users").value = wan.users ?? 100;
    document.getElementById("modal_wan_bandwidth").value = wan.bandwidth_mbps ?? 200;
    document.getElementById("modal_wan_node").value = wan.node_count ?? 50;
    document.getElementById("modal_wan_area").value = wan.wifi_area ?? 200;
    document.getElementById("modal_wan_wifi").checked = wan.has_wifi !== false;
    document.getElementById("modal_wan_ha").checked = !!wan.has_ha_gateway;
    document.getElementById("wan_prev_btn").disabled = wanEditIndex === 0;
    document.getElementById("wan_next_btn").innerText = wanEditIndex === surveyWans.length - 1 ? "Hoàn tất" : "Tiếp";
}}

function saveWanDialog() {{
    if (!surveyWans.length) return;

    surveyWans[wanEditIndex] = {{
        name: document.getElementById("modal_wan_name").value,
        users: numberValue("modal_wan_users", 0),
        bandwidth_mbps: numberValue("modal_wan_bandwidth", 0),
        node_count: numberValue("modal_wan_node", 0),
        has_wifi: document.getElementById("modal_wan_wifi").checked,
        wifi_area: numberValue("modal_wan_area", 0),
        has_ha_gateway: document.getElementById("modal_wan_ha").checked
    }};
}}

function nextWan() {{
    saveWanDialog();

    if (wanEditIndex < surveyWans.length - 1) {{
        wanEditIndex++;
        fillWanDialog();
        return;
    }}

    closeWanDialog();
}}

function previousWan() {{
    saveWanDialog();

    if (wanEditIndex > 0) {{
        wanEditIndex--;
        fillWanDialog();
    }}
}}

function closeWanDialog() {{
    saveWanDialog();
    document.getElementById("wan_modal").style.display = "none";
    renderWanSummary();
}}

function toggleServerFarm() {{
    const enabled = document.getElementById("sf_enabled").checked;
    document.getElementById("server_farm_fields").style.display = enabled ? "block" : "none";
}}

function toggleDcSdn() {{
    const enabled = document.getElementById("dc_sdn_enabled").checked;
    document.getElementById("dc_sdn_fields").style.display = enabled ? "block" : "none";
}}

function getBuildings() {{
    return surveyBuildings.map(building => ({{ ...building }}));
}}

function getWans() {{
    return surveyWans.map(wan => ({{ ...wan }}));
}}

function buildPayload() {{
    if (document.getElementById("building_modal").style.display === "block") {{
        saveBuildingDialog();
    }}

    if (document.getElementById("wan_modal").style.display === "block") {{
        saveWanDialog();
    }}

    resizeBuildings();
    resizeWans();
    const serverFarmEnabled = document.getElementById("sf_enabled").checked;
    const dcSdnEnabled = document.getElementById("dc_sdn_enabled").checked;

    return {{
        hq: {{
            users: numberValue("hq_users", 0),
            has_server_farm: serverFarmEnabled,
            has_outdoor_wifi: document.getElementById("hq_outdoor_wifi").checked,
            outdoor_area: numberValue("outdoor_area", 0)
        }},
        buildings: getBuildings(),
        server_farm: {{
            enabled: serverFarmEnabled,
            racks: numberValue("sf_racks", 0),
            servers_per_rack: numberValue("sf_servers_per_rack", 0),
            port_100g_per_server: numberValue("sf_100g", 0),
            port_10g_sfp_per_server: numberValue("sf_10g_sfp", 0),
            port_10g_rj45_per_server: numberValue("sf_10g_rj45", 0),
            port_1g_sfp_per_server: numberValue("sf_1g_sfp", 0),
            port_1g_rj45_per_server: numberValue("sf_1g_rj45", 0)
        }},
        dc_sdn: {{
            enabled: dcSdnEnabled,
            racks: numberValue("dc_sdn_racks", 0),
            servers_per_rack: numberValue("dc_sdn_servers_per_rack", 0),
            port_100g_per_server: numberValue("dc_sdn_100g", 0),
            port_10g_sfp_per_server: numberValue("dc_sdn_10g_sfp", 0),
            port_10g_rj45_per_server: numberValue("dc_sdn_10g_rj45", 0),
            port_1g_sfp_per_server: numberValue("dc_sdn_1g_sfp", 0),
            port_1g_rj45_per_server: numberValue("dc_sdn_1g_rj45", 0)
        }},
        wan_sites: getWans()
    }};
}}

function fillSurvey(payload) {{
    const hq = payload.hq || {{}};
    const serverFarm = payload.server_farm || {{}};
    const dcSdn = payload.dc_sdn || {{}};

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

    document.getElementById("dc_sdn_enabled").checked = dcSdn.enabled === true || dcSdn.enabled === "Y";
    toggleDcSdn();
    document.getElementById("dc_sdn_racks").value = dcSdn.racks ?? 2;
    document.getElementById("dc_sdn_servers_per_rack").value = dcSdn.servers_per_rack ?? 10;
    document.getElementById("dc_sdn_100g").value = dcSdn.port_100g_per_server ?? 1;
    document.getElementById("dc_sdn_10g_sfp").value = dcSdn.port_10g_sfp_per_server ?? 0;
    document.getElementById("dc_sdn_10g_rj45").value = dcSdn.port_10g_rj45_per_server ?? 0;
    document.getElementById("dc_sdn_1g_sfp").value = dcSdn.port_1g_sfp_per_server ?? 0;
    document.getElementById("dc_sdn_1g_rj45").value = dcSdn.port_1g_rj45_per_server ?? 0;

    surveyBuildings = (payload.buildings || []).map(building => ({{ ...building }}));
    surveyWans = (payload.wan_sites || []).map(wan => ({{ ...wan }}));
    document.getElementById("building_count").value = surveyBuildings.length;
    document.getElementById("wan_count").value = surveyWans.length;
    renderBuildingSummary();
    renderWanSummary();
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
        dc_sdn: {{
            enabled: true,
            racks: 2,
            servers_per_rack: 10,
            port_100g_per_server: 1,
            port_10g_sfp_per_server: 1,
            port_10g_rj45_per_server: 1,
            port_1g_sfp_per_server: 0,
            port_1g_rj45_per_server: 0
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

function setDisplayFor(element, visible) {{
    if (element) element.style.display = visible ? "" : "none";
}}

function setSectionDisplay(titleText, visible) {{
    const titles = Array.from(document.querySelectorAll(".section-title"));
    const title = titles.find(el => String(el.textContent || "").toLowerCase().includes(titleText));
    if (!title) return;
    setDisplayFor(title, visible);
    let next = title.nextElementSibling;
    while (next && !next.classList.contains("section-title") && !next.classList.contains("actions")) {{
        setDisplayFor(next, visible);
        next = next.nextElementSibling;
    }}
}}

function applySolutionAreaMode() {{
    const isDc = SOLUTION_AREA === "dc-sdn";
    setSectionDisplay("1.", !isDc);
    setSectionDisplay("2.", !isDc);
    setSectionDisplay("3.", !isDc);
    setSectionDisplay("5.", !isDc);
    setSectionDisplay("4.", isDc);
    ["buildings_summary", "wan_summary", "server_farm_fields"].forEach(id => {{
        const element = document.getElementById(id);
        setDisplayFor(element, !isDc);
        if (element && element.previousElementSibling && element.previousElementSibling.classList.contains("actions")) {{
            setDisplayFor(element.previousElementSibling, !isDc);
        }}
    }});
    ["building_modal", "wan_modal"].forEach(id => setDisplayFor(document.getElementById(id), !isDc));
    const dcEnabled = document.getElementById("dc_sdn_enabled");
    if (dcEnabled) dcEnabled.checked = isDc || dcEnabled.checked;
    toggleDcSdn();
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

        window.location.href = "{solution_base}/calculation-results";
    }} catch (e) {{
        showError("Không gọi được API. Kiểm tra uvicorn còn chạy không.\\n" + e);
    }}
}}

restoreSurvey();
applySolutionAreaMode();
</script>
</body>
</html>
    """
