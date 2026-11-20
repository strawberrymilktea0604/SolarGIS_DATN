"""
STRtree + cKDTree Spatial Index & Boundary Landmarks API
Reference: DATA_CONTRACT.md (Section 3.1)
"""

from pathlib import Path
from typing import Dict, List, Any


class SpatialGridIndex:
    """Quản trị chỉ mục không gian R-Tree (STRtree) + 2D cKDTree cho 4 nhà máy."""

    def __init__(self, gpkg_dir: Path, crs_epsg: int = 32649) -> None:
        self.gpkg_dir = Path(gpkg_dir)
        self.crs_epsg = crs_epsg

    def get_candidates_in_radius(
        self,
        plant_code: str,
        x_utm: float,
        y_utm: float,
        radius_m: float = 0.524,
    ) -> List[Dict[str, Any]]:
        """Truy vấn O(log N) các tấm pin ứng viên trong bán kính r = 52.4 cm."""
        raise NotImplementedError("TV1 implements in Week 2-3")

    def get_block_string_boundary_landmarks(
        self,
        plant_code: str,
        block_code: str,
        string_code: str,
    ) -> Dict[str, Any]:
        """Trả về tọa độ UTM 4 góc biên và trục nội tại PCA (u, v) phục vụ Bidirectional Strip Anchoring."""
        raise NotImplementedError("TV1 implements in Week 2-3")
