# Network Quotation Web

Hệ thống web hỗ trợ khảo sát nhu cầu, tính toán giải pháp mạng, đề xuất model, tổng hợp báo giá và xuất BOM Excel. Ứng dụng được xây dựng bằng FastAPI, sử dụng PostgreSQL để lưu giá nhập bổ sung, tài khoản, phiên đăng nhập và lịch sử báo giá.

## Chức năng chính

- Khảo sát và tính toán giải pháp `Campus`, `Server Farm`, `WAN` và `DC-SDN`.
- Đề xuất model thiết bị theo yêu cầu kỹ thuật.
- Chọn model và tổng hợp báo giá theo từng phương án.
- Vẽ topology từ dữ liệu khảo sát và xuất ảnh PNG.
- Xuất BOM chi tiết sang file Excel.
- Tạo báo giá on-demand từ danh sách part number và số lượng.
- Tra cứu catalog, nhập giá AM, bổ sung list price và import giá từ Excel.
- Đăng ký, đăng nhập, cập nhật hồ sơ và quản lý tài khoản.
- Lưu báo giá, theo dõi trạng thái và ghi nhận hoạt động người dùng.

## Công nghệ

- Python 3.10+
- FastAPI và Uvicorn
- PostgreSQL
- `psycopg`
- `openpyxl`, `pandas`, `numpy`
- HTML, CSS và JavaScript thuần

## Cấu trúc thư mục

```text
app/
  main.py                  # FastAPI app, routes và API
  requirement_engine.py    # Tính toán requirement từ khảo sát
  recommendation_engine.py # Đề xuất model
  quote_engine.py          # Tổng hợp báo giá
  bom_engine.py            # Tạo BOM và file Excel
  pricing_engine.py        # Import và áp giá
  pricing/                 # Catalog, quy tắc giá và PostgreSQL storage
  pages/                   # Giao diện HTML
data/
  BOM/                     # File BOM nguồn theo dòng thiết bị
icon-library/              # Icon dùng cho topology
scripts/                   # Công cụ kiểm tra và phân tích dữ liệu
```

## Cài đặt

### 1. Tạo môi trường Python

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Tạo database PostgreSQL

Ví dụ tạo database tên `network_quotation`:

```sql
CREATE DATABASE network_quotation;
```

### 3. Cấu hình biến môi trường

Tạo file `.env` tại thư mục gốc:

```text
DATABASE_URL=postgresql://user:password@localhost:5432/network_quotation
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-this-password
```

`DATABASE_URL` là biến bắt buộc. không commit file `.env`.

### 4. Chạy ứng dụng

```powershell
uvicorn app.main:app --reload
```

Mở trình duyệt tại [http://localhost:8000](http://localhost:8000).

## Khởi tạo database và tài khoản admin

Ứng dụng tự tạo schema PostgreSQL khi kết nối database lần đầu. Các bảng chính gồm:

- `custom_price_entries`: list price nhập bổ sung.
- `am_prices`: giá AM.
- `app_users`: tài khoản.
- `user_sessions`: phiên đăng nhập.
- `activity_logs`: lịch sử hoạt động.
- `quote_records`: báo giá đã lưu.
- `vendors`, `system_settings`: dữ liệu cấu hình mở rộng.

Nếu database chưa có tài khoản, ứng dụng tự tạo admin đầu tiên từ:

```text
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

Đây là giá trị mặc định của mã nguồn. Luôn cấu hình mật khẩu khác trong `.env`.

Để đồng bộ lại mật khẩu của admin đã tồn tại theo `.env`, thêm tạm thời:

```text
ADMIN_SYNC_PASSWORD=1
```

Khởi động lại ứng dụng một lần, sau đó xóa biến này để tránh ghi đè mật khẩu ở mỗi lần restart.

## Luồng sử dụng

### Tính toán giải pháp

1. Đăng nhập và mở `Giải pháp`.
2. Chọn `Campus` hoặc `DC-SDN`.
3. Nhập thông tin khảo sát.
4. Xem kết quả tính toán requirement.
5. Xem topology và xuất ảnh nếu cần.
6. Chọn model, kiểm tra báo giá và xuất BOM Excel.

### Chọn model on-demand

Trang `Chọn model` hỗ trợ hai cách:

- Nhập yêu cầu kỹ thuật để hệ thống đề xuất thiết bị.
- Nhập trực tiếp danh sách part number và số lượng để tổng hợp báo giá, sau đó xuất BOM.

### Quản lý giá

Trang `Báo giá & cập nhật giá` cho phép:

- Tìm kiếm catalog theo hãng hoặc model.
- Nhập list price bổ sung và giá AM.
- Import file Excel có ba cột: `Device`, `List Price`, `AM Price`.

Nếu import gặp part number đã có giá, giao diện sẽ yêu cầu xác nhận trước khi ghi đè.

Quy tắc chọn giá cuối cùng:

1. Dùng giá AM nếu model có giá AM.
2. Nếu không có giá AM, dùng list price.

Catalog Cisco gốc được tổng hợp từ các file trong `data/BOM/`. Giá nhập bổ sung được lưu trong PostgreSQL. File SQLite cũ `data/pricing.db` không còn được sử dụng.

## Phân quyền

- `user`: sử dụng các luồng khảo sát, báo giá, BOM, topology, catalog và cập nhật giá.
- `admin`: có thêm quyền truy cập `/admin` để quản lý tài khoản, xem tổng quan, lịch sử hoạt động, báo giá đã lưu và cập nhật trạng thái báo giá.

Trạng thái báo giá hỗ trợ: `draft`, `submitted`, `approved`, `locked`.

## Kiểm tra hệ thống

Kiểm tra server:

```text
GET /health
```

Kết quả mong đợi:

```json
{"status":"ok"}
```

Sau khi đăng nhập bằng admin, kiểm tra kết nối PostgreSQL:

```text
GET /api/db-health
```

Kiểm tra catalog và các model thiếu giá:

```powershell
python scripts/validate_system.py
```

## Endpoint quan trọng

| Endpoint | Mô tả |
| --- | --- |
| `/dashboard` | Trang tổng quan |
| `/campus/survey` | Khảo sát Campus |
| `/dc-sdn/survey` | Khảo sát DC-SDN |
| `/model-quote` | Chọn model và báo giá on-demand |
| `/pricing` | Catalog và cập nhật giá |
| `/admin` | Quản trị hệ thống |
| `/health` | Kiểm tra FastAPI server |
| `/api/db-health` | Kiểm tra PostgreSQL, yêu cầu quyền admin |

## Lưu ý vận hành

- Không xóa các file `data/BOM/*.xlsx`: đây là nguồn catalog và BOM chi tiết.
- Dữ liệu khảo sát, báo giá đang thao tác và layout topology được lưu tạm trong `localStorage` của trình duyệt.
- Báo giá chỉ được lưu vào PostgreSQL khi người dùng bấm lưu tại giao diện hỗ trợ chức năng này.
- Session đăng nhập có thời hạn 7 ngày.
- Activity log cũ hơn 3 ngày được dọn tự động.
