import os

from PyQt4 import QtGui, uic


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'EleView_dialog_base.ui'))


class EleViewMainDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(EleViewMainDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)


DISPLAY_FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'EleView_dialog_display.ui'))


class EleViewDialogDisp(QtGui.QDialog, DISPLAY_FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(EleViewDialogDisp, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
