from PyQt4.QtCore import Qt
from PyQt4.QtGui import QPen


ZOOM_IN_FACTOR = 1.25
ZOOM_OUT_FACTOR = 1 / ZOOM_IN_FACTOR
PT1, PT2 = "first point", "second point"
GPEN, RPEN = QPen(Qt.green, 1), QPen(Qt.red, 1)