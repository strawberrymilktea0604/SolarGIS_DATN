# SolarGIS Digital Twin (`solargis-digital-twin-rust`)

**Đề tài Đồ án Tốt nghiệp Khoa học Máy tính (`7724162`) — Trường Đại học Xây dựng Hà Nội (HUCE)**  
*Hệ thống Bản sao số (Digital Twin) và Trí tuệ Nhân tạo Đa luồng trong Giám sát, Định vị Khuyết tật Nhà máy Điện mặt trời từ Dữ liệu UAV*

---

## 1. Kiến trúc Phân chia 03 Module Độc lập (`33% – 33% – 34%`)

| Thành viên | Module Phụ trách | Thư mục Mã nguồn Chính |
| :--- | :--- | :--- |
| **Thành viên 1 (`33%`)** | **Module 1:** Pipeline AI 1 Nhận diện Bản đồ Ortho chính (Bắt vùng pin méo), Nội suy Lưới PCA Khóa Hướng Từng Hàng, Thư viện `spatial_grid_index` & Xuất `PMTiles / XYZ WebP` | `packages/spatial_grid_index/`<br>`modules/module1_ortho_pipeline/` |
| **Thành viên 2 (`33%`)** | **Module 2:** Pipeline AI 2 Nhận diện Ảnh lẻ RGB + Lỗi Nhiệt (Chuẩn IEC TS 62446-3:2017 & `DJI Thermal SDK`), Khử méo `DewarpData` (`P=K`), Ánh xạ `Bidirectional Strip Homography` + `Hungarian` & `Multi-View Deduplication` | `modules/module2_uav_thermal_ai/` |
| **Thành viên 3 (`34%`)** | **Module 3:** Thiết kế PTTKHT 6 Bước, CSDL Không gian PostGIS 7 Bảng (`ST_AsMVT` + Trigger An toàn Thời gian) & Phần mềm Web Quản trị Bản sao số (`Rust Axum` + `React/MapLibre WebGL 60 FPS` + `Typst PDF`) | `infra/`<br>`docs/pttkht/`<br>`modules/module3_digital_twin_app/` |

---

## 2. Lệnh Khởi chạy Nhanh (Quick Start)

```bash
# 1. Khởi chạy hạ tầng PostGIS 16-3.4 (tự động nạp 01_schema.sql, 02_triggers.sql, 03_mvt_funcs.sql) & Redis 7
make up

# 2. Mở phiên truy vấn SQL trực tiếp vào container PostGIS
make psql

# 3. Kiểm tra biên dịch Workspace Rust của Module 3
make check-rust
```

---

## 3. Tài liệu Đặc tả & Thiết kế Hệ thống
- [Đặc tả Tổng quan Đề tài ĐATN V6](docs/dac_ta_tong_quan_datn_solargis.md)
- [Kế hoạch Phân công Chi tiết 9 Tuần (`16/11/2026` – `17/01/2027`)](docs/ke_hoach_phan_cong_chi_tiet_9_tuan_solargis.md)
- [Hợp đồng Giao tiếp Dữ liệu Liên Module (`DATA_CONTRACT.md`)](docs/DATA_CONTRACT.md)
- [Hồ sơ PTTKHT Bước 1, 2, 3 (Đặc tả 7 Use Cases, Sơ đồ Use Case & ERD 7 Bảng PostGIS)](docs/pttkht/PTTKHT_Buoc1_2_3_UseCase_ERD.md)
  - Sơ đồ Use Case PlantUML: [01_use_case.puml](docs/pttkht/01_use_case.puml)
  - Sơ đồ ERD 7 Bảng PlantUML: [02_erd_7tables.puml](docs/pttkht/02_erd_7tables.puml)
