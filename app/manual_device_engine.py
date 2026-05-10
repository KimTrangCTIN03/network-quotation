from typing import Any, Dict, List

from app.catalog_engine import load_catalogs, normalize_model
from app.quote_engine import build_quote
from app.recommendation_engine import fixed_model_device


SHEET_LABELS = {
    "Router": ("Router", "Router"),
    "SwitchCampus": ("Switch Campus", "Switch"),
    "ModularSwitch": ("Modular Switch", "Switch"),
    "NexusSwitch": ("Nexus Switch", "Switch"),
    "WiFi": ("WiFi", "Access Point"),
    "SFP": ("SFP", "SFP"),
}


def parse_quantity(value: Any, default: int = 1) -> int:
    try:
        quantity = int(float(str(value).strip()))
    except Exception:
        return default
    return quantity if quantity > 0 else default


def split_device_line(line: str) -> tuple[str, int] | None:
    text = str(line or "").strip()

    if not text or text.startswith("#"):
        return None

    parts = [part.strip() for part in text.replace("\t", ",").split(",") if part.strip()]

    if len(parts) >= 2:
        first_is_qty = parts[0].replace(".", "", 1).isdigit()
        last_is_qty = parts[-1].replace(".", "", 1).isdigit()

        if first_is_qty:
            return normalize_model(parts[1]), parse_quantity(parts[0])
        if last_is_qty:
            return normalize_model(parts[0]), parse_quantity(parts[-1])

        return normalize_model(parts[0]), 1

    tokens = text.split()
    if not tokens:
        return None

    if tokens[0].replace(".", "", 1).isdigit() and len(tokens) > 1:
        return normalize_model(tokens[1]), parse_quantity(tokens[0])

    if tokens[-1].replace(".", "", 1).isdigit() and len(tokens) > 1:
        return normalize_model(" ".join(tokens[:-1])), parse_quantity(tokens[-1])

    return normalize_model(text), 1


def build_quote_from_device_list(text: str) -> Dict[str, Any]:
    catalogs = load_catalogs()
    recommended_lines: List[Dict[str, Any]] = []
    warnings: List[str] = []

    for line_number, raw_line in enumerate(str(text or "").splitlines(), start=1):
        parsed = split_device_line(raw_line)
        if not parsed:
            continue

        model, quantity = parsed
        if not model or model.lower() in {"model", "part number", "item name", "device"}:
            continue

        choice = fixed_model_device(model, "Manual", catalogs)
        if not choice.get("model"):
            warnings.append(f"Line {line_number}: khong nhan dien duoc model '{raw_line.strip()}'")
            continue

        group, item_type = SHEET_LABELS.get(choice.get("sheet"), ("Danh sach thiet bi nhap tay", model))
        options = {opt: [choice] for opt in ["opt1", "opt2", "opt3"]}

        recommended_lines.append({
            "group": group,
            "item_type": item_type,
            "quantity": quantity,
            "options": options,
            "requirement": {"fixed_model": model},
        })

    quote = build_quote(recommended_lines)

    return {
        "requirements": {
            "source": "manual_device_list",
            "requirements": [],
            "proposal_lines": [
                {
                    "group": line["group"],
                    "item_type": line["item_type"],
                    "quantity": line["quantity"],
                    "requirement": line["requirement"],
                }
                for line in recommended_lines
            ],
        },
        "quote": quote,
        "warnings": warnings,
    }
