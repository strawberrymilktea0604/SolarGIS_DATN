"""
spatial_grid_index: Shared spatial indexing library (TV1 -> TV2)
Reference: DATA_CONTRACT.md (Section 3)
"""

from .index import SpatialGridIndex
from .snapping import topological_grid_snap
from .mass_spring import mass_spring_refine

__all__ = [
    "SpatialGridIndex",
    "topological_grid_snap",
    "mass_spring_refine",
]
