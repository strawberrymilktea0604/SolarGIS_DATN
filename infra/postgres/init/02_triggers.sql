-- =============================================================================
-- SolarGIS Digital Twin - 02_triggers.sql
-- Trigger Đồng bộ Sức khỏe Tấm pin An toàn Thời gian (INSERT / UPDATE / DELETE)
-- Chỉ đồng bộ vào solar_modules khi đợt bay có flight_date = MAX(flight_date)
-- Tham chiếu: DATA_CONTRACT.md (Mục 5.2 - Bản vá kỹ thuật #3)
-- =============================================================================

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
