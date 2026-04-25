from typing import Any, Callable, Dict, List

from app.catalog_engine import load_catalogs, normalize_model


OPTION_CLASSES = [
    ("opt1", "Low End"),
    ("opt2", "Mid Range"),
    ("opt3", "High End"),
]

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


def recommend_for_line_and_class(
    catalogs: Dict[str, Any],
    line: Dict[str, Any],
    target_class: str,
) -> List[Dict[str, Any]]:
    item_type = str(line.get("item_type") or "").lower()

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


def recommend_for_line(line: Dict[str, Any]) -> Dict[str, Any]:
    catalogs = load_catalogs()
    options = {}

    for opt_name, target_class in OPTION_CLASSES:
        recs = recommend_for_line_and_class(catalogs, line, target_class)
        options[opt_name] = normalize_recommendation_items(recs)

    return {
        **line,
        "options": options,
    }


def recommend_all(requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [recommend_for_line(line) for line in requirements]
