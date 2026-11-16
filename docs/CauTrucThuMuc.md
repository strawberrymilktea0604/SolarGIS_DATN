solargis-digital-twin-rust/

├── .github/

│   └── workflows/               # CI tự động chạy test Python (pytest) \& Rust (cargo check)

├── docs/                        # Hồ sơ học thuật \& Quy chế ĐATN

│   ├── DATA\_CONTRACT.md         # Hợp đồng giao tiếp dữ liệu (Khóa cứng ngày 16/11/2026)

│   ├── pttkht/                  # Sơ đồ 6 bước PTTKHT (Use Case, ERD, Sequence, Activity)

│   └── report/                  # Bản thảo báo cáo ĐATN \& Slide bảo vệ

│

├── infra/                       # Hạ tầng Docker \& CSDL (TV3 chủ trì, TV1 hỗ trợ)

│   ├── docker-compose.yml       # Chạy trọn bộ PostGIS 16-3.4, Redis 7, Rust Backend, AI Worker

│   ├── Dockerfile.backend       # Build Rust Axum + trình biên dịch Typst PDF

│   ├── Dockerfile.worker        # Build Python AI Worker (--platform=linux/amd64 + DJI SDK)

│   ├── dji\_tsdk/                # Chứa libdirp.so, libv\_dirp.so, libv\_iirp.so, libv\_list.ini (gitignored nếu nặng)

│   └── postgres/

│       └── init/

│           ├── 01\_schema.sql    # DDL 7 bảng PostGIS (EPSG:32649) \& chỉ mục GIST

│           ├── 02\_triggers.sql  # Trigger fn\_sync\_module\_health\_after\_inspection

│           └── 03\_mvt\_funcs.sql # Hàm truy vấn Vector Tiles ST\_AsMVT

│

├── packages/                    # Thư viện Python dùng chung giữa Module 1 \& Module 2

│   └── spatial\_grid\_index/      # \[TV1 xây dựng -> TV2 gọi API]

│       ├── pyproject.toml

│       ├── spatial\_grid\_index/

│       │   ├── \_\_init\_\_.py

│       │   ├── index.py         # STRtree + cKDTree (get\_candidates\_in\_radius, landmarks)

│       │   ├── snapping.py      # Topological Grid Snapping

│       │   └── mass\_spring.py   # Elastic Mass-Spring Regularization (mass\_spring\_refine)

│       └── tests/

│

├── modules/                     # MÃ NGUỒN CHUYÊN BIỆT CỦA 3 THÀNH VIÊN

│   ├── module1\_ortho\_pipeline/  # \[THÀNH VIÊN 1 - 33%]

│   │   ├── pyproject.toml

│   │   ├── scripts/

│   │   │   ├── 01\_audit\_4plants.py      # Kiểm kê thông số kỹ thuật 4 trang trại

│   │   │   ├── 02\_pca\_gap\_interp.py     # Nội suy vùng pin méo theo PCA khóa hướng từng hàng

│   │   │   ├── 03\_tile\_slicer.py        # Cắt ảnh 1024x1024 \& SeamlineShift Augmentation

│   │   │   └── 04\_build\_pmtiles.sh      # Chạy gdal2tiles --xyz --exclude -z 15-21 -> .pmtiles

│   │   ├── training/                    # Khảo sát 4 họ mô hình \& Train AI 1 (Ortho-OBB)

│   │   └── inference/                   # Suy luận cửa sổ trượt + xuất ONNX

│   │

│   ├── module2\_uav\_thermal\_ai/  # \[THÀNH VIÊN 2 - 33%]

│   │   ├── pyproject.toml

│   │   ├── preprocessing/

│   │   │   ├── spatial\_split\_15m.py     # Chia tập Train/Val/Test cách ly dải đệm 15m

│   │   │   ├── dewarp\_undistort.py      # Khử méo DewarpData (W/2, H/2 \& cv2.undistortPoints P=K)

│   │   │   └── dji\_dirp\_decoder.py      # Giải mã R-JPEG đủ 4 trường (emissivity=0.85, d<=25m)

│   │   ├── training/

│   │   │   ├── ai2a\_rgb\_panel/          # Train \& khảo sát AI 2A (tấm pin ảnh lẻ RGB)

│   │   │   └── ai2b\_thermal\_fault/      # Train \& khảo sát AI 2B (4 lớp lỗi nhiệt IEC 62446-3)

│   │   ├── mapping/

│   │   │   ├── dual\_sensor\_align.py     # Ghép cặp RGB-Nhiệt theo độ cao 31m/35m/42m

│   │   │   ├── strip\_homography.py      # Bidirectional Strip Anchoring (4-DoF/6-DoF + Hartley DLT)

│   │   │   ├── hungarian\_matcher.py     # Ghép cặp tối ưu Hungarian hai ngưỡng

│   │   │   └── multiview\_agg.py         # Khử trùng lặp đa góc nhìn (chọn ảnh nadir nhất)

│   │   └── worker/

│   │       └── redis\_consumer.py        # Lắng nghe queue:solargis:strip\_inspection\_jobs

│   │

│   └── module3\_digital\_twin\_app/# \[THÀNH VIÊN 3 - 34%]

│       ├── Cargo.toml                   # Rust Workspace

│       ├── crates/

│       │   ├── solar\_shared/            # Struct dùng chung, Enum CoA 1/2/3, Parser EXIF/XMP

│       │   └── solar\_backend/           # Axum REST API, SQLx PostGIS, Redis Pub/Sub SSE, Typst PDF

│       ├── templates/

│       │   └── iec\_62446\_3\_report.typ   # Mẫu biên bản bảo trì chuẩn IEC TS 62446-3 (Typst)

│       └── frontend/                    # Next.js / React + TypeScript + MapLibre GL JS (60 FPS)

│

├── data/                        # Dữ liệu cục bộ (KHÔNG đẩy file nặng lên Git)

│   ├── raw/                     # .tif, \_W.JPG, \_T.JPG (ignored)

│   ├── gpkg/                    # thuannam19\_master.gpkg \& các file .gpkg 4 nhà máy

│   └── artifacts/               # Trọng số .pt, .onnx, .pmtiles (ignored - lưu trên Drive/Releases)

│

├── .gitignore

├── Makefile                     # Lệnh tắt: make up, make test, make tiles-tn19

└── README.md



