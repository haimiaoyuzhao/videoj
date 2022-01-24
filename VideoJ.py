from myui import MyUiWindow
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow


class MyApp():
    def __init__(self):
        self.window = QMainWindow()
        self.ui = MyUiWindow(self.window, sys.argv)

    def show(self):
        self.window.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myapp = MyApp()
    myapp.show()
    sys.exit(app.exec_())
