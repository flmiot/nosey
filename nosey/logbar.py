import logging
import nosey
from pyqtgraph import QtGui

class StatusBarHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            stream.writeLog(msg, level = record.levelno)
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


class Logbar(QtGui.QStatusBar):
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.progressBar    = QtGui.QProgressBar()
            self.progressBar.setTextVisible(False)
            self.progressBar.setMaximumSize(75, 5)
            self.messageLabel = QtGui.QLabel("")
            self.messageLabel.setObjectName("MessageLabel")
            self.setLogColor('#f7f7f7')
            self.addPermanentWidget(self.messageLabel)
            self.addPermanentWidget(self.progressBar)



    def writeLog(self, message, level):
        if message != '\n':
            if level == logging.ERROR:
                self.setLogColor('#ff9369')
            else:
                self.setLogColor('#f7f7f7')
            self.messageLabel.setText(message)


    def writeCursorPosition(self, message):
        if message != '\n':
            self.showMessage(message)


    def flush(self, *args):
        pass


    def setProgressBarFraction(self, value):
        if value >= 1:
            fmt = 'QProgressBar::chunk {background-color:  #adf056;border-radius: 2px;}'
        else:
            fmt = 'QProgressBar::chunk {background-color:  #787878;border-radius: 2px;}'

        self.progressBar.setStyleSheet(fmt)
        self.progressBar.setValue(value * 100)



    def setLogColor(self, color):
        fmt = "padding:3px; background-color: {}; border-radius: 5px;"
        self.messageLabel.setStyleSheet(fmt.format(color))
