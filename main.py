"""
기능
- "설정" 메뉴에서 수입/지출 세부 항목을 설정할 수 있음
- "입력" 버튼을 사용하여 가계부 데이터를 입력할 수 있음
- "조회" 버튼을 사용하여 입력한 데이터를 조회할 수 있음 (다양한 조회 조건 및 정렬 기능 포함)
- 조회된 결과를 "더블클릭" 하여 데이터를 수정하거나 삭제할 수 있음
- 엑셀 불러오기 메뉴를 사용하여 엑셀 데이터를 프로그램 으로 가져올 수 있음
- 엑셀 내보내기 메뉴를 사용하여 프로그램 데이터를 엑셀 파일로 내보낼 수 있음
- 전체/년도/월 단위로 데이터를 삭제할 수 있음
"""
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
class cashbookWindow(QMainWindow):
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

        # 상세 UI 셋업 호출
        self.setupUI()

    def setupUI(self):
        # 년월 조건
        self.label1 = QLabel('조회조건 : ', self)
        self.label1.move(15, 33)
        self.label1.setFont(QFont('굴림체', 10))
        self.dateEdit1 = QDateEdit(self)
        self.dateEdit1.move(95, 35)
        self.dateEdit1.resize(75, 25)
        self.dateEdit1.setFont(QFont('굴림체', 10))
        self.dateEdit1.setDisplayFormat("yyyy-MM")  # 년월 포맷 지정
        self.dateEdit1.setDate(QDate.currentDate())  # 현재일자 출력
        self.dateEdit1.setCurrentSectionIndex(1)  # 1 : 디폴트로 월이 증가되도록 함, 0 : 년도가 증가함

        # 수입/지출 조건
        self.comboBox1 = QComboBox(self)
        self.comboBox1.setGeometry(180, 35, 80, 25)
        self.comboBox1.addItem("전체")
        self.comboBox1.addItem("수입")
        self.comboBox1.addItem("지출")
        self.comboBox1.setCurrentIndex(0)
        #self.comboBox1.activated[str].connect(self.comboBox1Activated) UBI 이벤트 추가하고 주석 풀기

        # 항목 상세 조건
        self.comboBox2 = QComboBox(self)
        self.comboBox2.setGeometry(270, 35, 100, 25)
        self.comboBox2.addItem("전체")
        self.comboBox2.setCurrentIndex(0)

        # 적요 조건
        self.lineEdit1 = QLineEdit(self)
        self.lineEdit1.setGeometry(380, 35, 90, 25)
        self.lineEdit1.setMaxLength(20)
        self.label2 = QLabel(',', self)
        self.label2.move(473, 35)
        self.label2.setFont(QFont('굴림체', 10))

        # 정렬 조건
        self.label3 = QLabel('정렬방식 : ', self)
        self.label3.move(487, 33)
        self.label3.setFont(QFont('굴림체', 10))
        self.comboBox3 = QComboBox(self)
        self.comboBox3.setGeometry(565, 35, 80, 25)
        self.comboBox3.addItem("일자")
        self.comboBox3.addItem("수입/지출")
        self.comboBox3.addItem("세부항목")
        self.comboBox3.addItem("적요")
        self.comboBox3.addItem("금액")
        self.comboBox3.setCurrentIndex(0)
        self.checkBox3 = QCheckBox("내림차순", self)
        self.checkBox3.setChecked(True)
        self.checkBox3.setGeometry(655, 35, 80, 25)
        self.checkBox3.setFont(QFont('굴림체', 10))

        # 조회 버튼
        self.pushButton1 = QPushButton("조회", self)
        self.pushButton1.move(770, 32)
        self.pushButton1.resize(100, 30)
        #self.pushButton1.clicked.connect(self.pushButton1Clicked) UBI 이벤트 추가하고 주석 풀기

        # 입력 버튼
        self.pushButton2 = QPushButton("입력", self)
        self.pushButton2.move(885, 32)
        #self.pushButton2.clicked.connect(self.pushButton2Clicked) UBI 이벤트 추가하고 주석 풀기

if __name__ == "__main__":  #현재 스크립트가 직접 실행될 때만 아래의 코드를 실행하도록
    app = QApplication(sys.argv)
    cashbookWindow = cashbookWindow()
    cashbookWindow.show()
    app.exec_()