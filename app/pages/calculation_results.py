from app.pages.styles import BASE_STYLE


def render_calculation_results_page():
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
    <div class="subtitle"></div>

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
