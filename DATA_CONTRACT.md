# HỢP ĐỒNG GIAO TIẾP DỮ LIỆU LIÊN MODULE (`DATA_CONTRACT.md`)

- **Dự án:** Hệ thống Bản sao số (Digital Twin) & AI Đa luồng Giám sát Nhà máy Điện mặt trời từ Dữ liệu UAV
- **Kho mã nguồn:** `solargis-digital-twin-rust`
- **Phiên bản:** `V6.1 (Locked Freeze - Production-Ready)`
- **Ngày hiệu lực:** `16/11/2026`
- **Thành viên ký kết:** Thành viên 1 (Module 1 – 33%) | Thành viên 2 (Module 2 – 33%) | Thành viên 3 (Module 3 – 34%)

---

## 1. QUY ƯỚC HỆ TỌA ĐỘ (CRS), ĐỊNH DANH & MÃ LỖI TOÀN CỤC

Mọi module trong hệ thống (Python AI 1, Python AI 2, Rust Backend, PostGIS, React/MapLibre Frontend) **bắt buộc** tuân thủ các hằng số bất biến sau:

### 1.1. Hệ quy chiếu không gian (CRS)
- **Lưu trữ & Tính toán hình học (`.gpkg`, PostGIS `geom`, `spatial_grid_index`, Homography, Hungarian):** `EPSG:32649` (WGS 84 / UTM Zone 49N — đơn vị: **mét**).
- **Truyền tải Bản đồ Web (`XYZ WebP Raster Tiles`, `PMTiles`, `PostGIS ST_AsMVT`):** `EPSG:3857` (Web Mercator).
- **Tọa độ GPS thô từ EXIF UAV:** `EPSG:4326` (WGS 84 kinh/vĩ độ) $\rightarrow$ phải chiếu ngay sang `EPSG:32649` khi nạp vào bảng `raw_image_pairs`.

### 1.2. Quy tắc đặt mã định danh
- **Mã nhà máy (`plant_code`):** Chỉ nhận 1 trong 4 giá trị chuỗi viết hoa cố định:
  - `TN19` (Thuận Nam 19)
  - `BIM2` (BIM 2)
  - `TNDL` (Thuận Nam Đức Long)
  - `TT12` (Thiên Tân 1.2)
- **Khóa chính nghiệp vụ tấm pin (`module_id` – `VARCHAR(64)`):**
  ```text
  {plant_code_lower}_block{B}_string{S}_{pin_index:05d}
  Ví dụ: tn19_block1_string4_00458
  ```
- **Khóa nguyên Vector Tile (`mvt_id` – `BIGSERIAL / int64 > 0`):**
  - Sinh tự động tại bảng `solar_modules`.
  - Dùng làm **top-level Feature ID** trong `ST_AsMVT(..., 'mvt_id')` và `map.setFeatureState({ id: mvt_id })`.
  - **Tuyệt đối không** dùng `promoteId: "module_id"` trên MapLibre GL JS để tránh nghẽn bộ nhớ WebGL và lỗi ép kiểu số nguyên.

### 1.3. Bảng mã 4 lớp lỗi nhiệt & Phân hạng chuẩn IEC TS 62446-3:2017

| `class_id` (YOLO-OBB) | `fault_class` (DB & JSON) | Thứ tự ưu tiên (`severity_rank`) | Quy tắc gán `iec_coa_class` chuẩn IEC TS 62446-3 | Gợi ý `om_priority` |
| :---: | :--- | :---: | :--- | :---: |
| *(Không hộp)* | `'NORMAL'` | `0` | **`1`** (*CoA 1: No thermal abnormality*) — Chỉ lưu ở `solar_modules` | — |
| `0` | `'SingleHotSpot'` | `1` | **`3`** nếu $\Delta T_{\text{measured}} > 20.0^\circ\text{C}$; **`2`** nếu $\Delta T_{\text{measured}} \le 20.0^\circ\text{C}$ | `LOW` ($\le 10^\circ\text{C}$), `MEDIUM` ($10\text{–}20^\circ\text{C}$), `HIGH` ($> 20^\circ\text{C}$) |
| `1` | `'MultiHotSpot'` | `2` | **`3`** nếu $\Delta T_{\text{measured}} > 20.0^\circ\text{C}$; **`2`** nếu $\Delta T_{\text{measured}} \le 20.0^\circ\text{C}$ | `MEDIUM` / `HIGH` |
| `2` | `'Bypass'` | `3` | **`3`** (*CoA 3: Safety-relevant abnormality*) | `HIGH` |
| `3` | `'ModuleOpenCircuit'` | `4` | **`3`** (*CoA 3: Safety-relevant abnormality*) | `HIGH` |

- **Công thức quy đổi chuẩn bức xạ $1000\text{ W/m}^2$:**
  $$\Delta T_{\text{norm}} = \Delta T_{\text{measured}} \times \left(\frac{1000.0}{G_{\text{POA}}}\right)^{1.0}$$
  *(Hệ thống hiển thị cảnh báo độ tin cậy trên giao diện nếu $G_{\text{POA}} < 600.0\text{ W/m}^2$).*

---

## 2. CẤU HÌNH PHẦN CỨNG ĐA CAMERA (`CAMERA_PROFILES`) & KHỬ MÉO ỐNG KÍNH

### 2.1. Bảng thông số phần cứng đa cảm biến (Bản vá kỹ thuật #1)
Do nhà máy `BIM2` sử dụng tổ hợp `DJI_M2EA` + `DJI_P1` khác biệt với `DJI_ZH20T` tại 3 nhà máy còn lại, hệ thống tách bạch cấu hình phần cứng như sau:

```json
{
  "DJI_ZH20T": {
    "role": "THERMAL_INSPECTION_AND_RGB_PAIR",
    "rgb_resolution": [4056, 3040],
    "thermal_resolution": [640, 512],
    "thermal_focal_mm": 13.5,
    "thermal_pitch_um": 12.0,
    "thermal_decoder": "DJI_DIRP_SDK",
    "homography_profile_key": "zh20t_dual_sensor_h",
    "iec_cell_level_max_alt_m": 35.0
  },
  "DJI_M2EA": {
    "role": "THERMAL_INSPECTION_AND_RGB_PAIR",
    "rgb_resolution": [8000, 6000],
    "thermal_resolution": [640, 512],
    "thermal_focal_mm": 9.0,
    "thermal_pitch_um": 12.0,
    "thermal_decoder": "DJI_DIRP_SDK_OR_RJPG_CALIBRATED",
    "homography_profile_key": "m2ea_dual_sensor_h",
    "iec_cell_level_max_alt_m": 23.4,
    "note": "Ở 31m GSD nhiệt đạt ~4.13 cm/px -> đánh giá cấp Module/Sub-string, có xét Spot-Size Effect"
  },
  "DJI_P1": {
    "role": "ORTHOMOSAIC_BASE_MAP_ONLY",
    "rgb_resolution": [8192, 5460],
    "thermal_resolution": null,
    "note": "Chỉ phục vụ Module 1 (Ortho AI 1 & XYZ WebP Tiles), không đẩy vào hàng đợi lỗi nhiệt Module 2"
  }
}
```

### 2.2. Quy tắc Khử méo Ống kính (`DewarpData` + OpenCV `P=K`) & San tải Parser (Bản vá kỹ thuật #5)
1. **San tải Tuần 1:** TV3 (trong Rust khi upload) và TV1 (trong script kiểm kê Python) dùng chung logic đọc EXIF/XMP trích xuất `DewarpFlag`, `DewarpData`, `RtkFlag`, `RelativeAltitude`, `FlightYawDegree`, `GimbalYawDegree`, `strip_id`, `strip_sequence_idx` để TV2 không phải viết lại bộ parser.
2. Nếu `dewarp_applied_in_camera == true` (`DewarpFlag == 1`): giữ nguyên ảnh và tọa độ nhãn.
3. Nếu `dewarp_applied_in_camera == false` (`DewarpFlag == 0`):
   - Quy đổi tâm quang học từ chuẩn DJI sang chuẩn OpenCV:
     ```python
     cx_opencv = (W / 2.0) + cx_dewarp
     cy_opencv = (H / 2.0) + cy_dewarp
     ```
   - Khử méo đỉnh đa giác OBB **bắt buộc truyền `P=K`** để giữ nguyên hệ tọa độ pixel chứ không bị đưa về tọa độ chuẩn hóa $(x/z, y/z)$:
     ```python
     pts_undist_px = cv2.undistortPoints(
         pts_px.reshape(-1, 1, 2), K, dist_coeffs, R=None, P=K
     ).reshape(-1, 2)
     ```

---

## 3. HỢP ĐỒNG API PYTHON DÙNG CHUNG: `spatial_grid_index` (TV1 $\rightarrow$ TV2)

### 3.1. Chữ ký hàm Python cố định
TV1 bàn giao gói Python `packages/spatial_grid_index` (chốt cứng chữ ký hàm chậm nhất **23:59 ngày 29/11/2026**):

```python
from dataclasses import dataclass
from typing import List, Literal, Tuple
import numpy as np

@dataclass(frozen=True)
class ModuleCandidate:
    module_id: str
    mvt_id: int
    block_code: str
    string_code: str
    row_id: int                  # 1..4
    pin_index: int               # ID_Pin tăng dần theo trục u đã khóa hướng
    centroid_utm: Tuple[float, float]
    corners_utm: np.ndarray      # shape (4, 2), float64, thứ tự: TL, TR, BR, BL trên trục (u, v)

@dataclass(frozen=True)
class BoundaryLandmark:
    landmark_id: str
    landmark_type: Literal["TABLE_CORNER", "AISLE_GAP_EDGE", "BLOCK_BOUNDARY"]
    block_code: str
    string_code: str
    pin_index_anchor: int        # Cột pin sát biên dùng để khóa cứng chỉ số cột tuyệt đối
    point_utm: Tuple[float, float]

class SpatialGridIndex:
    def __init__(self, postgis_dsn_or_gpkg_dir: str) -> None: ...

    def get_candidates_in_radius(
        self,
        plant_code: str,
        x_utm: float,
        y_utm: float,
        radius_m: float = 0.524,
    ) -> List[ModuleCandidate]:
        """Tra cứu R-Tree + KD-Tree trong O(log N). Bán kính mặc định 52.4 cm (< 1/2 bước cột 1.13m)."""

    def get_block_string_boundary_landmarks(
        self,
        plant_code: str,
        bbox_utm: Tuple[float, float, float, float],  # (min_x, min_y, max_x, max_y)
    ) -> List[BoundaryLandmark]:
        """
        Trả về cả biên 2 đầu dải bay LẪN các khe đường nội bộ giữa các Block/String (AISLE_GAP_EDGE)
        để TV2 làm điểm neo đầu/cuối và điểm neo trung gian (Mid-strip Anchor).
        """

    def mass_spring_refine(
        self,
        plant_code: str,
        projected_centers_utm: np.ndarray,  # shape (M, 2)
        neighbor_graph_edges: List[Tuple[int, int, Literal["ALONG_U", "ALONG_V"]]],
    ) -> np.ndarray:
        """Làm mịn đám mây tâm tấm pin bằng hệ lò xo thưa O(I * M), trả về mảng (M, 2) đã khử nhiễu."""
```

### 3.2. Quy tắc Chống đứt gãy Dải bay trong `Bidirectional Strip Anchoring` (Bản vá kỹ thuật #2)
- **Chế độ chuẩn (`BIDIRECTIONAL`):** Khi dải ảnh có $\ge 2$ điểm neo biên (`start_anchor` và `end_anchor`, hoặc `mid_strip_anchor` khi bay qua đường nội bộ giữa 2 Block `AISLE_GAP_EDGE`) $\rightarrow$ thực hiện nội suy song phương biến đổi cứng `4-DoF Similarity / 6-DoF Affine` liên khung kết hợp kẹp tâm RTK ($\pm 10\text{ cm}$).
- **Chế độ suy giảm an toàn (`UNIDIRECTIONAL_RTK_CLAMPED`):** Khi drone ngắt dải về thay pin (RTH) khiến chỉ 1 đầu thấy biên lối đi $\rightarrow$ lan truyền `4-DoF Similarity` từ đầu có biên kết hợp kẹp cứng bán kính sai số RTK (`rtk_fix_flag == 50`, $\pm 10\text{ cm}$). Nếu `rtk_fix_flag != 50` (Float/Single) hoặc độ lệch tích lũy $> 35\text{ cm}$, tự động ép trạng thái `qc_status = 'PENDING_QC'`.

---

## 4. HỢP ĐỒNG REDIS QUEUE & PUB/SUB (`Rust Axum` $\leftrightarrow$ `Python AI Worker`)

### 4.1. Tên kênh Redis cố định
- **Hàng đợi Pipeline AI 1 (Ortho Gap Recovery):** `queue:solargis:ortho_jobs` (`BLPOP`)
- **Hàng đợi Pipeline AI 2 (Theo từng Dải bay `strip_id` để chạy Strip Anchoring):** `queue:solargis:strip_inspection_jobs` (`BLPOP`)
- **Kênh sự kiện thời gian thực (Worker bắn $\rightarrow$ Rust Axum đẩy SSE lên Web):** `pubsub:solargis:campaign_events` (`PUBLISH`)

### 4.2. JSON Schema Job đầu vào: `queue:solargis:strip_inspection_jobs`
*(Lưu ý thiết kế quan trọng: Đẩy theo **từng dải bay `strip_id`** thay vì từng ảnh rời rạc để Worker của TV2 có đủ chuỗi ảnh liên tiếp `strip_sequence_idx` phục vụ `Bidirectional Strip Anchoring` và `Multi-View Deduplication`).*

```json
{
  "job_id": "019330a4-7c90-7b21-8812-9a1b2c3d4e5f",
  "campaign_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "plant_id": 1,
  "plant_code": "TN19",
  "uav_camera_model": "DJI_ZH20T",
  "strip_id": "TN19_20260411_31M_STRIP_04",
  "env_params": {
    "irradiance_wm2": 845.0,
    "wind_speed_ms": 3.2,
    "ambient_temp_c": 32.5,
    "relative_humidity_pct": 68.0,
    "reflected_temp_c": 5.0,
    "emissivity": 0.85
  },
  "image_pairs": [
    {
      "image_pair_id": "3f2504e0-4f89-11d3-9a0c-0305e82c3301",
      "strip_sequence_idx": 1,
      "rgb_path": "/data/uploads/TN19/camp_01/DJI_20260411101522_0001_W.JPG",
      "thermal_path": "/data/uploads/TN19/camp_01/DJI_20260411101522_0001_T.JPG",
      "gps_x_utm": 268412.35,
      "gps_y_utm": 1265890.12,
      "recorded_agl_m": 30.9,
      "gimbal_yaw": -89.4,
      "gimbal_pitch": -90.0,
      "rtk_fix_flag": 50,
      "dewarp_applied_in_camera": false,
      "dewarp_params": {
        "fx": 2912.45,
        "fy": 2911.88,
        "cx_opencv": 2032.15,
        "cy_opencv": 1518.40,
        "k1": -0.0412,
        "k2": 0.0185,
        "p1": -0.0003,
        "p2": 0.0002,
        "k3": -0.0061
      }
    }
  ]
}
```

### 4.3. JSON Schema Sự kiện trả về: `pubsub:solargis:campaign_events`
Sau khi Python Worker UPSERT kết quả vào `module_inspection_logs` (kích hoạt Trigger PostGIS), Worker `PUBLISH` gói tin siêu nhẹ sau để Rust Axum chuyển tiếp ngay qua SSE lên trình duyệt gọi `map.setFeatureState`:

```json
{
  "event_type": "STRIP_PROCESSED",
  "campaign_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "plant_id": 1,
  "is_latest_campaign": true,
  "progress": {
    "processed_pairs": 120,
    "total_pairs": 640
  },
  "updated_modules": [
    {
      "mvt_id": 14829,
      "module_id": "tn19_block1_string4_00458",
      "fault_class": "SingleHotSpot",
      "iec_coa_class": 3,
      "om_priority": "HIGH",
      "temp_delta_measured_c": 24.6,
      "temp_delta_norm_1000wm2_c": 29.1,
      "qc_status": "AUTO_VERIFIED"
    }
  ]
}
```

---

## 5. LƯỢC ĐỒ 7 BẢNG POSTGIS & TRIGGER AN TOÀN INSERT / UPDATE / DELETE (TV3)

### 5.1. Lược đồ DDL 7 bảng cốt lõi (`EPSG:32649`)

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Bảng 1: Nhà máy điện mặt trời
CREATE TABLE solar_plants (
    id SERIAL PRIMARY KEY,
    plant_code VARCHAR(16) UNIQUE NOT NULL CHECK (plant_code IN ('TN19', 'BIM2', 'TNDL', 'TT12')),
    plant_name VARCHAR(128) NOT NULL,
    capacity_mwp DOUBLE PRECISION,
    pmtiles_url TEXT NOT NULL,
    boundary_geom GEOMETRY(MultiPolygon, 32649) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Bảng 2: Khu vực / Block inverter
CREATE TABLE solar_blocks (
    id SERIAL PRIMARY KEY,
    plant_id INT NOT NULL REFERENCES solar_plants(id) ON DELETE CASCADE,
    block_code VARCHAR(32) NOT NULL,
    geom GEOMETRY(MultiPolygon, 32649) NOT NULL,
    UNIQUE (plant_id, block_code)
);

-- Bảng 3: Dãy bàn pin (String / Table)
CREATE TABLE solar_strings (
    id SERIAL PRIMARY KEY,
    block_id INT NOT NULL REFERENCES solar_blocks(id) ON DELETE CASCADE,
    string_code VARCHAR(32) NOT NULL,
    tilt_deg DOUBLE PRECISION NOT NULL DEFAULT 12.0,
    azimuth_deg DOUBLE PRECISION NOT NULL DEFAULT 180.0,
    geom GEOMETRY(Polygon, 32649) NOT NULL,
    UNIQUE (block_id, string_code)
);

-- Bảng 4: Tấm pin mặt trời (Master Digital Twin Inventory)
CREATE TABLE solar_modules (
    mvt_id BIGSERIAL UNIQUE NOT NULL,
    module_id VARCHAR(64) PRIMARY KEY,
    plant_id INT NOT NULL REFERENCES solar_plants(id) ON DELETE CASCADE,
    block_id INT NOT NULL REFERENCES solar_blocks(id) ON DELETE CASCADE,
    string_id INT NOT NULL REFERENCES solar_strings(id) ON DELETE CASCADE,
    row_id SMALLINT NOT NULL CHECK (row_id BETWEEN 1 AND 6),
    pin_index INT NOT NULL CHECK (pin_index > 0),
    is_distorted_recovered BOOLEAN NOT NULL DEFAULT FALSE,
    current_health_status VARCHAR(32) NOT NULL DEFAULT 'NORMAL'
        CHECK (current_health_status IN ('NORMAL', 'SingleHotSpot', 'MultiHotSpot', 'Bypass', 'ModuleOpenCircuit')),
    current_coa_class SMALLINT NOT NULL DEFAULT 1 CHECK (current_coa_class IN (1, 2, 3)),
    centroid_geom GEOMETRY(Point, 32649) NOT NULL,
    geom GEOMETRY(Polygon, 32649) NOT NULL
);

CREATE INDEX idx_solar_modules_geom ON solar_modules USING GIST (geom);
CREATE INDEX idx_solar_modules_centroid ON solar_modules USING GIST (centroid_geom);
CREATE INDEX idx_solar_modules_plant_mvt ON solar_modules (plant_id, mvt_id);

-- Bảng 5: Chiến dịch / Đợt bay kiểm tra UAV
CREATE TABLE flight_campaigns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plant_id INT NOT NULL REFERENCES solar_plants(id) ON DELETE CASCADE,
    campaign_name VARCHAR(128) NOT NULL,
    flight_date TIMESTAMPTZ NOT NULL,
    uav_camera_model VARCHAR(32) NOT NULL CHECK (uav_camera_model IN ('DJI_ZH20T', 'DJI_M2EA', 'DJI_P1')),
    irradiance_wm2 DOUBLE PRECISION NOT NULL DEFAULT 850.0,
    ambient_temp_c DOUBLE PRECISION NOT NULL DEFAULT 32.0,
    wind_speed_ms DOUBLE PRECISION NOT NULL DEFAULT 2.5,
    status VARCHAR(32) NOT NULL DEFAULT 'PROCESSING'
        CHECK (status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Bảng 6: Cặp ảnh thô RGB + Nhiệt theo dải bay
CREATE TABLE raw_image_pairs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID NOT NULL REFERENCES flight_campaigns(id) ON DELETE CASCADE,
    strip_id VARCHAR(64) NOT NULL,
    strip_sequence_idx INT NOT NULL,
    rgb_path TEXT NOT NULL,
    thermal_path TEXT,
    recorded_agl_m DOUBLE PRECISION NOT NULL,
    gimbal_yaw DOUBLE PRECISION NOT NULL,
    gimbal_pitch DOUBLE PRECISION NOT NULL,
    rtk_fix_flag SMALLINT NOT NULL DEFAULT 50,
    dewarp_applied_in_camera BOOLEAN NOT NULL DEFAULT FALSE,
    dewarp_params JSONB,
    camera_center_geom GEOMETRY(Point, 32649) NOT NULL
);

CREATE INDEX idx_raw_image_pairs_campaign_strip ON raw_image_pairs (campaign_id, strip_id, strip_sequence_idx);

-- Bảng 7: Nhật ký phát hiện lỗi nhiệt & Hậu kiểm QC
CREATE TABLE module_inspection_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID NOT NULL REFERENCES flight_campaigns(id) ON DELETE CASCADE,
    module_id VARCHAR(64) NOT NULL REFERENCES solar_modules(module_id) ON DELETE CASCADE,
    best_image_pair_id UUID REFERENCES raw_image_pairs(id) ON DELETE SET NULL,
    fault_class VARCHAR(32) NOT NULL
        CHECK (fault_class IN ('SingleHotSpot', 'MultiHotSpot', 'Bypass', 'ModuleOpenCircuit')),
    iec_coa_class SMALLINT NOT NULL CHECK (iec_coa_class IN (2, 3)),
    om_priority VARCHAR(16) NOT NULL CHECK (om_priority IN ('LOW', 'MEDIUM', 'HIGH')),
    confidence DOUBLE PRECISION NOT NULL,
    temp_max_c DOUBLE PRECISION NOT NULL,
    temp_median_ref_c DOUBLE PRECISION NOT NULL,
    temp_delta_measured_c DOUBLE PRECISION NOT NULL,
    temp_delta_norm_1000wm2_c DOUBLE PRECISION NOT NULL,
    anchoring_mode VARCHAR(32) NOT NULL DEFAULT 'BIDIRECTIONAL'
        CHECK (anchoring_mode IN ('BIDIRECTIONAL', 'UNIDIRECTIONAL_RTK_CLAMPED')),
    qc_status VARCHAR(32) NOT NULL DEFAULT 'AUTO_VERIFIED',
    reviewer_note TEXT,
    bbox_thermal_px JSONB NOT NULL,
    hotspot_geom GEOMETRY(Polygon, 32649),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_qc_status CHECK (
        qc_status IN ('AUTO_VERIFIED', 'PENDING_QC', 'HUMAN_CONFIRMED', 'HUMAN_CORRECTED', 'QC_REJECTED')
    )
);

CREATE INDEX idx_inspection_logs_campaign_module ON module_inspection_logs (campaign_id, module_id);
```

### 5.2. Trigger Đồng bộ Sức khỏe Tấm pin An toàn `INSERT / UPDATE / DELETE` (Bản vá kỹ thuật #3)
Xử lý trọn vẹn cả 3 thao tác `INSERT`, `UPDATE` (kể cả khi kỹ sư QC sửa mã `OLD.module_id` sang tấm pin bên cạnh `NEW.module_id` hoặc bác bỏ lỗi giả `QC_REJECTED`) và `DELETE` (tự động trả tấm pin về `'NORMAL'` / CoA 1 nếu không còn lỗi nào khác trong đợt bay mới nhất):

```sql
-- Hàm con tính lại trạng thái sức khỏe cho 1 tấm pin cụ thể tại đợt bay mới nhất
CREATE OR REPLACE FUNCTION fn_recompute_single_module_health(
    p_campaign_id UUID,
    p_module_id VARCHAR
) RETURNS VOID AS $$
DECLARE
    v_plant_id INT;
    v_camp_date TIMESTAMPTZ;
    v_max_date TIMESTAMPTZ;
    v_top_fault VARCHAR;
    v_top_coa SMALLINT;
BEGIN
    IF p_module_id IS NULL THEN
        RETURN;
    END IF;

    SELECT plant_id, flight_date INTO v_plant_id, v_camp_date
    FROM flight_campaigns WHERE id = p_campaign_id;

    SELECT MAX(flight_date) INTO v_max_date
    FROM flight_campaigns WHERE plant_id = v_plant_id;

    -- Chỉ cập nhật bảng gốc solar_modules nếu sự kiện thuộc đợt bay mới nhất của nhà máy
    IF v_camp_date = v_max_date THEN
        SELECT fault_class, iec_coa_class INTO v_top_fault, v_top_coa
        FROM module_inspection_logs
        WHERE campaign_id = p_campaign_id
          AND module_id = p_module_id
          AND qc_status <> 'QC_REJECTED'
        ORDER BY iec_coa_class DESC,
                 CASE fault_class
                     WHEN 'ModuleOpenCircuit' THEN 4
                     WHEN 'Bypass' THEN 3
                     WHEN 'MultiHotSpot' THEN 2
                     ELSE 1
                 END DESC,
                 temp_delta_measured_c DESC
        LIMIT 1;

        -- Nếu không còn lỗi hợp lệ nào (do DELETE hoặc QC_REJECTED), tự động trả về NORMAL & CoA 1
        UPDATE solar_modules
        SET current_health_status = COALESCE(v_top_fault, 'NORMAL'),
            current_coa_class = COALESCE(v_top_coa, 1)
        WHERE module_id = p_module_id;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Trigger chính bắt đủ INSERT, UPDATE, DELETE
CREATE OR REPLACE FUNCTION fn_sync_module_health_after_inspection()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        PERFORM fn_recompute_single_module_health(OLD.campaign_id, OLD.module_id);
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        -- Nếu kỹ sư QC đổi gán lỗi từ tấm pin cũ sang tấm pin bên cạnh, tính lại cho cả tấm cũ
        IF OLD.module_id IS DISTINCT FROM NEW.module_id THEN
            PERFORM fn_recompute_single_module_health(OLD.campaign_id, OLD.module_id);
        END IF;
        PERFORM fn_recompute_single_module_health(NEW.campaign_id, NEW.module_id);
        RETURN NEW;
    ELSE -- INSERT
        PERFORM fn_recompute_single_module_health(NEW.campaign_id, NEW.module_id);
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_sync_module_health_after_inspection ON module_inspection_logs;
CREATE TRIGGER trg_sync_module_health_after_inspection
AFTER INSERT OR UPDATE OR DELETE ON module_inspection_logs
FOR EACH ROW EXECUTE FUNCTION fn_sync_module_health_after_inspection();
```

---

## 6. HỢP ĐỒNG REST API & GIAO THỨC MAPLIBRE GL JS (`Rust Axum` $\leftrightarrow$ `React/Next.js`)

### 6.1. Các Endpoint bắt buộc trên Rust Axum
1. **`GET /api/tiles/{plant_id}/{z}/{x}/{y}.mvt`**
   - Header trả về: `Content-Type: application/vnd.mapbox-vector-tile`, `Cache-Control: public, max-age=3600`.
   - Layer name bên trong MVT: `solar_modules_layer`.
   - Top-level Feature ID: `mvt_id` (`uint64`); thuộc tính đi kèm: `mvt_id_prop`, `module_id`, `row_id`, `pin_index`, `is_distorted_recovered`, `current_health_status`, `current_coa_class`.
2. **`GET /api/campaigns/{campaign_id}/fault_states`**
   - Phục vụ chuyển đổi đợt bay lịch sử (~20 KB JSON):
     ```json
     {
       "campaign_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
       "is_latest": false,
       "irradiance_wm2": 845.0,
       "faults": [
         {
           "mvt_id": 14829,
           "fault_class": "SingleHotSpot",
           "iec_coa_class": 3,
           "om_priority": "HIGH",
           "qc_status": "AUTO_VERIFIED"
         }
       ]
     }
     ```
3. **`PATCH /api/inspections/{log_id}/qc`**
   - Body JSON khi kỹ sư duyệt QC:
     ```json
     {
       "qc_status": "HUMAN_CORRECTED",
       "corrected_module_id": "tn19_block1_string4_00459",
       "reviewer_note": "Lệch 1 cột ở biên dải cắt ngắt pin"
     }
     ```
   - Response trả về mảng `affected_modules` (gồm cả `old_mvt_id` và `new_mvt_id` cùng `current_coa_class` mới) để Frontend cập nhật màu tức thì mà không cần tải lại Vector Tile.
4. **`POST /api/campaigns/{campaign_id}/report.pdf`**
   - Bắt buộc chạy trình biên dịch Typst bên trong `tokio::task::spawn_blocking` để không chặn bất đồng bộ event loop của Tokio.

### 6.2. Quy tắc Bất biến trên Frontend MapLibre GL JS (Chống Ghost State & Lỗi Filter #6213)

```typescript
// 1. Khi đổi đợt bay (Campaign Switcher):
map.removeFeatureState({ source: "solar_modules", sourceLayer: "solar_modules_layer" });
for (const item of data.faults) {
  map.setFeatureState(
    { source: "solar_modules", sourceLayer: "solar_modules_layer", id: item.mvt_id },
    { coa_class: item.iec_coa_class, fault_class: item.fault_class, om_priority: item.om_priority }
  );
}

// Tuyệt đối fallback về 1 (CoA 1 Normal) khi xem lịch sử, KHÔNG fallback về ["get", "current_coa_class"]
const activeCoaExpr = data.is_latest
  ? ["coalesce", ["feature-state", "coa_class"], ["get", "current_coa_class"]]
  : ["coalesce", ["feature-state", "coa_class"], 1];

map.setPaintProperty("solar-modules-fill", "fill-color", [
  "match", activeCoaExpr,
  3, "#ef4444", // CoA 3 - Đỏ
  2, "#f59e0b", // CoA 2 - Vàng cam
  "#22c55e"     // CoA 1 - Xanh lá (Normal)
]);

// 2. Khi lọc theo lỗi / CoA (Lách giới hạn MapLibre Issue #6213):
if (activeFilter === "ALL") {
  map.setFilter("solar-modules-fill", null);
} else {
  const matchedMvtIds: number[] = currentFaultList
    .filter(f => matchesFilter(f, activeFilter))
    .map(f => f.mvt_id);
  map.setFilter("solar-modules-fill", ["in", ["id"], ["literal", matchedMvtIds]]);
}
```

---

## 7. QUY CHUẨN MÔI TRƯỜNG DOCKER & CÔNG CỤ BUILD BẢN ĐỒ (Bản vá kỹ thuật #4)

### 7.1. Container AI Worker (`Dockerfile.worker`)
- Bắt buộc khai báo `FROM --platform=linux/amd64 nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04` (hoặc `python:3.11-slim` với `--platform=linux/amd64` khi chạy CPU trên Mac Apple Silicon M1/M2/M3) vì thư viện gốc `libdirp.so` của DJI Thermal SDK chỉ biên dịch cho kiến trúc `x86_64`.
- Toàn bộ các tệp `libdirp.so`, `libv_dirp.so`, `libv_iirp.so`, `libv_list.ini` phải nằm chung một thư mục `/opt/dji_tsdk/` và khai báo:
  ```dockerfile
  ENV LD_LIBRARY_PATH="/opt/dji_tsdk:${LD_LIBRARY_PATH}"
  ```

### 7.2. Quy trình chuẩn xuất XYZ WebP $\rightarrow$ PMTiles (TV1 – Chốt bàn giao TN19 ngày 18/11/2026)

```bash
# Bước 1: Cắt XYZ WebP bằng container GDAL chính thức có sẵn libwebp
docker run --rm -e GDAL_CACHEMAX=4096 -v "$(pwd):/work" ghcr.io/osgeo/gdal:ubuntu-full-3.8.4 \
  gdal2tiles.py --xyz --exclude --processes=8 -z 15-21 \
  --tiledriver=WEBP --webp-quality=85 \
  /work/SonarPanel.tif /work/tiles_tn19/

# Bước 2: Đóng gói thành 1 file tĩnh .pmtiles duy nhất (qua mb-util + pmtiles CLI)
mb-util --image_format=webp --scheme=xyz ./tiles_tn19 ./tn19_ortho.mbtiles
pmtiles convert ./tn19_ortho.mbtiles ./tn19_ortho.pmtiles
```

---

## 8. CAM KẾT MỐC BÀN GIAO ĐƯỜNG GĂNG (CRITICAL PATH HANDOFFS)

| Mốc thời gian | Bên giao $\rightarrow$ Bên nhận | Sản phẩm bàn giao bắt buộc (Deliverables) |
| :---: | :---: | :--- |
| **17/11/2026** | Cả nhóm | Chốt Mẫu ĐATN-01, gom đủ `.gpkg` 4 nhà máy, commit `DATA_CONTRACT.md` lên nhánh `main` + Bảng kiểm kê thông số 4 trang trại. |
| **18/11/2026** | TV1 $\rightarrow$ TV3 | Gói `tn19_ortho.pmtiles` (hoặc `tiles_tn19/`) của Thuận Nam 19 để TV3 dựng bản đồ WebGL ngay trong Tuần 1–2. |
| **22/11/2026** | TV3 $\rightarrow$ TV1, TV2 | Docker Compose chạy sẵn PostGIS 16-3.4 (đủ 7 bảng + Trigger `INSERT/UPDATE/DELETE` + hàm `ST_AsMVT`) & Redis 7. |
| **29/11/2026** | TV1 $\rightarrow$ TV2 | Khóa cứng chữ ký hàm `spatial_grid_index` + Báo cáo Mốc M1 (20%). |
| **06/12/2026** | Cả nhóm | Nối thông Mock End-to-End Pipeline 10 cặp ảnh mẫu từ Giao diện Web $\rightarrow$ Rust Axum $\rightarrow$ Redis $\rightarrow$ Python Worker $\rightarrow$ PostGIS $\rightarrow$ SSE đổi màu bản đồ 60 FPS. |

---

## 9. CHỮ KÝ XÁC NHẬN KHÓA HỢP ĐỒNG (`LOCKED FREEZE`)

Mọi thay đổi đối với tên trường JSON, kiểu dữ liệu cột PostGIS, chữ ký hàm `spatial_grid_index` hoặc biểu thức màu MapLibre sau ngày **16/11/2026** đều phải tạo Pull Request có đủ sự đồng thuận (Approve) của cả 3 thành viên.

- **Thành viên 1 (Module 1 – Khôi phục Lưới Tấm pin Orthomosaic & Spatial Index):** ______________________
- **Thành viên 2 (Module 2 – AI Đa phương thức Nhiệt–Quang & Strip Anchoring):** ______________________
- **Thành viên 3 (Module 3 – Rust Axum Backend, PostGIS, MapLibre 60 FPS & Typst):** ______________________