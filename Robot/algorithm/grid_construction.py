"""Module for constructing occupancy grids from polygon geometries."""
import logging
import numpy as np
from shapely.geometry import Point

logger = logging.getLogger(__name__)


class Grid():
    """A class for building occupancy grids from wall and obstacle polygons."""
    
    def build_grid(self, wall_polygon, obstacle_polygons, resolution=0.1):
        """
        Build an occupancy grid from wall and obstacle polygons.
        
        Args:
            wall_polygon: Polygon defining the valid space
            obstacle_polygons: List of polygons representing obstacles
            resolution: Grid cell size in units
            
        Returns:
            numpy array representing the occupancy grid
        """
        minx, miny, maxx, maxy = wall_polygon.bounds

        width = int((maxx - minx) / resolution)
        height = int((maxy - miny) / resolution)

        grid = np.zeros((height, width), dtype=np.uint8)

        for r in range(height):
            for c in range(width):
                x = minx + c * resolution
                y = miny + r * resolution
                p = Point(x, y)

                if not wall_polygon.contains(p):
                    grid[r, c] = 1
                    continue

                for obs in obstacle_polygons:
                    if obs.contains(p):
                        grid[r, c] = 1
                        break

        return grid
