from app.pages.styles import BASE_STYLE, render_nav


def render_bom_page(
    user=None,
    *,
    storage_key: str = "quoteData",
    nav_active: str = "bom",
    title: str = "Xuất BOM",
    empty_message: str = "Chua co du lieu bao gia de xuat BOM.",
    single_option: bool = False,
    download_prefix: str = "network_bom",
):
    single_option_js = "true" if single_option else "false"
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
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 14px;
            margin-bottom: 16px;
        }}
        .bom-metric {{
            background: #f8fafc;
            border: 1px solid #dbe3ef;
            border-radius: 12px;
            padding: 18px;
            min-height: 122px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}

        .bom-metric.dc-sdn-metric {{
            background: linear-gradient(135deg, #fff7ed 0%, #ffffff 72%);
            border-color: #fed7aa;
        }}

        .bom-metric .label {{
            color: #64748b;
            font-size: 14px;
        }}

        .bom-metric .value {{
            margin-top: 8px;
            font-size: 28px;
            font-weight: 800;
            line-height: 1.15;
        }}

        .bom-toolbar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            flex-wrap: wrap;
            margin-bottom: 12px;
        }}

        .bom-toolbar h3 {{
            margin: 0;
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
            margin-right: 10px;
        }}

        .solution-label.dc {{
            background: #fff7ed;
            color: #9a3412;
        }}

        .cache-pill {{
            display: inline-flex;
            align-items: center;
            min-height: 28px;
            padding: 4px 10px;
            border-radius: 999px;
            border: 1px solid #cbd5e1;
            background: #f8fafc;
            color: #475569;
            font-size: 12px;
            font-weight: 700;
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

        @media (max-width: 1180px) {{
            .bom-summary {{
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }}
        }}

        @media (max-width: 640px) {{
            .bom-summary {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
{render_nav(nav_active, user)}
<div class="container">
    <h1>{title}</h1>
    <div id="bom_block"></div>
</div>

<script>
let currentBom = null;
let activeOption = "opt1";
let bomLoadedFromCache = false;
const BOM_CACHE_VERSION = "v3";
const BOM_STORAGE_KEY = "{storage_key}";
const BOM_EMPTY_MESSAGE = "{empty_message}";
const BOM_SINGLE_OPTION = {single_option_js};
const BOM_DOWNLOAD_PREFIX = "{download_prefix}";

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

function quoteHash(raw) {{
    let hash = 2166136261;
    for (let i = 0; i < raw.length; i += 1) {{
        hash ^= raw.charCodeAt(i);
        hash = Math.imul(hash, 16777619);
    }}
    return (hash >>> 0).toString(16);
}}

function bomCacheKey(raw) {{
    return `bomData:${{BOM_CACHE_VERSION}}:${{quoteHash(raw || "")}}`;
}}

function clearOldBomCaches(activeKey) {{
    for (let i = localStorage.length - 1; i >= 0; i -= 1) {{
        const key = localStorage.key(i);
        if (key && key.startsWith("bomData:") && key !== activeKey) {{
            localStorage.removeItem(key);
        }}
    }}
}}

function readCachedBom(raw) {{
    const key = bomCacheKey(raw);
    try {{
        const cached = JSON.parse(localStorage.getItem(key) || "null");
        if (!cached || !cached.bom) return null;
        return cached.bom;
    }} catch (error) {{
        localStorage.removeItem(key);
        return null;
    }}
}}

function writeCachedBom(raw, bom) {{
    const key = bomCacheKey(raw);
    try {{
        localStorage.setItem(key, JSON.stringify({{ bom, saved_at: new Date().toISOString() }}));
        clearOldBomCaches(key);
    }} catch (error) {{
        clearOldBomCaches(key);
    }}
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

async function loadBom(forceRefresh = false) {{
    const raw = localStorage.getItem(BOM_STORAGE_KEY);

    if (!raw) {{
        document.getElementById("bom_block").innerHTML = `
            <div class="card">
                <div class="empty-state">${{esc(BOM_EMPTY_MESSAGE)}}</div>
            </div>
        `;
        return;
    }}

    if (!forceRefresh) {{
        const cachedBom = readCachedBom(raw);
        if (cachedBom) {{
            currentBom = cachedBom;
            bomLoadedFromCache = true;
            renderBom();
            return;
        }}
    }}

    bomLoadedFromCache = false;
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
                    <div class="error-box" style="display:block;">Khong tao duoc BOM: ${{esc(text)}}</div>
                </div>
            `;
            return;
        }}

        currentBom = await res.json();
        writeCachedBom(raw, currentBom);
        renderBom();
    }} catch (error) {{
        document.getElementById("bom_block").innerHTML = `
            <div class="card">
                <div class="error-box" style="display:block;">Khong tao duoc BOM. Vui long thu lai.</div>
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
    const optionKeys = BOM_SINGLE_OPTION ? [activeOption].filter(opt => summary[opt]) : Object.keys(summary);

    return `
        <div class="bom-summary">
            ${{optionKeys.map(opt => `
                <div class="bom-metric ${{opt === "dc_sdn" ? "dc-sdn-metric" : ""}}">
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
    const optionKeys = Object.keys(options);
    if (!options[activeOption] && optionKeys.length) {{
        activeOption = optionKeys[0];
    }}
    const option = options[activeOption] || {{ rows: [], total: 0, label: activeOption }};
    const visibleOptionKeys = BOM_SINGLE_OPTION ? [activeOption].filter(opt => options[opt]) : optionKeys;

    document.getElementById("bom_block").innerHTML = `
        <div class="group-summary-card">
            <div class="bom-toolbar">
                <h3>Tổng quan BOM</h3>
                
            </div>
            ${{renderSummary()}}
        </div>

        <div class="group-summary-card">
            ${{BOM_SINGLE_OPTION ? "" : `
            <div class="bom-tabs">
                ${{visibleOptionKeys.map(opt => `
                    <button class="bom-tab ${{activeOption === opt ? "active" : ""}}" type="button" onclick="setOption('${{opt}}')">
                        ${{esc(options[opt]?.label || opt)}}
                    </button>
                `).join("")}}
            </div>
            `}}
            <div style="display:flex; justify-content:space-between; align-items:center; gap:12px; flex-wrap:wrap;">
                <h3>
                    <span class="solution-label ${{activeOption === "dc_sdn" ? "dc" : ""}}">${{activeOption === "dc_sdn" ? "Giải pháp DC-SDN" : "Giải pháp Campus"}}</span>
                    ${{esc(option.label)}} - ${{money(option.total || 0)}}
                </h3>
                <button id="downloadBomBtn" class="btn btn-primary" type="button" onclick="downloadBom()">Download BOM</button>
            </div>
            <div id="downloadStatus" class="small" style="margin:8px 0 12px;"></div>
            ${{renderRows(option.rows || [])}}
        </div>
    `;
}}

async function downloadBom() {{
    const raw = localStorage.getItem(BOM_STORAGE_KEY);
    const optionKey = activeOption;
    const btn = document.getElementById("downloadBomBtn");
    const status = document.getElementById("downloadStatus");

    if (!raw) return;
    if (status) {{
        status.style.color = "#475569";
        status.innerText = "Đang xuất BOM, vui lòng đợi...";
    }}

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
        a.download = `${{BOM_DOWNLOAD_PREFIX}}_${{optionKey || "all"}}.xlsx`;
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
