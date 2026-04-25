import pandas as pd
from pathlib import Path


DATA_PATH = Path("data/formula_map.csv")
OUTPUT_DIR = Path("data")


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    print("Columns:")
    print(df.columns.tolist())

    print("\nSố dòng:", len(df))

    if "is_formula" in df.columns:
        formula_df = df[df["is_formula"].astype(str).str.lower().isin(["true", "1", "yes"])]
    else:
        formula_df = df[df["value"].astype(str).str.startswith("=")]

    print("Số công thức:", len(formula_df))

    formula_df.to_csv(OUTPUT_DIR / "formulas_only.csv", index=False, encoding="utf-8-sig")

    summary = (
        formula_df
        .groupby(["file", "sheet"])
        .size()
        .reset_index(name="formula_count")
        .sort_values(["file", "formula_count"], ascending=[True, False])
    )

    summary.to_csv(OUTPUT_DIR / "formula_summary.csv", index=False, encoding="utf-8-sig")

    print("\nĐã xuất:")
    print("- data/formulas_only.csv")
    print("- data/formula_summary.csv")


if __name__ == "__main__":
    main()