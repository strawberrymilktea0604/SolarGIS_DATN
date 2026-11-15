\# HỢP ĐỒNG GIAO TIẾP DỮ LIỆU LIÊN MODULE (`DATA\_CONTRACT.md`)



\- \*\*Dự án:\*\* Hệ thống Bản sao số (Digital Twin) \& AI Đa luồng Giám sát Nhà máy Điện mặt trời từ Dữ liệu UAV

\- \*\*Kho mã nguồn:\*\* `solargis-digital-twin-rust`

\- \*\*Phiên bản:\*\* `V6.1 (Locked Freeze)` — \*\*Ngày hiệu lực:\*\* `16/11/2026`

\- \*\*Thành viên ký kết:\*\* Thành viên 1 (Module 1 – 33%) | Thành viên 2 (Module 2 – 33%) | Thành viên 3 (Module 3 – 34%)



\---



\## 1. QUY ƯỚC HỆ TỌA ĐỘ (CRS), ĐỊNH DANH \& MÃ LỖI TOÀN CỤC



Mọi module (Python AI 1, Python AI 2, Rust Backend, PostGIS, React/MapLibre Frontend) \*\*bắt buộc\*\* tuân thủ các hằng số bất biến sau:



\### 1.1. Hệ quy chiếu không gian (CRS)

\- \*\*Lưu trữ \& Tính toán hình học (`.gpkg`, PostGIS `geom`, `spatial\_grid\_index`, Homography, Hungarian):\*\* `EPSG:32649` (WGS 84 / UTM Zone 49N — đơn vị: \*\*mét\*\*).

\- \*\*Truyền tải Bản đồ Web (`XYZ WebP Raster Tiles`, `PMTiles`, `PostGIS ST\_AsMVT`):\*\* `EPSG:3857` (Web Mercator).

\- \*\*Tọa độ GPS thô từ EXIF UAV:\*\* `EPSG:4326` (WGS 84 kinh/vĩ độ) $\\rightarrow$ phải chiếu ngay sang `EPSG:32649` khi nạp vào bảng `raw\_image\_pairs`.



\### 1.2. Quy tắc đặt mã định danh

\- \*\*Mã nhà máy (`plant\_code`):\*\* Chỉ nhận 1 trong 4 giá trị chuỗi viết hoa:

&#x20; - `TN19` (Thuận Nam 19)

&#x20; - `BIM2` (BIM 2)

&#x20; - `TNDL` (Thuận Nam Đức Long)

&#x20; - `TT12` (Thiên Tân 1.2)

\- \*\*Khóa chính nghiệp vụ tấm pin (`module\_id` – `VARCHAR`):\*\*

&#x20; ```text

&#x20; {plant\_code\_lower}\_block{B}\_string{S}\_{pin\_index:05d}

&#x20; Ví dụ: tn19\_block1\_string4\_00458

&#x20; ```

\- \*\*Khóa nguyên Vector Tile (`mvt\_id` – `BIGSERIAL / int64 > 0`):\*\*

&#x20; - Sinh tự động tại bảng `solar\_modules`.

&#x20; - Dùng làm \*\*top-level Feature ID\*\* trong `ST\_AsMVT(..., 'mvt\_id')` và `map.setFeatureState({ id: mvt\_id })`.

&#x20; - \*\*Tuyệt đối không\*\* dùng `promoteId: "module\_id"` trên MapLibre GL JS.



\### 1.3. Bảng mã 4 lớp lỗi nhiệt \& Phân hạng chuẩn IEC TS 62446-3:2017



| `class\_id` (YOLO-OBB) | `fault\_class` (DB \& JSON) | Thứ tự ưu tiên (`severity\_rank`) | Quy tắc gán `iec\_coa\_class` chuẩn IEC TS 62446-3 | Gợi ý `om\_priority` |

| :---: | :--- | :---: | :--- | :---: |

| \*(Không hộp)\* | `'NORMAL'` | `0` | \*\*`1`\*\* (\*CoA 1: No thermal abnormality\*) — Chỉ lưu ở `solar\_modules` | — |

| `0` | `'SingleHotSpot'` | `1` | \*\*`3`\*\* nếu $\\Delta T\_{\\text{measured}} > 20.0^\\circ\\text{C}$; \*\*`2`\*\* nếu $\\Delta T\_{\\text{measured}} \\le 20.0^\\circ\\text{C}$ | `LOW` ($\\le 10^\\circ\\text{C}$), `MEDIUM` ($10\\text{–}20^\\circ\\text{C}$), `HIGH` ($> 20^\\circ\\text{C}$) |

| `1` | `'MultiHotSpot'` | `2` | \*\*`3`\*\* nếu $\\Delta T\_{\\text{measured}} > 20.0^\\circ\\text{C}$; \*\*`2`\*\* nếu $\\Delta T\_{\\text{measured}} \\le 20.0^\\circ\\text{C}$ | `MEDIUM` / `HIGH` |

| `2` | `'Bypass'` | `3` | \*\*`3`\*\* (\*CoA 3: Safety-relevant abnormality\*) | `HIGH` |

| `3` | `'ModuleOpenCircuit'` | `4` | \*\*`3`\*\* (\*CoA 3: Safety-relevant abnormality\*) | `HIGH` |



\- \*\*Công thức quy đổi chuẩn bức xạ $1000\\text{ W/m}^2$:\*\*

&#x20; $$\\Delta T\_{\\text{norm}} = \\Delta T\_{\\text{measured}} \\times \\left(\\frac{1000.0}{G\_{\\text{POA}}}\\right)^{1.0}$$

&#x20; \*(Cảnh báo giao diện nếu $G\_{\\text{POA}} < 600.0\\text{ W/m}^2$).\*



\---



\## 2. CẤU HÌNH PHẦN CỨNG ĐA CAMERA (`CAMERA\_PROFILES`)



Do nhà máy `BIM2` sử dụng tổ hợp `DJI\_M2EA` + `DJI\_P1` khác biệt với `DJI\_ZH20T` tại 3 nhà máy còn lại, hệ thống tách bạch cấu hình phần cứng như sau:



```json

{

&#x20; "DJI\_ZH20T": {

&#x20;   "role": "THERMAL\_INSPECTION\_AND\_RGB\_PAIR",

&#x20;   "rgb\_resolution": \[4056, 3040],

&#x20;   "thermal\_resolution": \[640, 512],

&#x20;   "thermal\_focal\_mm": 13.5,

&#x20;   "thermal\_pitch\_um": 12.0,

&#x20;   "thermal\_decoder": "DJI\_DIRP\_SDK",

&#x20;   "homography\_profile\_key": "zh20t\_dual\_sensor\_h",

&#x20;   "iec\_cell\_level\_max\_alt\_m": 35.0

&#x20; },

&#x20; "DJI\_M2EA": {

&#x20;   "role": "THERMAL\_INSPECTION\_AND\_RGB\_PAIR",

&#x20;   "rgb\_resolution": \[8000, 6000],

&#x20;   "thermal\_resolution": \[640, 512],

&#x20;   "thermal\_focal\_mm": 9.0,

&#x20;   "thermal\_pitch\_um": 12.0,

&#x20;   "thermal\_decoder": "DJI\_DIRP\_SDK\_OR\_RJPG\_CALIBRATED",

&#x20;   "homography\_profile\_key": "m2ea\_dual\_sensor\_h",

&#x20;   "iec\_cell\_level\_max\_alt\_m": 23.4,

&#x20;   "note": "Ở 31m GSD nhiệt đạt \~4.13 cm/px -> đánh giá cấp Module/Sub-string, có xét Spot-Size Effect"

&#x20; },

&#x20; "DJI\_P1": {

&#x20;   "role": "ORTHOMOSAIC\_BASE\_MAP\_ONLY",

&#x20;   "rgb\_resolution": \[8192, 5460],

&#x20;   "thermal\_resolution": null,

&#x20;   "note": "Chỉ phục vụ Module 1 (Ortho AI 1 \& XYZ WebP Tiles), không đẩy vào hàng đợi lỗi nhiệt Module 2"

&#x20; }

}

```



\### Quy tắc Khử méo Ống kính (`DewarpData` + OpenCV `P=K`)

1\. \*\*San tải Tuần 1:\*\* TV3 (trong Rust khi upload) và TV1 (trong script kiểm kê Python) dùng chung logic đọc EXIF/XMP trích xuất `DewarpFlag`, `DewarpData`, `RtkFlag`, `RelativeAltitude`, `FlightYawDegree`, `GimbalYawDegree`, `strip\_id`, `strip\_sequence\_idx` để TV2 không phải viết lại bộ parser.

2\. Nếu `dewarp\_applied\_in\_camera == true` (`DewarpFlag == 1`): giữ nguyên ảnh và tọa độ nhãn.

3\. Nếu `dewarp\_applied\_in\_camera == false` (`DewarpFlag == 0`):

&#x20;  - Quy đổi tâm quang học: `cx\_opencv = W / 2.0 + cx\_dewarp`, `cy\_opencv = H / 2.0 + cy\_dewarp`.

&#x20;  - Khử méo đỉnh đa giác OBB \*\*bắt buộc có `P=K`\*\*:

&#x20;    ```python

&#x20;    pts\_undist\_px = cv2.undistortPoints(

&#x20;        pts\_px.reshape(-1, 1, 2), K, dist\_coeffs, R=None, P=K

&#x20;    ).reshape(-1, 2)

&#x20;    ```



\---



\## 3. HỢP ĐỒNG API PYTHON DÙNG CHUNG: `spatial\_grid\_index` (TV1 cung cấp $\\rightarrow$ TV2 gọi)



TV1 bàn giao gói Python `packages/spatial\_grid\_index` (chốt cứng chữ ký hàm chậm nhất \*\*23:59 ngày 29/11/2026\*\*):



```python

from dataclasses import dataclass

from typing import List, Literal, Tuple

import numpy as np



@dataclass(frozen=True)

class ModuleCandidate:

&#x20;   module\_id: str

&#x20;   mvt\_id: int

&#x20;   block\_code: str

&#x20;   string\_code: str

&#x20;   row\_id: int                  # 1..4

&#x20;   pin\_index: int               # ID\_Pin tăng dần theo trục u đã khóa hướng

&#x20;   centroid\_utm: Tuple\[float, float]

&#x20;   corners\_utm: np.ndarray      # shape (4, 2), float64, thứ tự: TL, TR, BR, BL trên trục (u, v)



@dataclass(frozen=True)

class BoundaryLandmark:

&#x20;   landmark\_id: str

&#x20;   landmark\_type: Literal\["TABLE\_CORNER", "AISLE\_GAP\_EDGE", "BLOCK\_BOUNDARY"]

&#x20;   block\_code: str

&#x20;   string\_code: str

&#x20;   pin\_index\_anchor: int        # Cột pin sát biên dùng để khóa cứng chỉ số cột tuyệt đối

&#x20;   point\_utm: Tuple\[float, float]



class SpatialGridIndex:

&#x20;   def \_\_init\_\_(self, postgis\_dsn\_or\_gpkg\_dir: str) -> None: ...



&#x20;   def get\_candidates\_in\_radius(

&#x20;       self,

&#x20;       plant\_code: str,

&#x20;       x\_utm: float,

&#x20;       y\_utm: float,

&#x20;       radius\_m: float = 0.524,

&#x20;   ) -> List\[ModuleCandidate]:

&#x20;       """Tra cứu R-Tree + KD-Tree trong O(log N). Bán kính mặc định 52.4 cm (< 1/2 bước cột 1.13m)."""



&#x20;   def get\_block\_string\_boundary\_landmarks(

&#x20;       self,

&#x20;       plant\_code: str,

&#x20;       bbox\_utm: Tuple\[float, float, float, float], # (min\_x, min\_y, max\_x, max\_y)

&#x20;   ) -> List\[BoundaryLandmark]:

&#x20;       """

&#x20;       Trả về cả biên 2 đầu dải bay LẪN các khe đường nội bộ giữa các Block/String (AISLE\_GAP\_EDGE)

&#x20;       để TV2 làm điểm neo đầu/cuối và điểm neo trung gian (Mid-strip Anchor).

&#x20;       """



&#x20;   def mass\_spring\_refine(

&#x20;       self,

&#x20;       plant\_code: str,

&#x20;       projected\_centers\_utm: np.ndarray, # shape (M, 2)

&#x20;       neighbor\_graph\_edges: List\[Tuple\[int, int, Literal\["ALONG\_U", "ALONG\_V"]]],

&#x20;   ) -> np.ndarray:

&#x20;       """Làm mịn đám mây tâm tấm pin bằng hệ lò xo thưa O(I \* M), trả về mảng (M, 2) đã khử nhiễu."""

```



\### Quy tắc Chống đứt gãy Dải bay trong `Bidirectional Strip Anchoring` (TV2 – Đầu việc 4.2)

\- \*\*Chế độ chuẩn (`BIDIRECTIONAL`):\*\* Dải ảnh có $\\ge 2$ điểm neo biên (`start\_anchor` và `end\_anchor`, hoặc `mid\_strip\_anchor` khi bay qua đường nội bộ giữa 2 Block) $\\rightarrow$ nội suy song phương biến đổi cứng `4-DoF Similarity / 6-DoF Affine` liên khung + kẹp tâm RTK ($\\pm 10\\text{ cm}$).

\- \*\*Chế độ suy giảm an toàn (`UNIDIRECTIONAL\_RTK\_CLAMPED`):\*\* Khi drone ngắt dải về thay pin (RTH) khiến chỉ 1 đầu thấy biên lối đi $\\rightarrow$ lan truyền `4-DoF Similarity` từ đầu có biên kết hợp kẹp cứng bán kính sai số RTK (`rtk\_fix\_flag == 50`, $\\pm 10\\text{ cm}$). Nếu `rtk\_fix\_flag != 50` (Float/Single) hoặc độ lệch tích lũy $> 35\\text{ cm}$, tự động ép `qc\_status = 'PENDING\_QC'`.



\---



\## 4. HỢP ĐỒNG REDIS QUEUE \& PUB/SUB (`Rust Axum` $\\leftrightarrow$ `Python AI Worker`)



\### 4.1. Tên kênh Redis cố định

\- \*\*Hàng đợi Pipeline AI 1 (Ortho Gap Recovery):\*\* `queue:solargis:ortho\_jobs` (`BLPOP`)

\- \*\*Hàng đợi Pipeline AI 2 (Theo từng Dải bay `strip\_id` để chạy Strip Anchoring):\*\* `queue:solargis:strip\_inspection\_jobs` (`BLPOP`)

\- \*\*Kênh sự kiện thời gian thực (Worker bắn $\\rightarrow$ Rust Axum đẩy SSE/WebSocket lên Web):\*\* `pubsub:solargis:campaign\_events` (`PUBLISH`)



\### 4.2. JSON Schema Job đầu vào: `queue:solargis:strip\_inspection\_jobs`

\*(Lưu ý thiết kế quan trọng: Đẩy theo \*\*từng dải bay `strip\_id`\*\* thay vì từng ảnh rời rạc để Worker của TV2 có đủ chuỗi ảnh liên tiếp `strip\_sequence\_idx` phục vụ `Bidirectional Strip Anchoring` và `Multi-View Deduplication`).\*



```json

{

&#x20; "job\_id": "019330a4-7c90-7b21-8812-9a1b2c3d4e5f",

&#x20; "campaign\_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",

&#x20; "plant\_id": 1,

&#x20; "plant\_code": "TN19",

&#x20; "uav\_camera\_model": "DJI\_ZH20T",

&#x20; "strip\_id": "TN19\_20260411\_31M\_STRIP\_04",

&#x20; "env\_params": {

&#x20;   "irradiance\_wm2": 845.0,

&#x20;   "wind\_speed\_ms": 3.2,

&#x20;   "ambient\_temp\_c": 32.5,

&#x20;   "relative\_humidity\_pct": 68.0,

&#x20;   "reflected\_temp\_c": 5.0,

&#x20;   "emissivity": 0.85

&#x20; },

&#x20; "image\_pairs": \[

&#x20;   {

&#x20;     "image\_pair\_id": "3f2504e0-4f89-11d3-9a0c-0305e82c3301",

&#x20;     "strip\_sequence\_idx": 1,

&#x20;     "rgb\_path": "/data/uploads/TN19/camp\_01/DJI\_20260411101522\_0001\_W.JPG",

&#x20;     "thermal\_path": "/data/uploads/TN19/camp\_01/DJI\_20260411101522\_0001\_T.JPG",

&#x20;     "gps\_x\_utm": 268412.35,

&#x20;     "gps\_y\_utm": 1265890.12,

&#x20;     "recorded\_agl\_m": 30.9,

&#x20;     "gimbal\_yaw": -89.4,

&#x20;     "gimbal\_pitch": -90.0,

&#x20;     "rtk\_fix\_flag": 50,

&#x20;     "dewarp\_applied\_in\_camera": false,

&#x20;     "dewarp\_params": {

&#x20;       "fx": 2912.45,

&#x20;       "fy": 2911.88,

&#x20;       "cx\_opencv": 2032.15,

&#x20;       "cy\_opencv": 1518.40,

&#x20;       "k1": -0.0412,

&#x20;       "k2": 0.0185,

&#x20;       "p1": -0.0003,

&#x20;       "p2": 0.0002,

&#x20;       "k3": -0.0061

&#x20;     }

&#x20;   }

&#x20; ]

}

```



\### 4.3. JSON Schema Sự kiện trả về: `pubsub:solargis:campaign\_events`

Sau khi Python Worker `UPSERT` kết quả vào `module\_inspection\_logs` (kích hoạt Trigger PostGIS), Worker `PUBLISH` gói tin siêu nhẹ sau để Rust Axum chuyển tiếp ngay qua SSE lên trình duyệt gọi `map.setFeatureState`:



```json

{

&#x20; "event\_type": "STRIP\_PROCESSED",

&#x20; "campaign\_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",

&#x20; "plant\_id": 1,

&#x20; "is\_latest\_campaign": true,

&#x20; "progress": {

&#x20;   "processed\_pairs": 120,

&#x20;   "total\_pairs": 640

&#x20; },

&#x20; "updated\_modules": \[

&#x20;   {

&#x20;     "mvt\_id": 14829,

&#x20;     "module\_id": "tn19\_block1\_string4\_00458",

&#x20;     "fault\_class": "SingleHotSpot",

&#x20;     "iec\_coa\_class": 3,

&#x20;     "om\_priority": "HIGH",

&#x20;     "temp\_delta\_measured\_c": 24.6,

&#x20;     "temp\_delta\_norm\_1000wm2\_c": 29.1,

&#x20;     "qc\_status": "AUTO\_VERIFIED"

&#x20;   }

&#x20; ]

}

```



\---



\## 5. CƠ SỞ DỮ LIỆU POSTGIS \& TRIGGER AN TOÀN INSERT / UPDATE / DELETE (TV3)



Bản vá nâng cấp cho hàm Trigger `fn\_sync\_module\_health\_after\_inspection()`: xử lý trọn vẹn cả 3 thao tác `INSERT`, `UPDATE` (kể cả khi kỹ sư QC sửa mã `OLD.module\_id` sang tấm pin bên cạnh `NEW.module\_id` hoặc bác bỏ lỗi giả `QC\_REJECTED`) và `DELETE` (tự động trả tấm pin về `'NORMAL'` / CoA 1 nếu không còn lỗi nào khác trong đợt bay mới nhất).



```sql

\-- Bổ sung trạng thái QC\_REJECTED cho trường hợp kỹ sư bác bỏ hoàn toàn False Positive

ALTER TABLE module\_inspection\_logs

DROP CONSTRAINT IF EXISTS chk\_qc\_status,

ADD CONSTRAINT chk\_qc\_status CHECK (

&#x20;   qc\_status IN ('AUTO\_VERIFIED', 'PENDING\_QC', 'HUMAN\_CONFIRMED', 'HUMAN\_CORRECTED', 'QC\_REJECTED')

);



\-- Hàm con tính lại trạng thái sức khỏe cho 1 tấm pin cụ thể tại đợt bay mới nhất

CREATE OR REPLACE FUNCTION fn\_recompute\_single\_module\_health(

&#x20;   p\_campaign\_id UUID,

&#x20;   p\_module\_id VARCHAR

) RETURNS VOID AS $$

DECLARE

&#x20;   v\_plant\_id INT;

&#x20;   v\_camp\_date TIMESTAMPTZ;

&#x20;   v\_max\_date TIMESTAMPTZ;

&#x20;   v\_top\_fault VARCHAR;

&#x20;   v\_top\_coa SMALLINT;

BEGIN

&#x20;   IF p\_module\_id IS NULL THEN

&#x20;       RETURN;

&#x20;   END IF;



&#x20;   SELECT plant\_id, flight\_date INTO v\_plant\_id, v\_camp\_date

&#x20;   FROM flight\_campaigns WHERE id = p\_campaign\_id;



&#x20;   SELECT MAX(flight\_date) INTO v\_max\_date

&#x20;   FROM flight\_campaigns WHERE plant\_id = v\_plant\_id;



&#x20;   -- Chỉ cập nhật bảng gốc solar\_modules nếu sự kiện thuộc đợt bay mới nhất của nhà máy

&#x20;   IF v\_camp\_date = v\_max\_date THEN

&#x20;       SELECT fault\_class, iec\_coa\_class INTO v\_top\_fault, v\_top\_coa

&#x20;       FROM module\_inspection\_logs

&#x20;       WHERE campaign\_id = p\_campaign\_id

&#x20;         AND module\_id = p\_module\_id

&#x20;         AND qc\_status <> 'QC\_REJECTED'

&#x20;       ORDER BY iec\_coa\_class DESC,

&#x20;                CASE fault\_class

&#x20;                    WHEN 'ModuleOpenCircuit' THEN 4

&#x20;                    WHEN 'Bypass' THEN 3

&#x20;                    WHEN 'MultiHotSpot' THEN 2

&#x20;                    ELSE 1

&#x20;                END DESC,

&#x20;                temp\_delta\_measured\_c DESC

&#x20;       LIMIT 1;



&#x20;       -- Nếu không còn lỗi hợp lệ nào (do DELETE hoặc QC\_REJECTED), tự động trả về NORMAL \& CoA 1

&#x20;       UPDATE solar\_modules

&#x20;       SET current\_health\_status = COALESCE(v\_top\_fault, 'NORMAL'),

&#x20;           current\_coa\_class = COALESCE(v\_top\_coa, 1)

&#x20;       WHERE module\_id = p\_module\_id;

&#x20;   END IF;

END;

$$ LANGUAGE plpgsql;



\-- Trigger chính bắt đủ INSERT, UPDATE, DELETE

CREATE OR REPLACE FUNCTION fn\_sync\_module\_health\_after\_inspection()

RETURNS TRIGGER AS $$

BEGIN

&#x20;   IF TG\_OP = 'DELETE' THEN

&#x20;       PERFORM fn\_recompute\_single\_module\_health(OLD.campaign\_id, OLD.module\_id);

&#x20;       RETURN OLD;

&#x20;   ELSIF TG\_OP = 'UPDATE' THEN

&#x20;       -- Nếu kỹ sư QC đổi gán lỗi từ tấm pin cũ sang tấm pin bên cạnh, tính lại cho cả tấm cũ

&#x20;       IF OLD.module\_id IS DISTINCT FROM NEW.module\_id THEN

&#x20;           PERFORM fn\_recompute\_single\_module\_health(OLD.campaign\_id, OLD.module\_id);

&#x20;       END IF;

&#x20;       PERFORM fn\_recompute\_single\_module\_health(NEW.campaign\_id, NEW.module\_id);

&#x20;       RETURN NEW;

&#x20;   ELSE -- INSERT

&#x20;       PERFORM fn\_recompute\_single\_module\_health(NEW.campaign\_id, NEW.module\_id);

&#x20;       RETURN NEW;

&#x20;   END IF;

END;

$$ LANGUAGE plpgsql;



DROP TRIGGER IF EXISTS trg\_sync\_module\_health\_after\_inspection ON module\_inspection\_logs;

CREATE TRIGGER trg\_sync\_module\_health\_after\_inspection

AFTER INSERT OR UPDATE OR DELETE ON module\_inspection\_logs

FOR EACH ROW EXECUTE FUNCTION fn\_sync\_module\_health\_after\_inspection();

```



\---



\## 6. HỢP ĐỒNG REST API \& GIAO THỨC MAPLIBRE GL JS (`Rust Axum` $\\leftrightarrow$ `React/Next.js`)



\### 6.1. Các Endpoint bắt buộc trên Rust Axum

1\. \*\*`GET /api/tiles/{plant\_id}/{z}/{x}/{y}.mvt`\*\*

&#x20;  - Header trả về: `Content-Type: application/vnd.mapbox-vector-tile`, `Cache-Control: public, max-age=3600`.

&#x20;  - Layer name bên trong MVT: `solar\_modules\_layer`.

&#x20;  - Top-level Feature ID: `mvt\_id` (`uint64`); thuộc tính đi kèm: `mvt\_id\_prop`, `module\_id`, `row\_id`, `pin\_index`, `is\_distorted\_recovered`, `current\_health\_status`, `current\_coa\_class`.

2\. \*\*`GET /api/campaigns/{campaign\_id}/fault\_states`\*\*

&#x20;  - Phục vụ chuyển đổi đợt bay lịch sử (\~20 KB JSON):

&#x20;    ```json

&#x20;    {

&#x20;      "campaign\_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",

&#x20;      "is\_latest": false,

&#x20;      "irradiance\_wm2": 845.0,

&#x20;      "faults": \[

&#x20;        {

&#x20;          "mvt\_id": 14829,

&#x20;          "fault\_class": "SingleHotSpot",

&#x20;          "iec\_coa\_class": 3,

&#x20;          "om\_priority": "HIGH",

&#x20;          "qc\_status": "AUTO\_VERIFIED"

&#x20;        }

&#x20;      ]

&#x20;    }

&#x20;    ```

3\. \*\*`PATCH /api/inspections/{log\_id}/qc`\*\*

&#x20;  - Body JSON khi kỹ sư duyệt QC:

&#x20;    ```json

&#x20;    {

&#x20;      "qc\_status": "HUMAN\_CORRECTED",

&#x20;      "corrected\_module\_id": "tn19\_block1\_string4\_00459",

&#x20;      "reviewer\_note": "Lệch 1 cột ở biên dải cắt ngắt pin"

&#x20;    }

&#x20;    ```

&#x20;  - Trả về mảng `affected\_modules` (gồm cả `old\_mvt\_id` và `new\_mvt\_id`) để Frontend cập nhật màu tức thì mà không cần tải lại MVT.

4\. \*\*`POST /api/campaigns/{campaign\_id}/report.pdf`\*\*

&#x20;  - Bắt buộc chạy trình biên dịch Typst bên trong `tokio::task::spawn\_blocking` để không chặn event loop của Tokio.



\### 6.2. Quy tắc Bất biến trên Frontend MapLibre GL JS (Chống Ghost State \& Lỗi Filter #6213)



```typescript

// 1. Khi đổi đợt bay (Campaign Switcher):

map.removeFeatureState({ source: "solar\_modules", sourceLayer: "solar\_modules\_layer" });

for (const item of data.faults) {

&#x20; map.setFeatureState(

&#x20;   { source: "solar\_modules", sourceLayer: "solar\_modules\_layer", id: item.mvt\_id },

&#x20;   { coa\_class: item.iec\_coa\_class, fault\_class: item.fault\_class, om\_priority: item.om\_priority }

&#x20; );

}



// Tuyệt đối fallback về 1 (CoA 1 Normal) khi xem lịch sử, KHÔNG fallback về \["get", "current\_coa\_class"]

const activeCoaExpr = data.is\_latest

&#x20; ? \["coalesce", \["feature-state", "coa\_class"], \["get", "current\_coa\_class"]]

&#x20; : \["coalesce", \["feature-state", "coa\_class"], 1];



map.setPaintProperty("solar-modules-fill", "fill-color", \[

&#x20; "match", activeCoaExpr,

&#x20; 3, "#ef4444", // CoA 3 - Đỏ

&#x20; 2, "#f59e0b", // CoA 2 - Vàng cam

&#x20; "#22c55e"     // CoA 1 - Xanh lá (Normal)

]);



// 2. Khi lọc theo lỗi / CoA (Lách giới hạn MapLibre Issue #6213):

if (activeFilter === "ALL") {

&#x20; map.setFilter("solar-modules-fill", null);

} else {

&#x20; const matchedMvtIds: number\[] = currentFaultList

&#x20;   .filter(f => matchesFilter(f, activeFilter))

&#x20;   .map(f => f.mvt\_id);

&#x20; map.setFilter("solar-modules-fill", \["in", \["id"], \["literal", matchedMvtIds]]);

}

```



\---



\## 7. QUY CHUẨN MÔI TRƯỜNG DOCKER \& CÔNG CỤ BUILD BẢN ĐỒ (TV1 \& TV3)



1\. \*\*Container AI Worker (`Dockerfile.worker`):\*\*

&#x20;  - Bắt buộc khai báo `FROM --platform=linux/amd64 nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04` (hoặc `python:3.11-slim` với `--platform=linux/amd64` khi chạy CPU trên Mac Apple Silicon M1/M2/M3) vì thư viện gốc `libdirp.so` của DJI Thermal SDK chỉ biên dịch cho kiến trúc `x86\_64`.

&#x20;  - Toàn bộ các tệp `libdirp.so`, `libv\_dirp.so`, `libv\_iirp.so`, `libv\_list.ini` phải nằm chung một thư mục `/opt/dji\_tsdk/` và khai báo `ENV LD\_LIBRARY\_PATH="/opt/dji\_tsdk:${LD\_LIBRARY\_PATH}"`.

2\. \*\*Quy trình chuẩn xuất XYZ WebP $\\rightarrow$ PMTiles (TV1 – Chốt bàn giao TN19 ngày 18/11/2026):\*\*

&#x20;  ```bash

&#x20;  # Bước 1: Cắt XYZ WebP bằng container GDAL chính thức có sẵn libwebp

&#x20;  docker run --rm -e GDAL\_CACHEMAX=4096 -v "$(pwd):/work" ghcr.io/osgeo/gdal:ubuntu-full-3.8.4 \\

&#x20;    gdal2tiles.py --xyz --exclude --processes=8 -z 15-21 \\

&#x20;    --tiledriver=WEBP --webp-quality=85 \\

&#x20;    /work/SonarPanel.tif /work/tiles\_tn19/



&#x20;  # Bước 2: Đóng gói thành 1 file tĩnh .pmtiles duy nhất (qua mb-util + pmtiles CLI)

&#x20;  mb-util --image\_format=webp --scheme=xyz ./tiles\_tn19 ./tn19\_ortho.mbtiles

&#x20;  pmtiles convert ./tn19\_ortho.mbtiles ./tn19\_ortho.pmtiles

&#x20;  ```



\---



\## 8. CAM KẾT MỐC BÀN GIAO ĐƯỜNG GĂNG (CRITICAL PATH HANDOFFS)



| Mốc ngày | Bên giao $\\rightarrow$ Bên nhận | Sản phẩm bàn giao bắt buộc |

| :---: | :---: | :--- |

| \*\*17/11/2026\*\* | Cả nhóm | Chốt Mẫu ĐATN-01, gom đủ `.gpkg` 4 nhà máy, commit `DATA\_CONTRACT.md` lên nhánh `main` + Bảng kiểm kê thông số 4 trang trại. |

| \*\*18/11/2026\*\* | TV1 $\\rightarrow$ TV3 | Gói `tn19\_ortho.pmtiles` (hoặc `tiles\_tn19/`) của Thuận Nam 19 để TV3 dựng bản đồ WebGL ngay trong Tuần 1–2. |

| \*\*22/11/2026\*\* | TV3 $\\rightarrow$ TV1, TV2 | Docker Compose chạy sẵn PostGIS 16-3.4 (đủ 7 bảng + Trigger `INSERT/UPDATE/DELETE` + hàm `ST\_AsMVT`) \& Redis 7. |

| \*\*29/11/2026\*\* | TV1 $\\rightarrow$ TV2 | Khóa cứng chữ ký hàm `spatial\_grid\_index` + Báo cáo Mốc M1 (20%). |

| \*\*06/12/2026\*\* | Cả nhóm | Nối thông Mock End-to-End Pipeline 10 cặp ảnh mẫu từ Giao diện Web $\\rightarrow$ Rust Axum $\\rightarrow$ Redis $\\rightarrow$ Python Worker $\\rightarrow$ PostGIS $\\rightarrow$ SSE đổi màu bản đồ 60 FPS. |

