from pathlib import Path
from functools import lru_cache
from typing import Any, Dict, List
import re

import openpyxl
from openpyxl.utils import range_boundaries


DATA_DIR = Path("data")

SPECS_FILE = DATA_DIR / "Devices Specs_240426.xlsx"
PRICE_FILE = DATA_DIR / "Cisco Unit List Price_240426.xlsx"
TOOL_FILE = DATA_DIR / "Network Quotation Tool_210426 (1).xlsx"


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

    text = str(value).strip()

    while "  " in text:
        text = text.replace("  ", " ")

    return text


def parse_google_export_formula(value: Any) -> Any:
    """
    File export từ Google Sheet có thể có dạng:
    =IFERROR(__xludf.DUMMYFUNCTION(...),"C8200L-1N-4T")
    =IFERROR(__xludf.DUMMYFUNCTION(...),20055.59)

    Hàm này lấy phần fallback cuối cùng.
    """
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
    """
    Xử lý công thức tham chiếu đơn giản:
    =Specs!B1
    ='Đơn giá dự toán'!A1
    """
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
    """
    Đọc giá theo logic:

    Final Price =
    nếu có Giá AM nhập thì lấy Giá AM nhập,
    nếu không thì lấy List Price.

    Ưu tiên sheet Cisco vì đây là sheet đã gom từ các tab BOM.
    """
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
    """
    Fallback đọc trực tiếp từ các tab BOM.

    Logic:
    - Lấy model chính ở cột B.
    - Chỉ lấy dòng Line Number dạng số nguyên ở cột A.
    - Lấy giá SubTotal ở cột N khi cột M = SubTotal.
    - Ghép model chính với SubTotal theo thứ tự.
    """
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
    """
    Đọc các sheet có dạng tổng hợp sẵn:
    Devices / Price Base / Final Price...
    """
    header_map = {}

    for col in range(1, ws.max_column + 1):
        header = cell_value(wb, ws, 1, col)

        if header is None:
            continue

        header_text = str(header).strip().lower()
        header_map[header_text] = col

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


def find_class_in_specs(specs: Dict[str, Any]) -> str:
    for key, value in specs.items():
        if "class" in str(key).lower():
            return str(value or "").strip()
    return ""


def read_specs_matrix_sheet(sheet_name: str) -> List[Dict[str, Any]]:
    """
    Đọc các sheet specs dạng matrix:
    - Router
    - SwitchCampus
    - ModularSwitch
    - WiFi

    Model nằm theo chiều ngang, thông số nằm theo dòng.
    """
    wb = openpyxl.load_workbook(SPECS_FILE, data_only=False)
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

        if not model:
            continue

        specs = {}

        for row, label in row_labels.items():
            specs[label] = cell_value(wb, ws, row, col)

        device_class = find_class_in_specs(specs)
        price = price_map.get(model, 0)

        devices.append({
            "model": model,
            "sheet": sheet_name,
            "class": device_class,
            "price": price,
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


def infer_sfp_class(model: str) -> str:
    text = model.upper()

    if "FICER" in text:
        return "Low End"

    if "QSFP" in text or "SFP" in text or "GLC" in text:
        return "High End"

    return "Mid Range"


def looks_like_sfp_model(model: str) -> bool:
    """
    Nhận diện các SKU optic/transceiver.
    """
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


def read_sfp_catalog() -> List[Dict[str, Any]]:
    """
    Đọc SFP/optic robust hơn.
    """
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

    devices = list(devices_by_model.values())

    devices = sorted(
        devices,
        key=lambda x: (
            x.get("speed", 0) or 0,
            x.get("price", 0) or 0,
            x.get("model", "")
        )
    )

    return devices


# ============================================================
# Đọc đúng dropdown/data validation từ tab Campus
# ============================================================

def clean_option_model(value: Any) -> str:
    """
    Giữ nguyên model như Excel dropdown hiển thị.
    Ví dụ:
    - GLC-SX-MMD= giữ nguyên
    - C9404R giữ nguyên
    """
    if value is None:
        return ""

    text = str(value).strip()

    if not text:
        return ""

    return text


def is_valid_option_model(value: Any) -> bool:
    """
    Lọc các giá trị không phải model trong dropdown/range.
    """
    if value is None:
        return False

    if isinstance(value, (int, float)):
        return False

    text = str(value).strip()

    if not text:
        return False

    upper = text.upper()
    lower = text.lower()

    invalid_values = {
        "0",
        "0.0",
        "N/A",
        "NA",
        "-",
        "NONE",
        "LOW END",
        "MID RANGE",
        "HIGH END",
        "OPT 1",
        "OPT 2",
        "OPT 3",
        "OPTION 1",
        "OPTION 2",
        "OPTION 3",
        "SỐ LƯỢNG",
        "SO LUONG",
    }

    if upper in invalid_values:
        return False

    if text.startswith("$"):
        return False

    if lower.startswith("giá"):
        return False

    if lower.startswith("please"):
        return False

    if re.fullmatch(r"\d+(\.\d+)?", text):
        return False

    return True


def option_map_empty() -> Dict[str, List[str]]:
    return {
        "Low End": [],
        "Mid Range": [],
        "High End": [],
    }


def default_proposal_option_map() -> Dict[str, Dict[str, List[str]]]:
    """
    Fallback tối thiểu.
    Data validation từ tab Campus vẫn là nguồn chính.
    """
    return {
        "SFP 100G": {
            "Low End": ["Ficer-100G-10km"],
            "Mid Range": ["QSFP-100G-LR4-S"],
            "High End": ["QSFP-100G-LR4-S"],
        },
        "SFP 10G": {
            "Low End": ["Ficer-10G-10km"],
            "Mid Range": ["SFP-10G-SR-S"],
            "High End": ["SFP-10G-SR-S"],
        },
        "SFP 1G": {
            "Low End": ["Ficer-1G-10km"],
            "Mid Range": ["GLC-SX-MMD=", "GLC-LH-SMD="],
            "High End": ["GLC-SX-MMD=", "GLC-LH-SMD="],
        },
    }


def cell_display_value(wb, ws, row: int, col: int) -> Any:
    """
    Lấy value của cell, có xử lý merged cell.
    Nếu cell nằm trong vùng merge nhưng không phải top-left,
    openpyxl trả None nên cần lấy value từ top-left.
    """
    value = cell_value(wb, ws, row, col)

    if value is not None:
        return value

    for merged_range in ws.merged_cells.ranges:
        if (
            merged_range.min_row <= row <= merged_range.max_row
            and merged_range.min_col <= col <= merged_range.max_col
        ):
            return cell_value(wb, ws, merged_range.min_row, merged_range.min_col)

    return value


def normalize_option_class(value: Any) -> str:
    """
    Map header trong Excel sang class nội bộ.

    Excel có thể ghi:
    - Low End / Mid Range / High End
    - Opt 1 / Opt 2 / Opt 3
    - Option 1 / Option 2 / Option 3

    Quy ước:
    Opt 1 = Low End
    Opt 2 = Mid Range
    Opt 3 = High End
    """
    text = str(value or "").strip().lower()

    if not text:
        return ""

    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)

    if "low end" in text:
        return "Low End"

    if "mid range" in text or "mid-range" in text:
        return "Mid Range"

    if "high end" in text:
        return "High End"

    if re.fullmatch(r"(opt|option)\s*1", text):
        return "Low End"

    if re.fullmatch(r"(opt|option)\s*2", text):
        return "Mid Range"

    if re.fullmatch(r"(opt|option)\s*3", text):
        return "High End"

    return ""


def find_class_above_cell(wb, ws, row: int, col: int) -> str:
    """
    Tìm class của dropdown cell.

    Quan trọng:
    - Phải tìm header gần nhất phía trên.
    - Quét cột hiện tại và cột lân cận để xử lý merged cells.
    """
    nearby_cols = [
        col,
        col - 1,
        col + 1,
        col - 2,
        col + 2,
        col - 3,
        col + 3,
    ]

    for r in range(row - 1, max(1, row - 40), -1):
        for c in nearby_cols:
            if c < 1 or c > ws.max_column:
                continue

            value = cell_display_value(wb, ws, r, c)
            class_name = normalize_option_class(value)

            if class_name:
                return class_name

    return ""


def is_group_label(text: str) -> bool:
    normalized = str(text or "").strip().lower()

    if not normalized:
        return False

    return (
        "campus" in normalized
        or normalized == "server farm"
        or normalized == "wan"
    )


def find_item_label_left(wb, ws, row: int, col: int) -> tuple[str, int]:
    """
    Từ ô dropdown, quét sang trái để tìm tên hạng mục.
    Ví dụ:
    - Server Farm Opt1 cell -> Core Switch (hoặc Spine Switch)
    - WAN Opt1 cell -> WAN Router loại vừa/nhỏ
    """
    for c in range(col - 1, max(1, col - 30), -1):
        value = cell_display_value(wb, ws, row, c)
        text = str(value or "").strip()

        if not text:
            continue

        lower = text.lower()

        if lower in ["số lượng", "so luong", "opt 1", "opt 2", "opt 3"]:
            continue

        if lower in ["low end", "mid range", "high end"]:
            continue

        if is_group_label(text):
            continue

        if re.fullmatch(r"\d+(\.\d+)?", text):
            continue

        return text, c

    return "", 0


def find_group_for_item_row(wb, ws, row: int, label_col: int) -> str:
    """
    Tìm group của dòng proposal:
    - Campus - Trụ sở chính
    - Server Farm
    - WAN
    """
    for r in range(row, 0, -1):
        value = cell_display_value(wb, ws, r, label_col)
        text = str(value or "").strip()

        if not text:
            continue

        lower = text.lower()

        if "campus" in lower:
            return "Campus - Trụ sở chính"

        if lower == "server farm":
            return "Server Farm"

        if lower == "wan":
            return "WAN"

    return ""


def find_proposal_start_row(wb, ws) -> int:
    """
    Tìm dòng bắt đầu vùng GIẢI PHÁP ĐỀ XUẤT.
    Dùng để bỏ qua các dropdown khảo sát phía trên.
    """
    for row in range(1, ws.max_row + 1):
        for col in range(1, min(ws.max_column, 30) + 1):
            value = cell_display_value(wb, ws, row, col)
            text = str(value or "").strip().upper()

            if "GIẢI PHÁP ĐỀ XUẤT" in text:
                return row

    return 1


def get_defined_name_values(wb, defined_name: str) -> List[str]:
    """
    Đọc dropdown nếu Data Validation dùng named range.
    """
    values: List[str] = []

    try:
        dn = wb.defined_names[defined_name]
    except Exception:
        try:
            dn = wb.defined_names.get(defined_name)
        except Exception:
            dn = None

    if not dn:
        return values

    try:
        destinations = list(dn.destinations)
    except Exception:
        return values

    for sheet_name, coord in destinations:
        if sheet_name not in wb.sheetnames:
            continue

        ws = wb[sheet_name]

        try:
            min_col, min_row, max_col, max_row = range_boundaries(coord)
        except Exception:
            continue

        for row in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):
                value = cell_value(wb, ws, row, col)

                if not is_valid_option_model(value):
                    continue

                model = clean_option_model(value)

                if model not in values:
                    values.append(model)

    return values


def read_values_from_validation_formula(wb, base_ws, formula: Any) -> List[str]:
    """
    Đọc đúng danh sách model từ formula data validation của từng ô.

    Hỗ trợ:
    - "A,B,C"
    - ='Campus-Calculation'!$K$100:$K$105
    - =Campus-Calculation!$K$100:$K$105
    - =$K$100:$K$105
    - Named range
    """
    if formula is None:
        return []

    text = str(formula).strip()

    if not text:
        return []

    if text.startswith("="):
        text = text[1:].strip()

    # Case 1: list trực tiếp
    if text.startswith('"') and text.endswith('"'):
        raw_items = text[1:-1].split(",")
        result = []

        for item in raw_items:
            if is_valid_option_model(item):
                model = clean_option_model(item)
                if model not in result:
                    result.append(model)

        return result

    # Case 2: named range
    if "!" not in text and not re.search(r"\$?[A-Z]+\$?\d+", text):
        named_values = get_defined_name_values(wb, text)
        if named_values:
            return named_values

    # Case 3: range reference
    sheet_name = base_ws.title
    coord = text

    if "!" in text:
        sheet_part, coord_part = text.rsplit("!", 1)
        sheet_name = sheet_part.strip().strip("'")
        coord = coord_part.strip()

    coord = coord.replace("$", "")

    if sheet_name not in wb.sheetnames:
        return []

    try:
        min_col, min_row, max_col, max_row = range_boundaries(coord)
    except Exception:
        return []

    ws = wb[sheet_name]
    result = []

    for row in range(min_row, max_row + 1):
        for col in range(min_col, max_col + 1):
            value = cell_value(wb, ws, row, col)

            if not is_valid_option_model(value):
                continue

            model = clean_option_model(value)

            if model not in result:
                result.append(model)

    return result


def iter_data_validation_cells(dv):
    """
    Lặp qua toàn bộ cell thuộc một DataValidation.
    """
    ranges_obj = getattr(dv, "cells", None) or getattr(dv, "sqref", None)

    if not ranges_obj:
        return

    try:
        ranges = ranges_obj.ranges
    except Exception:
        ranges = str(ranges_obj).split()

    for cell_range in ranges:
        min_col, min_row, max_col, max_row = range_boundaries(str(cell_range))

        for row in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):
                yield row, col


def set_option_map_value(
    result: Dict[str, Dict[str, List[str]]],
    key: str,
    class_name: str,
    models: List[str],
    overwrite: bool = True,
):
    key = normalize_proposal_key(key)

    if not key or not class_name or not models:
        return

    if key not in result:
        result[key] = option_map_empty()

    if overwrite or not result[key].get(class_name):
        result[key][class_name] = models


def read_option_map_from_campus_dropdowns() -> Dict[str, Dict[str, List[str]]]:
    """
    Nguồn chính xác nhất.

    Đọc trực tiếp dropdown/data validation của từng cell trong tab Campus.
    Mỗi cell có thể trỏ tới một dải riêng trong Campus-Calculation.
    """
    result: Dict[str, Dict[str, List[str]]] = {}

    if not TOOL_FILE.exists():
        return result

    wb = openpyxl.load_workbook(TOOL_FILE, data_only=False)

    if "Campus" not in wb.sheetnames:
        return result

    ws = wb["Campus"]

    if not ws.data_validations:
        return result

    proposal_start_row = find_proposal_start_row(wb, ws)

    for dv in ws.data_validations.dataValidation:
        if str(dv.type).lower() != "list":
            continue

        models = read_values_from_validation_formula(wb, ws, dv.formula1)

        if not models:
            continue

        for row, col in iter_data_validation_cells(dv):
            if row < proposal_start_row:
                continue

            class_name = find_class_above_cell(wb, ws, row, col)

            if not class_name:
                continue

            item_label, label_col = find_item_label_left(wb, ws, row, col)

            if not item_label:
                continue

            group_name = find_group_for_item_row(wb, ws, row, label_col)

            item_key = normalize_proposal_key(item_label)
            group_item_key = normalize_proposal_key(f"{group_name}||{item_label}") if group_name else ""

            # Key chính xác nhất: group + item
            if group_item_key:
                set_option_map_value(
                    result=result,
                    key=group_item_key,
                    class_name=class_name,
                    models=models,
                    overwrite=True,
                )

            # Key fallback: item
            set_option_map_value(
                result=result,
                key=item_key,
                class_name=class_name,
                models=models,
                overwrite=False,
            )

    return result


def read_option_map_from_campus_calculation_rows() -> Dict[str, Dict[str, List[str]]]:
    """
    Fallback nếu không đọc được data validation.

    Đọc các dòng dạng:
    Gateway Router - Low End
    WAN Router loại vừa/nhỏ - Low End
    SFP 1G - Low End
    """
    result: Dict[str, Dict[str, List[str]]] = {}

    if not TOOL_FILE.exists():
        return result

    wb = openpyxl.load_workbook(TOOL_FILE, data_only=False)

    if "Campus-Calculation" not in wb.sheetnames:
        return result

    ws = wb["Campus-Calculation"]

    pattern = re.compile(
        r"^(?P<item>.+?)\s*-\s*(?P<class>Low End|Mid Range|High End)\s*$",
        re.IGNORECASE,
    )

    class_map = {
        "low end": "Low End",
        "mid range": "Mid Range",
        "high end": "High End",
    }

    for row in range(1, ws.max_row + 1):
        for col in range(1, ws.max_column + 1):
            raw_label = cell_value(wb, ws, row, col)

            if not raw_label:
                continue

            label = str(raw_label).strip()
            match = pattern.match(label)

            if not match:
                continue

            item_key = normalize_proposal_key(match.group("item"))
            class_name = class_map[match.group("class").lower()]

            models = []
            blank_streak = 0

            for model_col in range(col + 1, ws.max_column + 1):
                raw_model = cell_value(wb, ws, row, model_col)

                if raw_model is None or raw_model == "":
                    blank_streak += 1
                    if blank_streak >= 5 and models:
                        break
                    continue

                blank_streak = 0

                if not is_valid_option_model(raw_model):
                    continue

                model = clean_option_model(raw_model)

                if model not in models:
                    models.append(model)

            if models:
                set_option_map_value(
                    result=result,
                    key=item_key,
                    class_name=class_name,
                    models=models,
                    overwrite=True,
                )

    return result


def merge_option_maps(
    fallback: Dict[str, Dict[str, List[str]]],
    primary: Dict[str, Dict[str, List[str]]],
) -> Dict[str, Dict[str, List[str]]]:
    """
    primary ghi đè fallback.
    """
    result = {}

    for key, class_map in fallback.items():
        result[key] = {
            "Low End": list(class_map.get("Low End", [])),
            "Mid Range": list(class_map.get("Mid Range", [])),
            "High End": list(class_map.get("High End", [])),
        }

    for key, class_map in primary.items():
        if key not in result:
            result[key] = option_map_empty()

        for class_name, models in class_map.items():
            if models:
                result[key][class_name] = models

    return result


def read_proposal_option_map_from_campus_calculation() -> Dict[str, Dict[str, List[str]]]:
    """
    Output cuối cho recommendation engine.

    Thứ tự ưu tiên:
    1. default fallback
    2. dòng mapping trong Campus-Calculation
    3. data validation dropdown trong tab Campus

    Dropdown trong tab Campus là nguồn chính xác nhất.
    """
    default_map = default_proposal_option_map()
    row_map = read_option_map_from_campus_calculation_rows()
    dropdown_map = read_option_map_from_campus_dropdowns()

    merged = merge_option_maps(default_map, row_map)
    merged = merge_option_maps(merged, dropdown_map)

    return merged


@lru_cache(maxsize=1)
def load_catalogs() -> Dict[str, Any]:
    return {
        "prices": read_price_map(),
        "routers": read_specs_matrix_sheet("Router") if sheet_exists(SPECS_FILE, "Router") else [],
        "switches": read_specs_matrix_sheet("SwitchCampus") if sheet_exists(SPECS_FILE, "SwitchCampus") else [],
        "modular_switches": read_specs_matrix_sheet("ModularSwitch") if sheet_exists(SPECS_FILE, "ModularSwitch") else [],
        "wifi": read_specs_matrix_sheet("WiFi") if sheet_exists(SPECS_FILE, "WiFi") else [],
        "sfps": read_sfp_catalog(),
        "proposal_option_map": read_proposal_option_map_from_campus_calculation(),
    }


def debug_catalog_summary() -> Dict[str, Any]:
    catalogs = load_catalogs()
    proposal_map = catalogs.get("proposal_option_map", {})

    server_farm_keys = {
        key: value
        for key, value in proposal_map.items()
        if key.startswith("Server Farm||")
    }

    wan_keys = {
        key: value
        for key, value in proposal_map.items()
        if key.startswith("WAN||")
    }

    return {
        "price_count": len(catalogs["prices"]),
        "router_count": len(catalogs["routers"]),
        "switch_count": len(catalogs["switches"]),
        "modular_switch_count": len(catalogs["modular_switches"]),
        "wifi_count": len(catalogs["wifi"]),
        "sfp_count": len(catalogs["sfps"]),
        "proposal_option_map_count": len(proposal_map),
        "server_farm_option_map": server_farm_keys,
        "wan_option_map": wan_keys,
        "proposal_option_map_sample": dict(list(proposal_map.items())[:15]),
        "sample_prices": list(catalogs["prices"].items())[:10],
    }