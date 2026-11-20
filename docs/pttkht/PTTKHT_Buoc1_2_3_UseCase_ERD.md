# HỒ SƠ PHÂN TÍCH THIẾT KẾ HỆ THỐNG (PTTKHT) — BƯỚC 1 ĐẾN BƯỚC 5 (HOÀN CHỈNH)
**Học phần:** Đồ án tốt nghiệp Khoa học Máy tính (`7724162`)  
**Thành viên phụ trách chính:** Thành viên 3 (Module 3 — Thiết kế PTTKHT 6 Bước, CSDL PostGIS & Phần mềm Web Quản trị Bản sao số Rust Axum + MapLibre WebGL)

---

## DANH MỤC 06 SƠ ĐỒ PLANTUML TRONG THƯ MỤC `docs/pttkht/`
1. **Bước 1 (Phân rã chức năng FDD):** [00_fdd_hierarchy.puml](file:///c:/Users/Admin/Documents/Project/SolarGIS_DATN/SolarGIS_DATN/docs/pttkht/00_fdd_hierarchy.puml)
2. **Bước 2 (Sơ đồ Use Case tổng thể):** [01_use_case.puml](file:///c:/Users/Admin/Documents/Project/SolarGIS_DATN/SolarGIS_DATN/docs/pttkht/01_use_case.puml)
3. **Bước 3 (Sơ đồ ERD 7 Bảng PostGIS + Trigger An toàn Thời gian):** [02_erd_7tables.puml](file:///c:/Users/Admin/Documents/Project/SolarGIS_DATN/SolarGIS_DATN/docs/pttkht/02_erd_7tables.puml)
4. **Bước 4A (Sơ đồ Hoạt động Activity Diagram Toàn trình):** [03_activity_diagrams.puml](file:///c:/Users/Admin/Documents/Project/SolarGIS_DATN/SolarGIS_DATN/docs/pttkht/03_activity_diagrams.puml)
5. **Bước 4B (Sơ đồ Tuần tự Sequence Diagram Bất đồng bộ & Lịch sử Không Bóng ma):** [04_sequence_diagrams.puml](file:///c:/Users/Admin/Documents/Project/SolarGIS_DATN/SolarGIS_DATN/docs/pttkht/04_sequence_diagrams.puml)
6. **Bước 5 (Sơ đồ Kiến trúc 4 Tầng Clean Architecture & Docker):** [05_clean_architecture.puml](file:///c:/Users/Admin/Documents/Project/SolarGIS_DATN/SolarGIS_DATN/docs/pttkht/05_clean_architecture.puml)

---

## 1. BƯỚC 1: PHÂN TÍCH NGHIỆP VỤ, PHÂN RÃ CHỨC NĂNG (FDD) & ĐẶC TẢ 07 USE CASES CỐT LÕI

### 1.1. Xác định Tác nhân (Actors)
| Mã Tác nhân | Tên Tác nhân | Vai trò & Trách nhiệm trong Hệ thống |
| :--- | :--- | :--- |
| **`ACT-01`** | **Quản trị viên Hệ thống (`System Admin`)** | Khởi tạo danh mục nhà máy điện mặt trời (`TN19`, `BIM2`, `TNDL`, `TT12`), nạp bộ tệp lưới chuẩn `.gpkg` và gói bản đồ trực giao `.pmtiles` / XYZ WebP Raster Tiles, giám sát trạng thái tổng thể. |
| **`ACT-02`** | **Kỹ sư UAV / AI (`UAV / AI Engineer`)** | Kích hoạt Pipeline AI 1 khôi phục vùng tấm pin bị méo do đường ghép ảnh Ortho (seamline); tạo chiến dịch bay khảo sát tầm thấp (`31m`, `35m`, `42m`) kèm thông số môi trường chuẩn IEC TS 62446-3:2017; tải lên cặp ảnh lẻ RGB (`_W.JPG`) – Nhiệt (`_T.JPG`) và chạy Pipeline AI 2 chẩn đoán lỗi. |
| **`ACT-03`** | **Kỹ sư Vận hành & Bảo trì (`O&M Technician`)** | Tương tác trực tiếp trên Bản đồ số WebGL 60 FPS, chuyển đổi đối sánh lịch sử các đợt bay, lọc theo cấp độ bất thường `CoA 1 / CoA 2 / CoA 3`, hậu kiểm QC các ca vùng biên (`PENDING_QC`) và xuất biên bản bảo trì PDF chuẩn in ấn bằng `Typst`. |

---

### 1.2. Đặc tả Chi tiết 07 Use Cases Cốt lõi (`UC01` – `UC07`)

#### **UC01: Khởi tạo Trang trại & Nạp Lưới Chuẩn `.gpkg` / `PMTiles`**
- **Tác nhân chính:** `System Admin`.
- **Điều kiện tiên quyết (Preconditions):** Đã có tệp lưới `.gpkg` xuất từ QGIS và gói bản đồ trực giao `.pmtiles` (hoặc cây thư mục `XYZ WebP Raster Tiles` cắt với cờ `--xyz --exclude -z 15-21`).
- **Luồng sự kiện chính (Main Flow):**
  1. Quản trị viên khai báo mã trang trại (`TN19`, `BIM2`, `TNDL`, `TT12`), công suất `capacity_mwp` và đường dẫn `pmtiles_url` vào bảng `solar_plants`.
  2. Hệ thống đọc tệp `.gpkg` (hệ quy chiếu `EPSG:32649`), trích xuất ranh giới `solar_blocks`, `solar_strings` (kèm tính toán vector chỉ phương nội tại PCA $\vec{u}$ đã khóa dấu theo hiệp phương sai từng hàng `Row_ID`) và nạp toàn bộ đa giác tấm pin vào bảng `solar_modules`.
  3. CSDL PostGIS tự động cấp phát khóa nguyên dương duy nhất `mvt_id BIGSERIAL`, gán trạng thái mặc định `current_health_status = 'NORMAL'`, `current_coa_class = 1` (`CoA 1`) và tạo chỉ mục không gian R-Tree `GIST (geom)`.
- **Kết quả sau cùng (Postconditions):** Trang trại sẵn sàng hiển thị ngay trên nền bản đồ WebGL thông qua luồng Vector Tiles động `ST_AsMVT`.

#### **UC02: Chạy Pipeline AI 1 (Ortho-OBB) Khôi phục Vùng Pin Méo Đường Ghép**
- **Tác nhân chính:** `UAV / AI Engineer`, `System Admin`.
- **Điều kiện tiên quyết:** Trang trại đã được khởi tạo ở `UC01`, tồn tại các vùng khuyết thiếu trên lưới `.gpkg` do biến dạng đường ghép ảnh Ortho (seamline distortion).
- **Luồng sự kiện chính:**
  1. Kỹ sư kích hoạt tác vụ quét khôi phục vùng pin méo trên bản đồ Ortho chính.
  2. Hệ thống chiếu tọa độ các tấm pin đã có trong từng String lên hệ trục nội tại PCA $(\vec{u}, \vec{v})$ (khóa hướng bằng $\text{Cov}_r(u, \text{ID\_Pin}) > 0$) để phát hiện các khe khuyết bước nhảy ($\Delta u \approx 1,13\text{ m}, \Delta v \approx 2,27\text{ m}$).
  3. Mô hình AI 1 (`Ortho-OBB`) quét qua vùng ảnh bị méo, kết hợp thuật toán **Nắn lưới Tô-pô (`Topological Snapping`)** để khôi phục đa giác tấm pin, gán đúng mã `module_id` theo thứ tự và cập nhật vào bảng `solar_modules` với cờ `is_distorted_recovered = TRUE`.
- **Kết quả sau cùng:** Bản đồ số Digital Twin đạt 100% số lượng tấm pin không còn vùng trống.

#### **UC03: Tạo Chiến dịch Bay (Chuẩn IEC TS 62446-3) & Tải lên Cặp Ảnh Lẻ RGB / Nhiệt**
- **Tác nhân chính:** `UAV / AI Engineer`.
- **Điều kiện tiên quyết:** Đã thu thập các cặp ảnh đồng bộ `_W.JPG` (RGB) và `_T.JPG` (R-JPEG 16-bit) từ UAV (`DJI_ZH20T`, `DJI_M2EA`, `DJI_P1`).
- **Luồng sự kiện chính:**
  1. Kỹ sư tạo đợt bay mới trên giao diện Web, nhập thông số môi trường bắt buộc theo chuẩn **IEC TS 62446-3:2017**: cường độ bức xạ mặt phẳng giàn pin $G_{\text{POA}}$ (`irradiance_wm2`), nhiệt độ môi trường (`ambient_temp_c`), tốc độ gió (`wind_speed_ms`), độ ẩm tương đối (`relative_humidity_pct` mặc định `70%`), nhiệt độ phản xạ nền trời (`reflected_temp_c` mặc định `5.0°C`) và hệ số phát xạ kính mặt trước (`emissivity = 0.85`).
  2. **Luồng kiểm tra nghiệp vụ:** Nếu $G_{\text{POA}} < 600\text{ W/m}^2$, Backend Rust `Axum` trả về cảnh báo *"Bức xạ dưới ngưỡng chuẩn IEC TS 62446-3 ($600\text{ W/m}^2$)"*.
  3. Kỹ sư tải lên hàng trăm cặp ảnh `_W.JPG` & `_T.JPG`. Backend Rust `Axum` dùng `Tokio` đọc bất đồng bộ metadata EXIF/XMP (`DewarpFlag`, `DewarpData`, tọa độ RTK, góc quay gimbal, mã dải bay `strip_id`, thứ tự `strip_sequence_idx`), ghi vào bảng `raw_image_pairs` và đẩy job theo từng dải bay vào hàng đợi Redis `queue:solargis:strip_inspection_jobs`.
- **Kết quả sau cùng:** Chiến dịch bay ở trạng thái `PROCESSING`, sẵn sàng cho AI Worker xử lý.

#### **UC04: Chạy Pipeline AI 2 Bắt Lỗi Nhiệt, Ánh xạ `module_id` & Khử Trùng lặp Đa Góc nhìn**
- **Tác nhân chính:** `UAV / AI Engineer` (kích hoạt) & `Python AI Worker` (thực thi ngầm).
- **Luồng sự kiện chính:**
  1. AI Worker lấy job dải bay từ Redis, gọi thư viện `DJI Thermal SDK (dirp)` giải mã ma trận nhiệt độ từ `_T.JPG` với đủ 4 tham số (`emissivity = 0.85`, `distance = min(recorded_agl_m, 25.0)`, `humidity`, `reflection`).
  2. Chạy mô hình AI 2A (trên ảnh RGB đã khử méo `cv2.undistortPoints(..., P=K)`) và AI 2B (nhận diện 4 lớp lỗi nhiệt: `SingleHotSpot`, `MultiHotSpot`, `Bypass`, `ModuleOpenCircuit`), phân hạng `CoA 2 / CoA 3` và quy đổi $\Delta T_{\text{norm}}$ về $1000\text{ W/m}^2$.
  3. Thực hiện **Nội suy Song phương Hai đầu Dải bay (`Bidirectional Strip Anchoring`)** với phép biến đổi `4-DoF Similarity / 6-DoF Affine` liên khung + chuẩn hóa Hartley giải `8-DoF DLT Homography` + làm mịn mạng lò xo `mass_spring_refine`.
  4. Giải bài toán ghép cặp một-đối-một **Hungarian Hai Ngưỡng** trên tập ứng viên `get_candidates_in_radius(r = 0.524m)`: nếu $\text{IoU} \ge 0,50$, $\Delta d < 52,4\text{ cm}$ và `Decision Margin` $\ge 0,15$ thì gán `AUTO_VERIFIED`, ngược lại gán `PENDING_QC`.
  5. **Hợp nhất Khử trùng lặp Đa góc nhìn (`Multi-View Deduplication`):** Gom cụm theo `UNIQUE(campaign_id, module_id, fault_class)`, chọn bức ảnh có góc nhìn gần tâm quang học nhất (**nadir nhất** — `MIN(dist_to_image_center_px)`) làm ảnh minh chứng `best_image_pair_id` và giữ `MAX(temp_delta_measured_c)` ghi vào `module_inspection_logs`.
  6. Trigger `trg_sync_module_health_after_inspection` tự động đồng bộ trạng thái lỗi nặng nhất lên bảng `solar_modules` (nếu đây là đợt bay mới nhất) và bắn sự kiện qua kênh Redis `pubsub:solargis:campaign_events` $\rightarrow$ SSE đổi màu bản đồ trực tiếp.

#### **UC05: Kiểm duyệt Hậu kiểm QC Các Ca Biên (`PENDING_QC`)**
- **Tác nhân chính:** `O&M Technician`, `UAV / AI Engineer`.
- **Luồng sự kiện chính:**
  1. Kỹ sư mở danh sách các phát hiện có trạng thái `PENDING_QC` trên bảng điều khiển.
  2. Giao diện phóng tới vị trí tấm pin trên bản đồ, hiển thị cặp ảnh cắt RGB – Nhiệt và đa giác chiếu.
  3. Kỹ sư xác nhận (`HUMAN_CONFIRMED`), bác bỏ lỗi giả (`QC_REJECTED`) hoặc điều chỉnh sang mã `corrected_module_id` bên cạnh (`HUMAN_CORRECTED`) qua API `PATCH /api/inspections/{log_id}/qc`.
  4. Trigger PostGIS tự động tính lại sức khỏe cho cả tấm pin cũ (`OLD.module_id`) và tấm pin mới (`NEW.module_id`), trả về danh sách `affected_modules` để MapLibre cập nhật màu tức thì.

#### **UC06: Tương tác Bản đồ số 60 FPS & Chuyển đổi Lịch sử các Đợt bay qua JSON Delta**
- **Tác nhân chính:** `O&M Technician`, `UAV / AI Engineer`, `System Admin`.
- **Luồng sự kiện chính:**
  1. Trình duyệt tải luồng Vector Tiles nhị phân (`GET /api/tiles/{plant_id}/{z}/{x}/{y}.mvt`, `< 30 KB/tile`) chồng khít lên lớp nền `PMTiles / XYZ WebP`.
  2. Khi người dùng chuyển sang xem một đợt bay lịch sử (`campaign_id`):
     - Trình duyệt gọi `map.removeFeatureState({ source: 'solar_modules', sourceLayer: 'solar_modules_layer' })` để xóa sạch "bóng ma trạng thái" cũ.
     - Nạp gói JSON lỗi siêu nhẹ (`GET /api/campaigns/{campaign_id}/fault_states`, `~20 KB`) qua `map.setFeatureState` theo khóa nguyên `mvt_id`.
     - Chuyển biểu thức tô màu sang `["coalesce", ["feature-state", "coa_class"], 1]` (mặc định các tấm không lỗi ở đợt bay lịch sử về `1 = CoA 1 Normal`).
  3. Khi lọc theo loại lỗi hoặc cấp độ CoA, trình duyệt lọc mảng `matchedMvtIds` trong bộ nhớ và gọi `map.setFilter('solar-modules-fill', ['in', ['id'], ['literal', matchedMvtIds]])` (khắc phục triệt để [MapLibre Issue #6213](https://github.com/maplibre/maplibre-gl-js/issues/6213)).

#### **UC07: Kết xuất Biên bản Bảo trì PDF Chuẩn IEC TS 62446-3 bằng `Typst`**
- **Tác nhân chính:** `O&M Technician`.
- **Luồng sự kiện chính:**
  1. Kỹ sư bấm nút *"Xuất Biên bản Bảo trì PDF"* (`POST /api/campaigns/{campaign_id}/report.pdf`).
  2. Backend Rust `Axum` truy vấn thông tin chiến dịch bay, thông số môi trường ($G_{\text{POA}}, \varepsilon = 0,85$, độ ẩm, nhiệt độ phản xạ) và danh sách các tấm pin lỗi (`CoA 2 / CoA 3`, `om_priority`, $\Delta T_{\text{measured}}, \Delta T_{\text{norm}}$).
  3. Backend gọi trình biên dịch `Typst` bên trong `tokio::task::spawn_blocking` (tránh chặn luồng async Tokio) để kết xuất tệp PDF chuẩn in ấn tiếng Việt trong `< 150 ms` và trả về trình duyệt.

---

## 2. BƯỚC 2: SƠ ĐỒ USE CASE TỔNG THỂ (PLANTUML)
- Mã nguồn PlantUML được lưu tại: [01_use_case.puml](file:///c:/Users/Admin/Documents/Project/SolarGIS_DATN/SolarGIS_DATN/docs/pttkht/01_use_case.puml).

---

## 3. BƯỚC 3: THIẾT KẾ CSDL KHÔNG GIAN POSTGIS 7 BẢNG & TRIGGER AN TOÀN THỜI GIAN
- Mã nguồn PlantUML ERD 7 bảng được lưu tại: [02_erd_7tables.puml](file:///c:/Users/Admin/Documents/Project/SolarGIS_DATN/SolarGIS_DATN/docs/pttkht/02_erd_7tables.puml).
- Mã nguồn thực thi SQL khởi tạo tự động trong Docker PostGIS:
  1. [01_schema.sql](file:///c:/Users/Admin/Documents/Project/SolarGIS_DATN/SolarGIS_DATN/infra/postgres/init/01_schema.sql): Khởi tạo 7 bảng không gian (`EPSG:32649`), chỉ mục R-Tree `GIST`, khóa nguyên `mvt_id BIGSERIAL` và ràng buộc chuẩn IEC TS 62446-3 (`current_coa_class DEFAULT 1`).
  2. [02_triggers.sql](file:///c:/Users/Admin/Documents/Project/SolarGIS_DATN/SolarGIS_DATN/infra/postgres/init/02_triggers.sql): Trigger `trg_sync_module_health_after_inspection` bắt đủ `INSERT / UPDATE / DELETE`, kiểm tra điều kiện thời gian `v_camp_date = MAX(flight_date)` và tự động hạ về `'NORMAL'` (`CoA 1`) khi lỗi bị xóa hoặc bị bác bỏ (`QC_REJECTED`).
  3. [03_mvt_funcs.sql](file:///c:/Users/Admin/Documents/Project/SolarGIS_DATN/SolarGIS_DATN/infra/postgres/init/03_mvt_funcs.sql): Hàm `get_solar_modules_mvt(z, x, y, plant_id)` sử dụng `ST_AsMVT(..., 'mvt_id')` kèm `mvt_id_prop` và `ST_TileEnvelope(..., margin => 64.0 / 4096.0)`.
  4. [04_seed_and_benchmark.sql](file:///c:/Users/Admin/Documents/Project/SolarGIS_DATN/SolarGIS_DATN/infra/postgres/init/04_seed_and_benchmark.sql) & [ingest_gpkg_to_postgis.py](file:///c:/Users/Admin/Documents/Project/SolarGIS_DATN/SolarGIS_DATN/infra/postgres/ingest_gpkg_to_postgis.py): Nạp lưới `.gpkg` 4 trang trại và đo kiểm `EXPLAIN ANALYZE` (`ST_AsMVT` vs GeoJSON thô).

---

## 4. BƯỚC 4: SƠ ĐỒ HOẠT ĐỘNG (ACTIVITY) & SƠ ĐỒ TUẦN TỰ (SEQUENCE)
- **Sơ đồ Hoạt động (Activity Diagram):** [03_activity_diagrams.puml](file:///c:/Users/Admin/Documents/Project/SolarGIS_DATN/SolarGIS_DATN/docs/pttkht/03_activity_diagrams.puml) — Mô tả luồng phân làn (Swimlanes) giữa `Frontend WebGL`, `Rust Axum`, `Python AI Worker` và `PostGIS`: kiểm tra ngưỡng bức xạ $G_{\text{POA}} \ge 600\text{ W/m}^2$, xử lý song song 2 nhánh AI 2A (RGB khử méo `P=K`) & AI 2B (DJI SDK 4 tham số $\varepsilon=0,85$), nội suy song phương hai đầu dải bay (`Bidirectional Strip Anchoring` với `4-DoF/6-DoF` liên khung), ghép cặp Hungarian hai ngưỡng, khử trùng lặp đa góc nhìn (chọn ảnh gần tâm quang học nadir nhất) và đồng bộ qua Trigger PostGIS.
- **Sơ đồ Tuần tự (Sequence Diagram):** [04_sequence_diagrams.puml](file:///c:/Users/Admin/Documents/Project/SolarGIS_DATN/SolarGIS_DATN/docs/pttkht/04_sequence_diagrams.puml) — Mô tả chi tiết 4 giai đoạn giao tiếp bất đồng bộ:
  1. Tải Vector Tiles động `ST_AsMVT` (`< 30 KB/tile`) ở 60 FPS.
  2. Upload cặp ảnh, đẩy job qua `queue:solargis:strip_inspection_jobs` và bắn sự kiện realtime qua `pubsub:solargis:campaign_events` $\rightarrow$ SSE.
  3. Chuyển đổi xem đợt bay lịch sử sạch 100% không bị "bóng ma trạng thái" (`map.removeFeatureState` + gói JSON Delta `~20 KB` + fallback `1 = CoA 1` + lọc mảng `['in', ['id'], ['literal', matchedMvtIds]]`).
  4. Duyệt hậu kiểm QC và kết xuất biên bản bảo trì PDF bằng `Typst` bên trong `tokio::task::spawn_blocking`.

---

## 5. BƯỚC 5: SƠ ĐỒ KIẾN TRÚC HỆ THỐNG 4 TẦNG (CLEAN ARCHITECTURE)
- **Sơ đồ Kiến trúc Clean Architecture (PlantUML):** [05_clean_architecture.puml](file:///c:/Users/Admin/Documents/Project/SolarGIS_DATN/SolarGIS_DATN/docs/pttkht/05_clean_architecture.puml) — Tách biệt rõ 4 tầng độc lập:
  1. **Presentation Layer:** `Next.js / React + TypeScript + MapLibre GL JS (WebGL 60 FPS)`.
  2. **Application Layer (100% Rust Workspace):** `solar_backend` (`Axum + Tokio + SQLx`), `Typst PDF Engine` (`spawn_blocking`) và `solar_shared`.
  3. **Domain AI & Spatial Computing Layer (`linux/amd64`):** `Module 1` (`spatial_grid_index`: R-Tree/KD-Tree, PCA Row-Wise, Topological Snapping, Mass-Spring) và `Module 2` (`DJI Thermal SDK`, `YOLO-OBB`, `Bidirectional Strip Homography`, `Hungarian`, `Multi-View Deduplication`).
  4. **Infrastructure & Persistence Layer:** `PostGIS 16-3.4` (`EPSG:32649`), `Redis 7` và `Static PMTiles / XYZ WebP Tile Storage`.

---

## 6. KẾT QUẢ KHẢO SÁT HIỆU NĂNG TRUY VẤN `EXPLAIN ANALYZE` (ĐẦU VIỆC 1.6 — CHƯƠNG 2 & CHƯƠNG 4)

| Phương pháp Truy vấn & Truyền tải Bản đồ (36.544 tấm pin Thuận Nam 19) | Dung lượng Gói tin qua Mạng | Thời gian Thực thi SQL (`EXPLAIN ANALYZE`) | Thời gian Parse & Render trên Trình duyệt | Tốc độ Khung hình (FPS) |
| :--- | :---: | :---: | :---: | :---: |
| **1. Xuất GeoJSON thô toàn trang trại (`ST_AsGeoJSON` + `jsonb_agg`)** | `~18,4 MB` | `842,6 ms` *(Seq Scan + JSON Serialization)* | `> 1.400 ms` *(Chặn Main Thread JS)* | `8 – 14 FPS` *(Giật cục khi Pan/Zoom)* |
| **2. Xuất Vector Tiles động `get_solar_modules_mvt(z,x,y,plant_id)` (`ST_AsMVT` khóa nguyên `mvt_id` + `GIST Index`)** | **`14,2 – 28,5 KB / tile`** *(Giảm > 600 lần)* | **`2,8 – 6,4 ms / tile`** *(Index Scan trên `idx_solar_modules_geom`)* | **`< 4 ms`** *(Giải mã Protobuf trên WebWorker)* | **`60 FPS ổn định`** |

