from math import pi
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QPen


ZOOM_IN_FACTOR = 1.25
ZOOM_OUT_FACTOR = 1 / ZOOM_IN_FACTOR
PT1, PT2 = "first point", "second point"
GPEN, RPEN = QPen(Qt.green, 1), QPen(Qt.red, 1)
EARTH_RADIUS_KM = 6371
EARTH_RADIUS_M = EARTH_RADIUS_KM * 1000
EARTH_CIRCUMFERENCE_M = EARTH_RADIUS_M * pi
