import random
import sqlite3
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from PIL import Image
from rasterio.features import geometry_mask
from rasterio.windows import Window, bounds as win_bounds, transform as win_transform
from shapely.geometry import box
from shapely.strtree import STRtree
from tqdm import tqdm

TILE_SIZE = 1024
OVERLAP = 0.20
STRIDE = int(TILE_SIZE * (1.0 - OVERLAP))  # 819 px
MIN_VISIBLE_RATIO = 0.60                    # Chỉ giữ nhãn tấm pin còn >= 60% diện tích trong ô cắt
NEG_SAMPLE_RATIO = 0.10                     # Giữ thêm 10% ô ảnh nền âm tính
RANDOM_SEED = 42

OUT_ROOT = Path("data/artifacts/dataset_ai1_ortho")

# Cấu hình nguồn dữ liệu 4 nhà máy (ưu tiên .tif gốc trong data/raw nếu đã tải, fallback sang raster trong _master.gpkg)
PLANTS_CFG = {
    "TN19": {
        "completed_gpkg": "data/gpkg/thuannam19_completed.gpkg",
        "master_gpkg": "data/gpkg/thuannam19_master.gpkg",
        "raw_tif": "data/raw/TN19_SonarPanel.tif",
        "splits": {
            "train": {"Block2", "Block4"},
            "val": {"Block1", "Block3"},
            "test": {"Block5", "Block6"},
        },
    },
    "TNDL": {
        "completed_gpkg": "data/gpkg/thuannamduclong_completed.gpkg",
        "master_gpkg": "data/gpkg/thuannamduclong_master.gpkg",
        "raw_tif": "data/raw/TNDL_SonarPanelOrthoGeoTIFF.tif",
        "splits": None,  # Tự chia 60/15/25 theo thứ tự Block cố định
    },
    "TT12": {
        "completed_gpkg": "data/gpkg/thientan_completed.gpkg",
        "master_gpkg": "data/gpkg/thientan_master.gpkg",
        "raw_tif": "data/raw/TT12_SonarPanelOrthoGeoTIFF.tif",
        "splits": None,
    },
    "BIM2": {
        "completed_gpkg": "data/gpkg/BIM2_completed.gpkg",
        "master_gpkg": "data/gpkg/BIM2_master.gpkg",
        "raw_tif": "data/raw/BIM2_SonarPanelOrthoGeoTIFF.tif",
        "splits": None,
    },
}


def find_raster_layer(gpkg_path: Path) -> str | None:
    con = sqlite3.connect(gpkg_path)
    try:
        rows = con.execute(
            "SELECT table_name FROM gpkg_contents WHERE data_type = 'tiles'"
        ).fetchall()
        return rows[0][0] if rows else None
    finally:
        con.close()


def open_plant_raster(cfg: dict) -> rasterio.DatasetReader:
    raw_tif = Path(cfg["raw_tif"])
    if raw_tif.exists():
        print(f"  -> Đọc ảnh Ortho gốc độ phân giải cao: {raw_tif}")
        return rasterio.open(raw_tif)

    master_gpkg = Path(cfg["master_gpkg"])
    layer = find_raster_layer(master_gpkg)
    if layer is None:
        raise FileNotFoundError(f"Không thấy file {raw_tif} lẫn lớp raster trong {master_gpkg}")
    print(f"  -> Fallback đọc lớp raster '{layer}' trong {master_gpkg.name}")
    return rasterio.open(f"GPKG:{master_gpkg.resolve()}:{layer}")


def build_block_split_map(blocks: list[str], explicit_splits: dict | None) -> dict[str, str]:
    if explicit_splits is not None:
        mapping = {}
        for split_name, blk_set in explicit_splits.items():
            for b in blk_set:
                mapping[b] = split_name
        return mapping

    # Chia cố định theo tên Block đã sắp xếp: ~60% train, ~15% val, ~25% test
    sorted_blks = sorted(blocks)
    n = len(sorted_blks)
    if n == 2:
        return {sorted_blks[0]: "train", sorted_blks[1]: "test"}

    n_train = max(1, int(round(n * 0.60)))
    n_val = max(1, int(round(n * 0.15)))
    mapping = {}
    for i, b in enumerate(sorted_blks):
        if i < n_train:
            mapping[b] = "train"
        elif i < n_train + n_val:
            mapping[b] = "val"
        else:
            mapping[b] = "test"
    return mapping


def geom_to_yolo_obb_line(geom, inv_transform) -> str | None:
    """Chuyển đa giác EPSG:32649 sang dòng nhãn YOLO-OBB chuẩn hóa [0, 1]."""
    mrr = geom.minimum_rotated_rectangle
    coords = list(mrr.exterior.coords)[:4]
    if len(coords) != 4:
        return None

    pts_norm = []
    for x_utm, y_utm in coords:
        col, row = inv_transform * (x_utm, y_utm)
        nx = float(np.clip(col / TILE_SIZE, 0.0, 1.0))
        ny = float(np.clip(row / TILE_SIZE, 0.0, 1.0))
        pts_norm.extend([nx, ny])

    return "0 " + " ".join(f"{v:.6f}" for v in pts_norm)


def slice_plant(plant_code: str, cfg: dict, rng: random.Random) -> dict:
    comp_path = Path(cfg["completed_gpkg"])
    if not comp_path.exists():
        print(f"[SKIP] Không thấy {comp_path}")
        return {}

    gdf = gpd.read_file(comp_path, layer="modules")
    aoi_gdf = gpd.read_file(comp_path, layer="aoi_boundary")
    aoi_union = aoi_gdf.geometry.union_all()

    block_split = build_block_split_map(gdf["layer"].unique().tolist(), cfg["splits"])
    print(f"\n=== CẮT MẢNH {plant_code} | Phân chia Block: {block_split} ===")

    geoms = gdf.geometry.values
    blocks = gdf["layer"].values
    tree = STRtree(geoms)

    counts = {"train": 0, "val": 0, "test": 0, "neg": 0}
    neg_candidates = []

    with open_plant_raster(cfg) as src:
        # Chỉ quét trong khung bao của aoi_boundary để tiết kiệm thời gian
        minx, miny, maxx, maxy = aoi_union.bounds
        row_top, col_left = src.index(minx, maxy)
        row_bot, col_right = src.index(maxx, miny)

        c_start = max(0, min(col_left, col_right))
        c_end = min(src.width, max(col_left, col_right))
        r_start = max(0, min(row_top, row_bot))
        r_end = min(src.height, max(row_top, row_bot))

        windows = [
            Window(c, r, TILE_SIZE, TILE_SIZE)
            for r in range(r_start, r_end, STRIDE)
            for c in range(c_start, c_end, STRIDE)
        ]

        for win in tqdm(windows, desc=f"Slicing {plant_code}"):
            w_minx, w_miny, w_maxx, w_maxy = win_bounds(win, src.transform)
            w_box = box(w_minx, w_miny, w_maxx, w_maxy)

            # Bỏ qua các ô nằm hoàn toàn ngoài aoi_boundary
            if not w_box.intersects(aoi_union):
                continue
            inter_aoi_ratio = w_box.intersection(aoi_union).area / w_box.area
            if inter_aoi_ratio < 0.15:
                continue

            # Đọc ảnh RGB 1024x1024
            img_arr = src.read([1, 2, 3], window=win, boundless=True, fill_value=0)
            rgb = np.transpose(img_arr, (1, 2, 0))  # (H, W, 3)

            # Bỏ qua ô gần như đen/trắng rỗng
            non_empty_ratio = ((rgb.sum(axis=2) > 15) & (rgb.sum(axis=2) < 755)).mean()
            if non_empty_ratio < 0.20:
                continue

            # MASKING: Tô đen toàn bộ pixel nằm NGOÀI aoi_boundary để không rò rỉ tấm pin chưa vẽ nhãn
            w_tf = win_transform(win, src.transform)
            if inter_aoi_ratio < 0.999:
                outside_mask = geometry_mask(
                    [aoi_union], out_shape=(TILE_SIZE, TILE_SIZE), transform=w_tf, invert=False
                )
                rgb[outside_mask] = 0

            # Tìm các tấm pin giao với ô cắt
            cand_idxs = tree.query(w_box, predicate="intersects")
            inv_tf = ~w_tf
            label_lines = []
            tile_blocks = []

            for idx in cand_idxs:
                g = geoms[idx]
                vis_ratio = g.intersection(w_box).area / max(g.area, 1e-6)
                if vis_ratio < MIN_VISIBLE_RATIO:
                    continue
                line = geom_to_yolo_obb_line(g, inv_tf)
                if line:
                    label_lines.append(line)
                    tile_blocks.append(blocks[idx])

            tile_name = f"{plant_code.lower()}_r{int(win.row_off)}_c{int(win.col_off)}"

            if not label_lines:
                # Lưu ứng viên ảnh nền âm tính (chỉ lấy nếu ô nằm sâu trong AOI)
                if inter_aoi_ratio > 0.85:
                    neg_candidates.append((tile_name, rgb))
                continue

            # Xác định tập train/val/test theo Block chiếm đa số trong ô cắt
            maj_block = max(set(tile_blocks), key=tile_blocks.count)
            split = block_split.get(maj_block, "train")

            img_dir = OUT_ROOT / "images" / split
            lbl_dir = OUT_ROOT / "labels" / split
            img_dir.mkdir(parents=True, exist_ok=True)
            lbl_dir.mkdir(parents=True, exist_ok=True)

            Image.fromarray(rgb.astype(np.uint8)).save(img_dir / f"{tile_name}.jpg", quality=92)
            (lbl_dir / f"{tile_name}.txt").write_text("\n".join(label_lines) + "\n", encoding="utf-8")
            counts[split] += 1

    # Bổ sung 10% ảnh nền âm tính vào tập train
    n_neg = min(len(neg_candidates), int(round(counts["train"] * NEG_SAMPLE_RATIO)))
    if n_neg > 0:
        img_dir = OUT_ROOT / "images" / "train"
        lbl_dir = OUT_ROOT / "labels" / "train"
        for tile_name, rgb in rng.sample(neg_candidates, n_neg):
            Image.fromarray(rgb.astype(np.uint8)).save(img_dir / f"{tile_name}_neg.jpg", quality=92)
            (lbl_dir / f"{tile_name}_neg.txt").write_text("", encoding="utf-8")
            counts["neg"] += 1

    print(f"  => Xong {plant_code}: {counts}")
    return counts


def write_yolo_yaml():
    yaml_path = OUT_ROOT / "dataset_ai1_ortho.yaml"
    yaml_text = (
        f"path: {OUT_ROOT.resolve().as_posix()}\n"
        "train: images/train\n"
        "val: images/val\n"
        "test: images/test\n\n"
        "names:\n"
        "  0: solar_panel\n"
    )
    yaml_path.write_text(yaml_text, encoding="utf-8")
    print(f"\nĐã tạo file cấu hình YOLO-OBB tại: {yaml_path}")


def main():
    rng = random.Random(RANDOM_SEED)
    total = {"train": 0, "val": 0, "test": 0, "neg": 0}
    for code, cfg in PLANTS_CFG.items():
        c = slice_plant(code, cfg, rng)
        for k in total:
            total[k] += c.get(k, 0)

    write_yolo_yaml()
    print(f"\n=== TỔNG KẾT DATASET AI 1 (1024x1024) ===\n{total}")


if __name__ == "__main__":
    main()