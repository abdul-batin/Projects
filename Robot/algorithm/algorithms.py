"""Module containing pathfinding algorithms."""
import logging
import heapq

logger = logging.getLogger(__name__)

class Algorithms:
    """Class containing various pathfinding algorithms."""
    
    def astar(self, grid, start, goal):
        """
        A* pathfinding algorithm.
        
        Args:
            grid: 2D array representing the grid
            start: Starting position tuple
            goal: Goal position tuple
            
        Returns:
            List of positions representing the path, or empty list if no path found
        """
        h, w = grid.shape

        def neighbors(n):
            r, c = n
            for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < h and 0 <= nc < w and grid[nr, nc] == 0:
                    yield (nr, nc)

        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        pq = [(0, start)]
        came_from = {}
        g = {start: 0}

        while pq:
            _, cur = heapq.heappop(pq)

            if cur == goal:
                return self._reconstruct_path(came_from, cur)

            for n in neighbors(cur):
                cost = g[cur] + 1
                if cost < g.get(n, float("inf")):
                    came_from[n] = cur
                    g[n] = cost
                    f = cost + heuristic(n, goal)
                    heapq.heappush(pq, (f, n))
        
        return []
    
    def _reconstruct_path(self, came_from, cur):
        """Reconstruct path from came_from dictionary."""
        path = [cur]
        while cur in came_from:
            cur = came_from[cur]
            path.append(cur)
        return path[::-1]
