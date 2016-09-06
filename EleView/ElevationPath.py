from PyQt4.QtCore import QPointF

from .Constants import EARTH_RADIUS_M, EARTH_CIRCUMFERENCE_M


class ElevationPath(object):
    def __init__(self, points):
        if not isinstance(points, list):
            raise TypeError("points argument must be a list")
        if len(points) < 2:
            raise TypeError("need at least two points to work with")
        if not all(isinstance(p, QPointF) for p in points):
            raise TypeError("points must be given as QPointF")
        self.points = points
        self.min_x = self.max_x = points[0].x()
        self.min_y = self.max_y = points[0].y()
        self._extract_bounds()

    def _extract_bounds(self):
        for point in self.points:
            self.min_x = min(self.min_x, point.x())
            self.max_x = max(self.max_x, point.x())
            self.min_y = min(self.min_y, point.y())
            self.max_y = max(self.max_y, point.y())

    def calculate_points(self):
        pass

    def create_path(self):
        pass
