from typing import Any, Callable, Dict, List

from app.catalog_engine import load_catalogs, normalize_model, read_price_map


OPTION_CLASSES = [
    ("opt1", "Low End"),
    ("opt2", "Mid Range"),
    ("opt3", "High End"),
]

SPEC_SELECTOR_LABELS = {
    "throughput_mbps": "Throughput (Mbps)",
    "switching_bandwidth_gbps": "Switching Bandwidth - Full Duplex (Gbps)",
    "forwarding_mpps": "Forwarding Capacity (Mpps)",
    "min_wan_1g": "Số lượng cổng WAN 1GE",
    "min_wan_10g": "Số lượng cổng WAN 10GE",
    "min_lan_1g": "Số lượng cổng LAN 1GE",
    "min_lan_10g": "Số lượng cổng LAN 10GE",
    "min_1g_rj45": "Số lượng cổng 1GE đồng",
    "min_1g_sfp": "Số lượng cổng 1GE SFP",
    "min_10g_rj45": "Số lượng cổng 10GE đồng",
    "min_10g_sfp": "Số lượng cổng 10GE quang",
    "min_100g": "Số lượng cổng 100GE",
    "wifi_users_per_ap": "Số lượng người dùng trong phạm vi phủ sóng 1 AP",
    "wifi_radius_m": "Bán kính phủ sóng (m)",
    "speed": "speed",
    "distance": "distance",
}

SPEC_SELECTOR_TEXT_LABELS = {
    "stacking": "Stacking (Y/N)",
    "poe": "PoE (Y/N)",
    "wifi_technology": "Công nghệ WiFi (WiFi6/WiFi7)",
    "antenna_type": "Antenna Type (Omni or Directional)",
}

SPEC_SELECTOR_CLASS_BY_SHEET = {
    "Router": "Router Class",
    "SwitchCampus": "Switch Class",
    "ModularSwitch": "Switch Class",
    "NexusSwitch": "Switch Class",
    "WiFi": "Access Point Class",
    "SFP": "SFP Class",
}

CLASS_FALLBACKS = {
    "Low End": ["Low End", "Mid Range", "High End"],
    "Mid Range": ["Mid Range", "High End"],
    "High End": ["High End"],
}


def spec_number(device: Dict[str, Any], label: str) -> float:
    value = device.get("specs", {}).get(label)

    if value is None or value == "":
        return 0

    try:
        return float(value)
    except Exception:
        return 0


def spec_text(device: Dict[str, Any], label: str) -> str:
    return str(device.get("specs", {}).get(label) or "").strip()


def get_class(device: Dict[str, Any]) -> str:
    if device.get("class"):
        return str(device.get("class")).strip()

    for key, value in device.get("specs", {}).items():
        if "class" in str(key).lower():
            return str(value or "").strip()

    return ""


def device_price(device: Dict[str, Any]) -> float:
    try:
        return float(device.get("price") or 0)
    except Exception:
        return 0


def model_text(device: Dict[str, Any]) -> str:
    return normalize_model(device.get("model", "")).upper()


def requirement_number(requirement: Dict[str, Any], key: str) -> float:
    try:
        return float(requirement.get(key) or 0)
    except Exception:
        return 0


def spec_selector_requirement_map(requirement: Dict[str, Any]) -> Dict[str, float]:
    mapped: Dict[str, float] = {}

    for req_key, spec_label in SPEC_SELECTOR_LABELS.items():
        value = requirement_number(requirement, req_key)
        if value:
            mapped[spec_label] = value

    return mapped


def spec_selector_text_requirement_map(requirement: Dict[str, Any]) -> Dict[str, str]:
    mapped: Dict[str, str] = {}

    for req_key, spec_label in SPEC_SELECTOR_TEXT_LABELS.items():
        value = str(requirement.get(req_key) or "").strip()
        if value:
            mapped[spec_label] = value

    return mapped


def device_matches_text_requirements(device: Dict[str, Any], requirement: Dict[str, Any]) -> bool:
    ap_type = str(requirement.get("ap_type") or "").strip().lower()
    if ap_type and spec_text(device, "Loại Access Point (indoor/outdoor)").lower() != ap_type:
        return False

    preferred_class = str(requirement.get("preferred_class") or "").strip()
    if preferred_class and get_class(device) != preferred_class:
        return False

    return True


def device_spec_selector_score(device: Dict[str, Any], criteria: Dict[str, float], text_criteria: Dict[str, str]) -> int:
    score = 0

    for spec_label, required in criteria.items():
        available = spec_number(device, spec_label)

        if spec_label == "speed":
            if available == required:
                score += 1
        elif available >= required:
            score += 1

    for spec_label, required in text_criteria.items():
        available = spec_text(device, spec_label).lower()
        if available and required.lower() in available:
            score += 1

    return score


def order_by_device_spec_selector(devices: List[Dict[str, Any]], requirement: Dict[str, Any]) -> List[Dict[str, Any]]:
    criteria = spec_selector_requirement_map(requirement)
    text_criteria = spec_selector_text_requirement_map(requirement)
    candidates = [
        device
        for device in devices
        if normalize_model(device.get("model"))
        and device_matches_text_requirements(device, requirement)
    ]

    if not candidates:
        return []

    if not criteria and not text_criteria:
        return sorted(candidates, key=lambda device: (device_price(device) <= 0, device_price(device), model_text(device)))

    scored = [(device_spec_selector_score(device, criteria, text_criteria), device) for device in candidates]
    required_score = len(criteria) + len(text_criteria)
    best_score_devices = [device for score, device in scored if score >= required_score]

    return sorted(best_score_devices, key=lambda device: (device_price(device) <= 0, device_price(device), model_text(device)))


def spec_selector_devices(catalogs: Dict[str, Any], sheet_name: str) -> List[Dict[str, Any]]:
    if sheet_name == "Router":
        return list(catalogs.get("routers", []))
    if sheet_name == "SwitchCampus":
        return list(catalogs.get("switches", []))
    if sheet_name == "ModularSwitch":
        return list(catalogs.get("modular_switches", []))
    if sheet_name == "NexusSwitch":
        return list(catalogs.get("nexus_switches", []))
    if sheet_name == "WiFi":
        return list(catalogs.get("wifi", []))
    if sheet_name == "SFP":
        return list(catalogs.get("sfps", []))
    return []


def spec_selector_sheet_for_line(line: Dict[str, Any]) -> str:
    requirement = line.get("requirement", {}) or {}
    explicit_sheet = str(requirement.get("device_spec_sheet") or "").strip()
    if explicit_sheet:
        return explicit_sheet

    item_type = str(line.get("item_type") or "").lower()
    group = str(line.get("group") or "").lower()

    if item_type.startswith("sfp "):
        return "SFP"
    if "access point" in item_type:
        return "WiFi"
    if "router" in item_type:
        return "Router"
    if "nexus" in item_type or "leaf" in item_type or "dc-sdn" in group:
        return "NexusSwitch"
    if "modular" in item_type or "spine switch" in item_type:
        return "ModularSwitch"
    if "switch" in item_type:
        return "SwitchCampus"

    return ""


def recommend_by_device_specs_sheet(
    catalogs: Dict[str, Any],
    line: Dict[str, Any],
    target_class: str,
) -> List[Dict[str, Any]]:
    requirement = dict(line.get("requirement", {}) or {})
    sheet_name = spec_selector_sheet_for_line(line)

    if not sheet_name:
        return []

    if not requirement.get("preferred_class") and target_class:
        requirement["preferred_class"] = target_class

    devices = spec_selector_devices(catalogs, sheet_name)
    selected = order_by_device_spec_selector(devices, requirement)

    return clone_all(selected, target_class)


def recommend_device_specs_candidates(sheet_name: str, requirement: Dict[str, Any]) -> List[Dict[str, Any]]:
    catalogs = load_catalogs()
    devices = spec_selector_devices(catalogs, sheet_name)
    criteria = dict(requirement or {})
    criteria["device_spec_sheet"] = sheet_name
    selected = order_by_device_spec_selector(devices, criteria)
    result = []

    for device in selected:
        result.append({
            "model": device.get("model", ""),
            "price": device_price(device),
            "class": get_class(device),
            "sheet": device.get("sheet", sheet_name),
            "specs": dict(device.get("specs", {})),
        })

    return result


SERVER_FARM_SFP_OPTION_MODELS = {
    "SFP 100G": {"opt1": "Ficer-100G-10km", "opt2": "QSFP-100G-LR4-S", "opt3": "QSFP-100G-LR4-S"},
    "SFP 10G": {"opt1": "Ficer-10G-10km", "opt2": "SFP-10G-LR", "opt3": "SFP-10G-LR-S"},
    "SFP 1G": {"opt1": "Ficer-1G-10km", "opt2": "GLC-LH-SMD", "opt3": "GLC-SX-MMD"},
}

SERVER_FARM_ACCESS_SWITCH_DEFAULT_MODELS = {
    "Access Switch 48x10G SFP (hoặc Leaf Switch)": {"opt1": "C9500-48Y4C", "opt2": "C9500X-60L4D", "opt3": "C9500X-60L4D"},
    "Access Switch 48x10G RJ45 (hoặc Leaf Switch)": {"opt1": "N9K-C93216TC-FX2", "opt2": "N9K-C93108TC-FX3", "opt3": "N9K-C93108TC-FX3"},
    "Access Switch 48x1G SFP (hoặc Leaf Switch)": {"opt1": "C9300-48S", "opt2": "C9500-48Y4C", "opt3": "C9300-48S"},
    "Access Switch 48x1G RJ45 (hoặc Leaf Switch)": {"opt1": "C1200-48T-4G", "opt2": "C9200L-48T-4X", "opt3": "C9300L-48T-4X"},
}

SERVER_FARM_ACCESS_SWITCH_OPTION_MODELS = {
    "Access Switch 100G (hoặc Leaf Switch)": {"opt1": "Check DC-SDN", "opt2": "Check DC-SDN", "opt3": "Check DC-SDN"},
}

DC_SDN_EXCEL_DEFAULTS = {
    "spine": ["N9K-C9504", "N9K-C9508", "N9K-C9516"],
    "spine_card_100g": ["N9K-X9736C-FX3"],
    "leaf_100g": ["N9K-C93600CD-GX", "N9K-C9316D-GX", "N9K-C9364C-GX"],
    "leaf_10g_sfp": ["N9K-C93360YC-FX2", "N9K-C93240YC-FX2", "N9K-C93180YC-FX3"],
    "leaf_1g_sfp": ["N9K-C93360YC-FX2", "N9K-C93240YC-FX2", "N9K-C93180YC-FX3"],
    "leaf_10g_rj45": ["N9K-C93108TC-FX3", "N9K-C93216TC-FX2"],
    "leaf_1g_rj45": ["N9K-C9348GC-FX3", "N9K-C93108TC-FX3", "N9K-C93216TC-FX2"],
    "sfp_100g_spine_leaf": ["QSFP-100G-LR-S", "QSFP-100G-LR4-S", "Ficer-100G-10km", "Ficer-100G-40km", "Ficer-100G-80km"],
    "sfp_100g_server": ["QSFP-100G-LR-S", "QSFP-100G-LR4-S", "Ficer-100G-10km", "Ficer-100G-40km", "Ficer-100G-80km"],
    "sfp_10g_server": ["SFP-10G-SR", "SFP-10G-SR-S", "Ficer-10G-10km", "Ficer-10G-40km", "Ficer-10G-80km"],
    "sfp_1g_server": ["GLC-SX-MMD", "GLC-LH-SMD", "GLC-EX-SMD", "GLC-ZX-SMD", "Ficer-1G-10km", "Ficer-1G-40km", "Ficer-1G-80km"],
}


def fixed_model_device(model: str, target_class: str, catalogs: Dict[str, Any] | None = None) -> Dict[str, Any]:
    model_key = normalize_model(model)
    if model_key == "Check DC-SDN":
        return {"model": model_key, "sheet": "Excel Note", "class": target_class, "price": 0, "specs": {"selection_source": "excel_note"}}

    for bucket in ["routers", "switches", "modular_switches", "nexus_switches", "wifi", "sfps"]:
        for device in (catalogs or {}).get(bucket, []):
            if normalize_model(device.get("model")) == model_key:
                result = clone_with_class(device, target_class)
                result["model"] = model_key
                if device_price(result) <= 0:
                    prices = (catalogs or {}).get("prices") or read_price_map()
                    result["price"] = prices.get(model_key, 0)
                    if result["price"] <= 0 and model_key == "QSFP-100G-LR4-S":
                        bundle_price = prices.get("100GQSFP-LR4-4", 0)
                        if bundle_price > 0:
                            result["price"] = bundle_price / 4
                result["specs"]["selection_source"] = "excel_fixed_model"
                return result

    prices = (catalogs or {}).get("prices") or read_price_map()
    price = prices.get(model_key, 0)
    if price <= 0 and model_key == "QSFP-100G-LR4-S":
        bundle_price = prices.get("100GQSFP-LR4-4", 0)
        if bundle_price > 0:
            price = bundle_price / 4

    return {"model": model_key, "sheet": "Fixed", "class": target_class, "price": price, "specs": {"selection_source": "excel_fixed_model"}}


def is_server_farm_access_switch_line(line: Dict[str, Any]) -> bool:
    if str(line.get("group") or "").strip().lower() != "server farm":
        return False
    item_type = str(line.get("item_type") or "").strip().lower()
    return item_type.startswith("access switch") and "leaf switch" in item_type


def fixed_option_model_for_line(line: Dict[str, Any], option_key: str) -> str:
    group = str(line.get("group") or "").strip().lower()
    item_type = str(line.get("item_type") or "").strip()
    if group == "server farm":
        return (
            SERVER_FARM_ACCESS_SWITCH_OPTION_MODELS.get(item_type, {}).get(option_key, "")
            or SERVER_FARM_SFP_OPTION_MODELS.get(item_type, {}).get(option_key, "")
        )
    return ""


def dedupe_devices(devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    result = []
    for device in devices:
        model = normalize_model(device.get("model", ""))
        if model and model not in seen:
            seen.add(model)
            result.append(device)
    return result


def order_excel_default_first(devices: List[Dict[str, Any]], default_model: str) -> List[Dict[str, Any]]:
    model_key = normalize_model(default_model)
    if not model_key:
        return devices
    return sorted(devices, key=lambda d: 0 if normalize_model(d.get("model", "")) == model_key else 1)


def sf_access_switch_matches_excel_range(
    device: Dict[str, Any],
    *,
    min_1g_rj45: float = 0,
    min_1g_sfp: float = 0,
    min_10g_rj45: float = 0,
    min_10g_sfp: float = 0,
    min_100g: float = 0,
    device_class: str = "",
) -> bool:
    if device_class and get_class(device) != device_class:
        return False
    return switch_matches_requirement(device, {
        "min_1g_rj45": min_1g_rj45,
        "min_1g_sfp": min_1g_sfp,
        "min_10g_rj45": min_10g_rj45,
        "min_10g_sfp": min_10g_sfp,
        "min_100g": min_100g,
    })


def recommend_server_farm_access_switch(
    catalogs: Dict[str, Any],
    line: Dict[str, Any],
    option_key: str,
    target_class: str,
) -> List[Dict[str, Any]]:
    item_type = str(line.get("item_type") or "").lower()
    switches = list(catalogs.get("switches", []))
    nexus = list(catalogs.get("nexus_switches", []))

    if "100g" in item_type:
        return [fixed_model_device("Check DC-SDN", target_class, catalogs)]
    if "48x10g sfp" in item_type:
        selected = [d for d in switches if sf_access_switch_matches_excel_range(d, min_10g_sfp=48, min_100g=2)]
    elif "48x10g rj45" in item_type:
        if option_key == "opt3":
            selected = [d for d in nexus if sf_access_switch_matches_excel_range(d, min_10g_rj45=48)]
        else:
            selected = [d for d in switches if sf_access_switch_matches_excel_range(d, min_10g_rj45=48, min_100g=2)]
            if not selected:
                selected = [d for d in nexus if sf_access_switch_matches_excel_range(d, min_10g_rj45=48, min_100g=2)]
    elif "48x1g sfp" in item_type:
        selected = [d for d in switches if sf_access_switch_matches_excel_range(d, min_1g_sfp=48, min_10g_sfp=2)]
    elif "48x1g rj45" in item_type:
        class_by_option = {"opt1": "Low End", "opt2": "Mid Range", "opt3": "High End"}
        selected = [
            d for d in switches
            if sf_access_switch_matches_excel_range(
                d,
                min_1g_rj45=48,
                min_10g_sfp=0 if option_key == "opt1" else 2,
                device_class=class_by_option.get(option_key, target_class),
            )
        ]
    else:
        selected = []

    item_key = str(line.get("item_type") or "").strip()
    default_model = SERVER_FARM_ACCESS_SWITCH_DEFAULT_MODELS.get(item_key, {}).get(option_key, "")
    return clone_all(order_excel_default_first(dedupe_devices(selected), default_model), target_class)


def class_fallback_order(target_class: str) -> List[str]:
    return CLASS_FALLBACKS.get(target_class, [target_class])


def select_by_class(
    devices: List[Dict[str, Any]],
    target_class: str,
    class_getter: Callable[[Dict[str, Any]], str] | None = None,
) -> List[Dict[str, Any]]:
    getter = class_getter or get_class

    for class_name in class_fallback_order(target_class):
        selected = [d for d in devices if getter(d) == class_name]

        if selected:
            return selected

    return []


def select_by_class_order(
    devices: List[Dict[str, Any]],
    class_names: List[str],
    class_getter: Callable[[Dict[str, Any]], str] | None = None,
) -> List[Dict[str, Any]]:
    getter = class_getter or get_class

    for class_name in class_names:
        selected = [d for d in devices if getter(d) == class_name]

        if selected:
            return selected

    return []


def clone_with_class(device: Dict[str, Any], target_class: str) -> Dict[str, Any]:
    result = dict(device)
    result["class"] = target_class
    result["price"] = device_price(device)
    result["specs"] = dict(device.get("specs", {}))
    result["specs"]["selection_source"] = "code_selector"
    return result


def sort_devices(devices: List[Dict[str, Any]], key: Callable[[Dict[str, Any]], tuple]) -> List[Dict[str, Any]]:
    return sorted(
        devices,
        key=lambda d: (
            key(d),
            device_price(d) if device_price(d) > 0 else float("inf"),
            normalize_model(d.get("model", "")),
        ),
    )


def clone_all(devices: List[Dict[str, Any]], target_class: str) -> List[Dict[str, Any]]:
    return [clone_with_class(d, target_class) for d in devices]


def router_bucket(device: Dict[str, Any], item_type: str) -> str:
    current_class = get_class(device)

    if current_class:
        return current_class

    model = model_text(device)
    throughput = spec_number(device, "Throughput (Mbps)")
    item = item_type.lower()

    if "gateway" in item:
        if model.startswith("C8500"):
            return "High End"
        if model.startswith("C8200") or model.startswith("C8300"):
            return "Mid Range"
        return "Low End"

    if "lớn" in item or "lon" in item:
        if model.startswith("C8500"):
            return "High End"
        if model.startswith("C8300") and throughput > 2000:
            return "Mid Range"
        return "Low End"

    if model.startswith(("C11", "C110", "C112", "C113", "C116")):
        return "Low End"

    if model.startswith("C8500"):
        return "High End"

    return "Mid Range"


def router_matches_requirement(device: Dict[str, Any], requirement: Dict[str, Any]) -> bool:
    throughput = spec_number(device, "Throughput (Mbps)")
    wan_1g = spec_number(device, "Số lượng cổng WAN 1GE")
    wan_10g = spec_number(device, "Số lượng cổng WAN 10GE")
    lan_1g = spec_number(device, "Số lượng cổng LAN 1GE")

    required_throughput = float(requirement.get("throughput_mbps") or 0)
    required_wan_1g = float(requirement.get("min_wan_1g") or 0)
    required_wan_10g = float(requirement.get("min_wan_10g") or 0)
    required_lan_1g = float(requirement.get("min_lan_1g") or 0)

    if throughput < required_throughput:
        return False

    if wan_1g < required_wan_1g:
        return False

    if wan_10g < required_wan_10g:
        return False

    # Some high-end routers expose routed 1G ports as WAN ports in the specs.
    if required_lan_1g and max(lan_1g, wan_1g) < required_lan_1g:
        return False

    return True


def recommend_routers(
    catalogs: Dict[str, Any],
    line: Dict[str, Any],
    target_class: str,
) -> List[Dict[str, Any]]:
    item_type = str(line.get("item_type") or "")
    requirement = line.get("requirement", {})
    item_lower = item_type.lower()
    is_wan_small = (
        requirement.get("wan_router_size") == "Small"
        or "vừa/nhỏ" in item_lower
        or "vua/nho" in item_lower
    )
    is_wan_large = (
        requirement.get("wan_router_size") == "Large"
        or "loại lớn" in item_lower
        or "loai lon" in item_lower
    )

    if is_wan_small:
        matching = [
            d
            for d in catalogs.get("routers", [])
            if spec_number(d, "Throughput (Mbps)") <= 2000
            and spec_number(d, "Throughput (Mbps)") > 0
            and (
                spec_number(d, "Số lượng cổng WAN 1GE")
                + spec_number(d, "Số lượng cổng WAN 10GE")
            ) >= 2
        ]
    elif is_wan_large:
        matching = [
            d
            for d in catalogs.get("routers", [])
            if spec_number(d, "Throughput (Mbps)") > 2000
            and (
                spec_number(d, "Số lượng cổng WAN 1GE")
                + spec_number(d, "Số lượng cổng WAN 10GE")
            ) >= 2
        ]
    else:
        matching = [
            d
            for d in catalogs.get("routers", [])
            if router_matches_requirement(d, requirement)
        ]

    if is_wan_small and target_class == "High End":
        selected = select_by_class_order(
            matching,
            ["Mid Range", "High End"],
            class_getter=lambda d: router_bucket(d, item_type),
        )
    else:
        selected = select_by_class(
            matching,
            target_class,
            class_getter=lambda d: router_bucket(d, item_type),
        )

    return clone_all(selected, target_class)

def switch_matches_requirement(device: Dict[str, Any], requirement: Dict[str, Any]) -> bool:
    checks = [
        ("min_1g_rj45", "Số lượng cổng 1GE đồng"),
        ("min_1g_sfp", "Số lượng cổng 1GE SFP"),
        ("min_10g_rj45", "Số lượng cổng 10GE đồng"),
        ("min_10g_sfp", "Số lượng cổng 10GE quang"),
        ("min_100g", "Số lượng cổng 100GE"),
    ]

    for req_key, spec_key in checks:
        required = float(requirement.get(req_key) or 0)
        if required and spec_number(device, spec_key) < required:
            return False

    return True


def port_range_match(device: Dict[str, Any], lower: float, upper: float | None = None) -> bool:
    ports = spec_number(device, "Số lượng cổng 1GE đồng")

    if ports < lower:
        return False

    if upper is not None and ports >= upper:
        return False

    return True


def select_access_switch_rj45(
    candidates: List[Dict[str, Any]],
    target_class: str,
    requested_ports: float,
) -> List[Dict[str, Any]]:
    class_devices = [d for d in candidates if get_class(d) == target_class]

    if requested_ports >= 48:
        ranges = [(48, None)]
    elif requested_ports >= 24:
        ranges = [(24, 48), (48, None)]
    elif requested_ports >= 16:
        ranges = [(16, 24), (24, 48), (48, None)]
    else:
        ranges = [(8, 16), (16, 24), (24, 48), (48, None)]

    for lower, upper in ranges:
        selected = [d for d in class_devices if port_range_match(d, lower, upper)]

        if selected:
            return selected

    return []


def select_1g_sfp_switch(
    candidates: List[Dict[str, Any]],
    target_class: str,
    requested_ports: float,
    requirement: Dict[str, Any],
) -> List[Dict[str, Any]]:
    if requested_ports >= 48:
        ranges = [(48, None)]
    else:
        ranges = [(24, 48), (48, None)]

    for class_name in class_fallback_order(target_class):
        class_devices = [d for d in candidates if get_class(d) == class_name]

        for lower, upper in ranges:
            selected = [
                d
                for d in class_devices
                if port_range_match_sfp(d, lower, upper)
                and switch_matches_requirement(
                    d,
                    {k: v for k, v in requirement.items() if k != "min_1g_sfp"},
                )
            ]

            if selected:
                return selected

    return []


def port_range_match_sfp(device: Dict[str, Any], lower: float, upper: float | None = None) -> bool:
    ports = spec_number(device, "Số lượng cổng 1GE SFP")

    if ports < lower:
        return False

    if upper is not None and ports >= upper:
        return False

    return True


def recommend_switches(
    catalogs: Dict[str, Any],
    line: Dict[str, Any],
    target_class: str,
) -> List[Dict[str, Any]]:
    item_type = str(line.get("item_type") or "").lower()
    requirement = line.get("requirement", {})
    candidates = list(catalogs.get("switches", []))

    if "core switch modular" in item_type or "spine switch" in item_type:
        candidates = list(catalogs.get("modular_switches", []))
    elif requirement.get("min_100g"):
        candidates = list(catalogs.get("switches", [])) + list(catalogs.get("modular_switches", []))

    matching = [
        d
        for d in candidates
        if switch_matches_requirement(d, requirement)
    ]

    requested_rj45 = float(requirement.get("min_1g_rj45") or 0)

    requested_1g_sfp = float(requirement.get("min_1g_sfp") or 0)

    if (
        "core switch" in item_type
        and "ge sfp" in item_type
        and requested_1g_sfp
    ):
        selected = select_1g_sfp_switch(candidates, target_class, requested_1g_sfp, requirement)
    elif "access switch" in item_type and "rj45" in item_type and requested_rj45:
        selected = select_access_switch_rj45(candidates, target_class, requested_rj45)
    else:
        selected = select_by_class(matching, target_class)

    if not selected and ("core switch" in item_type or "spine switch" in item_type):
        selected = matching

    return clone_all(selected, target_class)


def wifi_bucket(device: Dict[str, Any]) -> str:
    current_class = get_class(device)

    if current_class:
        return current_class

    technology = spec_text(device, "Công nghệ WiFi (WiFi6/WiFi7)").upper()

    if "WIFI7" in technology:
        return "High End"

    if "WIFI6" in technology or "6E" in technology:
        return "Mid Range"

    return ""


def recommend_wifi(
    catalogs: Dict[str, Any],
    line: Dict[str, Any],
    target_class: str,
) -> List[Dict[str, Any]]:
    requirement = line.get("requirement", {})
    ap_type = str(requirement.get("ap_type") or "").lower()
    wifi_devices = list(catalogs.get("wifi", []))
    campus_start = next(
        (index for index, device in enumerate(wifi_devices) if normalize_model(device.get("model")) == "CW9164I"),
        None,
    )

    if campus_start is not None:
        wifi_devices = wifi_devices[campus_start:]

    matching = [
        d
        for d in wifi_devices
        if not ap_type or spec_text(d, "Loại Access Point (indoor/outdoor)").lower() == ap_type
    ]

    selected = select_by_class(matching, target_class, class_getter=wifi_bucket)

    return clone_all(selected, target_class)


def sfp_bucket(device: Dict[str, Any]) -> str:
    current = get_class(device)

    if current:
        return current

    return "High End"


def recommend_sfps(
    catalogs: Dict[str, Any],
    line: Dict[str, Any],
    target_class: str,
) -> List[Dict[str, Any]]:
    requirement = line.get("requirement", {})
    speed = float(requirement.get("speed") or 0)
    distance = float(requirement.get("distance") or 0)

    matching = []

    for device in catalogs.get("sfps", []):
        if speed and spec_number(device, "speed") != speed:
            continue

        if (
            distance
            and not (target_class == "High End" and speed == 1 and distance == 10)
            and spec_number(device, "distance") != distance
        ):
            continue

        matching.append(device)

    selected = select_by_class(matching, target_class, class_getter=sfp_bucket)

    if target_class == "High End" and speed == 1 and distance == 10:
        selected = [
            d
            for d in selected
            if normalize_model(d.get("model")) == "GLC-SX-MMD"
        ] or selected

    return clone_all(selected, target_class)


def is_dc_sdn_line(line: Dict[str, Any]) -> bool:
    return str(line.get("group") or "").strip().lower() == "dc-sdn"


def model_in_excel_default_order(devices: List[Dict[str, Any]], order: List[str]) -> List[Dict[str, Any]]:
    rank = {normalize_model(model): index for index, model in enumerate(order)}
    return sorted(
        devices,
        key=lambda d: (
            rank.get(normalize_model(d.get("model", "")), len(rank) + 1),
            device_price(d) if device_price(d) > 0 else float("inf"),
            normalize_model(d.get("model", "")),
        ),
    )


def dc_sdn_switch_matches(device: Dict[str, Any], requirement: Dict[str, Any]) -> bool:
    model = normalize_model(device.get("model", ""))
    prefix = normalize_model(requirement.get("model_prefix", ""))
    contains = str(requirement.get("model_contains") or "")

    if prefix and not model.startswith(prefix):
        return False

    if contains and contains not in str(device.get("model", "")) and contains not in model:
        return False

    return switch_matches_requirement(device, requirement)


def recommend_dc_sdn(catalogs: Dict[str, Any], line: Dict[str, Any], target_class: str) -> List[Dict[str, Any]]:
    requirement = line.get("requirement", {})
    role = str(requirement.get("dc_sdn_role") or "")
    default_model = str(requirement.get("default_model") or "")
    excel_order = DC_SDN_EXCEL_DEFAULTS.get(role, [])

    if not role:
        return recommend_for_line_and_class(catalogs, line, target_class)

    if role.startswith("sfp_"):
        speed = float(requirement.get("speed") or 0)
        max_distance = float(requirement.get("max_distance") or 10)
        selected = [
            d for d in catalogs.get("sfps", [])
            if (not speed or spec_number(d, "speed") == speed)
            and (not max_distance or spec_number(d, "distance") <= max_distance)
        ]
    else:
        selected = [
            d for d in catalogs.get("nexus_switches", [])
            if dc_sdn_switch_matches(d, requirement)
        ]

    if excel_order:
        selected = [
            d for d in selected
            if normalize_model(d.get("model", "")) in {normalize_model(m) for m in excel_order}
        ] or selected
        selected = model_in_excel_default_order(dedupe_devices(selected), excel_order)
    else:
        selected = dedupe_devices(selected)

    if default_model:
        selected = order_excel_default_first(selected, default_model)

    if not selected and default_model:
        selected = [fixed_model_device(default_model, target_class, catalogs)]

    return clone_all(selected, target_class)


def recommend_for_line_and_class(
    catalogs: Dict[str, Any],
    line: Dict[str, Any],
    target_class: str,
) -> List[Dict[str, Any]]:
    item_type = str(line.get("item_type") or "").lower()
    requirement = line.get("requirement", {})

    if requirement.get("fixed_model"):
        return [fixed_model_device(requirement["fixed_model"], target_class, catalogs)]

    if "router" in item_type:
        return recommend_routers(catalogs, line, target_class)

    if "access point" in item_type:
        return recommend_wifi(catalogs, line, target_class)

    if item_type.startswith("sfp "):
        return recommend_sfps(catalogs, line, target_class)

    if "switch" in item_type:
        return recommend_switches(catalogs, line, target_class)

    return []


def normalize_recommendation_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {
            "model": r.get("model", ""),
            "price": r.get("price", 0),
            "class": r.get("class", get_class(r)),
            "sheet": r.get("sheet", ""),
        }
        for r in items
    ]


def recommend_for_line(line: Dict[str, Any], use_device_specs_selector: bool = False) -> Dict[str, Any]:
    catalogs = load_catalogs()
    options = {}
    preferred_class = str((line.get("requirement") or {}).get("preferred_class") or "").strip()
    valid_classes = {target_class for _, target_class in OPTION_CLASSES}
    if preferred_class not in valid_classes:
        preferred_class = ""

    for opt_name, target_class in OPTION_CLASSES:
        effective_class = preferred_class or target_class
        if is_dc_sdn_line(line):
            recs = recommend_dc_sdn(catalogs, line, effective_class)
        elif is_server_farm_access_switch_line(line):
            recs = recommend_server_farm_access_switch(catalogs, line, opt_name, effective_class)
        elif use_device_specs_selector:
            recs = recommend_by_device_specs_sheet(catalogs, line, effective_class)
            if not recs:
                recs = recommend_for_line_and_class(catalogs, line, effective_class)
        else:
            fixed_option_model = fixed_option_model_for_line(line, opt_name)
            if fixed_option_model:
                recs = [fixed_model_device(fixed_option_model, effective_class, catalogs)]
            else:
                recs = recommend_for_line_and_class(catalogs, line, effective_class)
        options[opt_name] = normalize_recommendation_items(recs)

    return {
        **line,
        "options": options,
    }


def recommend_all(requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    catalogs = load_catalogs()
    result = []

    for line in requirements:
        options = {}

        for opt_name, target_class in OPTION_CLASSES:
            if is_dc_sdn_line(line):
                recs = recommend_dc_sdn(catalogs, line, target_class)
            elif is_server_farm_access_switch_line(line):
                recs = recommend_server_farm_access_switch(catalogs, line, opt_name, target_class)
            else:
                fixed_option_model = fixed_option_model_for_line(line, opt_name)
                if fixed_option_model:
                    recs = [fixed_model_device(fixed_option_model, target_class, catalogs)]
                else:
                    recs = recommend_for_line_and_class(catalogs, line, target_class)
            options[opt_name] = normalize_recommendation_items(recs)

        result.append({
            **line,
            "options": options,
        })

    return result
