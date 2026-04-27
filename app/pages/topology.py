import base64
import json
from pathlib import Path

from app.pages.styles import BASE_STYLE, render_nav


ICON_ROOT = Path(__file__).resolve().parent.parent.parent / "icon-library" / "project-topology-icons"
ICON_FILES = {
    "router": "network-core/router.png",
    "gateway-router": "network-core/gateway-router.png",
    "wan-router": "network-core/wan-router.png",
    "firewall": "security/firewall.png",
    "core": "network-core/core-switch-modular.png",
    "core-switch": "network-core/core-switch.png",
    "spine-core": "network-core/spine-switch.png",
    "leaf": "network-core/leaf-switch.png",
    "access-switch": "network-core/access-switch.png",
    "ap-indoor": "wireless/access-point-indoor.png",
    "ap-outdoor": "wireless/access-point-outdoor.png",
    "server": "datacenter/server.png",
    "storage": "datacenter/storage.png",
    "internet": "wan/internet-cloud.png",
    "wan-cloud": "wan/wan-cloud.png",
    "users": "location/branch-office.png",
}


def icon_data_urls() -> str:
    icons = {}
    fallback = ICON_ROOT / "network-core" / "router.png"

    for key, relative_path in ICON_FILES.items():
        path = ICON_ROOT / relative_path
        if not path.exists():
            path = fallback
        if path.exists():
            payload = base64.b64encode(path.read_bytes()).decode("ascii")
            icons[key] = f"data:image/png;base64,{payload}"

    return json.dumps(icons)


TOPOLOGY_PAGE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="utf-8" />
    <title>Topology - Network Quotation</title>
    __BASE_STYLE__
    <style>
        .topology-toolbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
            margin-bottom: 16px;
        }

        .topology-actions {
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }

        .topology-grid {
            display: grid;
            grid-template-columns: minmax(0, 1fr) minmax(300px, 340px);
            gap: 18px;
            align-items: start;
        }

        .canvas-card,
        .sidebar-card {
            background: #fff;
            border: 1px solid #dbe3ef;
            border-radius: 16px;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
        }

        .canvas-card {
            padding: 18px;
            min-width: 0;
        }

        .sidebar-card {
            padding: 18px;
            position: sticky;
            top: 16px;
        }

        .canvas-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
            margin-bottom: 12px;
        }

        .topology-canvas-wrap {
            border: 1px solid #dbe3ef;
            border-radius: 14px;
            overflow: scroll;
            background: #fff;
            cursor: grab;
            height: calc(100vh - 250px);
            min-height: 560px;
            max-height: calc(100vh - 250px);
            overscroll-behavior: contain;
            touch-action: none;
        }

        .topology-canvas-wrap.panning {
            cursor: grabbing;
        }

        #topologyCanvas {
            width: 2200px;
            height: 1420px;
            display: block;
            background-color: #ffffff;
            background-image:
                linear-gradient(#edf2f7 1px, transparent 1px),
                linear-gradient(90deg, #edf2f7 1px, transparent 1px),
                linear-gradient(#dbe3ef 1px, transparent 1px),
                linear-gradient(90deg, #dbe3ef 1px, transparent 1px);
            background-size: 16px 16px, 16px 16px, 80px 80px, 80px 80px;
        }

        .zone-box {
            fill: transparent;
            stroke: #94a3b8;
            stroke-width: 1.15;
            stroke-dasharray: 10 8;
        }

        .zone-title {
            font: 800 18px Arial, sans-serif;
            fill: #0f172a;
        }

        .topo-link {
            stroke: #475569;
            stroke-width: 2;
            fill: none;
        }

        .topo-link.cross {
            stroke-width: 1.7;
        }

        .topo-node {
            cursor: move;
        }

        .topo-node.dragging {
            opacity: 0.72;
        }

        .node-hitbox {
            fill: transparent;
            stroke: none;
            pointer-events: all;
        }

        .node-title {
            font: 800 10px Arial, sans-serif;
            fill: #0f172a;
        }

        .node-desc {
            font: 8px Arial, sans-serif;
            fill: #475569;
        }

        .node-qty {
            font: 800 8px Arial, sans-serif;
            fill: #1d4ed8;
        }

        .ha-link {
            stroke: #334155;
            stroke-width: 1.8;
            stroke-dasharray: 4 3;
        }

        .ha-label {
            font: 800 9px Arial, sans-serif;
            fill: #0f172a;
            paint-order: stroke;
            stroke: #ffffff;
            stroke-width: 3px;
            stroke-linejoin: round;
        }

        .sidebar-title {
            font-size: 18px;
            font-weight: 800;
            margin-bottom: 14px;
            color: #0f172a;
        }

        .topo-table-wrap {
            max-height: calc(100vh - 250px);
            overflow: auto;
            border: 1px solid #dbe3ef;
            border-radius: 12px;
        }

        .topo-table {
            width: 100%;
            border-collapse: collapse;
        }

        .topo-table th,
        .topo-table td {
            border: 1px solid #dbe3ef;
            font-size: 12px;
            padding: 8px;
            text-align: left;
            vertical-align: top;
        }

        .topo-table th {
            background: #f8fafc;
            font-weight: 800;
            position: sticky;
            top: 0;
            z-index: 1;
        }

        .building-zone-box,
        .wan-site-zone-box {
            fill: #eff6ff;
            fill-opacity: 0.48;
            stroke: #cbd5e1;
            stroke-width: 1;
            stroke-dasharray: 6 5;
        }

        .wan-site-zone-box {
            fill: #ecfdf5;
            stroke: #86efac;
        }

        .building-zone-title,
        .wan-site-zone-title {
            font: 800 12px Arial, sans-serif;
            fill: #334155;
        }

        @media (max-width: 640px) {
            .topology-grid {
                grid-template-columns: 1fr;
            }

            .sidebar-card {
                position: static;
            }

            .topology-canvas-wrap {
                height: 70vh;
                max-height: 70vh;
            }

            .topo-table-wrap {
                max-height: 320px;
            }
        }
    </style>
</head>
<body>
__NAV__
<div class="container">
    <div class="topology-toolbar">
        <div>
            <h1>Topo</h1>
        </div>
        <div class="topology-actions">
            <button class="btn btn-secondary" type="button" onclick="exportPng()">Xuất ảnh</button>
            <a class="btn btn-primary" href="/quote" onclick="saveTopologyLayout(false)">Chọn model</a>
        </div>
    </div>

    <div id="message"></div>

    <div class="topology-grid">
        <div class="canvas-card">
            <div class="canvas-header">
                <div class="section-title" style="margin:0;">Sơ đồ tổng quan</div>
            </div>

            <div class="topology-actions" style="justify-content:flex-end;margin-bottom:10px;">
                <button class="btn btn-secondary" type="button" onclick="focusZone('all')">Toàn bộ</button>
                <button class="btn btn-secondary" type="button" onclick="focusZone('campus')">Tòa nhà</button>
                <button class="btn btn-secondary" type="button" onclick="focusZone('serverFarm')">Server Farm</button>
                <button class="btn btn-secondary" type="button" onclick="focusZone('wan')">WAN</button>
            </div>

            <div class="topology-canvas-wrap">
                <svg id="topologyCanvas" viewBox="0 0 2200 2200" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"></svg>
            </div>
        </div>

        <div class="sidebar-card">
            <div class="sidebar-title">Danh sách thiết bị</div>
            <div class="topo-table-wrap">
                <table class="topo-table">
                    <thead>
                        <tr>
                            <th>Group</th>
                            <th>Item Type</th>
                            <th>Qty</th>
                        </tr>
                    </thead>
                    <tbody id="requirementRows"></tbody>
                </table>
            </div>
        </div>
    </div>
</div>

<script>
const ICONS = __ICON_DATA__;
const CANVAS_W = 2200;
const CANVAS_H = 2200;
const STORAGE_KEY = "topologyLayout:fixed-tier-v5";

const NODE_W = 132;
const NODE_H = 100;
const ICON = 100 ;
const CLUSTER_ICON = 70;
const ENDPOINT_ICON = 64;
const TEXT_Y = {
    title: 80,
    desc: 90,
    qty: 100
};
const MIN_X_GAP = 36;
const MIN_Y_GAP = 0;
const ZONE_MARGIN = 35;

let topologyLines = [];
let topologyMeta = {
    buildings: [],
    wanSites: []
};
let nodes = [];
let links = [];
let dragState = null;
let panState = null;
let zoom = 1;
let topologyView = "overview";

const ZONES = {
    campus: {
        title: "Campus - Trụ sở chính",
        x: 20,
        y: 30,
        w: 830,
        h: 1220
    },
    serverFarm: {
        title: "Server Farm",
        x: 880,
        y: 220,
        w: 1180,
        h: 660
    },
    wan: {
        title: "WAN",
        x: 180,
        y: 1320,
        w: 1880,
        h: 780
    }
};

const LAYOUT = {
    internet:       { x: 380,  y: 80, zone: "campus" },
    gatewayRouter:  { x: 380,  y: 180, zone: "campus" },

    firewall:       { x: 380,  y: 300, zone: "campus" },

    core:           { x: 380,  y: 430, zone: "campus" },

    access48:       { x: 150,  y: 590, zone: "campus" },
    access24:       { x: 330,  y: 590, zone: "campus" },
    access16:       { x: 510,  y: 590, zone: "campus" },
    access8:        { x: 690,  y: 590, zone: "campus" },

    apIndoor:       { x: 240,  y: 730, zone: "campus" },
    apOutdoor:      { x: 430,  y: 730, zone: "campus" },
    campusUsers:    { x: 620,  y: 730, zone: "campus" },

    buildingAccess1:{ x: 150,  y: 590, zone: "campus" },
    buildingAp1:    { x: 150,  y: 710, zone: "campus" },
    buildingUsers1: { x: 95,   y: 790, zone: "campus" },
    buildingUsers1b:{ x: 205,  y: 790, zone: "campus" },
    buildingAccess2:{ x: 370,  y: 590, zone: "campus" },
    buildingAp2:    { x: 370,  y: 710, zone: "campus" },
    buildingUsers2: { x: 315,  y: 790, zone: "campus" },
    buildingUsers2b:{ x: 425,  y: 790, zone: "campus" },
    buildingAccess3:{ x: 590,  y: 590, zone: "campus" },
    buildingAp3:    { x: 590,  y: 710, zone: "campus" },
    buildingUsers3: { x: 535,  y: 790, zone: "campus" },
    buildingUsers3b:{ x: 645,  y: 790, zone: "campus" },

    sfSpine:        { x: 1300, y: 360, zone: "serverFarm" },

    sfLeaf100:      { x: 1030, y: 530, zone: "serverFarm" },
    sfLeaf10Sfp:    { x: 1230, y: 530, zone: "serverFarm" },
    sfLeaf10Rj45:   { x: 1430, y: 530, zone: "serverFarm" },
    sfLeaf1Sfp:     { x: 1830, y: 530, zone: "serverFarm" },
    sfLeaf1Rj45:    { x: 1630, y: 530, zone: "serverFarm" },

    sfServer1:      { x: 1030, y: 700, zone: "serverFarm" },
    sfServer2:      { x: 1230, y: 700, zone: "serverFarm" },
    sfServer3:      { x: 1430, y: 700, zone: "serverFarm" },
    sfServer4:      { x: 1630, y: 700, zone: "serverFarm" },
    sfServer5:      { x: 1830, y: 700, zone: "serverFarm" },

    wanCloud:       { x: 380,  y: 980, zone: "wan" },
    wanRouter:      { x: 600,  y: 980, zone: "wan" },

    wanAccessBranch1:{ x: 860,  y: 990,  zone: "wan" },
    wanApBranch1:   { x: 1130, y: 990,  zone: "wan" },
    wanUsersBranch1:{ x: 1360, y: 990,  zone: "wan" },
    wanAccessBranch2:{ x: 860,  y: 1160, zone: "wan" },
    wanApBranch2:   { x: 1130, y: 1160, zone: "wan" },
    wanUsersBranch2:{ x: 1360, y: 1160, zone: "wan" },

    wanAccess48:    { x: 850,  y: 1040, zone: "wan" },
    wanAccess24:    { x: 1050, y: 1040, zone: "wan" },
    wanAccess16:    { x: 1250, y: 1040, zone: "wan" },
    wanAccess8:     { x: 1450, y: 1040, zone: "wan" },

    wanAp:          { x: 1650, y: 1040, zone: "wan" },
    wanUsers:       { x: 1850, y: 1040, zone: "wan" },
    wanUsers2:      { x: 1850, y: 950, zone: "wan" },
    wanUsers3:      { x: 1850, y: 1130, zone: "wan" },

    wanAp1:         { x: 850,  y: 1140, zone: "wan" },
    wanBranchUsers1:{ x: 850,  y: 1220, zone: "wan" },
    wanAp2:         { x: 1050, y: 1140, zone: "wan" },
    wanBranchUsers2:{ x: 1050, y: 1220, zone: "wan" },
    wanAp3:         { x: 1250, y: 1140, zone: "wan" },
    wanBranchUsers3:{ x: 1250, y: 1220, zone: "wan" },
    wanAp4:         { x: 1450, y: 1140, zone: "wan" },
    wanBranchUsers4:{ x: 1450, y: 1220, zone: "wan" }
};

const SAMPLE_LINES = [
    { group: "Campus - Trụ sở chính", item_type: "Gateway Router", quantity: 2 },
    { group: "Campus - Trụ sở chính", item_type: "Firewall", quantity: 2 },
    { group: "Campus - Trụ sở chính", item_type: "Core Switch Modular", quantity: 2 },
    { group: "Campus - Trụ sở chính", item_type: "Access Switch 48x1GE RJ45", quantity: 6 },
    { group: "Campus - Trụ sở chính", item_type: "Access Switch 24x1GE RJ45", quantity: 3 },
    { group: "Campus - Trụ sở chính", item_type: "Access Point indoor (kèm Power Injector)", quantity: 51 },
    { group: "Campus - Trụ sở chính", item_type: "Access Point outdoor (kèm Power Injector)", quantity: 2 },
    { group: "Campus - Trụ sở chính", item_type: "SFP 10G", quantity: 18 },
    { group: "Campus - Trụ sở chính", item_type: "SFP 1G", quantity: 53 },

    { group: "Server Farm", item_type: "Core Switch (hoặc Spine Switch)", quantity: 2 },
    { group: "Server Farm", item_type: "Access Switch 100G (hoặc Leaf Switch)", quantity: 2 },
    { group: "Server Farm", item_type: "Access Switch 48x10G SFP (hoặc Leaf Switch)", quantity: 2 },
    { group: "Server Farm", item_type: "Access Switch 48x10G RJ45 (hoặc Leaf Switch)", quantity: 2 },
    { group: "Server Farm", item_type: "Access Switch 48x1G RJ45 (hoặc Leaf Switch)", quantity: 2 },
    { group: "Server Farm", item_type: "Server Farm Resources", quantity: 1 },
    { group: "Server Farm", item_type: "SFP 100G", quantity: 8 },
    { group: "Server Farm", item_type: "SFP 10G", quantity: 6 },

    { group: "WAN", item_type: "WAN Router loại vừa/nhỏ", quantity: 5 },
    { group: "WAN", item_type: "Access Switch 48x1GE RJ45", quantity: 2 },
    { group: "WAN", item_type: "Access Switch 24x1GE RJ45", quantity: 3 },
    { group: "WAN", item_type: "Access Point indoor (kèm Power Injector)", quantity: 4 },
    { group: "WAN", item_type: "SFP 1G", quantity: 5 }
];

function esc(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;");
}

function canonical(text) {
    return String(text || "").toLowerCase();
}

function normalizeTopologyLines(rawLines) {
    return (rawLines || [])
        .map(line => ({
            group: String(line.group || line.group_name || line.solution_group || ""),
            item_type: String(line.item_type || line.item_name || line.name || line.description || ""),
            quantity: parseQuantity(line.quantity ?? line.qty ?? line.count ?? line.amount ?? 0),
            selected: line.selected || {}
        }))
        .filter(line => line.quantity > 0);
}

function parseQuantity(value) {
    if (typeof value === "number") return value;
    const parsed = Number(String(value || "0").replaceAll(",", "").trim());
    return Number.isFinite(parsed) ? parsed : 0;
}

function isSfp(line) {
    return canonical(line.item_type).includes("sfp");
}

function detectNodeType(line) {
    const group = canonical(line.group);
    const item = canonical(line.item_type);

    if (isSfp(line)) return "";

    if (group.includes("server farm")) {
        if (item.includes("core") || item.includes("spine")) return "sfSpine";
        if (item.includes("100g")) return "sfLeaf100";
        if (item.includes("48x10g sfp")) return "sfLeaf10Sfp";
        if (item.includes("48x10g rj45")) return "sfLeaf10Rj45";
        if (item.includes("48x1g sfp")) return "sfLeaf1Sfp";
        if (item.includes("48x1g rj45")) return "sfLeaf1Rj45";
        if (item.includes("server")) return "sfServer";
        if (item.includes("access") || item.includes("leaf")) return "sfLeaf10Sfp";
        return "";
    }

    if (group.includes("wan")) {
        if (item.includes("router") && (item.includes("vừa") || item.includes("nhỏ"))) return "wanRouterSmall";
        if (item.includes("router")) return "wanRouterLarge";
        if (item.includes("48x1ge")) return "wanAccess48";
        if (item.includes("24x1ge")) return "wanAccess24";
        if (item.includes("16x1ge")) return "wanAccess16";
        if (item.includes("8x1ge")) return "wanAccess8";
        if (item.includes("access point")) return "wanAp";
        return "";
    }

    if (item.includes("gateway") || item.includes("router")) return "gatewayRouter";
    if (item.includes("firewall")) return "firewall";
    if (item.includes("core")) return "campusCore";
    if (item.includes("48x1ge")) return "access48";
    if (item.includes("24x1ge")) return "access24";
    if (item.includes("16x1ge")) return "access16";
    if (item.includes("8x1ge")) return "access8";
    if (item.includes("outdoor")) return "apOutdoor";
    if (item.includes("access point")) return "apIndoor";

    return "";
}

function addAggregate(map, key, qty) {
    if (!key || qty <= 0) return;
    map[key] = (map[key] || 0) + qty;
}

function aggregateTopologyNodes(lines) {
    const aggregate = {};
    lines.forEach(line => addAggregate(aggregate, detectNodeType(line), line.quantity));
    normalizeBackboneAggregate(aggregate);
    return aggregate;
}

function normalizeBackboneAggregate(aggregate) {
    const hasCampusDownstream = Boolean(
        aggregate.access48 || aggregate.access24 || aggregate.access16 || aggregate.access8 ||
        aggregate.apIndoor || aggregate.apOutdoor
    );
    const hasServerFarm = Boolean(
        aggregate.sfSpine || aggregate.sfLeaf100 || aggregate.sfLeaf10Sfp ||
        aggregate.sfLeaf10Rj45 || aggregate.sfLeaf1Sfp || aggregate.sfLeaf1Rj45 || aggregate.sfServer
    );
    const hasWan = Boolean(
        aggregate.wanRouterSmall || aggregate.wanRouterLarge || aggregate.wanAccess48 ||
        aggregate.wanAccess24 || aggregate.wanAccess16 || aggregate.wanAccess8 || aggregate.wanAp
    );
    const needsBackbone = aggregate.gatewayRouter || aggregate.firewall || hasCampusDownstream || hasServerFarm || hasWan;

    if (needsBackbone && !aggregate.campusCore) aggregate.campusCore = 2;
    if ((aggregate.campusCore || needsBackbone) && !aggregate.firewall) aggregate.firewall = 2;
    if ((aggregate.firewall || aggregate.campusCore || needsBackbone) && !aggregate.gatewayRouter) aggregate.gatewayRouter = 2;
}

function sfpQty(groupNeedle, speed) {
    return topologyLines
        .filter(line => canonical(line.group).includes(groupNeedle))
        .filter(line => isSfp(line) && canonical(line.item_type).includes(speed))
        .reduce((sum, line) => sum + line.quantity, 0);
}

function linkLabel(base, groupNeedle, speed) {
    return sfpQty(groupNeedle, speed) > 0
        ? `${base} / SFP ${speed.toUpperCase()}`
        : base;
}

function createNodeAt(id, title, desc, qty, type, icon, pos, options = {}) {
    if (!qty || qty <= 0) return null;

    return {
        id,
        title,
        desc,
        qty,
        type,
        icon,
        zone: pos.zone,
        x: pos.x,
        y: pos.y,
        baseX: pos.x,
        baseY: pos.y,
        isCluster: Boolean(options.isCluster),
        hideQty: Boolean(options.hideQty) || type === "cloud"
    };
}

function createNode(id, title, desc, qty, type, icon, posKey, options = {}) {
    return createNodeAt(id, title, desc, qty, type, icon, LAYOUT[posKey], options);
}

function switchQtyFromBuilding(building) {
    const switches = building.switches || {};
    return Object.values(switches).reduce((sum, value) => sum + parseQuantity(value), 0);
}

function nodeQtyFromBuilding(building) {
    const explicitNodes = parseQuantity(building.node_count ?? building.nodes ?? building.users ?? 0);
    if (explicitNodes) return explicitNodes;

    const floors = parseQuantity(building.floors ?? 1) || 1;
    const nodePerFloor = parseQuantity(building.node_per_floor ?? 0);

    return floors * nodePerFloor;
}

function dynamicBuildingPosition(index, part) {
    const columns = topologyView === "building" ? 4 : 3;
    const col = index % columns;
    const row = Math.floor(index / columns);
    const x = (topologyView === "building" ? 75 : 105) + col * 205;
    const y = 590 + row * 310;

    const offsets = {
        access: { x: 55, y: 0 },
        ap: { x: 55, y: 105 },
        users: { x: 0, y: 180 },
        usersB: { x: 110, y: 180 }
    };

    const offset = offsets[part] || { x: 0, y: 0 };
    return { x: x + offset.x, y: y + offset.y, zone: "campus" };
}

function visibleBuildingIds() {
    return nodes
        .filter(node => node.id.startsWith("buildingAccess"))
        .map(node => node.id)
        .sort((a, b) => Number(a.replace("buildingAccess", "")) - Number(b.replace("buildingAccess", "")));
}

function dynamicWanPosition(index, part) {
    const row = index;
    const y = (topologyView === "wan" ? 1080 : 990) + row * 170;
    const offsets = {
        access: { x: topologyView === "wan" ? 960 : 860, y: 0 },
        ap: { x: topologyView === "wan" ? 1190 : 1130, y: 0 },
        users: { x: topologyView === "wan" ? 1390 : 1360, y: 0 }
    };

    const offset = offsets[part] || { x: 0, y: 0 };
    return { x: offset.x, y: y + offset.y, zone: "wan" };
}

function visibleWanAccessIds() {
    return nodes
        .filter(node => node.id.startsWith("wanAccessBranch"))
        .map(node => node.id)
        .sort((a, b) => Number(a.replace("wanAccessBranch", "")) - Number(b.replace("wanAccessBranch", "")));
}

function normalizeBuildingDetails(rawBuildings) {
    return (rawBuildings || [])
        .map((building, index) => ({
            name: String(building.name || `Tòa nhà ${index + 1}`),
            accessQty: switchQtyFromBuilding(building),
            apQty: parseQuantity(building.indoor_ap ?? building.ap_quantity ?? building.apIndoor ?? 0),
            userQty: nodeQtyFromBuilding(building),
            raw: building
        }))
        .filter(building => building.accessQty || building.apQty || building.userQty);
}

function visibleBuildings() {
    const buildings = topologyMeta.buildings || [];
    return topologyView === "building" ? buildings : buildings.slice(0, 3);
}

function normalizeWanDetails(rawSites) {
    return (rawSites || [])
        .map((site, index) => {
            const switches = site.switches || {};
            const accessQty = Object.values(switches).reduce((sum, value) => sum + parseQuantity(value), 0);

            return {
                name: String(site.name || `WAN ${index + 1}`),
                routerQty: parseQuantity(site.router_quantity ?? 1),
                accessQty,
                apQty: parseQuantity(site.ap_quantity ?? 0),
                userQty: parseQuantity(site.node_count ?? site.users ?? 0),
                raw: site
            };
        })
        .filter(site => site.routerQty || site.accessQty || site.apQty || site.userQty);
}

function visibleWanSites() {
    const sites = topologyMeta.wanSites || [];
    return topologyView === "wan" ? sites : sites.slice(0, 2);
}

function updateZonesForView() {
    const buildingRows = Math.max(1, Math.ceil(visibleBuildings().length / 3));
    const wanRows = Math.max(1, visibleWanSites().length || 1);

    ZONES.campus.h = topologyView === "building"
        ? Math.max(870, 590 + buildingRows * 310)
        : 870;

    ZONES.wan.y = topologyView === "building"
        ? Math.max(930, ZONES.campus.y + ZONES.campus.h + 30)
        : 930;
    ZONES.wan.h = topologyView === "wan"
        ? Math.max(440, 250 + wanRows * 170)
        : 440;
}

function buildCampus(agg) {
    const result = [];
    const buildings = visibleBuildings();

    if (agg.gatewayRouter) {
        result.push(createNode("internet", "Internet", "ISP / WAN", 1, "cloud", "internet", "internet"));
    }

    result.push(createNode(
        "gatewayRouter",
        agg.gatewayRouter >= 2 ? "Router HA" : "Router",
        agg.gatewayRouter >= 2 ? "Gateway Pair" : "Campus Gateway",
        agg.gatewayRouter,
        "router",
        "gateway-router",
        "gatewayRouter",
        { isCluster: agg.gatewayRouter >= 2 }
    ));

    if (agg.firewall >= 2) {
        result.push(createNode("firewallCluster", "Firewall HA", "Security Cluster", agg.firewall, "firewall", "firewall", "firewall", { isCluster: true }));
    } else {
        result.push(createNode("firewall", "Firewall", "Security", agg.firewall, "firewall", "firewall", "firewall"));
    }

    if (agg.campusCore >= 2) {
        result.push(createNode("coreCluster", "Core Switch HQ", "Campus Core Pair", agg.campusCore, "core", "core", "core", { isCluster: true }));
    } else {
        result.push(createNode("core", "Core Switch HQ", "Campus Core", agg.campusCore, "core", "core", "core"));
    }

    if (buildings.length) {
        buildings.forEach((building, index) => {
            const idx = index + 1;
            result.push(createNodeAt(`buildingAccess${idx}`, "Access", building.name, building.accessQty || 1, "access", "access-switch", dynamicBuildingPosition(index, "access")));
            if (building.apQty) {
                result.push(createNodeAt(`buildingAp${idx}`, "AP Indoor", "Wireless", building.apQty, "ap", "ap-indoor", dynamicBuildingPosition(index, "ap")));
            }
            result.push(createNodeAt(`buildingUsers${idx}`, "Users", "Endpoints", building.userQty || 1, "endpoint", "users", dynamicBuildingPosition(index, "users")));
            result.push(createNodeAt(`buildingUsers${idx}b`, "Users", "Guest / IoT", 1, "endpoint", "users", dynamicBuildingPosition(index, "usersB")));
        });
    } else {
        result.push(createNode("access48", "Access", "48GE RJ45", agg.access48, "access", "access-switch", "access48"));
        result.push(createNode("access24", "Access", "24GE RJ45", agg.access24, "access", "access-switch", "access24"));
        result.push(createNode("access16", "Access", "16GE RJ45", agg.access16, "access", "access-switch", "access16"));
        result.push(createNode("access8", "Access", "8GE RJ45", agg.access8, "access", "access-switch", "access8"));

        result.push(createNode("apIndoor", "AP Indoor", "Wireless", agg.apIndoor, "ap", "ap-indoor", "apIndoor"));
        result.push(createNode("apOutdoor", "AP Outdoor", "Wireless", agg.apOutdoor, "ap", "ap-outdoor", "apOutdoor"));

        if (agg.access48 || agg.access24 || agg.access16 || agg.access8 || agg.apIndoor || agg.apOutdoor) {
            result.push(createNode("campusUsers", "Users", "Endpoints", 1, "endpoint", "users", "campusUsers"));
        }
    }

    return result.filter(Boolean);
}

function buildServerFarm(agg) {
    const result = [];

    if (agg.sfSpine >= 2) {
        result.push(createNode("spineCluster", "Spine HA", "Data Center Spine Pair", agg.sfSpine, "core", "spine-core", "sfSpine", { isCluster: true }));
    } else {
        result.push(createNode("spine", "Spine/Core", "Server Farm", agg.sfSpine, "core", "spine-core", "sfSpine"));
    }

    const leafDefs = [
        ["sfLeaf100", "Leaf", "100G", agg.sfLeaf100, "sfServer1", "Server", "Application", "server"],
        ["sfLeaf10Sfp", "Leaf", "48x10G SFP", agg.sfLeaf10Sfp, "sfServer2", "Storage", "Storage / DB", "storage"],
        ["sfLeaf10Rj45", "Leaf", "48x10G RJ45", agg.sfLeaf10Rj45, "sfServer3", "Server", "Compute", "server"],
        ["sfLeaf1Rj45", "Leaf", "48x1G RJ45", agg.sfLeaf1Rj45, "sfServer4", "Server", "Database", "server"],
        ["sfLeaf1Sfp", "Leaf", "48x1G SFP", agg.sfLeaf1Sfp, "sfServer5", "Storage", "Backup", "storage"]
    ];

    leafDefs.forEach(([leafId, title, desc, qty]) => {
        result.push(createNode(leafId, title, desc, qty, "access", "leaf", leafId));
    });

    leafDefs.forEach(([leafId, , , qty, serverId, serverTitle, serverDesc, serverIcon]) => {
        if (qty > 0) {
            result.push(createNode(serverId, serverTitle, serverDesc, 1, "server", serverIcon, serverId));
        }
    });

    if (agg.sfSpine && !leafDefs.some(([, , , qty]) => qty > 0)) {
        result.push(createNode("sfServer1", "Server", "Application", 1, "server", "server", "sfServer1"));
    }

    return result.filter(Boolean);
}

function buildWan(agg) {
    const result = [];
    const wanSites = visibleWanSites();
    const wanRouterQty = (agg.wanRouterSmall || 0) + (agg.wanRouterLarge || 0);
    const wanAccessQty = (agg.wanAccess48 || 0) + (agg.wanAccess24 || 0) + (agg.wanAccess16 || 0) + (agg.wanAccess8 || 0);
    const hasWan = wanRouterQty || wanAccessQty || agg.wanAp;

    if (hasWan) {
        result.push(createNode("wanCloud", "WAN Cloud", "Carrier WAN", 1, "cloud", "wan-cloud", "wanCloud"));
    }

    result.push(createNode(
        wanRouterQty >= 2 ? "wanRouterCluster" : "wanRouter",
        wanRouterQty >= 2 ? "WAN Router Cluster" : "WAN Router",
        wanRouterQty >= 2 ? "Hub-Spoke Routers" : "Branch Gateway",
        wanRouterQty,
        "router",
        "wan-router",
        "wanRouter",
        { isCluster: wanRouterQty >= 2, hideQty: wanRouterQty >= 2 }
    ));

    if (wanSites.length) {
        wanSites.forEach((site, index) => {
            const idx = index + 1;
            result.push(createNodeAt(`wanAccessBranch${idx}`, "WAN Access", site.name, site.accessQty || 1, "access", "access-switch", dynamicWanPosition(index, "access")));
            result.push(createNodeAt(`wanApBranch${idx}`, "WAN AP", "Wireless", site.apQty || 1, "ap", "ap-indoor", dynamicWanPosition(index, "ap")));
            result.push(createNodeAt(`wanUsersBranch${idx}`, "Branch Users", site.name, site.userQty || 1, "endpoint", "users", dynamicWanPosition(index, "users")));
        });
    } else {
        const branchCount = wanRouterQty >= 2 ? 2 : (hasWan ? 1 : 0);
        const accessPerBranch = Math.max(1, Math.ceil((wanAccessQty || branchCount) / Math.max(branchCount, 1)));
        const apPerBranch = Math.max(1, Math.ceil((agg.wanAp || branchCount) / Math.max(branchCount, 1)));

        for (let idx = 1; idx <= branchCount; idx += 1) {
            const remainingAccess = Math.max(1, (wanAccessQty || branchCount) - accessPerBranch * (idx - 1));
            const remainingAp = Math.max(1, (agg.wanAp || branchCount) - apPerBranch * (idx - 1));
            const index = idx - 1;

            result.push(createNodeAt(`wanAccessBranch${idx}`, "WAN Access", `Site ${idx}`, Math.min(accessPerBranch, remainingAccess), "access", "access-switch", dynamicWanPosition(index, "access")));
            result.push(createNodeAt(`wanApBranch${idx}`, "WAN AP", "Wireless", Math.min(apPerBranch, remainingAp), "ap", "ap-indoor", dynamicWanPosition(index, "ap")));
            result.push(createNodeAt(`wanUsersBranch${idx}`, "Branch Users", `Site ${idx}`, 1, "endpoint", "users", dynamicWanPosition(index, "users")));
        }
    }

    return result.filter(Boolean);
}

function nodeBox(node) {
    return {
        x: node.x,
        y: node.y,
        w: NODE_W,
        h: 116
    };
}

function boxesOverlap(a, b, gapX = MIN_X_GAP, gapY = MIN_Y_GAP) {
    return !(
        a.x + a.w + gapX <= b.x ||
        b.x + b.w + gapX <= a.x ||
        a.y + a.h + gapY <= b.y ||
        b.y + b.h + gapY <= a.y
    );
}

function clampNodeToZone(node) {
    node.x = Math.max(8, Math.min(CANVAS_W - NODE_W - 8, node.x));
    node.y = Math.max(8, Math.min(CANVAS_H - NODE_H - 8, node.y));
}

function avoidNodeOverlap() {
    nodes.forEach(clampNodeToZone);

    const grouped = {};
    nodes.forEach(node => {
        if (!grouped[node.zone]) grouped[node.zone] = [];
        grouped[node.zone].push(node);
    });

    Object.keys(grouped).forEach(zoneKey => {
        const zoneNodes = grouped[zoneKey];
        const zone = ZONES[zoneKey];
        if (!zone) return;

        for (let pass = 0; pass < 24; pass += 1) {
            for (let i = 0; i < zoneNodes.length; i += 1) {
                for (let j = i + 1; j < zoneNodes.length; j += 1) {
                    const a = zoneNodes[i];
                    const b = zoneNodes[j];

                    if (!boxesOverlap(nodeBox(a), nodeBox(b))) continue;

                    b.x += NODE_W + MIN_X_GAP;

                    if (b.x + NODE_W > zone.x + zone.w - ZONE_MARGIN) {
                        b.x = Math.max(zone.x + ZONE_MARGIN, a.x - NODE_W - MIN_X_GAP);
                    }

                    clampNodeToZone(b);
                    b.y = b.baseY;
                }
            }
        }
    });
}

function nodeExists(id) {
    return nodes.some(node => node.id === id);
}

function addLink(result, from, to, label, cross = false) {
    if (nodeExists(from) && nodeExists(to)) {
        result.push({
            from,
            to,
            label,
            cross
        });
    }
}

function addBusLink(result, from, targets, label, options = {}) {
    const source = nodes.find(node => node.id === from);
    const existingTargets = targets
        .map(id => nodes.find(node => node.id === id))
        .filter(Boolean);

    if (!source || !existingTargets.length) return;

    result.push({
        from,
        targets: existingTargets.map(node => node.id),
        label,
        bus: true,
        orientation: options.orientation || "auto"
    });
}

function firstExisting(ids) {
    return ids.find(nodeExists);
}

function buildCampusLinks() {
    const result = [];
    const firewallId = firstExisting(["firewallCluster", "firewall"]);
    const coreId = firstExisting(["coreCluster", "core"]);
    const buildingAccessIds = visibleBuildingIds();
    const accessIds = ["access48", "access24", "access16", "access8"].filter(nodeExists);
    const apIds = ["apIndoor", "apOutdoor"].filter(nodeExists);

    if (nodeExists("internet") && nodeExists("gatewayRouter")) {
        addLink(result, "internet", "gatewayRouter", "Internet");
    }

    if (nodeExists("gatewayRouter") && firewallId) {
        addLink(result, "gatewayRouter", firewallId, "HSRP / VRRP");
    }

    if (firewallId && coreId) {
        addLink(result, firewallId, coreId, "OSPF / BGP");
    } else if (nodeExists("gatewayRouter") && coreId) {
        addLink(result, "gatewayRouter", coreId, "OSPF / BGP");
    }

    if (coreId && buildingAccessIds.length) {
        addBusLink(result, coreId, buildingAccessIds, "LACP / 10G", {
            orientation: "vertical"
        });
    }

    buildingAccessIds.forEach(access => {
        const idx = Number(access.replace("buildingAccess", ""));
        const buildingAp = `buildingAp${idx}`;
        const buildingUsers = [`buildingUsers${idx}`, `buildingUsers${idx}b`].filter(nodeExists);

        if (nodeExists(buildingAp)) {
            addLink(result, access, buildingAp, "1G PoE");
            if (buildingUsers.length) {
                addBusLink(result, buildingAp, buildingUsers, "Wi-Fi", {
                    orientation: "vertical"
                });
            }
        } else if (buildingUsers.length) {
            addBusLink(result, access, buildingUsers, "1G", {
                orientation: "vertical"
            });
        }
    });

    if (coreId && accessIds.length) {
        addBusLink(result, coreId, accessIds, "LACP / 10G", {
            orientation: "vertical"
        });
    }

    apIds.forEach((ap, index) => {
        const access = accessIds[index % Math.max(accessIds.length, 1)];
        if (access) {
            addLink(result, access, ap, index === 0 ? "1G PoE" : "");
        }
    });

    if (accessIds.length && nodeExists("campusUsers")) {
        addLink(result, accessIds[accessIds.length - 1], "campusUsers", linkLabel("1G", "campus", "1g"));
    }

    apIds.forEach((ap, index) => {
        addLink(result, ap, "campusUsers", index === 0 ? "Wi-Fi" : "");
    });

    return result;
}

function buildServerFarmLinks() {
    const result = [];
    const campusCore = firstExisting(["coreCluster", "core"]);
    const spine = firstExisting(["spineCluster", "spine"]);
    const leaves = ["sfLeaf100", "sfLeaf10Sfp", "sfLeaf10Rj45", "sfLeaf1Rj45", "sfLeaf1Sfp"].filter(nodeExists);

    if (campusCore && spine) {
        addLink(result, campusCore, spine, "10G uplink / LACP");
    }

    if (spine && leaves.length) {
        addBusLink(result, spine, leaves, "10G / 100G", {
            orientation: "vertical"
        });
    }

    const serverIds = ["sfServer1", "sfServer2", "sfServer3", "sfServer4", "sfServer5"].filter(nodeExists);
    const leafServerMap = {
        sfLeaf100: "sfServer1",
        sfLeaf10Sfp: "sfServer2",
        sfLeaf10Rj45: "sfServer3",
        sfLeaf1Rj45: "sfServer4",
        sfLeaf1Sfp: "sfServer5"
    };

    if (leaves.length) {
        leaves.forEach(leaf => {
            const server = leafServerMap[leaf];
            if (server && nodeExists(server)) {
                addLink(result, leaf, server, "");
            }
        });
    } else if (spine && serverIds.length) {
        serverIds.forEach(server => {
            addLink(result, spine, server, "");
        });
    }

    return result;
}

function buildWanLinks() {
    const result = [];
    const wanRouter = firstExisting(["wanRouterCluster", "wanRouter"]);
    const wanAccess = visibleWanAccessIds();
    const campusEdge = firstExisting(["coreCluster", "core"]);

    if (campusEdge && nodeExists("wanCloud")) {
        addLink(result, campusEdge, "wanCloud", "MPLS / SD-WAN");
    } else if (campusEdge && wanRouter) {
        addLink(result, campusEdge, wanRouter, "MPLS / SD-WAN");
    }

    if (wanRouter && nodeExists("wanCloud")) {
        addLink(result, "wanCloud", wanRouter, "IPsec VPN");
    }

    if (wanRouter && wanAccess.length) {
        addBusLink(result, wanRouter, wanAccess, linkLabel("1G", "wan", "1g"), {
            orientation: "horizontal"
        });
    }

    if (wanAccess.length) {
        wanAccess.forEach(accessId => {
            const idx = Number(accessId.replace("wanAccessBranch", ""));
            const apId = `wanApBranch${idx}`;
            const userId = `wanUsersBranch${idx}`;

            if (nodeExists(apId)) {
                addLink(result, accessId, apId, "");
                if (nodeExists(userId)) {
                    addLink(result, apId, userId, "");
                }
            } else if (nodeExists(userId)) {
                addLink(result, accessId, userId, "");
            }
        });
    } else if (wanAccess.length && nodeExists("wanAp")) {
        addLink(result, wanAccess[wanAccess.length - 1], "wanAp", "1G PoE");

        const branchUsers = ["wanUsers", "wanUsers2", "wanUsers3"].filter(nodeExists);
        if (branchUsers.length) {
            addBusLink(result, "wanAp", branchUsers, "Wi-Fi", {
                orientation: "horizontal"
            });
        }
    }

    return result;
}

function buildTopology(lines) {
    const aggregate = aggregateTopologyNodes(lines);

    updateZonesForView();

    nodes = [
        ...buildCampus(aggregate),
        ...buildServerFarm(aggregate),
        ...buildWan(aggregate)
    ];

    avoidNodeOverlap();

    links = [
        ...buildCampusLinks(),
        ...buildServerFarmLinks(),
        ...buildWanLinks()
    ];
}

function renderZone(zone) {
    return `
        <g>
            <rect class="zone-box" x="${zone.x}" y="${zone.y}" width="${zone.w}" height="${zone.h}" rx="20" fill="transparent" stroke="#94a3b8" stroke-width="1.15" stroke-dasharray="10 8"></rect>
            <text class="zone-title" x="${zone.x + 18}" y="${zone.y + 30}">${esc(zone.title)}</text>
        </g>
    `;
}

function renderBuildingZone(building, index) {
    const access = nodes.find(node => node.id === `buildingAccess${index + 1}`);
    if (!access) return "";

    const width = 176;
    const height = 300;
    const x = access.x - 22;
    const y = access.y - 36;

    return `
        <g>
            <rect class="building-zone-box" x="${x}" y="${y}" width="${width}" height="${height}" rx="14" fill="#eff6ff" fill-opacity="0.48" stroke="#cbd5e1" stroke-width="1" stroke-dasharray="6 5"></rect>
            <text class="building-zone-title" x="${x + 12}" y="${y + 20}">${esc(building.name)}</text>
        </g>
    `;
}

function renderBuildingZones() {
    return visibleBuildings().map(renderBuildingZone).join("");
}

function renderWanSiteZone(index) {
    const access = nodes.find(node => node.id === `wanAccessBranch${index}`);
    if (!access) return "";

    const x = access.x - 34;
    const y = access.y - 38;
    const width = 690;
    const height = 132;

    return `
        <g>
            <rect class="wan-site-zone-box" x="${x}" y="${y}" width="${width}" height="${height}" rx="14" fill="#ecfdf5" fill-opacity="0.48" stroke="#86efac" stroke-width="1" stroke-dasharray="6 5"></rect>
            <text class="wan-site-zone-title" x="${x + 12}" y="${y + 20}">WAN Site ${index}</text>
        </g>
    `;
}

function renderWanSiteZones() {
    return nodes
        .filter(node => node.id.startsWith("wanAccessBranch"))
        .map((_, index) => renderWanSiteZone(index + 1))
        .join("");
}

function renderZones() {
    return Object.values(ZONES).map(renderZone).join("") + renderBuildingZones() + renderWanSiteZones();
}

function center(node) {
    const bounds = getNodeIconBounds(node);

    return {
        x: bounds.x + bounds.w / 2,
        y: bounds.y + bounds.h / 2
    };
}

function getNodeIconBounds(node) {
    if (node.type === "endpoint") {
        return {
            x: node.x,
            y: node.y + 3,
            w: ENDPOINT_ICON,
            h: ENDPOINT_ICON
        };
    }

    if (node.isCluster) {
        const leftX = 4;
        const rightX = NODE_W - CLUSTER_ICON - 4;
        const iconY = 4;
        return {
            x: node.x + leftX,
            y: node.y + iconY,
            w: rightX - leftX + CLUSTER_ICON,
            h: CLUSTER_ICON
        };
    }

    return {
        x: node.x + (NODE_W - ICON) / 2,
        y: node.y,
        w: ICON,
        h: ICON
    };
}

function getNodeAnchorPoint(node, side) {
    const bounds = getNodeIconBounds(node);
    const inset = node.isCluster ? 7 : 18;

    if (side === "top") return { x: bounds.x + bounds.w / 2, y: bounds.y + inset };
    if (side === "right") return { x: bounds.x + bounds.w - inset, y: bounds.y + bounds.h / 2 };
    if (side === "bottom") return { x: bounds.x + bounds.w / 2, y: bounds.y + bounds.h - inset };
    return { x: bounds.x + inset, y: bounds.y + bounds.h / 2 };
}

function edgePoint(from, to) {
    const a = center(from);
    const b = center(to);
    const dx = b.x - a.x;
    const dy = b.y - a.y;

    if (Math.abs(dx) > Math.abs(dy)) {
        return {
            from: getNodeAnchorPoint(from, dx > 0 ? "right" : "left"),
            to: getNodeAnchorPoint(to, dx > 0 ? "left" : "right")
        };
    }

    return {
        from: getNodeAnchorPoint(from, dy > 0 ? "bottom" : "top"),
        to: getNodeAnchorPoint(to, dy > 0 ? "top" : "bottom")
    };
}

function orthogonalPath(from, to) {
    const pts = edgePoint(from, to);
    const a = pts.from;
    const b = pts.to;

    if (Math.abs(a.x - b.x) < 24 || Math.abs(a.y - b.y) < 24) {
        return `M ${a.x} ${a.y} L ${b.x} ${b.y}`;
    }

    const midX = (a.x + b.x) / 2;
    return `M ${a.x} ${a.y} L ${midX} ${a.y} L ${midX} ${b.y} L ${b.x} ${b.y}`;
}

function labelBox(x, y, width) {
    return {
        x: x - width / 2,
        y: y - 14,
        w: width,
        h: 20
    };
}

function labelOverlapsNode(box) {
    return nodes.some(node => boxesOverlap(box, nodeBox(node), 12, 12));
}

function getLinkLabelPosition(link, from, to, width) {
    const pts = edgePoint(from, to);
    const a = pts.from;
    const b = pts.to;

    let x = (a.x + b.x) / 2;
    let y = (a.y + b.y) / 2;

    if (Math.abs(a.x - b.x) < 32) {
        x += 44;
    } else if (Math.abs(a.y - b.y) < 32) {
        y -= 28;
    } else {
        y -= 28;
    }

    let box = labelBox(x, y, width);

    if (labelOverlapsNode(box)) {
        y -= 38;
        box = labelBox(x, y, width);
    }

    if (labelOverlapsNode(box)) {
        y += 76;
        box = labelBox(x, y, width);
    }

    return {
        x,
        y
    };
}

function renderLink(link) {
    if (link.bus) return renderBusLink(link);

    const from = nodes.find(node => node.id === link.from);
    const to = nodes.find(node => node.id === link.to);

    if (!from || !to) return "";

    const path = `
        <path class="topo-link ${link.cross ? "cross" : ""}" d="${orthogonalPath(from, to)}"></path>
    `;

    return path;
}

function renderBusLink(link) {
    const from = nodes.find(node => node.id === link.from);
    const targets = (link.targets || [])
        .map(id => nodes.find(node => node.id === id))
        .filter(Boolean);

    if (!from || !targets.length) return "";

    const sourceCenter = center(from);
    const targetCenters = targets.map(center);
    const vertical = link.orientation === "vertical" || (
        link.orientation === "auto" &&
        Math.abs(sourceCenter.y - targetCenters[0].y) > Math.abs(sourceCenter.x - targetCenters[0].x)
    );

    let bus = "";
    let labelX = sourceCenter.x;
    let labelY = sourceCenter.y;

    if (vertical) {
        const targetYsBelow = targetCenters[0].y >= sourceCenter.y;
        const fromPoint = getNodeAnchorPoint(from, targetYsBelow ? "bottom" : "top");
        const targetAnchors = targets.map(target => getNodeAnchorPoint(target, targetYsBelow ? "top" : "bottom"));
        const nearestTargetY = targetYsBelow
            ? Math.min(...targetAnchors.map(point => point.y))
            : Math.max(...targetAnchors.map(point => point.y));
        const gap = nearestTargetY - fromPoint.y;
        const trunkY = fromPoint.y + gap * 0.55;
        const minX = Math.min(...targetCenters.map(point => point.x), fromPoint.x);
        const maxX = Math.max(...targetCenters.map(point => point.x), fromPoint.x);

        bus += `M ${fromPoint.x} ${fromPoint.y} L ${fromPoint.x} ${trunkY}`;
        bus += ` M ${minX} ${trunkY} L ${maxX} ${trunkY}`;

        targetAnchors.forEach(anchor => {
            bus += ` M ${anchor.x} ${trunkY} L ${anchor.x} ${anchor.y}`;
        });

        labelX = fromPoint.x;
        labelY = trunkY - 8;
    } else {
        const fromPoint = getNodeAnchorPoint(from, targetCenters[0].x >= sourceCenter.x ? "right" : "left");
        const targetsRight = targetCenters[0].x >= sourceCenter.x;
        const targetAnchors = targets.map(target => getNodeAnchorPoint(target, targetsRight ? "left" : "right"));
        const nearestTargetX = targetsRight
            ? Math.min(...targetAnchors.map(point => point.x))
            : Math.max(...targetAnchors.map(point => point.x));
        const gap = nearestTargetX - fromPoint.x;
        const trunkX = fromPoint.x + gap * 0.55;
        const minY = Math.min(...targetCenters.map(point => point.y), fromPoint.y);
        const maxY = Math.max(...targetCenters.map(point => point.y), fromPoint.y);

        bus += `M ${fromPoint.x} ${fromPoint.y} L ${trunkX} ${fromPoint.y}`;
        bus += ` M ${trunkX} ${minY} L ${trunkX} ${maxY}`;

        targetAnchors.forEach(anchor => {
            bus += ` M ${trunkX} ${anchor.y} L ${anchor.x} ${anchor.y}`;
        });

        labelX = trunkX;
        labelY = fromPoint.y - 8;
    }

    return `<path class="topo-link" d="${bus}"></path>`;
}

function getIconForType(node) {
    return ICONS[node.icon] || ICONS.router || "";
}

function renderSingleNode(node) {
    const icon = getIconForType(node);
    const qty = node.hideQty ? "" : `<text class="node-qty" x="${NODE_W / 2}" y="${TEXT_Y.qty}" text-anchor="middle">Qty: ${Number(node.qty || 0).toLocaleString()}</text>`;

    if (node.type === "endpoint") {
        const endpointTextX = 58;
        const endpointQty = node.hideQty ? "" : `<text class="node-qty" x="${endpointTextX}" y="58" text-anchor="start">Qty: ${Number(node.qty || 0).toLocaleString()}</text>`;

        return `
            <g class="topo-node" data-id="${node.id}" transform="translate(${node.x}, ${node.y})">
                <title>Kéo để di chuyển thiết bị</title>
                <rect class="node-hitbox" x="0" y="0" width="146" height="${NODE_H}"></rect>
                <image href="${icon}" xlink:href="${icon}" x="0" y="8" width="${ENDPOINT_ICON}" height="${ENDPOINT_ICON}" preserveAspectRatio="xMidYMid meet"></image>
                <text class="node-title" x="${endpointTextX}" y="30" text-anchor="start">${esc(node.title)}</text>
                <text class="node-desc" x="${endpointTextX}" y="44" text-anchor="start">${esc(node.desc)}</text>
                ${endpointQty}
            </g>
        `;
    }

    return `
        <g class="topo-node" data-id="${node.id}" transform="translate(${node.x}, ${node.y})">
            <title>Kéo để di chuyển thiết bị</title>
            <rect class="node-hitbox" x="0" y="0" width="${NODE_W}" height="${NODE_H}"></rect>
            <image href="${icon}" xlink:href="${icon}" x="${(NODE_W - ICON) / 2}" y="0" width="${ICON}" height="${ICON}" preserveAspectRatio="xMidYMid meet"></image>
            <text class="node-title" x="${NODE_W / 2}" y="${TEXT_Y.title}" text-anchor="middle">${esc(node.title)}</text>
            <text class="node-desc" x="${NODE_W / 2}" y="${TEXT_Y.desc}" text-anchor="middle">${esc(node.desc)}</text>
            ${qty}
        </g>
    `;
}

function renderClusterNode(node) {
    const icon = getIconForType(node);
    const qty = node.hideQty ? "" : `<text class="node-qty" x="${NODE_W / 2}" y="${TEXT_Y.qty}" text-anchor="middle">Qty: ${Number(node.qty || 0).toLocaleString()}</text>`;
    const leftX = 4;
    const rightX = NODE_W - CLUSTER_ICON - 4;
    const iconY = 4;
    const linkY = iconY + CLUSTER_ICON / 2;

    return `
        <g class="topo-node" data-id="${node.id}" transform="translate(${node.x}, ${node.y})">
            <title>KÃ©o Ä‘á»ƒ di chuyá»ƒn cá»¥m thiáº¿t bá»‹</title>
            <rect class="node-hitbox" x="0" y="0" width="${NODE_W}" height="${NODE_H}"></rect>
            <line class="ha-link" x1="${leftX + CLUSTER_ICON}" y1="${linkY}" x2="${rightX}" y2="${linkY}"></line>
            <image href="${icon}" xlink:href="${icon}" x="${leftX}" y="${iconY}" width="${CLUSTER_ICON}" height="${CLUSTER_ICON}" preserveAspectRatio="xMidYMid meet"></image>
            <image href="${icon}" xlink:href="${icon}" x="${rightX}" y="${iconY}" width="${CLUSTER_ICON}" height="${CLUSTER_ICON}" preserveAspectRatio="xMidYMid meet"></image>
            <text class="ha-label" x="${NODE_W / 2}" y="${linkY - 5}" text-anchor="middle">HA</text>
            <text class="node-title" x="${NODE_W / 2}" y="${TEXT_Y.title}" text-anchor="middle">${esc(node.title)}</text>
            <text class="node-desc" x="${NODE_W / 2}" y="${TEXT_Y.desc}" text-anchor="middle">${esc(node.desc)}</text>
            ${qty}
        </g>
    `;
}

function renderNode(node) {
    return node.isCluster ? renderClusterNode(node) : renderSingleNode(node);
}

function renderTopology() {
    const svg = document.getElementById("topologyCanvas");

    svg.innerHTML = renderZones() + links.map(renderLink).join("") + nodes.map(renderNode).join("");

    svg.querySelectorAll(".topo-node").forEach(el => {
        el.addEventListener("pointerdown", startDrag);
    });

    applyZoom();
}

function svgPoint(event) {
    const svg = document.getElementById("topologyCanvas");
    const point = svg.createSVGPoint();

    point.x = event.clientX;
    point.y = event.clientY;

    return point.matrixTransform(svg.getScreenCTM().inverse());
}

function startDrag(event) {
    const id = event.currentTarget.dataset.id;
    const node = nodes.find(item => item.id === id);
    const point = svgPoint(event);

    dragState = {
        id,
        offsetX: point.x - node.x,
        offsetY: point.y - node.y
    };

    event.currentTarget.classList.add("dragging");
    event.currentTarget.setPointerCapture(event.pointerId);
    event.stopPropagation();
}

function drag(event) {
    if (!dragState) return;

    const node = nodes.find(item => item.id === dragState.id);
    const point = svgPoint(event);

    node.x = Math.max(8, Math.min(CANVAS_W - NODE_W - 8, point.x - dragState.offsetX));
    node.y = Math.max(8, Math.min(CANVAS_H - NODE_H - 8, point.y - dragState.offsetY));

    clampNodeToZone(node);
    renderTopology();
}

function stopDrag() {
    const shouldSave = Boolean(dragState);

    document.querySelectorAll(".topo-node.dragging").forEach(node => {
        node.classList.remove("dragging");
    });

    dragState = null;

    if (shouldSave) {
        saveTopologyLayout(false);
    }
}

function startPan(event) {
    if (event.target.closest(".topo-node")) return;

    const wrap = document.querySelector(".topology-canvas-wrap");

    panState = {
        x: event.clientX,
        y: event.clientY,
        left: wrap.scrollLeft,
        top: wrap.scrollTop
    };

    wrap.classList.add("panning");
    event.preventDefault();
}

function panCanvas(event) {
    if (!panState || dragState) return;

    const wrap = document.querySelector(".topology-canvas-wrap");

    wrap.scrollLeft = panState.left - (event.clientX - panState.x);
    wrap.scrollTop = panState.top - (event.clientY - panState.y);
}

function stopPan() {
    const wrap = document.querySelector(".topology-canvas-wrap");

    if (wrap) {
        wrap.classList.remove("panning");
    }

    panState = null;
}

function applyZoom() {
    const svg = document.getElementById("topologyCanvas");

    svg.style.width = `${CANVAS_W * zoom}px`;
    svg.style.height = `${CANVAS_H * zoom}px`;
}

function setZoom(value) {
    zoom = Math.max(0.25, Math.min(2.5, value));
    applyZoom();
}

function contentBox() {
    if (!nodes.length) {
        return { x: 0, y: 0, w: CANVAS_W, h: CANVAS_H };
    }

    const margin = 42;
    const minX = Math.max(0, Math.min(...nodes.map(node => node.x)) - margin);
    const minY = Math.max(0, Math.min(...nodes.map(node => node.y)) - margin);
    const maxX = Math.min(CANVAS_W, Math.max(...nodes.map(node => node.x + NODE_W)) + margin);
    const maxY = Math.min(CANVAS_H, Math.max(...nodes.map(node => node.y + NODE_H)) + margin);

    return { x: minX, y: minY, w: maxX - minX, h: maxY - minY };
}

function fitViewportToBox(box) {
    const wrap = document.querySelector(".topology-canvas-wrap");
    if (!wrap || !box) return;

    const padding = 18;
    const nextZoom = Math.max(0.25, Math.min(1.1, Math.min(
        (wrap.clientWidth - padding * 2) / box.w,
        (wrap.clientHeight - padding * 2) / box.h
    )));

    setZoom(nextZoom);

    wrap.scrollLeft = Math.max(0, (box.x + box.w / 2) * nextZoom - wrap.clientWidth / 2);
    wrap.scrollTop = Math.max(0, (box.y + box.h / 2) * nextZoom - wrap.clientHeight / 2);
}

function focusZone(zoneKey) {
    const nextView = zoneKey === "campus"
        ? "building"
        : zoneKey === "wan"
            ? "wan"
            : "overview";

    if (nextView !== topologyView) {
        topologyView = nextView;
        buildTopology(topologyLines);
        applySavedLayout();
        renderTopology();
    }

    if (zoneKey === "all") {
        fitViewportToBox(contentBox());
        return;
    }

    const zone = ZONES[zoneKey];
    if (!zone) return;

    fitViewportToBox({
        x: Math.max(0, zone.x - 18),
        y: Math.max(0, zone.y - 18),
        w: Math.min(CANVAS_W - zone.x, zone.w + 36),
        h: Math.min(CANVAS_H - zone.y, zone.h + 36)
    });
}

function wheelZoom(event) {
    const wrap = document.querySelector(".topology-canvas-wrap");
    const rect = wrap.getBoundingClientRect();

    const pointerX = event.clientX - rect.left + wrap.scrollLeft;
    const pointerY = event.clientY - rect.top + wrap.scrollTop;

    const logicalX = pointerX / zoom;
    const logicalY = pointerY / zoom;

    event.preventDefault();

    setZoom(zoom * (event.deltaY < 0 ? 1.1 : 0.9));

    wrap.scrollLeft = logicalX * zoom - (event.clientX - rect.left);
    wrap.scrollTop = logicalY * zoom - (event.clientY - rect.top);
}

function saveTopologyLayout(showMessage = true) {
    const positions = {};

    nodes.forEach(node => {
        positions[node.id] = { x: Math.round(node.x), y: Math.round(node.y) };
    });

    localStorage.setItem(STORAGE_KEY, JSON.stringify(positions));

    if (showMessage) {
        const message = document.getElementById("message");
        if (message) {
            message.innerHTML = '<div class="success-box" style="display:block;margin-bottom:12px;">Da luu vi tri topo.</div>';
            window.setTimeout(() => {
                message.innerHTML = "";
            }, 1800);
        }
    }
}

function applySavedLayout() {
    const raw = localStorage.getItem(STORAGE_KEY);

    if (!raw) return;

    try {
        const saved = JSON.parse(raw);

        nodes = nodes.map(node => {
            return saved[node.id]
                ? { ...node, x: saved[node.id].x, y: saved[node.id].y }
                : node;
        });
    } catch (error) {
        localStorage.removeItem(STORAGE_KEY);
    }
}

function resetLayout() {
    localStorage.removeItem(STORAGE_KEY);
    buildTopology(topologyLines);
    renderTopology();
    requestAnimationFrame(() => focusZone("all"));
}

async function svgWithEmbeddedIcons() {
    const clone = document.getElementById("topologyCanvas").cloneNode(true);

    clone.style.width = `${CANVAS_W}px`;
    clone.style.height = `${CANVAS_H}px`;
    clone.setAttribute("width", CANVAS_W);
    clone.setAttribute("height", CANVAS_H);

    const exportStyle = document.createElementNS("http://www.w3.org/2000/svg", "style");
    exportStyle.textContent = `
        .zone-box { fill: transparent; stroke: #94a3b8; stroke-width: 1.15; stroke-dasharray: 10 8; }
        .building-zone-box { fill: #eff6ff; fill-opacity: 0.48; stroke: #cbd5e1; stroke-width: 1; stroke-dasharray: 6 5; }
        .wan-site-zone-box { fill: #ecfdf5; fill-opacity: 0.48; stroke: #86efac; stroke-width: 1; stroke-dasharray: 6 5; }
        .zone-title { font: 800 18px Arial, sans-serif; fill: #0f172a; }
        .building-zone-title, .wan-site-zone-title { font: 800 12px Arial, sans-serif; fill: #334155; }
        .topo-link { stroke: #475569; stroke-width: 2; fill: none; }
        .topo-link.cross { stroke-width: 1.7; }
        .ha-link { stroke: #0f172a; stroke-width: 1.7; }
        .ha-label { font: 800 9px Arial, sans-serif; fill: #0f172a; paint-order: stroke; stroke: #ffffff; stroke-width: 3px; stroke-linejoin: round; }
        .node-title { font: 800 10px Arial, sans-serif; fill: #0f172a; }
        .node-desc { font: 8px Arial, sans-serif; fill: #475569; }
        .node-qty { font: 800 8px Arial, sans-serif; fill: #1d4ed8; }
        .node-hitbox { fill: transparent; }
    `;
    clone.insertBefore(exportStyle, clone.firstChild);

    return new XMLSerializer().serializeToString(clone);
}

async function exportPng() {
    const source = await svgWithEmbeddedIcons();
    const blob = new Blob([source], { type: "image/svg+xml;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const img = new Image();

    img.onload = () => {
        const canvas = document.createElement("canvas");

        canvas.width = CANVAS_W;
        canvas.height = CANVAS_H;

        const ctx = canvas.getContext("2d");

        ctx.fillStyle = "#ffffff";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0);

        URL.revokeObjectURL(url);

        const a = document.createElement("a");
        a.href = canvas.toDataURL("image/png");
        a.download = "network_topology.png";
        document.body.appendChild(a);
        a.click();
        a.remove();
    };

    img.src = url;
}

function renderRequirementRows(lines) {
    document.getElementById("requirementRows").innerHTML = lines
        .filter(line => line.quantity > 0)
        .map(line => `
            <tr>
                <td>${esc(line.group)}</td>
                <td>${esc(line.item_type)}</td>
                <td>${Number(line.quantity || 0).toLocaleString()}</td>
            </tr>
        `).join("");
}

function readTopologySource() {
    const raw = localStorage.getItem("quoteData");

    topologyMeta = { buildings: [], wanSites: [] };

    if (!raw) return SAMPLE_LINES;

    try {
        const data = JSON.parse(raw);
        const requirementLines = (((data || {}).requirements || {}).requirements || []);
        topologyMeta = {
            buildings: normalizeBuildingDetails((((data || {}).requirements || {}).building_details || [])),
            wanSites: normalizeWanDetails((((data || {}).requirements || {}).wan_details || []))
        };
        const quoteLines = (((data || {}).quote || {}).quote_lines || []);
        const lines = requirementLines.length ? requirementLines : quoteLines;

        return lines.length ? lines : SAMPLE_LINES;
    } catch (error) {
        return SAMPLE_LINES;
    }
}

function initTopology() {
    topologyLines = normalizeTopologyLines(readTopologySource());
    buildTopology(topologyLines);
    applySavedLayout();
    renderRequirementRows(topologyLines);
    renderTopology();
    requestAnimationFrame(() => focusZone("all"));
}

const topologyWrap = document.querySelector(".topology-canvas-wrap");

topologyWrap.addEventListener("pointerdown", startPan);

window.addEventListener("pointermove", event => {
    drag(event);
    panCanvas(event);
});

window.addEventListener("pointerup", () => {
    stopDrag();
    stopPan();
});

window.addEventListener("pointercancel", () => {
    stopDrag();
    stopPan();
});

topologyWrap.addEventListener("wheel", event => {
    if (event.shiftKey) {
        event.preventDefault();
        topologyWrap.scrollLeft += event.deltaY;
        return;
    }

    wheelZoom(event);
}, { passive: false });

initTopology();
</script>
</body>
</html>
"""


def render_topology_page():
    return (
        TOPOLOGY_PAGE
        .replace("__BASE_STYLE__", BASE_STYLE)
        .replace("__NAV__", render_nav("topology"))
        .replace("__ICON_DATA__", icon_data_urls())
    )
