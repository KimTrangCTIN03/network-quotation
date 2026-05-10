import math
from typing import Dict, Any, List



def ceil_div(value: float, divisor: float) -> int:
    if value <= 0 or divisor <= 0:
        return 0
    return math.ceil(value / divisor)


def to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value

    if value is None:
        return False

    return str(value).strip().upper() in ["Y", "YES", "TRUE", "1", "CÓ", "CO"]


def gateway_demand_mbps(users: int) -> float:
    """
    Logic Excel:
    số user × 5 Mbps × 20%
    """
    return users * 5 * 0.2


def wan_demand_mbps(users: int, bandwidth_mbps: float) -> float:
    """
    Logic WAN Router Size:
    WAN demand = Users × 5 Mbps × 20% + Bandwidth WAN Mbps
    """
    return users * 5 * 0.2 + bandwidth_mbps


def wan_router_size(users: int, bandwidth_mbps: float) -> str:
    """
    Nếu WAN demand <= 2000 Mbps: Small
    Nếu > 2000 Mbps: Large
    """
    return "Small" if wan_demand_mbps(users, bandwidth_mbps) <= 2000 else "Large"


def split_access_switch(node_count: int, multiplier: int = 1) -> Dict[str, int]:
    """
    Chia node thành switch:
    48 port → 24 port → 16 port → 8 port
    """
    if node_count <= 0 or multiplier <= 0:
        return {
            "access_switch_48": 0,
            "access_switch_24": 0,
            "access_switch_16": 0,
            "access_switch_8": 0,
        }

    remaining = node_count

    sw48 = remaining // 48
    remaining = remaining % 48

    if remaining > 24:
        sw48 += 1
        remaining = 0

    sw24 = 0
    if remaining > 0:
        sw24 = remaining // 24
        remaining = remaining % 24

        if remaining > 16:
            sw24 += 1
            remaining = 0

    sw16 = 0
    if remaining > 0:
        sw16 = remaining // 16
        remaining = remaining % 16

        if remaining > 8:
            sw16 += 1
            remaining = 0

    sw8 = 0
    if remaining > 0:
        sw8 = math.ceil(remaining / 8)

    return {
        "access_switch_48": sw48 * multiplier,
        "access_switch_24": sw24 * multiplier,
        "access_switch_16": sw16 * multiplier,
        "access_switch_8": sw8 * multiplier,
    }


def is_empty_wan_site(site: Dict[str, Any]) -> bool:
    name = str(site.get("name", "")).strip()
    users = int(site.get("users", 0))
    bandwidth = float(site.get("bandwidth_mbps", 0))
    node_count = int(site.get("node_count", 0))
    wifi_area = float(site.get("wifi_area", 0))

    return (
        name == ""
        and users == 0
        and bandwidth == 0
        and node_count == 0
        and wifi_area == 0
    )


def calculate_wan_proposal(wan_sites: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Logic WAN theo tab Campus:

    WAN demand = Users × 5 Mbps × 20% + Bandwidth WAN Mbps

    Nếu WAN demand <= 2000:
        WAN Router Size = Small
    Nếu WAN demand > 2000:
        WAN Router Size = Large

    Proposal WAN gom tổng:
    - WAN Router loại vừa/nhỏ
    - WAN Router loại lớn
    - Access Switch 48/24/16/8
    - AP indoor
    - SFP 1G
    """

    wan_small_router_qty = 0
    wan_large_router_qty = 0

    wan_access_totals = {
        "access_switch_48": 0,
        "access_switch_24": 0,
        "access_switch_16": 0,
        "access_switch_8": 0,
    }

    wan_ap_total = 0
    wan_sfp_1g_qty = 0
    wan_details = []

    for index, site in enumerate(wan_sites, start=1):
        if is_empty_wan_site(site):
            continue

        site_name = site.get("name", f"WAN {index}")
        wan_users = int(site.get("users", 0))
        bandwidth_mbps = float(site.get("bandwidth_mbps", 0))
        node_count = int(site.get("node_count", 0))
        has_wifi = to_bool(site.get("has_wifi", False))
        wifi_area = float(site.get("wifi_area", 0))
        has_ha = to_bool(site.get("has_ha_gateway", False))

        site_demand = wan_demand_mbps(wan_users, bandwidth_mbps)
        router_size = wan_router_size(wan_users, bandwidth_mbps)
        router_qty = 2 if has_ha else 1

        if router_size == "Small":
            wan_small_router_qty += router_qty
            router_small_qty = router_qty
            router_large_qty = 0
        else:
            wan_large_router_qty += router_qty
            router_small_qty = 0
            router_large_qty = router_qty

        ap_qty = 0
        if has_wifi:
            ap_qty = ceil_div(wifi_area, 100)
            wan_ap_total += ap_qty

        # Excel WAN switch sizing uses node count + indoor AP count.
        # Example: I56 references B21 + I60, where I60 is WAN AP quantity.
        switch_node_count = node_count + ap_qty
        wan_switches = split_access_switch(switch_node_count, 1)

        for key in wan_access_totals:
            wan_access_totals[key] += wan_switches[key]

        # Excel per-site formula:
        # I61=(I53<>"")*(2+SUM(I56:I59)*2*(I54+I55))
        site_sfp_1g_qty = 2 + sum(wan_switches.values()) * 2 * router_qty
        wan_sfp_1g_qty += site_sfp_1g_qty

        wan_details.append({
            "name": site_name,
            "users": wan_users,
            "bandwidth_mbps": bandwidth_mbps,
            "wan_demand_mbps": site_demand,
            "router_size": router_size,
            "router_quantity": router_qty,
            "router_small_quantity": router_small_qty,
            "router_large_quantity": router_large_qty,
            "node_count": node_count,
            "switch_node_count": switch_node_count,
            "switches": wan_switches,
            "has_wifi": has_wifi,
            "wifi_area": wifi_area,
            "ap_quantity": ap_qty,
            "sfp_1g_quantity": site_sfp_1g_qty,
            "has_ha_gateway": has_ha,
        })

    wan_total_switch = sum(wan_access_totals.values())
    wan_total_router = wan_small_router_qty + wan_large_router_qty

    return {
        "wan_small_router_qty": wan_small_router_qty,
        "wan_large_router_qty": wan_large_router_qty,
        "wan_access_totals": wan_access_totals,
        "wan_ap_total": wan_ap_total,
        "wan_total_switch": wan_total_switch,
        "wan_sfp_1g_qty": wan_sfp_1g_qty,
        "wan_details": wan_details,
    }


def requirement_line(
    group: str,
    item_type: str,
    quantity: int,
    requirement: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "group": group,
        "item_type": item_type,
        "quantity": quantity,
        "requirement": requirement,
    }


def proposal_line(
    group: str,
    item_type: str,
    quantity: int,
    requirement: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Proposal line giữ cả quantity = 0
    để bảng Giải pháp đề xuất giống template Excel.
    """
    return {
        "group": group,
        "item_type": item_type,
        "quantity": quantity,
        "requirement": requirement,
    }


def fixed_model_requirement(model: str) -> Dict[str, Any]:
    return {"fixed_model": model}


DC_SDN_DEFAULT_CAPACITY = {
    "N9K-C9504": {"min_100g": 144},
    "N9K-C9508": {"min_100g": 288},
    "N9K-C9516": {"min_100g": 576},
    "N9K-X9736C-FX3": {"min_100g": 36},
    "N9K-C93600CD-GX": {"min_100g": 36},
    "N9K-C9316D-GX": {"min_100g": 16},
    "N9K-C9364C-GX": {"min_100g": 64},
    "N9K-C93360YC-FX2": {"min_10g_sfp": 96, "min_1g_sfp": 96, "min_100g": 12},
    "N9K-C93240YC-FX2": {"min_10g_sfp": 48},
    "N9K-C93180YC-FX3": {"min_10g_sfp": 48, "min_1g_sfp": 48},
    "N9K-C9348GC-FX3": {"min_1g_rj45": 48},
    "N9K-C93108TC-FX3": {"min_1g_rj45": 48, "min_10g_rj45": 48, "min_100g": 6},
    "N9K-C93216TC-FX2": {"min_1g_rj45": 96, "min_10g_rj45": 96, "min_100g": 12},
}


def dc_sdn_requirement(role: str, default_model: str, **requirements: Any) -> Dict[str, Any]:
    return {
        **requirements,
        "dc_sdn_role": role,
        "default_model": default_model,
        "selection_source": "DC-Calculation",
    }


def dc_model_capacity(model: str, key: str) -> float:
    return float(DC_SDN_DEFAULT_CAPACITY.get(model, {}).get(key) or 0)


def calculate_dc_sdn(dc_sdn: Dict[str, Any]) -> Dict[str, Any]:
    enabled = to_bool(dc_sdn.get("enabled", False))
    if not enabled:
        return {"enabled": False, "requirements": [], "proposal_lines": []}

    racks = int(dc_sdn.get("racks", 0))
    servers_per_rack = int(dc_sdn.get("servers_per_rack", 0))
    p100 = int(dc_sdn.get("port_100g_per_server", 0))
    p10_sfp = int(dc_sdn.get("port_10g_sfp_per_server", 0))
    p10_rj45 = int(dc_sdn.get("port_10g_rj45_per_server", 0))
    p1_sfp = int(dc_sdn.get("port_1g_sfp_per_server", 0))
    p1_rj45 = int(dc_sdn.get("port_1g_rj45_per_server", 0))

    spine_qty = 2
    leaf_100g_default = "N9K-C9316D-GX"
    leaf_10g_sfp_default = "N9K-C93180YC-FX3"
    leaf_1g_sfp_default = "N9K-C93180YC-FX3"
    leaf_10g_rj45_default = "N9K-C93108TC-FX3"
    leaf_1g_rj45_default = "N9K-C9348GC-FX3"
    card_default = "N9K-X9736C-FX3"

    # DC-SDN leaf sizing follows the survey labels directly.
    leaf_100g_qty = racks * ceil_div(
        servers_per_rack * p100,
        dc_model_capacity(leaf_100g_default, "min_100g") - 2,
    )
    leaf_10g_sfp_qty = racks * ceil_div(
        servers_per_rack * p10_sfp,
        dc_model_capacity(leaf_10g_sfp_default, "min_10g_sfp"),
    )
    leaf_1g_sfp_qty = racks * ceil_div(
        servers_per_rack * p1_sfp,
        dc_model_capacity(leaf_1g_sfp_default, "min_1g_sfp"),
    )
    leaf_10g_rj45_qty = racks * ceil_div(
        servers_per_rack * p10_rj45,
        dc_model_capacity(leaf_10g_rj45_default, "min_10g_rj45"),
    )
    leaf_1g_rj45_qty = racks * ceil_div(
        servers_per_rack * p1_rj45,
        dc_model_capacity(leaf_1g_rj45_default, "min_1g_rj45"),
    )
    total_leaf_qty = leaf_100g_qty + leaf_10g_sfp_qty + leaf_10g_rj45_qty + leaf_1g_sfp_qty + leaf_1g_rj45_qty
    spine_card_qty = spine_qty * ceil_div(total_leaf_qty, dc_model_capacity(card_default, "min_100g"))

    proposal_lines = [
        proposal_line("DC-SDN", "APIC Cluster", 1, fixed_model_requirement("APIC-CLUSTERG5")),
        proposal_line("DC-SDN", "Spine", spine_qty, dc_sdn_requirement("spine", "N9K-C9504", min_100g=total_leaf_qty, model_prefix="N9K-C95", excel_range="DC-Calculation!B15:Z15")),
        proposal_line("DC-SDN", "Card 100G cho Spine", spine_card_qty, dc_sdn_requirement("spine_card_100g", card_default, min_100g=2, model_contains="=", excel_range="DC-Calculation!B16:Z16")),
        proposal_line("DC-SDN", "Leaf 100G", leaf_100g_qty, dc_sdn_requirement("leaf_100g", leaf_100g_default, min_100g=16, model_prefix="N9K-C93", excel_range="DC-Calculation!B17:Z17")),
        proposal_line("DC-SDN", "Leaf 10G quang", leaf_10g_sfp_qty, dc_sdn_requirement("leaf_10g_sfp", leaf_10g_sfp_default, min_10g_sfp=24, model_prefix="N9K-C93", excel_range="DC-Calculation!B18:Z18")),
        proposal_line("DC-SDN", "Leaf 10G đồng", leaf_10g_rj45_qty, fixed_model_requirement("N9K-C93108TC-FX3")),
        proposal_line("DC-SDN", "Leaf 1G quang", leaf_1g_sfp_qty, dc_sdn_requirement("leaf_1g_sfp", leaf_1g_sfp_default, min_1g_sfp=24, model_prefix="N9K-C93", excel_range="DC-Calculation!B19:Z19")),
        proposal_line("DC-SDN", "Leaf 1G đồng", leaf_1g_rj45_qty, fixed_model_requirement("N9K-C93108TC-FX3")),
        proposal_line("DC-SDN", "SFP 100G kết nối Spine-Leaf", total_leaf_qty * 4, fixed_model_requirement("QSFP-100G-LR4-S")),
        proposal_line("DC-SDN", "SFP 100G kết nối Server", racks * servers_per_rack * p100, fixed_model_requirement("QSFP-100G-LR-S")),
        proposal_line("DC-SDN", "SFP 10G kết nối Server", racks * servers_per_rack * p10_sfp, fixed_model_requirement("SFP-10G-SR")),
        proposal_line("DC-SDN", "SFP 1G kết nối Server", racks * servers_per_rack * p1_sfp, fixed_model_requirement("GLC-SX-MMD")),
    ]

    return {
        "enabled": True,
        "racks": racks,
        "servers_per_rack": servers_per_rack,
        "total_leaf_qty": total_leaf_qty,
        "requirements": [line for line in proposal_lines if line["quantity"] > 0],
        "proposal_lines": proposal_lines,
    }


def calculate_dc_sdn(dc_sdn: Dict[str, Any]) -> Dict[str, Any]:
    enabled = to_bool(dc_sdn.get("enabled", False))
    if not enabled:
        return {"enabled": False, "requirements": [], "proposal_lines": []}

    racks = int(dc_sdn.get("racks", 0))
    servers_per_rack = int(dc_sdn.get("servers_per_rack", 0))
    p100 = int(dc_sdn.get("port_100g_per_server", 0))
    p10_sfp = int(dc_sdn.get("port_10g_sfp_per_server", 0))
    p10_rj45 = int(dc_sdn.get("port_10g_rj45_per_server", 0))
    p1_sfp = int(dc_sdn.get("port_1g_sfp_per_server", 0))
    p1_rj45 = int(dc_sdn.get("port_1g_rj45_per_server", 0))

    spine_qty = 2
    leaf_100g_default = "N9K-C9316D-GX"
    leaf_10g_sfp_default = "N9K-C93180YC-FX3"
    leaf_1g_sfp_default = "N9K-C93180YC-FX3"
    leaf_10g_rj45_default = "N9K-C93108TC-FX3"
    leaf_1g_rj45_default = "N9K-C9348GC-FX3"
    card_default = "N9K-X9736C-FX3"

    # DC-SDN leaf sizing follows the survey labels directly.
    leaf_100g_qty = racks * ceil_div(
        servers_per_rack * p100,
        dc_model_capacity(leaf_100g_default, "min_100g") - 2,
    )
    leaf_10g_sfp_qty = racks * ceil_div(
        servers_per_rack * p10_sfp,
        dc_model_capacity(leaf_10g_sfp_default, "min_10g_sfp"),
    )
    leaf_1g_sfp_qty = racks * ceil_div(
        servers_per_rack * p1_sfp,
        dc_model_capacity(leaf_1g_sfp_default, "min_1g_sfp"),
    )
    leaf_10g_rj45_qty = racks * ceil_div(
        servers_per_rack * p10_rj45,
        dc_model_capacity(leaf_10g_rj45_default, "min_10g_rj45"),
    )
    leaf_1g_rj45_qty = racks * ceil_div(
        servers_per_rack * p1_rj45,
        dc_model_capacity(leaf_1g_rj45_default, "min_1g_rj45"),
    )
    total_leaf_qty = leaf_100g_qty + leaf_10g_sfp_qty + leaf_1g_sfp_qty + leaf_10g_rj45_qty + leaf_1g_rj45_qty
    spine_card_qty = spine_qty * ceil_div(total_leaf_qty, dc_model_capacity(card_default, "min_100g"))

    proposal_lines = [
        proposal_line("DC-SDN", "APIC Cluster", 1, fixed_model_requirement("APIC-CLUSTERG5")),
        proposal_line("DC-SDN", "Spine", spine_qty, dc_sdn_requirement("spine", "N9K-C9504", min_100g=total_leaf_qty, model_prefix="N9K-C95", excel_range="DC-Calculation!B15:Z15")),
        proposal_line("DC-SDN", "Card 100G cho Spine", spine_card_qty, dc_sdn_requirement("spine_card_100g", card_default, min_100g=2, model_contains="=", excel_range="DC-Calculation!B16:Z16")),
        proposal_line("DC-SDN", "Leaf 100G", leaf_100g_qty, dc_sdn_requirement("leaf_100g", leaf_100g_default, min_100g=16, model_prefix="N9K-C93", excel_range="DC-Calculation!B17:Z17")),
        proposal_line("DC-SDN", "Leaf 10G quang", leaf_10g_sfp_qty, dc_sdn_requirement("leaf_10g_sfp", leaf_10g_sfp_default, min_10g_sfp=24, model_prefix="N9K-C93", excel_range="DC-Calculation!B18:Z18")),
        proposal_line("DC-SDN", "Leaf 1G quang", leaf_1g_sfp_qty, dc_sdn_requirement("leaf_1g_sfp", leaf_1g_sfp_default, min_1g_sfp=24, model_prefix="N9K-C93", excel_range="DC-Calculation!B19:Z19")),
        proposal_line("DC-SDN", "Leaf 10G dong", leaf_10g_rj45_qty, dc_sdn_requirement("leaf_10g_rj45", leaf_10g_rj45_default, min_10g_rj45=24, model_prefix="N9K-C93", excel_range="DC-Calculation!B20:Z20")),
        proposal_line("DC-SDN", "Leaf 1G dong", leaf_1g_rj45_qty, dc_sdn_requirement("leaf_1g_rj45", leaf_1g_rj45_default, min_1g_rj45=24, model_prefix="N9K-C93", excel_range="DC-Calculation!B21:Z21")),
        proposal_line("DC-SDN", "SFP 100G kết nối Spine-Leaf", total_leaf_qty * 4, dc_sdn_requirement("sfp_100g_spine_leaf", "QSFP-100G-LR-S", speed=100, distance=10, excel_range="DC-Calculation!B24:Z28")),
        proposal_line("DC-SDN", "SFP 100G kết nối Server", racks * servers_per_rack * p100, dc_sdn_requirement("sfp_100g_server", "QSFP-100G-LR-S", speed=100, distance=10, excel_range="DC-Calculation!B24:Z28")),
        proposal_line("DC-SDN", "SFP 10G kết nối Server", racks * servers_per_rack * p10_sfp, dc_sdn_requirement("sfp_10g_server", "SFP-10G-SR", speed=10, distance=0.5, excel_range="DC-Calculation!B24:Z28")),
        proposal_line("DC-SDN", "SFP 1G kết nối Server", racks * servers_per_rack * p1_sfp, dc_sdn_requirement("sfp_1g_server", "GLC-SX-MMD", speed=1, distance=0.5, excel_range="DC-Calculation!B24:Z28")),
    ]

    return {
        "enabled": True,
        "racks": racks,
        "servers_per_rack": servers_per_rack,
        "total_leaf_qty": total_leaf_qty,
        "leaf_100g_qty": leaf_100g_qty,
        "leaf_10g_sfp_qty": leaf_10g_sfp_qty,
        "leaf_1g_sfp_qty": leaf_1g_sfp_qty,
        "leaf_10g_rj45_qty": leaf_10g_rj45_qty,
        "leaf_1g_rj45_qty": leaf_1g_rj45_qty,
        "spine_card_qty": spine_card_qty,
        "requirements": [line for line in proposal_lines if line["quantity"] > 0],
        "proposal_lines": proposal_lines,
    }


def build_requirements(payload: Dict[str, Any]) -> Dict[str, Any]:
    hq = payload.get("hq", {})
    buildings = payload.get("buildings", [])
    server_farm = payload.get("server_farm", {})
    wan_sites = payload.get("wan_sites", [])
    dc_sdn = payload.get("dc_sdn", {})

    hq_users = int(hq.get("users", 0))
    has_outdoor_wifi = to_bool(hq.get("has_outdoor_wifi", False))
    outdoor_area = float(hq.get("outdoor_area", 0))

    gateway_demand = gateway_demand_mbps(hq_users)

    requirements: List[Dict[str, Any]] = []

    # =========================
    # 1. Campus HQ calculation
    # =========================

    campus_gateway_router_qty = 2
    campus_firewall_qty = 2

    access_totals = {
        "access_switch_48": 0,
        "access_switch_24": 0,
        "access_switch_16": 0,
        "access_switch_8": 0,
    }

    indoor_ap_total = 0
    building_details = []

    for building in buildings:
        name = building.get("name", "Building")
        floors = int(building.get("floors", 0))
        area_per_floor = float(building.get("area_per_floor", 0))
        rooms_per_floor = int(building.get("rooms_per_floor", 0))
        node_per_floor = int(building.get("node_per_floor", 0))
        has_indoor_wifi = to_bool(building.get("has_indoor_wifi", False))

        switches = split_access_switch(node_per_floor, floors)

        for key in access_totals:
            access_totals[key] += switches[key]

        indoor_ap = 0
        if has_indoor_wifi:
            indoor_ap = ceil_div(area_per_floor, 100) * floors
            indoor_ap_total += indoor_ap

        building_details.append({
            "name": name,
            "floors": floors,
            "area_per_floor": area_per_floor,
            "rooms_per_floor": rooms_per_floor,
            "node_per_floor": node_per_floor,
            "has_indoor_wifi": has_indoor_wifi,
            "switches": switches,
            "indoor_ap": indoor_ap,
        })

    total_access_switch = sum(access_totals.values())

    campus_core_modular_qty = 0
    campus_core_48_qty = 0
    campus_core_24_qty = 0

    if total_access_switch > 0:
        if total_access_switch < 24:
            campus_core_24_qty = 2
        elif total_access_switch < 48:
            campus_core_48_qty = 2
        else:
            campus_core_modular_qty = 2 if total_access_switch <= 96 else 4

    outdoor_ap_total = ceil_div(outdoor_area, 1000) if has_outdoor_wifi else 0

    # =========================
    # 2. Server Farm calculation
    # =========================

    sf_enabled = to_bool(server_farm.get("enabled", False))

    sf_bandwidth_gbps = 0
    sf_campus_uplink_bandwidth_gbps = 0
    sf_core_spine_qty = 0
    sf_card_100g_qty = 0
    sf_card_10g_qty = 0
    sf_leaf_100g_qty = 0
    sf_leaf_10g_sfp_qty = 0
    sf_leaf_10g_rj45_qty = 0
    sf_leaf_1g_sfp_qty = 0
    sf_leaf_1g_rj45_qty = 0

    total_100g_ports = 0
    total_10g_sfp_ports = 0
    total_10g_rj45_ports = 0
    total_1g_sfp_ports = 0
    total_1g_rj45_ports = 0

    if sf_enabled:
        racks = int(server_farm.get("racks", 0))
        servers_per_rack = int(server_farm.get("servers_per_rack", 0))
        total_servers = racks * servers_per_rack

        p100 = int(server_farm.get("port_100g_per_server", 0))
        p10_sfp = int(server_farm.get("port_10g_sfp_per_server", 0))
        p10_rj45 = int(server_farm.get("port_10g_rj45_per_server", 0))
        p1_sfp = int(server_farm.get("port_1g_sfp_per_server", 0))
        p1_rj45 = int(server_farm.get("port_1g_rj45_per_server", 0))

        total_100g_ports = total_servers * p100
        total_10g_sfp_ports = total_servers * p10_sfp
        total_10g_rj45_ports = total_servers * p10_rj45
        total_1g_sfp_ports = total_servers * p1_sfp
        total_1g_rj45_ports = total_servers * p1_rj45

        # Logic theo file Excel:
        # SF BW = rack × server/rack × (100GE/server × 100 + 10GE SFP/server × 10 + 10GE RJ45/server)
        # 1GE không tham gia tính SF BW.
        # Latest workbook formula for Server Farm SFP rows 55-56.
        sf_bandwidth_gbps = total_servers * (
            p100 * 100
            + p10_sfp * 10
            + p10_rj45 * 10
            + p1_sfp
            + p1_rj45
        )
        sf_campus_uplink_bandwidth_gbps = total_servers * (
            p100 * 100
            + p10_sfp * 10
            + p10_rj45
        )

        total_server_ports = (
            total_100g_ports
            + total_10g_sfp_ports
            + total_10g_rj45_ports
            + total_1g_sfp_ports
            + total_1g_rj45_ports
        )

        # Logic theo Excel: có Server Farm và có server thì Core/Spine = 2.
        if False:
            sf_core_spine_qty = 2

        if total_100g_ports > 0:
            sf_leaf_100g_qty = max(2, ceil_div(total_100g_ports, 48))

        if total_10g_sfp_ports > 0:
            sf_leaf_10g_sfp_qty = max(2, ceil_div(total_10g_sfp_ports, 48))

        if total_10g_rj45_ports > 0:
            sf_leaf_10g_rj45_qty = max(2, ceil_div(total_10g_rj45_ports, 48))

        if total_1g_sfp_ports > 0:
            sf_leaf_1g_sfp_qty = max(2, ceil_div(total_1g_sfp_ports, 48))

        if total_1g_rj45_ports > 0:
            sf_leaf_1g_rj45_qty = max(2, ceil_div(total_1g_rj45_ports, 48))

    # =========================
    # 3. SFP calculation
    # =========================

    campus_sfp_100g_qty = 8 if sf_campus_uplink_bandwidth_gbps > 60 else 0

    campus_sfp_10g_qty = (
        (campus_gateway_router_qty * 4 + campus_firewall_qty * 4)
        if gateway_demand >= 5000
        else 0
    ) + (8 if sf_campus_uplink_bandwidth_gbps <= 60 else 0)

    # Campus SFP 1G:
    # Mỗi access switch có 2 uplink.
    # Mỗi uplink cần module quang ở 2 đầu nên nhân 4.
    # Cộng thêm 16 SFP cho phần Gateway / Firewall / Core.
    campus_sfp_1g_qty = (
        (campus_gateway_router_qty * 4 + campus_firewall_qty * 4)
        if gateway_demand < 5000
        else 0
    ) + total_access_switch * 4

    campus_core_100g_card_qty = campus_core_modular_qty * (1 if campus_sfp_1g_qty > 0 else 0)
    campus_core_10g_1g_card_qty = campus_core_modular_qty * ceil_div(
        total_access_switch + campus_sfp_10g_qty / 4,
        48,
    )

    # Server Farm SFP:
    # Các cổng quang xuống server tính 2 đầu.
    # Uplink Server Farm sang Campus/Core tính thêm 8 SFP theo loại uplink.
    server_farm_sfp_100g_qty = 0
    server_farm_sfp_10g_qty = 0
    server_farm_sfp_1g_qty = 0

    if sf_enabled:
        server_farm_sfp_100g_qty = (
            (8 if sf_bandwidth_gbps > 60 else 0)
            + total_100g_ports
            + (sf_leaf_100g_qty + sf_leaf_10g_sfp_qty + sf_leaf_10g_rj45_qty) * 4
        )
        server_farm_sfp_10g_qty = (
            (8 if sf_bandwidth_gbps <= 60 else 0)
            + total_10g_sfp_ports
            + (sf_leaf_1g_sfp_qty + sf_leaf_1g_rj45_qty) * 4
        )
        server_farm_sfp_1g_qty = total_1g_sfp_ports

    sf_leaf_total = (
        sf_leaf_100g_qty
        + sf_leaf_10g_sfp_qty
        + sf_leaf_10g_rj45_qty
        + sf_leaf_1g_sfp_qty
        + sf_leaf_1g_rj45_qty
    )

    if sf_leaf_total >= 3:
        sf_core_spine_qty = 2 if sf_leaf_total < 384 else 4

    sf_card_100g_qty = sf_core_spine_qty * ceil_div(server_farm_sfp_100g_qty, 48)
    sf_card_10g_qty = sf_core_spine_qty * ceil_div(server_farm_sfp_10g_qty, 160)

    # =========================
    # 4. WAN calculation
    # =========================

    wan_calc = calculate_wan_proposal(wan_sites)

    wan_small_router_qty = wan_calc["wan_small_router_qty"]
    wan_large_router_qty = wan_calc["wan_large_router_qty"]
    wan_access_totals = wan_calc["wan_access_totals"]
    wan_ap_total = wan_calc["wan_ap_total"]
    wan_sfp_1g_qty = wan_calc["wan_sfp_1g_qty"]
    wan_details = wan_calc["wan_details"]

    # =========================
    # 5. Requirements for page 2
    # =========================

    def add_requirement(group: str, item_type: str, quantity: int, req: Dict[str, Any]):
        if quantity > 0:
            requirements.append(requirement_line(group, item_type, quantity, req))

    add_requirement("Campus - Trụ sở chính", "Gateway Router", campus_gateway_router_qty, {
        "throughput_mbps": gateway_demand,
        "min_wan_1g": 4 if gateway_demand < 5000 else 0,
        "min_wan_10g": 4 if gateway_demand >= 5000 else 0,
        "min_lan_1g": 4,
    })

    add_requirement("Campus - Trụ sở chính", "Firewall", campus_firewall_qty, {
        "device_family": "firewall"
    })

    add_requirement("Campus - Trụ sở chính", "Core Switch Modular", campus_core_modular_qty, {
        "min_total_access_ports": total_access_switch,
        "min_100g": 0,
    })

    add_requirement("Campus - Trụ sở chính", "Card 100GE", campus_core_100g_card_qty, {
        **fixed_model_requirement("C9400-LC-12QC"),
        "parent_item": "Core Switch Modular",
    })

    add_requirement("Campus - Trụ sở chính", "Card 10GE/1GE", campus_core_10g_1g_card_qty, {
        **fixed_model_requirement("C9400-LC-48XS"),
        "parent_item": "Core Switch Modular",
    })

    add_requirement("Campus - Trụ sở chính", "Core Switch 48 GE SFP", campus_core_48_qty, {
        "min_1g_sfp": 48,
    })

    add_requirement("Campus - Trụ sở chính", "Core Switch 24 GE SFP", campus_core_24_qty, {
        "min_1g_sfp": 24,
    })

    for item, qty, port in [
        ("Access Switch 48x1GE RJ45", access_totals["access_switch_48"], 48),
        ("Access Switch 24x1GE RJ45", access_totals["access_switch_24"], 24),
        ("Access Switch 16x1GE RJ45", access_totals["access_switch_16"], 16),
        ("Access Switch 8x1GE RJ45", access_totals["access_switch_8"], 8),
    ]:
        add_requirement("Campus - Trụ sở chính", item, qty, {"min_1g_rj45": port})

    add_requirement("Campus - Trụ sở chính", "Access Point indoor (kèm Power Injector)", indoor_ap_total, {
        "ap_type": "indoor"
    })

    add_requirement("Campus - Trụ sở chính", "Access Point outdoor (kèm Power Injector)", outdoor_ap_total, {
        "ap_type": "outdoor"
    })

    add_requirement("Campus - Trụ sở chính", "Power Injector indoor", indoor_ap_total, fixed_model_requirement("AIR-PWRINJ7"))
    add_requirement("Campus - Trụ sở chính", "Power Injector outdoor", outdoor_ap_total, fixed_model_requirement("IW-PWRINJ-60RGDMG"))

    add_requirement("Campus - Trụ sở chính", "SFP 100G", campus_sfp_100g_qty, {"speed": 100, "distance": 10})
    add_requirement("Campus - Trụ sở chính", "SFP 10G", campus_sfp_10g_qty, {"speed": 10, "distance": 10})
    add_requirement("Campus - Trụ sở chính", "SFP 1G", campus_sfp_1g_qty, {"speed": 1, "distance": 10})

    add_requirement("Server Farm", "Core Switch (hoặc Spine Switch)", sf_core_spine_qty, {"min_100g": 2})
    add_requirement("Server Farm", "Card 100GE", sf_card_100g_qty, {
        **fixed_model_requirement("C9400-LC-12QC"),
        "parent_item": "Core Switch (hoặc Spine Switch)",
    })
    add_requirement("Server Farm", "Card 10GE", sf_card_10g_qty, {
        **fixed_model_requirement("C9400-LC-48XS"),
        "parent_item": "Core Switch (hoặc Spine Switch)",
    })
    add_requirement("Server Farm", "Access Switch 100G (hoặc Leaf Switch)", sf_leaf_100g_qty, {"min_100g": 48})
    add_requirement("Server Farm", "Access Switch 48x10G SFP (hoặc Leaf Switch)", sf_leaf_10g_sfp_qty, {"min_10g_sfp": 48})
    add_requirement("Server Farm", "Access Switch 48x10G RJ45 (hoặc Leaf Switch)", sf_leaf_10g_rj45_qty, {"min_10g_rj45": 48})
    add_requirement("Server Farm", "Access Switch 48x1G SFP (hoặc Leaf Switch)", sf_leaf_1g_sfp_qty, {"min_1g_sfp": 48})
    add_requirement("Server Farm", "Access Switch 48x1G RJ45 (hoặc Leaf Switch)", sf_leaf_1g_rj45_qty, {"min_1g_rj45": 48})
    add_requirement("Server Farm", "SFP 100G", server_farm_sfp_100g_qty, {"speed": 100, "distance": 10})
    add_requirement("Server Farm", "SFP 10G", server_farm_sfp_10g_qty, {"speed": 10, "distance": 10})
    add_requirement("Server Farm", "SFP 1G", server_farm_sfp_1g_qty, {"speed": 1, "distance": 10})

    add_requirement("WAN", "WAN Router loại vừa/nhỏ", wan_small_router_qty, {
        "throughput_mbps": 2000,
        "wan_router_size": "Small",
        "min_wan_1g": 1,
        "min_lan_1g": 4,
    })

    add_requirement("WAN", "WAN Router loại lớn", wan_large_router_qty, {
        "throughput_mbps": 2001,
        "wan_router_size": "Large",
        "min_wan_10g": 1,
        "min_lan_1g": 4,
    })

    for item, qty, port in [
        ("Access Switch 48x1GE RJ45", wan_access_totals["access_switch_48"], 48),
        ("Access Switch 24x1GE RJ45", wan_access_totals["access_switch_24"], 24),
        ("Access Switch 16x1GE RJ45", wan_access_totals["access_switch_16"], 16),
        ("Access Switch 8x1GE RJ45", wan_access_totals["access_switch_8"], 8),
    ]:
        add_requirement("WAN", item, qty, {"min_1g_rj45": port})

    add_requirement("WAN", "Access Point indoor (kèm Power Injector)", wan_ap_total, {"ap_type": "indoor"})
    add_requirement("WAN", "Power Injector indoor", wan_ap_total, fixed_model_requirement("AIR-PWRINJ7"))
    add_requirement("WAN", "SFP 1G", wan_sfp_1g_qty, {"speed": 1, "distance": 10})

    # =========================
    # 6. Proposal lines for page 3
    # Fixed template giống Excel
    # =========================

    proposal_lines = [
        proposal_line("Campus - Trụ sở chính", "Gateway Router", campus_gateway_router_qty, {
            "throughput_mbps": gateway_demand,
            "min_wan_1g": 4 if gateway_demand < 5000 else 0,
            "min_wan_10g": 4 if gateway_demand >= 5000 else 0,
            "min_lan_1g": 4,
        }),
        proposal_line("Campus - Trụ sở chính", "Firewall", campus_firewall_qty, {
            "device_family": "firewall"
        }),
        proposal_line("Campus - Trụ sở chính", "Core Switch Modular", campus_core_modular_qty, {
            "min_total_access_ports": total_access_switch,
            "min_100g": 0,
        }),
        proposal_line("Campus - Trụ sở chính", "Card 100GE", campus_core_100g_card_qty, {
            **fixed_model_requirement("C9400-LC-12QC"),
            "parent_item": "Core Switch Modular",
        }),
        proposal_line("Campus - Trụ sở chính", "Card 10GE/1GE", campus_core_10g_1g_card_qty, {
            **fixed_model_requirement("C9400-LC-48XS"),
            "parent_item": "Core Switch Modular",
        }),
        proposal_line("Campus - Trụ sở chính", "Core Switch 48 GE SFP", campus_core_48_qty, {
            "min_1g_sfp": 48,
        }),
        proposal_line("Campus - Trụ sở chính", "Core Switch 24 GE SFP", campus_core_24_qty, {
            "min_1g_sfp": 24,
        }),
        proposal_line("Campus - Trụ sở chính", "Access Switch 48x1GE RJ45", access_totals["access_switch_48"], {
            "min_1g_rj45": 48,
        }),
        proposal_line("Campus - Trụ sở chính", "Access Switch 24x1GE RJ45", access_totals["access_switch_24"], {
            "min_1g_rj45": 24,
        }),
        proposal_line("Campus - Trụ sở chính", "Access Switch 16x1GE RJ45", access_totals["access_switch_16"], {
            "min_1g_rj45": 16,
        }),
        proposal_line("Campus - Trụ sở chính", "Access Switch 8x1GE RJ45", access_totals["access_switch_8"], {
            "min_1g_rj45": 8,
        }),
        proposal_line("Campus - Trụ sở chính", "Access Point indoor (kèm Power Injector)", indoor_ap_total, {
            "ap_type": "indoor",
        }),
        proposal_line("Campus - Trụ sở chính", "Access Point outdoor (kèm Power Injector)", outdoor_ap_total, {
            "ap_type": "outdoor",
        }),
        proposal_line("Campus - Trụ sở chính", "Power Injector indoor", indoor_ap_total, fixed_model_requirement("AIR-PWRINJ7")),
        proposal_line("Campus - Trụ sở chính", "Power Injector outdoor", outdoor_ap_total, fixed_model_requirement("IW-PWRINJ-60RGDMG")),
        proposal_line("Campus - Trụ sở chính", "SFP 100G", campus_sfp_100g_qty, {
            "speed": 100,
            "distance": 10,
        }),
        proposal_line("Campus - Trụ sở chính", "SFP 10G", campus_sfp_10g_qty, {
            "speed": 10,
            "distance": 10,
        }),
        proposal_line("Campus - Trụ sở chính", "SFP 1G", campus_sfp_1g_qty, {
            "speed": 1,
            "distance": 10,
        }),

        proposal_line("Server Farm", "Core Switch (hoặc Spine Switch)", sf_core_spine_qty, {
            "min_100g": 2,
        }),
        proposal_line("Server Farm", "Card 100GE", sf_card_100g_qty, {
            **fixed_model_requirement("C9400-LC-12QC"),
            "parent_item": "Core Switch (hoặc Spine Switch)",
        }),
        proposal_line("Server Farm", "Card 10GE", sf_card_10g_qty, {
            **fixed_model_requirement("C9400-LC-48XS"),
            "parent_item": "Core Switch (hoặc Spine Switch)",
        }),
        proposal_line("Server Farm", "Access Switch 100G (hoặc Leaf Switch)", sf_leaf_100g_qty, {
            "min_100g": 48,
        }),
        proposal_line("Server Farm", "Access Switch 48x10G SFP (hoặc Leaf Switch)", sf_leaf_10g_sfp_qty, {
            "min_10g_sfp": 48,
        }),
        proposal_line("Server Farm", "Access Switch 48x10G RJ45 (hoặc Leaf Switch)", sf_leaf_10g_rj45_qty, {
            "min_10g_rj45": 48,
        }),
        proposal_line("Server Farm", "Access Switch 48x1G SFP (hoặc Leaf Switch)", sf_leaf_1g_sfp_qty, {
            "min_1g_sfp": 48,
        }),
        proposal_line("Server Farm", "Access Switch 48x1G RJ45 (hoặc Leaf Switch)", sf_leaf_1g_rj45_qty, {
            "min_1g_rj45": 48,
        }),
        proposal_line("Server Farm", "SFP 100G", server_farm_sfp_100g_qty, {
            "speed": 100,
            "distance": 10,
        }),
        proposal_line("Server Farm", "SFP 10G", server_farm_sfp_10g_qty, {
            "speed": 10,
            "distance": 10,
        }),
        proposal_line("Server Farm", "SFP 1G", server_farm_sfp_1g_qty, {
            "speed": 1,
            "distance": 10,
        }),

        proposal_line("WAN", "WAN Router loại vừa/nhỏ", wan_small_router_qty, {
            "throughput_mbps": 2000,
            "wan_router_size": "Small",
            "min_wan_1g": 1,
            "min_lan_1g": 4,
        }),
        proposal_line("WAN", "WAN Router loại lớn", wan_large_router_qty, {
            "throughput_mbps": 2001,
            "wan_router_size": "Large",
            "min_wan_10g": 1,
            "min_lan_1g": 4,
        }),
        proposal_line("WAN", "Access Switch 48x1GE RJ45", wan_access_totals["access_switch_48"], {
            "min_1g_rj45": 48,
        }),
        proposal_line("WAN", "Access Switch 24x1GE RJ45", wan_access_totals["access_switch_24"], {
            "min_1g_rj45": 24,
        }),
        proposal_line("WAN", "Access Switch 16x1GE RJ45", wan_access_totals["access_switch_16"], {
            "min_1g_rj45": 16,
        }),
        proposal_line("WAN", "Access Switch 8x1GE RJ45", wan_access_totals["access_switch_8"], {
            "min_1g_rj45": 8,
        }),
        proposal_line("WAN", "Access Point indoor (kèm Power Injector)", wan_ap_total, {
            "ap_type": "indoor",
        }),
        proposal_line("WAN", "Power Injector indoor", wan_ap_total, fixed_model_requirement("AIR-PWRINJ7")),
        proposal_line("WAN", "SFP 1G", wan_sfp_1g_qty, {
            "speed": 1,
            "distance": 10,
        }),
    ]

    dc_sdn_calc = calculate_dc_sdn(dc_sdn)
    requirements.extend(dc_sdn_calc["requirements"])
    proposal_lines.extend(dc_sdn_calc["proposal_lines"])

    return {
        "gateway_demand_mbps": gateway_demand,
        "server_farm_bandwidth_gbps": sf_bandwidth_gbps,
        "campus_core_100g_card_qty": campus_core_100g_card_qty,
        "campus_core_10g_1g_card_qty": campus_core_10g_1g_card_qty,
        "server_farm_core_card_100g_qty": sf_card_100g_qty,
        "server_farm_core_card_10g_qty": sf_card_10g_qty,
        "building_count": len(buildings),
        "wan_count": len(wan_details),
        "building_details": building_details,
        "wan_details": wan_details,
        "dc_sdn": dc_sdn_calc,
        "requirements": requirements,
        "proposal_lines": proposal_lines,
    }
