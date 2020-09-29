#!/usr/bin/env python3
from PyQt5  import QtWidgets
from PyQt5.QtCore import QTimer
from TABs import TABs
import sys, design  

class Application(QtWidgets.QMainWindow, design.Ui_MainWindow):
  def __init__(self): 
    super().__init__()
    self.setupUi(self)
    self.setWindowTitle('Digital MCA Control & Acquisition')
    self.actionExit.triggered.connect(self.close)
    self.timerA = QTimer()
    self.timerB = QTimer()
    self.tabs   = TABs(self)


def main():
  try:
    app    = QtWidgets.QApplication(sys.argv)
    window = Application()
    window.show()
    app.exec_()
  except:
    window.tabs.__del__()
  del window.tabs
  print("Good Bye!")
  
if __name__ == '__main__':  main()  
  

