import re
from pyqtgraph.Qt import QtCore, QtGui

import nosey
from nosey.roi import ROI

class Projects(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def saveProject(self):
        file = QtGui.QFileDialog.getSaveFileName(self, 'Save project file')[0]
        print(file)

    def loadProject(self, project_file = None):
        if project_file:
            file = project_file
        else:
            file = QtGui.QFileDialog.getOpenFileName(self, 'Select project')[0]

        self.parseProjectFile(file)


    def parseProjectFile(self, file):
    # test = [] #['H:/raw/alignment_00887', 'H:/raw/alignment_00888', 'H:/raw/alignment_00889', 'H:/raw/alignment_00890']

        # msgBox = QtGui.QMessageBox( QtGui.QMessageBox.Information,
        #     "Processing...", "Preparing", QtGui.QMessageBox.NoButton )
        #
        # # Get the layout
        # l = msgBox.layout()
        #
        # # Hide the default button
        # l.itemAtPosition( l.rowCount() - 1, 0 ).widget().hide()
        #
        # progress = QtGui.QProgressBar()
        # progress.setMinimumSize(360,25)
        #
        # # Add the progress bar at the bottom (last row + 1) and first column with column span
        # l.addWidget(progress,1, 1, 1, l.columnCount(), QtCore.Qt.AlignCenter )
        #
        # msgBox.show()

        with open(file, 'r') as input_file:
            data=input_file.read().replace('\n', '')

        # Divide input file into keyword blocks
        # !SCANS, !ANALYZERS, !CALIBRATIONS, !GROUPS, !REFERENCES, !SETTINGS
        pattern = r'\!\s*([^\!]*)'
        blocks = re.findall(pattern, data)
        kw_pattern = r'{}[()](.*?)[()]'
        kp = r'{}\s*=\s*\'*\"*([^=,\t\'\"]*)'

        # Control keywords
        keywords = dict(
            PLOT                = [False, 'refresh manual'],
            NORMALIZE           = [False, 'normalize'],
            SINGLE_SCANS        = [False, 'single_scans'],
            SINGLE_ANALYZERS    = [False, 'single_analyzers'],
            SUBTRACT_BACKGROUND = [False, 'subtract_background'],
            AUTO                = [False, 'refresh toggle']
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
                    scans = re.findall(kw_pattern.format('scan'),b)
                    for ind, s in enumerate(scans):
                        print(s)

                        # msgBox.setText('Importing scans')
                        # progress.setValue(101.* ind/len(scans))
                        # QtGui.QApplication.processEvents()

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

                        # msgBox.setText('Processing analyzers')
                        # progress.setValue(101.* ind/len(analyzers))
                        # QtGui.QApplication.processEvents()

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

                        rows = self.tableRoi.rowCount()
                        roi = ROI([x, y], [w, h], 'ROI {}'.format(rows))
                        roi.objects[1].setSize(h_1)
                        roi.objects[2].setSize(h_2)
                        roi.b1_distance = d_1
                        roi.b2_distance = d_2
                        self.addRoi(roi = roi)

                        # Stir the analyzer
                        roi.regionChanged(roi.objects[0])
                        roi.regionChanged(roi.objects[1])
                        roi.regionChanged(roi.objects[2])


                elif 'GROUPS' in b:
                    groups = re.findall(kw_pattern.format('group'), b)
                    for g in groups:

                        # msgBox.setText('Processing models')
                        # progress.setValue(101.* ind/len(models))
                        # QtGui.QApplication.processEvents()

                        b1 = str(re.findall(kp.format('include'), g)[0])
                        include = True if b1 == '1' or b1 == 'True' else False
                        b2 = str(re.findall(kp.format('reference'), g)[0])
                        reference = True if b2 == '1' or b2 == 'True' else False
                        name = str(re.findall(kp.format('name'), g)[0])

                        self.addPlottingGroup(plottingGroupName = name)



                else:
                    # Not a recognized keyword
                    fmt = "Warning! Unrecognized block in the input-file: {}"
                    nosey.Log.error(fmt.format(b))
                    continue

        else:
            # Finally! Fiddle it all together

            # for row in range(self.tableSources.rowCount()):
            #     comboBox    = self.tableSources.cellWidget(row, 2)
            #     group       = groups_to_set[row]
            #     for grow in range(self.tableGroups.rowCount()):
            #         text = self.tableGroups.item(grow, 3).text()
            #         if text == group:
            #             comboBox.setCurrentIndex(grow)
            #     else:
            #         fmt = "Unknown group '{}' is not specified in input file."
            #         raise Exception(fmt.format(group))

            # msgBox.setText('Processing analysis')
            # progress.setValue(0)

            # Fit models
            # par = self.background_tree.invisibleRootItem().child(0).param
            # for child in par.children():
            #     child.fit_model()

            # msgBox.setText('Model fitting')
            # progress.setValue(50)

            # Execute plotting keywords
            for ind, value in enumerate(keywords.values()):
                # msgBox.setText('Processing analysis and plotting options [{}]'.format(value[1]))
                # progress.setValue(100 * ind/len(keywords.values()))
                if value[0]:
                    pass
                    # self.plot.buttons[value[1]].click()
