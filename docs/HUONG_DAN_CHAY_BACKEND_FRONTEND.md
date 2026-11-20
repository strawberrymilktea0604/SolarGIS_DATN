# HƯỚNG DẪN KHỞI CHẠY & KIỂM THỬ HỆ THỐNG (POSTGIS, RUST AXUM BACKEND & NEXT.JS MAPLIBRE FRONTEND)

**Dự án:** Hệ thống Bản sao số (Digital Twin) & AI Đa luồng Giám sát Nhà máy Điện mặt trời (`SolarGIS_DATN`)  
**Module phụ trách:** Module 3 — Thành viên 3 (`PostGIS 16-3.4` + `Rust Axum` + `Next.js / MapLibre GL JS 60 FPS`)

---

## 1. YÊU CẦU MÔI TRƯỜNG ĐÃ CÀI ĐẶT TRÊN MÁY
Trên máy Windows hiện tại của bạn đã có sẵn đầy đủ bộ công cụ:
- **Docker Desktop:** `Docker version 29.x` (dùng để chạy container `PostGIS 16-3.4` và `Redis 7`).
- **Rust Toolchain:** `cargo` & `rustc` (dùng để biên dịch và chạy `solar_backend` trên cổng `8080`).
- **Node.js & npm:** `Node.js v24.x` & `npm v11.x` (dùng để chạy giao diện bản đồ `Next.js + MapLibre GL JS` trên cổng `3000`).

---

## 2. QUY TRÌNH 4 BƯỚC CHẠY THỬ NGAY TRÊN MÁY CỤC BỘ (WINDOWS POWERSHELL)

Để quá trình phát triển và gỡ lỗi (debug) thuận tiện nhất, bạn nên bật **PostGIS + Redis bằng Docker**, còn **Rust Backend** và **Next.js Frontend** chạy trực tiếp trên PowerShell để có Hot-Reload nhanh.

### Bước 1: Kiểm tra file `.env` & Khởi chạy Cơ sở dữ liệu PostGIS 16-3.4 + Redis 7
Toàn bộ mật khẩu CSDL (`POSTGRES_PASSWORD`) và chuỗi kết nối (`DATABASE_URL`) đã được tách riêng ra file [`.env`](file:///c:/Users/Admin/Documents/Project/SolarGIS_DATN/SolarGIS_DATN/.env) ở thư mục gốc (file này đã nằm trong `.gitignore` nên không bao giờ bị lộ lên Git; khi thành viên khác clone repo về chỉ cần copy từ [`.env.example`](file:///c:/Users/Admin/Documents/Project/SolarGIS_DATN/SolarGIS_DATN/.env.example) sang `.env`).

Mở **PowerShell #1** tại thư mục gốc của dự án (`c:\Users\Admin\Documents\Project\SolarGIS_DATN\SolarGIS_DATN`) và chạy:

```powershell
# 1. Khởi chạy riêng 2 container nền tảng là PostGIS và Redis (nạp biến từ file .env)
docker compose --env-file .env -f infra/docker-compose.yml up -d postgis redis

# 2. Kiểm tra trạng thái container (đợi chữ "healthy")
docker ps
```

Khi container `solargis_postgis` khởi chạy lần đầu, nó sẽ **tự động thực thi theo thứ tự** 4 file SQL trong thư mục [infra/postgres/init/](file:///c:/Users/Admin/Documents/Project/SolarGIS_DATN/SolarGIS_DATN/infra/postgres/init):
1. [01_schema.sql](file:///c:/Users/Admin/Documents/Project/SolarGIS_DATN/SolarGIS_DATN/infra/postgres/init/01_schema.sql): Tạo 7 bảng không gian (`EPSG:32649`), khóa nguyên `mvt_id BIGSERIAL` và chỉ mục R-Tree `GIST`.
2. [02_triggers.sql](file:///c:/Users/Admin/Documents/Project/SolarGIS_DATN/SolarGIS_DATN/infra/postgres/init/02_triggers.sql): Tạo Trigger `trg_sync_module_health_after_inspection` (kiểm tra `MAX(flight_date)` và bắt đủ `INSERT / UPDATE / DELETE`).
3. [03_mvt_funcs.sql](file:///c:/Users/Admin/Documents/Project/SolarGIS_DATN/SolarGIS_DATN/infra/postgres/init/03_mvt_funcs.sql): Tạo hàm `get_solar_modules_mvt(z, x, y, plant_id)` xuất Vector Tiles nhị phân (`ST_AsMVT`).
4. [04_seed_and_benchmark.sql](file:///c:/Users/Admin/Documents/Project/SolarGIS_DATN/SolarGIS_DATN/infra/postgres/init/04_seed_and_benchmark.sql): Tạo sẵn danh mục 4 trang trại (`TN19`, `BIM2`, `TNDL`, `TT12`) và hàm sinh lưới mẫu `seed_synthetic_tn19_modules()`.

---

### Bước 2: Sinh 36.544 Tấm pin Mẫu của Thuận Nam 19 (hoặc Nạp file `.gpkg` thật) & Đo `EXPLAIN ANALYZE`

#### Trường hợp A: Chưa có file `.gpkg` từ TV1 (Chạy lưới mẫu 36.544 tấm pin Thuận Nam 19 ngay lập tức)
Chạy lệnh sau trên **PowerShell #1** để sinh 36.544 tấm pin của nhà máy Thuận Nam 19 (đúng tọa độ `EPSG:32649`, kích thước chuẩn $\Delta u = 1,13\text{ m}, \Delta v = 2,27\text{ m}$) và gán thử một số tấm pin bị lỗi `CoA 2` (vàng) và `CoA 3` (đỏ) để thấy rõ màu sắc trên bản đồ:

```powershell
# 1. Gọi hàm sinh 36.544 tấm pin chuẩn cho Thuận Nam 19
docker exec -it solargis_postgis psql -U solargis -d solargis_db -c "SELECT seed_synthetic_tn19_modules(36544); ANALYZE solar_modules;"

# 2. (Tùy chọn) Giả lập 1 đợt bay mới nhất và chèn thử lỗi nhiệt CoA 2 / CoA 3 để kiểm chứng Trigger tự động đổi màu tấm pin
docker exec -it solargis_postgis psql -U solargis -d solargis_db -c "
UPDATE solar_modules SET current_coa_class = 3, current_health_status = 'Bypass' WHERE mvt_id % 47 = 0;
UPDATE solar_modules SET current_coa_class = 2, current_health_status = 'SingleHotSpot' WHERE mvt_id % 23 = 0;
"
```

#### Trường hợp B: Khi đã có file `thuannam19_master.gpkg` trong `data/gpkg/`
```powershell
python infra/postgres/ingest_gpkg_to_postgis.py --gpkg data/gpkg/thuannam19_master.gpkg --plant TN19
```

#### Chạy lệnh khảo sát `EXPLAIN ANALYZE` (lấy số liệu cho Đầu việc 1.6):
```powershell
# Đo thời gian xuất 1 ô Vector Tile động ST_AsMVT (< 8 ms, < 30 KB)
docker exec -it solargis_postgis psql -U solargis -d solargis_db -c "EXPLAIN (ANALYZE, BUFFERS) SELECT OCTET_LENGTH(get_solar_modules_mvt(17, 104674, 61072, 1));"
```

---

### Bước 3: Khởi chạy Backend 100% Rust (`Axum` + `Tokio` + `SQLx`)
Backend Rust (`solar_backend`) đã được tích hợp sẵn bộ đọc tự động file `.env` ở thư mục gốc (`load_dotenv_file()`), nên bạn **không cần gõ tay mật khẩu trên PowerShell nữa**. Mở **PowerShell #2**, di chuyển vào thư mục Module 3 và chạy:

```powershell
cd c:\Users\Admin\Documents\Project\SolarGIS_DATN\SolarGIS_DATN\modules\module3_digital_twin_app

# Biên dịch và khởi chạy server Rust Axum tại cổng 8080 (tự động đọc DATABASE_URL từ file .env)
cargo run --bin solar_backend
```

Khi thấy dòng log:
```text
INFO solar_backend: SolarGIS Rust Axum Backend listening on http://0.0.0.0:8080
```
Bạn có thể mở trình duyệt hoặc chạy `curl` để kiểm tra ngay các API:
- Kiểm tra kết nối PostGIS: `http://localhost:8080/api/health`
- Danh sách 4 trang trại: `http://localhost:8080/api/plants`
- Luồng Vector Tiles `.mvt`: `http://localhost:8080/api/tiles/1/17/104674/61072.mvt`

---

### Bước 4: Khởi chạy Giao diện Web Quản trị Bản sao số (`Next.js` + `MapLibre GL JS` 60 FPS)
Mở **PowerShell #3**, di chuyển vào thư mục `frontend` của Module 3:

```powershell
cd c:\Users\Admin\Documents\Project\SolarGIS_DATN\SolarGIS_DATN\modules\module3_digital_twin_app\frontend

# 1. Cài đặt các thư viện (next, react, maplibre-gl, pmtiles)
npm install

# 2. Khởi chạy máy chủ giao diện ở cổng 3000
npm run dev
```

Sau khi lệnh báo `Ready in ... on http://localhost:3000`, hãy mở trình duyệt truy cập:
- **`http://localhost:3000`**

---

## 3. CÁC TÍNH NĂNG BẠN CÓ THỂ TƯƠNG TÁC NGAY TRÊN GIAO DIỆN WEB (`http://localhost:3000`)
1. **Kiểm tra trạng thái kết nối:** Ở góc trên thanh bên trái (Sidebar), trạng thái sẽ báo màu xanh lá: **`Đã kết nối PostGIS & Rust Axum`**.
2. **Hiển thị 36.544 tấm pin ở 60 FPS qua Vector Tiles (`ST_AsMVT`):**
   - Bản đồ [page.tsx](file:///c:/Users/Admin/Documents/Project/SolarGIS_DATN/SolarGIS_DATN/modules/module3_digital_twin_app/frontend/src/app/page.tsx) tự động phóng tới khu vực lưới pin của **Nhà máy Thuận Nam 19** (`center: [108.893, 11.439], zoom: 17.2`).
   - Các tấm pin khỏe mạnh hiển thị màu **Xanh lá (`CoA 1`)**, các tấm pin bất thường nhiệt hiển thị màu **Vàng cam (`CoA 2`)** và **Đỏ (`CoA 3`)** theo đúng chuẩn **IEC TS 62446-3:2017**.
3. **Bấm chọn từng tấm pin (Inspector Drawer):**
   - Click chuột vào bất kỳ ô đa giác tấm pin nào trên bản đồ, khung **Chi tiết Tấm pin (Inspector Drawer)** ở bên trái sẽ lập tức đọc khóa nguyên `mvt_id` (`e.features[0].id`) và các thuộc tính `module_id` (ví dụ `tn19_block1_string4_00015`), `Row_ID`, `ID_Pin`, trạng thái lỗi và phân hạng `CoA 1 / 2 / 3`.
4. **Bộ lọc nhanh theo cấp độ bất thường (`Tất cả` / `CoA 2` / `CoA 3`):**
   - Bấm vào các nút lọc ở Sidebar để chỉ hiển thị các tấm pin đang gặp sự cố nhiệt trên bản đồ.

---

## 4. CÁC LỆNH XỬ LÝ SỰ CỐ THƯỜNG GẶP (TROUBLESHOOTING)
- **Làm mới hoàn toàn CSDL PostGIS (khi bạn sửa file trong `infra/postgres/init/`):**
  ```powershell
  docker compose -f infra/docker-compose.yml down -v
  docker compose -f infra/docker-compose.yml up -d postgis redis
  ```
  *(Cờ `-v` sẽ xóa volume cũ để container PostGIS chạy lại các file `01_schema.sql` $\rightarrow$ `04_seed_and_benchmark.sql` từ đầu).*
- **Đổi cổng Backend nếu cổng `8080` bị chiếm:** Tạo biến môi trường `$env:NEXT_PUBLIC_BACKEND_URL="http://localhost:8081"` trước khi chạy `npm run dev`.
