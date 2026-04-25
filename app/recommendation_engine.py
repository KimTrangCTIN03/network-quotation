from typing import Any, Dict, List

from app.catalog_engine import load_catalogs, normalize_model, normalize_proposal_key


CLASS_ORDER = {
    "Low End": ["Low End", "Mid Range", "High End"],
    "Mid Range": ["Mid Range", "High End", "Low End"],
    "High End": ["High End", "Mid Range", "Low End"],
}


def safe_float(value: Any) -> float:
    if value is None or value == "":
        return 0

    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip().replace(",", "")

    try:
        return float(text)
    except Exception:
        return 0


def spec_num(device: Dict[str, Any], contains: str) -> float:
    contains = contains.lower()

    for key, value in device.get("specs", {}).items():
        if contains in str(key).lower():
            return safe_float(value)

    return 0


def spec_num_any(device: Dict[str, Any], keywords: List[str]) -> float:
    for keyword in keywords:
        value = spec_num(device, keyword)
        if value > 0:
            return value

    return 0


def get_class(device: Dict[str, Any]) -> str:
    if device.get("class"):
        return str(device.get("class")).strip()

    for key, value in device.get("specs", {}).items():
        if "class" in str(key).lower():
            return str(value or "").strip()

    return ""


def filter_by_class(devices: List[Dict[str, Any]], target_class: str) -> List[Dict[str, Any]]:
    allowed = CLASS_ORDER.get(target_class, [target_class])

    for cls in allowed:
        same_cls = [d for d in devices if get_class(d) == cls]
        if same_cls:
            return same_cls

    return devices


def fallback_top_price(devices: List[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
    devices = [d for d in devices if d.get("model")]
    devices = sorted(devices, key=lambda x: x.get("price", 0) or 0)
    return devices[:limit]


def find_device_in_all_catalogs(catalogs: Dict[str, Any], model: str) -> Dict[str, Any]:
    """
    Tìm model trong tất cả catalog đã đọc từ Devices Specs.
    So sánh bằng normalize_model để:
    - GLC-SX-MMD= match được GLC-SX-MMD
    - C9404R có khoảng trắng vẫn match được C9404R
    """
    model_key = normalize_model(model)

    all_devices = []
    all_devices.extend(catalogs.get("routers", []))
    all_devices.extend(catalogs.get("switches", []))
    all_devices.extend(catalogs.get("modular_switches", []))
    all_devices.extend(catalogs.get("wifi", []))
    all_devices.extend(catalogs.get("sfps", []))

    for device in all_devices:
        if normalize_model(device.get("model")) == model_key:
            return dict(device)

    return {}


def build_mapped_device(
    catalogs: Dict[str, Any],
    model: str,
    target_class: str,
    fallback_sheet: str = "Campus dropdown",
) -> Dict[str, Any]:
    """
    Tạo device từ model lấy từ dropdown của tab Campus.

    Model hiển thị giữ nguyên như Excel.
    Giá lookup bằng normalize_model từ Cisco Unit List Price.
    """
    display_model = str(model or "").strip()
    model_key = normalize_model(display_model)

    price = (
        catalogs.get("prices", {}).get(model_key)
        or catalogs.get("prices", {}).get(display_model)
        or 0
    )

    found = find_device_in_all_catalogs(catalogs, display_model)

    if found:
        found["model"] = display_model
        found["class"] = target_class
        found["price"] = price if price > 0 else found.get("price", 0)
        found["sheet"] = found.get("sheet") or fallback_sheet
        return found

    return {
        "model": display_model,
        "price": price,
        "class": target_class,
        "sheet": fallback_sheet,
        "specs": {
            "source": "Campus data validation",
            "normalized_model": model_key,
        }
    }


def get_mapped_models_for_line(
    catalogs: Dict[str, Any],
    line: Dict[str, Any],
    target_class: str,
) -> List[str]:
    """
    Lấy đúng danh sách model theo từng dòng proposal.

    Ưu tiên:
    1. group||item_type
       Ví dụ: Server Farm||Core Switch (hoặc Spine Switch)

    2. item_type
       Ví dụ: Core Switch (hoặc Spine Switch)
    """
    proposal_map = catalogs.get("proposal_option_map", {})

    group_key = normalize_proposal_key(line.get("group", ""))
    item_key = normalize_proposal_key(line.get("item_type", ""))

    candidate_keys = []

    if group_key and item_key:
        candidate_keys.append(normalize_proposal_key(f"{group_key}||{item_key}"))

    if item_key:
        candidate_keys.append(item_key)

    for key in candidate_keys:
        models = proposal_map.get(key, {}).get(target_class, [])

        if models:
            return models

    return []


def recommend_from_campus_calculation(
    line: Dict[str, Any],
    target_class: str,
) -> List[Dict[str, Any]]:
    """
    Ưu tiên chọn model đúng theo dropdown/data validation của tab Campus.
    """
    catalogs = load_catalogs()

    mapped_models = get_mapped_models_for_line(
        catalogs=catalogs,
        line=line,
        target_class=target_class,
    )

    if not mapped_models:
        return []

    return [
        build_mapped_device(
            catalogs=catalogs,
            model=model,
            target_class=target_class,
        )
        for model in mapped_models
    ]


def recommend_router(requirement: Dict[str, Any], target_class: str) -> List[Dict[str, Any]]:
    catalogs = load_catalogs()
    routers = catalogs["routers"]

    throughput = float(requirement.get("throughput_mbps", 0))
    min_wan_1g = float(requirement.get("min_wan_1g", 0))
    min_wan_10g = float(requirement.get("min_wan_10g", 0))
    min_lan_1g = float(requirement.get("min_lan_1g", 0))

    candidates = []

    for router in routers:
        router_throughput = spec_num_any(router, [
            "throughput",
            "performance",
            "routing throughput",
        ])

        if throughput > 0 and router_throughput > 0 and router_throughput < throughput:
            continue

        if min_wan_1g > 0:
            value = spec_num_any(router, [
                "wan 1ge",
                "wan 1g",
                "1ge wan",
                "1g wan",
            ])
            if value < min_wan_1g:
                continue

        if min_wan_10g > 0:
            value = spec_num_any(router, [
                "wan 10ge",
                "wan 10g",
                "10ge wan",
                "10g wan",
            ])
            if value < min_wan_10g:
                continue

        if min_lan_1g > 0:
            value = spec_num_any(router, [
                "lan 1ge",
                "lan 1g",
                "1ge lan",
                "1g lan",
            ])
            if value < min_lan_1g:
                continue

        candidates.append(router)

    if not candidates:
        candidates = fallback_top_price(routers, 5)

    candidates = filter_by_class(candidates, target_class)

    return sorted(candidates, key=lambda x: x.get("price", 0) or 0)[:5]


def recommend_switch(requirement: Dict[str, Any], target_class: str) -> List[Dict[str, Any]]:
    catalogs = load_catalogs()
    switches = catalogs["switches"]

    min_1g_rj45 = float(requirement.get("min_1g_rj45", 0))
    min_1g_sfp = float(requirement.get("min_1g_sfp", 0))
    min_10g_rj45 = float(requirement.get("min_10g_rj45", 0))
    min_10g_sfp = float(requirement.get("min_10g_sfp", 0))
    min_100g = float(requirement.get("min_100g", 0))

    candidates = []

    for sw in switches:
        if min_1g_rj45 > 0:
            value = spec_num_any(sw, [
                "1ge đồng",
                "1ge rj45",
                "1g rj45",
                "1g đồng",
                "copper 1g",
                "1ge copper",
                "1g copper",
            ])
            if value < min_1g_rj45:
                continue

        if min_1g_sfp > 0:
            value = spec_num_any(sw, [
                "1ge sfp",
                "1g sfp",
                "sfp 1g",
                "sfp 1ge",
            ])
            if value < min_1g_sfp:
                continue

        if min_10g_rj45 > 0:
            value = spec_num_any(sw, [
                "10ge rj45",
                "10g rj45",
                "10ge đồng",
                "10g đồng",
                "copper 10g",
                "10ge copper",
                "10g copper",
            ])
            if value < min_10g_rj45:
                continue

        if min_10g_sfp > 0:
            value = spec_num_any(sw, [
                "10ge sfp",
                "10g sfp",
                "sfp 10g",
                "sfp 10ge",
            ])
            if value < min_10g_sfp:
                continue

        if min_100g > 0:
            value = spec_num_any(sw, [
                "100ge",
                "100g",
                "100ge qsfp",
                "100g qsfp",
            ])
            if value < min_100g:
                continue

        candidates.append(sw)

    if not candidates:
        candidates = fallback_top_price(switches, 5)

    candidates = filter_by_class(candidates, target_class)

    return sorted(candidates, key=lambda x: x.get("price", 0) or 0)[:5]


def recommend_modular(requirement: Dict[str, Any], target_class: str) -> List[Dict[str, Any]]:
    catalogs = load_catalogs()
    devices = catalogs["modular_switches"]

    min_total_ports = float(requirement.get("min_total_access_ports", 0))
    min_100g = float(requirement.get("min_100g", 0))

    candidates = []

    for device in devices:
        total_ports = (
            spec_num_any(device, [
                "1ge đồng",
                "1ge rj45",
                "1g rj45",
                "1g đồng",
                "copper 1g",
            ])
            + spec_num_any(device, [
                "1ge sfp",
                "1g sfp",
                "sfp 1g",
                "sfp 1ge",
            ])
        )

        if min_total_ports > 0 and total_ports > 0 and total_ports < min_total_ports:
            continue

        if min_100g > 0:
            value = spec_num_any(device, [
                "100ge",
                "100g",
                "100ge qsfp",
                "100g qsfp",
            ])
            if value < min_100g:
                continue

        candidates.append(device)

    if not candidates:
        candidates = fallback_top_price(devices, 5)

    candidates = filter_by_class(candidates, target_class)

    return sorted(candidates, key=lambda x: x.get("price", 0) or 0)[:5]


def recommend_sfp(requirement: Dict[str, Any], target_class: str) -> List[Dict[str, Any]]:
    catalogs = load_catalogs()
    sfps = catalogs.get("sfps", [])

    speed = float(requirement.get("speed", 0))
    distance = float(requirement.get("distance", 0))

    candidates = []

    for sfp in sfps:
        sfp_speed = float(sfp.get("speed", 0) or 0)
        sfp_distance = float(sfp.get("distance", 0) or 0)

        if speed > 0 and sfp_speed > 0 and sfp_speed != speed:
            continue

        if distance > 0 and sfp_distance > 0 and sfp_distance < distance:
            continue

        candidates.append(sfp)

    if not candidates and speed > 0:
        speed_text = f"{int(speed)}G"

        for sfp in sfps:
            model_text = str(sfp.get("model", "")).upper()

            if speed_text in model_text:
                candidates.append(sfp)

    if not candidates:
        candidates = fallback_top_price(sfps, 10)

    if not candidates:
        return []

    candidates = filter_by_class(candidates, target_class)

    return sorted(candidates, key=lambda x: x.get("price", 0) or 0)[:10]


def recommend_wifi(requirement: Dict[str, Any], target_class: str) -> List[Dict[str, Any]]:
    catalogs = load_catalogs()
    wifi_devices = catalogs.get("wifi", [])

    ap_type = str(requirement.get("ap_type", "")).lower()

    candidates = []

    for ap in wifi_devices:
        specs_text = " ".join(
            f"{k} {v}" for k, v in ap.get("specs", {}).items()
        ).lower()

        model_text = ap.get("model", "").lower()

        if ap_type == "outdoor":
            if "outdoor" not in specs_text and "outdoor" not in model_text:
                continue

        if ap_type == "indoor":
            if "outdoor" in specs_text or "outdoor" in model_text:
                continue

        candidates.append(ap)

    if not candidates:
        candidates = wifi_devices[:]

    if not candidates:
        return []

    candidates = filter_by_class(candidates, target_class)

    return sorted(candidates, key=lambda x: x.get("price", 0) or 0)[:5]


def recommend_firewall(requirement: Dict[str, Any], target_class: str) -> List[Dict[str, Any]]:
    """
    Firewall sẽ được lấy từ Campus dropdown nếu có mapping.
    Nếu không có mapping thì tạm chưa recommend.
    """
    return []


def normalize_recommendation_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {
            "model": r.get("model", ""),
            "price": r.get("price", 0),
            "class": r.get("class", get_class(r)),
            "sheet": r.get("sheet", "")
        }
        for r in items
    ]


def recommend_for_line(line: Dict[str, Any]) -> Dict[str, Any]:
    item_type = line["item_type"]
    requirement = line.get("requirement", {})

    options = {}

    for opt_name, target_class in [
        ("opt1", "Low End"),
        ("opt2", "Mid Range"),
        ("opt3", "High End"),
    ]:
        # 1. Ưu tiên tuyệt đối model lấy từ dropdown/data validation của tab Campus
        recs = recommend_from_campus_calculation(line, target_class)

        # 2. Nếu không có dropdown mapping thì fallback sang filter specs
        if not recs:
            if "Router" in item_type:
                recs = recommend_router(requirement, target_class)

            elif "Firewall" in item_type:
                recs = recommend_firewall(requirement, target_class)

            elif "Modular" in item_type:
                recs = recommend_modular(requirement, target_class)

            elif "Switch" in item_type:
                recs = recommend_switch(requirement, target_class)

            elif item_type.strip().startswith("SFP"):
                recs = recommend_sfp(requirement, target_class)

            elif "Access Point" in item_type:
                recs = recommend_wifi(requirement, target_class)

            else:
                recs = []

        options[opt_name] = normalize_recommendation_items(recs)

    return {
        **line,
        "options": options
    }


def recommend_all(requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [recommend_for_line(line) for line in requirements]