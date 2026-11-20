//! SolarGIS Shared Domain Types, IEC TS 62446-3 Enums & Redis Contracts
//! Reference: DATA_CONTRACT.md

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

/// 4 lớp lỗi hình thái nhiệt cấp tấm pin (Module-level visual thermal-pattern labels)
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum ThermalFaultClass {
    SingleHotSpot,
    MultiHotSpot,
    Bypass,
    ModuleOpenCircuit,
}

/// Phân hạng bất thường nhiệt theo chuẩn quốc tế IEC TS 62446-3:2017
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[repr(i16)]
pub enum IecCoaClass {
    /// CoA 1: Không có bất thường nhiệt (Normal / Healthy)
    Coa1Normal = 1,
    /// CoA 2: Có bất thường nhiệt cần theo dõi / bảo trì định kỳ
    Coa2ThermalAbnormality = 2,
    /// CoA 3: Bất thường nhiệt nghiêm trọng ảnh hưởng an toàn, cần can thiệp sớm
    Coa3SafetyRelevant = 3,
}

/// Mức độ ưu tiên bảo trì O&M nội bộ
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum OmPriority {
    LOW,
    MEDIUM,
    HIGH,
}

/// Trạng thái kiểm duyệt QC
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum QcStatus {
    AUTO_VERIFIED,
    PENDING_QC,
    HUMAN_CONFIRMED,
    HUMAN_CORRECTED,
    QC_REJECTED,
}

/// Gói tin trả về tại GET /api/campaigns/{campaign_id}/fault_states
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CampaignFaultStatesResponse {
    pub campaign_id: Uuid,
    pub is_latest: bool,
    pub irradiance_wm2: f64,
    pub faults: Vec<ModuleFaultStateItem>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ModuleFaultStateItem {
    pub mvt_id: i64,
    pub fault_class: ThermalFaultClass,
    pub iec_coa_class: i16,
    pub om_priority: OmPriority,
    pub qc_status: QcStatus,
}

/// Payload duyệt QC tại PATCH /api/inspections/{log_id}/qc
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QcReviewRequest {
    pub qc_status: QcStatus,
    pub corrected_module_id: Option<String>,
    pub reviewer_note: Option<String>,
}

/// Sự kiện SSE/Redis PubSub bắn về từ Python AI Worker
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CampaignProgressEvent {
    pub event_type: String,
    pub campaign_id: Uuid,
    pub strip_id: String,
    pub processed_pairs: i32,
    pub total_pairs: i32,
    pub timestamp: DateTime<Utc>,
}
