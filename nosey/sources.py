import re
import os
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

import nosey
from nosey.analysis.scan import Scan
from nosey.analysis.recipes import SOLEILRecipe
from nosey.templates import HideButton, RemoveButton, ViewButton

class Sources(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.threads = []
        self.proxies = []


    def setupSources(self):
        pass


    def addSource(self):
        try:
            #log_path = str(QtGui.QFileDialog.getOpenFileName(self, 'Select logfile')[0])
            paths = QtGui.QFileDialog.getOpenFileNames(self, 'Select images')[0]
            print(paths)

            for file_path in paths:
                print(file_path)
                self._read_scan(file_path, log_file = None)

        except Exception as e:
            nosey.Log.error(e)


    def _read_scan(self, img_path, log_file):

        rows = self.tableSources.rowCount()
        self.tableSources.insertRow(rows)

        # Button items
        btn_active = HideButton()
        btn_active.setCheckable(True)
        btn_active.toggle()

        btn_remove = RemoveButton()
        btn_view = ViewButton("View")
        self.tableSources.setCellWidget(rows, 0, btn_active)
        self.tableSources.setCellWidget(rows, 1, btn_remove)
        self.tableSources.setCellWidget(rows, 2, btn_view)

        # Remaining items
        item01 = QtGui.QTableWidgetItem()

        self.tableSources.setItem(rows, 3, item01)

        # matches = re.findall(r'.?\_(\d{5})\.FIO', os.path.split(path)[1])
        # scan_no = matches[0]
        # scan_no = '_' + scan_no + '_'   # add underscores to avoid moxing up image and scan numbers
        # #img_path = os.path.join(path, 'pilatus_100k')
        scan_name = os.path.split(img_path)[1]
        # file_names = os.listdir(img_path)
        # file_names = [f for f in file_names if scan_no in f and "tif" in f]
        # files = sorted(list([os.path.join(img_path,f) for f in file_names]))
        # files = [f for f in files if scan_no in f]
        nosey.Log.debug("Reading {} ...".format(scan_name))
        s = Scan(log_file = scan_name, image_files = img_path)
        loader = QThread_Loader(s)
        self.threads.append(loader)
        loader.start()
        nosey.Log.debug("Scan {} loaded.".format(s))
        item01.setData(pg.QtCore.Qt.UserRole, s)
        item01.setText(scan_name)
        self.tableSources.resizeColumnsToContents()

        # Events
        btn_view.clicked.connect(lambda : self.display(s))
        btn_active.clicked.connect(s.toggle)
        btn_active.clicked.connect(self.updatePlot)
        btn_remove.clicked.connect(lambda : self.removeSource(item01))

        return s


    def getScans(self):
        scans = []
        for row in range(self.tableSources.rowCount()):
            item = self.tableSources.item(row, 3)
            scan = item.data(pg.QtCore.Qt.UserRole)
            if scan.active:
                scans.append(scan)
        return scans


    def removeSource(self, item):
        row = self.tableSources.row(item)
        self.tableSources.removeRow(row)
        self.updatePlot()


class QThread_Loader(QtCore.QThread):
    taskFinished = QtCore.pyqtSignal(int)
    imageLoaded = QtCore.pyqtSignal(int)

    def __init__(self, scan, *arg, **kwarg):
        self.scan = scan
        QtCore.QThread.__init__(self, *arg, **kwarg)

    def run(self):
        try:
            nosey.Log.info("Loading scan {}, please wait...".format(self.scan.name))
            #self.scan.read_logfile(recipe = SOLEILRecipe())
            self.scan.read_files(recipe = SOLEILRecipe())
            n = len(self.scan.images)
            self.taskFinished.emit(n)
        except Exception as e:
            nosey.Log.error("Loader thread crashed: {}".format(e))
