import sys
import datetime
import sqlite3
import openpyxl
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import rc
import matplotlib.font_manager as fm

# 메인 윈도우
class JcashbookWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 윈도우 센터에 위치 시키기, 타이틀 지정, Modal 지정
        # 해상도 구하기 (sg = QDesktopWidget().screenGeometry())
        ag = QDesktopWidget().availableGeometry()
        mainWindowWidth = 1000
        mainWindowHeight = 740
        mainWindowLeft = int((ag.width() - mainWindowWidth) / 2)
        mainWindowTop = int((ag.height() - mainWindowHeight) / 2)
        self.setGeometry(mainWindowLeft, mainWindowTop, mainWindowWidth, mainWindowHeight)
        self.setFixedSize(mainWindowWidth, mainWindowHeight)
        self.setWindowTitle("팀 얼랑뚱땅 - 가계부")


if __name__ == "__main__":  #현재 스크립트가 직접 실행될 때만 아래의 코드를 실행하도록
    app = QApplication(sys.argv)
    jcashbookWindow = JcashbookWindow()
    jcashbookWindow.show()
    app.exec_()