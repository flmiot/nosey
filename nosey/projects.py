import re
from datetime import datetime
from pyqtgraph.Qt import QtCore, QtGui

import nosey
from nosey.monitor import Monitor
from nosey.sources import Sources
from nosey.plot import Plot
from nosey.groups import Groups
from nosey.settings import Settings
from nosey.references import References
from nosey.roi import ROI



class Projects(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def saveProject(self):
        try:
            file = QtGui.QFileDialog.getSaveFileName(self, 'Save project file')[0]
            self.saveProjectFile(file)
        except Exception as e:
            nosey.Log.error("Project could not be saved: {}".format(e))


    def loadProject(self, project_file = None):
        try:
            if project_file:
                file = project_file
            else:
                file = QtGui.QFileDialog.getOpenFileName(self, 'Select project')[0]

            self.clearProject()
            self.parseProjectFile(file)
        except Exception as e:
            nosey.Log.error("Project could not be openend: {}".format(e))


    def parseProjectFile(self, file):
    # test = [] #['H:/raw/alignment_00887', 'H:/raw/alignment_00888', 'H:/raw/alignment_00889', 'H:/raw/alignment_00890']

        msgBox = QtGui.QMessageBox( QtGui.QMessageBox.Information,
            "Processing...", "Preparing", QtGui.QMessageBox.NoButton)
        l = msgBox.layout()
        l.itemAtPosition( l.rowCount() - 1, 0 ).widget().hide()
        progress = QtGui.QProgressBar()
        progress.setMinimumSize(360,25)
        l.addWidget(progress,1, 1, 1, l.columnCount(), QtCore.Qt.AlignCenter )
        msgBox.show()

        with open(file, 'r') as input_file:
            data=input_file.read().replace('\n', '')

        # Divide input file into keyword blocks
        # !SCANS, !ANALYZERS, !CALIBRATIONS, !GROUPS, !REFERENCES, !SETTINGS
        pattern     = r'\!\s*([^\!]*)'
        blocks      = re.findall(pattern, data)
        kw_pattern  = r'{}[()](.*?)[()]'
        kp          = r'{}\s*=\s*\'*\"*([^=,\t\'\"]*)'
        f_pattern   = r'(\d+\.?\d*)'

        # Control keywords
        keywords = dict(
            PLOT                = [False, self.actionUpdatePlot],
            NORMALIZE           = [False, self.actionNormalize],
            SINGLE_SCANS        = [False, self.actionSingleScans],
            SINGLE_ANALYZERS    = [False, self.actionSingleAnalyzers],
            SUBTRACT_BACKGROUND = [False, self.actionSubtractBackground],
            COM_SHIFT           = [False, self.actionCOMShift],
            AUTO                = [False, self.actionUpdate_automatically]
        )

        groups_to_set = []
        for b in blocks:

            # Test plotting keywords
            for word in keywords:
                if word in b:
                    keywords[word][0] = True
                    break
            else:

                # No plotting keyword found,
                # test analysis keywords
                if 'SCANS' in b:
                    scans = re.findall(kw_pattern.format('scan'), b)
                    for ind, s in enumerate(scans):
                        msgBox.setText('Importing scans')
                        progress.setValue(101.* ind/len(scans))
                        QtGui.QApplication.processEvents()

                        path = str(re.findall(kp.format('path'),s)[0])
                        b1 = str(re.findall(kp.format('include'),s)[0])
                        include = True if b1 == '1' or b1 == 'True' else False
                        group = str(re.findall(kp.format('group'),s)[0])
                        groups_to_set.append(group)

                        scan = self._read_scan(path, log_file = None,
                            include = include)

                elif 'ANALYZERS' in b:
                    analyzers = re.findall(kw_pattern.format('analyzer'), b)
                    for ind, a in enumerate(analyzers):

                        msgBox.setText('Processing analyzers')
                        progress.setValue(101.* ind/len(analyzers))
                        QtGui.QApplication.processEvents()

                        x = float(re.findall(kp.format('position-x'),a)[0])
                        y = float(re.findall(kp.format('position-y'),a)[0])
                        h = float(re.findall(kp.format('height'),a)[0])
                        w = float(re.findall(kp.format('width'),a)[0])
                        b1 = str(re.findall(kp.format('include'),a)[0])
                        include = True if b1 == '1' or b1 == 'True' else False
                        d_1 = float(re.findall(kp.format('bg01-distance'),a)[0])
                        d_2 = float(re.findall(kp.format('bg02-distance'),a)[0])
                        h_1 = float(re.findall(kp.format('bg01-height'),a)[0])
                        h_2 = float(re.findall(kp.format('bg02-height'),a)[0])
                        ep = re.findall(kp.format('energy-points'), a)[0]
                        points = [float(f) for f in re.findall(f_pattern, ep)]
                        rows = self.tableRoi.rowCount()
                        roi = ROI([x, y], [w, h], 'ROI {}'.format(rows))
                        roi.objects[1].setSize(h_1)
                        roi.objects[2].setSize(h_2)
                        roi.b1_distance = d_1
                        roi.b2_distance = d_2
                        roi.connectUpdateSlotProxy(self.updatePlot)
                        self.addRoi(roi = roi, energy_point_positions = points)

                        # Stir the analyzer
                        roi.regionChanged(roi.objects[0])
                        roi.regionChanged(roi.objects[1])
                        roi.regionChanged(roi.objects[2])


                elif 'GROUPS' in b:
                    groups = re.findall(kw_pattern.format('group'), b)
                    for ind, g in enumerate(groups):

                        msgBox.setText('Processing groups')
                        progress.setValue(101.* ind/len(groups))
                        QtGui.QApplication.processEvents()

                        b1 = str(re.findall(kp.format('include'), g)[0])
                        i = True if b1 == '1' or b1 == 'True' else False
                        b2 = str(re.findall(kp.format('reference'), g)[0])
                        r = True if b2 == '1' or b2 == 'True' else False
                        n = str(re.findall(kp.format('name'), g)[0])

                        self.addGroup(name = n, active = i, reference = r)

                elif 'CALIBRATIONS' in b:
                    energies = re.findall(kw_pattern.format('energy'), b)
                    for e in energies:
                        pos = re.findall(kp.format('position'), e)[0]
                        self.addEnergyPoint(energy = pos, touch_roi = False)


                elif 'SETTINGS' in b:
                    settings   = re.findall(kw_pattern.format('settings'), b)[0]

                    keywordMap = Settings.getKeywordMap(self)

                    for key_ext, key_int in keywordMap.items():
                        try:
                            value = re.findall(kp.format(key_ext), settings)[0]
                            Settings.setSetting(self, key_int, value)
                        except Exception as e:
                            fmt = "Property {} not found, skipped."
                            nosey.Log.debug(fmt.format(key_ext))

                    msgBox.setText('Loading settings')
                    QtGui.QApplication.processEvents()

                elif 'REFERENCES' in b:
                    references   = re.findall(kw_pattern.format('reference'), b)

                    for ind, r in enumerate(references):
                        path = str(re.findall(kp.format('path'),r)[0])
                        b1 = str(re.findall(kp.format('r1'),r)[0])
                        r1 = True if b1 == '1' or b1 == 'True' else False
                        b1 = str(re.findall(kp.format('r2'),r)[0])
                        r2 = True if b1 == '1' or b1 == 'True' else False
                        name = str(re.findall(kp.format('name'),r)[0])

                        References.addExternalReference(self, event = None,
                            paths = [path], include = include,
                            setAsRef1 = r1, setAsRef2 = r2)

                    msgBox.setText('Loading references')
                    QtGui.QApplication.processEvents()

                else:
                    # Not a recognized keyword
                    fmt = "Warning! Unrecognized block in the input-file: {}"
                    nosey.Log.error(fmt.format(b))
                    continue

        else:
            # Finally! Fiddle it all together

            # Set groups
            for row in range(self.tableSources.rowCount()):
                comboBox    = self.tableSources.cellWidget(row, 2)
                group       = groups_to_set[row]
                for grow in range(self.tableGroups.rowCount()):
                    text = self.tableGroups.item(grow, 3).text()
                    if text == group:
                        comboBox.setCurrentIndex(grow)
                        break
                else:
                    fmt = "Unknown group '{}' is not specified in input file."
                    raise Exception(fmt.format(group))

            # Display last loaded scan
            try:
                last_item_row   = self.tableSources.rowCount() - 1
                btn_view        = self.tableSources.cellWidget(last_item_row, 3)
                btn_view.click()
            except:
                fmt = "No run was displayed because none was available."
                nosey.Log.debug(fmt)

            msgBox.setText('Processing analysis')
            progress.setValue(0)

            # Fit models
            # par = self.background_tree.invisibleRootItem().child(0).param
            # for child in par.children():
            #     child.fit_model()

            msgBox.setText('Model fitting')
            progress.setValue(50)

            # Execute plotting keywords
            for ind, value in enumerate(keywords.values()):
                msgBox.setText('Processing analysis and plotting options [{}]'.format(value[0]))
                progress.setValue(100 * ind/len(keywords.values()))
                if value[0]:
                    value[1].trigger()


    def saveProjectFile(self, filename):

        saveString  = ""
        fmt         = 'NOSEY project file (v{}), saved: {}'
        fmt         = fmt.format(nosey.__version__, datetime.now())
        l           = len(fmt)
        header      = '#'+ '-'* (l+2) + '#\n| '+fmt+' |\n#'+'-'* (l+2) + '#\n\n'

        saveString += header
        saveString += Plot.getSaveString(self)
        saveString += Groups.getSaveString(self)
        saveString += Sources.getSaveString(self)
        saveString += Monitor.getSaveString(self)
        saveString += References.getSaveString(self)
        saveString += Settings.getSaveString(self)

        with open(filename, 'w+') as file:
            file.write(saveString)

        nosey.Log.info("Project file saved.")


    def clearProject(self):
        """ Remove all scans, analyzers, groups and calibrations and reset all
        buttons.
        """

        while self.tableSources.rowCount() > 0:
            self.tableSources.removeRow(0)

        while self.tableRoi.rowCount() > 0:
            self.tableRoi.removeRow(0)

        while self.tableGroups.rowCount() > 0:
            self.tableGroups.removeRow(0)

        while self.tableEnergy.rowCount() > 0:
            self.tableEnergy.removeRow(0)

        while self.tableExternalReferences.rowCount() > 0:
            self.tableExternalReferences.removeRow(0)

        self.actionUpdatePlot.setChecked(True)
        self.actionNormalize.setChecked(False)
        self.actionSubtractBackground.setChecked(False)
        self.actionCOMShift.setChecked(False)
        self.actionSingleAnalyzers.setChecked(False)
        self.actionSingleScans.setChecked(False)
