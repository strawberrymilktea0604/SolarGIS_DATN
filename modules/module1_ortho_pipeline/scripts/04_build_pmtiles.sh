#!/usr/bin/env bash
# =============================================================================
# 04_build_pmtiles.sh - Xuất XYZ WebP Raster Tiles (--exclude -z 15-21) & PMTiles
# Tham chiếu: DATA_CONTRACT.md (Mục 7.2)
# =============================================================================
set -euo pipefail

INPUT_TIF="${1:-data/raw/SonarPanel.tif}"
TILES_DIR="${2:-data/artifacts/tiles_tn19}"
OUTPUT_PMTILES="${3:-data/artifacts/tn19_ortho.pmtiles}"

echo "[1/2] Slicing GeoTIFF into XYZ WebP tiles (zoom 15-21, exclude empty tiles)..."
docker run --rm -e GDAL_CACHEMAX=4096 -v "$(pwd):/work" ghcr.io/osgeo/gdal:ubuntu-full-3.8.4 \
  gdal2tiles.py --xyz --exclude --processes=8 -z 15-21 \
  --tiledriver=WEBP --webp-quality=85 \
  "/work/${INPUT_TIF}" "/work/${TILES_DIR}"

echo "[2/2] Packaging into single static PMTiles archive..."
mb-util --image_format=webp --scheme=xyz "${TILES_DIR}" "${TILES_DIR}.mbtiles"
pmtiles convert "${TILES_DIR}.mbtiles" "${OUTPUT_PMTILES}"
echo "Done: ${OUTPUT_PMTILES}"
