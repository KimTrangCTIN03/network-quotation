from app.pages.styles import BASE_STYLE


def render_survey_page():
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
    <div class="subtitle"></div>

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
