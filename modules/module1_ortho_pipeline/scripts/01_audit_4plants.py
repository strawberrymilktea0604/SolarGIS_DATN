from pathlib import Path
import geopandas as gpd
import numpy as np

PLANTS = {
    "TN19": "data/gpkg/thuannam19_master.gpkg",
    "TNDL": "data/gpkg/thuannamduclong_master.gpkg",
    "TT12": "data/gpkg/thientan_master.gpkg",
    "BIM2": "data/gpkg/BIM2_master.gpkg",
}

def audit_all():
    for code, rel_path in PLANTS.items():
        p = Path(rel_path)
        if not p.exists():
            print(f"[SKIP] Không thấy {p}")
            continue

        gdf = gpd.read_file(p, layer="modules")
        cols = list(gdf.columns)
        print(f"\n=== {code} ({p.name} — {p.stat().st_size / 1e6:.1f} MB) ===")
        print(f"CRS       : {gdf.crs}")
        print(f"Số tấm pin: {len(gdf):,}")
        print(f"Các cột   : {[c for c in cols if c != 'geometry']}")
        if "layer" in gdf.columns and "String_ID" in gdf.columns:
            print(f"Số Block  : {gdf['layer'].nunique()} | Số String: {gdf.groupby(['layer', 'String_ID']).ngroups}")

if __name__ == "__main__":
    audit_all()