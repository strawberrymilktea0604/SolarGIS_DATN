// =============================================================================
// Mẫu Biên bản Kiểm định Nhiệt Điện mặt trời theo chuẩn Quốc tế IEC TS 62446-3:2017
// Được biên dịch bởi Rust Backend bên trong tokio::task::spawn_blocking
// =============================================================================

#set page(
  paper: "a4",
  margin: (x: 1.8cm, y: 2cm),
  header: align(right)[
    #text(size: 9pt, fill: luma(100))[
      *SOLARGIS DIGITAL TWIN* — Biên bản Kiểm định Nhiệt Chuẩn IEC TS 62446-3:2017
    ]
  ],
  footer: [
    #line(length: 100%, stroke: 0.5pt + luma(180))
    #grid(
      columns: (1fr, 1fr),
      align(left)[#text(size: 8.5pt)[Hệ thống Bản sao số & AI Đa luồng]],
      align(right)[#text(size: 8.5pt)[Trang #counter(page).display("1 / 1", both: true)]],
    )
  ]
)

#set text(font: "Liberation Sans", size: 10.5pt, lang: "vi")

= BIÊN BẢN CHẨN ĐOÁN KHUYẾT TẬT NHIỆT NHÀ MÁY ĐIỆN MẶT TRỜI
== Tham chiếu Tiêu chuẩn Quốc tế IEC TS 62446-3:2017 & IEA PVPS Task 13

#v(0.4cm)
*1. Thông tin Chiến dịch Bay & Thông số Môi trường Giải mã DJI Thermal SDK (`dirp`):*
- *Mã chiến dịch:* `{{campaign_id}}`
- *Cường độ bức xạ mặt phẳng giàn pin ($G_"POA"$):* `{{irradiance_wm2}} W/m²` (Yêu cầu chuẩn $\ge 600\text{ W/m}^2$)
- *Hệ số phát xạ kính cường lực mặt trước ($\varepsilon$):* `0.85`
- *Độ ẩm tương đối:* `{{relative_humidity_pct}}%` | *Nhiệt độ phản xạ nền trời:* `{{reflected_temp_c}} °C`

#v(0.4cm)
*2. Bảng Phân hạng Lớp Bất thường (`Classes of Abnormality - CoA`):*
- *CoA 1 (Normal):* Không có bất thường nhiệt — Trạng thái vận hành khỏe mạnh.
- *CoA 2 (Thermal Abnormality):* Có điểm nóng hoặc chênh lệch nhiệt độ cần theo dõi định kỳ.
- *CoA 3 (Safety-Relevant Abnormality):* Quá nhiệt nghiêm trọng / Hở mạch / Bypass — Cần can thiệp O&M sớm.
