-- =============================================================================
-- SolarGIS Digital Twin - 03_mvt_funcs.sql
-- Hàm truy vấn Vector Tiles động ST_AsMVT chuẩn khóa nguyên mvt_id
-- Tham chiếu: Đề cương ĐATN V6 (Mục 3.3) & DATA_CONTRACT.md (Mục 6.1)
-- =============================================================================

CREATE OR REPLACE FUNCTION get_solar_modules_mvt(
    p_z INT,
    p_x INT,
    p_y INT,
    p_plant_id INT
) RETURNS BYTEA AS $$
DECLARE
    v_mvt BYTEA;
BEGIN
    SELECT ST_AsMVT(tile, 'solar_modules_layer', 4096, 'geom', 'mvt_id') INTO v_mvt
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
                ST_TileEnvelope(p_z, p_x, p_y),
                4096,
                64,
                true
            ) AS geom
        FROM solar_modules m
        WHERE m.plant_id = p_plant_id
          AND m.geom && ST_Transform(
              ST_TileEnvelope(p_z, p_x, p_y, margin => (64.0 / 4096.0)),
              32649
          )
    ) AS tile
    WHERE geom IS NOT NULL;

    RETURN COALESCE(v_mvt, ''::BYTEA);
END;
$$ LANGUAGE plpgsql STABLE PARALLEL SAFE;
