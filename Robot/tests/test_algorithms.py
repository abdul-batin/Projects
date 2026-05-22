"""Unit tests for algorithm components."""
import pytest
import numpy as np
from algorithm.grid_construction import Grid
from algorithm.sweep import Sweep
from algorithm.algorithms import Algorithms
from algorithm.metrics import Metrics
from shapely.geometry import Polygon


class TestGridConstruction:
    """Tests for grid construction."""
    
    def test_build_simple_grid(self):
        """Test building a simple grid without obstacles."""
        wall_poly = Polygon([[0, 0], [5, 0], [5, 5], [0, 5]])
        grid_builder = Grid()
        
        grid = grid_builder.build_grid(wall_poly, [], resolution=1.0)
        
        assert grid.shape[0] > 0
        assert grid.shape[1] > 0
        assert grid.dtype == np.uint8
        
        # Most cells should be free (0) for empty space
        free_cells = np.sum(grid == 0)
        assert free_cells > 0
    
    def test_build_grid_with_obstacles(self):
        """Test building a grid with obstacles."""
        wall_poly = Polygon([[0, 0], [10, 0], [10, 10], [0, 10]])
        obstacle = Polygon([[2, 2], [4, 2], [4, 4], [2, 4]])
        
        grid_builder = Grid()
        grid = grid_builder.build_grid(wall_poly, [obstacle], resolution=0.5)
        
        # Should have both free and occupied cells
        free_cells = np.sum(grid == 0)
        occupied_cells = np.sum(grid == 1)
        
        assert free_cells > 0
        assert occupied_cells > 0
    
    def test_grid_resolution(self):
        """Test that grid resolution affects grid size."""
        wall_poly = Polygon([[0, 0], [10, 0], [10, 10], [0, 10]])
        grid_builder = Grid()
        
        grid_coarse = grid_builder.build_grid(wall_poly, [], resolution=1.0)
        grid_fine = grid_builder.build_grid(wall_poly, [], resolution=0.5)
        
        # Finer resolution should produce larger grid
        assert grid_fine.shape[0] > grid_coarse.shape[0]
        assert grid_fine.shape[1] > grid_coarse.shape[1]


class TestSweepAlgorithms:
    """Tests for sweep algorithms."""
    
    def test_horizontal_sweep(self):
        """Test horizontal sweep algorithm."""
        # Simple 5x5 grid, all free
        grid = np.zeros((5, 5), dtype=np.uint8)
        
        sweep = Sweep(robot=None)
        segments = sweep.horizontal_sweep(grid)
        
        assert len(segments) > 0
        # Should have 5 segments (one per row)
        assert len(segments) == 5
    
    def test_vertical_sweep(self):
        """Test vertical sweep algorithm."""
        # Simple 5x5 grid, all free
        grid = np.zeros((5, 5), dtype=np.uint8)
        
        sweep = Sweep(robot=None)
        segments = sweep.vertical_sweep(grid)
        
        assert len(segments) > 0
        # Should have 5 segments (one per column)
        assert len(segments) == 5
    
    def test_sweep_with_obstacles(self):
        """Test sweep with obstacles."""
        # Grid with obstacle in middle
        grid = np.zeros((5, 5), dtype=np.uint8)
        grid[2, 2] = 1  # Obstacle
        
        sweep = Sweep(robot=None)
        segments = sweep.horizontal_sweep(grid)
        
        # Should break segments around obstacle
        assert len(segments) > 5


class TestAStar:
    """Tests for A* pathfinding."""
    
    def test_astar_simple_path(self):
        """Test A* finding a simple path."""
        # Simple grid, all free
        grid = np.zeros((10, 10), dtype=np.uint8)
        
        algo = Algorithms()
        path = algo.astar(grid, (0, 0), (5, 5))
        
        assert path is not None
        assert len(path) > 0
        assert path[0] == (0, 0)
        assert path[-1] == (5, 5)
    
    def test_astar_with_obstacle(self):
        """Test A* navigating around obstacle."""
        # Grid with wall in middle
        grid = np.zeros((10, 10), dtype=np.uint8)
        grid[:, 5] = 1  # Vertical wall
        grid[5, 5] = 0  # Gap in wall
        
        algo = Algorithms()
        path = algo.astar(grid, (0, 3), (0, 7))
        
        assert path is not None
        assert len(path) > 0
        # Path should go through the gap
        assert (5, 5) in path or any(p[0] == 5 for p in path)
    
    def test_astar_no_path(self):
        """Test A* when no path exists."""
        # Grid completely blocked
        grid = np.ones((10, 10), dtype=np.uint8)
        grid[0, 0] = 0  # Start free
        grid[9, 9] = 0  # Goal free, but unreachable
        
        algo = Algorithms()
        path = algo.astar(grid, (0, 0), (9, 9))
        
        # Should return empty list when no path found
        assert path == [] or path is None


class TestMetrics:
    """Tests for metrics calculation."""
    
    def test_compute_metrics_full_coverage(self):
        """Test metrics with full coverage."""
        grid = np.zeros((5, 5), dtype=np.uint8)
        
        # Path covers all cells
        path = [(r, c) for r in range(5) for c in range(5)]
        
        metrics_calc = Metrics()
        metrics = metrics_calc.compute_metrics(path, grid)
        
        assert "coverage" in metrics
        assert "path_length" in metrics
        assert metrics["coverage"] == 1.0
        assert metrics["path_length"] == 25
    
    def test_compute_metrics_partial_coverage(self):
        """Test metrics with partial coverage."""
        grid = np.zeros((10, 10), dtype=np.uint8)
        
        # Path covers only first row
        path = [(0, c) for c in range(10)]
        
        metrics_calc = Metrics()
        metrics = metrics_calc.compute_metrics(path, grid)
        
        assert metrics["coverage"] < 1.0
        assert metrics["coverage"] == 0.1  # 10 out of 100 cells
        assert metrics["path_length"] == 10
    
    def test_compute_metrics_with_obstacles(self):
        """Test metrics with obstacles in grid."""
        grid = np.zeros((10, 10), dtype=np.uint8)
        grid[5:, :] = 1  # Half the grid is obstacles
        
        # Path covers all free cells
        path = [(r, c) for r in range(5) for c in range(10)]
        
        metrics_calc = Metrics()
        metrics = metrics_calc.compute_metrics(path, grid)
        
        # Coverage should be 100% of free space
        assert metrics["coverage"] == 1.0
        assert metrics["path_length"] == 50
