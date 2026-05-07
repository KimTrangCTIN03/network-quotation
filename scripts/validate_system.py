import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.catalog_engine import debug_catalog_summary, load_catalogs, read_price_map


def main() -> None:
    catalogs = load_catalogs()
    prices = read_price_map()

    print("=" * 80)
    print("DEVICE CATALOG VALIDATION REPORT")
    print("=" * 80)

    categories = ["routers", "switches", "modular_switches", "nexus_switches", "wifi"]
    total_devices = 0
    total_missing = 0

    for category in categories:
        devices = catalogs.get(category, [])
        missing = [
            device.get("model", "")
            for device in devices
            if not device.get("price") and not prices.get(device.get("model", ""))
        ]
        total_devices += len(devices)
        total_missing += len(missing)
        print(f"{category:18} total={len(devices):4} missing_price={len(missing):4}")

    print("-" * 80)
    print(f"TOTAL devices={total_devices} missing_price={total_missing}")

    if total_missing:
        print("Status: NEEDS PRICING ATTENTION")
    else:
        print("Status: OK")

    print(debug_catalog_summary())


if __name__ == "__main__":
    main()
