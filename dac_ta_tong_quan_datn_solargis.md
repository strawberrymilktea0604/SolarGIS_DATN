# ĐẶC TẢ TỔNG QUAN ĐỀ TÀI ĐỒ ÁN TỐT NGHIỆP (ĐATN) — BẢN HOÀN THIỆN V6 (FINAL RELEASE CANDIDATE)
## HỆ THỐNG BẢN SAO SỐ (DIGITAL TWIN) VÀ TRÍ TUỆ NHÂN TẠO ĐA LUỒNG TRONG GIÁM SÁT, ĐỊNH VỊ KHUYẾT TẬT NHÀ MÁY ĐIỆN MẶT TRỜI TỪ DỮ LIỆU UAV

- **Trường:** Trường Đại học Xây dựng Hà Nội (HUCE)
- **Khoa / Bộ môn:** Khoa Công nghệ Thông tin – Bộ môn Khoa học Máy tính
- **Học phần:** Đồ án tốt nghiệp Khoa học Máy tính (Mã học phần: `7724162` – `14` tín chỉ)
- **Quy mô nhóm:** `03` sinh viên (Phân bổ tải trọng cân bằng `33% – 33% – 34%`, mỗi sinh viên phụ trách độc lập `01` Module cốt lõi theo Điều 7 – Quyết định số `483/QĐ-ĐHXDHN` ngày `20/03/2026`)
- **Thời gian thực hiện kế hoạch:** `16/11/2026` – `17/01/2027` (`09` tuần làm việc tập trung đến hạn nộp báo cáo tổng kết)

---

## 1. TỔNG QUAN ĐỀ TÀI, CÁC NGUYÊN TẮC CỐT LÕI & BÀI TOÁN THỰC TẾ (ĐẦU VÀO – XỬ LÝ – ĐẦU RA)

### 1.1. Bối cảnh thực tế và 05 Nguyên tắc kỹ thuật cốt lõi đã chuẩn hóa của Đồ án
Các nhà máy điện mặt trời quy mô công nghiệp tại Ninh Thuận gồm **04 trang trại khảo sát thực tế** trong đợt [1. Khảo sát điện mặt trời Ninh Thuận - 4/2026](https://www.google.com/search?q=https://drive.google.com/drive/folders/1pNG8IsaklZ65U-JpmXnPZmDTCVDmwlu9):
1. **[Nhà máy Thuận Nam 19](https://www.google.com/search?q=https://drive.google.com/drive/folders/1WPPAEHEcZEhZ1ULd4_TZQ1ATtIHrIgS3)** (Khu vực khảo sát có **36.544 tấm pin** chia thành `6` Block, `148` chuỗi String trong tệp [thuannam19_master.gpkg](https://drive.google.com/file/d/1ytHofNRDcg9pFgoFGIhPRunAOChdTycN/view?usp=drivesdk), chụp bằng UAV gắn cảm biến kép `DJI Zenmuse H20T`).
2. **[Nhà máy BIM 2](https://www.google.com/search?q=https://drive.google.com/drive/folders/1oXIHbyJ_v_xHeJkR81LJpibSoQRzs9Pa)** (Chụp bằng `DJI Mavic 2 Enterprise Advanced` & `Zenmuse P1`, bản đồ trực giao [SonarPanelOrthoGeoTIFF.tif](https://drive.google.com/file/d/19k_ia4llf9KCkB4fFUKR3GyV2AQadmxu/view?usp=drivesdk) trong [1. Nhà máy BIM 2 - 10.4](https://www.google.com/search?q=https://drive.google.com/drive/folders/1WTOCRZBoMsuxe5vDS0Rzmpc8R9JJM73b)).
3. **[Nhà máy Thuận Nam Đức Long](https://www.google.com/search?q=https://drive.google.com/drive/folders/1xclyH3rnpCbCuroNabF8wbUbHAm_L3o6)** (Chụp bằng `DJI Zenmuse H20T`, bản đồ trực giao [SonarPanelOrthoGeoTIFF.tif](https://drive.google.com/file/d/1WrAFbh_WOvAMbpFP5e0eNgodggf2d1ZR/view?usp=drivesdk) trong [3. Nhà máy Thuận Nam Đức Long - 11.4](https://www.google.com/search?q=https://drive.google.com/drive/folders/1XW-7dqv9eY4zyisO54M3ynrzFFfTy3r3)).
4. **[Điện mặt trời Thiên Tân 1.2](https://www.google.com/search?q=https://drive.google.com/drive/folders/1DJdRk5LAD30srVknErJ57DWZuP5ebFPE)** (Chụp bằng `DJI Zenmuse H20T`, bản đồ trực giao [SonarPanelOrthoGeoTIFF.tif](https://drive.google.com/file/d/1fpnqBPQdIcpw2t9ZezBEkOzJlTu3e1hn/view?usp=drivesdk) và [Thien Tan 12.tif](https://drive.google.com/file/d/1BjYr4Y6dzG9JuYvb8vnt1Ep4IqQVR5gF/view?usp=drivesdk) trong [4. Điện mặt trời Thiên Tân 1.2](https://www.google.com/search?q=https://drive.google.com/drive/folders/1DZBOKkgHn8xfMliNeHWyKJgSSHCuktCW)).

**05 Nguyên tắc Kỹ thuật Cốt lõi (Đã hiệu chỉnh toàn diện theo tài liệu gốc của DJI, OpenCV, GDAL, PostGIS, MapLibre & chuẩn quốc tế IEC TS 62446-3:2017):**
1. **Huấn luyện mới hoàn toàn trên bộ dữ liệu tiền sơ khai (Không dùng lại `.pt`, `.csv` cũ và loại bỏ bộ `Báo cáo Fine-Tuning`):**
   - Toàn bộ các file trọng số `.pt` (`best.pt`, `fault_obb_4class.pt`) và các file `.csv` cũ vốn chỉ phục vụ viết bài báo công bố dữ liệu (Data Descriptor) được loại bỏ hoàn toàn; tuyệt đối không so sánh với `best.pt` cũ. Bộ `Fine-Tuning -> Solar_Model_Test` thuộc tập dữ liệu khác cũng được tách khỏi đồ án.
   - Để đáp ứng chặt chẽ yêu cầu của Hội đồng về **"Tự huấn luyện mô hình từ đầu (không gọi API ngoài) và có khảo sát trước khi chọn model"**, nhóm sử dụng tập con đại diện phân tầng (`Stratified Subset` 25–30% dữ liệu cố định `seed=42`) trong Tuần 2 để khảo sát nhanh 4 họ kiến trúc (`HBB`, `Oriented R-CNN`/`Rotated RetinaNet`, `RT-DETR`, `YOLO-OBB`), đồng thời đối chứng minh bạch cả **02 chế độ khởi tạo trên tập dữ liệu tự xây dựng**:
     - *Chế độ 1 (Khởi tạo ngẫu nhiên 100% – `weights=None` / Pure Scratch):* Huấn luyện với số vòng lặp lớn (`300 epochs`) kết hợp chiến lược `Cosine Annealing LR` + `Linear Warm-up` và `Mosaic/OBB Copy-Paste`.
     - *Chế độ 2 (Khởi tạo từ Backbone gốc công khai – `Pre-trained Backbone Initialization` từ ImageNet/DOTAv1 của nhà phát hành Ultralytics, không dùng bất kỳ trọng số `.pt` cũ nào của dự án):* Giúp hội tụ nhanh và tránh overfitting ở các lớp lỗi hiếm (`Bypass`, `ModuleOpenCircuit`).
2. **Khai thác trọn bộ các tệp `.gpkg` đã vẽ bằng QGIS của cả 4 Trang trại bằng Hệ trục Nội tại PCA Khóa Hướng theo Tương quan Từng Hàng & Xuất Bản đồ `gdal2tiles --xyz --exclude -z 15-21`:**
   - Cả 4 trang trại (`Thuận Nam 19`, `BIM 2`, `Thuận Nam Đức Long`, `Thiên Tân 1.2`) đều đã được kẻ lưới tấm pin chuẩn trên QGIS và xuất ra các tệp `.gpkg`, nhưng những vùng tấm pin bị méo nặng do đường ghép ảnh Ortho (seamline) đã bị bỏ trống.
   - Thuật toán `Grid Gap Interpolation` của Module 1 chiếu tọa độ tâm tấm pin lên **Hệ trục tọa độ nội tại của từng String (dùng PCA tìm vector chỉ phương $\vec{u}$ dọc dãy pin và vector pháp tuyến $\vec{v}$ vuông góc dãy pin)**. Để loại bỏ hoàn toàn độ bất định dấu $\pm 180^\circ$ của PCA và miễn nhiễm 100% với trường hợp String bị khuyết mất cột đầu/cuối hoặc đánh số zíc-zắc giữa các hàng `Row_ID` $\in \{1, 2, 3, 4\}$, thuật toán **tính hiệp phương sai dọc theo từng hàng `Row_ID` riêng biệt**:
     $$\text{Cov}_r(u, \text{ID\_Pin}) = \sum_{i \in \text{Row } r} (u_i - \bar{u}_r)(\text{ID\_Pin}_i - \overline{\text{ID\_Pin}}_r) > 0$$
     Nếu tổng hiệp phương sai âm thì đảo dấu $\vec{u} \leftarrow -\vec{u}$ (đồng thời tự động phát hiện nếu có hàng đánh số ngược chiều zíc-zắc) và cố định $\vec{v} = (-u_y, u_x)$ theo quy tắc bàn tay phải trước khi nội suy bước nhảy dọc hàng ($\Delta u \approx 1,13\text{ m}$) và vuông góc hàng ($\Delta v \approx 2,27\text{ m}$).
   - Khi xuất cây thư mục Raster Tiles từ ảnh Ortho `.tif` hàng GB bằng [gdal2tiles.py](https://opengxt.mangosystem.com/gdal/programs/gdal2tiles.html), bắt buộc truyền cờ **`--xyz --exclude -z 15-21 --tiledriver=WEBP --webp-quality=85`** (cờ `--exclude` bỏ qua toàn bộ các ô rỗng ở viền đen/trong suốt quanh nhà máy, và dừng ở mức zoom `21` tương ứng độ phân giải gốc $1\text{ cm/px}$ 1:1, tránh sinh hàng trăm nghìn file rỗng ở mức zoom 22).
3. **Chuẩn hóa Quốc tế IEC TS 62446-3:2017 (`CoA 1 = Normal`, `CoA 2/3 = Abnormality`, `emissivity = 0.85`, Ngưỡng $5 \times 5\text{ px/cell}$) & Giải mã Đủ 4 Trường Vật lý trong `DJI Thermal SDK (dirp)` (`sdk_distance <= 25.0m`):**
   - Định nghĩa rõ 4 lớp lỗi nhiệt (`0: SingleHotSpot`, `1: MultiHotSpot`, `2: Bypass`, `3: ModuleOpenCircuit`) là **nhãn hình thái nhiệt quan sát thị giác cấp tấm pin (Module-level visual thermal-pattern labels)** tham chiếu theo tiêu chuẩn [IEC TS 62446-3:2017](https://www.abovesurveying.com/blog/understanding-iec-62446-32017-outdoor-infrared-thermography) và [IEA PVPS Task 13](https://iea-pvps.org/wp-content/uploads/2020/01/Review_on_IR_and_EL_Imaging_for_PV_Field_Applications_by_Task_13.pdf) (yêu cầu bức xạ mặt phẳng giàn pin $G_{\text{POA}} \ge 600\text{ W/m}^2$).
   - **Giải trình vật lý quang học về độ phân giải $5 \times 5\text{ pixels/cell}$ theo Phụ lục A.1 của [IEC TS 62446-3:2017](https://datatec.es/wp-content/uploads/2019/09/Normativa-IEC-TS-62446-3.pdf) và [QopterVision Guide](https://qoptervision.at/en/ratgeber/thermography-report-iec-ts-62446-3-contents):** Kiểm định chi tiết cấp tế bào quang điện (cell-level, kích thước cell chuẩn $15,6 \times 15,6\text{ cm}$) yêu cầu tối thiểu $5 \times 5\text{ pixels/cell}$ (tức $\text{GSD}_{\text{thermal}} \le 3,0\text{ cm/px}$). Với cảm biến nhiệt Zenmuse H20T ($640 \times 512$, tiêu cự $f = 13,5\text{ mm}$, kích thước điểm ảnh $p = 12\ \mu\text{m}$):
     - Ở độ cao **`31m`**: $\text{GSD}_{\text{thermal}} = \frac{31 \times 12\ \mu\text{m}}{13,5\text{ mm}} \approx 2,75\text{ cm/px}$ ($\approx 5,7 \times 5,7\text{ px/cell}$ — **Đạt chuẩn kiểm định cấp cell**).
     - Ở độ cao **`35m`**: $\text{GSD}_{\text{thermal}} \approx 3,11\text{ cm/px}$ ($\approx 5,0 \times 5,0\text{ px/cell}$ — **Xấp xỉ biên chuẩn cấp cell**).
     - Ở độ cao **`42m`**: $\text{GSD}_{\text{thermal}} \approx 3,73\text{ cm/px}$ ($\approx 4,2 \times 4,2\text{ px/cell}$ — Đạt chuẩn kiểm định cấp tấm pin/chuỗi nhưng chịu **hiệu ứng trung bình hóa diện tích điểm ảnh – *Spot-Size Effect*** làm suy giảm nhẹ $\Delta T_{\text{measured}}$ của lỗi `SingleHotSpot`, qua đó chứng minh cơ sở khoa học vì sao đồ án khuyến nghị bay ở dải `31m–35m`).
   - **Định nghĩa chuẩn 3 Lớp Bất thường (`Classes of Abnormality - CoA`) theo [IEC 62446 Standards](https://solarthermography.com/blog/iec-62446-standards/):**
     - **`CoA 1` (Không có bất thường nhiệt – *No thermal abnormality / OK*):** Trạng thái mặc định của tấm pin khỏe mạnh (`solar_modules.current_coa_class DEFAULT 1`) — Không cần hành động bảo trì.
     - **`CoA 2` (Có bất thường nhiệt – *Thermal abnormality*):** Có điểm nóng hoặc chênh lệch nhiệt độ cần theo dõi và lên kế hoạch bảo trì trong thời gian hợp lý.
     - **`CoA 3` (Bất thường nhiệt ảnh hưởng an toàn – *Safety-relevant abnormality*):** Điểm nóng nghiêm trọng, quá nhiệt diode bypass hoặc hở mạch toàn module — Cần can thiệp/ngắt vận hành sớm.
     - Bảng `module_inspection_logs` chỉ ghi nhận các phát hiện lỗi thuộc **`iec_coa_class IN (2, 3)`** đi kèm thang độ ưu tiên O&M nội bộ **`om_priority IN ('LOW', 'MEDIUM', 'HIGH')`**, đồng thời lưu song song $\Delta T_{\text{norm}} = \Delta T_{\text{measured}} \times \left(\frac{1000}{G_{\text{POA}}}\right)^x$ ($x = 1,0$).
   - **Đặt đầy đủ 4 tham số trong `dirp_measurement_params_t` và đóng gói `libv_list.ini`:** Gọi `dirp_get_measurement_params` (theo [dirp_api.h](https://github.com/Mendru/DJI_thermal_SDK/blob/main/tsdk-core/api/dirp_api.h)) trước, sau đó cập nhật đủ 4 trường vật lý bắt buộc của `dirp_set_measurement_params`:
     1. `emissivity = 0.85` (hệ số phát xạ chuẩn của mặt kính cường lực phía trước ở góc chụp nadir theo [IEA PVPS Task 13](https://iea-pvps.org/wp-content/uploads/2020/01/Review_on_IR_and_EL_Imaging_for_PV_Field_Applications_by_Task_13.pdf) và [HIKMICRO PV Guide](https://www.hikmicrotech.com/it/explore/industrial-blog/Inspection_of_Photovoltaic_Panels_with_Thermal_Imaging_Camera/), thay vì `0.95` của tấm đáy polymer backsheet).
     2. `distance = min(recorded_agl_m, 25.0)` (kẹp trần ở `25.0m` theo giới hạn cứng `[1.0m – 25.0m]` của `tsdk-core/api/dirp_api.h`).
     3. `humidity = relative_humidity_pct` (mặc định `70.0%`).
     4. `reflection = reflected_temp_c` (giữ giá trị cấu hình hiện trường đọc từ `dirp_get_measurement_params` hoặc lấy từ bảng `flight_campaigns`). Khi thiếu phép đo tấm phản xạ nhôm nhăn ASTM E1862 tại hiện trường, sai số dịch chuyển hệ thống nhỏ lên $T_{\max}$ tuyệt đối bị **triệt tiêu bậc nhất** khi tính hiệu số vi sai $\Delta T_{\text{measured}} = T_{\max} - T_{\text{median\_string}}$ trên cùng mặt phẳng kính đồng nhất.
4. **Khử méo ống kính (`DewarpData` + `cv2.undistortPoints(..., P=K)`), Nội suy Song phương Hai đầu Dải bay (`Bidirectional Strip Anchoring` với `4-DoF/6-DoF` liên khung) & Hợp nhất Đa Góc nhìn (`Multi-View Deduplication`):**
   - **Khử méo ống kính và truyền `P=K` trong [cv2.undistortPoints](https://docs.pupil-labs.com/alpha-lab/undistort/):** Kiểm tra cờ `DewarpFlag` trong XMP; nếu `DewarpFlag == 0`, đọc `drone-dji:DewarpData`, chuyển đổi gốc tâm quang học sang góc trên bên trái của OpenCV (`cx_opencv = W / 2.0 + cx_dewarp`, `cy_opencv = H / 2.0 + cy_dewarp`), và **bắt buộc truyền `P=K`** (`cv2.undistortPoints(pts, K, distCoeffs, P=K)`) trước khi chia cho $(W, H)$ để chuẩn hóa về $[0, 1]$.
   - **Chống trượt cột tuần hoàn và chống trôi dạt tỷ lệ (`Perspective Scale Drift`) ở độ cao 31m bằng Nội suy Song phương Hai đầu Dải bay (`Bidirectional Strip Anchoring`):** Thay vì nhân chuỗi ma trận phối cảnh 8 bậc tự do qua 15–25 ảnh liên tiếp (dễ gây suy biến tỷ lệ phối cảnh ở giữa dãy), hệ thống:
     1. Dùng hàm `get_block_string_boundary_landmarks` (do TV1 cung cấp) để **neo cứng cả 2 đầu dải bay** ($t_{\text{start}}$ và $t_{\text{end}}$ nơi nhìn thấy biên lối đi nội bộ / góc giàn ở hai đầu).
     2. Giữa 2 khung hình liên tiếp $t-1$ và $t$ trên mặt phẳng giàn pin cố định, chỉ ước lượng phép biến đổi cứng **`4-DoF Similarity` (hoặc `6-DoF Affine`)** kết hợp nội suy song phương hai đầu dải bay và kẹp cứng tâm bức ảnh trong bán kính sai số RTK ($\pm 10\text{ cm}$) để xác định chính xác chỉ số cột, sau đó mới giải `8-DoF DLT Homography (Hartley)` cục bộ khớp vào lưới `.gpkg`.
   - **Hợp nhất quan sát trùng lặp đa góc nhìn (`Multi-View Observation Aggregation`) & Trigger đồng bộ an toàn thời gian (`MAX(flight_date)`):** Sau bước ghép cặp Hungarian, gom nhóm theo `UNIQUE(campaign_id, module_id, fault_class)`, chọn bức ảnh gần tâm quang học nhất (`MIN(dist_to_image_center_px)`) và giữ `MAX(temp_delta_measured_c)` ghi vào `module_inspection_logs`. Trigger PL/pgSQL trên PostGIS **chỉ cập nhật `solar_modules` khi đợt bay đó có `flight_date = MAX(flight_date)` của nhà máy** (chống lỗi ghi đè khi re-upload đợt bay cũ) và tự động chọn `fault_class` có mức độ nghiêm trọng cao nhất nếu 1 tấm pin mắc đồng thời nhiều lỗi.
5. **Viết mới hoàn toàn Module 3 với Backend RUST (`Axum` + `PostGIS ST_AsMVT` chuẩn khóa nguyên `mvt_id` + `Typst PDF` trong `spawn_blocking`) & Frontend `React / TypeScript + MapLibre GL JS (WebGL)` 60 FPS (Đã vá lỗi "Bóng ma trạng thái" & `setFilter`):**
   - Toàn bộ Backend được viết mới 100% bằng **Rust (`Axum` + `Tokio` + `SQLx`)**:
     - Sử dụng câu lệnh SQL [ST_AsMVT](https://postgis.net/docs/ST_AsMVT.html) truyền `'mvt_id'` làm tham số thứ 5 (`feature_id_name`) kèm `SELECT m.mvt_id, m.mvt_id AS mvt_id_prop, m.module_id, ...` và vùng đệm cắt ô [ST_TileEnvelope](https://postgis.net/docs/ST_TileEnvelope.html) `margin => (64.0 / 4096.0)`.
     - Chốt kiến trúc Frontend dùng **`React / TypeScript (Next.js) + MapLibre GL JS (WebGL)`** kết nối trực tiếp vào Backend 100% Rust `Axum` ngay từ đầu Tuần 2 (giải phóng TV3 khỏi việc gỡ lỗi vòng đời bộ nhớ DOM/JS trong `wasm-bindgen`).
     - **Cơ chế xóa "Bóng ma trạng thái" (`removeFeatureState`) và lọc mảng ID (`["in", ["id"], ...]`) trên MapLibre GL JS:** Khi người dùng chuyển sang xem một đợt bay cũ trong lịch sử (`isHistoricalView = true`), trình duyệt gọi [map.removeFeatureState](https://maplibre.org/maplibre-gl-js/docs/API/classes/Map/) `({ source: 'solar_modules', sourceLayer: 'solar_modules_layer' })` trước, nạp gói JSON lỗi siêu nhẹ (`~20 KB`) qua `setFeatureState`, đồng thời đổi biểu thức tô màu sang `["coalesce", ["feature-state", "coa_class"], 1]` (mặc định các tấm không nằm trong JSON lỗi của đợt bay cũ về `1 = Normal`, tuyệt đối không đọc lại `["get", "current_coa_class"]` của đợt bay mới nhất). Khi lọc chỉ hiển thị tấm pin lỗi ở đợt bay lịch sử, do [MapLibre Issue #6213](https://github.com/maplibre/maplibre-gl-js/issues/6213) không hỗ trợ `["feature-state", ...]` trong `setFilter`, giao diện dùng biểu thức `map.setFilter('solar-modules-fill', ['in', ['id'], ['literal', faultMvtIds]])` hoặc điều khiển `fill-opacity` trong `paint`.

---

### 1.2. Xác định rõ: ĐẦU VÀO $\rightarrow$ XỬ LÝ $\rightarrow$ ĐẦU RA
*(Lưu ý bắt buộc khi làm Slide bảo vệ: Slide phần Mở đầu chỉ trình bày **Đầu vào** và **Đầu ra** nghiệp vụ dưới đây, tuyệt đối **không** nêu tên thuật toán/mô hình. Các thuật toán chỉ được trình bày ở Slide phần Thực thi/Triển khai).*

#### A. ĐẦU VÀO (Inputs)
1. **Bản đồ trực giao tổng thể (Main Orthomosaic `.tif`) & Bộ tệp lưới chuẩn QGIS (`.gpkg`) của 4 Trang trại:**
   - Ảnh trực giao bay cao độ `85m–125m` (GSD $\approx 0,92–3,04\text{ cm/pixel}$, hệ quy chiếu `EPSG:32649`) tại [SolarGISExport](https://drive.google.com/drive/folders/1AZRTJ8_ywbQ5bM90SK7C_bmgeReL6B9n) và [SolarPanel\_ExportOrtho](https://www.google.com/search?q=https://drive.google.com/drive/folders/1r9IpvEDOiUttqkTFHFfX1D4kgsqZk2y0).
   - Bộ tệp `.gpkg` đã vẽ bằng QGIS của cả 4 nhà máy (tiêu biểu là [thuannam19_master.gpkg](https://drive.google.com/file/d/1ytHofNRDcg9pFgoFGIhPRunAOChdTycN/view?usp=drivesdk) gồm `36.544` tấm pin cùng các file `.gpkg` của `BIM 2`, `Thuận Nam Đức Long`, `Thiên Tân 1.2`), trong đó các tấm pin thẳng đã được đánh thứ tự `module_id` còn các vùng pin bị méo do ghép ảnh đang để trống.
2. **Cặp ảnh lẻ RGB (`_W.JPG`) và Ảnh nhiệt bức xạ 16-bit (`_T.JPG`) đồng bộ từ các đợt bay tầm thấp (`31m`, `35m`, `42m`):**
   - Cặp ảnh chụp đồng thời từ UAV trong [1. Khảo sát điện mặt trời Ninh Thuận - 4/2026](https://www.google.com/search?q=https://drive.google.com/drive/folders/1pNG8IsaklZ65U-JpmXnPZmDTCVDmwlu9), kèm dữ liệu nhãn gốc tại [SolarGIS\_Dataset\_1](https://www.google.com/search?q=https://github.com/strawberrymilktea0604/SolarGIS_Dataset_1), [Roboflow solar-segment-obb](https://universe.roboflow.com/qu-nguyn-nh-s-workspace/solar-segment-obb), [SolarGIS\_Dataset\_2](https://www.google.com/search?q=https://github.com/strawberrymilktea0604/SolarGIS_Dataset_2) và [Dataset SolarGIS - Thermal](https://drive.google.com/drive/folders/13FbPVPVISPv3EP0hrTF-lqKFfJ2dJ8zl) cùng thông số môi trường ($G_{\text{POA}} \ge 600\text{ W/m}^2$, tốc độ gió, độ ẩm tương đối, nhiệt độ phản xạ nền trời).

#### B. ĐẦU RA (Outputs)
1. **Bản đồ số Digital Twin hoàn chỉnh 100% vị trí tấm pin (Bao gồm cả vùng pin bị méo):**
   - Phát hiện đầy đủ các tấm pin trên bản đồ Ortho chính (lấp đầy cả các vùng tấm pin bị méo đường ghép mảnh mà bản vẽ QGIS bỏ trống), chuẩn hóa lưới và gán mã định danh duy nhất `module_id` theo đúng thứ tự `Plant -> Block -> String -> Row -> ID_Pin`.
2. **Báo cáo chẩn đoán khuyết tật nhiệt gắn chính xác vào từng mã `module_id` (Đã khử trùng lặp đa góc nhìn):**
   - Trả lời tự động và chính xác 3 câu hỏi nghiệp vụ cho mỗi chiến dịch bay:
     1. **Nhận diện các lỗi gì?** (`SingleHotSpot`, `MultiHotSpot`, `Bypass`, `ModuleOpenCircuit` kèm nhiệt độ giải mã qua SDK $T_{\max}, \Delta T_{\text{measured}}, \Delta T_{\text{norm}}$, phân hạng bất thường `CoA 2 / CoA 3` theo IEC TS 62446-3 và độ ưu tiên O&M `LOW / MEDIUM / HIGH`).
     2. **Rơi vào tấm pin nào trên ảnh chụp và trên bản đồ số?** (Tọa độ tâm $(X, Y)$ trên hệ `EPSG:32649`, sai số định vị $< 12\text{ cm}$).
     3. **Mã `module_id` của tấm pin đó là gì?** (Thuộc trang trại nào, `Block` nào, `String` nào, `Row` nào, thứ tự tấm `ID_Pin` số mấy, kèm cặp ảnh cắt RGB – Nhiệt gần tâm quang học nadir nhất).
3. **Phần mềm Web Quản trị Bản sao số Đa Trang trại (Rust Digital Twin Portal):**
   - Giao diện WebGIS 60 FPS quản lý tập trung cả 4 trang trại và nhiều lần bay khảo sát, lọc lỗi theo cấp độ CoA 1/2/3, kiểm duyệt QC các ca vùng biên và xuất biên bản bảo trì PDF chuẩn in ấn bằng `Typst`.

---

## 2. KIẾN TRÚC PHÂN CHIA 03 MODULE CÂN BẰNG TẢI TRỌNG (`33% – 33% – 34%`)

| Thành viên & Tỷ trọng | Tên Module Độc lập (Chấm điểm cá nhân) | Các hạng mục kỹ thuật phụ trách (Sau khi đã san tải đường găng) | Đầu ra bàn giao (Deliverables) |
| :--- | :--- | :--- | :--- |
| **Thành viên 1 (TV1)**<br>**Tải trọng: ~33%**<br>*(Trưởng nhóm – Module 1)* | **Module 1: Pipeline AI 1 Nhận diện Bản đồ Ortho chính (Bắt vùng pin méo), Quản trị Chỉ mục Lưới Không gian Đa Trang trại & Xuất Bản đồ XYZ WebP / PMTiles** | 1. **Khai thác bộ `.gpkg` 4 trang trại & Nội suy vùng pin méo bằng Hệ trục Nội tại PCA Khóa Hướng theo Từng Hàng (`Row-Wise Covariance`):** Quét toàn bộ các file `.gpkg` đã vẽ bằng QGIS của 4 nhà máy, chiếu lên trục nội tại $(\vec{u}, \vec{v})$ (khóa dấu bằng hiệp phương sai từng hàng $\sum_{i \in \text{Row}} (u_i - \bar{u})(\text{ID\_Pin}_i - \overline{\text{ID\_Pin}}) > 0$) để phát hiện lỗ khuyết ở vùng méo đường ghép ảnh và nội suy đa giác bù (`Grid Gap Interpolation`).<br>2. **Huấn luyện mô hình AI 1 (Ortho-OBB Detector):** Cắt ảnh Ortho $1024 \times 1024$, tạo Augmentation biến dạng đường ghép mảnh (`SeamlineShift` + `ElasticTransform`) và huấn luyện mới hoàn toàn mô hình AI 1.<br>3. **Thư viện Chỉ mục Không gian, Điểm neo Biên Hai Đầu Dải bay & Nắn lưới dùng chung (`spatial_grid_index`):** Xây dựng cây **R-Tree / KD-Tree**, hàm trích xuất tọa độ biên lối đi / góc giàn ở hai đầu dải bay (`get_block_string_boundary_landmarks` hỗ trợ TV2 neo 2 đầu dải ảnh 31m), thuật toán **Nắn lưới Tô-pô (`Topological Snapping`)**, thuật toán **Mạng lò xo đàn hồi (`Elastic Mass-Spring`)** và phụ giúp đóng gói Docker cho `libdirp.so` ở Tuần 3.<br>4. **Kịch bản Chuyển đổi Raster Tiles (`gdal2tiles.py --xyz --exclude -z 15-21 --tiledriver=WEBP` + đóng gói `PMTiles/MBTiles`):** Xuất trước nhà máy Thuận Nam 19 ngay ngày thứ 3 của Tuần 1 để TV3 dựng Web sớm, 3 nhà máy còn lại xuất chạy nền trong Tuần 2. | - Trọng số AI 1 (`.pt`, `.onnx`) + Bảng khảo sát chọn mô hình theo VRAM.<br>- Thư viện Python `spatial_grid_index` (KD-Tree, R-Tree, Boundary Landmarks, Topological Snapping, Mass-Spring) + Bộ file `.gpkg` hoàn chỉnh 100% vùng méo.<br>- Gói `PMTiles/MBTiles` & XYZ WebP Tiles (`--exclude -z 15-21`) của 4 nhà máy.<br>- Sơ đồ Sequence/Activity của Module 1 + Chương 1 & Chương 3 (Phần 1). |
| **Thành viên 2 (TV2)**<br>**Tải trọng: ~33%**<br>*(Phụ trách Module 2)* | **Module 2: Pipeline AI 2 Nhận diện Ảnh lẻ RGB + Phát hiện Lỗi Ảnh nhiệt (Chuẩn IEC 62446-3) & Ánh xạ Phối cảnh Gán mã `module_id`** | 1. **Chia tập Ảnh lẻ RGB & Ảnh nhiệt cách ly `15m` + Giải mã Đủ 4 Trường `DJI Thermal SDK`:** Chia tập dữ liệu tiền sơ khai theo dải không gian cách ly `15m`; bọc thư viện **DJI Thermal SDK (`dirp`)** kèm `libv_list.ini` với đủ 4 tham số (`emissivity = 0.85`, `distance = min(agl, 25.0)`, `humidity`, `reflection`) để giải mã nhiệt độ chuẩn từ `_T.JPG`, phân hạng bất thường `CoA 2 / CoA 3` (với `CoA 1 = Normal`), tính GSD nhiệt chứng minh ngưỡng $5 \times 5\text{ px/cell}$ và quy đổi $\Delta T_{\text{norm}}$ theo chuẩn IEC TS 62446-3.<br>2. **Huấn luyện mới 2 mô hình AI 2A & AI 2B:** Huấn luyện mới mô hình AI 2A (nhận diện tấm pin trên ảnh lẻ RGB) và AI 2B (nhận diện 4 lớp lỗi nhiệt `SingleHotSpot`, `MultiHotSpot`, `Bypass`, `ModuleOpenCircuit`).<br>3. **Khử méo ống kính (`DewarpData` + `cv2.undistortPoints(..., P=K)`) & Ghép cặp Nội tại RGB–Nhiệt theo Độ cao:** Kiểm tra `DewarpFlag`, quy đổi `cx_opencv = W/2 + cx_dewarp`, `cy_opencv = H/2 + cy_dewarp`, truyền `P=K` khi khử méo 4 đỉnh nhãn OBB và tính ma trận đồng trục `Dual-sensor Homography` riêng cho từng tầng độ cao (`31m`, `35m`, `42m`).<br>4. **Phép chiếu 8-DoF DLT Homography (Nội suy Song phương Hai đầu Dải bay `Bidirectional Strip Anchoring` với `4-DoF/6-DoF` liên khung), Ghép cặp Hungarian & Khử trùng lặp Đa góc nhìn:** Khóa cứng 2 ảnh đầu/cuối dải bay thấy biên lối đi, nội suy song phương bằng biến đổi `4-DoF Similarity / 6-DoF Affine` liên khung kèm kẹp tâm RTK ($\pm 10\text{ cm}$) để chống trôi dạt tỷ lệ ở giữa dãy trước khi giải `8-DoF DLT Homography (Hartley)`, **Hungarian Hai Ngưỡng** và gom cụm khử trùng lặp đa ảnh. | - Trọng số AI 2A & AI 2B (`.pt`, `.onnx`) + Bảng khảo sát mô hình & Confusion Matrix.<br>- Module giải mã `DJI Thermal SDK` (4 tham số + `libv_list.ini`) + Khử méo `DewarpData` (`P=K`) + Ghép cặp RGB–Nhiệt.<br>- Module chiếu `8-DoF DLT Homography` (Bidirectional Strip Anchoring) + `Hungarian Matching` + `Multi-View Deduplication`.<br>- Sơ đồ Sequence/Activity của Module 2 + Chương 3 (Phần 2). |
| **Thành viên 3 (TV3)**<br>**Tải trọng: ~34%**<br>*(Phụ trách Module 3)* | **Module 3: Thiết kế PTTKHT 6 Bước, CSDL PostGIS (`ST_AsMVT` + Trigger An toàn Thời gian) & Phần mềm Web Quản trị Bản sao số (`Rust Axum` + `MapLibre WebGL` + `Typst PDF`)** | 1. **Chuẩn hóa Hồ sơ 6 bước PTTKHT & CSDL PostGIS 7 bảng:** Thiết kế Use Case, ERD 7 bảng (có khóa `mvt_id BIGSERIAL`, `current_coa_class DEFAULT 1`, các cột môi trường chuẩn IEC 62446-3, `dewarp_applied_in_camera`, ràng buộc `UNIQUE(campaign_id, module_id, fault_class)` và **PostgreSQL Trigger kiểm tra `MAX(flight_date)` + ưu tiên độ nghiêm trọng lỗi**).<br>2. **Backend 100% Rust (`Axum` + `SQLx` + `PostGIS Dynamic MVT` + `Typst PDF`):** Viết mới hoàn toàn Backend bằng Rust; dùng hàm nội tại **`ST_AsMVT(..., 'mvt_id')` (SELECT kèm `mvt_id AS mvt_id_prop`) và `ST_TileEnvelope(..., margin => 64.0/4096.0)`** phát luồng Vector Tiles (`.mvt` `< 30 KB/tile`), cung cấp API JSON trạng thái lỗi lịch sử (`GET /api/campaigns/{id}/fault_states`), dựng khung `Redis Worker` phụ giúp TV2, và xuất biên bản bảo trì PDF bằng **`Typst`** trong `tokio::task::spawn_blocking`.<br>3. **Giao diện Web Quản trị 60 FPS (`React / TypeScript + MapLibre GL JS`):** Chốt kiến trúc Frontend `React/TypeScript + MapLibre GL JS (WebGL)` nối trực tiếp vào Backend Rust `Axum` ngay từ đầu Tuần 2; dùng khóa nguyên `mvt_id` cho `setFeatureState`, gọi `removeFeatureState` + đổi fallback style khi xem lịch sử đợt bay (chống bug "bóng ma trạng thái") và lọc theo mảng `['in', ['id'], ['literal', faultMvtIds]]`. | - Bộ bản vẽ 6 bước PTTKHT hoàn chỉnh.<br>- Docker PostGIS 7 bảng (kèm Trigger kiểm tra `MAX(flight_date)`) + Redis + Backend 100% Rust `Axum` (`ST_AsMVT` + `Typst PDF`).<br>- Giao diện Web Quản trị Bản sao số chạy mượt 60 FPS.<br>- Chương 2 PTTKHT & Kịch bản Demo trực tiếp. |

---

## 3. THIẾT KẾ HỆ THỐNG THEO 6 BƯỚC PTTKHT, CSDL POSTGIS 7 BẢNG & LUỒNG VECTOR TILES ĐỘNG (`ST_AsMVT`)

### 3.1. Tóm tắt 6 Bước PTTKHT Chuẩn Kỹ nghệ Phần mềm
1. **Bước 1 (Phân tích nghiệp vụ, Phân rã chức năng FDD & Đặc tả Use Case):** Hệ thống phục vụ 3 tác nhân (`System Admin`, `UAV/AI Engineer`, `O&M Technician`) với 7 Use Cases cốt lõi (`UC01` Khởi tạo trang trại & nạp `.gpkg` / XYZ WebP Tiles; `UC02` Chạy Pipeline AI 1 bắt vùng pin méo trên Ortho; `UC03` Tạo đợt bay khảo sát kèm thông số môi trường IEC 62446-3 & tải cặp ảnh lẻ RGB/Nhiệt; `UC04` Chạy Pipeline AI 2 bắt lỗi nhiệt, ánh xạ `module_id` & khử trùng lặp đa góc nhìn; `UC05` Kiểm duyệt QC các ca biên; `UC06` Tương tác Bản đồ số 60 FPS & chuyển đổi xem lịch sử các đợt bay qua JSON Delta; `UC07` Kết xuất biên bản bảo trì PDF chuẩn IEC TS 62446-3 bằng `Typst`).
2. **Bước 2 (Sơ đồ Use Case tổng thể):** Phân quyền rõ ràng giữa Quản trị viên, Kỹ sư AI và Kỹ sư O&M.
3. **Bước 3 (Thiết kế Cơ sở dữ liệu Không gian PostGIS – ERD 7 Bảng + Trigger Đồng bộ An toàn Thời gian):** Chi tiết tại Mục 3.2 bên dưới.
4. **Bước 4 (Sơ đồ Hoạt động Activity & Sơ đồ Tuần tự Sequence):** Mô tả chi tiết luồng bất đồng bộ qua `Rust Axum <-> Redis Queue <-> Python AI Worker <-> PostGIS (Trigger Sync) <-> SSE/WebSocket`.
5. **Bước 5 (Sơ đồ Kiến trúc Clean Architecture):** Tách biệt 4 tầng (Presentation WebGL 60 FPS $\rightarrow$ Application Rust Axum + Typst `spawn_blocking` $\rightarrow$ Domain Spatial & AI Engine $\rightarrow$ Infrastructure PostGIS R-Tree & Redis).
6. **Bước 6 (Hiện thực hóa & Kiểm thử Tích hợp sớm từ cuối Tuần 3):** Nối thông Mock Pipeline ngay cuối Tuần 3 trước khi nạp trọng số AI thật ở Tuần 4–5.

### 3.2. Sơ đồ Thực thể Liên kết (ERD 7 Bảng Cốt lõi — Đã chuẩn hóa `CoA 1 = Normal`, `mvt_id_prop` & Trigger Chống Ghi Đè Đợt Bay Cũ)
1. `solar_plants`:
   - `id` (PK, SERIAL), `plant_code` (VARCHAR UNIQUE: `TN19`, `BIM2`, `TNDL`, `TT12`), `name`, `crs_epsg` (INT DEFAULT 32649), `aoi_geom` (GEOMETRY(Polygon, 32649)), `raster_tile_url_template` (TEXT), `created_at`.
2. `plant_blocks_strings`:
   - `id` (PK, SERIAL), `plant_id` (FK), `block_code` (VARCHAR), `string_code` (VARCHAR), `pca_axis_u_x` (DOUBLE PRECISION), `pca_axis_u_y` (DOUBLE PRECISION — vector chỉ phương $\vec{u}$ đã khóa dấu theo tương quan từng hàng `Row_ID`), `row_count` (SMALLINT DEFAULT 4), `expected_modules` (INT).
3. `solar_modules` *(Bảng định danh gốc Digital Twin của cả 4 nhà máy — Chuẩn hóa `current_coa_class DEFAULT 1` theo IEC TS 62446-3)*:
   - `module_id` (PK, VARCHAR, ví dụ `tn19_block1_string4_00458`), **`mvt_id`** (BIGSERIAL UNIQUE — ID số nguyên dương duy nhất dùng làm top-level Feature ID cho Vector Tiles `.mvt` và `setFeatureState`), `plant_id` (FK), `block_string_id` (FK), `row_id` (SMALLINT 1..4), `pin_index` (INT `ID_Pin`).
   - `geom` (GEOMETRY(Polygon, 32649) — gắn chỉ mục không gian `CREATE INDEX idx_modules_geom_gist ON solar_modules USING GIST (geom)`).
   - `centroid_x` (DOUBLE PRECISION), `centroid_y` (DOUBLE PRECISION).
   - `is_distorted_recovered` (BOOLEAN DEFAULT FALSE — đánh dấu tấm pin vùng méo đường ghép ảnh được AI 1 + Topological Snapping khôi phục).
   - `current_health_status` (VARCHAR DEFAULT `'NORMAL'`), **`current_coa_class`** (SMALLINT **DEFAULT `1`** CHECK (`current_coa_class IN (1, 2, 3)`) — trong đó `1 = CoA 1 (Normal / No abnormality)`, `2 = CoA 2 (Thermal abnormality)`, `3 = CoA 3 (Safety-relevant abnormality)` theo đúng chuẩn IEC TS 62446-3).
4. `flight_campaigns` *(Quản lý các lần bay khảo sát — Đủ 4 tham số môi trường cho `DJI Thermal SDK` & IEC TS 62446-3)*:
   - `id` (PK, UUID), `plant_id` (FK), `campaign_name`, `flight_date` (TIMESTAMPTZ NOT NULL), `uav_camera_model` (VARCHAR: `DJI_ZH20T`, `DJI_M2EA`, `DJI_P1`), `planned_altitude_m` (FLOAT), `recorded_altitude_m` (FLOAT: `87.0, 41.9, 34.9, 30.9`), `gsd_rgb_cm` (FLOAT), `gsd_thermal_cm` (FLOAT).
   - **`irradiance_wm2`** (FLOAT — Cường độ bức xạ mặt phẳng giàn pin $G_{\text{POA}} \ge 600\text{ W/m}^2$), **`wind_speed_ms`** (FLOAT), **`ambient_temp_c`** (FLOAT), **`relative_humidity_pct`** (FLOAT **DEFAULT 70.0**), **`reflected_temp_c`** (FLOAT **DEFAULT 5.0** — Nhiệt độ bức xạ biểu kiến nền trời quang/môi trường hoặc đọc trực tiếp từ R-JPEG qua `dirp_get_measurement_params`), **`emissivity`** (FLOAT **DEFAULT 0.85** — Hệ số phát xạ kính cường lực mặt trước theo IEC TS 62446-3).
   - `status` (`UPLOADED`, `PROCESSING_AI`, `COMPLETED`, `FAILED`).
5. `raw_image_pairs` *(Có cờ `dewarp_applied_in_camera` và chỉ số dải bay `strip_id`, `strip_sequence_idx`)*:
   - `id` (PK, UUID), `campaign_id` (FK), `rgb_filename` (`_W.JPG`), `thermal_filename` (`_T.JPG`), `strip_id` (VARCHAR), `strip_sequence_idx` (INT — thứ tự ảnh liên tiếp trong dải bay phục vụ nội suy song phương hai đầu dải bay), `gps_x_utm` (DOUBLE PRECISION), `gps_y_utm` (DOUBLE PRECISION), `recorded_agl_m` (FLOAT), `gimbal_yaw` (FLOAT), `gimbal_pitch` (FLOAT), `rtk_fix_flag` (SMALLINT).
   - **`dewarp_applied_in_camera`** (BOOLEAN DEFAULT FALSE — đọc từ `DewarpFlag` trong XMP), `dewarp_params_json` (JSONB — lưu $f_x, f_y, c_{x,\text{opencv}}, c_{y,\text{opencv}}, k_1..k_4, p_1, p_2$).
6. `ai_raw_detections` *(Lưu toàn bộ các phát hiện thô trên từng khung ảnh trước khi gom cụm khử trùng lặp)*:
   - `id` (PK, UUID), `campaign_id` (FK), `image_pair_id` (FK NULLABLE), `pipeline_type` (`ORTHO_PANEL`, `SINGLE_RGB_PANEL`, `THERMAL_FAULT`), `class_label` (VARCHAR), `confidence` (FLOAT), `obb_pixel_coords` (JSONB), `dist_to_image_center_px` (FLOAT — khoảng cách tới tâm quang học $(W/2, H/2)$ để chọn góc nhìn nadir nhất), `temp_max_c` (FLOAT), `temp_mean_c` (FLOAT), `temp_delta_measured_c` (FLOAT), `temp_delta_norm_1000wm2_c` (FLOAT).
7. `module_inspection_logs` *(Bảng kết quả chẩn đoán chính thức sau khi đã gom cụm khử trùng lặp đa góc nhìn — Chỉ nhận `iec_coa_class IN (2, 3)` kèm `om_priority`)*:
   - `id` (PK, UUID), `campaign_id` (FK), `module_id` (FK $\rightarrow$ `solar_modules.module_id`), `best_image_pair_id` (FK — ảnh có góc nhìn gần tâm quang học nhất), `best_detection_id` (FK), `observation_count` (SMALLINT — số ảnh liên tiếp cùng nhìn thấy lỗi này).
   - `fault_class` (`SingleHotSpot`, `MultiHotSpot`, `Bypass`, `ModuleOpenCircuit`), **`iec_coa_class`** (SMALLINT CHECK (`iec_coa_class IN (2, 3)`) — phân hạng bất thường `CoA 2` hoặc `CoA 3` theo hình thái lỗi + $\Delta T_{\text{measured}}$ chuẩn IEC TS 62446-3), **`om_priority`** (VARCHAR CHECK (`om_priority IN ('LOW', 'MEDIUM', 'HIGH')`) — độ ưu tiên bảo trì O&M nội bộ), `temp_max_c` (FLOAT), `temp_delta_measured_c` (FLOAT), `temp_delta_norm_1000wm2_c` (FLOAT).
   - `projected_geom` (GEOMETRY(Polygon, 32649)), `spatial_iou` (FLOAT), `centroid_error_cm` (FLOAT), `hungarian_margin` (FLOAT).
   - `qc_status` (`AUTO_VERIFIED`, `PENDING_QC`, `HUMAN_CONFIRMED`, `HUMAN_CORRECTED`), `crop_rgb_url` (TEXT), `crop_thermal_url` (TEXT), `created_at`.
   - **Ràng buộc duy nhất:** `UNIQUE (campaign_id, module_id, fault_class)`.
   - **Cơ chế Đồng bộ Ngược An toàn Thời gian & Xử lý Đa lỗi (`trg_sync_module_health_after_inspection`):**
     ```sql
     CREATE OR REPLACE FUNCTION fn_sync_module_health_after_inspection()
     RETURNS TRIGGER AS $$
     DECLARE
         v_plant_id INT;
         v_camp_date TIMESTAMPTZ;
         v_max_date TIMESTAMPTZ;
         v_top_fault VARCHAR;
         v_top_coa SMALLINT;
     BEGIN
         SELECT plant_id, flight_date INTO v_plant_id, v_camp_date
         FROM flight_campaigns WHERE id = NEW.campaign_id;

         SELECT MAX(flight_date) INTO v_max_date
         FROM flight_campaigns WHERE plant_id = v_plant_id;

         -- Chỉ đồng bộ vào bảng solar_modules nếu đây là đợt bay mới nhất của nhà máy
         IF v_camp_date = v_max_date THEN
             SELECT fault_class, iec_coa_class INTO v_top_fault, v_top_coa
             FROM module_inspection_logs
             WHERE campaign_id = NEW.campaign_id AND module_id = NEW.module_id
             ORDER BY iec_coa_class DESC,
                      CASE fault_class
                          WHEN 'ModuleOpenCircuit' THEN 4
                          WHEN 'Bypass' THEN 3
                          WHEN 'MultiHotSpot' THEN 2
                          ELSE 1
                      END DESC,
                      temp_delta_measured_c DESC
             LIMIT 1;

             UPDATE solar_modules
             SET current_health_status = COALESCE(v_top_fault, 'NORMAL'),
                 current_coa_class = COALESCE(v_top_coa, 1)
             WHERE module_id = NEW.module_id;
         END IF;
         RETURN NEW;
     END;
     $$ LANGUAGE plpgsql;
     ```

### 3.3. Truy vấn SQL Vector Tiles Động (`ST_AsMVT`) & Logic Chuyển đổi Đợt bay Lịch sử Không Bị "Bóng ma Trạng thái" trên MapLibre GL JS
```sql
SELECT ST_AsMVT(tile, 'solar_modules_layer', 4096, 'geom', 'mvt_id') AS mvt_binary
FROM (
    SELECT 
        m.mvt_id,
        m.mvt_id AS mvt_id_prop,
        m.module_id,
        m.row_id,
        m.pin_index,
        m.is_distorted_recovered,
        m.current_health_status,
        m.current_coa_class,
        ST_AsMVTGeom(
            ST_Transform(m.geom, 3857),
            ST_TileEnvelope($1, $2, $3),
            4096, 64, true
        ) AS geom
    FROM solar_modules m
    WHERE m.plant_id = $4
      AND m.geom && ST_Transform(
          ST_TileEnvelope($1, $2, $3, margin => (64.0 / 4096.0)),
          32649
      )
) AS tile
WHERE geom IS NOT NULL;
```
- **Giải pháp triệt tiêu hoàn toàn Bug "Bóng ma trạng thái" (`Ghost State`) & Giới hạn `setFilter` trên MapLibre GL JS:**
  1. Khi người dùng chuyển sang xem một đợt bay cũ trong lịch sử (`isHistoricalView = true`), trình duyệt gọi `map.removeFeatureState({ source: 'solar_modules', sourceLayer: 'solar_modules_layer' })` để xóa sạch trạng thái cũ, nạp gói JSON lỗi siêu nhẹ (`~20 KB`) của đợt bay đó qua `map.setFeatureState({ source: 'solar_modules', sourceLayer: 'solar_modules_layer', id: item.mvt_id }, { coa_class: item.iec_coa_class, fault_class: item.fault_class })`, và cập nhật biểu thức tô màu dùng fallback `1` (Normal) thay vì đọc cột `current_coa_class` của đợt bay mới nhất:
     ```javascript
     const activeCoaExpr = isHistoricalView
       ? ["coalesce", ["feature-state", "coa_class"], 1]
       : ["coalesce", ["feature-state", "coa_class"], ["get", "current_coa_class"]];
     ```
  2. Khi người dùng bật bộ lọc *"Chỉ hiện tấm pin lỗi CoA 3 / Loại lỗi X"*, vì MapLibre GL JS không cho phép dùng `["feature-state", ...]` bên trong `map.setFilter` ([MapLibre Issue #6213](https://github.com/maplibre/maplibre-gl-js/issues/6213)), giao diện lọc danh sách `mvt_id` thỏa mãn điều kiện ngay trên mảng JSON trong bộ nhớ và gọi:
     ```javascript
     map.setFilter('solar-modules-fill', ['in', ['id'], ['literal', filteredMvtIds]]);
     ```

---

## 4. ĐÁNH GIÁ ĐỘ PHỨC TẠP THUẬT TOÁN & BỘ CÂU TRẢ LỜI PHẢN BIỆN AI TRƯỚC HỘI ĐỒNG

### 4.1. Bảng Đánh giá Độ phức tạp Thuật toán ($O(\cdot)$)
| Bài toán con trong Pipeline | Giải thuật ngây thơ (Naive Approach) | Giải thuật đề xuất trong ĐATN | Độ phức tạp Thời gian & Không gian | Hiệu quả thực tế |
| :--- | :--- | :--- | :--- | :--- |
| **1. Tìm tấm pin ứng viên trên Bản đồ số (`spatial_grid_index`)** | Quét vét cạn tính IoU giữa $M$ hộp dự đoán với $N$ tấm pin trong CSDL: **$O(M \times N)$** ($\approx 1,86 \times 10^8$ phép tính). | Truy vấn vùng bao **R-Tree (`GIST` / `STRtree`)** kết hợp **KD-Tree** 2D trong bán kính $r = 52,4\text{ cm}$: **$O(M \log N)$**. | Thời gian: **$O((N + M) \log N)$**<br>Không gian: **$O(N)$** | Giảm số phép tính IoU hình học hơn **4.500 lần**, chạy xong trong **$< 0,2\text{ giây}$**. |
| **2. Nắn chỉnh lưới đàn hồi (`Elastic Mass-Spring Regularization`)** | Giải hệ phương trình ma trận đặc $(2M \times 2M)$ bằng khử Gauss: **$O(M^3)$**. | Biểu diễn đồ thị lò xo thưa (bậc trung bình $d \le 4$) và giải tối ưu lặp `Conjugate Gradient / L-BFGS`: **$O(I \cdot |E|) = O(I \cdot M)$**. | Thời gian: **$O(I \cdot M)$**<br>Không gian: **$O(M + |E|)$** | Xử lý hàng nghìn tấm pin trong **$< 0,8\text{ giây}$**, kéo sai số RMSE xuống **`< 12 cm`**. |
| **3. Ghép cặp tối ưu Một-đối-Một (`Hungarian Optimal Assignment`)** | Chạy thuật toán Kuhn-Munkres trên toàn ma trận đặc $(M \times N)$: **$O(M^2 \cdot N)$**. | **Phân rã cụm không gian theo `Block/String` + Cắt tỉa ma trận thưa ($\Delta d < 52,4\text{ cm}$):** Chia thành $C$ chuỗi độc lập, mỗi chuỗi có $m_c \approx 35$ tấm: **$O(\sum_{c=1}^{C} m_c^3) \approx O(M \cdot \bar{m}^2)$**. | Thời gian: **$O(M \cdot \bar{m}^2)$** ($\bar{m} \ll M$)<br>Không gian: **$O(M \cdot k)$** | Ghép cặp toàn khu vực chỉ mất **$\approx 0,15\text{ giây}$**, đạt độ chính xác gán mã **`module_id` $> 99,8\%$**. |
| **4. Ước lượng Phối cảnh `8-DoF DLT Homography` + Nội suy Song phương Dải bay** | Giải SVD trực tiếp trên tọa độ UTM thô ($\kappa(A) \sim 1,90 \times 10^{17}$) hoặc nhân chuỗi 8-DoF Homography đơn hướng gây suy biến tỷ lệ ở giữa dãy. | **Neo Hai đầu Dải bay (`Bidirectional Strip Anchoring` với `4-DoF/6-DoF` liên khung) + Chuẩn hóa Hartley** đưa tọa độ về gốc $(0,0)$ khoảng cách trung bình $\sqrt{2}$ trước khi giải SVD + RANSAC: **$O(R_{\text{iter}} + K)$**. | Thời gian: **$O(K)$**<br>Không gian: **$O(K)$** | Giảm số điều kiện ma trận $\kappa(A)$ xuống **$\sim 1.496$** (cải thiện $10^{13}$ lần), triệt tiêu 100% lỗi trượt cột và lỗi trôi dạt tỷ lệ ở độ cao 31m. |

### 4.2. Bảng Khảo sát & Lý giải Chọn Mô hình theo Phần cứng (CPU, GPU, VRAM)
- **Trả lời câu hỏi 1 (*"Tại sao chọn YOLO-OBB theo phần cứng hiện có?"*):** Các dãy pin mặt trời nằm nghiêng một góc $\theta$ và xếp sát khít nhau (khe hở `2–5 cm` $\approx 1–2$ pixel). Nếu dùng hộp ngang (HBB), các hộp đè lên nhau làm NMS xóa nhầm tấm pin bên cạnh. Với GPU tầm trung (Tesla T4 16GB / RTX 3060 12GB VRAM) khi train ảnh $1024 \times 1024$ chứa `150–300 tấm pin/ảnh`, kiến trúc **YOLO11s-OBB / YOLOv8s-OBB** (`~11,4M` tham số, `~29 GFLOPs`) chỉ chiếm **6,8 – 11,2 GB VRAM** ở `batch_size = 8–16` và đạt tốc độ suy luận **12–22 ms/ảnh**.
- **Trả lời câu hỏi 2 (*"Tại sao các mô hình cũ hơn không phù hợp?"*):**
  1. **Họ HBB cũ (`YOLOv5/v7/v8 HBB`, `Faster R-CNN`):** Không có góc xoay $\theta$, hộp bao chứa $35–50\%$ nền thừa và đè lên tấm bên cạnh, làm hỏng phép tính giao cắt IoU khi gán `module_id`.
  2. **Họ R-CNN 2 giai đoạn có hướng (`Oriented R-CNN`, `RoI Transformer`, `Gliding Vertex`):** Với mật độ `200–300 tấm pin/ảnh`, tầng Rotated RPN sinh hàng nghìn vùng đề xuất làm VRAM vượt **$> 18\text{ GB}$** ở kích thước $1024 \times 1024$ và tốc độ chậm **120–250 ms/ảnh** (chậm hơn 8–12 lần).
  3. **Họ Phân vùng mặt nạ (`Mask R-CNN`, `SAM`):** Tại vùng ảnh Ortho bị **méo đường ghép mảnh (seamline)**, mặt nạ pixel bị đứt gãy hoặc biến dạng đa giác lồi lõm, không thể trích xuất 4 đỉnh chuẩn để khớp vào lưới `.gpkg`.
  4. **Họ Transformer (`DETR`, `Deformable DETR`, `RT-DETR`):** Chi phí Self-Attention bậc hai $O((H \times W)^2)$ ở độ phân giải $1024 \times 1024$ và giới hạn cứng `300 queries` bị bão hòa khi một khung ảnh Ortho chứa trên `250–350` tấm pin dày đặc.
  5. **Họ Anchor xoay đời cũ (`Rotated RetinaNet`, `R3Det`):** Phải đặt sẵn hàng chục Anchor xoay cho mỗi điểm ảnh gây sai số lượng tử hóa góc, kém xa cơ chế **Anchor-free + ProbIoU Loss** (tính khoảng cách Bhattacharyya giữa 2 phân phối Gaussian 2D) của YOLO-OBB.

---

## 5. MA TRẬN THAM CHIẾU CHUẨN ĐẦU RA (CLO) – HƯỚNG CHỨNG MINH & HƯỚNG MỞ

| Mã CLO (HP `7724162` & QĐ `483`) | Nội dung yêu cầu của Chuẩn đầu ra | Hướng chứng minh cụ thể trong Báo cáo & Sản phẩm ĐATN | Hướng mở phát triển (Future Work) |
| :--- | :--- | :--- | :--- |
| **`CLO1` (HP)**<br>*(Tương ứng `CLO1`, `CLO3` QĐ 483)* | Phân tích có hệ thống bài toán KHMT bằng toán học, KHTN và kiến thức chuyên ngành; đánh giá độ phức tạp thuật toán $O(n)$, ma trận, xác suất, quy luật vật lý. | 1. **Toán học & Quang học:** Hệ trục nội tại PCA $(\vec{u}, \vec{v})$ khóa hướng bằng tương quan từng hàng $\text{Cov}_r(u, \text{ID\_Pin}) > 0$, khử méo ống kính `DewarpData` với `cx_opencv = W/2 + cx_dewarp` và `cv2.undistortPoints(..., P=K)`, chuẩn hóa Hartley, 8-DoF DLT Homography (Nội suy song phương hai đầu dải bay `Bidirectional Strip Anchoring`), hàm mất mát `ProbIoU` và thuật toán Hungarian.<br>2. **Vật lý nhiệt học & Quang học (IEC TS 62446-3):** Giải mã bức xạ Planck qua `DJI Thermal SDK (dirp)` với đủ 4 tham số (`emissivity = 0.85`, `sdk_distance <= 25.0m`, `humidity`, `reflection`), phân tích ngưỡng GSD nhiệt $5 \times 5\text{ px/cell}$ ($2,75\text{ cm/px}$ ở `31m` vs $3,73\text{ cm/px}$ ở `42m`), phân hạng chuẩn `CoA 1 = Normal`, `CoA 2/3 = Abnormality` và quy đổi $\Delta T_{\text{norm}} = \Delta T_{\text{measured}} \cdot (1000/G_{\text{POA}})^x$.<br>3. **Độ phức tạp thuật toán:** Bảng chứng minh giảm độ phức tạp từ $O(M \times N)$ xuống $O((N+M) \log N)$ nhờ R-Tree/KD-Tree và giải hệ thưa $O(I \cdot M)$ cho mạng lò xo Mass-Spring. | Mở rộng sang mô hình **Chiếu tia 3D (3D Ray-Casting trên DSM/DEM `.tif` và đám mây điểm `.laz`)** cho các nhà máy điện mặt trời lắp đặt trên sườn đồi dốc phức tạp. |
| **`CLO2` (HP)**<br>*(Tương ứng `CLO2`, `CLO5`, `CLO7` QĐ 483)* | Thiết kế và hiện thực hóa giải pháp đáp ứng yêu cầu, khả thi, hiệu quả; tuân thủ PTTKHT (UML, ERD, Clean Architecture) và tích hợp yếu tố đạo đức, môi trường, an toàn xã hội. | 1. **Thiết kế PTTKHT 6 bước & Kiến trúc hiện đại:** Backend Rust `Axum`, PostGIS `ST_AsMVT` (có `mvt_id_prop`, `margin` và Trigger kiểm tra `MAX(flight_date)`), XYZ WebP Raster Tiles (`--exclude -z 15-21`) / `PMTiles`, xuất báo cáo PDF bằng `Typst` trong `spawn_blocking`.<br>2. **Đạo đức AI & An toàn vận hành:** Cơ chế **Dual-Threshold Gating & QC Queue**: tự động gắn cờ `PENDING_QC` khi biên quyết định $< 0,15$ hoặc bức xạ mặt trời $< 600\text{ W/m}^2$ (cảnh báo điều kiện đo chưa đạt chuẩn IEC TS 62446-3 để kỹ sư không kết luận nhầm). | Tự động xuất tệp đường bay kiểm tra lại (`.kmz` Waypoint) cho drone DJI tại các cụm `module_id` có cấp độ lỗi nghiêm trọng CoA 3. |
| **`CLO3` (HP)**<br>*(Tương ứng `CLO1`, `CLO2`, `CLO7` QĐ 483)* | Vận dụng hiệu quả kiến thức Trí tuệ nhân tạo: khảo sát lựa chọn mô hình theo phần cứng, tự huấn luyện mô hình trên bộ dữ liệu xây dựng từ đầu, tối ưu hóa và đánh giá định lượng. | 1. **Tự huấn luyện & Khảo sát đối chứng minh bạch:** Bảng thực nghiệm đối sánh giữa 4 họ kiến trúc (`HBB`, `Oriented R-CNN`/`Rotated RetinaNet`, `RT-DETR`, `YOLO-OBB`) trên `Stratified Subset` và đối chứng cả 2 chế độ khởi tạo (`Random Init 300 epochs` vs `Pretrained Backbone Init`) theo CPU, GPU, VRAM, GFLOPs, FPS.<br>2. **Đánh giá đa trang trại & đa độ cao:** Kiểm chứng trên dữ liệu 4 trang trại Ninh Thuận và 4 tầng độ cao (`87m`, `42m`, `35m`, `31m`). | Nghiên cứu mạng **Cross-Modal Attention hợp nhất trực tiếp đặc trưng RGB + Nhiệt 16-bit** và lưu trữ vector đặc trưng vào **Qdrant Vector DB** để dự báo tốc độ suy thoái tấm pin theo chuỗi thời gian. |
| **`CLO4` (HP)**<br>*(Tương ứng `CLO4`, `CLO6` QĐ 483)* | Trình bày hiệu quả đồ án qua báo cáo văn bản chuẩn thể thức, slide bảo vệ tách bạch Đầu vào/Đầu ra – Thực thi, thuyết trình và trả lời phản biện. | Báo cáo $\le 150$ trang chuẩn Quy định `483/QĐ-ĐHXDHN`; Slide Mở đầu chỉ nêu Đầu vào/Đầu ra; Slide Thực thi trình bày thuật toán, độ phức tạp $O(\cdot)$ và luồng dữ liệu qua 7 bảng PostGIS; Demo trực tiếp 60 FPS. | Công bố bài báo khoa học và bộ dữ liệu chuẩn hóa của 4 trang trại điện mặt trời. |
| **`CLO5` (HP)**<br>*(Tương ứng `CLO4`, `CLO6`, `CLO8` QĐ 483)* | Làm việc nhóm hiệu quả: phân chia 3 module cân bằng tải (`33% – 33% – 34%`), tích hợp sớm từ Tuần 3–4 qua GitFlow/Docker. | Phân định rõ 3 Module cá nhân kèm thư viện giao tiếp chung (`spatial_grid_index`, `solar_shared` crate, Mock Pipeline tích hợp sớm từ cuối Tuần 3 và chốt kiến trúc Frontend hiệu năng cao từ đầu Tuần 2). | Phát triển thành nền tảng SaaS thương mại phục vụ kiểm định O&M cho các nhà máy năng lượng tái tạo tại Việt Nam. |

---

## 6. PHỤ LỤC: DỰ THẢO NỘI DUNG PHIẾU GIAO NHIỆM VỤ ĐATN (THEO MẪU ĐATN-01 – HUCE)

1. **Tên đề tài Đồ án tốt nghiệp:**
   - **Tiếng Việt:** *Xây dựng hệ thống Bản sao số (Digital Twin) tích hợp Trí tuệ nhân tạo nhận diện tấm pin biến dạng và định vị khuyết tật nhiệt từ dữ liệu UAV phục vụ quản lý vận hành nhà máy điện mặt trời.*
   - **Tiếng Anh:** *Building an AI-Integrated Digital Twin System for Distorted Solar Panel Detection and UAV Thermal Defect Localization in Photovoltaic Plant Operations and Maintenance.*
2. **Các dữ liệu ban đầu và tài liệu chính:**
   - Bộ cơ sở dữ liệu bản đồ số `.gpkg` và ảnh trực giao `.tif` của 04 nhà máy điện mặt trời tại Ninh Thuận (Thuận Nam 19, BIM 2, Thuận Nam Đức Long, Thiên Tân 1.2) cùng dữ liệu bay khảo sát thực tế ở các độ cao `87m`, `42m`, `35m`, `31m` (cặp ảnh lẻ RGB `_W.JPG` và ảnh nhiệt bức xạ 16-bit R-JPEG `_T.JPG`).
3. **Nội dung các phần thuyết minh và tính toán (Phân chia cân bằng `33% – 33% – 34%` cho 03 thành viên):**
   - **Phần chung:** Khảo sát nghiệp vụ O&M nhà máy điện mặt trời theo chuẩn IEC TS 62446-3, xác định bài toán Đầu vào – Đầu ra, thiết kế kiến trúc tổng thể hệ thống Bản sao số và kiểm thử tích hợp toàn hệ thống.
   - **Sinh viên 1 (Module 1 – 33%):** Khai thác bộ tệp `.gpkg` của 4 trang trại, xây dựng thuật toán nội suy vùng tấm pin bị méo theo hệ trục nội tại PCA khóa hướng từng hàng; huấn luyện mô hình AI 1 (Ortho-OBB Detector) bắt vùng pin méo trên bản đồ trực giao chính; xây dựng thư viện chỉ mục không gian dùng chung `spatial_grid_index` (R-Tree/KD-Tree, trích xuất điểm neo biên hai đầu dải bay `get_block_string_boundary_landmarks`, nắn lưới tô-pô `Topological Snapping`, mạng lò xo đàn hồi `Elastic Mass-Spring`) và xuất bản đồ nền `XYZ WebP Raster Tiles` (`--exclude -z 15-21`) / `PMTiles`.
   - **Sinh viên 2 (Module 2 – 33%):** Chia tập dữ liệu ảnh lẻ RGB và ảnh nhiệt theo dải không gian cách ly `15m`; tích hợp `DJI Thermal SDK (dirp)` giải mã nhiệt độ bức xạ 16-bit (đủ 4 tham số với `emissivity = 0.85`, `d <= 25m`), phân hạng `CoA 2 / CoA 3` (với `CoA 1 = Normal`), phân tích ngưỡng GSD nhiệt $5 \times 5\text{ px/cell}$ và chuẩn hóa $\Delta T_{\text{norm}}$ theo IEC TS 62446-3; huấn luyện mô hình AI 2A (nhận diện tấm pin ảnh lẻ) và AI 2B (phát hiện 4 lớp lỗi nhiệt); khử méo ống kính `DewarpData` (`cx_opencv = W/2 + cx_dewarp`, `cv2.undistortPoints(..., P=K)`), ghép cặp RGB–Nhiệt đa độ cao, thực hiện phép chiếu `8-DoF DLT Homography` (nội suy song phương hai đầu dải bay `Bidirectional Strip Anchoring` với `4-DoF/6-DoF` liên khung + chuẩn hóa Hartley) kết hợp thuật toán `Hungarian Hai Ngưỡng` và gom cụm khử trùng lặp đa góc nhìn (`Multi-View Deduplication`) để định vị lỗi vào đúng `module_id`.
   - **Sinh viên 3 (Module 3 – 34%):** Phân tích và thiết kế hệ thống theo chuẩn 6 bước PTTKHT; thiết kế cơ sở dữ liệu không gian PostgreSQL/PostGIS 7 bảng có chỉ mục R-Tree, Trigger đồng bộ trạng thái kiểm tra `MAX(flight_date)` và hàm truy vấn Vector Tiles động `ST_AsMVT` (`mvt_id`, `mvt_id_prop`, `margin`); xây dựng Backend hiệu năng cao bằng ngôn ngữ Rust (`Axum` + `SQLx` + `Redis Queue` + xuất báo cáo PDF bằng `Typst` trong `spawn_blocking`) và giao diện Web Quản trị Bản sao số 60 FPS sử dụng `MapLibre GL JS (WebGL)`.
4. **Các bản vẽ và sản phẩm phần mềm cần nộp:**
   - Báo cáo thuyết minh ĐATN ($\le 150$ trang A4) kèm bộ bản vẽ 6 bước PTTKHT (Use Case, ERD, Sequence, Activity, System Architecture) và lưu đồ thuật toán AI / Ánh xạ không gian.
   - Bộ trọng số các mô hình AI (`.pt`, `.onnx`), thư viện `spatial_grid_index` và phần mềm Web Quản trị Bản sao số hoàn chỉnh.
5. **Ngày giao nhiệm vụ:** `16/11/2026` — **Ngày hoàn thành nộp báo cáo:** `17/01/2027`.
