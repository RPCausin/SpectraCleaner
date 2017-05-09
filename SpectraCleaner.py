from sys import argv as sys_argv
from sys import exit as sys_exit
from os import remove as os_remove
from os.path import expanduser

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QColor, QWidget, QVBoxLayout, QFileSystemModel, QTreeView, QMessageBox, QApplication, \
    QDesktopWidget

import opusFC
import pyqtgraph as pg


class SpectraCleaning(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self)

        self.filename = ""

        layout = QVBoxLayout()
        self.fsmdl = QFileSystemModel()
        self.fsmdl.setRootPath(expanduser("~"))
        self.view = QTreeView()
        self.view.setModel(self.fsmdl)
        self.view.setRootIndex(self.fsmdl.index(expanduser("~")))
        self.view.setColumnWidth(0, 300)
        self.view.hideColumn(2)  # Hide "Type" column
        self.view.hideColumn(3)  # Hide "Date" column
        self.view.selectionModel().currentChanged.connect(self.get_selected_data)

        self.pen = pg.mkPen(color=QColor(Qt.black), width=2)
        self.plt = pg.PlotWidget(title="Select a file", pen=self.pen, background='w',
                                 bottom="Wavenumber (cm⁻¹)", left="Absorbance (a.u.)")
        self.plt.invertX()

        self.setLayout(layout)
        self.layout().addWidget(self.view)
        self.layout().addWidget(self.plt)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.delete_file()

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
                os_remove(fn)
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


def main(argv=None):
    if argv is None:
        argv = sys_argv
    argv = list(argv)
    app = QApplication(argv)
    w = SpectraCleaning()

    width, height = 900, 800

    # Center the app to the desktop
    wid = QDesktopWidget()
    screen_width = wid.screen().width()
    screen_height = wid.screen().height()
    w.setGeometry((screen_width / 2.0) - (width / 2.0), (screen_height / 2.0) - (height / 2.0), width, height)

    w.show()

    rval = app.exec_()
    w.deleteLater()
    del w
    app.processEvents()
    return rval


if __name__ == "__main__":
    sys_exit(main())
