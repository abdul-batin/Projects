"""Module for computing path coverage metrics."""
import logging

logger = logging.getLogger(__name__)


class Metrics():
    """Class for computing metrics on robot paths."""

    def compute_metrics(self, path, grid):
        """Compute coverage and path length metrics."""
        logger.debug(f"Metrics: Computing metrics for path of length {len(path)}")
        covered = set(path)

        free_cells = sum(
            1 for r in range(grid.shape[0])
            for c in range(grid.shape[1])
            if grid[r, c] == 0
        )

        coverage = len(covered) / free_cells if free_cells else 0

        return {
            "coverage": round(coverage, 3),
            "path_length": len(path)
        }