from sys import argv as sys_argv
from sys import exit as sys_exit
from os import remove as os_remove
from os.path import expanduser

from AnyQt.QtCore import Qt, QPoint
from AnyQt.QtGui import QColor
from AnyQt.QtWidgets import QWidget, QVBoxLayout, QFileSystemModel, QTreeView, QMessageBox, QApplication, \
    QDesktopWidget, QMainWindow, qApp, QAction, QWidgetAction, QCheckBox

import opusFC
import pyqtgraph as pg


class SpectraCleaner(QWidget):
    """
    Class defining the SpectraCleaner widget, which consists of both system navigator and plot viewer.
    """
    def __init__(self, parent=None):
        # Inherits the Qt class QWidget, which has to be initialized:
        QWidget.__init__(self, parent)

        # Create class attributes to handle the message box that appears to confirm a file deletion
        # and the selected file name.
        self.msgBox = None
        self.filename = ""

        self.mylayout = QVBoxLayout()  # Create layout

        self.fsmdl = QFileSystemModel()  # Initialize a QFileSystemModel class to handle the system's files
        self.fsmdl.setRootPath(expanduser(''))  # Set the root path at the top system level

        self.view = QTreeView()  # Initialize a QTreeView class
        self.view.setModel(self.fsmdl)  # Set QTreeView model with QFileSystemModel, so that the File system is
        # visualized with a tree view
        self.view.setRootIndex(self.fsmdl.index(expanduser('~')))  # Set tree view root at "home"
        self.view.setColumnWidth(0, 300) # Set File column width
        self.view.hideColumn(2)  # Hide "Type" column
        self.view.hideColumn(3)  # Hide "Date" column

        # Call self.get_selected_data whenever the selection has changed:
        self.view.selectionModel().currentChanged.connect(self.get_selected_data)

        self.pen = pg.mkPen(color=QColor(Qt.black), width=2)  # Create a pen to plot the curves
        # Create the plot widget:
        self.plt = pg.PlotWidget(title="Select a file", pen=self.pen, background='w',
                                 bottom="Wavenumber (cm⁻¹)", left="Absorbance (a.u.)")
        self.plt.invertX()  # Invert the x-axis

        #  Set the layout and add both widgets (the plot and the tree view)
        self.setLayout(self.mylayout)
        self.layout().addWidget(self.view)
        self.layout().addWidget(self.plt)

    def keyPressEvent(self, event):
        """
        Handle key press events.
        """
        if event.key() == Qt.Key_Delete:  # Only get Delete key press events
            self.delete_file()  # Call the function to delete the selected file when Del key is pressed

    def mousePressEvent(self, event):
        """
        Handle mouse press events.
        """
        pass
        # In process of implementation
        print(event.button())
        if event.button() == Qt.RightButton:
            self.delete_file()

    def get_selected_data(self, current):
        """
        Load and plot the selected data.
        :param current: current selection
        """
        self.filename = self.fsmdl.filePath(current)  # Get filename
        fn = self.filename
        self.plt.clear()  # Clear plot
        try:
            data = opusFC.getOpusData(fn, opusFC.listContents(fn)[0])  # Load Opus data of the selected file
            self.plt.setTitle("File: {}".format(fn))  # Write filename in the plot title
            self.plt.plot(data.x, data.y, pen=self.pen)  # Plot data
        except IsADirectoryError:
            self.plt.setTitle("{} is a directory".format(fn))  # Inform that the selection is a directory
        except:
            self.plt.setTitle("Unable to load file {}".format(fn))

    def delete_file(self):
        """
        Delete selected filename.
        """
        fn = self.filename
        ret = self.message_box()  # Create a message box asking the user if he really wants to erase the file
        if ret == QMessageBox.Yes:  # If the user's answer is yes...
            try:
                os_remove(fn)  # Remove (irreversible) the file
                # Create informative message box telling the user that the file has been successfully removed
                QMessageBox.information(self.msgBox, "File removed", "File \"{}\" was successfully removed.".format(fn))
            except FileNotFoundError:
                QMessageBox.critical(self.msgBox, "Error", "File {} not found.".format(fn))
            except IsADirectoryError:
                QMessageBox.critical(self.msgBox, "Error", "{} is a directory, not a file.".format(fn))

    def message_box(self):
        """
        Create message box that asks the user if he wants to remove the file.
        :return: user's answer
        """
        self.msgBox = QMessageBox()  # Create message box
        self.msgBox.setWindowTitle("Remove file")  # Set window title
        self.msgBox.setText("Are you sure you want to remove the following file?\n\"{}\"".format(self.filename))
        self.msgBox.setInformativeText("Press yes to remove the file.")
        # Add Yes and Cancel buttons
        self.msgBox.addButton(QMessageBox.Yes)
        self.msgBox.addButton(QMessageBox.Cancel)
        self.msgBox.setDefaultButton(QMessageBox.Cancel)  # Set Cancel button as default
        self.msgBox.setEscapeButton(QMessageBox.Cancel)  # Escape button presses Cancel
        self.msgBox.setIcon(QMessageBox.Question)  # Add question icon
        return self.msgBox.exec_()


class MainWindow(QMainWindow):
    """
    Class defining the main window of the program
    """
    def __init__(self):
        QMainWindow.__init__(self)  # Inherits QMainWindow Class from Qt

        self.SpectraCleanerWidget = SpectraCleaner(self)  # Initialize SpectraCleaner
        self.setCentralWidget(self.SpectraCleanerWidget)  # Set it as central widget of the main window

        self.bar = self.menuBar()  # Create a menu bar
        self.menu = self.bar.addMenu("Options")  # Add an Options menu to the bar

        self.rootindex_checkbox = QCheckBox("Show top level", self.menu)  # Add a checkbox to Options menu
        self.rootindex_action = QWidgetAction(self.menu)  # Create a widget action in the Options menu
        self.rootindex_action.setDefaultWidget(self.rootindex_checkbox)  # Connect the action to the checkbox
        # When the checkbox state changes call the function self.top_RootIndex
        self.rootindex_checkbox.stateChanged.connect(self.top_rootindex)
        self.menu.addAction(self.rootindex_action)  # Add action to menu

        self.exit_action = QAction('Exit', self)  # Add an Exit action to the Options menu
        self.exit_action.triggered.connect(qApp.quit)  # When Exit is pressed, quit the app
        self.menu.addAction(self.exit_action)  # Add the Exit action to the Options menu

    def top_rootindex(self):
        """
        Handle the change in checkbox state.
        """
        if self.rootindex_checkbox.isChecked():
            # If the option is checked, set the tree view's root index to the top level
            self.SpectraCleanerWidget.view.setRootIndex(self.SpectraCleanerWidget.fsmdl.index(expanduser('')))
        else:
            # If the option is unchecked, set the tree view's root index to "home"
            self.SpectraCleanerWidget.view.setRootIndex(self.SpectraCleanerWidget.fsmdl.index(expanduser('~')))


def main(argv=None):
    """
    Execute the app.
    """
    if argv is None:
        argv = sys_argv
    argv = list(argv)
    app = QApplication(argv)  # Create a Qt application
    w = MainWindow()  # Initialize the main window

    width, height = 900, 800

    # Center the app to the desktop
    wid = QDesktopWidget()
    screen_width = wid.screen().width()
    screen_height = wid.screen().height()
    w.setGeometry((screen_width / 2.0) - (width / 2.0), (screen_height / 2.0) - (height / 2.0), width, height)

    w.show()  # Show the window

    rval = app.exec_()  # Execute the app
    w.deleteLater()
    del w
    app.processEvents()
    return rval


if __name__ == "__main__":  # Run the code
    sys_exit(main())
