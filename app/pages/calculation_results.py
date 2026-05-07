from app.pages.styles import BASE_STYLE, render_nav


def render_calculation_results_page(user=None):
    return f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="utf-8" />
    <title>Calculation Results</title>
    {BASE_STYLE}
    <style>
        .calc-layout {{
            display: grid;
            gap: 18px;
        }}

        .calc-summary-card {{
            padding: 24px 26px 28px;
        }}

        .calc-summary-card h2 {{
            margin: 0 0 22px;
        }}

        .calc-summary-grid {{
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 14px;
            align-items: stretch;
        }}

        .calc-summary-grid .metric {{
            min-height: 112px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: 18px 20px;
        }}

        .calc-summary-grid .metric-label {{
            font-size: 14px;
        }}

        .calc-summary-grid .metric-value {{
            font-size: 24px;
            line-height: 1.2;
        }}

        .area-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 16px;
        }}

        .area-card {{
            border: 1px solid #dbe4f0;
            border-left: 6px solid #64748b;
            border-radius: 8px;
            background: #ffffff;
            overflow: hidden;
        }}

        .area-jump {{
            cursor: pointer;
            transition: transform 0.16s ease, box-shadow 0.16s ease, border-color 0.16s ease;
        }}

        .area-jump:hover {{
            transform: translateY(-2px);
            box-shadow: 0 12px 26px rgba(15, 23, 42, 0.1);
            border-color: #bfdbfe;
        }}

        .area-card .area-head {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            padding: 14px 16px;
            border-bottom: 1px solid rgba(148, 163, 184, 0.28);
        }}

        .area-card h2,
        .area-card h3 {{
            margin: 0;
        }}

        .area-body {{
            padding: 16px;
        }}

        .area-campus {{
            border-left-color: #2563eb;
            background: linear-gradient(90deg, #eff6ff 0, #ffffff 36%);
        }}

        .area-server {{
            border-left-color: #7c3aed;
            background: linear-gradient(90deg, #f5f3ff 0, #ffffff 36%);
        }}

        .area-wan {{
            border-left-color: #059669;
            background: linear-gradient(90deg, #ecfdf5 0, #ffffff 36%);
        }}

        .area-dc {{
            border-left-color: #ea580c;
            background: linear-gradient(90deg, #fff7ed 0, #ffffff 36%);
        }}

        .area-chip {{
            display: inline-flex;
            align-items: center;
            min-height: 26px;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 700;
            color: #0f172a;
            background: rgba(255, 255, 255, 0.78);
            border: 1px solid rgba(148, 163, 184, 0.35);
            white-space: nowrap;
        }}

        .mini-metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(145px, 1fr));
            gap: 10px;
            margin-bottom: 14px;
        }}

        .mini-metric {{
            border: 1px solid rgba(148, 163, 184, 0.3);
            border-radius: 8px;
            padding: 10px 12px;
            background: rgba(255, 255, 255, 0.74);
        }}

        .mini-label {{
            color: #64748b;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
        }}

        .mini-value {{
            color: #0f172a;
            font-size: 20px;
            font-weight: 800;
            margin-top: 3px;
        }}

        .calc-table {{
            width: 100%;
            margin-top: 8px;
        }}

        .calc-table th {{
            background: rgba(241, 245, 249, 0.88);
        }}

        .compact-pre {{
            max-height: 170px;
            overflow: auto;
            white-space: pre-wrap;
            word-break: break-word;
            margin: 0;
        }}

        .grouped-requirements {{
            display: grid;
            gap: 14px;
        }}

        .empty-note {{
            color: #64748b;
            padding: 12px 0;
        }}

        @media (max-width: 720px) {{
            .calc-summary-grid {{
                grid-template-columns: 1fr;
            }}

            .area-card .area-head {{
                align-items: flex-start;
                flex-direction: column;
            }}
        }}

        @media (min-width: 721px) and (max-width: 1180px) {{
            .calc-summary-grid {{
                grid-template-columns: repeat(3, minmax(0, 1fr));
            }}
        }}
    </style>
</head>
<body>
{render_nav("calculation", user)}
<div class="container">
    <h1>Kết quả tính toán</h1>
    <div class="subtitle"></div>
    <div id="content"></div>

    <div class="actions">
        <a class="btn btn-secondary" href="/survey">Quay lại khảo sát</a>
        <a class="btn btn-secondary" href="/topology">V&#7869; topo gi&#7843;i ph&#225;p</a>
        <a class="btn btn-primary" href="/quote">Tiếp tục chọn model & xem báo giá</a>
    </div>
</div>

<script>
function esc(v) {{
    return String(v ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}}

function jsonBlock(v) {{
    return esc(JSON.stringify(v || {{}}, null, 2));
}}

function displayRequirement(req) {{
    const cleaned = {{ ...(req || {{}}) }};
    delete cleaned.default_model;
    delete cleaned.selection_source;
    delete cleaned.excel_range;
    delete cleaned.model_prefix;
    delete cleaned.model_contains;
    delete cleaned.dc_sdn_role;
    return cleaned;
}}

function money(v) {{
    return "$" + Number(v || 0).toLocaleString(undefined, {{
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }});
}}

function scrollToArea(id) {{
    const target = document.getElementById(id);
    if (!target) return;
    target.scrollIntoView({{ behavior: "smooth", block: "start" }});
}}

function normGroup(group) {{
    return String(group || "").trim().toLowerCase();
}}

function areaClass(group) {{
    const g = normGroup(group);
    if (g.includes("dc-sdn")) return "area-dc";
    if (g.includes("server farm")) return "area-server";
    if (g.includes("wan")) return "area-wan";
    return "area-campus";
}}

function areaLabel(group) {{
    const g = normGroup(group);
    if (g.includes("dc-sdn")) return "DC-SDN";
    if (g.includes("server farm")) return "Server Farm";
    if (g.includes("wan")) return "WAN";
    return "Campus";
}}

function renderRequirementTable(lines, emptyText) {{
    if (!lines.length) {{
        return `<div class="empty-note">${{esc(emptyText || "Không có requirement.")}}</div>`;
    }}

    return `
        <table class="calc-table">
            <thead>
                <tr>
                    <th>Group</th>
                    <th>Item Type</th>
                    <th>Quantity</th>
                    <th>Requirement</th>
                </tr>
            </thead>
            <tbody>
                ${{lines.map(line => `
                    <tr>
                        <td>${{esc(line.group)}}</td>
                        <td>${{esc(line.item_type)}}</td>
                        <td>${{esc(line.quantity)}}</td>
                        <td><pre class="compact-pre">${{jsonBlock(displayRequirement(line.requirement))}}</pre></td>
                    </tr>
                `).join("")}}
            </tbody>
        </table>
    `;
}}

function renderDcSdnBlock(dcSdn, dcLines) {{
    const enabled = dcSdn && dcSdn.enabled;

    if (!enabled && !dcLines.length) {{
        return `
            <div class="area-card area-dc area-jump" onclick="scrollToArea('dc-requirements')" role="button" tabindex="0">
                <div class="area-head">
                    <h2>DC-SDN</h2>
                    <span class="area-chip">Chưa bật</span>
                </div>
                <div class="area-body">
                    <div class="empty-note">DC-SDN đang tắt nên không sinh calculation, chọn thiết bị hoặc BOM riêng.</div>
                </div>
            </div>
        `;
    }}

    return `
        <div class="area-card area-dc area-jump" onclick="scrollToArea('dc-requirements')" role="button" tabindex="0">
            <div class="area-head">
                <h2>DC-SDN</h2>
                
            </div>
            
        </div>
    `;
}}

function renderBuildingTable(buildings) {{
    if (!buildings.length) {{
        return `<div class="empty-note">Không có dữ liệu tòa nhà.</div>`;
    }}

    return `
        <table class="calc-table">
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
                ${{buildings.map(b => `
                    <tr>
                        <td>${{esc(b.name)}}</td>
                        <td>${{esc(b.floors)}}</td>
                        <td>${{esc(b.area_per_floor)}}</td>
                        <td>${{esc(b.node_per_floor)}}</td>
                        <td>${{b.has_indoor_wifi ? "Y" : "N"}}</td>
                        <td><pre class="compact-pre">${{jsonBlock(b.switches)}}</pre></td>
                        <td>${{esc(b.indoor_ap)}}</td>
                    </tr>
                `).join("")}}
            </tbody>
        </table>
    `;
}}

function renderWanTable(wans) {{
    if (!wans.length) {{
        return `<div class="empty-note">Không có dữ liệu WAN.</div>`;
    }}

    return `
        <table class="calc-table">
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
                ${{wans.map(w => `
                    <tr>
                        <td>${{esc(w.name)}}</td>
                        <td>${{esc(w.users)}}</td>
                        <td>${{esc(w.bandwidth_mbps)}} Mbps</td>
                        <td>${{Number(w.wan_demand_mbps || 0).toFixed(2)}} Mbps</td>
                        <td>${{esc(w.router_size)}}</td>
                        <td>${{esc(w.node_count)}}</td>
                        <td>${{w.has_wifi ? "Y" : "N"}}</td>
                        <td>${{w.has_ha_gateway ? "Y" : "N"}}</td>
                        <td><pre class="compact-pre">${{jsonBlock({{
                            router_small: w.router_small_quantity || 0,
                            router_large: w.router_large_quantity || 0
                        }})}}</pre></td>
                        <td><pre class="compact-pre">${{jsonBlock(w.switches || {{}})}}</pre></td>
                        <td>${{esc(w.ap_quantity || 0)}}</td>
                        <td>${{esc(w.sfp_1g_quantity || 0)}}</td>
                    </tr>
                `).join("")}}
            </tbody>
        </table>
    `;
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
    const req = data.requirements || {{}};
    const requirements = req.requirements || [];
    const buildings = req.building_details || [];
    const wans = req.wan_details || [];
    const dcSdn = req.dc_sdn || {{}};
    const campusLines = requirements.filter(line => areaLabel(line.group) === "Campus");
    const serverLines = requirements.filter(line => areaLabel(line.group) === "Server Farm");
    const wanLines = requirements.filter(line => areaLabel(line.group) === "WAN");
    const dcLines = requirements.filter(line => areaLabel(line.group) === "DC-SDN");

    let html = `
        <div class="calc-layout">
            <div class="card calc-summary-card">
                <h2>Tổng quan kết quả</h2>
                <div class="calc-summary-grid">
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
                    <div class="metric">
                        <div class="metric-label">DC-SDN</div>
                        <div class="metric-value">${{dcSdn.enabled ? "Có" : "Không"}}</div>
                    </div>
                </div>
            </div>

            <div class="area-grid">
                <div class="area-card area-campus area-jump" onclick="scrollToArea('campus-requirements')" role="button" tabindex="0">
                    <div class="area-head">
                        <h2>Campus - Trụ sở chính</h2>
                    </div>
                    
                </div>

                <div class="area-card area-server area-jump" onclick="scrollToArea('server-requirements')" role="button" tabindex="0">
                    <div class="area-head">
                        <h2>Server Farm</h2>
                    </div>
                    
                </div>

                <div class="area-card area-wan area-jump" onclick="scrollToArea('wan-requirements')" role="button" tabindex="0">
                    <div class="area-head">
                        <h2>WAN</h2>
                    </div>
                    
                </div>

                ${{renderDcSdnBlock(dcSdn, dcLines)}}
            </div>

            <div class="area-card area-campus" id="campus-detail">
                <div class="area-head">
                    <h2>Chi tiết tính toán theo tòa nhà</h2>
                    <span class="area-chip">Campus</span>
                </div>
                <div class="area-body">${{renderBuildingTable(buildings)}}</div>
            </div>

            <div class="area-card area-wan" id="wan-detail">
                <div class="area-head">
                    <h2>Chi tiết tính toán WAN</h2>
                    <span class="area-chip">WAN</span>
                </div>
                <div class="area-body">${{renderWanTable(wans)}}</div>
            </div>

            <div class="card">
                <h2>Danh sách requirement kỹ thuật theo vùng</h2>
                <div class="grouped-requirements">
                    <div class="area-card area-campus" id="campus-requirements">
                        <div class="area-head">
                            <h3>Campus - Trụ sở chính</h3>
                        </div>
                        <div class="area-body">${{renderRequirementTable(campusLines, "Không có line Campus.")}}</div>
                    </div>
                    <div class="area-card area-server" id="server-requirements">
                        <div class="area-head">
                            <h3>Server Farm</h3>
                        </div>
                        <div class="area-body">${{renderRequirementTable(serverLines, "Không có line Server Farm.")}}</div>
                    </div>
                    <div class="area-card area-wan" id="wan-requirements">
                        <div class="area-head">
                            <h3>WAN</h3>
                        </div>
                        <div class="area-body">${{renderRequirementTable(wanLines, "Không có line WAN.")}}</div>
                    </div>
                    <div class="area-card area-dc" id="dc-requirements">
                        <div class="area-head">
                            <h3>DC-SDN</h3>
                            
                        </div>
                        <div class="area-body">${{renderRequirementTable(dcLines, "Không có line DC-SDN.")}}</div>
                    </div>
                </div>
            </div>
        </div>
    `;

    document.getElementById("content").innerHTML = html;
}}

render();
</script>
</body>
</html>
    """
