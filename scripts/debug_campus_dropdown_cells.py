from app.catalog_engine import (
    TOOL_FILE,
    cell_display_value,
    read_values_from_validation_formula,
    iter_data_validation_cells,
    find_proposal_start_row,
    find_class_above_cell,
    find_item_label_left,
    find_group_for_item_row,
)

import openpyxl


def main():
    wb = openpyxl.load_workbook(TOOL_FILE, data_only=False)
    ws = wb["Campus"]

    proposal_start_row = find_proposal_start_row(wb, ws)

    print("Proposal start row:", proposal_start_row)
    print()

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
            item_label, label_col = find_item_label_left(wb, ws, row, col)
            group_name = find_group_for_item_row(wb, ws, row, label_col) if label_col else ""

            if group_name not in ["Server Farm", "WAN"]:
                continue

            cell = ws.cell(row=row, column=col).coordinate

            print("CELL:", cell)
            print("GROUP:", group_name)
            print("ITEM:", item_label)
            print("CLASS:", class_name)
            print("FORMULA:", dv.formula1)
            print("MODELS:", models)
            print("-" * 80)


if __name__ == "__main__":
    main()