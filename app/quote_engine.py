from typing import Any, Dict, List


def line_quantity(line: Dict[str, Any]) -> int:
    try:
        return int(float(line.get("quantity", 0) or 0))
    except (TypeError, ValueError):
        return 0


def selected_amount(line: Dict[str, Any], opt: str) -> float:
    quantity = line_quantity(line)
    if quantity <= 0:
        return 0

    selected = (line.get("selected") or {}).get(opt) or {}
    return quantity * float(selected.get("price") or 0)


def choice_sort_key(choice: Dict[str, Any]) -> tuple:
    model = str(choice.get("model") or "")
    price = float(choice.get("price") or 0)

    if model.strip().lower() == "check dc-sdn":
        return (0, 0, model)

    if price > 0:
        return (1, price, model)

    return (2, price, model)


def sort_choices_by_price(choices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(choices, key=choice_sort_key)


def default_select_first(recommended_lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    quote_lines = []

    for line in recommended_lines:
        quantity = line_quantity(line)
        options = {
            opt: sort_choices_by_price(line.get("options", {}).get(opt, []))
            for opt in ["opt1", "opt2", "opt3"]
        }

        selected = {}

        for opt in ["opt1", "opt2", "opt3"]:
            choices = options.get(opt, [])

            if choices:
                selected[opt] = choices[0]
            else:
                selected[opt] = {
                    "model": "",
                    "price": 0,
                    "class": "",
                    "sheet": ""
                }

        quote_lines.append({
            "group": line.get("group"),
            "item_type": line.get("item_type"),
            "quantity": quantity,
            "selected": selected,
            "amount": {
                "opt1": 0 if quantity <= 0 else quantity * float(selected["opt1"]["price"] or 0),
                "opt2": 0 if quantity <= 0 else quantity * float(selected["opt2"]["price"] or 0),
                "opt3": 0 if quantity <= 0 else quantity * float(selected["opt3"]["price"] or 0),
            },
            "options": options
        })

    return quote_lines


def summarize_quote(quote_lines: List[Dict[str, Any]]) -> Dict[str, Any]:
    totals = {
        "opt1": 0,
        "opt2": 0,
        "opt3": 0,
    }

    group_totals = {}

    for line in quote_lines:
        group = line["group"]

        if group not in group_totals:
            group_totals[group] = {
                "opt1": 0,
                "opt2": 0,
                "opt3": 0,
            }

        for opt in ["opt1", "opt2", "opt3"]:
            amount = selected_amount(line, opt)
            line.setdefault("amount", {})[opt] = amount
            totals[opt] += amount
            group_totals[group][opt] += amount

    return {
        "group_totals": group_totals,
        "grand_total": totals,
    }


def build_quote(recommended_lines: List[Dict[str, Any]]) -> Dict[str, Any]:
    quote_lines = default_select_first(recommended_lines)
    summary = summarize_quote(quote_lines)

    return {
        "quote_lines": quote_lines,
        "summary": summary,
    }
