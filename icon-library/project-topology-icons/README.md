# Project Topology Icons

Bộ icon đã được lọc riêng cho dự án Network Quotation Web.

## Cách dùng trong project

Copy folder này vào project, ví dụ:

```text
NETWORK-QUOTATION-WEB/
  static/
    topology-icons/
```

Sau đó gọi icon trong HTML/JS:

```html
<img src="/static/topology-icons/network-core/gateway-router.png" width="48" />
```

Hoặc trong SVG:

```html
<image href="/static/topology-icons/network-core/gateway-router.png" width="48" height="48" />
```

## Các icon chính

- Gateway Router / WAN Router
- Firewall
- Core Switch / Modular Core Switch
- Access Switch / Leaf Switch / Spine Switch
- Access Point indoor / outdoor
- Internet / WAN Cloud
- Server / Server Farm / Storage
- SFP 1G / 10G / 100G
- Campus / Branch Office

## Gợi ý mount static cho FastAPI

```python
from pathlib import Path
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent.parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
```
