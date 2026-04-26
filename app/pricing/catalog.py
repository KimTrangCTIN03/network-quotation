from typing import Any, Dict, List

from app.catalog_engine import (
    clear_catalog_cache,
    normalize_model,
    read_price_map_from_bom_files,
    read_price_overrides,
    to_float,
)
from app.pricing.rules import apply_composed_price_rules, build_composed_list_prices
from app.pricing.storage import (
    delete_custom_price_entry,
    read_am_prices,
    read_custom_price_entries,
    save_am_price_entry,
    save_custom_price_entry,
)

DEFAULT_VENDOR = "Cisco"
INTERNAL_COMPONENT_MODELS = {
    "AIR-MNT-VERT1",
    "AIR-PWRINJ7",
    "CISCO-NETWORK-SUB",
    "IW-PWRINJ-60RGDMG",
    "L-DNA-TIER-ADD",
}


def normalize_vendor(vendor: str | None) -> str:
    text = str(vendor or "").strip()
    return text or DEFAULT_VENDOR


def read_list_price_map() -> Dict[str, float]:
    # Base Cisco prices come from exported BOM files plus mapping rules.
    # Runtime pricing must not read final prices from Cisco Unit List Price;
    # that workbook is only kept for comparison/debug.
    return apply_composed_price_rules(read_price_map_from_bom_files())


def read_final_price_map() -> Dict[str, float]:
    prices = {
        row["model"]: row["final_price"]
        for row in build_price_catalog()
    }
    return prices


def read_vendor_list_price_entries() -> List[Dict[str, Any]]:
    entries = []
    composed_prices = build_composed_list_prices()

    # Cisco rows are generated from BOM subtotals. Internal accessory/license
    # parts are filtered from the visible catalog but can still be used by rules
    # to compose final prices for AP/ISR/C8000 Secure product lines.
    for model, price in read_list_price_map().items():
        if model in INTERNAL_COMPONENT_MODELS:
            continue

        entries.append({
            "vendor": DEFAULT_VENDOR,
            "model": model,
            "list_price": price,
            "rule": "bom_composed" if model in composed_prices else "bom_subtotal",
        })

    # Non-Cisco or AM-provided List Price rows are appended from the DB. These
    # are created by the 3-column price import or by the manual List Price field.
    entries.extend(read_custom_price_entries())
    return entries


def entry_key(vendor: str, model: str) -> str:
    return f"{normalize_vendor(vendor).lower()}::{normalize_model(model)}"


def read_am_price_entry_map(entries: List[Dict[str, Any]]) -> Dict[str, float]:
    # AM price precedence:
    # 1. Legacy JSON overrides are kept for older Cisco overrides.
    # 2. PostgreSQL AM prices are the current source for web-entered/imported AM
    #    prices and override the legacy map when they target the same key.
    raw = {
        **read_price_overrides(),
        **read_am_prices(),
    }
    by_model_vendor: Dict[str, str] = {}

    for entry in entries:
        by_model_vendor.setdefault(entry["model"], entry["vendor"])

    result: Dict[str, float] = {}

    for raw_model, price in raw.items():
        vendor = DEFAULT_VENDOR
        model = raw_model

        if "::" in raw_model:
            vendor, model = raw_model.split("::", 1)
        else:
            vendor = by_model_vendor.get(raw_model, DEFAULT_VENDOR)

        model_key = normalize_model(model)
        final_price = to_float(price, 0)

        if model_key and final_price > 0:
            result[entry_key(vendor, model_key)] = final_price

    return result


def build_price_catalog() -> List[Dict[str, Any]]:
    base_entries = read_vendor_list_price_entries()
    by_key: Dict[str, Dict[str, Any]] = {}

    # Start with every known List Price row, keyed by vendor + normalized model.
    # A row may come from Cisco BOM logic or from custom imported/manual entries.
    for entry in base_entries:
        key = entry_key(entry["vendor"], entry["model"])
        by_key[key] = {
            "vendor": normalize_vendor(entry["vendor"]),
            "model": normalize_model(entry["model"]),
            "list_price": to_float(entry["list_price"], 0),
            "rule": entry.get("rule", "vendor_sheet"),
        }

    am_prices = read_am_price_entry_map(list(by_key.values()))

    # Then overlay AM prices. If an AM price exists for a part that has no List
    # Price yet, keep it visible as an AM-only row with list_price = 0.
    for key, price in am_prices.items():
        if key not in by_key:
            vendor, model = key.split("::", 1)
            by_key[key] = {
                "vendor": normalize_vendor(vendor),
                "model": model,
                "list_price": 0,
                "rule": "am_db",
            }

        by_key[key]["am_price"] = price

    rows = []

    for row in by_key.values():
        list_price = to_float(row.get("list_price"), 0)
        am_price = to_float(row.get("am_price"), 0)
        # Final Price follows the quotation rule: AM-entered price wins when
        # present; otherwise fall back to List Price.
        final_price = am_price if am_price > 0 else list_price

        rows.append({
            "vendor": row["vendor"],
            "model": row["model"],
            "list_price": list_price,
            "am_price": am_price,
            "final_price": final_price,
            "source": "am" if am_price > 0 else row.get("rule", "vendor_sheet"),
            "rule": row.get("rule", "vendor_sheet"),
        })

    return sorted(rows, key=lambda row: (row["vendor"].lower(), row["model"]))


def build_legacy_model_price_map() -> Dict[str, float]:
    result: Dict[str, float] = {}

    for row in build_price_catalog():
        if row["final_price"] > 0:
            result[row["model"]] = row["final_price"]

    return result


def list_price_entries(query: str = "", limit: int | None = None, vendor: str = "") -> Dict[str, Any]:
    text = normalize_model(query).lower()
    vendor_text = normalize_vendor(vendor).lower() if vendor else ""
    rows = build_price_catalog()

    if text:
        rows = [
            row
            for row in rows
            if text in row["model"].lower() or text in row["vendor"].lower()
        ]

    if vendor_text:
        rows = [row for row in rows if row["vendor"].lower() == vendor_text]

    total_count = len(rows)

    if limit is not None and limit > 0:
        rows = rows[:limit]

    return {
        "total_count": total_count,
        "rows": rows,
    }


def save_am_price(
    model: str,
    price: float,
    vendor: str = DEFAULT_VENDOR,
    list_price: float | None = None,
) -> Dict[str, Any]:
    vendor_key = normalize_vendor(vendor)
    model_key = normalize_model(model)
    final_price = to_float(price, 0)
    final_list_price = to_float(list_price, 0) if list_price is not None else None

    if not model_key:
        raise ValueError("Model không hợp lệ.")

    if final_list_price is not None:
        if final_list_price > 0:
            save_custom_price_entry(vendor_key, model_key, final_list_price)
        else:
            delete_custom_price_entry(vendor_key, model_key)

    if final_price > 0:
        save_am_price_entry(vendor_key, model_key, final_price)
    else:
        save_am_price_entry(vendor_key, model_key, 0)

    clear_catalog_cache()

    row = next(
        (
            item
            for item in build_price_catalog()
            if item["model"] == model_key and item["vendor"].lower() == vendor_key.lower()
        ),
        None,
    )

    return {
        "saved": True,
        "row": row,
    }
