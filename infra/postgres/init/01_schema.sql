-- =============================================================================
-- SolarGIS Digital Twin - 01_schema.sql
-- DDL 7 Bảng Cốt lõi PostGIS (Hệ quy chiếu chuẩn UTM Zone 49N - EPSG:32649)
-- Tham chiếu: DATA_CONTRACT.md (Mục 5.1) & Đề cương ĐATN V6 (Mục 3.2)
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- -----------------------------------------------------------------------------
-- Bảng 1: Nhà máy điện mặt trời (solar_plants)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS solar_plants (
    id SERIAL PRIMARY KEY,
    plant_code VARCHAR(16) UNIQUE NOT NULL CHECK (plant_code IN ('TN19', 'BIM2', 'TNDL', 'TT12')),
    plant_name VARCHAR(128) NOT NULL,
    capacity_mwp DOUBLE PRECISION,
    crs_epsg INT NOT NULL DEFAULT 32649,
    pmtiles_url TEXT NOT NULL,
    raster_tile_url_template TEXT,
    boundary_geom GEOMETRY(MultiPolygon, 32649) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_solar_plants_boundary ON solar_plants USING GIST (boundary_geom);

-- -----------------------------------------------------------------------------
-- Bảng 2: Khu vực / Block inverter (solar_blocks)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS solar_blocks (
    id SERIAL PRIMARY KEY,
    plant_id INT NOT NULL REFERENCES solar_plants(id) ON DELETE CASCADE,
    block_code VARCHAR(32) NOT NULL,
    geom GEOMETRY(MultiPolygon, 32649) NOT NULL,
    UNIQUE (plant_id, block_code)
);

CREATE INDEX IF NOT EXISTS idx_solar_blocks_geom ON solar_blocks USING GIST (geom);

-- -----------------------------------------------------------------------------
-- Bảng 3: Dãy bàn pin (solar_strings)
-- Lưu kèm hệ trục nội tại PCA (pca_axis_u_x, pca_axis_u_y) đã khóa hướng từng hàng
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS solar_strings (
    id SERIAL PRIMARY KEY,
    block_id INT NOT NULL REFERENCES solar_blocks(id) ON DELETE CASCADE,
    string_code VARCHAR(32) NOT NULL,
    tilt_deg DOUBLE PRECISION NOT NULL DEFAULT 12.0,
    azimuth_deg DOUBLE PRECISION NOT NULL DEFAULT 180.0,
    pca_axis_u_x DOUBLE PRECISION,
    pca_axis_u_y DOUBLE PRECISION,
    row_count SMALLINT NOT NULL DEFAULT 4,
    expected_modules INT,
    geom GEOMETRY(Polygon, 32649) NOT NULL,
    UNIQUE (block_id, string_code)
);

CREATE INDEX IF NOT EXISTS idx_solar_strings_geom ON solar_strings USING GIST (geom);

-- -----------------------------------------------------------------------------
-- Bảng 4: Tấm pin mặt trời - Master Digital Twin Inventory (solar_modules)
-- Chuẩn hóa current_coa_class DEFAULT 1 (CoA 1 = Normal) theo IEC TS 62446-3:2017
-- Khóa nguyên mvt_id BIGSERIAL dùng trực tiếp làm Feature ID cho ST_AsMVT
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS solar_modules (
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
    current_coa_class SMALLINT NOT NULL DEFAULT 1
        CHECK (current_coa_class IN (1, 2, 3)),
    centroid_geom GEOMETRY(Point, 32649) NOT NULL,
    geom GEOMETRY(Polygon, 32649) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_solar_modules_geom ON solar_modules USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_solar_modules_centroid ON solar_modules USING GIST (centroid_geom);
CREATE INDEX IF NOT EXISTS idx_solar_modules_plant_mvt ON solar_modules (plant_id, mvt_id);

-- -----------------------------------------------------------------------------
-- Bảng 5: Chiến dịch / Đợt bay kiểm tra UAV (flight_campaigns)
-- Lưu đầy đủ 4 tham số vật lý cho DJI Thermal SDK (dirp) & chuẩn IEC TS 62446-3
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS flight_campaigns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plant_id INT NOT NULL REFERENCES solar_plants(id) ON DELETE CASCADE,
    campaign_name VARCHAR(128) NOT NULL,
    flight_date TIMESTAMPTZ NOT NULL,
    uav_camera_model VARCHAR(32) NOT NULL CHECK (uav_camera_model IN ('DJI_ZH20T', 'DJI_M2EA', 'DJI_P1')),
    planned_altitude_m DOUBLE PRECISION,
    recorded_altitude_m DOUBLE PRECISION,
    gsd_rgb_cm DOUBLE PRECISION,
    gsd_thermal_cm DOUBLE PRECISION,
    irradiance_wm2 DOUBLE PRECISION NOT NULL DEFAULT 850.0,
    ambient_temp_c DOUBLE PRECISION NOT NULL DEFAULT 32.0,
    wind_speed_ms DOUBLE PRECISION NOT NULL DEFAULT 2.5,
    relative_humidity_pct DOUBLE PRECISION NOT NULL DEFAULT 70.0,
    reflected_temp_c DOUBLE PRECISION NOT NULL DEFAULT 5.0,
    emissivity DOUBLE PRECISION NOT NULL DEFAULT 0.85,
    status VARCHAR(32) NOT NULL DEFAULT 'PROCESSING'
        CHECK (status IN ('PENDING', 'UPLOADED', 'PROCESSING', 'PROCESSING_AI', 'COMPLETED', 'FAILED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_flight_campaigns_plant_date ON flight_campaigns (plant_id, flight_date DESC);

-- -----------------------------------------------------------------------------
-- Bảng 6: Cặp ảnh thô RGB + Nhiệt theo dải bay (raw_image_pairs)
-- Lưu cờ DewarpFlag và thứ tự dải bay phục vụ Bidirectional Strip Anchoring
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_image_pairs (
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

CREATE INDEX IF NOT EXISTS idx_raw_image_pairs_campaign_strip ON raw_image_pairs (campaign_id, strip_id, strip_sequence_idx);
CREATE INDEX IF NOT EXISTS idx_raw_image_pairs_center_geom ON raw_image_pairs USING GIST (camera_center_geom);

-- -----------------------------------------------------------------------------
-- Bảng 7: Nhật ký phát hiện lỗi nhiệt & Hậu kiểm QC (module_inspection_logs)
-- Chỉ ghi nhận các phát hiện lỗi thuộc iec_coa_class IN (2, 3) đã khử trùng lặp
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS module_inspection_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID NOT NULL REFERENCES flight_campaigns(id) ON DELETE CASCADE,
    module_id VARCHAR(64) NOT NULL REFERENCES solar_modules(module_id) ON DELETE CASCADE,
    best_image_pair_id UUID REFERENCES raw_image_pairs(id) ON DELETE SET NULL,
    observation_count SMALLINT NOT NULL DEFAULT 1,
    fault_class VARCHAR(32) NOT NULL
        CHECK (fault_class IN ('SingleHotSpot', 'MultiHotSpot', 'Bypass', 'ModuleOpenCircuit')),
    iec_coa_class SMALLINT NOT NULL CHECK (iec_coa_class IN (2, 3)),
    om_priority VARCHAR(16) NOT NULL CHECK (om_priority IN ('LOW', 'MEDIUM', 'HIGH')),
    confidence DOUBLE PRECISION NOT NULL,
    temp_max_c DOUBLE PRECISION NOT NULL,
    temp_median_ref_c DOUBLE PRECISION NOT NULL,
    temp_delta_measured_c DOUBLE PRECISION NOT NULL,
    temp_delta_norm_1000wm2_c DOUBLE PRECISION NOT NULL,
    spatial_iou DOUBLE PRECISION,
    centroid_error_cm DOUBLE PRECISION,
    hungarian_margin DOUBLE PRECISION,
    anchoring_mode VARCHAR(32) NOT NULL DEFAULT 'BIDIRECTIONAL'
        CHECK (anchoring_mode IN ('BIDIRECTIONAL', 'UNIDIRECTIONAL_RTK_CLAMPED')),
    qc_status VARCHAR(32) NOT NULL DEFAULT 'AUTO_VERIFIED',
    reviewer_note TEXT,
    crop_rgb_url TEXT,
    crop_thermal_url TEXT,
    bbox_thermal_px JSONB NOT NULL,
    hotspot_geom GEOMETRY(Polygon, 32649),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_campaign_module_fault UNIQUE (campaign_id, module_id, fault_class),
    CONSTRAINT chk_qc_status CHECK (
        qc_status IN ('AUTO_VERIFIED', 'PENDING_QC', 'HUMAN_CONFIRMED', 'HUMAN_CORRECTED', 'QC_REJECTED')
    )
);

CREATE INDEX IF NOT EXISTS idx_inspection_logs_campaign_module ON module_inspection_logs (campaign_id, module_id);
CREATE INDEX IF NOT EXISTS idx_inspection_logs_qc_status ON module_inspection_logs (campaign_id, qc_status);
