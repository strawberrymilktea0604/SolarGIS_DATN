#!/usr/bin/env python3
"""
ingest_gpkg_to_postgis.py
Nạp toàn bộ đa giác tấm pin từ bộ tệp .gpkg (QGIS) của 4 trang trại
(Thuận Nam 19, BIM 2, Thuận Nam Đức Long, Thiên Tân 1.2) vào bảng solar_modules (EPSG:32649).

Tham chiếu:
- Đầu việc 1.6 (Tuần 1): Khởi tạo CSDL PostGIS 7 bảng & nạp .gpkg
- Quy tắc đặt mã module_id: {plant_code_lower}_{block}_{string}_{pin_id:05d}
  Ví dụ: tn19_block1_string4_00458
"""

import argparse
import os
from pathlib import Path
import geopandas as gpd
import psycopg
from shapely.geometry import MultiPolygon


PLANT_META = {
    "TN19": ("Nhà máy Điện mặt trời Thuận Nam 19", 49.0),
    "BIM2": ("Nhà máy Điện mặt trời BIM 2", 250.0),
    "TNDL": ("Nhà máy Điện mặt trời Thuận Nam Đức Long", 50.0),
    "TT12": ("Nhà máy Điện mặt trời Thiên Tân 1.2", 100.0),
}


def ingest_gpkg(gpkg_path: Path, plant_code: str, db_url: str, layer: str | None = None) -> None:
    plant_code = plant_code.upper()
    if plant_code not in PLANT_META:
        raise ValueError(f"Unsupported plant_code: {plant_code}. Must be one of {list(PLANT_META.keys())}")

    print(f"[1/4] Reading GeoPackage: {gpkg_path} (plant={plant_code})...")
    gdf = gpd.read_file(gpkg_path, layer=layer) if layer else gpd.read_file(gpkg_path)

    if gdf.crs is None or gdf.crs.to_epsg() != 32649:
        print(f"      Reprojecting CRS from {gdf.crs} -> EPSG:32649...")
        gdf = gdf.to_crs(epsg=32649)

    plant_name, capacity_mwp = PLANT_META[plant_code]
    prefix = plant_code.lower()

    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            print(f"[2/4] Upserting plant record '{plant_code}' into solar_plants...")
            union_poly = gdf.geometry.unary_union.convex_hull
            if union_poly.geom_type == "Polygon":
                union_poly = MultiPolygon([union_poly])

            cur.execute(
                """
                INSERT INTO solar_plants (plant_code, plant_name, capacity_mwp, crs_epsg, pmtiles_url, boundary_geom)
                VALUES (%s, %s, %s, 32649, %s, ST_GeomFromText(%s, 32649))
                ON CONFLICT (plant_code) DO UPDATE
                SET plant_name = EXCLUDED.plant_name
                RETURNING id;
                """,
                (plant_code, plant_name, capacity_mwp, f"/tiles/{prefix}_ortho.pmtiles", union_poly.wkt),
            )
            plant_id = cur.fetchone()[0]

            print(f"[3/4] Inserting blocks, strings, and {len(gdf)} solar modules into PostGIS...")
            block_cache: dict[str, int] = {}
            string_cache: dict[tuple[int, str], int] = {}
            inserted_count = 0

            for idx, row in gdf.iterrows():
                block_code = str(row.get("block_code", row.get("Block", "block1"))).lower()
                string_code = str(row.get("string_code", row.get("String", "string1"))).lower()
                row_id = int(row.get("row_id", row.get("Row_ID", 1)))
                pin_index = int(row.get("pin_index", row.get("ID_Pin", idx + 1)))
                is_recovered = bool(row.get("is_distorted_recovered", False))

                module_id = str(
                    row.get("module_id")
                    or f"{prefix}_{block_code}_{string_code}_{pin_index:05d}"
                )

                geom = row.geometry
                if geom is None or geom.is_empty:
                    continue
                if geom.geom_type == "MultiPolygon":
                    geom = max(geom.geoms, key=lambda g: g.area)

                if block_code not in block_cache:
                    cur.execute(
                        """
                        INSERT INTO solar_blocks (plant_id, block_code, geom)
                        VALUES (%s, %s, ST_Multi(ST_GeomFromText(%s, 32649)))
                        ON CONFLICT (plant_id, block_code) DO UPDATE SET block_code = EXCLUDED.block_code
                        RETURNING id;
                        """,
                        (plant_id, block_code, geom.wkt),
                    )
                    block_cache[block_code] = cur.fetchone()[0]
                block_id = block_cache[block_code]

                str_key = (block_id, string_code)
                if str_key not in string_cache:
                    cur.execute(
                        """
                        INSERT INTO solar_strings (block_id, string_code, geom)
                        VALUES (%s, %s, ST_GeomFromText(%s, 32649))
                        ON CONFLICT (block_id, string_code) DO UPDATE SET string_code = EXCLUDED.string_code
                        RETURNING id;
                        """,
                        (block_id, string_code, geom.wkt),
                    )
                    string_cache[str_key] = cur.fetchone()[0]
                string_id = string_cache[str_key]

                centroid = geom.centroid
                cur.execute(
                    """
                    INSERT INTO solar_modules (
                        module_id, plant_id, block_id, string_id, row_id, pin_index,
                        is_distorted_recovered, current_health_status, current_coa_class,
                        centroid_geom, geom
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s,
                        %s, 'NORMAL', 1,
                        ST_GeomFromText(%s, 32649),
                        ST_GeomFromText(%s, 32649)
                    )
                    ON CONFLICT (module_id) DO UPDATE SET
                        geom = EXCLUDED.geom,
                        centroid_geom = EXCLUDED.centroid_geom,
                        is_distorted_recovered = EXCLUDED.is_distorted_recovered;
                    """,
                    (
                        module_id,
                        plant_id,
                        block_id,
                        string_id,
                        max(1, min(6, row_id)),
                        max(1, pin_index),
                        is_recovered,
                        centroid.wkt,
                        geom.wkt,
                    ),
                )
                inserted_count += 1

            conn.commit()
            print(f"[4/4] Completed! Upserted {inserted_count} solar modules for {plant_code}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest QGIS .gpkg solar panel grid into PostGIS")
    parser.add_argument("--gpkg", required=True, type=Path, help="Path to .gpkg file (e.g. data/gpkg/thuannam19_master.gpkg)")
    parser.add_argument("--plant", required=True, choices=["TN19", "BIM2", "TNDL", "TT12"], help="Plant code")
    parser.add_argument("--layer", default=None, help="Optional layer name inside .gpkg")
    parser.add_argument(
        "--db-url",
        default=os.environ.get("DATABASE_URL", "postgresql://solargis:solargis_secret_2026@localhost:5432/solargis_db"),
        help="PostgreSQL connection string",
    )
    args = parser.parse_args()
    ingest_gpkg(args.gpkg, args.plant, args.db_url, args.layer)
