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
    self.timerA = QTimer()
    self.timerB = QTimer()
    self.tabs   = TABs(self)
    self.actionExit.triggered.connect(self.close)
    self.actionAbout.triggered.connect(self.about)
   
  def closeEvent(self, event):
    if self.tabs.DPP.Connection:
      end = self.tabs.DPP.EndLibrary()
      print("Close connection: ", end)
      self.tabs.DPP.Connection = False
    event.accept()
#    else: event.ignore()

  def about(self):
    QtWidgets.QMessageBox.about(self, "About Application", "The <b>Application</b> example")

def main():
  try:
    app    = QtWidgets.QApplication(sys.argv)
    window = Application()
    window.show()
    app.exec_()
  except:
    window.closeEvent()
#    window.tabs.__del__()
  print("Good Bye!")
  
if __name__ == '__main__':  main()  
  

