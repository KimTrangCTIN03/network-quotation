from typing import Any, Dict, List


def default_select_first(recommended_lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    quote_lines = []

    for line in recommended_lines:
        quantity = int(line.get("quantity", 0))

        selected = {}

        for opt in ["opt1", "opt2", "opt3"]:
            choices = line.get("options", {}).get(opt, [])

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
                "opt1": quantity * float(selected["opt1"]["price"] or 0),
                "opt2": quantity * float(selected["opt2"]["price"] or 0),
                "opt3": quantity * float(selected["opt3"]["price"] or 0),
            },
            "options": line.get("options", {})
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
            amount = float(line["amount"][opt] or 0)
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