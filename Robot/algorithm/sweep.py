
"""Module for sweep algorithms used in robot path planning."""
import logging

logger = logging.getLogger(__name__)


class Sweep():
    """Implements horizontal and vertical sweep algorithms for grid traversal."""
    def __init__(self, robot):
        # Store robot instance for future use in sweep operations
        self.robot = robot

    def horizontal_sweep(self, grid):
        """Perform a horizontal sweep across the grid in alternating directions."""
        h, w = grid.shape
        logger.debug(f"Sweep: Starting horizontal sweep on {h}x{w} grid")
        segments = []
        ltr = True

        for r in range(h):
            cols = range(w) if ltr else range(w - 1, -1, -1)
            current = []

            for c in cols:
                if grid[r, c] == 0:
                    current.append((r, c))
                else:
                    if current:
                        segments.append(current)
                        current = []

            if current:
                segments.append(current)

            ltr = not ltr

        return segments

    def vertical_sweep(self, grid):
        """Perform a vertical sweep down the grid in alternating directions."""
        h, w = grid.shape
        logger.debug(f"Sweep: Starting vertical sweep on {h}x{w} grid")
        segments = []
        ttb = True

        for c in range(w):
            rows = range(h) if ttb else range(h - 1, -1, -1)
            current = []

            for r in rows:
                if grid[r, c] == 0:
                    current.append((r, c))
                else:
                    if current:
                        segments.append(current)
                        current = []

            if current:
                segments.append(current)

            ttb = not ttb

        return segments


    