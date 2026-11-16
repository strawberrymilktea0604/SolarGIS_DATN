# KẾ HOẠCH PHÂN CÔNG CÔNG VIỆC CHI TIẾT GIAI ĐOẠN 1 & LỘ TRÌNH 9 TUẦN (`16/11/2026` – `17/01/2027`) — BẢN HOÀN THIỆN V6 (FINAL RELEASE CANDIDATE)

## ĐỀ TÀI: HỆ THỐNG BẢN SAO SỐ (DIGITAL TWIN) & AI ĐA LUỒNG GIÁM SÁT NHÀ MÁY ĐIỆN MẶT TRỜI TỪ DỮ LIỆU UAV

* **Quy mô nhóm:** `03` Thành viên — Phân bổ tải trọng cân bằng **`33% (TV1) – 33% (TV2) – 34% (TV3)`**
* **Thời gian thực hiện:** `16/11/2026` – `17/01/2027` (`09` tuần)
* **Danh mục 05 lỗ hổng logic ngầm & 02 tinh chỉnh san tải đường găng đã khóa chặt 100% trong Bản V6 (Trước khi ký `DATA_CONTRACT.md` ngày `16/11/2026`):**
  1. **Triệt tiêu Bug "Bóng ma trạng thái" (`Ghost State`) & Giới hạn `setFilter` trên MapLibre GL JS (TV3 – Đầu việc 5.3):** Khi người dùng chuyển sang xem một đợt bay cũ trong lịch sử (`isHistoricalView = true`), trình duyệt bắt buộc gọi [map.removeFeatureState](https://maplibre.org/maplibre-gl-js/docs/API/classes/Map/) `({ source: 'solar_modules', sourceLayer: 'solar_modules_layer' })` trước khi áp gói JSON lỗi (`~20 KB`), đồng thời đổi biểu thức tô màu sang `["coalesce", ["feature-state", "coa_class"], 1]` (mặc định tấm không nằm trong JSON lỗi về `1 = Normal`, tuyệt đối không fallback về cột `["get", "current_coa_class"]` của đợt bay mới nhất). Khi lọc chỉ hiển thị tấm pin lỗi ở đợt bay lịch sử, do [MapLibre Issue #6213](https://github.com/maplibre/maplibre-gl-js/issues/6213) không hỗ trợ `["feature-state", ...]` trong `layer.filter`, giao diện dùng `map.setFilter('solar-modules-fill', ['in', ['id'], ['literal', faultMvtIds]])` (hoặc điều khiển `fill-opacity: 0` trong `paint`).
  2. **Chống Race Condition & Ghi đè Đợt bay cũ / Đa lỗi trong PostgreSQL Trigger `trg_sync_module_health_after_inspection` (TV2 & TV3 – Đầu việc 1.6 & 5.2):** Trong hàm Trigger PL/pgSQL, bắt buộc kiểm tra điều kiện `IF v_camp_date = (SELECT MAX(flight_date) FROM flight_campaigns WHERE plant_id = v_plant_id)` mới cho phép cập nhật bảng `solar_modules` (tránh lỗi re-upload đợt bay tháng 4 ghi đè mất trạng thái đợt bay tháng 10), và khi 1 tấm pin mắc đồng thời nhiều lỗi trong cùng đợt bay thì ưu tiên giữ `MAX(iec_coa_class)` và `fault_class` nặng nhất (`ModuleOpenCircuit > Bypass > MultiHotSpot > SingleHotSpot`).
  3. **Giải trình giới hạn độ phân giải $5 \times 5\text{ pixels/cell}$ theo Phụ lục A.1 [IEC TS 62446-3:2017](https://datatec.es/wp-content/uploads/2019/09/Normativa-IEC-TS-62446-3.pdf) khi bay `31m – 42m` (TV2 – Đầu việc 6.2 & 7.2):** Đưa phép tính quang học của cảm biến nhiệt Zenmuse H20T ($f = 13,5\text{ mm}, p = 12\ \mu\text{m}$) vào báo cáo: ở `31m` đạt $\text{GSD}_{\text{thermal}} \approx 2,75\text{ cm/px}$ ($\ge 5,6 \times 5,6\text{ px/cell}$ — đạt chuẩn kiểm định cấp cell cho cell $15,6\text{ cm}$), ở `35m` đạt $\approx 3,11\text{ cm/px}$ (xấp xỉ biên $5 \times 5$), còn ở `42m` đạt $\approx 3,73\text{ cm/px}$ ($\approx 4,2 \times 4,2\text{ px/cell}$ — chịu hiệu ứng trung bình hóa diện tích điểm ảnh *Spot-Size Effect* làm giảm nhẹ $\Delta T_{\text{measured}}$ của lỗi `SingleHotSpot`), qua đó chứng minh cơ sở vật lý cho khuyến nghị bay ở dải `31m–35m`.
  4. **Khử trôi dạt tỷ lệ phối cảnh (`Perspective Scale Drift`) ở độ cao 31m bằng Nội suy Song phương Hai đầu Dải bay (`Bidirectional Strip Anchoring`) với `4-DoF/6-DoF` liên khung (TV2 – Đầu việc 4.2):** Thay vì nhân chuỗi ma trận phối cảnh 8 bậc tự do qua 15–25 khung hình liên tiếp, TV2 neo cứng cả 2 đầu dải bay ($t_{\text{start}}$ và $t_{\text{end}}$ nhìn thấy biên lối đi hai bên), ước lượng phép biến đổi cứng `4-DoF Similarity / 6-DoF Affine` giữa các khung hình liên tiếp kết hợp nội suy song phương hai đầu và kẹp tâm bức ảnh trong bán kính sai số RTK ($\pm 10\text{ cm}$) trước khi giải `8-DoF DLT Homography (Hartley)` cục bộ với lưới `.gpkg`.
  5. **Thêm cờ `--exclude` và giới hạn `-z 15-21` trong lệnh [gdal2tiles.py](https://opengxt.mangosystem.com/gdal/programs/gdal2tiles.html) + Tinh chỉnh San tải Đường găng (TV1, TV2, TV3 – Đầu việc 1.3, 2.4, 3.3):**
     - Lệnh `gdal2tiles.py --xyz --exclude --processes=8 -z 15-21 --tiledriver=WEBP --webp-quality=85` bỏ qua toàn bộ các ô rỗng ở viền đen/trong suốt và dừng ở mức zoom `21` (tương ứng độ phân giải gốc $1\text{ cm/px}$ 1:1, tránh tốn gấp 4 lần ổ cứng ở mức zoom 22). TV1 xuất trước gói `PMTiles/MBTiles` của nhà máy `Thuận Nam 19` ngay ngày thứ 3 của Tuần 1 để TV3 dựng Web sớm.
     - Chuyển việc viết `Dockerfile` đóng gói `libdirp.so` + `libv_*.so` + `libv_list.ini` và khung `Redis Worker` ở Tuần 3 sang cho TV1 & TV3 phụ trách để giảm tải cho TV2; đồng thời TV3 chốt luôn kiến trúc **Backend 100% Rust `Axum` + Frontend `React / TypeScript (Next.js) + MapLibre GL JS`** ngay từ đầu Tuần 2 để dành trọn thời gian tối ưu UX 60 FPS, bộ lọc lịch sử đợt bay, QC Queue và mẫu báo cáo `Typst`.

---

## DANH MỤC 06 NGUỒN DỮ LIỆU TIỀN SƠ KHAI CHÍNH THỨC (CHỈ ĐỊNH RÕ RÀNG CHO TỪNG MODULE)

1. **Nguồn 1 — Bộ tệp Lưới `.gpkg` đã vẽ bằng QGIS của cả 4 Trang trại (Dành cho TV1 & TV3):**
   * Tệp [thuannam19_master.gpkg](https://drive.google.com/file/d/1ytHofNRDcg9pFgoFGIhPRunAOChdTycN/view?usp=drivesdk) (`36.544` tấm pin chia 6 Block, 148 String + lớp ảnh `orthophoto_87m`), các file `Block1.gpkg`..`Block6.gpkg` trong [Mapping 1](https://www.google.com/search?q=https://drive.google.com/drive/folders/1YRM4ZKcbs0kbv4Erp4QW1XaB3p4jYbjl) và các file `.gpkg` đã vẽ bằng QGIS trên máy của 3 trang trại `BIM 2`, `Thuận Nam Đức Long`, `Thiên Tân 1.2`.
2. **Nguồn 2 — Bản đồ Trực giao Chính (`.tif`), Mô hình Độ cao (`DEM .tif`) & File Hiệu chuẩn Camera (`SonarPanel.xml`) của 4 Trang trại (Dành cho TV1 & TV2):**
   * Thư mục [SolarGISExport](https://drive.google.com/drive/folders/1AZRTJ8_ywbQ5bM90SK7C_bmgeReL6B9n) gồm 4 nhánh:
     * [1. Nhà máy BIM 2 - 10.4](https://www.google.com/search?q=https://drive.google.com/drive/folders/1WTOCRZBoMsuxe5vDS0Rzmpc8R9JJM73b) ([SonarPanelOrthoGeoTIFF.tif](https://drive.google.com/file/d/19k_ia4llf9KCkB4fFUKR3GyV2AQadmxu/view?usp=drivesdk), [SonarPanel.xml](https://drive.google.com/file/d/1webOywFx4nrVcAh5fksJt--954sU1QA2/view?usp=drivesdk)).
     * [2. Nhà máy Thuận Nam 19 -11/4](https://www.google.com/search?q=https://drive.google.com/drive/folders/1Ij6uwNGUt4jcxVz_ziVh8GVTnxhW8PQK) ([SonarPanel.tif](https://drive.google.com/file/d/1-DUPuL4MTz3m78p0BV1IeujSOut_esIq/view?usp=drivesdk), [SonarPanel.xml](https://drive.google.com/file/d/1URpxCueIAsw04BcJr-eepvSqc9Adxp5k/view?usp=drivesdk)).
     * [3. Nhà máy Thuận Nam Đức Long - 11.4](https://www.google.com/search?q=https://drive.google.com/drive/folders/1XW-7dqv9eY4zyisO54M3ynrzFFfTy3r3) ([SonarPanelOrthoGeoTIFF.tif](https://drive.google.com/file/d/1WrAFbh_WOvAMbpFP5e0eNgodggf2d1ZR/view?usp=drivesdk), [SolarPanel.xml](https://drive.google.com/file/d/1iSMODWjS_OoNbsqysz-rTDqKmrIBxBgL/view?usp=drivesdk)).
     * [4. Điện mặt trời Thiên Tân 1.2](https://www.google.com/search?q=https://drive.google.com/drive/folders/1DZBOKkgHn8xfMliNeHWyKJgSSHCuktCW) ([SonarPanelOrthoGeoTIFF.tif](https://drive.google.com/file/d/1fpnqBPQdIcpw2t9ZezBEkOzJlTu3e1hn/view?usp=drivesdk), [SonarPanel.xml](https://drive.google.com/file/d/1COdFfCHdxIVqLjq5ajmPcO03jlosvIgk/view?usp=drivesdk), [Thien Tan 12.tif](https://drive.google.com/file/d/1BjYr4Y6dzG9JuYvb8vnt1Ep4IqQVR5gF/view?usp=drivesdk)).
3. **Nguồn 3 — Các bản đồ Ortho vùng bay thấp (`31m`, `35m`, `42m`) & Ortho nhiệt (Dành cho TV1 & TV2):**
   * Thư mục [SolarPanel\_ExportOrtho](https://www.google.com/search?q=https://drive.google.com/drive/folders/1r9IpvEDOiUttqkTFHFfX1D4kgsqZk2y0) ([ThuanNam19\_Export](https://www.google.com/search?q=https://drive.google.com/drive/folders/1nKL1GspOozQI_p4wT0ag-9gmeWVX7pD-), [BIM2\_Export](https://www.google.com/search?q=https://drive.google.com/drive/folders/1CDPEBNRe62Ww0FEpxhtZ5eI15oRB2Ynx), [ThuanNamDucLong\_Export](https://www.google.com/search?q=https://drive.google.com/drive/folders/1VOOgETSe7tz01MwSoQH8UEZUsJ4FYsZ4), [ThienTan\_Export](https://www.google.com/search?q=https://drive.google.com/drive/folders/15PpXKcDpTmQzyksb6AUqgixrLBb6Oy3O)).
4. **Nguồn 4 — Ảnh bay UAV gốc (Cặp ảnh lẻ RGB `_W.JPG` & Ảnh nhiệt R-JPEG `_T.JPG`) của 4 Trang trại (Dành cho TV2):**
   * Thư mục [1. Khảo sát điện mặt trời Ninh Thuận -4/2026](https://www.google.com/search?q=https://drive.google.com/drive/folders/1pNG8IsaklZ65U-JpmXnPZmDTCVDmwlu9) (`12.557` ảnh tại Thuận Nam 19 và các thư mục ảnh gốc của BIM 2, Thuận Nam Đức Long, Thiên Tân 1.2).
5. **Nguồn 5 — Bộ nhãn OBB Tiền sơ khai Nhận diện Tấm pin trên Ảnh lẻ RGB (Dành cho TV2 – Nhánh AI 2A):**
   * Thư mục `images` và `labels` gốc trong kho [SolarGIS\_Dataset\_1](https://www.google.com/search?q=https://github.com/strawberrymilktea0604/SolarGIS_Dataset_1) và kho [**Roboflow solar-segment-obb**](https://universe.roboflow.com/qu-nguyn-nh-s-workspace/solar-segment-obb) *(xóa bỏ toàn bộ file `.pt`, `.csv` cũ và không dùng bộ `Fine-Tuning`)*.
6. **Nguồn 6 — Bộ nhãn OBB Tiền sơ khai 4 Lớp Lỗi Nhiệt trên Ảnh Nhiệt (Dành cho TV2 – Nhánh AI 2B):**
   * Thư mục [**Dataset SolarGIS - Thermal**](https://drive.google.com/drive/folders/13FbPVPVISPv3EP0hrTF-lqKFfJ2dJ8zl) gồm [images](https://www.google.com/search?q=https://drive.google.com/drive/folders/11xlcA2VLmS8bQmlqPn-pzMMjSOykfHch) và [labels](https://www.google.com/search?q=https://drive.google.com/drive/folders/1sQxDAJ9hVDUGEOWMcv5d90ZxNRPz9yaW) (chứa các file `ThuanNam19__31M/35M/42M__DJI_..._T.jpg` và `.txt`), cùng dữ liệu gốc trong kho [SolarGIS\_Dataset\_2](https://www.google.com/search?q=https://github.com/strawberrymilktea0604/SolarGIS_Dataset_2) *(xóa bỏ file `fault_obb_4class.pt` cũ)*.

---

## PHẦN I: CHI TIẾT TỪNG ĐẦU VIỆC GIAI ĐOẠN 1 (TUẦN 1 & TUẦN 2: `16/11/2026` – `29/11/2026`)
*(Mục tiêu kết thúc Giai đoạn 1: Báo cáo **Mốc M1 – 20% điểm** gồm Đề cương nhiệm vụ `Mẫu ĐATN-01`, Bản vẽ 6 bước PTTKHT, Bộ dữ liệu sạch đã chia Train/Val/Test và Bảng khảo sát huấn luyện mô hình mới từ đầu).*

### TUẦN 1 (`16/11/2026` – `22/11/2026`): Tập hợp Đủ `.gpkg` 4 Trang trại, Nội suy Vùng Pin Méo bằng Trục PCA Khóa Hướng Từng Hàng, Xuất Sớm `PMTiles` Thuận Nam 19, Khử Méo `DewarpData` (`P=K`), Giải mã `DJI SDK` (Chuẩn `CoA 1/2/3`) & Thiết kế PTTKHT

#### Đầu việc 1.1 (Cả nhóm – Ngày 16/11 đến 17/11): Chốt Phiếu giao nhiệm vụ `Mẫu ĐATN-01`, Gom đủ `.gpkg` 4 Trang trại & Ký Hợp đồng Giao tiếp Dữ liệu (`DATA_CONTRACT.md`)
* **1. Phải làm những gì:**
  * Điền hoàn chỉnh biểu mẫu `Mẫu ĐATN-01` (trong `HUCE_QD_DATN_v2_260119.docx`) ghi rõ tên đề tài và 3 Module cá nhân đã cân bằng tải (`33% – 33% – 34%`).
  * Tập hợp toàn bộ các file `.gpkg` đã vẽ bằng QGIS của cả 4 nhà máy (`Thuận Nam 19`, `BIM 2`, `Thuận Nam Đức Long`, `Thiên Tân 1.2`) lên chung 1 thư mục chuẩn.
  * Khởi tạo kho GitHub mới tinh (`solargis-digital-twin-rust`) và ký kết văn bản `DATA_CONTRACT.md` quy định rõ kiểu dữ liệu đầu vào/đầu ra giữa 3 Module (chữ ký hàm `spatial_grid_index`, JSON Schema qua Redis Queue, quy ước `CoA 1 = Normal`, `CoA 2/3 = Abnormality`, Trigger kiểm tra `MAX(flight_date)` và cơ chế `removeFeatureState` trên MapLibre).
* **2. Dùng những bộ dữ liệu gì:**
  * File `Quy định Tổ chức thực hiện và đánh giá ĐATN của Trường ĐHXDHN.pdf`, `HUCE_QD_DATN_v2_260119.docx`, `2. Đề cương HP-ĐATN-V2.docx`, [thuannam19_master.gpkg](https://drive.google.com/file/d/1ytHofNRDcg9pFgoFGIhPRunAOChdTycN/view?usp=drivesdk) và các file `.gpkg` của 3 nhà máy còn lại.
* **3. Cách thức làm:**
  * Thống nhất quy tắc đặt khóa chính `module_id` là `{plant_code}_block{B}_string{S}_{ID_Pin:05d}` (đi kèm khóa số nguyên dương `mvt_id BIGSERIAL UNIQUE` dùng thống nhất cho Vector Tiles `.mvt` và `MapLibre setFeatureState`), hệ tọa độ lưu trữ trong PostGIS là `EPSG:32649` (UTM Zone 49N), hệ tọa độ truyền Vector Tiles lên Web là `EPSG:3857` (Web Mercator), và 4 mã lớp lỗi nhiệt là `0: SingleHotSpot`, `1: MultiHotSpot`, `2: Bypass`, `3: ModuleOpenCircuit`.
* **4. Khảo sát như thế nào:**
  * Viết 1 script Python đọc trực tiếp header của các file Ortho `.tif`, `.xml` và `.gpkg` của cả 4 nhà máy để xuất ra **Bảng kiểm kê thông số kỹ thuật 4 trang trại Ninh Thuận**: Loại drone/camera (`ZH20T`, `M2EA`, `Zenmuse P1`), độ cao bay kế hoạch vs thực tế, GSD RGB & GSD Nhiệt thực tế (cm/px), mã EPSG gốc và tổng số tấm pin đã vẽ trong mỗi file `.gpkg`.

#### Đầu việc 1.2 (Thành viên 1 – Module 1): Quét bộ `.gpkg` của 4 Trang trại tìm vùng tấm pin bị méo chưa vẽ & Tự động nội suy khung bù theo Hệ trục Nội tại PCA Khóa Hướng Từng Hàng (`Row-Wise Covariance Orientation-Locked PCA`)
* **1. Phải làm những gì:**
  * Khi vẽ lưới tấm pin trên QGIS cho 4 trang trại, những vùng tấm pin bị méo nặng do đường ghép ảnh Ortho (seamline) đã bị bỏ trống. Bạn phải viết thuật toán tự động tìm tất cả các lỗ khuyết đó trên các file `.gpkg` và vẽ bù đa giác vào mà không phụ thuộc vào góc xoay của giàn pin, không bị lật dấu khi String bị khuyết cột đầu/cuối hoặc đánh số zíc-zắc.
* **2. Dùng những bộ dữ liệu gì:**
  * Bảng `modules` trong [thuannam19_master.gpkg](https://drive.google.com/file/d/1ytHofNRDcg9pFgoFGIhPRunAOChdTycN/view?usp=drivesdk), các file `Block1.gpkg`..`Block6.gpkg` trong [Mapping 1](https://www.google.com/search?q=https://drive.google.com/drive/folders/1YRM4ZKcbs0kbv4Erp4QW1XaB3p4jYbjl) và các file `.gpkg` đã vẽ bằng QGIS của `BIM 2`, `Thuận Nam Đức Long`, `Thiên Tân 1.2`, đối chiếu với ảnh nền `SonarPanel.tif` / `SonarPanelOrthoGeoTIFF.tif` trong [SolarGISExport](https://drive.google.com/drive/folders/1AZRTJ8_ywbQ5bM90SK7C_bmgeReL6B9n).
* **3. Cách thức làm (Đã gia cố khóa hướng PCA theo tương quan từng hàng `Row_ID`):**
  * **Bước 1 (Xác định Hệ trục Nội tại $(\vec{u}, \vec{v})$ bằng PCA và Khóa Dấu bằng Hiệp phương sai Từng Hàng):** Với mỗi `(Block, String_ID)`, lấy tập hợp tâm các tấm pin đã vẽ, phân tích thành phần chính (**PCA**) để tìm vector riêng dọc theo chiều dài dãy pin $\vec{u} = (\cos\theta, \sin\theta)$. Thay vì chỉ lấy 2 điểm cực trị $\mathbf{p}_{\min}, \mathbf{p}_{\max}$, thuật toán tính hiệp phương sai dọc theo từng hàng `Row_ID` $r \in \{1, 2, 3, 4\}$ riêng biệt:
    $$\text{Cov}_r(u, \text{ID\_Pin}) = \sum_{i \in \text{Row } r} (u_i - \bar{u}_r)(\text{ID\_Pin}_i - \overline{\text{ID\_Pin}}_r)$$
    Nếu $\sum_r \text{Cov}_r < 0$ thì đổi dấu $\vec{u} \leftarrow -\vec{u}$ (đồng thời nếu phát hiện hàng $r$ nào có dấu $\text{Cov}_r$ ngược với hàng còn lại thì tự động chuẩn hóa lại chiều đánh số zíc-zắc của hàng đó), và cố định vector pháp tuyến $\vec{v} = (-u_y, u_x)$ theo quy tắc bàn tay phải.
  * **Bước 2 (Phát hiện lỗ khuyết trên trục nội tại):** Chiếu tâm các tấm pin lên hệ trục $(u, v)$ của String. Trong mỗi hàng `Row_ID` $\in \{1, 2, 3, 4\}$ (cách nhau $\Delta v \approx 2,27\text{ m}$), sắp xếp các tấm pin tăng dần theo tọa độ dọc $u$. Chỗ nào số thứ tự `ID_Pin` bị nhảy cóc (như `Block1` Thuận Nam 19 khuyết `4049..4068`, hoặc `string35..37` khuyết ở rìa méo) hoặc khoảng cách dọc $\Delta u > 1,6\text{ m}$ (so với bước chuẩn $\Delta u \approx 1,13\text{ m}$), thuật toán đánh dấu đó là lỗ khuyết vùng méo.
  * **Bước 3 (Nội suy đa giác bù):** Dịch chuyển dọc theo vector $\vec{u}$ các bước bằng đúng $\Delta u$ (hoặc chiếu từ hàng nguyên vẹn lân cận sang theo vector $\vec{v}$ một đoạn $\Delta v$) để tự động sinh các đa giác bù vào đúng chỗ tấm pin bị méo, gắn cờ `panel_type = 'distorted_seamline'`.
* **4. Khảo sát như thế nào:**
  * Lập bảng thống kê trên cả 4 trang trại: Góc nghiêng trung bình $\theta$ (độ) của các dãy pin ở từng nhà máy, số lượng String đánh số thuận chiều vs zíc-zắc phát hiện được nhờ $\text{Cov}_r$, số tấm pin chuẩn đã vẽ sẵn trong `.gpkg`, và số lượng tấm pin vùng méo nội suy bù thêm được ở từng trang trại.

#### Đầu việc 1.3 (Thành viên 1 – Module 1): Cắt mảnh Bản đồ Ortho $1024 \times 1024$ từ `.gpkg` Đa Trang trại & Xuất Cây Thư mục `XYZ WebP Raster Tiles` (`--exclude -z 15-21` + Xuất sớm Thuận Nam 19 trong Tuần 1)
* **1. Phải làm những gì:**
  * Cắt ảnh Ortho `.tif` và đa giác trong `.gpkg` (đã có đủ cả tấm pin thẳng lẫn tấm pin méo từ Đầu việc 1.2) thành bộ dữ liệu chuẩn YOLO-OBB ($1024 \times 1024$ pixel), chia tập `Train / Valid / Test` theo phân khu không gian đa trang trại.
  * Chạy kịch bản `GDAL` có cờ `--exclude` và giới hạn `-z 15-21` để xuất **XYZ Tiles (`.webp`) / gói `PMTiles`**. **Lịch bàn giao sớm chống nghẽn:** Xuất xong nhà máy `Thuận Nam 19` ngay ngày thứ 3 của Tuần 1 (`18/11/2026`) để TV3 có dữ liệu dựng bản đồ WebGL sớm; 3 nhà máy còn lại cho chạy nền trong Tuần 2.
* **2. Dùng những bộ dữ liệu gì:**
  * Bộ file `.gpkg` đã bù vùng méo và các file ảnh `SonarPanel.tif` / `SonarPanelOrthoGeoTIFF.tif` của 4 nhà máy trong [SolarGISExport](https://drive.google.com/drive/folders/1AZRTJ8_ywbQ5bM90SK7C_bmgeReL6B9n) cùng các bản đồ vùng tại [SolarPanel\_ExportOrtho](https://www.google.com/search?q=https://drive.google.com/drive/folders/1r9IpvEDOiUttqkTFHFfX1D4kgsqZk2y0).
* **3. Cách thức làm (Đã bổ sung `--exclude` và giới hạn `-z 15-21` theo [GDAL gdal2tiles](https://opengxt.mangosystem.com/gdal/programs/gdal2tiles.html)):**
  * **Bước 1 (Chia tập Train/Val/Test không rò rỉ):** Chia theo ranh giới các `Block` trong `.gpkg` của 4 trang trại: `Train (60%)` gồm `Block2`, `Block4` của Thuận Nam 19 + các Block huấn luyện của `BIM 2`, `Thuận Nam Đức Long`; `Valid (15%)` gồm `Block1`, `Block3` của Thuận Nam 19 + Block kiểm định của `BIM 2`; `Test (25%)` giữ độc lập `Block5`, `Block6` của Thuận Nam 19 và các phân khu kiểm thử của `Thiên Tân 1.2` / `BIM 2`.
  * **Bước 2 (Cắt ảnh huấn luyện):** Dùng `rasterio` trượt cửa sổ $1024 \times 1024$ pixel (chồng lấn `20%`), đổi tọa độ 4 đỉnh đa giác (kèm mã `module_id` gốc) từ mét (`EPSG:32649`) sang tọa độ pixel của ô cắt; nếu xoay ảnh $270^\circ$ thì áp dụng cùng ma trận xoay cho tọa độ 4 đỉnh đa giác, cộng thêm `10%` ô ảnh nền âm tính.
  * **Bước 3 (Xuất XYZ WebP Raster Tiles bằng câu lệnh chuẩn GDAL có `--exclude`):** Bắt buộc dùng cờ `--xyz` (để gốc $y=0$ ở phía Bắc), `--exclude` (bỏ qua toàn bộ các ô rỗng ở viền đen/trong suốt quanh nhà máy) và giới hạn ở `-z 15-21` (vì GSD $\approx 1\text{ cm/px}$ đã đạt độ phân giải 1:1 ở mức zoom 21):
    ```bash
    gdal2tiles.py --xyz --exclude --processes=8 -z 15-21 --tiledriver=WEBP --webp-quality=85 input_ortho.tif output_tiles/
    ```
    *(Sau đó đóng gói cây thư mục `output_tiles/` thành 1 file `.pmtiles` hoặc `.mbtiles` duy nhất để triển khai Docker cực gọn).*
* **4. Khảo sát như thế nào:**
  * Khảo sát đối sánh giữa kích thước ô cắt ($640 \times 640$ vs $1024 \times 1024$), lượng dung lượng ổ cứng tiết kiệm được khi bật cờ `--exclude -z 15-21` (giảm $> 75\%$ số lượng file rỗng so với chạy `-z 14-22` không lọc) và tốc độ tải mảnh bản đồ `.webp` (`< 5 ms/tile`).

#### Đầu việc 1.4 (Thành viên 2 – Module 2, Nhánh AI 2A): Chia tập Ảnh lẻ RGB cách ly `15m` & Khử méo ống kính (`DewarpFlag`, Gốc Tâm ảnh `W/2, H/2` & Tham số `P=K` trong `cv2.undistortPoints`)
* **1. Phải làm những gì:**
  * Lấy bộ ảnh lẻ RGB và nhãn OBB tiền sơ khai (xóa bỏ mọi file `.pt`, `.csv` cũ), chia thành 3 tập `Train (60%) – Valid (15%) – Test (25%)` có dải đệm cách ly `15m`.
  * Viết hàm **Khử méo ống kính (Lens Undistortion)** xử lý đúng gốc tọa độ tâm quang học của DJI, cờ `DewarpFlag` và truyền đúng ma trận chiếu `P=K` khi khử méo tọa độ đỉnh nhãn OBB.
* **2. Dùng những bộ dữ liệu gì:**
  * Thư mục `images` và `labels` tiền sơ khai trong [SolarGIS\_Dataset\_1](https://www.google.com/search?q=https://github.com/strawberrymilktea0604/SolarGIS_Dataset_1) và [**Roboflow solar-segment-obb**](https://universe.roboflow.com/qu-nguyn-nh-s-workspace/solar-segment-obb).
  * Ảnh lẻ gốc `_W.JPG` ở các độ cao `31m`, `35m`, `42m` trong [1. Khảo sát điện mặt trời Ninh Thuận -4/2026](https://www.google.com/search?q=https://drive.google.com/drive/folders/1pNG8IsaklZ65U-JpmXnPZmDTCVDmwlu9) và các file hiệu chuẩn [SonarPanel.xml](https://drive.google.com/file/d/1URpxCueIAsw04BcJr-eepvSqc9Adxp5k/view?usp=drivesdk).
* **3. Cách thức làm (Đã vá lỗi tọa độ chuẩn hóa của [cv2.undistortPoints](https://docs.pupil-labs.com/alpha-lab/undistort/)):**
  * **Bước 1 (Chia dải cách ly 15m):** Đọc tọa độ RTK (`GPSLatitude`, `GPSLongitude`, `RtkFlag = 50`), mã dải bay (`strip_id`), số thứ tự ảnh trong dải bay (`strip_sequence_idx`) và độ cao thực tế (`Recorded AGL`: `30,9m`, `34,9m`, `41,9m`) trong EXIF để tính đa giác vùng phủ mặt đất (`Camera Ground Footprint`). Chia khu vực bay thành 3 dải cột không gian ngăn cách bởi **dải đệm rộng `15m`** (loại bỏ mọi ảnh có footprint chạm vào dải đệm).
  * **Bước 2 (Kiểm tra `DewarpFlag`, Quy đổi gốc `(cx, cy)` & Truyền `P=K` vào `cv2.undistortPoints`):**
    1. Đọc thẻ XMP `drone-dji:DewarpFlag`: nếu `DewarpFlag == 1`, ghi `dewarp_applied_in_camera = TRUE` và không gọi `cv2.undistort`.
    2. Nếu `DewarpFlag == 0`: đọc chuỗi `drone-dji:DewarpData = "date;fx,fy,cx,cy,k1,k2,p1,p2,k3"` (hoặc đọc từ `SonarPanel.xml` làm nguồn dự phòng). Cộng thêm nửa kích thước ảnh để đổi gốc từ tâm cảm biến sang góc trên bên trái của OpenCV:
       $$c_{x,\text{opencv}} = \frac{W}{2.0} + c_{x,\text{dewarp}}, \quad c_{y,\text{opencv}} = \frac{H}{2.0} + c_{y,\text{dewarp}}$$
    3. Lập ma trận nội tại $K = \begin{bmatrix} f_x & 0 & c_{x,\text{opencv}} \\ 0 & f_y & c_{y,\text{opencv}} \\ 0 & 0 & 1 \end{bmatrix}$. Gọi `cv2.undistort(img, K, distCoeffs)` cho ảnh `_W.JPG` và **bắt buộc truyền `P=K`** khi biến đổi tọa độ pixel của 4 đỉnh nhãn OBB:
       ```python
       pts_undistorted_px = cv2.undistortPoints(pts_px, K, distCoeffs, R=None, P=K)
       pts_yolo_norm = pts_undistorted_px / np.array([W, H], dtype=np.float32)
       ```
* **4. Khảo sát như thế nào:**
  * Lập bảng khảo sát độ nhạy của dải đệm (`5m`, `10m`, `15m`, `20m`) và kiểm chứng trực quan bằng cách vẽ chồng hộp nhãn OBB sau khi `cv2.undistortPoints(..., P=K)` lên ảnh đã khử méo.

#### Đầu việc 1.5 (Thành viên 2 – Module 2, Nhánh AI 2B): Chuẩn hóa Bộ nhãn 4 Lớp Lỗi Nhiệt, Tích hợp Đủ 4 Trường `DJI Thermal SDK (dirp)` & Chuẩn hóa Phân hạng `CoA 1 / CoA 2 / CoA 3` theo IEC TS 62446-3
* **1. Phải làm những gì:**
  * Chuẩn hóa bộ dữ liệu ảnh nhiệt `_T.JPG` ($640 \times 512$) và nhãn OBB 4 lớp lỗi nhiệt theo dải cách ly `15m`.
  * Bọc thư viện chuẩn **DJI Thermal SDK (`dirp`)** kèm các tệp phụ thuộc `libv_*.so`, `libv_list.ini`, truyền đủ 4 trường vật lý của `dirp_measurement_params_t` (theo [dirp_api.h](https://github.com/Mendru/DJI_thermal_SDK/blob/main/tsdk-core/api/dirp_api.h)) và áp dụng đúng định nghĩa phân hạng **CoA 1 (Normal) / CoA 2 (Thermal Abnormality) / CoA 3 (Safety-Relevant Abnormality)** của chuẩn [IEC 62446 Standards](https://solarthermography.com/blog/iec-62446-standards/).
* **2. Dùng những bộ dữ liệu gì:**
  * Thư mục [**Dataset SolarGIS - Thermal**](https://drive.google.com/drive/folders/13FbPVPVISPv3EP0hrTF-lqKFfJ2dJ8zl) ([images](https://www.google.com/search?q=https://drive.google.com/drive/folders/11xlcA2VLmS8bQmlqPn-pzMMjSOykfHch) & [labels](https://www.google.com/search?q=https://drive.google.com/drive/folders/1sQxDAJ9hVDUGEOWMcv5d90ZxNRPz9yaW) gồm các file `ThuanNam19__31M/35M/42M__DJI_..._T.jpg` và `.txt`), dữ liệu gốc trong [SolarGIS\_Dataset\_2](https://www.google.com/search?q=https://github.com/strawberrymilktea0604/SolarGIS_Dataset_2) và cặp ảnh gốc `_T.JPG` trong [1. Khảo sát điện mặt trời Ninh Thuận -4/2026](https://www.google.com/search?q=https://drive.google.com/drive/folders/1pNG8IsaklZ65U-JpmXnPZmDTCVDmwlu9).
* **3. Cách thức làm:**
  * **Bước 1:** Kiểm tra tự động toàn bộ file `.txt` để đảm bảo mỗi khung OBB bao trọn 1 tấm pin bị lỗi (`0: SingleHotSpot`, `1: MultiHotSpot`, `2: Bypass`, `3: ModuleOpenCircuit`); các tấm pin bình thường không có hộp lỗi (mặc định thuộc `CoA 1 = Normal`).
  * **Bước 2 (Gọi `dirp_get_measurement_params` trước rồi ghi đè đủ 4 trường vật lý):**
    1. Đặt `libdirp.so` cùng thư mục với toàn bộ các file `libv_*.so` và `libv_list.ini`.
    2. Khởi tạo handle bằng `dirp_create_from_rjpeg`, gọi **`dirp_get_measurement_params(handle, &params)`** trước để đọc cấu hình gốc trong R-JPEG, sau đó ghi đè 4 trường:
       * `params.emissivity = 0.85` (mặt kính cường lực phía trước ở góc chụp nadir theo [IEA PVPS Task 13](https://iea-pvps.org/wp-content/uploads/2020/01/Review_on_IR_and_EL_Imaging_for_PV_Field_Applications_by_Task_13.pdf)).
       * `params.distance = min(recorded_agl_m, 25.0)` (kẹp trần trong dải `[1.0m – 25.0m]` của `dirp_api.h`).
       * `params.humidity = relative_humidity_pct` (mặc định `70.0%`).
       * `params.reflection = reflected_temp_c` (giữ giá trị hiện trường trong R-JPEG hoặc lấy nhiệt độ bức xạ biểu kiến nền trời quang từ `flight_campaigns`). *Lưu ý thuyết minh: sai số dịch chuyển trên $T_{\max}$ tuyệt đối do thiếu tấm phản xạ nhôm nhăn ASTM E1862 bị triệt tiêu bậc nhất khi lấy hiệu số $\Delta T_{\text{measured}} = T_{\max} - T_{\text{median\_string}}$ trên cùng mặt kính đồng nhất.*
    3. Gọi `dirp_set_measurement_params` và `dirp_measure_ex` để lấy mảng nhiệt độ thực `float32` ($640 \times 512$) tính bằng độ C.
  * **Bước 3 (Phân hạng `CoA 2 / CoA 3` kết hợp Hình thái + $\Delta T_{\text{measured}}$ và Quy đổi $\Delta T_{\text{norm}}$ theo IEC TS 62446-3):**
    * Tấm pin bình thường: `CoA 1` (`current_coa_class = 1`).
    * Tấm pin có lỗi nhiệt: phân vào **`CoA 2` (Thermal abnormality)** hoặc **`CoA 3` (Safety-relevant abnormality)** dựa trên hình thái lỗi (`Bypass`, `ModuleOpenCircuit` hoặc điểm nóng có $\Delta T_{\text{measured}} > 20^\circ\text{C} \rightarrow \text{CoA 3}$; điểm nóng nhẹ $\Delta T_{\text{measured}} \le 20^\circ\text{C} \rightarrow \text{CoA 2}$) đi kèm nhãn độ ưu tiên O&M nội bộ `om_priority IN ('LOW', 'MEDIUM', 'HIGH')`.
    * Tính và lưu song song $\Delta T_{\text{norm}} = \Delta T_{\text{measured}} \times \left(\frac{1000}{G_{\text{POA}}}\right)^x$ ($x = 1,0$).
* **4. Khảo sát như thế nào:**
  * Lập bảng so sánh nhiệt độ đọc ra giữa 3 trường hợp: (1) Dịch byte `APP3` tuyến tính thô, (2) Dùng `DJI Thermal SDK` với `emissivity = 0.95`, và (3) Dùng `DJI Thermal SDK` với đủ 4 tham số chuẩn (`emissivity = 0.85`, `d <= 25.0m`, `humidity`, `reflection`) theo IEC TS 62446-3.

#### Đầu việc 1.6 (Thành viên 3 – Module 3): Hoàn thành Bước 1, 2, 3 của PTTKHT & Khởi tạo CSDL PostGIS 7 Bảng hỗ trợ `ST_AsMVT` (`mvt_id_prop`, `margin` & Trigger Kiểm tra `MAX(flight_date)`)
* **1. Phải làm những gì:**
  * Thiết kế phần mềm Quản lý Bản sao số mới hoàn toàn từ đầu theo Bước 1, Bước 2, Bước 3 của PTTKHT; trong đó mỗi thành viên (TV1, TV2, TV3) tự phác thảo luồng tuần tự của module mình để giảm tải cho TV3.
  * Dựng CSDL PostgreSQL/PostGIS gồm 7 bảng (có khóa `mvt_id BIGSERIAL`, `current_coa_class DEFAULT 1`, đủ 4 cột môi trường IEC 62446-3, `dewarp_applied_in_camera`, `strip_id`, `strip_sequence_idx`, ràng buộc `UNIQUE(campaign_id, module_id, fault_class)`, **PostgreSQL Trigger đồng bộ ngược có kiểm tra `MAX(flight_date)` và ưu tiên lỗi nặng**, cùng hàm truy vấn Vector Tiles động `ST_AsMVT`).
* **2. Dùng những bộ dữ liệu gì:**
  * File mẫu `TONG_QUAN_DU_AN.md`, tệp [thuannam19_master.gpkg](https://drive.google.com/file/d/1ytHofNRDcg9pFgoFGIhPRunAOChdTycN/view?usp=drivesdk) và các file `.gpkg` của 3 trang trại `BIM 2`, `Thuận Nam Đức Long`, `Thiên Tân 1.2`.
* **3. Cách thức làm:**
  * **Bước 1:** Viết đặc tả 7 Use Cases, vẽ sơ đồ Use Case và vẽ sơ đồ ERD 7 bảng (`solar_plants`, `plant_blocks_strings`, `solar_modules`, `flight_campaigns`, `raw_image_pairs`, `ai_raw_detections`, `module_inspection_logs`).
  * **Bước 2:** Dựng Docker `postgis/postgis:16-3.4`, nạp toàn bộ đa giác tấm pin từ các file `.gpkg` của 4 trang trại vào bảng `solar_modules`, tạo chỉ mục không gian R-Tree `GIST (geom)`, tạo Trigger `trg_sync_module_health_after_inspection` (kiểm tra `v_camp_date = MAX(flight_date)` và chọn `ORDER BY iec_coa_class DESC` khi 1 tấm pin có nhiều lỗi) và viết hàm SQL `get_solar_modules_mvt(z, x, y, plant_id)` dùng `ST_AsMVT(tile, 'solar_modules_layer', 4096, 'geom', 'mvt_id')` (trong đó `SELECT m.mvt_id, m.mvt_id AS mvt_id_prop, m.module_id, ...`) và `ST_TileEnvelope(z, x, y, margin => (64.0 / 4096.0))`.
* **4. Khảo sát như thế nào:**
  * Chạy `EXPLAIN ANALYZE` đo thời gian truy vấn và dung lượng gói tin truyền qua mạng giữa **Xuất GeoJSON thô (`~18 MB`, mất `> 800 ms`)** với **Xuất Vector Tiles động `ST_AsMVT` (`< 30 KB/tile`, chỉ mất `< 8 ms`)** để đưa vào Chương 2 và Chương 4 báo cáo.

---

### TUẦN 2 (`23/11/2026` – `29/11/2026`): Khảo sát Nhanh 4 Họ Mô hình trên `Stratified Subset`, Huấn luyện Mô hình Mới, Chốt API `spatial_grid_index` & Báo cáo Mốc M1 (20%)

#### Đầu việc 2.1 (Thành viên 1 – Module 1): Khảo sát 4 Họ Kiến trúc trên `Stratified Subset`, Huấn luyện Mô hình AI 1 (Ortho-OBB bắt vùng pin méo) & Chốt cứng API `spatial_grid_index`
* **1. Phải làm những gì:**
  * Tạo bộ Augmentation giả lập biến dạng đường ghép ảnh (`SeamlineShift` + `ElasticTransform`) và huấn luyện mô hình AI 1 nhận diện bản đồ Ortho chính của 4 trang trại.
  * Chạy khảo sát đối sánh 4 họ kiến trúc (`HBB`, `Oriented R-CNN`/`Rotated RetinaNet`, `RT-DETR`, `YOLO-OBB`) và đối chứng 2 chế độ khởi tạo (`Random Init` vs `Pretrained Backbone Init`) trên **Tập con đại diện phân tầng (`Stratified Subset` 25–30% dữ liệu cố định `seed=42`)**, sau đó dồn 100% tài nguyên GPU train full dataset cho kiến trúc chiến thắng (`YOLO-OBB`).
  * **Chốt cứng chữ ký hàm (API signature) của thư viện `spatial_grid_index`** (gồm cả hàm `get_block_string_boundary_landmarks` trả về tọa độ biên lối đi hai đầu dải bay hỗ trợ TV2 neo ảnh 31m) ngay cuối Tuần 2.
* **2. Dùng những bộ dữ liệu gì:**
  * Bộ ảnh cắt Ortho $1024 \times 1024$ sinh từ các file `.gpkg` và `.tif` của 4 trang trại đã chia tập `Train / Valid / Test` ở Đầu việc 1.3.
* **3. Cách thức làm:**
  * **Bước 1:** Áp dụng phép dịch trượt đường ghép mảnh (`SeamlineShift` lệch `5–15 pixel` ngang qua thân tấm pin) và biến dạng lưới đàn hồi (`ElasticTransform`) lên tập Train để dạy AI nhận ra vùng tấm pin bị méo vẫn là tấm pin.
  * **Bước 2:** Chạy bảng khảo sát chọn mô hình trên `Stratified Subset` và huấn luyện full dataset cho `YOLOv8s-OBB / YOLO11s-OBB`.
* **4. Khảo sát như thế nào (Vũ khí trả lời Hội đồng bảo vệ):**
  * Lập bảng số liệu gồm 6 cột trên cùng cấu hình GPU: `Mô hình & Chế độ khởi tạo`, `Tham số (M) & GFLOPs`, `VRAM tiêu thụ (GB)`, `Tốc độ suy luận (ms/ảnh)`, `mAP@50 toàn cục (%)`, và `Recall riêng trên tập các tấm pin bị méo (%)`.

#### Đầu việc 2.2 (Thành viên 2 – Module 2, Nhánh AI 2A): Huấn luyện Mô hình AI 2A (Nhận diện Tấm pin trên Ảnh lẻ RGB đã Khử méo `P=K`)
* **1. Phải làm những gì:**
  * Huấn luyện mới hoàn toàn mô hình AI 2A nhận diện tấm pin trên ảnh lẻ RGB (`_W.JPG`) để định vị chính xác từng tấm pin trên khung hình chụp tầm thấp (`31m`, `35m`, `42m`).
* **2. Dùng những bộ dữ liệu gì:**
  * Bộ dữ liệu ảnh lẻ RGB đã khử méo `DewarpData` (`cv2.undistortPoints(..., P=K)`) và chia theo dải không gian cách ly `15m` ở Đầu việc 1.4 từ [SolarGIS\_Dataset\_1](https://www.google.com/search?q=https://github.com/strawberrymilktea0604/SolarGIS_Dataset_1), [**Roboflow solar-segment-obb**](https://universe.roboflow.com/qu-nguyn-nh-s-workspace/solar-segment-obb) và [1. Khảo sát điện mặt trời Ninh Thuận -4/2026](https://www.google.com/search?q=https://drive.google.com/drive/folders/1pNG8IsaklZ65U-JpmXnPZmDTCVDmwlu9).
* **3. Cách thức làm:**
  * Khảo sát nhanh các biến thể kích thước mạng (`Nano`, `Small`, `Medium`) và đối chứng `Random Init` vs `Pretrained Backbone Init` trên `Stratified Subset`, sau đó huấn luyện full dataset ở kích thước $1024 \times 1024$ với hàm mất mát `ProbIoU Loss`.
* **4. Khảo sát như thế nào:**
  * Lập bảng so sánh `Precision`, `Recall`, `mAP@50`, `mAP@50:95`, mức ngốn VRAM (GB) và tốc độ suy luận (ms/ảnh) giữa các kiến trúc ở cả 3 tầng độ cao `31m`, `35m`, `42m`.

#### Đầu việc 2.3 (Thành viên 2 – Module 2, Nhánh AI 2B): Huấn luyện Mô hình AI 2B (Phát hiện 4 Lớp Lỗi Nhiệt trên Ảnh Nhiệt)
* **1. Phải làm những gì:**
  * Huấn luyện mới hoàn toàn mô hình AI 2B nhận diện khung xoay OBB cấp tấm pin cho 4 loại lỗi nhiệt (`0: SingleHotSpot`, `1: MultiHotSpot`, `2: Bypass`, `3: ModuleOpenCircuit`) trên ảnh nhiệt `_T.JPG`.
* **2. Dùng những bộ dữ liệu gì:**
  * Bộ dữ liệu ảnh nhiệt và nhãn 4 lớp đã chia theo dải cách ly `15m` ở Đầu việc 1.5 từ [**Dataset SolarGIS - Thermal**](https://drive.google.com/drive/folders/13FbPVPVISPv3EP0hrTF-lqKFfJ2dJ8zl) và [SolarGIS\_Dataset\_2](https://www.google.com/search?q=https://github.com/strawberrymilktea0604/SolarGIS_Dataset_2).
* **3. Cách thức làm:**
  * Áp dụng kỹ thuật nhân bản đối tượng xoay (`OBB Copy-Paste Augmentation`) và `Class-weighted Focal Loss` để tăng mẫu cho 2 lớp hiếm (`Bypass`, `ModuleOpenCircuit`); huấn luyện ở kích thước $640 \times 640$ và đối chứng rõ vì sao việc khởi tạo từ Backbone gốc kết hợp Augmentation giúp tránh overfitting ở lớp ít mẫu tốt hơn khởi tạo ngẫu nhiên thuần túy.
* **4. Khảo sát như thế nào:**
  * Xuất Ma trận nhầm lẫn (`Confusion Matrix`), đường cong `PR-Curve` và bảng `Precision / Recall / F1-score / mAP@50` cho từng lớp trong 4 lớp lỗi nhiệt ở 3 độ cao `31M`, `35M`, `42M`.

#### Đầu việc 2.4 (Thành viên 3 – Module 3): Hoàn thành Bước 4, 5 PTTKHT & Dựng Khung Backend 100% RUST `Axum` + Frontend `React / TypeScript + MapLibre GL JS (WebGL)` (Thống nhất Khóa Nguyên `mvt_id`)
* **1. Phải làm những gì:**
  * Tổng hợp các sơ đồ Sequence/Activity của TV1, TV2 vào bộ bản vẽ PTTKHT hoàn chỉnh (Bước 4 & Bước 5) và dựng xong Backend **100% Rust (`Axum` + `Tokio` + `SQLx` + `PostGIS ST_AsMVT`)** kết nối với tầng Frontend bản đồ **`React / TypeScript (Next.js) + MapLibre GL JS (WebGL)`** ngay từ đầu Tuần 2 để báo cáo Mốc M1.
* **2. Dùng những bộ dữ liệu gì:**
  * CSDL PostGIS 7 bảng (Đầu việc 1.6) và gói `PMTiles` / cây thư mục `XYZ WebP Raster Tiles` của nhà máy Thuận Nam 19 do TV1 xuất sớm từ ngày thứ 3 của Tuần 1.
* **3. Cách thức làm:**
  * **Bước 1 (Backend 100% Rust):** Khởi tạo `crates/solar_shared` và `crates/solar_backend` bằng **Rust (`Axum` + `Tokio` + `SQLx`)**, mở API `/api/tiles/{plant_id}/{z}/{x}/{y}.mvt` gọi trực tiếp câu lệnh SQL `ST_AsMVT(..., 'mvt_id')` của PostGIS và phục vụ `PMTiles / XYZ WebP Raster Tiles (.webp)`.
  * **Bước 2 (Chốt Frontend `React / TypeScript + MapLibre GL JS` & Thống nhất khóa nguyên `mvt_id`):**
    * Chốt luôn kiến trúc Frontend `React / TypeScript + MapLibre GL JS` nối vào Backend 100% Rust `Axum` ngay từ đầu Tuần 2 (không mất thời gian bọc DOM MapLibre trong `wasm-bindgen`).
    * Khi khai báo Vector Tile Source trong MapLibre GL JS, **không đặt `promoteId: "module_id"`**; sử dụng trực tiếp top-level Feature ID số nguyên dương `mvt_id` do PostGIS `ST_AsMVT(..., 'mvt_id')` sinh ra để gọi `map.setFeatureState({ source: 'solar_modules', sourceLayer: 'solar_modules_layer', id: mvt_id }, ...)` nhanh và ổn định tuyệt đối. Khi người dùng click vào đa giác, đọc `e.features[0].id` (hoặc `e.features[0].properties.mvt_id_prop`) và `e.features[0].properties.module_id`.
* **4. Khảo sát như thế nào:**
  * Đo kiểm hiệu năng thực tế của Backend Rust `Axum` + `ST_AsMVT` khi chịu tải `100–500 requests/giây`: ghi nhận thời gian phản hồi trung bình (`< 10 ms`) và mức tiêu thụ RAM của tiến trình Rust (`< 50 MB`).

---

## PHẦN II: CHI TIẾT TỪNG ĐẦU VIỆC GIAI ĐOẠN 2 (TUẦN 3 – TUẦN 6: `30/11/2026` – `27/12/2026`)
*(Mục tiêu kết thúc Giai đoạn 2: Nối thông sớm luồng tích hợp ngay từ cuối Tuần 3, hoàn thiện thư viện không gian `spatial_grid_index`, thuật toán ánh xạ `module_id` có nội suy song phương hai đầu dải bay + khử trùng lặp đa góc nhìn và nghiệm thu **Mốc giữa kỳ M2 – 30% điểm**).*

### TUẦN 3 (`30/11/2026` – `06/12/2026`): Xây dựng Thư viện Không gian `spatial_grid_index` (Kèm Hàm Điểm Neo Hai Đầu Dải bay), Ghép cặp RGB–Nhiệt Đa Độ cao & Tích hợp Sớm Khung Mock End-to-End (TV1 & TV3 Phụ giúp Docker cho TV2)

#### Đầu việc 3.1 (Thành viên 1 – Module 1): Quét Suy luận Bản đồ Ortho & Xây dựng Thư viện Chỉ mục Không gian Dùng chung (`spatial_grid_index` — San tải Đường găng cho TV2)
* **1. Phải làm những gì:**
  * Viết luồng suy luận cửa sổ trượt $1024 \times 1024$ + `Rotational NMS` cho mô hình AI 1 trên ảnh Ortho của 4 trang trại.
  * Xây dựng gói thư viện Python dùng chung tên là **`spatial_grid_index`** chứa cây chỉ mục **R-Tree (`rtree` / `STRtree`)** và **KD-Tree (`scipy.spatial.cKDTree`)** quản lý toàn bộ lưới `.gpkg` của 4 nhà máy, cung cấp sẵn 2 hàm cốt lõi để san tải cho TV2:
    1. `get_candidates_in_radius(plant_code, x_utm, y_utm, radius_m=0.524)` phục vụ ghép cặp Hungarian.
    2. `get_block_string_boundary_landmarks(plant_code, bbox_utm)` trích xuất chính xác tọa độ các góc giàn pin (Table Corners) và đường biên lối đi nội bộ ở hai đầu dải bay để TV2 neo cứng 2 đầu dải ảnh `31m`.
* **2. Dùng những bộ dữ liệu gì:**
  * Trọng số AI 1 (từ Đầu việc 2.1) và bộ file `.gpkg` + ảnh Ortho `.tif` của 4 trang trại trong [SolarGISExport](https://drive.google.com/drive/folders/1AZRTJ8_ywbQ5bM90SK7C_bmgeReL6B9n).
* **3. Cách thức làm:**
  * Nạp toàn bộ đa giác tấm pin và các góc biên giàn pin (Table Corners / Road Edges) của từng trang trại vào cấu trúc `STRtree` và `cKDTree` trong bộ nhớ; viết hàm tra cứu ứng viên lân cận trả về danh sách `module_id`, `mvt_id` và tọa độ 4 đỉnh chỉ trong vài micro-giây ($O(\log N)$).
* **4. Khảo sát như thế nào:**
  * Đo thời gian tra cứu ứng viên cho `5.000` hộp dự đoán bằng thư viện `spatial_grid_index` ($O(M \log N)$, mất `< 0,2 giây`) so với vòng lặp vét cạn $O(M \times N)$ (`> 45 giây`).

#### Đầu việc 3.2 (Thành viên 2 – Module 2): Thuật toán Ghép cặp Nội tại (Intra-pair RGB–Thermal Alignment) Độc lập theo Từng Độ cao (`31m`, `35m`, `42m`)
* **1. Phải làm những gì:**
  * Sau khi ảnh lẻ `_W.JPG` đã được khử méo ống kính bằng `DewarpData` (`P=K` ở Đầu việc 1.4), bạn xây dựng bộ ma trận đồng trục `Dual-sensor Homography` riêng biệt cho 3 độ cao bay (`31m`, `35m`, `42m`) để chiếu hộp lỗi nhiệt trên ảnh `_T.JPG` ($640 \times 512$) sang đúng tấm pin trên ảnh `_W.JPG` mà không bị lệch thị sai (parallax).
* **2. Dùng những bộ dữ liệu gì:**
  * Cặp ảnh đồng bộ `_W.JPG` và `_T.JPG` ở 3 độ cao `31m`, `35m`, `42m` trong [1. Khảo sát điện mặt trời Ninh Thuận -4/2026](https://www.google.com/search?q=https://drive.google.com/drive/folders/1pNG8IsaklZ65U-JpmXnPZmDTCVDmwlu9) cùng đầu ra của mô hình AI 2A và AI 2B.
* **3. Cách thức làm:**
  * Với mỗi tầng độ cao $h \in \{31\text{m}, 35\text{m}, 42\text{m}\}$, ước lượng ma trận $H_{\text{thermal}\rightarrow\text{rgb}}^{(h)}$ ($3 \times 3$) trên ảnh đã khử méo `DewarpData`; chiếu 4 đỉnh hộp lỗi nhiệt sang khung ảnh RGB, ghép với tấm pin có chỉ số `Skew-IoU` lớn nhất ($\ge 0,50$) và tính khoảng cách từ tâm tấm pin tới tâm quang học của ảnh (`dist_to_image_center_px`) phục vụ bước chọn ảnh nadir nhất ở Tuần 5.
* **4. Khảo sát như thế nào:**
  * Lập bảng so sánh sai số ghép cặp RGB–Nhiệt giữa **Dùng 1 ma trận cố định trên ảnh chưa khử méo** với **Khử méo `DewarpData` ($W/2, H/2, P=K$) + Ma trận hiệu chuẩn theo từng độ cao `31m, 35m, 42m`**.

#### Đầu việc 3.3 (Thành viên 3 & Thành viên 1 phụ giúp Docker cho TV2): Dựng Bản đồ WebGL 60 FPS, Đóng gói Docker `libdirp.so` + `Redis Worker` & Nối thông Khung Mock End-to-End ngay cuối Tuần 3
* **1. Phải làm những gì:**
  * Hoàn thiện hiển thị bản đồ 4 nhà máy bằng `MapLibre GL JS (WebGL)` đạt `60 FPS`.
  * **San tải cho TV2:** TV1 và TV3 phụ trách viết `Dockerfile` đóng gói `libdirp.so`, `libv_*.so`, `libv_list.ini` cùng khung `Redis Queue Worker` cơ sở để TV2 chỉ việc gắn hàm Python của mình vào.
  * **Đẩy sớm mốc tích hợp từ Tuần 6 lên ngay cuối Tuần 3:** Cả 3 thành viên cùng nối thông luồng `Frontend WebGL <-> Backend Rust Axum <-> Redis Queue <-> Python Worker <-> PostGIS (Trigger Sync)` bằng kịch bản chạy thử 10 cặp ảnh mẫu để kiểm tra khớp nối hệ tọa độ (`EPSG:32649` trong DB và `EPSG:3857` trên MVT Web) ngay từ bây giờ.
* **2. Dùng những bộ dữ liệu gì:**
  * CSDL PostGIS 7 bảng, luồng `ST_AsMVT`, gói `PMTiles` / XYZ WebP Tiles (`--xyz --exclude -z 15-21`) và lô 10 cặp ảnh mẫu của nhà máy Thuận Nam 19.
* **3. Cách thức làm:**
  * Khi bấm nút *"Chạy kiểm tra"* trên giao diện Web $\rightarrow$ Axum đẩy job vào Redis $\rightarrow$ Python Worker nhận job, ghi kết quả mẫu vào bảng `ai_raw_detections` và `module_inspection_logs` (Trigger kiểm tra `MAX(flight_date)` và tự động cập nhật `solar_modules.current_coa_class` lên `2` hoặc `3`) $\rightarrow$ Axum bắn sự kiện `SSE/WebSocket` kèm `mvt_id` báo cho trình duyệt gọi `setFeatureState` đổi màu tấm pin sang màu vàng/đỏ ngay lập tức.
* **4. Khảo sát như thế nào:**
  * Kiểm tra xác nhận 100% lớp ảnh nền XYZ WebP và lớp đa giác Vector Tiles `.mvt` chồng khít tuyệt đối (không bị lật ngược trục $Y$), khi F5 tải lại trang trạng thái lỗi vẫn giữ nguyên nhờ Trigger PostGIS, và đo độ trễ cập nhật trạng thái lên bản đồ Web (`< 100 ms`).

---

### TUẦN 4 (`07/12/2026` – `13/12/2026`): Nắn Lưới Tô-pô + Mạng Lò xo `Mass-Spring` (TV1), Phép chiếu `8-DoF DLT Homography` có Nội suy Song phương Hai đầu Dải bay (TV2) & Quản lý Đợt bay (TV3)

#### Đầu việc 4.1 (Thành viên 1 – Module 1): Xây dựng Thuật toán Nắn Lưới Tô-pô (`Topological Snapping`) & Mạng Lò xo Đàn hồi (`Elastic Mass-Spring` — San tải cho TV2)
* **1. Phải làm những gì:**
  * Để giảm tải toán học cho TV2, TV1 đảm nhận viết cả 2 thuật toán chuẩn hóa cấu trúc lưới trong thư viện `spatial_grid_index`:
    1. **Nắn chỉnh lưới tô-pô (`Topological KD-Tree Grid Snapping`):** Nắn các hộp tấm pin vùng méo trên bản đồ Ortho về đúng hàng/cột theo hệ trục nội tại PCA $(\vec{u}, \vec{v})$ đã khóa hướng theo tương quan từng hàng của từng String và điền khuyết vào bộ file `.gpkg` của cả 4 nhà máy.
    2. **Mạng lưới lò xo đàn hồi (`Elastic Mass-Spring Regularization`):** Hàm `mass_spring_refine()` làm mịn và khử biến dạng cục bộ cho một đám mây tâm các tấm pin sau khi chiếu xuống mặt phẳng UTM.
* **2. Dùng những bộ dữ liệu gì:**
  * Kết quả dự đoán của AI 1 từ Đầu việc 3.1 và bộ file `.gpkg` của 4 trang trại (`Thuận Nam 19`, `BIM 2`, `Thuận Nam Đức Long`, `Thiên Tân 1.2`).
* **3. Cách thức làm:**
  * Dùng cây KD-Tree trong `spatial_grid_index` nối mỗi tấm pin với các láng giềng dọc theo trục $\vec{u}$ (cùng hàng `Row_ID`) và trục $\vec{v}$ (cùng cột `ID_Pin`), giải hệ phương trình lò xo thưa bằng thuật toán lặp `Conjugate Gradient / L-BFGS` ($O(I \cdot M)$) để đưa các tấm pin bị méo về đúng vị trí nút lưới chuẩn và tự động cấp mã `module_id`.
* **4. Khảo sát như thế nào:**
  * Đo độ thẳng hàng (Collinearity RMS cm) và độ đồng đều khoảng cách giữa các tấm pin trên cả 4 trang trại trước và sau khi nắn lưới, đồng thời chứng minh độ phức tạp thời gian tuyến tính $O(I \cdot M)$.

#### Đầu việc 4.2 (Thành viên 2 – Module 2): Thuật toán Chiếu Tọa độ Không gian `8-DoF DLT Homography` (Quy trình 3 Bước: Neo Hai đầu Dải bay `Bidirectional Strip Anchoring` + Biến đổi `4-DoF/6-DoF` Liên khung + Chuẩn hóa Hartley)
* **1. Phải làm những gì:**
  * Chiếu tọa độ các tấm pin và lỗi nhiệt từ đợt bay tầm thấp (`31m`, `35m`, `42m`) xuống mặt phẳng UTM `EPSG:32649` mà không bị trượt 1 cột tuần hoàn ($\approx 1,13\text{ m}$) và **không bị suy biến trôi dạt tỷ lệ phối cảnh (`Perspective Scale Drift`)** khi đi qua 15–25 bức ảnh liên tiếp ở giữa khu giàn pin.
* **2. Dùng những bộ dữ liệu gì:**
  * Cặp ảnh bay tầm thấp trong [1. Khảo sát điện mặt trời Ninh Thuận -4/2026](https://www.google.com/search?q=https://drive.google.com/drive/folders/1pNG8IsaklZ65U-JpmXnPZmDTCVDmwlu9), các bản đồ vùng trong [SolarPanel\_ExportOrtho](https://www.google.com/search?q=https://drive.google.com/drive/folders/1r9IpvEDOiUttqkTFHFfX1D4kgsqZk2y0) và hàm `get_block_string_boundary_landmarks` trong thư viện `spatial_grid_index` của TV1.
* **3. Cách thức làm (Quy trình 3 bước chống trượt cột và chống trôi dạt tỷ lệ ở độ cao 31m):**
  * **Bước 1 (Khóa cứng Hai đầu Dải bay – `Bidirectional Boundary-Anchored Ends`):** Dùng tọa độ tâm chụp RTK (`gps_x_utm, gps_y_utm`), độ cao `recorded_agl_m` và góc quay `gimbal_yaw / gimbal_pitch` chiếu thô khung nhìn camera xuống `spatial_grid_index`. Với ảnh đầu dải bay ($t_{\text{start}}$) và ảnh cuối dải bay ($t_{\text{end}}$) nhìn thấy biên lối đi nội bộ / góc giàn ở hai phía (`get_block_string_boundary_landmarks`), khớp trực tiếp góc biên giàn pin / lối đi để khóa cứng chỉ số cột tuyệt đối ở cả hai đầu dải bay.
  * **Bước 2 (Nội suy Song phương Hai đầu Dải bay với Biến đổi `4-DoF Similarity / 6-DoF Affine` Liên khung – `Bidirectional Strip Interpolation`):** Vì mặt giàn pin là mặt phẳng nghiêng cố định và drone bay giữ độ cao ổn định trên từng dải (`strip_id`), giữa 2 ảnh `_W.JPG` liên tiếp ($t-1$ và $t$, chồng lấn 70–80%) **chỉ ước lượng phép biến đổi `4-DoF Similarity` (hoặc `6-DoF Affine`)** thay vì nhân chuỗi `8-DoF Homography` tự do (giúp khóa cứng tỷ lệ scale, không bao giờ bị phình to hay méo thang). Sau đó thực hiện nội suy song phương từ cả hai đầu $t_{\text{start}}$ và $t_{\text{end}}$ (với trọng số tỷ lệ nghịch khoảng cách tới từng đầu: $w_t = \frac{t_{\text{end}} - t}{t_{\text{end}} - t_{\text{start}}}$) kết hợp kẹp cứng tâm bức ảnh vào bán kính sai số RTK ($\pm 10\text{ cm}$) để gán chính xác số thứ tự cột cho từng bức ảnh nằm giữa giàn.
  * **Bước 3 (Giải `8-DoF DLT Homography` Cục bộ có Chuẩn hóa Hartley & Làm mịn `Mass-Spring`):** Khi đã biết chính xác mỗi tấm pin trong ảnh $t$ ứng với cột nào trong lưới `.gpkg`, áp dụng **Hartley Isotropic Scaling** đưa tọa độ các cặp điểm tương ứng (2D pixel $\leftrightarrow$ 2D UTM) về gốc $(0,0)$ khoảng cách trung bình $\sqrt{2}$ (giảm số điều kiện ma trận $\kappa(A)$ từ $1,90 \times 10^{17}$ xuống $\sim 1.496$), giải SVD + RANSAC tìm ma trận phối cảnh $H_t$ ($3 \times 3$) cục bộ, chiếu toàn bộ hộp tấm pin/lỗi nhiệt xuống hệ `EPSG:32649` rồi gọi hàm `mass_spring_refine()` của TV1.
* **4. Khảo sát như thế nào:**
  * Chạy kiểm định trên tập điểm kiểm tra độc lập (Independent Check Points) ở từng trang trại, lập bảng so sánh 5 phương pháp: `GPS/RTK thô` vs `6-DoF Affine` vs `8-DoF Homography nối chuỗi đơn hướng (Unidirectional 8-DoF Chaining)` vs `8-DoF Homography + Bidirectional Strip Anchoring (4-DoF/6-DoF)` vs `Bidirectional Strip Homography + Mass-Spring` theo 7 chỉ số sai số thống kê ($\text{RMSE}_X, \text{RMSE}_Y, \text{RMSE}_{2D}, \text{MAE}_{2D}, \text{Median}, \text{P95}, e_{\max}$ và $\text{Mean IoU}$).

#### Đầu việc 4.3 (Thành viên 3 – Module 3): Xây dựng API Quản lý Chiến dịch Bay (Đủ 4 Tham số Môi trường IEC 62446-3) & Luồng Upload Đa luồng trong Rust `Axum`
* **1. Phải làm những gì:**
  * Hoàn thiện chức năng tạo chiến dịch bay mới trên Web (nhập thông số bức xạ $G_{\text{POA}}$ `irradiance_wm2`, tốc độ gió `wind_speed_ms`, độ ẩm `relative_humidity_pct`, nhiệt độ phản xạ nền trời `reflected_temp_c`, hệ số phát xạ kính `emissivity` mặc định `0.85`, độ cao bay) và luồng tải lên hàng trăm cặp ảnh `_W.JPG` & `_T.JPG` đẩy vào hàng đợi `Redis` để chạy AI thật.
* **2. Dùng những bộ dữ liệu gì:**
  * Các lô ảnh khảo sát thực tế của 4 trang trại trong [1. Khảo sát điện mặt trời Ninh Thuận -4/2026](https://www.google.com/search?q=https://drive.google.com/drive/folders/1pNG8IsaklZ65U-JpmXnPZmDTCVDmwlu9).
* **3. Cách thức làm:**
  * Trong Backend Rust `Axum`, kiểm tra điều kiện môi trường: nếu $G_{\text{POA}} < 600\text{ W/m}^2$ thì tự động hiển thị cảnh báo *"Bức xạ dưới ngưỡng chuẩn IEC TS 62446-3 ($600\text{ W/m}^2$)"* trên giao diện; tự động đọc `DewarpFlag`, mã dải bay `strip_id` và thứ tự ảnh `strip_sequence_idx` lưu vào bảng `raw_image_pairs` và phát tiến độ xử lý qua `SSE/WebSocket`.
* **4. Khảo sát như thế nào:**
  * Đo tốc độ upload và trích xuất metadata bất đồng bộ bằng `Tokio` trong Rust cho lô `500` cặp ảnh.

---

### TUẦN 5 (`14/12/2026` – `20/12/2026`): Thuật toán Hungarian Gán mã `module_id`, Khử Trùng lặp Đa Góc nhìn (`Multi-View Deduplication`), Trigger An toàn Thời gian & Giao diện Lịch sử Đợt bay Không Bị "Bóng ma Trạng thái"

#### Đầu việc 5.1 (Thành viên 1 – Module 1): Tối ưu hóa Mô hình AI 1 sang `ONNX Runtime` & Đóng gói Pipeline Hoàn thiện `.gpkg` Tự động
* **1. Phải làm những gì:**
  * Xuất mô hình AI 1 sang chuẩn `.onnx` (FP16/FP32) và đóng gói luồng tự động: khi nạp bản đồ Ortho `.tif` và file `.gpkg` lên hệ thống, tự động phát hiện và điền khuyết toàn bộ vùng tấm pin bị méo, cập nhật vào bảng `solar_modules` của PostGIS.
* **2. Dùng những bộ dữ liệu gì:**
  * Trọng số AI 1 của TV1 cùng bộ file `.gpkg` và `.tif` của 4 trang trại.
* **3. Cách thức làm:**
  * Chuyển đổi `.pt` sang `.onnx`, tích hợp thẳng với thư viện `spatial_grid_index` để đánh dấu `is_distorted_recovered = TRUE` cho các tấm pin vùng méo được khôi phục.
* **4. Khảo sát như thế nào:**
  * Lập bảng so sánh tốc độ suy luận (FPS / ms) và mức chiếm dụng VRAM/RAM giữa PyTorch gốc và `ONNX Runtime`.

#### Đầu việc 5.2 (Thành viên 2 – Module 2): Thuật toán Ghép cặp Tối ưu Hungarian Hai Ngưỡng, Hợp nhất Khử Trùng lặp Đa Góc nhìn (`Multi-View Observation Aggregation`) & Đồng bộ An toàn Thời gian về `solar_modules`
* **1. Phải làm những gì:**
  * Gọi hàm `get_candidates_in_radius(plant_code, x, y, radius=0.524)` từ thư viện `spatial_grid_index` của TV1 để lấy danh sách ứng viên, giải thuật toán **Hungarian (Kuhn-Munkres)** hai ngưỡng để xác định từng lỗi nhiệt rơi vào mã `module_id` nào, **hợp nhất các phát hiện trùng lặp từ nhiều ảnh bay chồng lấn 70–80% trên cùng một `module_id`** và kích hoạt Trigger đồng bộ an toàn thời gian về bảng `solar_modules`.
* **2. Dùng những bộ dữ liệu gì:**
  * Tọa độ các tấm pin và lỗi nhiệt sau khi chiếu ở Đầu việc 4.2 cùng thư viện `spatial_grid_index` của TV1 trên dữ liệu 4 trang trại.
* **3. Cách thức làm:**
  * **Bước 1 (Hungarian Matching trên từng khung ảnh):** Lập ma trận chi phí $C_{ij} = \alpha(1 - \text{IoU}_{ij}) + (1 - \alpha)(d_{ij}/d_{\max})$ trên tập ứng viên lân cận do R-Tree/KD-Tree của TV1 trả về và giải bài toán phân công một-đối-một bằng `scipy.optimize.linear_sum_assignment`.
  * **Bước 2 (Dual-Threshold Gating):** Chỉ tự động chốt `module_id` (`qc_status = 'AUTO_VERIFIED'`) khi $\text{IoU} \ge 0,50$, $\Delta d < 52,4\text{ cm}$ và `Decision Margin` $\ge 0,15$; nếu biên quyết định $< 0,15$ thì gắn cờ `PENDING_QC`.
  * **Bước 3 (Hợp nhất Khử trùng lặp Đa góc nhìn & Trigger Kiểm tra `MAX(flight_date)`):** Gom nhóm toàn bộ các phát hiện trong cùng đợt bay theo bộ khóa `(campaign_id, module_id, fault_class)`:
    * Chọn bức ảnh có góc nhìn gần tâm quang học nhất (**nadir nhất** — tức có `MIN(dist_to_image_center_px)`) làm cặp ảnh minh chứng đại diện (`best_image_pair_id`, cắt `RGB Crop` & `Thermal Crop`).
    * Lấy giá trị `MAX(temp_delta_measured_c)` và đếm số lần quan sát `observation_count` để ghi 1 bản ghi duy nhất vào bảng `module_inspection_logs` (`ON CONFLICT (campaign_id, module_id, fault_class) DO UPDATE`, chỉ gán `iec_coa_class IN (2, 3)` kèm `om_priority`). Trigger `trg_sync_module_health_after_inspection` kiểm tra nếu `flight_date` của đợt bay bằng `MAX(flight_date)` của nhà máy thì tự động chọn lỗi có mức độ nghiêm trọng cao nhất cập nhật vào `solar_modules`.
* **4. Khảo sát như thế nào:**
  * Lập bảng so sánh giữa **Gán tham lam (Greedy Nearest Neighbor)** với **Thuật toán Hungarian Hai Ngưỡng + Multi-View Deduplication**: đo `Top-1 Module ID Accuracy (%)`, tỷ lệ nhảy nhầm sang tấm bên cạnh (`Aliasing Rate %`), và số lượng bản ghi trùng lặp được lọc bỏ nhờ `Multi-View Aggregation`.

#### Đầu việc 5.3 (Thành viên 3 – Module 3): Xây dựng Giao diện Chẩn đoán Chi tiết từng `module_id` & Chuyển đổi Lịch sử các Lần bay bằng `removeFeatureState` + Bộ lọc `['in', ['id'], ...]` (Không Bị "Bóng ma Trạng thái")
* **1. Phải làm những gì:**
  * Hoàn thiện bảng điều khiển (Inspector Drawer) trên giao diện Web: cho phép chọn 1 trong 4 trang trại, chuyển đổi xem lại bất kỳ đợt bay nào trong lịch sử mà không bị dính "bóng ma trạng thái" của đợt bay mới nhất, lọc tấm pin theo 4 loại lỗi nhiệt hoặc cấp độ `CoA 1 (Normal) / CoA 2 / CoA 3`, bấm vào từng tấm pin trên bản đồ để xem chi tiết.
* **2. Dùng những bộ dữ liệu gì:**
  * Dữ liệu thực tế từ 7 bảng PostGIS của cả 4 nhà máy.
* **3. Cách thức làm (Đã vá kín Bug "Bóng ma trạng thái" & Giới hạn `setFilter` theo [MapLibre Issue #6213](https://github.com/maplibre/maplibre-gl-js/issues/6213)):**
  * **Bước 1 (Chuyển đổi đợt bay lịch sử sạch 100%):** Khi người dùng chọn xem một `campaign_id` cũ trong lịch sử (`isHistoricalView = true`), giao diện thực hiện đúng 3 bước:
    1. Gọi [map.removeFeatureState](https://maplibre.org/maplibre-gl-js/docs/API/classes/Map/) `({ source: 'solar_modules', sourceLayer: 'solar_modules_layer' })` để xóa sạch mọi trạng thái cũ.
    2. Gọi API `GET /api/campaigns/{campaign_id}/fault_states` lấy gói JSON siêu nhẹ (`~20 KB`) chỉ gồm `{ mvt_id, fault_class, iec_coa_class, om_priority }` của các tấm bị lỗi trong đợt bay đó và áp `map.setFeatureState` hàng loạt.
    3. Cập nhật biểu thức `fill-color` sang `["coalesce", ["feature-state", "coa_class"], 1]` (để các tấm pin khỏe mạnh ở đợt bay cũ mặc định nhận giá trị `1 = CoA 1 Normal` thay vì đọc cột `["get", "current_coa_class"]` của đợt bay mới nhất).
  * **Bước 2 (Bộ lọc lỗi tương thích kiến trúc MapLibre):** Khi người dùng chọn bộ lọc *"Chỉ hiện tấm pin lỗi CoA 3 / Loại lỗi X"*, không dùng `["feature-state", ...]` trong `setFilter`, mà lấy danh sách `faultMvtIds` từ mảng JSON trong bộ nhớ và gọi `map.setFilter('solar-modules-fill', ['in', ['id'], ['literal', faultMvtIds]])` (hoặc đặt `fill-opacity: 0` trong `paint` cho các tấm có `coa_class == 1`).
* **4. Khảo sát như thế nào:**
  * Đo độ trễ phản hồi giao diện (`< 16 ms`) và kiểm chứng thực nghiệm: tấm pin bị lỗi ở đợt bay tháng 10 nhưng khỏe mạnh ở đợt bay tháng 4 khi chuyển về tháng 4 sẽ hiển thị màu xanh bình thường (`CoA 1`) 100%, không bao giờ bị tô đỏ nhầm.

---

### TUẦN 6 (`21/12/2026` – `27/12/2026`): Kiểm nghiệm Chéo Đa Độ cao ($5 \times 5\text{ px/cell}$ Phụ lục A.1 IEC 62446-3) / Đa Trang trại, Xuất Báo cáo PDF bằng `Typst` (`spawn_blocking`) & Báo cáo Giữa kỳ Mốc M2 (30%)

#### Đầu việc 6.1 (Cả nhóm): Chạy Thực nghiệm Toàn trình trên Cả 4 Trang trại & Nghiệm thu Mốc Giữa kỳ M2 (30% điểm)
* **1. Phải làm những gì:**
  * Vì khung tích hợp đã được nối thông từ cuối Tuần 3, ở Tuần 6 cả nhóm tập trung chạy toàn bộ dữ liệu thật của cả 4 trang trại qua hệ thống để lấy số liệu hoàn chỉnh và trình diễn tại buổi chấm giữa kỳ (**Mốc M2 – 30% điểm**).
* **2. Dùng những bộ dữ liệu gì:**
  * Toàn bộ bộ file `.gpkg`, ảnh Ortho `.tif` và cặp ảnh lẻ `_W.JPG` & `_T.JPG` của 4 trang trại (`Thuận Nam 19`, `BIM 2`, `Thuận Nam Đức Long`, `Thiên Tân 1.2`).
* **3. Cách thức làm:**
  * Chạy trọn vẹn Pipeline 1 và Pipeline 2 cho cả 4 nhà máy, nạp đầy đủ vào PostGIS và kiểm tra trực tiếp trên giao diện Web Quản trị Bản sao số.
* **4. Khảo sát như thế nào:**
  * Đo tổng thời gian xử lý toàn trình (End-to-End Throughput) cho từng đợt bay và xuất bộ bảng tổng hợp kết quả thực nghiệm giữa kỳ.

#### Đầu việc 6.2 (Thành viên 1 & Thành viên 2): Khảo sát Độ nhạy Đa Độ cao (`31m`, `35m`, `42m`, `87m` — Giải trình Ngưỡng $5 \times 5\text{ px/cell}$ Phụ lục A.1 IEC 62446-3) & Kiểm nghiệm Chéo Giữa 4 Nhà máy
* **1. Phải làm những gì:**
  * Thực hiện bài kiểm nghiệm chéo giữa các độ cao bay (Cross-Altitude) gắn liền với **phân tích quang học ngưỡng $5 \times 5\text{ pixels/cell}$ theo Phụ lục A.1 của [IEC TS 62446-3:2017](https://datatec.es/wp-content/uploads/2019/09/Normativa-IEC-TS-62446-3.pdf)**, và kiểm nghiệm chéo giữa các trang trại có camera khác nhau (`ZH20T`, `M2EA`, `Zenmuse P1`).
* **2. Dùng những bộ dữ liệu gì:**
  * Dữ liệu 4 tầng độ cao tại [ThuanNam19\_Export](https://www.google.com/search?q=https://drive.google.com/drive/folders/1nKL1GspOozQI_p4wT0ag-9gmeWVX7pD-) và dữ liệu của [BIM2\_Export](https://www.google.com/search?q=https://drive.google.com/drive/folders/1CDPEBNRe62Ww0FEpxhtZ5eI15oRB2Ynx), [ThuanNamDucLong\_Export](https://www.google.com/search?q=https://drive.google.com/drive/folders/1VOOgETSe7tz01MwSoQH8UEZUsJ4FYsZ4), [ThienTan\_Export](https://www.google.com/search?q=https://drive.google.com/drive/folders/15PpXKcDpTmQzyksb6AUqgixrLBb6Oy3O).
* **3. Cách thức làm:**
  * Tính toán và đối chiếu GSD nhiệt thực tế của Zenmuse H20T ($f = 13,5\text{ mm}, p = 12\ \mu\text{m}$): ở `31m` ($\text{GSD}_{\text{thermal}} \approx 2,75\text{ cm/px} \rightarrow 5,7 \times 5,7\text{ px/cell}$, đạt chuẩn cấp cell), ở `35m` ($\approx 3,11\text{ cm/px} \rightarrow 5,0 \times 5,0\text{ px/cell}$, chạm biên chuẩn), và ở `42m` ($\approx 3,73\text{ cm/px} \rightarrow 4,2 \times 4,2\text{ px/cell}$).
  * Đo mức suy giảm hiệu năng $\Delta\text{mAP}$ và mức suy giảm nhiệt độ cực đại $\Delta T_{\text{measured}}$ do hiệu ứng trung bình hóa diện tích điểm ảnh (*Spot-Size Effect*) ở `42m` so với `31m–35m`.
* **4. Khảo sát như thế nào:**
  * Lập bảng phân tích mối tương quan giữa độ cao bay, $\text{GSD}_{\text{thermal}}$ (cm/px), số pixel trên mỗi tế bào quang điện ($15,6\text{ cm}$), tốc độ bay khảo sát (ha/giờ) và độ chính xác chẩn đoán lỗi để chứng minh khuyến nghị bay ở **`31m – 35m`** là hoàn toàn có cơ sở vật lý quang học.

#### Đầu việc 6.3 (Thành viên 3 – Module 3): Hoàn thiện Giao diện Kiểm duyệt QC (`CLO2`) & Xuất Biên bản Bảo trì PDF Chuẩn IEC TS 62446-3 bằng `Typst` (`tokio::task::spawn_blocking`)
* **1. Phải làm những gì:**
  * Xây dựng màn hình duyệt nhanh trên Web cho các bản ghi `PENDING_QC` và chức năng xuất biên bản kiểm định nhiệt ra file PDF / Excel / GeoPackage theo mẫu báo cáo chuẩn IEC TS 62446-3.
* **2. Dùng những bộ dữ liệu gì:**
  * Bảng `module_inspection_logs`, `flight_campaigns` và `solar_modules` trong PostGIS.
* **3. Cách thức làm (Bọc `Typst` trong `tokio::task::spawn_blocking` trên Backend Rust):**
  * Vì trình biên dịch PDF của **`Typst`** (`typst` / `typst-as-lib`) là tác vụ tính toán đồng bộ nặng về CPU (CPU-bound), trong handler của Rust `Axum`, TV3 bọc lệnh kết xuất PDF bên trong **`tokio::task::spawn_blocking(move || render_iec_report_pdf(...))`** để không bao giờ làm nghẽn các luồng async đang phục vụ Vector Tiles `.mvt`.
  * Mẫu biên bản `.typ` in song song cả $\Delta T_{\text{measured}}$ (kèm phân hạng `CoA 2 / CoA 3` và độ ưu tiên O&M `LOW / MEDIUM / HIGH`) và $\Delta T_{\text{norm}}$ (quy về $1000\text{ W/m}^2$), thông số môi trường ($G_{\text{POA}}, \varepsilon = 0,85$, độ ẩm, nhiệt độ phản xạ), danh sách `module_id` bị lỗi và cặp ảnh RGB – Nhiệt minh chứng.
* **4. Khảo sát như thế nào:**
  * Đo thời gian kết xuất báo cáo PDF 50 trang bằng `Typst` trong `spawn_blocking` (`< 150 ms`) và thống kê tỷ lệ các ca cần con người kiểm duyệt (`< 1,5%`) làm minh chứng cho tiêu chí đạo đức và kiểm soát rủi ro AI của `CLO2`.

---

## PHẦN III: CHI TIẾT TỪNG ĐẦU VIỆC GIAI ĐOẠN 3 (TUẦN 7 – TUẦN 9: `28/12/2026` – `17/01/2027`)
*(Mục tiêu kết thúc Giai đoạn 3: Hoàn thành quyển Báo cáo ĐATN $\le 150$ trang, bộ Slide bảo vệ theo đúng rút kinh nghiệm đợt 25–26/06/2026 và nộp đúng hạn `17/01/2027` hướng tới **Mốc bảo vệ M3 – 50% điểm**).*

### TUẦN 7 (`28/12/2026` – `03/01/2027`): Chứng minh Độ phức tạp Thuật toán $O(\cdot)$, Đóng gói Docker & Viết Bản thảo Báo cáo ĐATN

#### Đầu việc 7.1 (Thành viên 1 – Module 1): Viết Chương 1 & Chương 3 – Phần 1 (Pipeline AI 1, Hệ trục Nội tại PCA Khóa Hướng Từng Hàng, Thư viện `spatial_grid_index` & Nắn lưới Đa Trang trại)
* **1. Phải làm những gì:** Viết hoàn chỉnh Chương 1 (Đặt vấn đề, Đầu vào – Đầu ra, phạm vi giải quyết trên 4 trang trại Ninh Thuận) và phần thuyết minh kỹ thuật của Module 1 (AI 1 bắt vùng pin méo, nội suy theo trục PCA $(\vec{u}, \vec{v})$ khóa hướng bằng hiệp phương sai từng hàng $\text{Cov}_r(u, \text{ID\_Pin}) > 0$, R-Tree/KD-Tree, hàm trích xuất điểm neo biên hai đầu dải bay `get_block_string_boundary_landmarks`, Topological Snapping, Mass-Spring và xuất XYZ WebP Tiles `--exclude -z 15-21` / `PMTiles`).
* **2. Dùng những bộ dữ liệu gì:** Toàn bộ kết quả thực nghiệm của TV1 từ Tuần 1 đến Tuần 6.
* **3. Cách thức làm & Khảo sát:** Lập bảng chứng minh độ phức tạp thuật toán tra cứu không gian giảm từ $O(M \times N)$ xuống $O((N+M) \log N)$ và giải hệ thưa mạng lò xo đạt $O(I \cdot M)$.

#### Đầu việc 7.2 (Thành viên 2 – Module 2): Viết Chương 3 – Phần 2 (Pipeline AI 2, Giải mã Đủ 4 Trường `DJI SDK`, Chuẩn `CoA 1/2/3` & Ngưỡng $5 \times 5\text{ px/cell}$, Khử méo `DewarpData` `P=K`, Ánh xạ `Bidirectional Strip Homography + Hungarian` & `Multi-View Deduplication`)
* **1. Phải làm những gì:** Viết hoàn chỉnh phần thuyết minh kỹ thuật của Module 2 từ chia tập cách ly `15m`, giải mã nhiệt học Planck qua `DJI Thermal SDK` (đủ 4 tham số với `emissivity = 0.85`, kẹp trần `25.0m`, giải trình sự triệt tiêu bậc nhất của sai số phản xạ bầu trời quang `reflected_temp_c`, định nghĩa chuẩn `CoA 1 = Normal`, `CoA 2/3 = Abnormality` và ngưỡng GSD nhiệt $5 \times 5\text{ px/cell}$ theo Phụ lục A.1 IEC TS 62446-3), huấn luyện AI 2A & AI 2B, khử méo ống kính `DewarpData` (`cx_opencv = W/2 + cx_dewarp`, `cv2.undistortPoints(..., P=K)`), ghép cặp RGB–Nhiệt đa độ cao, phép chiếu `8-DoF DLT Homography` (neo hai đầu dải bay `Bidirectional Strip Anchoring` với `4-DoF/6-DoF` liên khung + chuẩn hóa Hartley), thuật toán `Hungarian Hai Ngưỡng` đến gom cụm khử trùng lặp đa góc nhìn.
* **2. Dùng những bộ dữ liệu gì:** Toàn bộ kết quả thực nghiệm của TV2 từ Tuần 1 đến Tuần 6.
* **3. Cách thức làm & Khảo sát:** Đưa vào báo cáo bảng phân tích độ phức tạp của thuật toán Hungarian phân rã theo chuỗi String $O(M \cdot \bar{m}^2)$ và bảng đối sánh sai số định vị 7 chỉ số thống kê.

#### Đầu việc 7.3 (Thành viên 3 – Module 3): Viết Chương 2 (6 Bước PTTKHT, ERD 7 Bảng + Trigger Kiểm tra `MAX(flight_date)`, `PostGIS ST_AsMVT` có `mvt_id_prop` & `margin`, `Typst PDF` & Kiến trúc Rust) + Đóng gói `docker-compose.yml`
* **1. Phải làm những gì:** Viết hoàn chỉnh Chương 2 (6 bước PTTKHT) và đóng gói toàn bộ hệ thống vào `docker-compose.yml` (đảm bảo copy đủ `libdirp.so`, `libv_*.so`, `libv_list.ini` vào container AI Worker) để bật lên chạy ngay bằng 1 lệnh.
* **2. Dùng những bộ dữ liệu gì:** Toàn bộ bản vẽ UML, ERD 7 bảng và số liệu hiệu năng của TV3 từ Tuần 1 đến Tuần 6.
* **3. Cách thức làm & Khảo sát:** Giải trình chi tiết luồng dữ liệu AI đi qua 7 bảng PostGIS (kèm Trigger kiểm tra `MAX(flight_date)` và cơ chế `removeFeatureState` + lọc `['in', ['id'], ...]` khi xem lịch sử đợt bay) và bảng đối sánh hiệu năng của kiến trúc Rust (`Axum` + `ST_AsMVT` + `Typst PDF` + `MapLibre WebGL`).

---

### TUẦN 8 (`04/01/2027` – `10/01/2027`): Hợp nhất Quyển Báo cáo ĐATN ($\le 150$ trang), Đối chiếu CLO & Trình GVHD Duyệt

#### Đầu việc 8.1 (Cả nhóm): Hợp nhất Chương 4 (Thực nghiệm & Thảo luận), Kết luận – Hướng mở & Chuẩn hóa Thể thức HUCE
* **1. Phải làm những gì:** Ghép các chương của 3 thành viên thành quyển báo cáo hoàn chỉnh ($\le 150$ trang nội dung chính theo Điều 8 Quy định `483/QĐ-ĐHXDHN`), kiểm tra đối chiếu toàn bộ `CLO1`–`CLO5` và nộp bản thảo cho Giảng viên hướng dẫn duyệt.
* **2. Cách thức làm:** Đưa đầy đủ bảng khảo sát chọn mô hình theo CPU/GPU/VRAM (đối chứng cả 2 chế độ khởi tạo), bảng độ phức tạp thuật toán, bảng kiểm nghiệm trên 4 trang trại và bảng sai số ánh xạ vào Chương 4; lập bảng phân định rõ đóng góp cá nhân của từng thành viên (`33% – 33% – 34%`).

#### Đầu việc 8.2 (Cả nhóm): Luyện tập Bộ Câu hỏi & Câu trả lời Phản biện Cá nhân trước Hội đồng
* **1. Phải làm những gì:** Tập dượt trả lời ngắn gọn, đúng trọng tâm cho từng thành viên theo sát kinh nghiệm bảo vệ đợt 25–26/06/2026:
  * *TV1:* Lý giải chọn `YOLO-OBB` dựa trên VRAM và mật độ `200–300 tấm pin/ảnh`; vì sao các mô hình cũ (`HBB`, `Oriented R-CNN`, `Mask R-CNN`, `DETR`) không phù hợp; cách khai thác bộ `.gpkg` của 4 trang trại bằng hệ trục nội tại PCA $(\vec{u}, \vec{v})$ khóa hướng theo tương quan từng hàng $\text{Cov}_r(u, \text{ID\_Pin}) > 0$ để dạy AI bắt vùng pin bị méo và độ phức tạp $O((N+M)\log N)$ của thư viện `spatial_grid_index`.
  * *TV2:* Giải thích sự khác biệt giữa `Random Init` và `Pretrained Backbone Init` trên tập dữ liệu tự xây dựng; lý giải đủ 4 tham số của `DJI Thermal SDK` (`emissivity = 0.85` mặt kính trước, `sdk_distance <= 25.0m`, `humidity`, `reflection`), sự triệt tiêu bậc nhất của sai số phản xạ nền trời quang, định nghĩa chuẩn `CoA 1 = Normal`, `CoA 2/3 = Abnormality` và ngưỡng GSD nhiệt $5 \times 5\text{ px/cell}$ ($2,75\text{ cm/px}$ ở `31m` vs *Spot-Size Effect* ở `42m`) theo Phụ lục A.1 IEC TS 62446-3; cách chuyển đổi gốc tâm ảnh $(W/2, H/2)$ kèm tham số `P=K` trong `cv2.undistortPoints`; cách kết hợp neo hai đầu dải bay (`Bidirectional Strip Anchoring` với `4-DoF/6-DoF` liên khung) chống trượt cột và chống trôi dạt tỷ lệ ở độ cao 31m khi giải `DLT Homography (Hartley) + Hungarian` và khử trùng lặp đa góc nhìn (`Multi-View Deduplication`).
  * *TV3:* Trình bày 6 bước PTTKHT; chỉ rõ trên sơ đồ ERD dữ liệu AI chạy qua 7 bảng nào trong PostGIS và cơ chế Trigger kiểm tra `MAX(flight_date)` đồng bộ ngược về `solar_modules`; giải thích cách hàm `ST_AsMVT(..., 'mvt_id')` (kèm `mvt_id_prop` và `margin => 64.0/4096.0`), khóa nguyên `mvt_id`, lệnh `removeFeatureState` và bộ lọc `['in', ['id'], ...]` giúp bản đồ WebGL đạt `60 FPS` mà không bị lỗi "bóng ma trạng thái", cùng cơ chế xuất báo cáo PDF tiếng Việt bằng `Typst` trong `spawn_blocking`.

---

### TUẦN 9 (`11/01/2027` – `17/01/2027`): Thiết kế Slide Bảo vệ Chuẩn Cấu trúc Mới & Nộp Báo cáo Chính thức (`17/01/2027`)

#### Đầu việc 9.1 (Từ 11/01 đến 14/01/2027): Thiết kế Bộ Slide Bảo vệ tách bạch nghiêm ngặt "Đầu vào / Đầu ra" và "Thực thi"
* **Slide phần Mở đầu:** Chỉ trình bày Bài toán thực tế trên 4 nhà máy Ninh Thuận, **Đầu vào** và **Đầu ra** (tuyệt đối không viết tên bất kỳ thuật toán hay mô hình nào ở các slide mở đầu).
* **Slide phần Thiết kế (PTTKHT):** Use Case, Kiến trúc Hệ thống Rust + PostGIS, ERD 7 bảng (kèm Trigger kiểm tra `MAX(flight_date)`) và luồng luân chuyển dữ liệu AI qua các bảng CSDL.
* **Slide phần Thực thi (Triển khai):** Trình bày chi tiết Pipeline AI 1 (bắt vùng pin méo từ `.gpkg` 4 nhà máy bằng trục PCA khóa hướng từng hàng + `spatial_grid_index`), Pipeline AI 2 (`DJI Thermal SDK` 4 tham số $\varepsilon = 0,85$ + `CoA 1/2/3` + ngưỡng $5 \times 5\text{ px/cell}$ + `DewarpData P=K` + `Bidirectional Strip Homography` + `Hungarian` + `Multi-View Deduplication`), **Bảng khảo sát chọn mô hình theo CPU/GPU/VRAM** và **Bảng đánh giá Độ phức tạp thuật toán** $O(\cdot)$.
* **Slide phần Thực nghiệm & Demo:** Bảng số liệu tổng hợp trên 4 nhà máy và Demo trực tiếp Web Quản trị Bản sao số (kèm video quay màn hình dự phòng).

#### Đầu việc 9.2 (Từ 15/01 đến 17/01/2027): Hoàn thiện Hồ sơ & Nộp Quyển Báo cáo ĐATN + Mã nguồn đúng hạn `17/01/2027`
* Xuất file PDF báo cáo chính thức, đóng gói mã nguồn 3 Module + bộ trọng số (`.pt`, `.onnx`) + bộ file `.gpkg` đã hoàn thiện vùng méo của 4 nhà máy và nộp đúng hạn ngày **`17/01/2027`** theo đúng quy tắc đặt tên file `[Đợt]_[Khoa/Nhóm]_[Ngành]_[MãSV]_[HọTên]_[LoạiTàiLiệu]_[YYYYMMDD]_v1`.