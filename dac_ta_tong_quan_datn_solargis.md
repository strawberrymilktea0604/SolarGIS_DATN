# ĐẶC TẢ TỔNG QUAN ĐỀ TÀI ĐỒ ÁN TỐT NGHIỆP (ĐATN)
## HỆ THỐNG BẢN SAO SỐ (DIGITAL TWIN) VÀ TRÍ TUỆ NHÂN TẠO ĐA LUỒNG TRONG GIÁM SÁT, ĐỊNH VỊ KHUYẾT TẬT NHÀ MÁY ĐIỆN MẶT TRỜI TỪ DỮ LIỆU UAV

- **Trường:** Trường Đại học Xây dựng Hà Nội (HUCE)
- **Khoa / Bộ môn:** Khoa Công nghệ Thông tin – Bộ môn Khoa học Máy tính
- **Học phần:** Đồ án tốt nghiệp Khoa học Máy tính (Mã học phần: `7724162` – `14` tín chỉ)
- **Quy mô nhóm:** `03` sinh viên (Mỗi sinh viên phụ trách độc lập `01` Module cốt lõi và phối hợp tích hợp hệ thống chung theo Điều 7 – Quyết định số `483/QĐ-ĐHXDHN` ngày `20/03/2026`)
- **Thời gian thực hiện kế hoạch:** `16/11/2026` – `17/01/2027` (`09` tuần làm việc tập trung đến hạn nộp báo cáo tổng kết)

---

## 1. TỔNG QUAN ĐỀ TÀI & BÀI TOÁN THỰC TẾ (ĐẦU VÀO – XỬ LÝ – ĐẦU RA)

### 1.1. Bối cảnh và phạm vi giải quyết trong thực tế
Các nhà máy điện mặt trời quy mô công nghiệp tại Ninh Thuận (như [Nhà máy Thuận Nam 19](https://drive.google.com/drive/folders/1WPPAEHEcZEhZ1ULd4_TZQ1ATtIHrIgS3), [Nhà máy BIM 2](https://drive.google.com/drive/folders/1oXIHbyJ_v_xHeJkR81LJpibSoQRzs9Pa), [Nhà máy Thuận Nam Đức Long](https://drive.google.com/drive/folders/1xclyH3rnpCbCuroNabF8wbUbHAm_L3o6), và [Điện mặt trời Thiên Tân 1.2](https://drive.google.com/drive/folders/1DJdRk5LAD30srVknErJ57DWZuP5ebFPE) trong đợt khảo sát [Khảo sát điện mặt trời Ninh Thuận - 4/2026](https://drive.google.com/drive/folders/1pNG8IsaklZ65U-JpmXnPZmDTCVDmwlu9)) có diện tích hàng chục hecta với hàng chục nghìn tấm pin (riêng khu vực khảo sát tại Thuận Nam 19 có **36.544 tấm pin** chia thành `6` Block, `148` chuỗi String). Trong quá trình vận hành (O&M), các tấm pin thường xuyên xuất hiện lỗi nhiệt (Hotspot đơn điểm, đa điểm, lỗi Đi-ốt Bypass, hở mạch chuỗi/tấm) gây sụt giảm công suất và nguy cơ cháy nổ.

Khi dùng thiết bị bay không người lái (UAV) mang camera kép (RGB và Nhiệt bức xạ R-JPEG) để khảo sát định kỳ, đội ngũ kỹ sư gặp **03 bài toán thực tế lớn**:
1. **Biến dạng ghép mảnh trên bản đồ trực giao tổng thể (Orthomosaic 85m–87m):** Khi ghép hàng trăm ảnh bay cao độ lớn bằng phần mềm quang trắc (Agisoft Metashape), các tấm pin nằm ở đường ghép mảnh (seamline) hoặc rìa dãy bị uốn cong, răng cưa hoặc lệch trục. Nếu kẻ lưới thủ công trên QGIS thì phải bỏ trống các vùng méo này, còn mô hình AI thông thường thì bỏ sót vì hình dáng không còn chữ nhật chuẩn.
2. **Độ phân giải ảnh nhiệt thấp và sai số vị trí GPS giữa ảnh lẻ và bản đồ tổng:** Ảnh nhiệt bay tầm thấp (`31m`, `35m`, `42m`) có kích thước nhỏ ($640 \times 512$ px), khó nhìn ranh giới từng tấm pin nếu không ghép cặp với ảnh lẻ RGB cùng góc chụp. Hơn nữa, nếu chỉ dùng tọa độ GPS/RTK gắn trong EXIF của ảnh để chiếu thẳng lên bản đồ số thì sai số lệch vị trí lên tới **155,37 cm** (lệch sang tấm pin ở hàng hoặc cột bên cạnh).
3. **Thiếu phần mềm quản lý Bản sao số (Digital Twin) xuyên suốt các đợt bay:** Dữ liệu hiện tại nằm rời rạc ở các tệp `.tif`, `.gpkg` và thư mục ảnh lẻ, chưa có hệ thống Web quản trị tập trung để theo dõi lịch sử sức khỏe của từng mã định danh `module_id` qua nhiều lần bay khác nhau.

---

### 1.2. Xác định rõ: ĐẦU VÀO $\rightarrow$ XỬ LÝ $\rightarrow$ ĐẦU RA
*(Lưu ý quan trọng khi làm Slide mở đầu bảo vệ: Phần Mở đầu chỉ trình bày **Đầu vào** và **Đầu ra** nghiệp vụ dưới đây, tuyệt đối **không** nêu tên thuật toán/giải thuật. Các thuật toán chỉ được trình bày ở phần Thực thi/Triển khai).*

#### A. ĐẦU VÀO (Inputs)
1. **Bản đồ trực giao tổng thể (Main Orthomosaic) & Bản đồ số gốc:**
   - Ảnh trực giao toàn khu vực bay cao độ `85m–87m` (GSD $\approx 3,0\text{ cm/pixel}$, hệ tọa độ phẳng `EPSG:32649` – UTM Zone 49N) từ thư mục [SolarGISExport](https://drive.google.com/drive/folders/1AZRTJ8_ywbQ5bM90SK7C_bmgeReL6B9n) và [SolarPanel_ExportOrtho](https://drive.google.com/drive/folders/1r9IpvEDOiUttqkTFHFfX1D4kgsqZk2y0).
   - Cơ sở dữ liệu bản đồ gốc [thuannam19_master.gpkg](https://drive.google.com/file/d/1ytHofNRDcg9pFgoFGIhPRunAOChdTycN/view?usp=drivesdk) chứa ranh giới khu vực (`aoi_boundary`), `2.492` mảnh bản đồ nền (`orthophoto_87m`) và `36.544` đa giác tấm pin tiêu chuẩn (`modules`) đã gán sẵn `Block`, `String_ID`, `Row_ID`, `ID_Pin`, `module_id`.
2. **Cặp ảnh lẻ RGB và Ảnh nhiệt đồng bộ từ các đợt bay tầm thấp (`31m`, `35m`, `42m`):**
   - Cặp ảnh chụp đồng thời từ UAV (`_W.JPG` là ảnh màu RGB độ phân giải cao và `_T.JPG` là ảnh nhiệt R-JPEG 16-bit kích thước $640 \times 512$ px kèm thông số tọa độ RTK/GPS và góc nghiêng Gimbal trong EXIF) lưu tại [Dataset SolarGIS](https://drive.google.com/drive/folders/19Q4l_0n9PG-1jKd0byaydxeSapxwu5rL), [SolarGIS_Dataset_1](https://github.com/strawberrymilktea0604/SolarGIS_Dataset_1), [SolarGIS_Dataset_2](https://github.com/strawberrymilktea0604/SolarGIS_Dataset_2) và [Roboflow solar-segment-obb](https://universe.roboflow.com/qu-nguyn-nh-s-workspace/solar-segment-obb).

#### B. ĐẦU RA (Outputs)
1. **Bản đồ số Digital Twin hoàn chỉnh 100% vị trí tấm pin:**
   - Nhận diện đầy đủ các tấm pin trên bản đồ Ortho chính (bao gồm cả các vùng tấm pin bị méo/biến dạng do ghép ảnh mà bản vẽ QGIS cũ bỏ trống) và gán đúng mã định danh duy nhất `module_id` (ví dụ: `block1_string4_00458`) theo thứ tự chuỗi/hàng.
2. **Báo cáo chẩn đoán lỗi nhiệt gắn chính xác vào từng tấm pin (`module_id`):**
   - Trả lời tự động và chính xác 3 câu hỏi nghiệp vụ cho từng lần bay:
     1. **Nhận diện được các lỗi gì?** (`SingleHotSpot` – Quá nhiệt đơn điểm, `MultiHotSpot` – Quá nhiệt đa điểm, `Bypass` – Lỗi đi-ốt nhánh, `ModuleOpenCircuit` – Hở mạch toàn tấm/chuỗi).
     2. **Lỗi đó rơi vào tấm pin nào trên ảnh chụp và trên thực địa?** (Tọa độ tâm $(X, Y)$ hệ UTM `EPSG:32649`, độ lệch vị trí $< 12\text{ cm}$).
     3. **Mã `module_id` của tấm pin bị lỗi là gì?** (Thuộc `Block` nào, `String` nào, `Row` nào, thứ tự tấm `ID_Pin` số mấy, nhiệt độ bất thường và ảnh cắt minh chứng).
3. **Phần mềm Web quản trị Bản sao số (Digital Twin Web Portal):**
   - Giao diện bản đồ số tương tác hiển thị trực quan toàn bộ nhà máy, cho phép quản lý nhiều đợt bay khảo sát (Flight Campaigns), lọc tấm pin theo loại lỗi/mức độ nghiêm trọng, xem đối chiếu ảnh RGB – Ảnh nhiệt tại từng `module_id` và xuất biên bản bảo trì.

#### C. XỬ LÝ (Processing — Chỉ trình bày trong phần Thực thi / Triển khai)
Hệ thống thực thi qua **03 khối xử lý độc lập nhưng kết nối chặt chẽ**:
- **Pipeline AI 1 (Nhận diện Ortho chính & Khôi phục vùng pin méo):** Huấn luyện từ đầu mô hình nhận diện khung xoay định hướng (Oriented Bounding Box – OBB) kết hợp tăng cường dữ liệu biến dạng quang học/hình học (Elastic/Seamline Distortion Augmentation) và thuật toán nắn chỉnh lưới tô-pô (Topological Grid Snapping) để bắt trọn cả các tấm pin bị méo trên bản đồ Ortho `85m–87m` và đánh mã `module_id`.
- **Pipeline AI 2 (Nhận diện tấm pin trên ảnh lẻ + Phát hiện lỗi nhiệt & Ánh xạ bản đồ số):** Huấn luyện từ đầu mô hình nhận diện tấm pin trên ảnh lẻ và mô hình phân loại/định vị 4 nhóm lỗi nhiệt trên ảnh nhiệt; ghép cặp hộp giới hạn giữa ảnh nhiệt và ảnh RGB, sau đó dùng phép biến đổi hình học 8 bậc tự do (8-DoF DLT Homography có chuẩn hóa Hartley) kết hợp tối ưu hóa đàn hồi (Mass-Spring) và thuật toán ghép cặp tối ưu Hungarian hai ngưỡng (Dual-Threshold Gating) để chiếu chính xác lỗi lên đúng `module_id` trên bản đồ số.
- **Nền tảng Backend hiệu năng cao & Web Quản trị Digital Twin:** Lưu trữ dữ liệu không gian trong PostgreSQL/PostGIS (chỉ mục không gian R-Tree), xử lý luồng tải ảnh lớn/suy luận bất đồng bộ và hiển thị bản đồ WebGL 60 FPS.

---

## 2. GIẢI ĐÁP 02 CÂU HỎI KỸ THUẬT TRỌNG TÂM CỦA NHÓM

### 2.1. Câu hỏi 1: Có tận dụng được tệp `.gpkg` kẻ lưới sẵn của QGIS (như `thuannam19_master.gpkg` và các file `Block1..6.gpkg`) để chia tập Train / Valid / Test và huấn luyện nhận diện vùng pin bị méo không?

**Câu trả lời: HOÀN TOÀN ĐƯỢC VÀ ĐÂY LÀ LỢI THẾ CỰC LỚN CỦA ĐỀ TÀI.**
Qua phân tích trực tiếp tệp [thuannam19_master.gpkg](https://drive.google.com/file/d/1ytHofNRDcg9pFgoFGIhPRunAOChdTycN/view?usp=drivesdk) (dung lượng `64,68 MB`) và tài liệu [Nghiên cứu cấu trúc tệp Master GeoPackage (.gpkg).pdf](https://drive.google.com/file/d/1tBba9iAqlB-qD4d12fK46Dymw9i32b5B/view?usp=drivesdk), cơ sở dữ liệu hiện có **36.544 đa giác tấm pin** (`modules`) chia vào `6` Block (`Block1`: 4.352 tấm; `Block2`: 13.500 tấm; `Block3`: 1.428 tấm; `Block4`: 13.560 tấm; `Block5`: 1.628 tấm; `Block6`: 2.076 tấm). Tuy nhiên, ở những chỗ ảnh Ortho bị méo nặng do đường ghép mảnh (ví dụ `Block1` bị khuyết các mã `ID_Pin` từ `4049` đến `4068`, hoặc các `string35`, `string36`, `string37` bị khuyết các tấm ở rìa méo), người vẽ đã bỏ trống.

Nếu cắt ngẫu nhiên toàn bộ bản đồ Ortho ra để train thì các vùng bị méo (không có polygon trong `.gpkg`) sẽ vô tình biến thành **nhãn âm giả (False Negative / Background)**, làm mô hình học sai rằng *"pin bị méo không phải là tấm pin"*. Để khắc phục triệt để và tận dụng 100% các file `.gpkg` sẵn có, nhóm áp dụng **Quy trình 3 bước khai thác GeoPackage**:

1. **Bước 1 — Tự động phát hiện "Lỗ khuyết lưới" (Grid Gap Masking) từ quy luật thứ tự `ID_Pin` và `Row_ID`:**
   - Trong mỗi `(layer, String_ID)`, các tấm pin chuẩn luôn xếp thành 4 hàng (`Row_ID` $\in \{1, 2, 3, 4\}$) với bước nhảy tâm $\Delta X \approx 1,13\text{ m}$ và $\Delta Y \approx 2,27\text{ m}$.
   - Viết script Python đọc trực tiếp bảng `modules` trong `.gpkg`: chỗ nào khoảng cách giữa 2 tấm liên tiếp lớn hơn $1,5 \times \Delta X$ hoặc thiếu hụt số lượng tấm trong chuỗi (không chia hết cho bội số cụm), thuật toán **Nội suy khung lưới (Grid Interpolation)** sẽ tự động dựng các đa giác dự kiến (Candidate Distorted Polygons) lấp vào đúng vị trí bị méo đó.
2. **Bước 2 — Chiến lược chia tập Train / Valid / Test theo Dải không gian độc lập (Spatial Block / Strip Split) chống rò rỉ dữ liệu:**
   - Không chia ngẫu nhiên từng ảnh cắt (vì các ô cắt trượt có chồng lấn). Thay vào đó, chia trực tiếp theo các `Block` hoặc dải không gian có vùng đệm cách ly `15m` (như đã thiết lập trong [CAM_NANG_TRIEN_KHAI_VA_DAP_AN_KY_THUAT_UAV_SOLAR_PV_REVISED_v2 (1).pdf](https://drive.google.com/file/d/1P5ClqStIuasImGBTfBke0u-b4BQEeQsL/view?usp=drivesdk) và [PV_Standardized_GIS_Database.gpkg](https://drive.google.com/file/d/1qcgtcOvR2M4JYYmgTGzGhQ9ujRfPJw2I/view?usp=drivesdk)):
     - **Tập Train (60%):** Dùng `Block2`, `Block4` (các vùng lưới đầy đủ) + **Nhân bản biến dạng tổng hợp (Synthetic Seamline & Elastic Distortion)**: lấy chính các ô ảnh Ortho chuẩn trong `.gpkg`, áp dụng biến đổi dịch chuyển đường ghép mảnh (Seamline Shear), uốn cong cục bộ (Thin-Plate Spline / Elastic Grid Deformation) và nhòe chuyển động để tạo ra hàng nghìn mẫu "pin bị méo có nhãn chính xác 100%".
     - **Tập Validation (15%):** Dùng `Block1`, `Block3` (có chứa cả tấm chuẩn và các tấm méo đã được gán nhãn bổ sung từ khung nội suy Bước 1).
     - **Tập Test độc lập (25%):** Dùng `Block5`, `Block6` và các file `.gpkg` của đợt bay `35m`/`42m` hoặc nhà máy khác (BIM 2, Thiên Tân 1.2) để đánh giá khách quan khả năng bắt tấm pin bị méo.
3. **Bước 3 — Hậu xử lý Nắn chỉnh lưới tô-pô (Topological Grid Snapping) khi suy luận:**
   - Khi mô hình AI nhận diện được các tấm pin (kể cả tấm méo với độ tự tin thấp hơn, ví dụ `conf = 0.25–0.50`), thuật toán [topological_snapping_regularization.py](https://drive.google.com/file/d/1FiSXT5eAtyZ4huFgacCchmxRN7WjKH5D/view?usp=drivesdk) sẽ dùng cấu trúc hàng/cột của các tấm lân cận để khôi phục khung hình học chuẩn và điền khuyết vào bản đồ số.

---

### 2.2. Câu hỏi 2: Dùng ngôn ngữ RUST để làm Web Quản trị nhằm tối ưu hiệu năng có được không? Nên chọn kiến trúc nào để vừa điểm cao vừa kịp tiến độ 17/01?

**Câu trả lời: RẤT TỐT VÀ LÀ ĐIỂM CỘNG LỚN VỀ KỸ THUẬT HỆ THỐNG, NHƯNG NÊN DÙNG KIẾN TRÚC LAI (RUST BACKEND CORE + PYTHON AI WORKER) THAY VÌ VIẾT 100% BẰNG RUST.**

Tại buổi bảo vệ ĐATN, hội đồng rất đánh giá cao các nhóm giải quyết được bài toán hiệu năng thực tế (vận hành hàng chục nghìn polygon và cắt mảnh ảnh GeoTIFF dung lượng hàng Gigabyte mà không bị treo RAM hay nghẽn cổ chai như Python thuần). Tuy nhiên, nếu viết cả phần huấn luyện AI và xử lý ma trận quang trắc bằng Rust từ đầu trong 9 tuần thì sẽ quá tải. Do đó, kiến trúc tối ưu nhất cho nhóm 3 người là:

| Thành phần hệ thống | Công nghệ lựa chọn | Lý do kỹ thuật để bảo vệ trước Hội đồng |
| :--- | :--- | :--- |
| **Web Backend & API Quản trị + Tile Server** | **Rust (`Axum` + `SQLx` + `Tokio`)** | Xử lý bất đồng bộ đa luồng cực nhanh, tiêu thụ RAM chỉ bằng `1/5 – 1/10` so với Python/Node.js; truy vấn `36.544` tấm pin từ PostGIS dưới dạng GeoJSON / Vector Tiles (MVT) chỉ mất `< 15 ms`; an toàn bộ nhớ (Memory-safe) và chịu tải cao khi stream hàng nghìn mảnh bản đồ (`orthophoto_87m` tiles) cùng lúc. |
| **Luồng Suy luận AI & Ánh xạ Không gian** | **Python Service (`PyTorch` / `Ultralytics` / `GDAL` / `SciPy`) hoặc `ONNX Runtime (ort)` trong Rust** | Giữ nguyên hệ sinh thái huấn luyện từ đầu (Train from scratch) bằng Python/PyTorch và các thuật toán ma trận DLT Homography, Mass-Spring, Hungarian ([dlt_hartley_homography.py](https://drive.google.com/file/d/1_8oJtLRvv7DSrOq4ILtSZ3bbEfVmquv2/view?usp=drivesdk), [hungarian_optimal_matching.py](https://drive.google.com/file/d/1zepV-bkcOp89dl6odrQm_am99FQpjW25/view?usp=drivesdk)). Khi xuất mô hình ra chuẩn `.onnx`, Rust có thể gọi trực tiếp qua thư viện `ort` hoặc giao tiếp với Python Worker qua hàng đợi Redis/gRPC. |
| **Cơ sở dữ liệu Không gian** | **PostgreSQL 16 + PostGIS 3.4 + Redis** | Lưu trữ hình học `POLYGON` hệ tọa độ `EPSG:32649`, đánh chỉ mục không gian **R-Tree (GiST)** giúp tìm kiếm tấm pin theo vùng chọn hoặc giao cắt không gian đạt độ phức tạp $O(\log N)$ thay vì quét vét cạn $O(N^2)$. |
| **Giao diện Web Quản trị (Frontend)** | **React / Next.js + TypeScript + MapLibre GL JS (hoặc Deck.gl)** | Kết xuất (Render) toàn bộ `36.544` đa giác tấm pin và lớp phủ nhiệt bằng tăng tốc phần cứng GPU (**WebGL**) mượt `60 FPS` ngay trên trình duyệt (khắc phục hoàn toàn hiện tượng giật lag khi vẽ quá 5.000 polygon của thư viện Leaflet DOM truyền thống trong bản thử nghiệm [index.html](https://drive.google.com/file/d/1z1rCRsPV9Ub1GWpnCqcvHCUR9J6XDiIO/view?usp=drivesdk)). |

---

## 3. KIẾN TRÚC 02 PIPELINE AI ĐỘC LẬP & THUẬT TOÁN ÁNH XẠ BẢN SAO SỐ

Hệ thống tách bạch rõ ràng **02 luồng huấn luyện (Training) độc lập từ đầu (From Scratch)** và kết nối với nhau ở tầng Bản sao số (Digital Twin) như sau:

```
====================================================================================================
LUỒNG 1: XÂY DỰNG BẢN ĐỒ SỐ GỐC TỪ ORTHOMOSAIC CHÍNH (85m - 87m)
====================================================================================================
[Bản đồ Ortho chính (.tif / .gpkg)]
       │
       ▼ (1) Cắt mảnh trượt (Sliding Window 1024x1024, overlap 20%) + Xoay chuẩn hướng Bắc (270°)
[Mô hình AI 1: Ortho-OBB Detector (Train từ đầu với Augmentation biến dạng đường ghép mảnh)]
       │
       ▼ (2) Hợp nhất khung xoay toàn cục (Rotational NMS / WBF trên tọa độ UTM EPSG:32649)
[Thuật toán Nắn chỉnh lưới tô-pô (Topological KD-Tree Grid Snapping & Nội suy tấm méo/khuyết)]
       │
       ▼ (3) Định danh tự động theo phân cấp: Block -> String_ID -> Row_ID -> ID_Pin
[CSDL Bản sao số (PostGIS): Bảng `solar_modules` chứa 100% tấm pin chuẩn & méo kèm `module_id`]

====================================================================================================
LUỒNG 2: CHẨN ĐOÁN LỖI TỪ ẢNH LẺ RGB + ẢNH NHIỆT (31m, 35m, 42m) & ÁNH XẠ LÊN `module_id`
====================================================================================================
[Ảnh lẻ RGB (_W.JPG)]                           [Ảnh nhiệt bức xạ R-JPEG (_T.JPG 640x512)]
       │                                                       │
       ▼ (A1) Mô hình AI 2A (Train từ đầu)                     ▼ (A2) Mô hình AI 2B (Train từ đầu)
[Nhận diện OBB từng tấm pin trên ảnh lẻ]         [Nhận diện OBB 4 loại lỗi nhiệt + Đọc nhiệt độ ΔT]
       │                                                       │
       └──────────────────────► (B) Ghép cặp Nội tại (Intra-pair RGB-Thermal Alignment) ◄──────┘
                               Xác định lỗi nhiệt nằm ở tấm pin nào trên khung hình chụp
                                                       │
                                                       ▼
             (C) Ánh xạ Không gian từ Ảnh sang Bản đồ số (8-DoF DLT Homography + Hartley Norm
                 + Mass-Spring Regularization + Thuật toán Hungarian Dual-Threshold Gating)
                                                       │
                                                       ▼
        [Gán chính xác lỗi vào `module_id` trên Bản đồ số -> Lưu vào bảng `thermal_inspections`]
```

### 3.1. Chi tiết Pipeline 1: Nhận diện Ortho chính & Bắt vùng pin bị méo
1. **Dữ liệu huấn luyện:** Cắt từ bản đồ Ortho `87m` ([thuannam19_master.gpkg](https://drive.google.com/file/d/1ytHofNRDcg9pFgoFGIhPRunAOChdTycN/view?usp=drivesdk)) và Ortho `35m`/`42m` ([SolarPanel_ExportOrtho](https://drive.google.com/drive/folders/1r9IpvEDOiUttqkTFHFfX1D4kgsqZk2y0)), kết hợp bộ dữ liệu [Roboflow solar-segment-obb](https://universe.roboflow.com/qu-nguyn-nh-s-workspace/solar-segment-obb).
2. **Kỹ thuật xử lý vùng pin bị méo (Điểm mới khoa học của Module 1):**
   - **Tăng cường dữ liệu biến dạng đặc thù (Seamline & Elastic Augmentation):** Mô phỏng chính xác lỗi ghép ảnh của Agisoft Metashape bằng cách cắt dịch nửa tấm pin theo đường chéo/ngang (Seamline Shift $5–15\text{ px}$) và biến dạng lưới đàn hồi (Elastic Transform) ngay trong quá trình huấn luyện từ đầu.
   - **Tối ưu hướng đối tượng (Orientation Normalization):** Kết quả thực nghiệm trong [CAM_NANG_TRIEN_KHAI_VA_DAP_AN_KY_THUAT_UAV_SOLAR_PV_REVISED_v2 (1).pdf](https://drive.google.com/file/d/1P5ClqStIuasImGBTfBke0u-b4BQEeQsL/view?usp=drivesdk) chứng minh việc chuẩn hóa góc xoay $270^\circ$ trước khi suy luận giúp tăng Recall từ **53,1% lên 82,7%**, và khi huấn luyện lại từ đầu với góc xoay đa hướng $[0^\circ, 360^\circ)$ đạt **Precision = 97,2%, Recall = 92,5%, mAP50 = 97,1%, mAP50-95 = 90,5%** ([Báo cáo Fine-Tuning](https://docs.google.com/document/d/1ztpRNhU2W2jl3e1B2wqTLsh_QMlupXDE1lqGaZXALM8/edit?usp=drivesdk&ouid=100220332396231512082)).
   - **Khôi phục cấu trúc lưới (Topological Grid Snapping):** Dựa trên đồ thị lân cận KD-Tree ($k=8$), các hộp dự đoán bị méo hoặc co ngắn diện tích ở đường ghép ảnh được nắn chỉnh về kích thước vật lý chuẩn ($1,13\text{ m} \times 2,27\text{ m}$) và tự động cấp phát `module_id` theo thứ tự `Block -> String -> Row -> ID_Pin`.

### 3.2. Chi tiết Pipeline 2: Nhận diện tấm pin ảnh lẻ + Phát hiện lỗi ảnh nhiệt & Ánh xạ `module_id`
1. **Nhánh 2A — Mô hình nhận diện tấm pin trên ảnh lẻ (Single-Image Panel Detector):**
   - Huấn luyện từ đầu trên tập nhãn ảnh lẻ tại [Dataset SolarGIS - RGB](https://drive.google.com/drive/folders/1x_gIlsOf94t2B0pgzuOu9bEyZ8ZZod-I) và [SolarGIS_Dataset_1](https://github.com/strawberrymilktea0604/SolarGIS_Dataset_1) để khắc phục hạn chế của file `best.pt` cũ ở rìa ảnh bị méo phối cảnh ống kính (radial/tangential lens distortion).
2. **Nhánh 2B — Mô hình nhận diện và phân loại 4 nhóm lỗi nhiệt trên ảnh nhiệt (Thermal Anomaly Detector):**
   - Huấn luyện từ đầu trên tập dữ liệu nhiệt tại [Dataset SolarGIS - Thermal](https://drive.google.com/drive/folders/13FbPVPVISPv3EP0hrTF-lqKFfJ2dJ8zl) và [SolarGIS_Dataset_2](https://github.com/strawberrymilktea0604/SolarGIS_Dataset_2) với 4 lớp lỗi chuẩn quốc tế IEC TS 62446-3:
     - `0: SingleHotSpot` (Điểm nóng đơn cục bộ).
     - `1: MultiHotSpot` (Điểm nóng đa vùng / hiệu ứng che bóng, bẩn bề mặt).
     - `2: Bypass` (Đoản mạch / kích hoạt đi-ốt Bypass làm nóng cả 1/3 tấm pin).
     - `3: ModuleOpenCircuit` (Hở mạch tấm pin hoặc chuỗi String).
   - Đồng thời giải mã luồng byte `APP3` 16-bit trong file R-JPEG (`655.360` bytes cho khung $640 \times 512$) để trích xuất nhiệt độ tuyệt đối ($T_{\max}, T_{\text{mean}}, \Delta T$) của từng vết lỗi.
3. **Ghép cặp Nội tại & Ánh xạ Không gian lên Bản đồ số (`module_id` Assignment):**
   - **Bước 1 (Ghép cặp Ảnh nhiệt $\leftrightarrow$ Tấm pin trên Ảnh lẻ):** Đưa tọa độ hộp lỗi trên ảnh nhiệt ($640 \times 512$) về cùng hệ quy chiếu khung nhìn với tấm pin phát hiện trên ảnh lẻ RGB thông qua ma trận nội chuẩn đồng trục camera kép (Dual-sensor Homography Calibration), xác định chính xác lỗi nhiệt nằm trong tấm pin nào của bức ảnh đó.
   - **Bước 2 (Chiếu từ Ảnh xuống Bản đồ số Ortho):** Thay vì dùng tọa độ GPS thô (sai số `155,37 cm`, Mean IoU chỉ đạt `10,02%` theo [PV_Comprehensive_Experimental_Benchmark_Summary.csv](https://drive.google.com/file/d/15OVOfc4eX9M6DjJ3A5DyFkuEl5e34Jkc/view?usp=drivesdk)), hệ thống thực hiện:
     - **Biến đổi phối cảnh 8 bậc tự do (8-DoF DLT Homography có chuẩn hóa Hartley):** Giảm số điều kiện ma trận $\kappa(A)$ từ $1,90 \times 10^{17}$ xuống $1.496,14$, kéo sai số RMSE 2D xuống **15,25 cm** (`14,46 cm` trên tập kiểm thử độc lập).
     - **Nắn chỉnh mạng lưới lò xo đàn hồi (Elastic Mass-Spring Regularization):** Đưa sai số RMSE 2D xuống còn **11,93 cm** (Median `7,20 cm`, Mean IoU đạt **80,96%**).
     - **Thuật toán ghép cặp tối ưu Hungarian hai ngưỡng (Dual-Threshold Gating):** Giải bài toán phân công tối ưu một-đối-một với hàm chi phí kết hợp khoảng cách tâm và IoU ($\text{IoU} \ge 0,50$, khoảng cách tâm $\Delta d < 52,4\text{ cm}$, biên quyết định $\ge 0,15$), đạt độ chính xác gán mã **`module_id` Top-1 = 99,86%** (`4.885 / 4.892` tấm khớp chính xác, tỷ lệ nhầm lẫn sang tấm bên cạnh chỉ `0,14%`).

---

## 4. THIẾT KẾ HỆ THỐNG PHẦN MỀM THEO CHUẨN 6 BƯỚC PTTKHT & KIẾN TRÚC

Để đáp ứng trọn vẹn yêu cầu của hội đồng đối với đề tài **"Xây dựng hệ thống phần mềm + Tích hợp AI"**, phần mềm Quản lý Bản sao số được thiết kế tuân thủ nghiêm ngặt **06 bước Phân tích Thiết kế Hệ thống (PTTKHT)**:

### Bước 1: Phân tích nghiệp vụ, Phân rã chức năng (FDD) & Đặc tả Use Case
Hệ thống phục vụ 03 nhóm tác nhân chính (**Actors**):
1. **Quản trị viên hệ thống (System Admin):** Quản lý danh mục nhà máy (Plant), phân khu (Block/String), khởi tạo Bản đồ số gốc (Master Ortho & GeoPackage), quản lý người dùng và phân quyền.
2. **Kỹ sư Khảo sát & AI (UAV/AI Engineer):** Tạo đợt bay khảo sát mới (Flight Campaign), tải lên bản đồ Ortho hoặc lô ảnh lẻ RGB + Ảnh nhiệt, kích hoạt Pipeline AI 1 (cập nhật lưới tấm pin) hoặc Pipeline AI 2 (nhận diện lỗi nhiệt & ánh xạ `module_id`), kiểm duyệt (QC) các ca biên (Ambiguous/Flagged).
3. **Kỹ sư Vận hành & Bảo trì (O&M Technician / Viewer):** Tra cứu bản đồ số Digital Twin theo đợt bay, lọc danh sách `module_id` bị lỗi nhiệt, xem lịch sử biến thiên nhiệt độ của 1 tấm pin qua nhiều đợt bay, xuất phiếu công tác bảo trì (PDF/CSV/GeoPackage).

**Sơ đồ phân rã chức năng (Functional Decomposition):**
- `1.0` Quản lý Bản sao số Nhà máy (Plant & Master Digital Twin Management)
  - `1.1` Nhập/Xuất bản đồ Ortho gốc & Tệp `.gpkg` chuẩn hóa
  - `1.2` Chạy Pipeline AI 1: Phát hiện tấm pin chuẩn/méo & Đánh mã `module_id` tự động
  - `1.3` Hiệu chỉnh lưới tô-pô & Quản lý phiên bản lưới (Grid Versioning)
- `2.0` Quản lý Chiến dịch Bay & Chẩn đoán Lỗi Nhiệt (Flight Campaign & AI Inspection)
  - `2.1` Tải lên lô ảnh lẻ RGB (`_W.JPG`) và Ảnh nhiệt R-JPEG (`_T.JPG`) kèm trích xuất EXIF/RTK
  - `2.2` Chạy Pipeline AI 2: Nhận diện tấm pin ảnh lẻ + Phát hiện 4 loại lỗi nhiệt
  - `2.3` Ánh xạ không gian (Homography + Mass-Spring + Hungarian) gắn lỗi vào `module_id`
- `3.0` Bản đồ số Tương tác & Báo cáo Bảo trì (WebGIS Visualization & O&M Analytics)
  - `3.1` Hiển thị bản đồ đa lớp WebGL (Lớp ảnh Ortho, Lớp lưới `36.544` tấm pin, Lớp điểm nóng nhiệt)
  - `3.2` Tra cứu chi tiết từng `module_id` (Xem song song ảnh cắt RGB – Ảnh nhiệt – Nhiệt độ $\Delta T$)
  - `3.3` So sánh lịch sử lỗi qua các đợt bay & Xuất báo cáo kỹ thuật

### Bước 2: Sơ đồ Use Case tổng thể (Use Case Diagram)
```
+-----------------------------------------------------------------------------------+
|                   HỆ THỐNG WEB QUẢN TRỊ BẢN SAO SỐ SOLARGIS                       |
|                                                                                   |
|  [Quản trị viên] ---> (UC01: Khởi tạo Nhà máy & Nạp Master Ortho / .gpkg)        |
|        |------------> (UC02: Kích hoạt Pipeline AI 1 - Nhận diện Pin chuẩn/méo)   |
|                                                                                   |
|  [Kỹ sư UAV/AI] ----> (UC03: Tạo Đợt bay & Tải lên Cặp ảnh lẻ RGB + Ảnh nhiệt)    |
|        |------------> (UC04: Chạy Pipeline AI 2 - Bắt lỗi nhiệt & Ánh xạ ID)      |
|        |------------> (UC05: Kiểm duyệt QC các tấm pin vùng biên / độ tự tin thấp)|
|                                                                                   |
|  [Kỹ sư O&M] -------> (UC06: Tương tác Bản đồ số Digital Twin & Lọc lỗi theo ID)  |
|        |------------> (UC07: Xem đối chiếu lịch sử các đợt bay & Xuất báo cáo)    |
+-----------------------------------------------------------------------------------+
```

### Bước 3: Thiết kế Cơ sở dữ liệu (ERD) & Luồng luân chuyển dữ liệu AI qua các bảng
Hệ thống sử dụng **PostgreSQL + PostGIS** làm CSDL quan hệ – không gian chính, kết hợp **Redis** (hàng đợi tác vụ AI & cache tile) và tùy chọn **Qdrant / MongoDB** (lưu vector đặc trưng hình ảnh tấm pin & log JSON thô của mô hình để tìm kiếm tương đồng hoặc truy vết huấn luyện).

#### Sơ đồ Thực thể Liên kết (ERD Tổng thể – 7 bảng cốt lõi):
1. `solar_plants` (`id` PK, `name`, `location_province`, `crs_epsg` DEFAULT 32649, `aoi_geom` GEOMETRY(Polygon, 32649), `created_at`)
2. `plant_blocks_strings` (`id` PK, `plant_id` FK, `block_code` VARCHAR [Block1..6], `string_code` VARCHAR [string1..39], `row_count` INT)
3. `solar_modules` *(Bảng định danh gốc Digital Twin — 36.544 bản ghi tại Thuận Nam 19)*:
   - `module_id` (PK, VARCHAR, ví dụ `block1_string4_00458`)
   - `plant_id` (FK), `block_string_id` (FK), `row_id` (SMALLINT 1..4), `pin_index` (INT `ID_Pin`)
   - `geom` (GEOMETRY(Polygon, 32649) — có chỉ mục không gian `GIST (geom)`)
   - `centroid_x` (DOUBLE PRECISION), `centroid_y` (DOUBLE PRECISION)
   - `is_distorted_recovered` (BOOLEAN — đánh dấu tấm pin vùng méo được AI 1 + Topological Snapping khôi phục)
   - `current_health_status` (VARCHAR: `NORMAL`, `SINGLE_HOTSPOT`, `MULTI_HOTSPOT`, `BYPASS`, `OPEN_CIRCUIT`)
4. `flight_campaigns` *(Quản lý các lần bay khảo sát)*:
   - `id` (PK, UUID), `plant_id` (FK), `campaign_name`, `flight_date`, `altitude_m` (FLOAT: 87.0, 42.0, 35.0, 31.0), `gsd_cm` (FLOAT), `ortho_tif_path`, `status` (`UPLOADED`, `PROCESSING_AI`, `COMPLETED`, `FAILED`)
5. `raw_image_pairs` *(Lưu cặp ảnh lẻ RGB và Ảnh nhiệt của từng lần bay)*:
   - `id` (PK, UUID), `campaign_id` (FK), `rgb_filename` (`_W.JPG`), `thermal_filename` (`_T.JPG`), `gps_x_utm`, `gps_y_utm`, `altitude_m`, `gimbal_yaw`, `gimbal_pitch`, `rtk_fix_status` (SMALLINT)
6. `ai_raw_detections` *(Lưu kết quả bóc tách thô từ AI trước và sau khi ghép cặp nội tại)*:
   - `id` (PK, UUID), `image_pair_id` (FK), `pipeline_type` (`ORTHO_PANEL`, `SINGLE_RGB_PANEL`, `THERMAL_FAULT`), `class_label`, `confidence` (FLOAT), `obb_pixel_coords` (JSONB), `temp_max_c` (FLOAT), `temp_delta_c` (FLOAT)
7. `module_inspection_logs` *(Bảng kết quả ánh xạ cuối cùng từ AI lên Bản sao số)*:
   - `id` (PK, UUID), `campaign_id` (FK), `module_id` (FK $\rightarrow$ `solar_modules.module_id`), `image_pair_id` (FK), `detection_id` (FK)
   - `fault_class` (`SingleHotSpot`, `MultiHotSpot`, `Bypass`, `ModuleOpenCircuit`)
   - `projected_geom` (GEOMETRY(Polygon, 32649)), `spatial_iou` (FLOAT), `centroid_error_cm` (FLOAT), `hungarian_margin` (FLOAT)
   - `qc_verified` (BOOLEAN), `crop_rgb_url`, `crop_thermal_url`, `created_at`

#### Giải trình câu hỏi Hội đồng: *"Dữ liệu AI luân chuyển trong CSDL qua các bảng nào?"*
- **Khi chạy Pipeline 1 (Bản đồ Ortho chính):** Người dùng tạo đợt bay `87m` trong bảng `flight_campaigns` $\rightarrow$ Модуль AI 1 quét ảnh Ortho, ghi các hộp dự đoán thô vào `ai_raw_detections` $\rightarrow$ Thuật toán Topological Snapping khớp và cập nhật/bổ sung các tấm pin (kể cả tấm méo) vào bảng gốc `solar_modules` kèm cờ `is_distorted_recovered = TRUE`.
- **Khi chạy Pipeline 2 (Ảnh lẻ + Ảnh nhiệt):** Hệ thống đọc EXIF từng cặp ảnh `_W.JPG` & `_T.JPG` nạp vào bảng `raw_image_pairs` $\rightarrow$ AI 2A và AI 2B suy luận song song, ghi tọa độ pixel của tấm pin và vết lỗi nhiệt (kèm nhiệt độ $T_{\max}, \Delta T$) vào bảng `ai_raw_detections` $\rightarrow$ Khối Ánh xạ Không gian (DLT Homography + Mass-Spring + Hungarian) đối chiếu với chỉ mục R-Tree của bảng `solar_modules`, tìm ra đúng `module_id` có $\text{IoU} \ge 0,50$ và ghi bản ghi chẩn đoán vào `module_inspection_logs`, đồng thời cập nhật trạng thái mới nhất `current_health_status` tại bảng `solar_modules` để hiển thị ngay màu cảnh báo trên Web.

### Bước 4: Sơ đồ Hoạt động (Activity Diagram) & Sơ đồ Tuần tự (Sequence Diagram)
- **Sơ đồ tuần tự luồng Chẩn đoán & Ánh xạ lỗi nhiệt (UC04):**
  `Kỹ sư UAV (Web UI)` $\xrightarrow{\text{1. Upload cặp ảnh RGB/Nhiệt}}$ `Rust API Gateway (Axum)` $\xrightarrow{\text{2. Lưu metadata}}$ `PostGIS (raw_image_pairs)` $\xrightarrow{\text{3. Đẩy job ID}}$ `Redis Queue` $\xrightarrow{\text{4. Nhận job}}$ `AI & Spatial Worker` $\xrightarrow{\text{5. Chạy YOLO-OBB 2A & 2B}}$ `Ghi ai_raw_detections` $\xrightarrow{\text{6. Chiếu Homography + Hungarian khớp R-Tree}}$ `PostGIS (module_inspection_logs & solar_modules)` $\xrightarrow{\text{7. Phát sự kiện WebSocket/SSE}}$ `Web UI cập nhật bản đồ màu đỏ/cam tại đúng module_id`.

### Bước 5: Sơ đồ Kiến trúc Hệ thống (Clean Architecture & Dataflow)
Hệ thống áp dụng **Clean Architecture 4 tầng** rõ ràng:
1. **Presentation Layer:** Next.js + MapLibre GL JS (WebGL Canvas 60 FPS) + Biểu đồ thống kê đợt bay.
2. **Application / Use Case Layer (Rust Axum Core):** Điều phối nghiệp vụ đợt bay, quản lý phiên làm việc, phân trang dữ liệu lớn, phát luồng Tile Server (`orthophoto_87m` & Vector Tiles).
3. **Domain / Spatial & AI Engine Layer:** Chứa thực thể lõi (`SolarModule`, `ThermalAnomaly`, `HomographyMatrix`) và giao diện trừu tượng gọi sang dịch vụ AI/Hình học.
4. **Infrastructure Layer:** PostgreSQL/PostGIS (`rtree_modules_geom`), Redis Task Queue, MinIO/Local Object Storage lưu ảnh cắt minh chứng.

---

## 5. ĐÁNH GIÁ ĐỘ PHỨC TẠP THUẬT TOÁN & BỘ CÂU TRẢ LỜI PHẢN BIỆN AI TRƯỚC HỘI ĐỒNG

*(Đây là phần "vũ khí" cốt lõi rút ra từ kinh nghiệm đợt bảo vệ 25–26/06/2026 để đạt mức **Exemplary 8.5–10.0** của CLO1, CLO2, CLO3).*

### 5.1. Đánh giá Độ phức tạp Thuật toán (Algorithmic Complexity Evaluation)
Trong báo cáo và slide phần Thực thi, nhóm chứng minh tính tối ưu của giải thuật bằng bảng phân tích độ phức tạp toán học thực nghiệm trên $N = 36.544$ tấm pin chuẩn và $M = 5.092$ hộp phát hiện AI:

| Bài toán con trong Pipeline | Giải thuật ngây thơ (Naive Approach) | Giải thuật đề xuất trong ĐATN | Độ phức tạp Thời gian & Không gian | Hiệu quả thực tế trên tập Thuận Nam 19 |
| :--- | :--- | :--- | :--- | :--- |
| **1. Tìm tấm pin ứng viên trên Bản đồ số để gán `module_id`** | Quét vét cạn tính IoU giữa từng hộp dự đoán $M$ với toàn bộ $N$ tấm pin trong CSDL: **$O(M \times N)$** ($\approx 1,86 \times 10^8$ phép tính giao cắt đa giác). | Truy vấn vùng bao **R-Tree (`GiST`)** kết hợp cây **KD-Tree** không gian 2D: Xây cây $O(N \log N)$, truy vấn $k$ láng giềng gần nhất trong bán kính $r = 1,5\text{ m}$: **$O(M \log N)$**. | Thời gian: **$O((N + M) \log N)$**<br>Không gian: **$O(N)$** | Giảm số phép tính IoU hình học từ **186 triệu** xuống còn **$\approx 40.700$ phép tính** (tăng tốc hơn **4.500 lần**, chạy xong trong $< 0,4\text{ giây}$). |
| **2. Nắn chỉnh lưới đàn hồi (Mass-Spring Grid Regularization)** | Giải hệ phương trình ma trận đặc kích thước $(2M \times 2M)$ bằng khử Gauss: **$O(M^3)$**. | Biểu diễn đồ thị lò xo thưa (Sparse Graph với $|E| = 14.912$ cạnh láng giềng, bậc trung bình $d \le 4$) và giải tối ưu lặp L-BFGS / Conjugate Gradient: **$O(I \cdot |E|) = O(I \cdot M)$** (với $I \approx 50$ vòng lặp). | Thời gian: **$O(I \cdot M)$**<br>Không gian: **$O(M + |E|)$** | Xử lý `5.092` tâm tấm pin và `14.912` cạnh lò xo trong **$< 0,8\text{ giây}$**, kéo sai số RMSE từ `15,25 cm` xuống **`11,93 cm`**. |
| **3. Ghép cặp tối ưu Một-đối-Một (Hungarian Optimal Assignment)** | Chạy thuật toán Kuhn-Munkres trên toàn ma trận đặc $(M \times N)$: **$O(M^2 \cdot N)$** — Không khả thi khi $N = 36.544$. | **Phân rã cụm không gian theo `Block/String` + Cắt tỉa ma trận thưa (Sparse Dual-Threshold Gating $\Delta d < 52,4\text{ cm}$):** Chia thành $C = 148$ chuỗi độc lập, mỗi chuỗi có $m_c \approx 35$ tấm: **$O(\sum_{c=1}^{C} m_c^3) \approx O(M \cdot \bar{m}^2)$**. | Thời gian: **$O(M \cdot \bar{m}^2)$** ($\bar{m} \ll M$)<br>Không gian: **$O(M \cdot k)$** | Thời gian ghép cặp toàn khu vực chỉ mất **$\approx 0,15\text{ giây}$**, đạt độ chính xác gán mã **`module_id` = 99,86%**. |
| **4. Ước lượng Ma trận Phối cảnh 8-DoF DLT Homography** | Giải SVD trực tiếp trên tọa độ UTM thô ($X \sim 2,65 \times 10^5, Y \sim 1,26 \times 10^6$) gây suy biến số học ($\kappa(A) = 1,90 \times 10^{17}$). | **Chuẩn hóa tâm và tỷ lệ Hartley (Hartley Isotropic Scaling)** đưa tọa độ về gốc $(0,0)$ khoảng cách trung bình $\sqrt{2}$ trước khi phân rã SVD trên ma trận $(2K \times 9)$ kết hợp RANSAC: **$O(R_{\text{iter}} + K)$**. | Thời gian: **$O(K)$** (với $K$ điểm neo)<br>Không gian: **$O(K)$** | Giảm số điều kiện ma trận $\kappa(A)$ xuống **$1.496,14$** (cải thiện $10^{13}$ lần), giữ vững độ ổn định số học tuyệt đối. |

---

### 5.2. Định hướng Điểm cộng Triển khai (Không cần thiết bị phần cứng Edge)
Theo rút kinh nghiệm bảo vệ, với đề tài không dùng phần cứng nhúng (Jetson/Raspberry Pi), nhóm tạo **03 điểm cộng thực chiến tương đương** để chinh phục Hội đồng:
1. **Triển khai mô hình AI đa định dạng tối ưu hóa phần cứng máy chủ/máy trạm (ONNX Runtime / TensorRT FP16):** Xuất cả 2 mô hình đã train từ đầu sang chuẩn `.onnx` và `.engine` (FP16), đo kiểm thực tế tốc độ suy luận (FPS / ms trên mỗi ô ảnh $1024 \times 1024$ và $640 \times 640$), mức chiếm dụng VRAM và RAM trước và sau khi tối ưu hóa.
2. **Xây dựng Tile Server & Vector MapEngine hiệu năng cao bằng Rust + WebGL:** Chứng minh trực tiếp trên giao diện Web lúc bảo vệ: tải bản đồ trực giao hàng trăm MB và bật cùng lúc **36.544 đa giác tấm pin** lên màn hình, zoom/pan ở tốc độ **60 FPS** mà không giật lag.
3. **Kiểm chứng chéo trên nhiều độ cao bay (`31m`, `35m`, `42m`, `87m`) và nhiều nhà máy thực tế tại Ninh Thuận:** Có bảng đối chứng số liệu thực tế tại Thuận Nam 19, BIM 2, Thuận Nam Đức Long, Thiên Tân 1.2 thay vì chỉ chạy trên tập ảnh mẫu tải trên mạng.

---

### 5.3. Kịch bản Trả lời Trực diện Các Câu hỏi Phản biện AI của Thầy Cô

#### Câu hỏi 1: *"Tại sao nhóm lại chọn kiến trúc YOLO-OBB (YOLO11-OBB / YOLOv8-OBB) làm mô hình chủ đạo? Trình bày dựa trên phần cứng thực tế (CPU, GPU, VRAM) và đặc thù bài toán!"*
- **Trả lời trọng tâm (Không văn vở):**
  1. **Về đặc thù hình học của dữ liệu UAV điện mặt trời:** Các dãy tấm pin mặt trời trên ảnh UAV và ảnh trực giao thường nằm nghiêng một góc $\theta$ so với trục ảnh và xếp sát khít nhau (khoảng hở giữa 2 tấm chỉ từ `2–5 cm`, tương ứng `1–2 pixel` ở độ cao `87m`). Nếu dùng hộp giới hạn ngang truyền thống (**Horizontal Bounding Box – HBB**), các hộp sẽ chồng lấn lên nhau rất mạnh, khiến thuật toán lọc hộp trùng (**NMS**) xóa nhầm các tấm pin nằm cạnh nhau. Bắt buộc phải dùng **Oriented Bounding Box (OBB – 5 tham số $x, y, w, h, \theta$)** để bao khít từng tấm pin theo đúng góc nghiêng thực tế.
  2. **Về ràng buộc Phần cứng huấn luyện và vận hành (GPU Tesla T4 16GB VRAM / RTX 3060–4060 8–12GB VRAM):**
     - Khi huấn luyện ảnh cắt Ortho độ phân giải cao ($1024 \times 1024$ px) chứa mật độ dày đặc từ `150 đến 300 tấm pin trên một bức ảnh`, bộ nhớ VRAM tiêu tốn chủ yếu ở các tầng Feature Pyramid và bộ nhớ lưu trữ Anchor/Proposal.
     - Với bản **YOLO11s-OBB / YOLOv8s-OBB** (`~11,4 triệu` tham số, `~29 GFLOPs`) hoặc **YOLO11l-OBB** (`~26,2 triệu` tham số): khi train ở kích thước $1024 \times 1024$, `batch_size = 8–16` chỉ chiếm **6,8 GB – 11,2 GB VRAM**, hoàn toàn vừa vặn trên 1 GPU tầm trung (12–16 GB VRAM) với tốc độ suy luận đạt **12–22 ms/ảnh** (tức quét xong toàn bộ bản đồ nhà máy `36.544` tấm chỉ trong **vài chục giây**).

#### Câu hỏi 2: *"Em hãy trình bày các mô hình cũ hơn hoặc các họ mô hình khác và cho biết vì sao chúng KHÔNG phù hợp với dự án này?"*
- **Bảng khảo sát & đối sánh thực nghiệm để đưa vào Slide và Báo cáo:**

| Họ mô hình khảo sát | Cơ chế hoạt động | Lý do KHÔNG phù hợp với bài toán Khảo sát Pin Mặt trời UAV của dự án |
| :--- | :--- | :--- |
| **1. Các mô hình HBB cũ (YOLOv5, YOLOv7, Faster R-CNN chuẩn)** | Dự đoán khung chữ nhật đứng $(x_{\min}, y_{\min}, x_{\max}, y_{\max})$ không có góc xoay $\theta$. | Khi tấm pin nghiêng $15^\circ–45^\circ$, diện tích hộp HBB chứa tới $35\%–50\%$ nền đất thừa và đè lên tấm pin bên cạnh. Khi tính giao cắt (IoU) để ánh xạ vào `module_id` trên bản đồ số, sai số hình học tăng vọt và NMS loại bỏ nhầm tới $>30\%$ số tấm pin. |
| **2. Mô hình R-CNN 2 giai đoạn có hướng (Oriented R-CNN, RoI Transformer, Gliding Vertex)** | Giai đoạn 1 sinh vùng đề xuất xoay (Rotated RPN), giai đoạn 2 phân loại và hồi quy khung. | Với mật độ `200–300 tấm pin/ảnh`, tầng RPN phải sinh hàng nghìn vùng đề xuất xoay, làm VRAM vọt lên **$> 18\text{ GB}$** ở kích thước $1024 \times 1024$ và tốc độ suy luận chậm (**120–250 ms/ảnh**, chậm hơn YOLO-OBB từ **8 đến 12 lần**), gây nghẽn khi xử lý lô hàng nghìn ảnh lẻ UAV. |
| **3. Mô hình Phân vùng thực thể (Mask R-CNN, Cascade Mask R-CNN, SAM)** | Dự đoán mặt nạ pixel (Pixel-level Mask) cho từng tấm pin. | Tốn chi phí tính toán mặt nạ cho từng đối tượng; đặc biệt ở vùng ảnh Ortho bị **méo đường ghép mảnh (seamline)**, mặt nạ phân vùng bị đứt gãy thành 2 mảnh rời nhau hoặc biến dạng đa giác lồi lõm, rất khó xác định 4 đỉnh chuẩn để tính ma trận Homography và khớp vào lưới `.gpkg`. |
| **4. Mô hình Transformer (DETR, Deformable DETR, RT-DETR)** | Dùng cơ chế Self-Attention toàn cục và tập truy vấn đối tượng cố định ($N_{\text{queries}} = 300$). | Chi phí phức tạp bậc hai theo độ phân giải ảnh $O((H \times W)^2)$ khi nâng lên $1024 \times 1024$; hơn nữa giới hạn số lượng `300 queries` mặc định dễ bị bão hòa khi một khung ảnh Ortho chứa trên `250–350` tấm pin dày đặc, hội tụ rất chậm khi train từ đầu trên tập dữ liệu chuyên biệt. |
| **5. Mô hình Одно-giai-đoạn xoay đời cũ (Rotated RetinaNet, R3Det)** | Dùng Anchor xoay đặt sẵn (ví dụ 6 góc $\times$ 3 tỷ lệ = 18 anchors/điểm ảnh). | Phải nhân số lượng Anchor lên gấp nhiều lần gây mất cân bằng mẫu âm/dương nghiêm trọng và sai số lượng tử hóa góc; trong khi **YOLO-OBB (Anchor-free + ProbIoU Loss)** dự đoán trực tiếp phân phối khoảng cách 4 cạnh và góc xoay liên tục dựa trên khoảng cách Bhattacharyya của phân phối Gaussian 2D, giúp hội tụ nhanh và chính xác hơn hẳn. |

---

## 6. MA TRẬN THAM CHIẾU CHUẨN ĐẦU RA (CLO) – HƯỚNG CHỨNG MINH & HƯỚNG MỞ

Bảng dưới đây ánh xạ trực tiếp đề tài với **5 CLO của Đề cương học phần ĐATN ngành KHMT (`7724162`)** và **8 CLO chung của Trường ĐHXDHN (`483/QĐ-ĐHXDHN`)**, kèm minh chứng cụ thể để đạt điểm tối đa (**Mức 4 – Exemplary: 8.5 – 10.0**):

| Mã CLO (HP `7724162` & QĐ `483`) | Nội dung yêu cầu của Chuẩn đầu ra | Hướng chứng minh cụ thể trong Báo cáo & Sản phẩm ĐATN này | Hướng mở phát triển (Future Work & Mở rộng nghiên cứu) |
| :--- | :--- | :--- | :--- |
| **`CLO1` (HP)**<br>*(Tương ứng `CLO1`, `CLO3` QĐ 483)* | Phân tích có hệ thống bài toán KHMT bằng toán học, KHTN và kiến thức chuyên ngành; đánh giá độ phức tạp thuật toán $O(n)$, ma trận, xác suất, quy luật vật lý. | 1. **Toán học & Hình học xạ ảnh:** Trình bày rõ hệ phương trình biến đổi phối cảnh 8-DoF DLT Homography, chuẩn hóa đẳng hướng Hartley ($\kappa(A)$ giảm từ $1,90 \times 10^{17}$ xuống $1.496,14$), hàm mất mát **ProbIoU** (khoảng cách Bhattacharyya giữa 2 elip hiệp phương sai Gaussian) và bài toán tối ưu tổ hợp Hungarian.<br>2. **Vật lý nhiệt học:** Giải mã bức xạ nhiệt 16-bit R-JPEG và độ lệch nhiệt độ $\Delta T$.<br>3. **Độ phức tạp thuật toán:** Bảng chứng minh giảm độ phức tạp từ $O(M \times N)$ xuống $O(M \log N)$ nhờ R-Tree/KD-Tree và giải hệ thưa $O(I \cdot M)$ cho mạng lò xo Mass-Spring. | Mở rộng mô hình toán học sang bài toán **chiếu ngược tia 3D (3D Ray-Casting trên mô hình số độ cao DEM `.tif` / đám mây điểm `.laz`)** cho các nhà máy điện mặt trời lắp trên địa hình đồi dốc lớn hoặc mái nhà xưởng phức tạp không đồng phẳng. |
| **`CLO2` (HP)**<br>*(Tương ứng `CLO2`, `CLO5`, `CLO7` QĐ 483)* | Thiết kế và hiện thực hóa giải pháp đáp ứng yêu cầu, khả thi, hiệu quả; tuân thủ PTTKHT (UML, ERD, Clean Architecture) và tích hợp yếu tố đạo đức, môi trường, an toàn xã hội. | 1. **Thiết kế PTTKHT chuẩn:** Đầy đủ 6 bước (Phân rã chức năng, Use Case, ERD 7 bảng PostGIS có chỉ mục `GIST`, Sequence/Activity Diagram, Clean Architecture kết hợp Rust Axum + MapLibre WebGL).<br>2. **Cơ chế an toàn & Trách nhiệm nghề nghiệp (Đạo đức AI):** Thiết kế cơ chế **Cổng kiểm soát hai ngưỡng (Dual-Threshold Gating & QC Flagging)**: những tấm pin ở rìa có độ tự tin thấp hoặc biên quyết định $< 0,15$ được hệ thống tự động gắn cờ `Cần kỹ sư kiểm duyệt (QC Pending)` thay vì tự ý kết luận sai gây lãng phí nhân công tháo lắp ngoài công trường; đóng góp trực tiếp vào chuyển đổi năng lượng xanh bền vững. | Tích hợp quy trình tự động xuất lộ trình bay kiểm tra lại (Re-inspection Waypoint `.kmz`) cho máy bay DJI đối với riêng các cụm `module_id` bị nghi ngờ lỗi nặng và kết nối trực tiếp với hệ thống SCADA/ERP của nhà máy điện. |
| **`CLO3` (HP)**<br>*(Tương ứng `CLO1`, `CLO2`, `CLO7` QĐ 483)* | Vận dụng hiệu quả kiến thức Trí tuệ nhân tạo: khảo sát lựa chọn mô hình theo phần cứng, **huấn luyện từ đầu (Train from scratch)**, tối ưu hóa và đánh giá bằng độ đo định lượng thực tế. | 1. **Huấn luyện từ đầu 100%:** Huấn luyện độc lập 2 pipeline (AI 1 bắt tấm pin chuẩn/méo trên Ortho; AI 2A bắt tấm pin ảnh lẻ + AI 2B bắt 4 loại lỗi nhiệt) trên tập dữ liệu thực tế Ninh Thuận đã chia theo dải không gian chống rò rỉ dữ liệu (Footprint-Disjoint Split).<br>2. **Khảo sát & Lý giải phần cứng:** Bảng so sánh thực nghiệm giữa các kiến trúc (HBB vs. Oriented R-CNN vs. Mask R-CNN vs. DETR vs. YOLO-OBB) theo VRAM, GFLOPs, FPS.<br>3. **Độ đo định lượng toàn diện:** Báo cáo đầy đủ Precision, Recall, mAP@50, mAP@50:95, RMSE 2D (`11,93 cm`), Mean IoU (`80,96%`) và Top-1 `module_id` Accuracy (`99,86%`). | 1. Xây dựng mô hình **Đa phương thức hợp nhất sớm (Early/Mid-Fusion RGB + Thermal Cross-Attention)** để phát hiện các lỗi ngầm nhẹ.<br>2. Lưu trữ vector đặc trưng của từng tấm pin vào **Vector Database (Qdrant)** để truy vấn tương đồng các mẫu lỗi hiếm và dự báo tốc độ lão hóa tấm pin theo chuỗi thời gian (Time-series Prognostics). |
| **`CLO4` (HP)**<br>*(Tương ứng `CLO4`, `CLO6` QĐ 483)* | Trình bày hiệu quả đồ án qua báo cáo văn bản chuẩn thể thức, slide bảo vệ tách bạch Đầu vào/Đầu ra – Thực thi, thuyết trình và trả lời phản biện. | 1. **Báo cáo & Slide:** Tuân thủ đúng giới hạn $\le 150$ trang của Quy định `483/QĐ-ĐHXDHN`; Slide Mở đầu chỉ nêu Đầu vào/Đầu ra; Slide Triển khai trình bày rõ thuật toán, độ phức tạp và luồng dữ liệu qua các bảng CSDL.<br>2. **Demo trực quan:** Kịch bản chạy thử trực tiếp từ lúc nạp ảnh đến khi bản đồ Digital Twin báo đỏ tại đúng `module_id` bị lỗi. | Chuẩn hóa kết quả nghiên cứu thành bài báo khoa học công bố tại hội nghị quốc gia/quốc tế về Viễn thám & AI trong Năng lượng tái tạo và đóng gói bộ dữ liệu chuẩn công bố mã nguồn mở. |
| **`CLO5` (HP)**<br>*(Tương ứng `CLO4`, `CLO6`, `CLO8` QĐ 483)* | Làm việc nhóm hiệu quả: phân chia 3 module độc lập, phối hợp nhịp nhàng qua công cụ quản lý số (Git, nhánh PR, nhật ký tuần) và định hướng khởi nghiệp/ứng dụng thực tiễn. | 1. **Phân quyền 3 thành viên rõ ràng:** Mỗi thành viên làm chủ 1 Module độc lập (Module 1: AI Ortho & Lưới GIS; Module 2: AI Ảnh lẻ/Ảnh nhiệt & Ánh xạ không gian; Module 3: Backend Rust/PostGIS & Web Digital Twin) có giao diện kết nối (API/Schema Contract) thống nhất.<br>2. **Quản trị số:** Quản lý mã nguồn trên GitHub theo chuẩn GitFlow, cập nhật Nhật ký thực hiện hàng tuần chấm điểm quá trình. | Phát triển thành nền tảng phần mềm dịch vụ (**SaaS – SolarGIS Inspection Cloud**) cung cấp dịch vụ kiểm định định kỳ bằng UAV cho các chủ đầu tư điện mặt trời và điện áp mái tại Việt Nam. |

---

## 7. PHÂN CÔNG NHIỆM VỤ 03 THÀNH VIÊN & LỘ TRÌNH CHI TIẾT (`16/11/2026` – `17/01/2027`)

### 7.1. Nguyên tắc chia việc cho 03 người (Độc lập từng Module – Dễ ghép nối – Dễ bảo vệ cá nhân)
Theo Điều 7 Quyết định `483/QĐ-ĐHXDHN`, đề tài nhóm 3 sinh viên phải chỉ rõ phần việc chung và **module độc lập của từng cá nhân** để Hội đồng chấm điểm riêng từng người:

| Thành viên | Tên Module phụ trách độc lập | Trọng tâm công việc kỹ thuật | Đầu ra bàn giao (Deliverables cá nhân) |
| :--- | :--- | :--- | :--- |
| **Thành viên 1 (TV1)**<br>*(Trưởng nhóm – Phụ trách Module 1)* | **Module 1: Pipeline AI Nhận diện Bản đồ Ortho chính, Xử lý vùng pin méo & Chuẩn hóa Lưới Bản sao số (`.gpkg`)** | 1. Khai thác `thuannam19_master.gpkg` và các file `Block1..6.gpkg`: viết thuật toán phát hiện lỗ khuyết lưới (Grid Gap Interpolation) tại các vùng pin bị méo chưa vẽ.<br>2. Tạo bộ dữ liệu cắt mảnh Ortho + Augmentation giả lập biến dạng đường ghép mảnh (Seamline/Elastic Distortion) và **huấn luyện từ đầu (Train from scratch)** mô hình AI 1 (Ortho-OBB Detector).<br>3. Xây dựng thuật toán Nắn chỉnh lưới tô-pô (Topological Grid Snapping) và tự động đánh mã `module_id` (`Block -> String -> Row -> ID_Pin`) cho 100% tấm pin (kể cả tấm méo). | - Bộ trọng số mô hình AI 1 (`.pt`, `.onnx`) + Bảng so sánh thực nghiệm các mô hình.<br>- Module code Python xử lý Ortho, nắn lưới tô-pô và sinh dữ liệu chuẩn nạp vào bảng `solar_modules`.<br>- Chương báo cáo & Slide phần Pipeline 1 + Độ phức tạp thuật toán lưới. |
| **Thành viên 2 (TV2)**<br>*(Phụ trách Module 2)* | **Module 2: Pipeline AI Nhận diện Tấm pin Ảnh lẻ + Phát hiện Lỗi Ảnh nhiệt & Ánh xạ Không gian lên `module_id`** | 1. Chuẩn hóa tập nhãn ảnh lẻ RGB (`_W.JPG`) và ảnh nhiệt (`_T.JPG` 4 lớp lỗi: `SingleHotSpot`, `MultiHotSpot`, `Bypass`, `ModuleOpenCircuit`) theo dải không gian không trùng lặp.<br>2. **Huấn luyện từ đầu (Train from scratch)** 2 mô hình: AI 2A (Nhận diện tấm pin trên ảnh lẻ) và AI 2B (Nhận diện 4 loại lỗi nhiệt) + giải mã nhiệt độ bức xạ 16-bit R-JPEG.<br>3. Xây dựng thuật toán Ghép cặp nội tại (Ảnh nhiệt $\leftrightarrow$ Tấm pin ảnh lẻ) và Pipeline Ánh xạ Không gian (8-DoF DLT Homography chuẩn hóa Hartley + Mass-Spring + Hungarian hai ngưỡng) để xác định chính xác lỗi rơi vào `module_id` nào trên bản đồ số. | - Bộ trọng số mô hình AI 2A & AI 2B (`.pt`, `.onnx`) + Bảng đánh giá mAP, IoU, RMSE.<br>- Module code ghép cặp RGB–Nhiệt và ánh xạ không gian xuất kết quả vào bảng `ai_raw_detections` & `module_inspection_logs`.<br>- Chương báo cáo & Slide phần Pipeline 2 + Chứng minh toán học ánh xạ. |
| **Thành viên 3 (TV3)**<br>*(Phụ trách Module 3)* | **Module 3: Hệ thống Phần mềm Quản lý Bản sao số (Backend Rust + PostGIS) & Web Quản trị Đa đợt bay (WebGIS 60 FPS)** | 1. Thực hiện trọn vẹn 6 bước PTTKHT: Đặc tả Use Case, vẽ sơ đồ Use Case, thiết kế CSDL PostgreSQL/PostGIS (`7` bảng + chỉ mục không gian R-Tree `GiST`), vẽ Sequence/Activity Diagram và sơ đồ Clean Architecture.<br>2. Xây dựng Backend hiệu năng cao bằng **Rust (`Axum` + `SQLx`)** kết nối PostGIS và hàng đợi Redis để điều phối tác vụ suy luận của Module 1 & Module 2, cung cấp API quản lý các lần bay và Tile Server.<br>3. Xây dựng giao diện Web Quản trị (**React/Next.js + MapLibre GL JS WebGL**) hiển thị mượt `36.544` tấm pin, tô màu cảnh báo theo loại lỗi tại từng `module_id`, xem đối chiếu ảnh RGB/Nhiệt và xuất biên bản bảo trì. | - Bộ bản vẽ PTTKHT đầy đủ (Use Case, ERD, Sequence, Activity, Architecture).<br>- Mã nguồn Backend Rust + CSDL PostGIS + Giao diện Web Quản trị Digital Twin chạy mượt.<br>- Chương báo cáo & Slide phần PTTKHT, CSDL và Demo trực tiếp hệ thống. |

---

### 7.2. Kế hoạch Triển khai Chi tiết từng Tuần (`16/11/2026` – `17/01/2027` — 9 Tuần)
*(Bám sát 3 mốc đánh giá M1, M2, M3 của Trường ĐHXDHN; toàn bộ dữ liệu đã sẵn sàng nên bắt tay ngay vào thiết kế và xây dựng mới từ Tuần 1).*

#### GIAI ĐOẠN 1: KHỞI ĐỘNG, CHỐT ĐẶC TẢ PTTKHT & CHUẨN HÓA PIPELINE DỮ LIỆU (Tuần 1 – Tuần 2: `16/11/2026` – `29/11/2026`) — *Hướng tới Mốc đánh giá M1 (20% điểm)*

- **Tuần 1 (`16/11` – `22/11/2026`): Chốt Đặc tả Nhiệm vụ ĐATN, Thiết kế PTTKHT & Khung Dữ liệu huấn luyện**
  - **Công việc chung cả nhóm:** Thống nhất định dạng giao tiếp dữ liệu (JSON Schema & PostGIS Table Schema) giữa 3 Module; khởi tạo GitHub Monorepo (`solar-digital-twin-datn`) chia 3 thư mục độc lập (`mod1_ortho_ai`, `mod2_thermal_mapping`, `mod3_rust_webgis`).
  - **TV1 (Module 1):** Viết script quét `thuannam19_master.gpkg` và `Block1..6.gpkg`, trích xuất danh sách các vị trí tấm pin bị méo chưa vẽ (như `Block1` khuyết mã `4049..4068`, `string35..37`), nội suy khung lưới bổ sung và chia tập Train (60%) / Val (15%) / Test (25%) theo Block.
  - **TV2 (Module 2):** Rà soát và đóng gói bộ nhãn ảnh lẻ RGB và bộ nhãn 4 lớp lỗi nhiệt (`SingleHotSpot`, `MultiHotSpot`, `Bypass`, `ModuleOpenCircuit`) theo dải không gian cách ly `15m`; viết module đọc EXIF RTK và giải mã mảng nhiệt độ 16-bit từ file `_T.JPG`.
  - **TV3 (Module 3):** Hoàn thành Bước 1, Bước 2, Bước 3 của PTTKHT (Phân rã chức năng, Đặc tả Use Case, vẽ sơ đồ Use Case, thiết kế ERD 7 bảng và khởi tạo Docker PostgreSQL + PostGIS nạp sẵn `36.544` tấm pin kèm chỉ mục R-Tree `GIST`).

- **Tuần 2 (`23/11` – `29/11/2026`): Hoàn thiện Thiết kế Kiến trúc & Chạy Huấn luyện Baseline từ đầu (Mốc M1)**
  - **Công việc chung cả nhóm:** Nộp báo cáo tiến độ giai đoạn đầu (**Mốc M1 – 20%**) gồm Đề cương chi tiết, bản vẽ PTTKHT và kết quả chạy thử nghiệm đầu tiên.
  - **TV1 (Module 1):** Xây dựng bộ Augmentation giả lập biến dạng đường ghép ảnh (Seamline Shift + Elastic Grid Deformation); bắt đầu **train từ đầu (from scratch)** các biến thể mô hình nhận diện Ortho (so sánh YOLOv8-OBB, YOLO11-OBB và mô hình đối chứng Rotated RetinaNet / HBB để lấy bảng số liệu khảo sát).
  - **TV2 (Module 2):** Bắt đầu **train từ đầu** mô hình nhận diện tấm pin trên ảnh lẻ (AI 2A) và mô hình phát hiện 4 loại lỗi nhiệt (AI 2B); ghi nhận thông số tiêu thụ phần cứng (VRAM, thời gian 1 epoch, tốc độ ms/ảnh) để phục vụ câu hỏi phản biện của thầy cô.
  - **TV3 (Module 3):** Hoàn thành Bước 4, Bước 5 PTTKHT (Sơ đồ Activity, Sequence, Kiến trúc Clean Architecture); dựng khung dự án **Rust (`Axum` + `SQLx`)** kết nối PostGIS và viết các API cơ bản truy vấn danh sách nhà máy, phân khu Block/String và xuất GeoJSON `36.544` tấm pin.

---

#### GIAI ĐOẠN 2: HUẤN LUYỆN CHUYÊN SÂU, THUẬT TOÁN ÁNH XẠ & XÂY DỰNG WEB DIGITAL TWIN (Tuần 3 – Tuần 6: `30/11/2026` – `27/12/2026`) — *Hướng tới Mốc đánh giá M2 (30% điểm)*

- **Tuần 3 (`30/11` – `06/12/2026`): Tối ưu hóa Mô hình AI (Train từ đầu) & Xây dựng Bản đồ WebGL**
  - **TV1 (Module 1):** Tinh chỉnh hàm mất mát ProbIoU, ngưỡng góc xoay và chạy suy luận cửa sổ trượt ($1024 \times 1024$, chồng lấn 20%) kèm hợp nhất Rotational NMS trên toàn bản đồ Ortho `87m` và `35m`.
  - **TV2 (Module 2):** Tinh chỉnh mô hình AI 2A (bắt đầy đủ các tấm pin ở rìa ảnh lẻ bị cong ống kính) và AI 2B (tăng Recall cho các lớp lỗi ít mẫu như `Bypass` và `ModuleOpenCircuit`); xây dựng thuật toán **Ghép cặp nội tại (Intra-pair RGB–Thermal Matching)** để gắn từng vết lỗi nhiệt vào đúng tấm pin trên bức ảnh lẻ.
  - **TV3 (Module 3):** Xây dựng giao diện bản đồ số trên **Next.js + MapLibre GL JS (WebGL)** kết nối với Rust Tile Server, hiển thị mượt đồng thời lớp ảnh nền Ortho (`orthophoto_87m`) và lớp đa giác `36.544` tấm pin ở tốc độ 60 FPS.

- **Tuần 4 (`07/12` – `13/12/2026`): Thuật toán Nắn lưới Pin méo (Module 1) & Phép chiếu Homography (Module 2)**
  - **TV1 (Module 1):** Hoàn thiện thuật toán **Topological KD-Tree Grid Snapping**: tự động bắt các tấm pin ở vùng bị méo đường ghép ảnh, khôi phục hình dáng chuẩn và đánh mã định danh `module_id` liên tục theo `Block -> String -> Row -> ID_Pin`.
  - **TV2 (Module 2):** Hiện thực hóa thuật toán **8-DoF DLT Homography có chuẩn hóa Hartley** và **Mạng lưới lò xo đàn hồi (Elastic Mass-Spring Regularization)** để chiếu tọa độ các tấm pin và lỗi nhiệt từ ảnh lẻ (`31m`, `35m`, `42m`) xuống hệ tọa độ phẳng `EPSG:32649` của Bản đồ số.
  - **TV3 (Module 3):** Xây dựng các API Rust quản lý Chiến dịch bay (`flight_campaigns`), tải lên lô ảnh khảo sát (`raw_image_pairs`) và cơ chế hàng đợi tác vụ bất đồng bộ (Redis Queue) để gọi sang Pipeline của TV1 và TV2.

- **Tuần 5 (`14/12` – `20/12/2026`): Ghép cặp Tối ưu Hungarian Gán `module_id` & Giao diện Quản trị Đợt bay**
  - **TV1 (Module 1):** Xuất mô hình AI 1 sang chuẩn `.onnx`; viết bộ đánh giá độ phức tạp thuật toán và đo đạc tỷ lệ bắt đúng các tấm pin bị méo trên tập Test độc lập.
  - **TV2 (Module 2):** Hoàn thiện thuật toán **Ghép cặp tối ưu Hungarian hai ngưỡng (Dual-Threshold Gating: $\text{IoU} \ge 0,50, \Delta d < 52,4\text{ cm}, \text{Margin} \ge 0,15$)** kết hợp truy vấn chỉ mục không gian R-Tree để xác định chính xác từng lỗi nhiệt rơi vào `module_id` nào; tự động cắt ảnh minh chứng (RGB Crop & Thermal Crop) lưu vào hệ thống.
  - **TV3 (Module 3):** Xây dựng giao diện chi tiết trên Web Quản trị: khi người dùng bấm vào bất kỳ tấm pin nào trên bản đồ (ví dụ `block1_string4_00458`), hiển thị ngay bảng thông tin chi tiết, lịch sử lỗi qua các đợt bay, ảnh cắt RGB – Ảnh nhiệt đối chiếu và biểu đồ thống kê toàn nhà máy.

- **Tuần 6 (`21/12` – `27/12/2026`): Tích hợp Liên thông 3 Module & Báo cáo Giữa kỳ (Mốc M2 – 30%)**
  - **Công việc chung cả nhóm:** Ghép nối toàn bộ luồng End-to-End từ Giao diện Web $\rightarrow$ Rust Backend $\rightarrow$ Pipeline AI 1 & AI 2 $\rightarrow$ PostGIS $\rightarrow$ Hiển thị kết quả lên Bản đồ số; kiểm tra tiến độ giữa kỳ (**Mốc M2 – 30%**).
  - **TV1 + TV2:** Chạy kiểm thử toàn bộ dữ liệu thực tế của đợt bay `87m`, `42m`, `35m`, `31m` tại nhà máy Thuận Nam 19 và thử nghiệm mở rộng trên dữ liệu nhà máy BIM 2 / Thiên Tân 1.2; xuất trọn bộ bảng biểu số liệu thực nghiệm.
  - **TV3:** Hoàn thiện chức năng Kiểm duyệt QC (cho phép kỹ sư xác nhận các tấm pin vùng biên) và chức năng Xuất biên bản chẩn đoán lỗi nhiệt ra file PDF / Excel / GeoPackage.

---

#### GIAI ĐOẠN 3: KIỂM THỬ TOÀN DIỆN, VIẾT BÁO CÁO ĐATN & CHUẨN BỊ BẢO VỆ (Tuần 7 – Tuần 9: `28/12/2026` – `17/01/2027`) — *Hướng tới Hạn nộp 17/01 & Bảo vệ M3 (50% điểm)*

- **Tuần 7 (`28/12/2026` – `03/01/2027`): Kiểm thử Hiệu năng, Đóng gói Docker & Viết Bản thảo Báo cáo ĐATN**
  - **TV1:** Viết Chương 1 (Tổng quan bài toán: Đầu vào – Đầu ra, phạm vi thực tế) và Chương 3 – Phần 1 (Pipeline AI 1 nhận diện Ortho chính, xử lý biến dạng ghép ảnh và nắn lưới tô-pô).
  - **TV2:** Viết Chương 3 – Phần 2 (Pipeline AI 2 nhận diện ảnh lẻ/ảnh nhiệt, giải mã nhiệt bức xạ, toán học ánh xạ Homography – Mass-Spring – Hungarian và phân tích độ phức tạp thuật toán).
  - **TV3:** Viết Chương 2 (Phân tích thiết kế hệ thống 6 bước PTTKHT, ERD, luồng dữ liệu qua các bảng CSDL, kiến trúc Rust + PostGIS + WebGL) và đóng gói toàn bộ hệ thống bằng `docker-compose.yml` để bật lên chạy ngay bằng 1 lệnh.

- **Tuần 8 (`04/01` – `10/01/2027`): Hợp nhất Báo cáo Toàn văn ($\le 150$ trang), Đối chiếu CLO & Duyệt GVHD**
  - **Công việc chung cả nhóm:** Ghép nối Chương 4 (Thực nghiệm, Đánh giá kết quả và Thảo luận) + Kết luận & Hướng mở; rà soát định dạng theo đúng Phụ lục II Quy định `483/QĐ-ĐHXDHN` (cỡ chữ, đánh số hình/bảng, tài liệu tham khảo IEEE/APA); nộp bản thảo cho Giảng viên hướng dẫn góp ý.
  - **TV1 + TV2 + TV3:** Chuẩn bị bộ câu hỏi & câu trả lời phản biện cá nhân cho từng Module (tại sao chọn mô hình, tại sao mô hình cũ không phù hợp, dữ liệu chạy qua bảng nào, độ phức tạp thuật toán là bao nhiêu).

- **Tuần 9 (`11/01` – `17/01/2027`): Chỉnh sửa Hoàn thiện, Thiết kế Slide Bảo vệ & Nộp Quyển Báo cáo Chính thức (`17/01/2027`)**
  - **Từ `11/01` – `15/01/2027`:** Chỉnh sửa báo cáo theo nhận xét của GVHD; thiết kế bộ **Slide Bảo vệ chuẩn cấu trúc mới**:
    - *Phần 1 (Mở đầu):* Chỉ trình bày Bài toán thực tế, **Đầu vào** và **Đầu ra** (tuyệt đối không để tên thuật toán ở slide mở đầu).
    - *Phần 2 (Phân tích & Thiết kế PTTKHT):* Use Case, Kiến trúc tổng thể, ERD và luồng dữ liệu AI đi qua 7 bảng CSDL.
    - *Phần 3 (Triển khai & Thuật toán):* Trình bày chi tiết Pipeline AI 1 (vùng pin méo), Pipeline AI 2 (ảnh lẻ + ảnh nhiệt + ánh xạ `module_id`), bảng khảo sát chọn mô hình theo phần cứng (CPU/GPU/VRAM) và bảng đánh giá Độ phức tạp thuật toán $O(\cdot)$.
    - *Phần 4 (Thực nghiệm & Demo):* Video dự phòng + Demo trực tiếp Web Quản trị Bản sao số.
  - **Ngày `16/01` – `17/01/2027`:** Kiểm tra lần cuối quy tắc đặt tên file chuẩn `[Đợt]_[Khoa]_[Ngành]_[MãSV]_[HọTên]_[LoạiTàiLiệu]_[YYYYMMDD]_v1`, xuất PDF và **Nộp chính thức Báo cáo ĐATN + Mã nguồn đúng hạn `17/01/2027`**.

---

## 8. PHỤ LỤC: DỰ THẢO NỘI DUNG PHIẾU GIAO NHIỆM VỤ ĐATN (THEO MẪU ĐATN-01 – HUCE)

*(Nhóm có thể chép trực tiếp nội dung dưới đây vào biểu mẫu `Mẫu ĐATN-01` trong tệp `HUCE_QD_DATN_v2_260119.docx` để trình Giảng viên hướng dẫn và Bộ môn Khoa học Máy tính phê duyệt).*

1. **Tên đề tài Đồ án tốt nghiệp:**
   - **Tiếng Việt:** *Xây dựng hệ thống Bản sao số (Digital Twin) tích hợp Trí tuệ nhân tạo nhận diện tấm pin biến dạng và định vị khuyết tật nhiệt từ dữ liệu UAV phục vụ quản lý vận hành nhà máy điện mặt trời.*
   - **Tiếng Anh:** *Building an AI-Integrated Digital Twin System for Distorted Solar Panel Detection and UAV Thermal Defect Localization in Photovoltaic Plant Operations and Maintenance.*
2. **Các dữ liệu ban đầu và tài liệu chính:**
   - Bộ cơ sở dữ liệu bản đồ số gốc `thuannam19_master.gpkg` (`36.544` tấm pin, `6` Block, `148` String, hệ quy chiếu `EPSG:32649`) và dữ liệu bay khảo sát thực tế tại 04 nhà máy điện mặt trời tỉnh Ninh Thuận (Thuận Nam 19, BIM 2, Thuận Nam Đức Long, Thiên Tân 1.2) ở các độ cao `87m`, `42m`, `35m`, `31m` (`12.557` ảnh RGB và ảnh nhiệt bức xạ 16-bit R-JPEG).
3. **Nội dung các phần thuyết minh và tính toán (Chia theo 03 thành viên):**
   - **Phần chung:** Khảo sát nghiệp vụ O&M nhà máy điện mặt trời, xác định bài toán Đầu vào – Đầu ra, thiết kế kiến trúc tổng thể hệ thống Bản sao số và kiểm thử tích hợp toàn hệ thống.
   - **Sinh viên 1 (Module 1):** Nghiên cứu và huấn luyện từ đầu mô hình AI nhận diện tấm pin có hướng (OBB) trên bản đồ trực giao chính (`85m–87m`) có khả năng phát hiện các vùng tấm pin bị méo/biến dạng do ghép ảnh; xây dựng thuật toán nắn chỉnh lưới tô-pô (Topological Grid Snapping) và tự động định danh `module_id`.
   - **Sinh viên 2 (Module 2):** Nghiên cứu và huấn luyện từ đầu mô hình nhận diện tấm pin trên ảnh lẻ và mô hình phát hiện 4 nhóm lỗi nhiệt trên ảnh nhiệt; xây dựng thuật toán ghép cặp nội tại RGB–Nhiệt và pipeline ánh xạ không gian (8-DoF DLT Homography chuẩn hóa Hartley, tối ưu đàn hồi Mass-Spring và thuật toán Hungarian hai ngưỡng) để định vị chính xác lỗi nhiệt vào từng `module_id` trên bản đồ số.
   - **Sinh viên 3 (Module 3):** Phân tích và thiết kế hệ thống theo chuẩn 6 bước PTTKHT; thiết kế cơ sở dữ liệu không gian PostgreSQL/PostGIS có chỉ mục R-Tree; xây dựng Backend hiệu năng cao bằng ngôn ngữ Rust (`Axum`) và giao diện Web quản trị Bản sao số đa đợt bay sử dụng công nghệ kết xuất phần cứng WebGL (`MapLibre GL JS`).
4. **Các bản vẽ và sản phẩm phần mềm cần nộp:**
   - Báo cáo thuyết minh ĐATN ($\le 150$ trang A4) kèm bộ bản vẽ PTTKHT (Use Case, ERD, Sequence, Activity, System Architecture) và lưu đồ thuật toán AI / Ánh xạ không gian.
   - Bộ trọng số các mô hình AI huấn luyện từ đầu (`.pt`, `.onnx`) và chương trình phần mềm Web quản trị Bản sao số hoàn chỉnh.
5. **Ngày giao nhiệm vụ:** `16/11/2026` — **Ngày hoàn thành nộp báo cáo:** `17/01/2027`.
