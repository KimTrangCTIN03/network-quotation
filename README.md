# Network Quotation Web

## PostgreSQL

Gia thiet bi do AM nhap va gia import tu file duoc luu trong PostgreSQL.
Ung dung khong dung `data/pricing.db` nua.

1. Tao database PostgreSQL, vi du `network_quotation`.
2. Cai dependencies:

```powershell
pip install -r requirements.txt
```

3. Set bien moi truong truoc khi chay server:

```powershell
$env:DATABASE_URL="postgresql://user:password@localhost:5432/network_quotation"
uvicorn app.main:app --reload
```

Co the dat dong sau trong file `.env` neu khong muon set bien moi truong moi lan chay:

```text
DATABASE_URL=postgresql://user:password@localhost:5432/network_quotation
```

Bang `custom_price_entries` va `am_prices` se duoc tao tu dong khi app ket noi DB lan dau.
Kiem tra ket noi DB bang endpoint `/api/db-health`.

## Dang nhap va phan quyen

He thong luu tai khoan va session trong PostgreSQL, dung chung `DATABASE_URL`.
Bang `app_users` va `user_sessions` se duoc tao tu dong.

Neu database chua co user nao, app se tao admin mac dinh:

```text
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

Nen doi `ADMIN_PASSWORD` trong `.env` truoc lan chay dau tien tren moi truong that. Admin truy cap `/admin` de tao/sua tai khoan va phan quyen.

Neu user admin da duoc tao truoc do va muon dong bo lai mat khau admin tu `.env`, them:

```text
ADMIN_SYNC_PASSWORD=1
```

Sau khi app khoi dong lai va cap nhat xong, nen bo dong nay de tranh ghi de mat khau admin moi lan restart.
