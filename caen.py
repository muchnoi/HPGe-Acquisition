#!/usr/bin/env python3
import os, sys 
from PyQt5  import QtWidgets
from PyQt5.QtCore import QTimer
from TABs import TABs
import design  # Это наш конвертированный файл дизайна

class Application(QtWidgets.QMainWindow, design.Ui_MainWindow):
  def __init__(self):  # Это здесь нужно для доступа к переменным, методам и т.д. в файле design.py
    super().__init__()
    self.setupUi(self)  # Это нужно для инициализации нашего дизайна
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
  

