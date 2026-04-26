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
