#!/usr/bin/env bash
set -euo pipefail

PLANT_NAME="${1:-tn19}"
INPUT_TIF="${2:-TN19_SonarPanel.tif}"

docker run --rm -e GDAL_CACHEMAX=4096 \
  -v "$(pwd)/data:/work" \
  ghcr.io/osgeo/gdal:ubuntu-full-3.8.4 \
  gdal2tiles.py --xyz --exclude --processes=8 -z 15-21 \
  --tiledriver=WEBP --webp-quality=85 \
  "/work/raw/${INPUT_TIF}" "/work/artifacts/tiles_${PLANT_NAME}/"

# Đóng gói PMTiles (nếu đã cài mb-util & pmtiles CLI)
if command -v mb-util >/dev/null 2>&1 && command -v pmtiles >/dev/null 2>&1; then
  mb-util --image_format=webp --scheme=xyz "data/artifacts/tiles_${PLANT_NAME}" "data/artifacts/${PLANT_NAME}_ortho.mbtiles"
  pmtiles convert "data/artifacts/${PLANT_NAME}_ortho.mbtiles" "data/artifacts/${PLANT_NAME}_ortho.pmtiles"
fi