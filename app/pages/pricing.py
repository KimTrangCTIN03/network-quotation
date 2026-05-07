from app.pages.styles import BASE_STYLE, render_nav


def render_pricing_page(user=None):
    is_admin = bool(user and user.get("role") == "admin")
    list_price_disabled = "" if is_admin else "disabled"
    admin_tools_style = "" if is_admin else "display:none;"
    user_note_style = "display:none;" if is_admin else ""
    return f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="utf-8" />
    <title>Price Catalog</title>
    {BASE_STYLE}
    <style>
        .topbar {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 18px;
            margin-bottom: 16px;
        }}

        .search-row {{
            display: grid;
            grid-template-columns: 1fr 180px;
            gap: 10px;
            margin-bottom: 14px;
        }}

        .pricing-grid {{
            display: grid;
            grid-template-columns: minmax(0, 1fr) 340px;
            gap: 18px;
            align-items: start;
        }}

        .table-wrap {{
            overflow-y: auto;
            overflow-x: hidden;
            border: 1px solid #dbe3ef;
            border-radius: 12px;
            background: #fff;
            max-height: 680px;
        }}

        .price-table {{
            width: 100%;
            table-layout: fixed;
            font-size: 13px;
        }}

        .price-table th {{
            position: sticky;
            top: 0;
            z-index: 1;
        }}

        .price-table th,
        .price-table td {{
            padding: 10px 8px;
            overflow-wrap: anywhere;
        }}

        .price-table th:nth-child(1) {{ width: 34%; }}
        .price-table th:nth-child(2) {{ width: 14%; }}
        .price-table th:nth-child(3),
        .price-table th:nth-child(4),
        .price-table th:nth-child(5) {{ width: 17%; }}

        .price-table tbody tr {{
            cursor: pointer;
        }}

        .price-table tbody tr:hover td {{
            background: #f8fafc;
        }}

        .num {{
            text-align: right;
            white-space: normal;
        }}

        .model-cell {{
            font-weight: 800;
        }}

        .muted {{
            color: #64748b;
        }}

        input[type="file"] {{
            width: 100%;
            padding: 10px;
            border: 1px solid #cbd5e1;
            border-radius: 10px;
            background: #fff;
            font-size: 13px;
        }}

        @media (max-width: 1000px) {{
            .topbar,
            .pricing-grid,
            .search-row {{
                display: grid;
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
{render_nav("pricing", user)}
<div class="container">
    <div class="topbar">
        <div>
            <div class="actions" style="margin-top:0;">
                <a class="btn btn-secondary" href="/dashboard">Dashboard</a>
                <a class="btn btn-secondary" href="/survey">Tính toán giải pháp</a>
            </div>
            <h1>Catalog giá thiết bị</h1>
            <div class="subtitle"></div>
        </div>
        <div class="card" style="min-width:280px; margin-bottom:0;">
            <div class="metric-label">Số thiết bị đang hiển thị</div>
            <div id="visibleCount" class="metric-value">0</div>
            <div id="totalCount" class="small"></div>
        </div>
    </div>

    <div class="pricing-grid">
        <div class="card">
            <div class="search-row">
                <input id="searchInput" type="text" placeholder="Tìm mã thiết bị hoặc hãng, ví dụ Cisco, Juniper, C9200, EX4300..." oninput="debouncedLoadPrices()" />
                <button class="btn btn-primary" type="button" onclick="loadPrices()">Tìm kiếm</button>
            </div>

            <div id="priceBlock">
                <div class="empty-state">Đang tải catalog giá...</div>
            </div>
        </div>

        <div>
            <div class="card">
                <div class="section-title" style="margin-top:0;">AM nhập giá thiết bị</div>
                <label>Hãng</label>
                <input id="amVendor" type="text" placeholder="Cisco, Juniper, ..." value="Cisco" />
                <div style="height:10px;"></div>
                <label>Mã thiết bị</label>
                <input id="amModel" type="text" placeholder="C8200L-1N-4T" />
                <div style="height:10px;"></div>
                <label>List Price ($)</label>
                <input id="listPrice" type="number" placeholder="26000" {list_price_disabled} />
                <div style="height:10px;"></div>
                <label>Giá AM ($)</label>
                <input id="amPrice" type="number" placeholder="18000" />
                <div class="small">List Price và Giá AM được lưu riêng. Để trống hoặc nhập 0 ở ô nào thì xóa giá nhập tay của ô đó.</div>
                <div class="actions">
                    <button class="btn btn-primary" type="button" onclick="saveAmPrice()">Lưu giá</button>
                </div>
                <div id="successBox" class="success-box"></div>
                <div id="errorBox" class="error-box"></div>
            </div>

            <div class="card" style="{admin_tools_style}">
                <div class="section-title" style="margin-top:0;">Import giá từ BOM</div>
                <label>Hãng</label>
                <input id="importVendor" type="text" placeholder="Cisco, Juniper, ..." value="Cisco" />
                <div style="height:10px;"></div>
                <label>File price</label>
                <input id="bomFile" type="file" accept=".xlsx,.xlsm" />
                <div class="actions">
                    <button class="btn btn-secondary" type="button" onclick="importAmPrices()">Import</button>
                </div>
                <div class="small">File import có 3 cột: Device, List Price và AM Price</div>
            </div>
            
        </div>
    </div>
</div>

<script>
let searchTimer = null;
const IS_ADMIN = {str(is_admin).lower()};

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

function showError(message) {{
    const el = document.getElementById("errorBox");
    el.style.display = "block";
    el.innerText = message;
}}

function showSuccess(message) {{
    const el = document.getElementById("successBox");
    el.style.display = "block";
    el.innerText = message;
}}

function clearMessage() {{
    document.getElementById("errorBox").style.display = "none";
    document.getElementById("successBox").style.display = "none";
}}

function debouncedLoadPrices() {{
    clearTimeout(searchTimer);
    searchTimer = setTimeout(loadPrices, 250);
}}

async function loadPrices() {{
    const q = document.getElementById("searchInput").value.trim();
    const res = await fetch(`/api/prices?q=${{encodeURIComponent(q)}}&limit=0`);

    if (!res.ok) {{
        document.getElementById("priceBlock").innerHTML = `<div class="error-box" style="display:block;">Không tải được catalog giá.</div>`;
        return;
    }}

    const data = await res.json();
    renderPrices(data.rows || [], data.total_count || 0);
}}

function renderPrices(rows, totalCount) {{
    document.getElementById("visibleCount").innerText = rows.length;
    document.getElementById("totalCount").innerText = "";

    if (!rows.length) {{
        document.getElementById("priceBlock").innerHTML = `<div class="empty-state">Không tìm thấy thiết bị phù hợp.</div>`;
        return;
    }}


    document.getElementById("priceBlock").innerHTML = `
        <div class="table-wrap">
            <table class="price-table">
                <thead>
                    <tr>
                        <th>Mã thiết bị</th>
                        <th>Hãng</th>
                        <th>List Price</th>
                        <th>Giá AM</th>
                        <th>Final Price</th>
                    </tr>
                </thead>
                <tbody>
                    ${{rows.map(row => `
                        <tr onclick="pickModel('${{esc(row.vendor)}}', '${{esc(row.model)}}', ${{Number(row.list_price || 0)}}, ${{Number(row.am_price || 0)}})">
                            <td class="model-cell">${{esc(row.model)}}</td>
                            <td>${{esc(row.vendor)}}</td>
                            <td class="num">${{row.list_price ? money(row.list_price) : '<span class="muted">-</span>'}}</td>
                            <td class="num">${{row.am_price ? money(row.am_price) : '<span class="muted">-</span>'}}</td>
                            <td class="num"><strong>${{money(row.final_price)}}</strong></td>
                        </tr>
                    `).join("")}}
                </tbody>
            </table>
        </div>
    `;
}}

function pickModel(vendor, model, listPrice, amPrice) {{
    document.getElementById("amVendor").value = vendor || "Cisco";
    document.getElementById("amModel").value = model;
    document.getElementById("listPrice").value = listPrice || "";
    document.getElementById("amPrice").value = amPrice || "";
    clearMessage();
}}

async function saveAmPrice() {{
    clearMessage();
    const vendor = document.getElementById("amVendor").value.trim() || "Cisco";
    const model = document.getElementById("amModel").value.trim();
    const list_price = IS_ADMIN ? Number(document.getElementById("listPrice").value || 0) : null;
    const price = Number(document.getElementById("amPrice").value || 0);

    const res = await fetch("/api/prices/am", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{ vendor, model, list_price, price }})
    }});

    if (!res.ok) {{
        showError(await res.text());
        return;
    }}

    showSuccess("Đã lưu giá AM.");
    await loadPrices();
}}

async function submitImport(confirmOverwrite = false) {{
    clearMessage();
    const file = document.getElementById("bomFile").files[0];

    if (!file) {{
        showError("Vui lòng chọn file BOM.");
        return;
    }}

    const vendor = document.getElementById("importVendor").value.trim() || "Cisco";
    const form = new FormData();
    form.append("file", file);
    form.append("vendor", vendor);
    form.append("confirm_overwrite", confirmOverwrite ? "true" : "false");

    const res = await fetch("/api/import-am-prices", {{ method: "POST", body: form }});

    if (!res.ok) {{
        showError(await res.text());
        return;
    }}

    const data = await res.json();

    if (data.template_error) {{
        showError(data.message || "File import chưa đúng định dạng 3 cột.");
        return;
    }}

    if (data.requires_confirmation) {{
        const sample = (data.conflicts || [])
            .slice(0, 8)
            .map(item => `${{item.model}}: List ${{money(item.old_list_price)}} -> ${{money(item.new_list_price)}}, AM ${{money(item.old_am_price)}} -> ${{money(item.new_am_price)}}`)
            .join("\\n");
        const ok = window.confirm(`File có ${{data.conflict_count || 0}} part number trùng giá đang có. Bạn có muốn thay thế giá cũ không?\\n\\n${{sample}}`);

        if (!ok) {{
            showError("Đã hủy import để không ghi đè giá cũ.");
            return;
        }}

        return submitImport(true);
    }}

    showSuccess(`Đã import ${{data.imported_count || 0}} dòng: ${{data.list_price_count || 0}} List Price, ${{data.am_price_count || 0}} Giá AM.`);
    await loadPrices();
}}

async function importAmPrices() {{
    return submitImport(false);
}}

loadPrices();
</script>
</body>
</html>
    """
