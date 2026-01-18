"""Main planning module that coordinates sweep and pathfinding algorithms."""
import logging
from algorithm.sweep import Sweep
from algorithm.algorithms import Algorithms
from algorithm.metrics import Metrics

logger = logging.getLogger(__name__)

sweep = Sweep(robot=None)  # Pass None since we don't need robot instance yet
algorithms = Algorithms()
metrics_calculator = Metrics()

def build_full_path(grid, segments):
    path = []

    for i, seg in enumerate(segments):
        path.extend(seg)

        if i + 1 < len(segments):
            connector = algorithms.astar(grid, seg[-1], segments[i + 1][0])
            if connector:
                path.extend(connector[1:])

    return path


def plan(grid):
    logger.info(f"Planning: Starting path planning for grid of shape {grid.shape}")
    candidates = []

    sweep_methods = {
        "horizontal": sweep.horizontal_sweep,
        "vertical": sweep.vertical_sweep
    }

    for name, sweep_fn in sweep_methods.items():
        logger.debug(f"Planning: Running {name} sweep")
        segments = sweep_fn(grid)
        full_path = build_full_path(grid, segments)
        metrics = metrics_calculator.compute_metrics(full_path, grid)
        logger.info(f"Planning: {name} strategy - coverage: {metrics['coverage']:.2%}, length: {metrics['path_length']}")

        candidates.append({
            "strategy": name,
            "path": full_path,
            "metrics": metrics
        })

    best = max(candidates, key=lambda c: c["metrics"]["coverage"])

    return {
        "best": best,
        "candidates": candidates
    }
