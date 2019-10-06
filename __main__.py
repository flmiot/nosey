import sys

from pyqtgraph.Qt import QtCore
import nosey

if __name__ == '__main__':
    input_file = None
    if len(sys.argv) > 1:
        input_file = sys.argv[1]



    if input_file:
        nosey.gui.loadProject(input_file)

    else:
        nosey.gui.addGroup()
        nosey.gui.tableGroups.cellWidget(0, 2).toggle()

    nosey.gui.show()
    nosey.app.exec_()
