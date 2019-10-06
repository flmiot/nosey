import sys

from pyqtgraph.Qt import QtCore
import nosey

if __name__ == '__main__':
    input_file = None
    if len(sys.argv) > 1:
        input_file = sys.argv[1]

    nosey.gui.show()    

    if input_file:
        timer = QtCore.QTimer()
        timer.singleShot(200, lambda : nosey.gui.loadProject(input_file))

    else:
        nosey.gui.addGroup()
        nosey.gui.tableGroups.cellWidget(0, 2).toggle()


    nosey.app.exec_()
