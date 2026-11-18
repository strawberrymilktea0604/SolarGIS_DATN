-- =============================================================================
-- SolarGIS Digital Twin - 04_seed_and_benchmark.sql
-- Kịch bản:
--   1. Khởi tạo danh mục 4 trang trại Ninh Thuận (TN19, BIM2, TNDL, TT12)
--   2. Hàm sinh lưới mẫu 36.544 tấm pin Thuận Nam 19 (nếu chưa nạp file .gpkg thật)
--      để kiểm thử ngay câu lệnh EXPLAIN ANALYZE của Đầu việc 1.6 (Tuần 1)
--   3. Khảo sát hiệu năng: Xuất GeoJSON thô vs Xuất Vector Tiles động ST_AsMVT
-- =============================================================================

-- 1. Khởi tạo 4 trang trại trong bảng solar_plants (nếu chưa tồn tại)
INSERT INTO solar_plants (plant_code, plant_name, capacity_mwp, crs_epsg, pmtiles_url, raster_tile_url_template, boundary_geom)
VALUES
    ('TN19', 'Nhà máy Điện mặt trời Thuận Nam 19', 49.0, 32649, '/tiles/tn19_ortho.pmtiles', '/tiles/tn19/{z}/{x}/{y}.webp',
     ST_GeomFromText('MULTIPOLYGON(((270000 1265000, 271500 1265000, 271500 1266500, 270000 1266500, 270000 1265000)))', 32649)),
    ('BIM2', 'Nhà máy Điện mặt trời BIM 2', 250.0, 32649, '/tiles/bim2_ortho.pmtiles', '/tiles/bim2/{z}/{x}/{y}.webp',
     ST_GeomFromText('MULTIPOLYGON(((272000 1265000, 273500 1265000, 273500 1266500, 272000 1266500, 272000 1265000)))', 32649)),
    ('TNDL', 'Nhà máy Điện mặt trời Thuận Nam Đức Long', 50.0, 32649, '/tiles/tndl_ortho.pmtiles', '/tiles/tndl/{z}/{x}/{y}.webp',
     ST_GeomFromText('MULTIPOLYGON(((274000 1265000, 275500 1265000, 275500 1266500, 274000 1266500, 274000 1265000)))', 32649)),
    ('TT12', 'Nhà máy Điện mặt trời Thiên Tân 1.2', 100.0, 32649, '/tiles/tt12_ortho.pmtiles', '/tiles/tt12/{z}/{x}/{y}.webp',
     ST_GeomFromText('MULTIPOLYGON(((276000 1265000, 277500 1265000, 277500 1266500, 276000 1266500, 276000 1265000)))', 32649))
ON CONFLICT (plant_code) DO NOTHING;

-- 2. Hàm tiện ích seed_synthetic_tn19_36544_modules() phục vụ đo kiểm EXPLAIN ANALYZE
--    khi chờ TV1 bàn giao đầy đủ 4 file .gpkg
CREATE OR REPLACE FUNCTION seed_synthetic_tn19_modules(p_target_count INT DEFAULT 36544)
RETURNS VOID AS $$
DECLARE
    v_plant_id INT;
    v_block_id INT;
    v_string_id INT;
    v_b INT;
    v_s INT;
    v_r INT;
    v_p INT;
    v_inserted INT := 0;
    v_x0 DOUBLE PRECISION;
    v_y0 DOUBLE PRECISION;
    v_poly GEOMETRY(Polygon, 32649);
BEGIN
    SELECT id INTO v_plant_id FROM solar_plants WHERE plant_code = 'TN19';
    IF EXISTS (SELECT 1 FROM solar_modules WHERE plant_id = v_plant_id LIMIT 1) THEN
        RAISE NOTICE 'Bảng solar_modules đã có dữ liệu của TN19, bỏ qua bước sinh lưới giả lập.';
        RETURN;
    END IF;

    -- Chia thành 6 Block, ~25 String/Block, 4 Row/String, ~62 tấm/Row (~36.544 tấm pin)
    FOR v_b IN 1..6 LOOP
        INSERT INTO solar_blocks (plant_id, block_code, geom)
        VALUES (
            v_plant_id,
            'block' || v_b,
            ST_MakeEnvelope(270100 + (v_b - 1) * 200, 1265100, 270100 + v_b * 200 - 10, 1265900, 32649)::GEOMETRY(MultiPolygon, 32649)
        )
        ON CONFLICT (plant_id, block_code) DO UPDATE SET block_code = EXCLUDED.block_code
        RETURNING id INTO v_block_id;

        FOR v_s IN 1..25 LOOP
            INSERT INTO solar_strings (block_id, string_code, pca_axis_u_x, pca_axis_u_y, row_count, expected_modules, geom)
            VALUES (
                v_block_id,
                'string' || v_s,
                1.0, 0.0, 4, 248,
                ST_MakeEnvelope(
                    270100 + (v_b - 1) * 200,
                    1265100 + (v_s - 1) * 12,
                    270100 + (v_b - 1) * 200 + 75,
                    1265100 + (v_s - 1) * 12 + 9.5,
                    32649
                )
            )
            ON CONFLICT (block_id, string_code) DO UPDATE SET string_code = EXCLUDED.string_code
            RETURNING id INTO v_string_id;

            FOR v_r IN 1..4 LOOP
                FOR v_p IN 1..62 LOOP
                    EXIT WHEN v_inserted >= p_target_count;
                    v_x0 := 270100.0 + (v_b - 1) * 200.0 + (v_p - 1) * 1.13;
                    v_y0 := 1265100.0 + (v_s - 1) * 12.0 + (v_r - 1) * 2.27;
                    v_poly := ST_MakeEnvelope(v_x0, v_y0, v_x0 + 1.08, v_y0 + 2.15, 32649);

                    INSERT INTO solar_modules (
                        module_id, plant_id, block_id, string_id, row_id, pin_index,
                        is_distorted_recovered, current_health_status, current_coa_class,
                        centroid_geom, geom
                    ) VALUES (
                        FORMAT('tn19_block%s_string%s_%s', v_b, v_s, LPAD(((v_r - 1) * 62 + v_p)::TEXT, 5, '0')),
                        v_plant_id, v_block_id, v_string_id, v_r, (v_r - 1) * 62 + v_p,
                        FALSE, 'NORMAL', 1,
                        ST_Centroid(v_poly), v_poly
                    );
                    v_inserted := v_inserted + 1;
                END LOOP;
                EXIT WHEN v_inserted >= p_target_count;
            END LOOP;
            EXIT WHEN v_inserted >= p_target_count;
        END LOOP;
        EXIT WHEN v_inserted >= p_target_count;
    END LOOP;

    RAISE NOTICE 'Đã khởi tạo thành công % tấm pin chuẩn cho nhà máy Thuận Nam 19.', v_inserted;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- 3. CÂU LỆNH KHẢO SÁT EXPLAIN ANALYZE (ĐẦU VIỆC 1.6 - CHƯƠNG 2 & CHƯƠNG 4)
-- Cách chạy trong psql:
--   SELECT seed_synthetic_tn19_modules(36544);
--   ANALYZE solar_modules;
--
-- [A] Đo thời gian & kích thước xuất GeoJSON thô toàn trang trại (~18 MB, > 800 ms):
--   EXPLAIN (ANALYZE, BUFFERS)
--   SELECT jsonb_build_object(
--       'type', 'FeatureCollection',
--       'features', jsonb_agg(ST_AsGeoJSON(m.*)::jsonb)
--   )
--   FROM solar_modules m WHERE m.plant_id = 1;
--
-- [B] Đo thời gian & kích thước xuất Vector Tiles động ST_AsMVT (< 30 KB/tile, < 8 ms):
--   EXPLAIN (ANALYZE, BUFFERS)
--   SELECT OCTET_LENGTH(get_solar_modules_mvt(18, 209348, 122145, 1)) AS mvt_bytes;
-- =============================================================================
