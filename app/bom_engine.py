from collections import OrderedDict
from io import BytesIO
from typing import Any, Dict, List

import openpyxl
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

from app.catalog_engine import PRICE_FILE, cell_value, is_integer_line_number, normalize_model, to_float


OPTIONS = [
    ("opt1", "Option 1 - Low End"),
    ("opt2", "Option 2 - Mid Range"),
    ("opt3", "Option 3 - High End"),
]

DETAIL_BOM_SHEETS = [
    "C8000",
    "C9200",
    "C9300",
    "C1300",
    "C9500",
    "ACI",
    "SFP",
    "AP_input",
    "ISR1000_input",
    "C8000_secure_input",
]

BOM_COLUMNS = [
    "option",
    "group",
    "item_type",
    "selected_model",
    "source_sheet",
    "line_number",
    "part_number",
    "smart_account_mandatory",
    "description",
    "group_name",
    "service_duration_months",
    "estimated_lead_time_days",
    "included_item",
    "quantity_per_unit",
    "quote_quantity",
    "total_quantity",
    "pricing_term",
    "list_price",
    "extended_list_price",
    "discount_percent",
    "selling_price",
    "extended_selling_price",
    "service_type",
]


def normalized_candidates(model: str) -> List[str]:
    normalized = normalize_model(model)
    candidates = [normalized]

    for suffix in ["-A", "-ROW", "-RTG"]:
        candidates.append(normalize_model(f"{normalized}{suffix}"))

    return list(dict.fromkeys([c for c in candidates if c]))


def row_to_bom_part(
    wb,
    ws,
    row: int,
    selected_model: str,
    quote_quantity: float,
    option_key: str,
    line: Dict[str, Any],
) -> Dict[str, Any] | None:
    part_number = cell_value(wb, ws, row, 2)

    if not part_number:
        return None

    quantity_per_unit = to_float(cell_value(wb, ws, row, 9), 1)
    list_price = to_float(cell_value(wb, ws, row, 11), 0)
    extended_list_price = to_float(cell_value(wb, ws, row, 12), list_price * quantity_per_unit)
    discount_percent = to_float(cell_value(wb, ws, row, 13), 0)
    selling_price = to_float(cell_value(wb, ws, row, 14), extended_list_price)

    return {
        "option": option_key,
        "group": line.get("group", ""),
        "item_type": line.get("item_type", ""),
        "selected_model": selected_model,
        "source_sheet": ws.title,
        "line_number": cell_value(wb, ws, row, 1),
        "part_number": str(part_number).strip(),
        "smart_account_mandatory": cell_value(wb, ws, row, 3),
        "description": cell_value(wb, ws, row, 4),
        "group_name": cell_value(wb, ws, row, 5),
        "service_duration_months": cell_value(wb, ws, row, 6),
        "estimated_lead_time_days": cell_value(wb, ws, row, 7),
        "included_item": cell_value(wb, ws, row, 8),
        "quantity_per_unit": quantity_per_unit,
        "quote_quantity": quote_quantity,
        "total_quantity": quantity_per_unit * quote_quantity,
        "pricing_term": cell_value(wb, ws, row, 10),
        "list_price": list_price,
        "extended_list_price": extended_list_price * quote_quantity,
        "discount_percent": discount_percent,
        "selling_price": selling_price,
        "extended_selling_price": selling_price * quote_quantity,
        "service_type": cell_value(wb, ws, row, 15),
    }


def find_bundle_parts(
    wb,
    selected_model: str,
    quote_quantity: float,
    option_key: str,
    line: Dict[str, Any],
) -> List[Dict[str, Any]]:
    candidates = set(normalized_candidates(selected_model))

    for sheet_name in DETAIL_BOM_SHEETS:
        if sheet_name not in wb.sheetnames:
            continue

        ws = wb[sheet_name]

        for row in range(2, ws.max_row + 1):
            line_number = cell_value(wb, ws, row, 1)
            part_number = cell_value(wb, ws, row, 2)

            if not is_integer_line_number(line_number):
                continue

            if normalize_model(part_number) not in candidates:
                continue

            parts = []
            stop_row = ws.max_row + 1

            for part_row in range(row, ws.max_row + 1):
                if part_row != row:
                    next_line_number = cell_value(wb, ws, part_row, 1)
                    next_part_number = cell_value(wb, ws, part_row, 2)

                    if is_integer_line_number(next_line_number) and next_part_number:
                        break

                subtotal_label = str(cell_value(wb, ws, part_row, 13) or "").strip().lower()

                if subtotal_label == "subtotal":
                    stop_row = part_row
                    break

                part = row_to_bom_part(wb, ws, part_row, selected_model, quote_quantity, option_key, line)

                if part:
                    parts.append(part)

            if ws.title == "ISR1000_input":
                marker_row = None
                model_key = normalize_model(selected_model).lower()

                for scan_row in range(stop_row + 1, min(ws.max_row, stop_row + 4) + 1):
                    marker = str(cell_value(wb, ws, scan_row, 3) or "").lower()

                    if "license" in marker and model_key in normalize_model(marker).lower():
                        marker_row = scan_row
                        break

                if marker_row:
                    for part_row in range(marker_row + 1, ws.max_row + 1):
                        subtotal_label = str(cell_value(wb, ws, part_row, 13) or "").strip().lower()

                        if subtotal_label == "subtotal":
                            break

                        part = row_to_bom_part(wb, ws, part_row, selected_model, quote_quantity, option_key, line)

                        if part:
                            parts.append(part)

            return parts

    return []


def fallback_selected_device_row(
    selected: Dict[str, Any],
    quote_quantity: float,
    option_key: str,
    line: Dict[str, Any],
) -> Dict[str, Any]:
    price = to_float(selected.get("price"), 0)
    model = selected.get("model", "")

    return {
        "option": option_key,
        "group": line.get("group", ""),
        "item_type": line.get("item_type", ""),
        "selected_model": model,
        "source_sheet": selected.get("sheet", ""),
        "line_number": "",
        "part_number": model,
        "smart_account_mandatory": "",
        "description": "No detailed BOM found in Cisco Unit List Price",
        "group_name": "",
        "service_duration_months": "",
        "estimated_lead_time_days": "",
        "included_item": "",
        "quantity_per_unit": 1,
        "quote_quantity": quote_quantity,
        "total_quantity": quote_quantity,
        "pricing_term": "",
        "list_price": price,
        "extended_list_price": price * quote_quantity,
        "discount_percent": 0,
        "selling_price": price,
        "extended_selling_price": price * quote_quantity,
        "service_type": "",
    }


def aggregate_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped: OrderedDict[str, Dict[str, Any]] = OrderedDict()

    for row in rows:
        key = (
            row.get("part_number", ""),
            row.get("description", ""),
            row.get("selling_price", 0),
            row.get("list_price", 0),
        )
        key_text = repr(key)

        if key_text not in grouped:
            grouped[key_text] = dict(row)
            grouped[key_text]["selected_model"] = row.get("selected_model", "")
            grouped[key_text]["item_type"] = row.get("item_type", "")
            grouped[key_text]["group"] = row.get("group", "")
            continue

        target = grouped[key_text]
        target["total_quantity"] = to_float(target.get("total_quantity"), 0) + to_float(row.get("total_quantity"), 0)
        target["extended_list_price"] = to_float(target.get("extended_list_price"), 0) + to_float(row.get("extended_list_price"), 0)
        target["extended_selling_price"] = to_float(target.get("extended_selling_price"), 0) + to_float(row.get("extended_selling_price"), 0)

        for field in ["selected_model", "item_type", "group", "source_sheet"]:
            current_values = [v.strip() for v in str(target.get(field) or "").split(";") if v.strip()]
            new_value = str(row.get(field) or "").strip()

            if new_value and new_value not in current_values:
                current_values.append(new_value)

            target[field] = "; ".join(current_values)

    return list(grouped.values())


def build_bom(quote_data: Dict[str, Any]) -> Dict[str, Any]:
    quote = quote_data.get("quote", quote_data)
    quote_lines = quote.get("quote_lines", [])
    wb = openpyxl.load_workbook(PRICE_FILE, data_only=False)
    result: Dict[str, Any] = {"options": {}, "summary": {}}

    for option_key, option_label in OPTIONS:
        rows = []

        for line in quote_lines:
            selected = (line.get("selected") or {}).get(option_key) or {}
            model = selected.get("model", "")
            quote_quantity = to_float(line.get("quantity"), 0)

            if not model or quote_quantity <= 0:
                continue

            parts = find_bundle_parts(wb, model, quote_quantity, option_key, line)

            if not parts:
                parts = [fallback_selected_device_row(selected, quote_quantity, option_key, line)]

            rows.extend(parts)

        aggregated = aggregate_rows(rows)
        total = sum(to_float(row.get("extended_selling_price"), 0) for row in aggregated)

        result["options"][option_key] = {
            "label": option_label,
            "rows": aggregated,
            "total": total,
            "line_count": len(aggregated),
        }
        result["summary"][option_key] = {
            "label": option_label,
            "total": total,
            "line_count": len(aggregated),
        }

    return result


def autosize_columns(ws) -> None:
    for col in range(1, ws.max_column + 1):
        width = 12

        for row in range(1, min(ws.max_row, 200) + 1):
            value = ws.cell(row=row, column=col).value

            if value is not None:
                width = max(width, min(len(str(value)) + 2, 48))

        ws.column_dimensions[get_column_letter(col)].width = width


def write_rows_sheet(wb, title: str, rows: List[Dict[str, Any]]) -> None:
    ws = wb.create_sheet(title)
    header_fill = PatternFill("solid", fgColor="EAF2FF")

    for col, column_name in enumerate(BOM_COLUMNS, start=1):
        cell = ws.cell(row=1, column=col, value=column_name)
        cell.font = Font(bold=True)
        cell.fill = header_fill

    for row_index, row in enumerate(rows, start=2):
        for col, column_name in enumerate(BOM_COLUMNS, start=1):
            ws.cell(row=row_index, column=col, value=row.get(column_name, ""))

    for col_name in ["list_price", "extended_list_price", "selling_price", "extended_selling_price"]:
        col_index = BOM_COLUMNS.index(col_name) + 1

        for row in range(2, ws.max_row + 1):
            ws.cell(row=row, column=col_index).number_format = '$#,##0.00'

    autosize_columns(ws)
    ws.freeze_panes = "A2"


def build_bom_excel(quote_data: Dict[str, Any]) -> BytesIO:
    bom = build_bom(quote_data)
    wb = openpyxl.Workbook()
    summary_ws = wb.active
    summary_ws.title = "Summary"
    summary_ws.append(["Option", "BOM Lines", "Total"])

    for cell in summary_ws[1]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="EAF2FF")

    for option_key, option_label in OPTIONS:
        option = bom["options"][option_key]
        summary_ws.append([option_label, option["line_count"], option["total"]])
        write_rows_sheet(wb, option_label[:31], option["rows"])

    for row in range(2, summary_ws.max_row + 1):
        summary_ws.cell(row=row, column=3).number_format = '$#,##0.00'

    autosize_columns(summary_ws)

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output
