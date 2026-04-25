from pathlib import Path
from functools import lru_cache
from typing import Any, Dict, List
import re

import openpyxl


DATA_DIR = Path("data")

SPECS_FILE = DATA_DIR / "Devices Specs_240426.xlsx"
PRICE_FILE = DATA_DIR / "Cisco Unit List Price_240426.xlsx"


SOURCE_BOM_SHEETS = [
    "C8000",
    "C9200",
    "C9300",
    "C1300",
    "C9500",
    "ACI",
    "ISR1000",
    "C8000_secure",
    "SFP",
    "AP",
]


def normalize_model(value: Any) -> str:
    if value is None:
        return ""

    text = str(value).strip()

    if not text:
        return ""

    text = text.rstrip("=")

    for suffix in ["-A", "-ROW", "-RTG"]:
        if text.endswith(suffix):
            text = text[: -len(suffix)]

    return text.strip()


def normalize_proposal_key(value: Any) -> str:
    if value is None:
        return ""

    text = str(value).strip().replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)

    return text


def parse_google_export_formula(value: Any) -> Any:
    if value is None:
        return None

    if not isinstance(value, str):
        return value

    text = value.strip()

    if not text.startswith("="):
        return text

    m = re.search(r',\s*"([^"]*)"\s*\)\s*$', text)
    if m:
        return m.group(1)

    m = re.search(r',\s*(-?\d+(?:\.\d+)?)\s*\)\s*$', text)
    if m:
        number = float(m.group(1))
        return int(number) if number.is_integer() else number

    return None


def resolve_simple_ref(wb, formula: str) -> Any:
    if not isinstance(formula, str):
        return formula

    text = formula.strip()

    m = re.fullmatch(r"='?([^'!]+)'?!([A-Z]+)(\d+)", text)
    if not m:
        return None

    sheet_name = m.group(1)
    cell_ref = f"{m.group(2)}{m.group(3)}"

    if sheet_name not in wb.sheetnames:
        return None

    return parse_google_export_formula(wb[sheet_name][cell_ref].value)


def cell_value(wb, ws, row: int, col: int) -> Any:
    raw = ws.cell(row=row, column=col).value

    if isinstance(raw, str) and raw.startswith("="):
        ref_value = resolve_simple_ref(wb, raw)

        if ref_value is not None:
            return ref_value

    return parse_google_export_formula(raw)


def to_float(value: Any, default: float = 0) -> float:
    value = parse_google_export_formula(value)

    if value is None or value == "":
        return default

    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip().replace(",", "")

    try:
        return float(text)
    except Exception:
        pass

    if re.fullmatch(r"[\d\.\+\-\*/\(\)\s]+", text):
        try:
            return float(eval(text, {"__builtins__": {}}))
        except Exception:
            return default

    return default


def is_integer_line_number(value: Any) -> bool:
    if value is None:
        return False

    text = str(value).strip()

    return re.fullmatch(r"\d+(\.0)?", text) is not None


def sheet_exists(file_path: Path, sheet_name: str) -> bool:
    if not file_path.exists():
        return False

    wb = openpyxl.load_workbook(file_path, read_only=True, data_only=False)

    return sheet_name in wb.sheetnames


@lru_cache(maxsize=1)
def read_price_map() -> Dict[str, float]:
    if not PRICE_FILE.exists():
        return {}

    wb = openpyxl.load_workbook(PRICE_FILE, data_only=False)

    price_map: Dict[str, float] = {}

    if "Cisco" in wb.sheetnames:
        ws = wb["Cisco"]

        for row in range(2, ws.max_row + 1):
            model = normalize_model(cell_value(wb, ws, row, 1))

            if not model:
                continue

            list_price = to_float(cell_value(wb, ws, row, 2), 0)
            am_price = to_float(cell_value(wb, ws, row, 3), 0)
            final_price = to_float(cell_value(wb, ws, row, 4), 0)

            if final_price <= 0:
                final_price = am_price if am_price > 0 else list_price

            if final_price > 0:
                price_map[model] = final_price

    bom_price_map = read_price_map_from_bom_tabs(wb)

    for model, price in bom_price_map.items():
        if model not in price_map and price > 0:
            price_map[model] = price

    return price_map


def read_price_map_from_bom_tabs(wb) -> Dict[str, float]:
    result: Dict[str, float] = {}

    for sheet_name in SOURCE_BOM_SHEETS:
        if sheet_name not in wb.sheetnames:
            continue

        ws = wb[sheet_name]

        read_aggregated_sheet_prices(wb, ws, result)

        base_models = []
        subtotals = []

        for row in range(2, ws.max_row + 1):
            line_number = cell_value(wb, ws, row, 1)
            item_name = cell_value(wb, ws, row, 2)

            if is_integer_line_number(line_number) and item_name:
                base_models.append(normalize_model(item_name))

            label_m = cell_value(wb, ws, row, 13)
            subtotal_n = cell_value(wb, ws, row, 14)

            if str(label_m or "").strip().lower() == "subtotal":
                price = to_float(subtotal_n, 0)

                if price > 0:
                    subtotals.append(price)

        for model, price in zip(base_models, subtotals):
            if model and price > 0:
                result[model] = price

    return result


def read_aggregated_sheet_prices(wb, ws, result: Dict[str, float]) -> None:
    header_map = {}

    for col in range(1, ws.max_column + 1):
        header = cell_value(wb, ws, 1, col)

        if header is None:
            continue

        header_map[str(header).strip().lower()] = col

    possible_device_cols = [
        header_map.get("devices"),
        header_map.get("device"),
        header_map.get("item name"),
    ]

    possible_price_cols = [
        header_map.get("final price"),
        header_map.get("price base"),
        header_map.get("list price"),
    ]

    device_cols = [c for c in possible_device_cols if c]
    price_cols = [c for c in possible_price_cols if c]

    if not device_cols or not price_cols:
        return

    device_col = device_cols[0]
    price_col = price_cols[-1]

    for row in range(2, ws.max_row + 1):
        model = normalize_model(cell_value(wb, ws, row, device_col))
        price = to_float(cell_value(wb, ws, row, price_col), 0)

        if model and price > 0:
            result[model] = price


CLASS_VALUES = {"Low End", "Mid Range", "High End"}


def normalize_device_class(value: Any) -> str:
    text = str(value or "").strip()

    for class_name in CLASS_VALUES:
        if text.lower() == class_name.lower():
            return class_name

    return ""


def find_class_in_specs(specs: Dict[str, Any]) -> str:
    for key, value in specs.items():
        if "class" in str(key).lower():
            class_name = normalize_device_class(value)

            if class_name:
                return class_name

    return ""


def infer_wifi_class(specs: Dict[str, Any]) -> str:
    technology = str(specs.get("Công nghệ WiFi (WiFi6/WiFi7)") or "").upper()

    if "WIFI7" in technology:
        return "High End"

    if "WIFI6" in technology:
        return "Mid Range"

    return ""


def read_specs_matrix_sheet(sheet_name: str) -> List[Dict[str, Any]]:
    if not SPECS_FILE.exists():
        return []

    wb = openpyxl.load_workbook(SPECS_FILE, data_only=False)

    if sheet_name not in wb.sheetnames:
        return []

    ws = wb[sheet_name]
    price_map = read_price_map()

    row_labels: Dict[int, str] = {}

    for row in range(1, min(ws.max_row, 150) + 1):
        label = cell_value(wb, ws, row, 1)

        if label:
            row_labels[row] = str(label).strip()

    devices: List[Dict[str, Any]] = []

    for col in range(2, ws.max_column + 1):
        model = normalize_model(cell_value(wb, ws, 1, col))

        if not model or model == "Requirement" or model.startswith("<openpyxl."):
            continue

        specs = {}
        label_counts: Dict[str, int] = {}

        for row, label in row_labels.items():
            value = cell_value(wb, ws, row, col)
            label_counts[label] = label_counts.get(label, 0) + 1
            spec_label = label if label_counts[label] == 1 else f"{label} #{label_counts[label]}"
            specs[spec_label] = value

        device_class = find_class_in_specs(specs)

        if sheet_name == "WiFi":
            device_class = device_class or infer_wifi_class(specs)
            if device_class:
                specs["Access Point Class"] = device_class

        devices.append({
            "model": model,
            "sheet": sheet_name,
            "class": device_class,
            "price": price_map.get(model, 0),
            "specs": specs,
        })

    return devices


def infer_sfp_speed(model: str, description: str = "") -> float:
    text = f"{model} {description}".upper()

    if "100G" in text:
        return 100

    if "40G" in text:
        return 40

    if "25G" in text:
        return 25

    if "10G" in text:
        return 10

    if "1G" in text or "GLC" in text:
        return 1

    return 0


def infer_sfp_distance(model: str, description: str = "") -> float:
    text = f"{model} {description}".upper()

    if "80KM" in text or "ZR" in text:
        return 80

    if "40KM" in text or "ER" in text:
        return 40

    if "10KM" in text or "LR" in text or "LH" in text:
        return 10

    if "SR" in text:
        return 0.3

    return 0


def looks_like_sfp_model(model: str) -> bool:
    text = str(model or "").upper().strip()

    if not text:
        return False

    keywords = [
        "SFP",
        "QSFP",
        "GLC",
        "FET",
        "CWDM",
        "DWDM",
        "X2-",
        "XFP",
        "CFP",
        "CVR-QSFP",
        "QDD",
        "FICER",
    ]

    return any(k in text for k in keywords)


def infer_sfp_class(model: str) -> str:
    text = model.upper()

    if "FICER" in text:
        return "Low End"

    if "QSFP" in text or "SFP" in text or "GLC" in text:
        return "High End"

    return "Mid Range"


def read_sfp_catalog() -> List[Dict[str, Any]]:
    price_map = read_price_map()
    devices_by_model: Dict[str, Dict[str, Any]] = {}

    def add_sfp_device(model: Any, description: str = "", price: float = 0):
        model_name = normalize_model(model)

        if not model_name:
            return

        if not looks_like_sfp_model(model_name):
            return

        final_price = price_map.get(model_name, price)

        speed = infer_sfp_speed(model_name, description)
        distance = infer_sfp_distance(model_name, description)

        devices_by_model[model_name] = {
            "model": model_name,
            "sheet": "SFP",
            "class": infer_sfp_class(model_name),
            "price": final_price,
            "speed": speed,
            "distance": distance,
            "specs": {
                "description": description,
                "speed": speed,
                "distance": distance,
            }
        }

    if sheet_exists(SPECS_FILE, "SFP"):
        wb = openpyxl.load_workbook(SPECS_FILE, data_only=False)
        ws = wb["SFP"]

        for col in range(2, ws.max_column + 1):
            model = normalize_model(cell_value(wb, ws, 1, col))

            if looks_like_sfp_model(model):
                speed = to_float(cell_value(wb, ws, 2, col), 0)
                distance = to_float(cell_value(wb, ws, 3, col), 0)
                sfp_class = str(cell_value(wb, ws, 4, col) or "").strip()
                price = price_map.get(model, to_float(cell_value(wb, ws, 5, col), 0))

                devices_by_model[model] = {
                    "model": model,
                    "sheet": "SFP",
                    "class": sfp_class or infer_sfp_class(model),
                    "price": price,
                    "speed": speed or infer_sfp_speed(model),
                    "distance": distance or infer_sfp_distance(model),
                    "specs": {
                        "speed": speed or infer_sfp_speed(model),
                        "distance": distance or infer_sfp_distance(model),
                    }
                }

        for row in range(2, ws.max_row + 1):
            item_name = cell_value(wb, ws, row, 2)

            if not item_name:
                continue

            model = normalize_model(item_name)

            if not looks_like_sfp_model(model):
                continue

            description_parts = []

            for col in range(3, min(ws.max_column, 8) + 1):
                v = cell_value(wb, ws, row, col)

                if v:
                    description_parts.append(str(v))

            description = " ".join(description_parts)
            price = price_map.get(model, 0)

            add_sfp_device(model, description, price)

    for model, price in price_map.items():
        if looks_like_sfp_model(model):
            add_sfp_device(model, "", price)

    return sorted(
        list(devices_by_model.values()),
        key=lambda x: (
            x.get("speed", 0) or 0,
            x.get("price", 0) or 0,
            x.get("model", "")
        )
    )


@lru_cache(maxsize=1)
def load_catalogs() -> Dict[str, Any]:
    return {
        "prices": read_price_map(),
        "routers": read_specs_matrix_sheet("Router"),
        "switches": read_specs_matrix_sheet("SwitchCampus"),
        "modular_switches": read_specs_matrix_sheet("ModularSwitch"),
        "wifi": read_specs_matrix_sheet("WiFi"),
        "sfps": read_sfp_catalog(),
    }


def debug_catalog_summary() -> Dict[str, Any]:
    catalogs = load_catalogs()

    return {
        "price_count": len(catalogs["prices"]),
        "router_count": len(catalogs["routers"]),
        "switch_count": len(catalogs["switches"]),
        "modular_switch_count": len(catalogs["modular_switches"]),
        "wifi_count": len(catalogs["wifi"]),
        "sfp_count": len(catalogs["sfps"]),
        "sample_prices": list(catalogs["prices"].items())[:10],
    }
