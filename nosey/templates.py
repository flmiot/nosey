import os
from pyqtgraph.Qt import QtCore, QtGui

class HideButton(QtGui.QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        icon = QtGui.QIcon()
        dirname = os.path.dirname(__file__)
        icon.addPixmap(QtGui.QPixmap(os.path.join(dirname, 'icons/shown.png')), QtGui.QIcon.Normal, QtGui.QIcon.On)
        icon.addPixmap(QtGui.QPixmap(os.path.join(dirname, 'icons/hidden.png')), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setIcon(icon)
        self.setIconSize(QtCore.QSize(20, 20))
        self.setStyleSheet("QPushButton:checked { background-color: #a8fc97 }")
        self.setToolTip("Hide/Show this item")
        self.setFocusPolicy(QtCore.Qt.NoFocus)


class RemoveButton(QtGui.QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        icon = QtGui.QIcon()
        dirname = os.path.dirname(__file__)
        icon.addPixmap(QtGui.QPixmap(os.path.join(dirname, 'icons/cross.png')), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.setIcon(icon)
        self.setIconSize(QtCore.QSize(20, 20))
        self.setStyleSheet("background-color: #e8a497")
        self.setToolTip("Remove this item")
        self.setFocusPolicy(QtCore.Qt.NoFocus)


class ViewButton(QtGui.QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        icon = QtGui.QIcon()
        dirname = os.path.dirname(__file__)
        icon.addPixmap(QtGui.QPixmap(os.path.join(dirname, 'icons/view.png')), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.setIcon(icon)
        self.setIconSize(QtCore.QSize(20, 20))
        self.setToolTip("View this item in monitor")
        self.setFocusPolicy(QtCore.Qt.NoFocus)
