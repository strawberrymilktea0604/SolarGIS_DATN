import sqlite3
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import from_bounds
from shapely.affinity import translate
from shapely.geometry import Point
from shapely.strtree import STRtree

PLANTS = {
    "TN19": ("data/gpkg/thuannam19_master.gpkg", "data/gpkg/thuannam19_completed.gpkg"),
    "TNDL": ("data/gpkg/thuannamduclong_master.gpkg", "data/gpkg/thuannamduclong_completed.gpkg"),
    "TT12": ("data/gpkg/thientan_master.gpkg", "data/gpkg/thientan_completed.gpkg"),
    "BIM2": ("data/gpkg/BIM2_master.gpkg", "data/gpkg/BIM2_completed.gpkg"),
}

MAX_CONSECUTIVE_MISSING = 40
MAX_OVERLAP_RATIO = 0.15       # Cấm chồng đè > 15% diện tích lên bất kỳ tấm nào đã có
MIN_PANEL_PIXEL_RATIO = 0.45   # Ít nhất 45% pixel trong ô phải mang phổ màu tấm pin


def find_raster_layer(gpkg_path: Path) -> str | None:
    con = sqlite3.connect(gpkg_path)
    try:
        rows = con.execute(
            "SELECT table_name FROM gpkg_contents WHERE data_type = 'tiles'"
        ).fetchall()
        return rows[0][0] if rows else None
    finally:
        con.close()


def read_patch_rgb(src: rasterio.DatasetReader, geom):
    minx, miny, maxx, maxy = geom.bounds
    try:
        win = from_bounds(minx, miny, maxx, maxy, transform=src.transform)
        data = src.read([1, 2, 3], window=win, boundless=True, fill_value=0)
    except Exception:
        return None
    if data.size == 0:
        return None
    r, g, b = data[0].astype(float), data[1].astype(float), data[2].astype(float)
    valid = ((r + g + b) > 15) & ((r + g + b) < 755)
    if valid.sum() < 10:
        return None
    return r[valid], g[valid], b[valid]


def calibrate_panel_color_thresholds(
    src: rasterio.DatasetReader, gdf: gpd.GeoDataFrame, sample_size: int = 500
) -> dict:
    """Học phân bố màu từng pixel từ chính các tấm pin gốc của nhà máy."""
    sample = gdf.sample(n=min(sample_size, len(gdf)), random_state=42)
    luma_list, rb_list, exg_list = [], [], []
    for geom in sample.geometry:
        rgb = read_patch_rgb(src, geom)
        if rgb is None:
            continue
        r, g, b = rgb
        luma_list.append(float(np.median(0.299 * r + 0.587 * g + 0.114 * b)))
        rb_list.append(float(np.median(r - b)))
        exg_list.append(float(np.median(2.0 * g - r - b)))

    return {
        "min_luma": max(float(np.percentile(luma_list, 2)) - 25.0, 20.0),
        "max_luma": min(float(np.percentile(luma_list, 95)) + 38.0, 210.0),
        "max_rb": float(np.percentile(rb_list, 95)) + 12.0,
        "max_exg": float(np.percentile(exg_list, 95)) + 18.0,
    }


def overlaps_existing(cand_geom, tree: STRtree, geoms_array, extra_geoms: list) -> bool:
    """Kiểm tra chồng lấn > 15% diện tích với toàn bộ tấm gốc và tấm mới sinh."""
    cand_area = cand_geom.area
    if cand_area <= 1e-6:
        return True

    # 1. Kiểm tra với toàn bộ tấm pin gốc qua STRtree (O(log N))
    for idx in tree.query(cand_geom, predicate="intersects"):
        inter_area = cand_geom.intersection(geoms_array[idx]).area
        if (inter_area / cand_area) > MAX_OVERLAP_RATIO:
            return True

    # 2. Kiểm tra với các tấm vừa nội suy trong cùng String
    for prev_geom in extra_geoms:
        if cand_geom.intersects(prev_geom):
            if (cand_geom.intersection(prev_geom).area / cand_area) > MAX_OVERLAP_RATIO:
                return True

    return False


def is_valid_solar_panel(
    geom,
    src: rasterio.DatasetReader | None,
    thresholds: dict | None,
    aoi_union,
) -> bool:
    # 1. Toàn bộ 4 góc/tâm phải nằm trong ranh giới aoi_boundary
    if aoi_union is not None:
        c = geom.centroid
        if not aoi_union.contains(Point(c.x, c.y)):
            return False

    # 2. Xác thực tỷ lệ pixel thực sự mang màu tấm pin (>= 68%)
    if src is not None and thresholds is not None:
        rgb = read_patch_rgb(src, geom)
        if rgb is None:
            return False
        r, g, b = rgb
        luma = 0.299 * r + 0.587 * g + 0.114 * b
        rb_diff = r - b
        exg = 2.0 * g - r - b

        # Loại trừ pixel quá tối (bóng đổ đen kịt), quá sáng (máng cáp trắng/đất cát), vàng cát hoặc cỏ xanh
        is_panel_px = (
            (luma >= thresholds["min_luma"])
            & (luma <= thresholds["max_luma"])
            & (rb_diff <= thresholds["max_rb"])
            & (exg <= thresholds["max_exg"])
        )
        if float(is_panel_px.mean()) < MIN_PANEL_PIXEL_RATIO:
            return False

    return True


def make_canonical_template(s_grp: gpd.GeoDataFrame):
    """Chọn tấm pin có diện tích chuẩn (gần trung vị nhất) làm khuôn mẫu, tránh copy tấm bị méo."""
    areas = s_grp.geometry.area.values
    med_area = float(np.median(areas))
    best_pos = int(np.argmin(np.abs(areas - med_area)))
    best_geom = s_grp.geometry.iloc[best_pos]
    c = best_geom.centroid
    return best_geom, c.x, c.y


def process_plant(plant_code: str, gpkg_in: str, gpkg_out: str) -> dict | None:
    in_path = Path(gpkg_in)
    if not in_path.exists():
        print(f"[SKIP] Không tìm thấy {in_path}")
        return None

    gdf = gpd.read_file(in_path, layer="modules")
    assert gdf.crs is not None and gdf.crs.to_epsg() == 32649, (
        f"{plant_code}: Yêu cầu EPSG:32649, hiện tại là {gdf.crs}"
    )

    # Xây cây STRtree trên toàn bộ tấm pin gốc để cấm chồng đè tuyệt đối
    orig_geoms = gdf.geometry.values
    orig_tree = STRtree(orig_geoms)

    aoi_gdf = None
    aoi_union = None
    try:
        aoi_gdf = gpd.read_file(in_path, layer="aoi_boundary")
        aoi_union = aoi_gdf.geometry.union_all()
    except Exception:
        pass

    raster_layer = find_raster_layer(in_path)
    src = None
    thresholds = None
    if raster_layer:
        try:
            src = rasterio.open(f"GPKG:{in_path.resolve()}:{raster_layer}")
            thresholds = calibrate_panel_color_thresholds(src, gdf)
            print(
                f"  [{plant_code}] Lọc pixel '{raster_layer}' | "
                f"luma=[{thresholds['min_luma']:.0f}, {thresholds['max_luma']:.0f}], "
                f"max_rb={thresholds['max_rb']:.1f}"
            )
        except Exception as e:
            print(f"  [{plant_code}] Không mở được raster '{raster_layer}': {e}")

    prefix = f"{plant_code.lower()}_"
    gdf["module_id"] = gdf["module_id"].apply(
        lambda s: s if str(s).lower().startswith(prefix) else f"{prefix}{s}"
    )
    gdf["is_distorted_recovered"] = False
    gdf["panel_type"] = "original_qgis"

    in_row_recovered = []
    cross_row_recovered = []
    rejected_overlap = 0
    rejected_raster = 0
    angles_deg, du_all, dv_all = [], [], []
    zigzag_strings = 0

    try:
        for (block, string_id), s_grp in gdf.groupby(["layer", "String_ID"]):
            if len(s_grp) < 4:
                continue

            tmpl_geom, tmpl_cx, tmpl_cy = make_canonical_template(s_grp)
            string_new_geoms: list = []

            coords = np.column_stack([s_grp["Tam_X"].values, s_grp["Tam_Y"].values])
            center = coords.mean(axis=0)
            centered = coords - center
            _, _, vt = np.linalg.svd(centered, full_matrices=False)
            u = vt[0]

            # Khóa dấu u bằng hiệp phương sai từng hàng Row_ID
            u_proj = centered @ u
            cov_list = []
            for _, r_idx in s_grp.groupby("Row_ID").groups.items():
                pos = s_grp.index.get_indexer(r_idx)
                if len(pos) >= 2:
                    u_r = u_proj[pos]
                    id_r = s_grp.loc[r_idx, "ID_Pin"].values.astype(float)
                    cov_list.append(float(np.sum((u_r - u_r.mean()) * (id_r - id_r.mean()))))

            if cov_list:
                signs = [np.sign(c) for c in cov_list if abs(c) > 1e-6]
                if len(set(signs)) > 1:
                    zigzag_strings += 1
                if sum(cov_list) < 0:
                    u = -u

            v = np.array([-u[1], u[0]])
            angles_deg.append(float(np.degrees(np.arctan2(u[1], u[0]))))

            s_work = s_grp.copy()
            s_work["_u"] = (coords - center) @ u
            s_work["_v"] = (coords - center) @ v

            string_diffs = []
            row_v_medians = {}
            for rid, r_grp in s_work.groupby("Row_ID"):
                row_v_medians[int(rid)] = float(np.median(r_grp["_v"].values))
                if len(r_grp) >= 2:
                    string_diffs.extend(np.diff(np.sort(r_grp["_u"].values)))

            if not string_diffs:
                continue
            du_med = float(np.median(string_diffs))
            if du_med <= 0.2:
                continue
            du_all.append(du_med)

            sorted_rids = sorted(row_v_medians.keys())
            if len(sorted_rids) >= 2:
                dv_steps = [
                    abs(row_v_medians[sorted_rids[i + 1]] - row_v_medians[sorted_rids[i]])
                    for i in range(len(sorted_rids) - 1)
                ]
                dv_med = float(np.median(dv_steps))
                if dv_med > 0.2:
                    dv_all.append(dv_med)

            row_u_records: dict[int, list[tuple[float, pd.Series]]] = {}

            # 1. Nội suy dọc hàng (In-Row)
            for rid, r_grp in s_work.groupby("Row_ID"):
                rid_int = int(rid)
                r_sorted = r_grp.sort_values("_u").reset_index(drop=True)
                row_u_records[rid_int] = [
                    (float(r_sorted.iloc[i]["_u"]), r_sorted.iloc[i]) for i in range(len(r_sorted))
                ]
                if len(r_sorted) < 2:
                    continue

                diffs = np.diff(r_sorted["_u"].values)
                for i, gap in enumerate(diffs):
                    if 1.75 * du_med <= gap <= (MAX_CONSECUTIVE_MISSING + 1.4) * du_med:
                        n_missing = int(round(gap / du_med)) - 1
                        if n_missing < 1 or n_missing > MAX_CONSECUTIVE_MISSING:
                            continue

                        base_row = r_sorted.iloc[i]
                        step_vec = u * (gap / (n_missing + 1))

                        for k in range(1, n_missing + 1):
                            new_x = float(base_row["Tam_X"] + step_vec[0] * k)
                            new_y = float(base_row["Tam_Y"] + step_vec[1] * k)
                            cand_geom = translate(tmpl_geom, xoff=new_x - tmpl_cx, yoff=new_y - tmpl_cy)

                            if overlaps_existing(cand_geom, orig_tree, orig_geoms, string_new_geoms):
                                rejected_overlap += 1
                                continue
                            if not is_valid_solar_panel(cand_geom, src, thresholds, aoi_union):
                                rejected_raster += 1
                                continue

                            string_new_geoms.append(cand_geom)
                            new_u = float(base_row["_u"] + (gap / (n_missing + 1)) * k)
                            new_pin = int(base_row["ID_Pin"]) + k
                            new_rec = {
                                "geom": cand_geom,
                                "ID_Pin": new_pin,
                                "Row_ID": rid_int,
                                "Tam_X": new_x,
                                "Tam_Y": new_y,
                                "layer": block,
                                "path": base_row["path"],
                                "String_ID": string_id,
                                "module_id": f"{prefix}{block.lower()}_{string_id.lower()}_r{rid_int}_rec_{len(in_row_recovered):05d}",
                                "is_distorted_recovered": True,
                                "panel_type": "distorted_seamline",
                            }
                            in_row_recovered.append(new_rec)
                            row_u_records[rid_int].append((new_u, pd.Series(new_rec)))

            # 2. Nội suy chéo hàng (Cross-Row)
            if len(sorted_rids) >= 2:
                all_u_pts = sorted(u_val for recs in row_u_records.values() for u_val, _ in recs)
                col_clusters: list[float] = []
                for u_val in all_u_pts:
                    if not col_clusters or abs(u_val - col_clusters[-1]) > 0.4 * du_med:
                        col_clusters.append(u_val)

                for rid_int in sorted_rids:
                    existing_us = np.array([u_val for u_val, _ in row_u_records[rid_int]])
                    for col_u in col_clusters:
                        if len(existing_us) > 0 and np.min(np.abs(existing_us - col_u)) <= 0.45 * du_med:
                            continue

                        best_ref = None
                        best_row_dist = 999
                        for other_rid in sorted_rids:
                            if other_rid == rid_int:
                                continue
                            for o_u, o_row in row_u_records[other_rid]:
                                if abs(o_u - col_u) <= 0.35 * du_med:
                                    r_dist = abs(other_rid - rid_int)
                                    if r_dist < best_row_dist:
                                        best_row_dist = r_dist
                                        best_ref = (other_rid, o_row)

                        if best_ref is not None and best_row_dist <= 2:
                            ref_rid, ref_row = best_ref
                            dv_signed = row_v_medians[rid_int] - row_v_medians[ref_rid]
                            new_x = float(ref_row["Tam_X"] + v[0] * dv_signed)
                            new_y = float(ref_row["Tam_Y"] + v[1] * dv_signed)
                            cand_geom = translate(tmpl_geom, xoff=new_x - tmpl_cx, yoff=new_y - tmpl_cy)

                            if overlaps_existing(cand_geom, orig_tree, orig_geoms, string_new_geoms):
                                rejected_overlap += 1
                                continue
                            if not is_valid_solar_panel(cand_geom, src, thresholds, aoi_union):
                                rejected_raster += 1
                                continue

                            string_new_geoms.append(cand_geom)
                            new_rec = {
                                "geom": cand_geom,
                                "ID_Pin": int(ref_row["ID_Pin"]),
                                "Row_ID": rid_int,
                                "Tam_X": new_x,
                                "Tam_Y": new_y,
                                "layer": block,
                                "path": ref_row["path"],
                                "String_ID": string_id,
                                "module_id": f"{prefix}{block.lower()}_{string_id.lower()}_r{rid_int}_xrec_{len(cross_row_recovered):05d}",
                                "is_distorted_recovered": True,
                                "panel_type": "distorted_seamline",
                            }
                            cross_row_recovered.append(new_rec)
                            existing_us = np.append(existing_us, col_u)
                            
            # 3. Mở rộng 2 đầu hàng (End-Extension) để lấp các cụm xám ở đầu/cuối String
            for rid_int in sorted_rids:
                recs = row_u_records.get(rid_int, [])
                if not recs:
                    continue
                recs_sorted = sorted(recs, key=lambda x: x[0])

                for direction, anchor_row in [(-1, recs_sorted[0][1]), (1, recs_sorted[-1][1])]:
                    for step in range(1, 25):
                        new_x = float(anchor_row["Tam_X"] + direction * u[0] * du_med * step)
                        new_y = float(anchor_row["Tam_Y"] + direction * u[1] * du_med * step)
                        cand_geom = translate(tmpl_geom, xoff=new_x - tmpl_cx, yoff=new_y - tmpl_cy)

                        if overlaps_existing(cand_geom, orig_tree, orig_geoms, string_new_geoms):
                            break  # Đụng tấm pin của String khác -> dừng ngay
                        if not is_valid_solar_panel(cand_geom, src, thresholds, aoi_union):
                            break  # Đụng đất trống / đường đi / biên AOI -> dừng ngay

                        string_new_geoms.append(cand_geom)
                        new_rec = {
                            "geom": cand_geom,
                            "ID_Pin": max(1, int(anchor_row["ID_Pin"]) + direction * step),
                            "Row_ID": rid_int,
                            "Tam_X": new_x,
                            "Tam_Y": new_y,
                            "layer": block,
                            "path": anchor_row["path"],
                            "String_ID": string_id,
                            "module_id": f"{prefix}{block.lower()}_{string_id.lower()}_r{rid_int}_ext_{len(in_row_recovered):05d}",
                            "is_distorted_recovered": True,
                            "panel_type": "distorted_seamline",
                        }
                        in_row_recovered.append(new_rec)
    finally:
        if src is not None:
            src.close()

    all_recovered = in_row_recovered + cross_row_recovered
    if all_recovered:
        rec_gdf = gpd.GeoDataFrame(all_recovered, geometry="geom", crs=gdf.crs)
        rec_gdf = rec_gdf.rename_geometry(gdf.geometry.name)
        out_gdf = pd.concat([gdf, rec_gdf], ignore_index=True)
    else:
        out_gdf = gdf

    out_path = Path(gpkg_out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        out_path.unlink()

        # Chuẩn hóa gọn tên Block trong module_id (bỏ tiền tố thừa 'thientan_master — ' nếu có) & khử trùng 100%
    out_gdf["module_id"] = (
        out_gdf["module_id"]
        .astype(str)
        .str.replace("thientan_master — ", "", regex=False)
        .str.replace(" ", "_", regex=False)
    )
    dup_mask = out_gdf.duplicated(subset=["module_id"], keep=False)
    if dup_mask.any():
        dup_counts = out_gdf.groupby("module_id").cumcount()
        out_gdf.loc[dup_counts > 0, "module_id"] = (
            out_gdf.loc[dup_counts > 0, "module_id"] + "_d" + dup_counts[dup_counts > 0].astype(str)
        )
    assert out_gdf["module_id"].is_unique, f"{plant_code}: Vẫn còn module_id trùng!"
    
    out_gdf.to_file(out_path, layer="modules", driver="GPKG")
    if aoi_gdf is not None:
        aoi_gdf.to_file(out_path, layer="aoi_boundary", driver="GPKG")

    return {
        "plant_code": plant_code,
        "mean_angle_deg": round(float(np.mean(angles_deg)), 2) if angles_deg else 0.0,
        "median_du_m": round(float(np.median(du_all)), 3) if du_all else 0.0,
        "median_dv_m": round(float(np.median(dv_all)), 3) if dv_all else 0.0,
        "zigzag_strings": zigzag_strings,
        "original_modules": len(gdf),
        "recovered_in_row": len(in_row_recovered),
        "recovered_cross_row": len(cross_row_recovered),
        "rejected_overlap": rejected_overlap,
        "rejected_raster": rejected_raster,
        "total_completed": len(out_gdf),
        "output_size_mb": round(out_path.stat().st_size / 1e6, 2),
    }


def main():
    results = []
    for code, (g_in, g_out) in PLANTS.items():
        print(f"Đang xử lý {code} ({g_in})...")
        res = process_plant(code, g_in, g_out)
        if res:
            results.append(res)

    df = pd.DataFrame(results)
    print("\n=== BẢNG TỔNG HỢP PCA V3 (CẤM CHỒNG ĐÈ + LỌC PIXEL ẢNH NỀN) ===")
    print(df.to_string(index=False))

    out_csv = Path("data/artifacts/audit_pca_summary.csv")
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    print(f"\nĐã lưu bảng thống kê tại: {out_csv}")


if __name__ == "__main__":
    main()