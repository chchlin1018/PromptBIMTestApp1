"""3D orthogonal A* pathfinding for MEP routing.

Pipes/ducts are routed on a discretised 3-D grid, restricted to 90-degree
turns.  A turn penalty discourages excessive bends.
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field

import numpy as np

from promptbim.debug import get_logger

logger = get_logger("mep.pathfinder")


@dataclass
class PathSegment:
    """A straight segment of a routed path."""

    start: tuple[float, float, float]
    end: tuple[float, float, float]
    direction: tuple[int, int, int]
    length_m: float


@dataclass
class RoutePath:
    """Result of a pathfinding run."""

    waypoints: list[tuple[float, float, float]]
    segments: list[PathSegment] = field(default_factory=list)
    total_length_m: float = 0.0

    @classmethod
    def from_waypoints(
        cls, waypoints: list[tuple[float, float, float]], grid_size: float
    ) -> RoutePath:
        segments: list[PathSegment] = []
        total = 0.0
        for i in range(len(waypoints) - 1):
            s, e = waypoints[i], waypoints[i + 1]
            dx = e[0] - s[0]
            dy = e[1] - s[1]
            dz = e[2] - s[2]
            length = (dx**2 + dy**2 + dz**2) ** 0.5
            direction = (
                int(np.sign(dx)) if abs(dx) > 1e-6 else 0,
                int(np.sign(dy)) if abs(dy) > 1e-6 else 0,
                int(np.sign(dz)) if abs(dz) > 1e-6 else 0,
            )
            segments.append(PathSegment(start=s, end=e, direction=direction, length_m=length))
            total += length
        return cls(waypoints=waypoints, segments=segments, total_length_m=total)


class MEPPathfinder:
    """3D orthogonal A* pathfinder (restricted to 90-degree turns)."""

    DIRECTIONS = [
        (1, 0, 0),
        (-1, 0, 0),
        (0, 1, 0),
        (0, -1, 0),
        (0, 0, 1),
        (0, 0, -1),
    ]

    def __init__(self, grid_size: float = 0.3, building_span_m: float = 0.0) -> None:
        # Adaptive grid size based on building span (MEP-01 fix)
        if building_span_m > 0:
            if building_span_m > 100:
                grid_size = 0.5
            elif building_span_m > 50:
                grid_size = 0.4
            # else keep default 0.3m
            logger.debug("Adaptive grid: span=%.1fm → grid=%.2fm", building_span_m, grid_size)
        self.grid = grid_size
        self.obstacles: set[tuple[int, int, int]] = set()

    def add_obstacle(self, gx: int, gy: int, gz: int) -> None:
        self.obstacles.add((gx, gy, gz))

    def add_obstacles_from_bbox(
        self,
        min_pt: tuple[float, float, float],
        max_pt: tuple[float, float, float],
    ) -> None:
        """Fill obstacle voxels for an axis-aligned bounding box."""
        g = self.grid
        x0 = int(np.floor(min_pt[0] / g))
        y0 = int(np.floor(min_pt[1] / g))
        z0 = int(np.floor(min_pt[2] / g))
        x1 = int(np.ceil(max_pt[0] / g))
        y1 = int(np.ceil(max_pt[1] / g))
        z1 = int(np.ceil(max_pt[2] / g))
        for ix in range(x0, x1 + 1):
            for iy in range(y0, y1 + 1):
                for iz in range(z0, z1 + 1):
                    self.obstacles.add((ix, iy, iz))

    def add_obstacles_from_walls(
        self,
        walls: list[dict],
        elevation: float,
        height: float,
    ) -> None:
        """Add obstacles from wall definitions (start/end + thickness)."""
        for w in walls:
            sx, sy = w["start"]
            ex, ey = w["end"]
            t = w.get("thickness", 0.2) / 2.0
            dx, dy = ex - sx, ey - sy
            length = (dx**2 + dy**2) ** 0.5
            if length < 1e-6:
                continue
            nx, ny = -dy / length, dx / length
            xs = [sx - nx * t, sx + nx * t, ex + nx * t, ex - nx * t]
            ys = [sy - ny * t, sy + ny * t, ey + ny * t, ey - ny * t]
            min_pt = (min(xs), min(ys), elevation)
            max_pt = (max(xs), max(ys), elevation + height)
            self.add_obstacles_from_bbox(min_pt, max_pt)

    # ---- coordinate conversion ----

    def _to_grid(self, pt: tuple[float, float, float]) -> tuple[int, int, int]:
        return (
            int(round(pt[0] / self.grid)),
            int(round(pt[1] / self.grid)),
            int(round(pt[2] / self.grid)),
        )

    def _to_world(self, gpt: tuple[int, int, int]) -> tuple[float, float, float]:
        return (
            gpt[0] * self.grid,
            gpt[1] * self.grid,
            gpt[2] * self.grid,
        )

    # ---- heuristic ----

    @staticmethod
    def _manhattan(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
        return float(abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2]))

    # ---- main pathfinding ----

    def find_path(
        self,
        start: tuple[float, float, float],
        end: tuple[float, float, float],
        turn_penalty: float = 2.0,
        max_iterations: int = 50_000,
    ) -> RoutePath:
        """A* search from *start* to *end* with turn penalty.

        Returns a :class:`RoutePath` with world-coordinate waypoints
        (empty if no path found).
        """
        logger.debug(
            "find_path: grid=%.2f, obstacles=%d, start=%s, end=%s",
            self.grid,
            len(self.obstacles),
            start,
            end,
        )
        start_g = self._to_grid(start)
        end_g = self._to_grid(end)

        if start_g == end_g:
            w = self._to_world(start_g)
            return RoutePath.from_waypoints([w], self.grid)

        # (f_cost, counter, position, prev_direction)
        counter = 0
        open_set: list[tuple[float, int, tuple[int, int, int], tuple[int, int, int] | None]] = [
            (0.0, counter, start_g, None),
        ]
        came_from: dict[tuple[int, int, int], tuple[int, int, int]] = {}
        g_score: dict[tuple[int, int, int], float] = {start_g: 0.0}
        direction_at: dict[tuple[int, int, int], tuple[int, int, int] | None] = {start_g: None}

        iterations = 0
        while open_set and iterations < max_iterations:
            iterations += 1
            f, _, current, prev_dir = heapq.heappop(open_set)

            if current == end_g:
                path = self._reconstruct(came_from, current)
                world_pts = [self._to_world(p) for p in path]
                # Simplify: merge collinear segments
                simplified = _simplify_path(world_pts)
                route = RoutePath.from_waypoints(simplified, self.grid)
                logger.debug(
                    "Path found: %d iterations, length=%.2fm, segments=%d",
                    iterations,
                    route.total_length_m,
                    len(route.segments),
                )
                return route

            for dx, dy, dz in self.DIRECTIONS:
                neighbor = (current[0] + dx, current[1] + dy, current[2] + dz)
                if neighbor in self.obstacles:
                    continue

                move_cost = self.grid
                curr_dir = (dx, dy, dz)
                if prev_dir is not None and curr_dir != prev_dir:
                    move_cost += turn_penalty

                new_g = g_score[current] + move_cost
                if new_g < g_score.get(neighbor, float("inf")):
                    g_score[neighbor] = new_g
                    h = self._manhattan(neighbor, end_g) * self.grid
                    counter += 1
                    heapq.heappush(open_set, (new_g + h, counter, neighbor, curr_dir))
                    came_from[neighbor] = current
                    direction_at[neighbor] = curr_dir

        logger.debug("No path found after %d iterations", iterations)
        return RoutePath(waypoints=[])  # no path found

    @staticmethod
    def _reconstruct(
        came_from: dict[tuple[int, int, int], tuple[int, int, int]],
        current: tuple[int, int, int],
    ) -> list[tuple[int, int, int]]:
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path


def _simplify_path(pts: list[tuple[float, float, float]]) -> list[tuple[float, float, float]]:
    """Remove intermediate collinear points."""
    if len(pts) <= 2:
        return pts
    result = [pts[0]]
    for i in range(1, len(pts) - 1):
        prev = result[-1]
        curr = pts[i]
        nxt = pts[i + 1]
        d1 = (curr[0] - prev[0], curr[1] - prev[1], curr[2] - prev[2])
        d2 = (nxt[0] - curr[0], nxt[1] - curr[1], nxt[2] - curr[2])
        # Normalize to compare direction
        l1 = (d1[0] ** 2 + d1[1] ** 2 + d1[2] ** 2) ** 0.5
        l2 = (d2[0] ** 2 + d2[1] ** 2 + d2[2] ** 2) ** 0.5
        if l1 < 1e-9 or l2 < 1e-9:
            continue
        n1 = (d1[0] / l1, d1[1] / l1, d1[2] / l1)
        n2 = (d2[0] / l2, d2[1] / l2, d2[2] / l2)
        if abs(n1[0] - n2[0]) > 1e-6 or abs(n1[1] - n2[1]) > 1e-6 or abs(n1[2] - n2[2]) > 1e-6:
            result.append(curr)
    result.append(pts[-1])
    return result
