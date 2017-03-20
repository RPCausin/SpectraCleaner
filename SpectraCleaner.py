import sys
import os

from Orange.widgets.widget import OWWidget, OWComponent
from Orange.widgets.settings import DomainContextHandler, SettingProvider

from os.path import expanduser
from AnyQt.QtCore import *
from AnyQt.QtGui import *
from AnyQt.QtWidgets import *

import opusFC
import pyqtgraph as pg


class SpectraCleaning(QWidget, OWComponent):
    def __init__(self, parent=None):
        QWidget.__init__(self)
        OWComponent.__init__(self, parent)

        self.filename = ""

        layout = QVBoxLayout()
        self.fsmdl = QFileSystemModel()
        self.fsmdl.setRootPath(expanduser("~"))
        self.view = QTreeView()
        self.view.setModel(self.fsmdl)
        self.view.setRootIndex(self.fsmdl.index(expanduser("~")))
        self.view.setColumnWidth(0, 300)
        self.view.selectionModel().currentChanged.connect(self.get_selected_data)
        self.connect(self, SIGNAL("delPressed"), self.delete_file)

        self.pen = pg.mkPen(color=QColor(Qt.black), width=2)
        self.plt = pg.PlotWidget(title="Select a file", pen=self.pen, background="w", \
                                 bottom="Wavenumber (cm⁻¹)",left="Absorbance (a.u.)")
        self.plt.invertX()

        self.setLayout(layout)
        self.layout().addWidget(self.view)
        self.layout().addWidget(self.plt)

    def keyPressEvent(self, event):
        if type(event) == QKeyEvent:
            if event.key() == Qt.Key_Delete:
                self.emit(SIGNAL('delPressed'))

    def get_selected_data(self, current):
        self.filename = self.fsmdl.filePath(current)
        fn = self.filename
        self.plt.clear()
        try:
            data = opusFC.getOpusData(fn, opusFC.listContents(fn)[0])
            self.plt.setTitle("File: {}".format(fn))
            self.plt.plot(data.x, data.y, pen=self.pen)
        except IsADirectoryError:
            self.plt.setTitle("{} is a directory".format(fn))
        except:
            self.plt.setTitle("Unable to load file {}".format(fn))

    def delete_file(self):
        fn = self.filename
        ret = self.message_box()
        if ret == QMessageBox.Yes:
            try:
                os.remove(fn)
                QMessageBox.information(self, "File removed", "File \"{}\" was successfully removed.".format(fn))
            except FileNotFoundError:
                QMessageBox.critical(self, "Error", "File {} not found.".format(fn))
            except IsADirectoryError:
                QMessageBox.critical(self, "Error", "{} is a directory, not a file.".format(fn))

    def message_box(self):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("Remove file")
        msgBox.setText("Are you sure you want to remove the following file?\n\"{}\"".format(self.filename))
        msgBox.setInformativeText("Press yes to remove the file.")
        msgBox.addButton(QMessageBox.Yes)
        msgBox.addButton(QMessageBox.Cancel)
        msgBox.setDefaultButton(QMessageBox.Cancel)
        msgBox.setEscapeButton(QMessageBox.Cancel)
        msgBox.setIcon(QMessageBox.Question)
        return msgBox.exec_()


class OWSpectraCleaner(OWWidget):
    name = "Spectra Cleaner"
    description = "Visualize plot of selected file corresponding to one spectrum"
    icon = "icons/DataSamplerA.svg"

    inputs = []
    outputs = []

    settingsHandler = DomainContextHandler()
    spectracleaning = SettingProvider(SpectraCleaning)

    def __init__(self):
        super().__init__()

        self.controlArea.hide()
        self.spectracleaning = SpectraCleaning(self)
        self.mainArea.layout().addWidget(self.spectracleaning)
        self.resize(900, 800)


def main(argv=None):
    if argv is None:
        argv = sys.argv
    argv = list(argv)
    app = QApplication(argv)
    w = OWSpectraCleaner()
    w.show()

    w.handleNewSignals()

    rval = app.exec_()
    w.handleNewSignals()
    w.deleteLater()
    del w
    app.processEvents()
    return rval


if __name__ == "__main__":
    sys.exit(main())

