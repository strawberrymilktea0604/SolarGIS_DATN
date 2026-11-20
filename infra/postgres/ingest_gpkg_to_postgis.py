#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ingest_gpkg_to_postgis.py
Nạp siêu tốc toàn bộ đa giác tấm pin từ bộ tệp .gpkg đã hoàn thiện vùng méo của 4 trang trại:
  - thuannam19_completed.gpkg (TN19 - 36.739 tấm pin)
  - BIM2_completed.gpkg (BIM2 - 21.451 tấm pin)
  - thuannamduclong_completed.gpkg (TNDL - 50.835 tấm pin)
  - thientan_completed.gpkg (TT12 - 38.040 tấm pin)
vào bảng solar_plants, solar_blocks, solar_strings, solar_modules trong PostGIS (EPSG:32649).

Ưu điểm:
- Đọc trực tiếp chuẩn nhị phân GeoPackage SQLite + WKB (chỉ dùng sqlite3 chuẩn, không cần cài geopandas/fiona/psycopg).
- Tự động truyền luồng SQL nạp hàng loạt (Batch COPY / INSERT) trực tiếp vào container `solargis_postgis`.
- Có cờ `--all` để nạp trọn bộ cả 4 nhà máy (~147.065 tấm pin) chỉ bằng 1 lệnh duy nhất.
"""

from __future__ import print_function
import argparse
import binascii
import os
import re
import sqlite3
import subprocess
import sys

PLANT_META = {
    "TN19": ("Nhà máy Điện mặt trời Thuận Nam 19", 49.0, "data/gpkg/thuannam19_completed.gpkg"),
    "BIM2": ("Nhà máy Điện mặt trời BIM 2", 250.0, "data/gpkg/BIM2_completed.gpkg"),
    "TNDL": ("Nhà máy Điện mặt trời Thuận Nam Đức Long", 50.0, "data/gpkg/thuannamduclong_completed.gpkg"),
    "TT12": ("Nhà máy Điện mặt trời Thiên Tân 1.2", 100.0, "data/gpkg/thientan_completed.gpkg"),
}

ENVELOPE_BYTE_LEN = {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}


def gpkg_blob_to_wkb_hex(blob):
    """Tách GeoPackage Binary Header (GP...) để lấy chuỗi WKB Hex chuẩn cho PostGIS (tương thích cả Python 2 & 3)."""
    if not blob:
        return None
    raw = bytearray(blob)
    if raw[0] != 0x47 or raw[1] != 0x50:  # 'G', 'P'
        return binascii.hexlify(bytes(raw)).decode("ascii")
    flags = raw[3]
    env_indicator = (flags >> 1) & 0x07
    env_bytes = ENVELOPE_BYTE_LEN.get(env_indicator, 0)
    wkb = bytes(raw[8 + env_bytes :])
    return binascii.hexlify(wkb).decode("ascii")


def normalize_block_code(layer_val, module_id):
    """Chuẩn hóa mã block_code (VD: 'thientan_master — Block1' -> 'block1')."""
    if module_id:
        parts = str(module_id).split("_")
        if len(parts) >= 4 and parts[1].lower().startswith("block"):
            return parts[1].lower()
    if layer_val:
        m = re.search(r"(block\s*\d+)", str(layer_val), re.IGNORECASE)
        if m:
            return m.group(1).replace(" ", "").lower()
        return re.sub(r"[^a-zA-Z0-9_]", "_", str(layer_val)).lower()
    return "block1"


def normalize_string_code(string_val, module_id):
    """Chuẩn hóa mã string_code (VD: 'string4')."""
    if string_val:
        return str(string_val).strip().lower()
    if module_id:
        parts = str(module_id).split("_")
        if len(parts) >= 4:
            return parts[2].lower()
    return "string1"


def ingest_single_gpkg(gpkg_path, plant_code, container_name="solargis_postgis", db_user="solargis", db_name="solargis_db"):
    plant_code = plant_code.upper()
    if plant_code not in PLANT_META:
        raise ValueError("Unsupported plant_code: {}".format(plant_code))

    if not os.path.exists(gpkg_path):
        raise IOError("Không tìm thấy file GeoPackage: {}".format(gpkg_path))

    plant_name, capacity_mwp, _ = PLANT_META[plant_code]
    prefix = plant_code.lower()

    print("=================================================================")
    print("[1/4] Đang đọc GeoPackage: {} (Mã nhà máy: {})...".format(gpkg_path, plant_code))
    conn = sqlite3.connect(gpkg_path)
    cur = conn.cursor()

    # Đọc ranh giới nhà máy từ bảng aoi_boundary (nếu có)
    aoi_wkb_hex = None
    try:
        row_aoi = cur.execute("SELECT geom FROM aoi_boundary LIMIT 1").fetchone()
        if row_aoi and row_aoi[0]:
            aoi_wkb_hex = gpkg_blob_to_wkb_hex(row_aoi[0])
    except Exception:
        pass

    rows = cur.execute(
        "SELECT fid, geom, ID_Pin, Row_ID, Tam_X, Tam_Y, layer, String_ID, module_id, is_distorted_recovered FROM modules"
    ).fetchall()
    conn.close()

    print("      Đã đọc {} tấm pin từ bảng 'modules'.".format(len(rows)))

    # Tập hợp danh sách block và string duy nhất
    blocks_set = set()
    strings_set = set()
    seen_module_ids = set()
    clean_modules = []

    for r in rows:
        fid, geom_blob, id_pin, row_id, tam_x, tam_y, layer_val, string_val, mod_id, is_rec = r
        wkb_hex = gpkg_blob_to_wkb_hex(geom_blob)
        if not wkb_hex:
            continue

        b_code = normalize_block_code(layer_val, mod_id)
        s_code = normalize_string_code(string_val, mod_id)
        r_id = int(row_id) if row_id is not None else 1
        r_id = max(1, min(6, r_id))
        p_idx = int(id_pin) if id_pin is not None else int(fid)
        p_idx = max(1, p_idx)

        if not mod_id:
            mod_id = "{}_{}_{}_{:05d}".format(prefix, b_code, s_code, p_idx)
        else:
            mod_id = str(mod_id).strip()

        # Nếu có trùng module_id (như 483 tấm ở Thiên Tân 1.2), gắn hậu tố fid để không mất tấm pin nào
        if mod_id in seen_module_ids:
            mod_id = "{}_dup{}".format(mod_id, fid)
        seen_module_ids.add(mod_id)

        rec_bool = "t" if (is_rec and int(is_rec) != 0) else "f"
        blocks_set.add(b_code)
        strings_set.add((b_code, s_code))
        clean_modules.append((mod_id, b_code, s_code, r_id, p_idx, rec_bool, wkb_hex))

    print("[2/4] Chuẩn bị luồng nạp tốc độ cao (COPY) cho {} Blocks, {} Strings, {} Modules...".format(
        len(blocks_set), len(strings_set), len(clean_modules)
    ))

    sql_lines = [
        "BEGIN;",
        "CREATE TEMP TABLE tmp_ingest_modules (",
        "    module_id VARCHAR(64),",
        "    block_code VARCHAR(32),",
        "    string_code VARCHAR(32),",
        "    row_id SMALLINT,",
        "    pin_index INT,",
        "    is_distorted_recovered BOOLEAN,",
        "    wkb_hex TEXT",
        ") ON COMMIT DROP;",
        "COPY tmp_ingest_modules (module_id, block_code, string_code, row_id, pin_index, is_distorted_recovered, wkb_hex) FROM STDIN;",
    ]

    for m in clean_modules:
        sql_lines.append("{}\t{}\t{}\t{}\t{}\t{}\t{}".format(m[0], m[1], m[2], m[3], m[4], m[5], m[6]))
    sql_lines.append("\\.")

    if aoi_wkb_hex:
        boundary_expr = "ST_Multi(ST_SetSRID(ST_GeomFromWKB(decode('{}', 'hex')), 32649))".format(aoi_wkb_hex)
    else:
        boundary_expr = "(SELECT ST_Multi(ST_ConvexHull(ST_Collect(ST_SetSRID(ST_GeomFromWKB(decode(wkb_hex, 'hex')), 32649)))) FROM tmp_ingest_modules)"

    sql_lines.append("""
-- 1. Upsert nhà máy vào bảng solar_plants
INSERT INTO solar_plants (plant_code, plant_name, capacity_mwp, crs_epsg, pmtiles_url, raster_tile_url_template, boundary_geom)
VALUES (
    '{plant_code}',
    '{plant_name}',
    {capacity_mwp},
    32649,
    '/tiles/{prefix}_ortho.pmtiles',
    '/tiles/{prefix}/{{z}}/{{x}}/{{y}}.webp',
    {boundary_expr}
)
ON CONFLICT (plant_code) DO UPDATE SET
    plant_name = EXCLUDED.plant_name,
    boundary_geom = EXCLUDED.boundary_geom;

-- 2. Xóa dữ liệu mẫu (synthetic) cũ của nhà máy này trước khi nạp lưới .gpkg thật
DELETE FROM solar_modules WHERE plant_id = (SELECT id FROM solar_plants WHERE plant_code = '{plant_code}');

-- 3. Upsert danh sách Blocks vào solar_blocks
INSERT INTO solar_blocks (plant_id, block_code, geom)
SELECT
    p.id,
    t.block_code,
    ST_Multi(ST_ConvexHull(ST_Collect(ST_SetSRID(ST_GeomFromWKB(decode(t.wkb_hex, 'hex')), 32649))))
FROM tmp_ingest_modules t
CROSS JOIN solar_plants p
WHERE p.plant_code = '{plant_code}'
GROUP BY p.id, t.block_code
ON CONFLICT (plant_id, block_code) DO UPDATE SET
    geom = EXCLUDED.geom;

-- 4. Upsert danh sách Strings vào solar_strings
INSERT INTO solar_strings (block_id, string_code, expected_modules, geom)
SELECT
    b.id,
    t.string_code,
    COUNT(*)::INT,
    ST_ConvexHull(ST_Collect(ST_SetSRID(ST_GeomFromWKB(decode(t.wkb_hex, 'hex')), 32649)))::GEOMETRY(Polygon, 32649)
FROM tmp_ingest_modules t
JOIN solar_plants p ON p.plant_code = '{plant_code}'
JOIN solar_blocks b ON b.plant_id = p.id AND b.block_code = t.block_code
GROUP BY b.id, t.string_code
ON CONFLICT (block_id, string_code) DO UPDATE SET
    expected_modules = EXCLUDED.expected_modules,
    geom = EXCLUDED.geom;

-- 5. Nạp toàn bộ tấm pin vào solar_modules
INSERT INTO solar_modules (
    module_id, plant_id, block_id, string_id, row_id, pin_index,
    is_distorted_recovered, current_health_status, current_coa_class,
    centroid_geom, geom
)
SELECT
    t.module_id,
    p.id,
    b.id,
    s.id,
    t.row_id,
    t.pin_index,
    t.is_distorted_recovered,
    'NORMAL',
    1,
    ST_Centroid(ST_GeometryN(ST_Multi(ST_SetSRID(ST_GeomFromWKB(decode(t.wkb_hex, 'hex')), 32649)), 1)),
    ST_GeometryN(ST_Multi(ST_SetSRID(ST_GeomFromWKB(decode(t.wkb_hex, 'hex')), 32649)), 1)
FROM tmp_ingest_modules t
JOIN solar_plants p ON p.plant_code = '{plant_code}'
JOIN solar_blocks b ON b.plant_id = p.id AND b.block_code = t.block_code
JOIN solar_strings s ON s.block_id = b.id AND s.string_code = t.string_code
ON CONFLICT (module_id) DO UPDATE SET
    is_distorted_recovered = EXCLUDED.is_distorted_recovered,
    centroid_geom = EXCLUDED.centroid_geom,
    geom = EXCLUDED.geom;

COMMIT;
ANALYZE solar_modules;
""".format(
        plant_code=plant_code,
        plant_name=plant_name,
        capacity_mwp=capacity_mwp,
        prefix=prefix,
        boundary_expr=boundary_expr,
    ))

    joined_sql = "\n".join(sql_lines)
    if isinstance(joined_sql, bytes):
        sql_payload = joined_sql
    else:
        sql_payload = joined_sql.encode("utf-8")

    print("[3/4] Đang truyền dữ liệu vào container PostGIS '{}'...".format(container_name))
    cmd = ["docker", "exec", "-i", container_name, "psql", "-U", db_user, "-d", db_name, "-v", "ON_ERROR_STOP=1"]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate(input=sql_payload)

    if proc.returncode != 0:
        print("LỖI KHI NẠP POSTGIS:\n", err.decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(proc.returncode)

    print("[4/4] Hoàn tất nạp {} tấm pin cho nhà máy {} ({})!".format(len(clean_modules), plant_code, plant_name))


def main():
    parser = argparse.ArgumentParser(description="Nạp file .gpkg 4 trang trại vào PostGIS (Không cần cài geopandas)")
    parser.add_argument("--gpkg", type=str, default=None, help="Đường dẫn tới file .gpkg (VD: data/gpkg/thuannam19_completed.gpkg)")
    parser.add_argument("--plant", type=str, choices=["TN19", "BIM2", "TNDL", "TT12"], default="TN19", help="Mã trang trại")
    parser.add_argument("--all", action="store_true", help="Nạp tự động toàn bộ cả 4 nhà máy trong data/gpkg/")
    parser.add_argument("--container", type=str, default="solargis_postgis", help="Tên container Docker PostGIS")
    args = parser.parse_args()

    if args.all:
        for code, (_, _, default_path) in PLANT_META.items():
            if os.path.exists(default_path):
                ingest_single_gpkg(default_path, code, container_name=args.container)
            else:
                print("Bỏ qua {} vì chưa có file {}".format(code, default_path))
    else:
        gpkg_path = args.gpkg or PLANT_META[args.plant][2]
        # Tự động fallback nếu người dùng gõ thuannam19_master.gpkg mà trong thư mục là thuannam19_completed.gpkg
        if not os.path.exists(gpkg_path) and os.path.exists(PLANT_META[args.plant][2]):
            print("Lưu ý: Chuyển tự động từ '{}' sang file có sẵn '{}'.".format(gpkg_path, PLANT_META[args.plant][2]))
            gpkg_path = PLANT_META[args.plant][2]
        ingest_single_gpkg(gpkg_path, args.plant, container_name=args.container)


if __name__ == "__main__":
    main()
