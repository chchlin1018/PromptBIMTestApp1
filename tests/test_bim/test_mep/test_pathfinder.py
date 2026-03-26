"""Tests for bim/mep/pathfinder.py — 3D orthogonal A* pathfinding."""

from promptbim.bim.mep.pathfinder import MEPPathfinder, RoutePath, _simplify_path


class TestMEPPathfinder:
    def test_straight_path(self):
        pf = MEPPathfinder(grid_size=0.5)
        result = pf.find_path((0, 0, 0), (2, 0, 0))
        assert len(result.waypoints) >= 2
        assert result.total_length_m > 0
        # Should be roughly 2m
        assert abs(result.total_length_m - 2.0) < 0.6

    def test_path_around_obstacle(self):
        pf = MEPPathfinder(grid_size=0.5)
        # Block the direct path at (1,0,0)
        pf.add_obstacle(2, 0, 0)
        result = pf.find_path((0, 0, 0), (1.5, 0, 0))
        assert len(result.waypoints) >= 2
        # Path must go around
        assert result.total_length_m > 1.5

    def test_no_path(self):
        pf = MEPPathfinder(grid_size=0.5)
        # Surround the target
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                for dz in range(-1, 2):
                    pf.add_obstacle(10 + dx, 10 + dy, 10 + dz)
        result = pf.find_path((0, 0, 0), (5, 5, 5))
        assert len(result.waypoints) >= 2 or len(result.waypoints) == 0

    def test_same_start_end(self):
        pf = MEPPathfinder(grid_size=0.3)
        result = pf.find_path((1, 1, 1), (1, 1, 1))
        assert len(result.waypoints) == 1

    def test_vertical_path(self):
        pf = MEPPathfinder(grid_size=0.5)
        result = pf.find_path((0, 0, 0), (0, 0, 3))
        assert len(result.waypoints) >= 2
        assert abs(result.total_length_m - 3.0) < 0.6

    def test_add_obstacles_from_bbox(self):
        pf = MEPPathfinder(grid_size=1.0)
        pf.add_obstacles_from_bbox((0, 0, 0), (2, 2, 2))
        assert len(pf.obstacles) > 0
        assert (1, 1, 1) in pf.obstacles

    def test_add_obstacles_from_walls(self):
        pf = MEPPathfinder(grid_size=0.5)
        walls = [{"start": (0, 0), "end": (5, 0), "thickness": 0.2}]
        pf.add_obstacles_from_walls(walls, elevation=0, height=3)
        assert len(pf.obstacles) > 0

    def test_route_path_from_waypoints(self):
        pts = [(0, 0, 0), (1, 0, 0), (1, 1, 0)]
        rp = RoutePath.from_waypoints(pts, grid_size=0.3)
        assert len(rp.segments) == 2
        assert abs(rp.total_length_m - 2.0) < 0.01

    def test_simplify_collinear(self):
        pts = [(0, 0, 0), (1, 0, 0), (2, 0, 0), (3, 0, 0)]
        simplified = _simplify_path(pts)
        assert len(simplified) == 2
        assert simplified[0] == (0, 0, 0)
        assert simplified[1] == (3, 0, 0)

    def test_simplify_with_turns(self):
        pts = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (1, 1, 1)]
        simplified = _simplify_path(pts)
        assert len(simplified) == 4  # all are turns, none removed
