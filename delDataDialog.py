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
import main
class delDataDialog(QDialog):
    def __init__(self, mainWindowLeft, mainWindowTop):
        super().__init__()

        # 윈도우 센터에 위치 시키기, 타이틀 지정, Modal 지정
        dialogLeft = mainWindowLeft + 290
        dialogTop = mainWindowTop + 120
        dialogWidth = 400
        dialogHeight = 150
        self.setGeometry(dialogLeft, dialogTop, dialogWidth, dialogHeight)
        self.setFixedSize(dialogWidth, dialogHeight)
        self.setWindowTitle("데이터 삭제하기")
        self.setModal(True)

        # 상세 UI 셋업 호출
        self.setupUI()

    def setupUI(self):

        # 그룹 박스
        self.groupBox1 = QGroupBox("범위 선택", self)
        self.groupBox1.setGeometry(20, 20, 360, 55)

        # 년도 조건
        self.label1 = QLabel('년도 : ', self)
        self.label1.move(45, 43)
        self.label1.setFont(QFont('굴림체', 10))
        self.comboBox1 = QComboBox(self)
        self.comboBox1.setGeometry(100, 40, 100, 20)
        self.comboBox1.setCurrentIndex(0)
        self.comboBox1.activated[str].connect(self.comboBox1Activated)

        # 월 조건
        self.label1 = QLabel('월 : ', self)
        self.label1.move(220, 43)
        self.label1.setFont(QFont('굴림체', 10))
        self.comboBox2 = QComboBox(self)
        self.comboBox2.setGeometry(260, 40, 100, 20)
        self.comboBox2.setCurrentIndex(0)

        # 내보내기 버튼
        self.pushButton1 = QPushButton("삭제하기", self)
        self.pushButton1.setGeometry(90, 95, 90, 30)
        self.pushButton1.clicked.connect(self.pushButton1Clicked)

        # 나가기 버튼
        self.pushButton2 = QPushButton("나가기", self)
        self.pushButton2.setGeometry(220, 95, 90, 30)
        self.pushButton2.clicked.connect(self.pushButton2Clicked)

        # 년도 조회 호출
        self.selectDistinctYears()

        # 월 조회 호출
        self.selectDistinctMonths()

    # 년도 조회
    def selectDistinctYears(self):
        self.comboBox1.addItem("전체")
        conn = sqlite3.connect('cashbook.db')
        with conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT DISTINCT SUBSTR(BAS_DT,1,4) || '년' 
                                FROM JCASHBOOK_MAIN_DATA
                               ORDER BY SUBSTR(BAS_DT,1,4) DESC""")
            self.selectDistinctYearResults = cursor.fetchall()
            for row in self.selectDistinctYearResults:
                self.comboBox1.addItem(row[0])
            self.comboBox1.setCurrentIndex(0)

    # 월 조회
    def selectDistinctMonths(self):
        self.comboBox2.addItem("전체")
        conn = sqlite3.connect('cashbook.db')
        with conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT DISTINCT SUBSTR(BAS_DT,6,2) || '월' 
                                FROM JCASHBOOK_MAIN_DATA
                               WHERE SUBSTR(BAS_DT,1,4) || '년' = ?
                               ORDER BY SUBSTR(BAS_DT,6,2) DESC""", (self.comboBox1.currentText(),))
            self.selectDistinctMonthResults = cursor.fetchall()
            for row in self.selectDistinctMonthResults:
                self.comboBox2.addItem(row[0])
            self.comboBox2.setCurrentIndex(0)

    # 수입/지출 조건 변경 시 세부 항목 리스트 초기화
    def comboBox1Activated(self):
        self.comboBox2.clear()
        self.selectDistinctMonths()

    # 삭제하기 버튼 클릭 시
    def pushButton1Clicked(self):
        messageReply = QMessageBox.question(self, '삭제 확인', "정말로 삭제하시겠습니까?",
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if messageReply == QMessageBox.Yes:
            # 데이터베이스 처리
            conn = sqlite3.connect('cashbook.db')
            with conn:
                cursor = conn.cursor()
                cursor.execute("""DELETE FROM JCASHBOOK_MAIN_DATA
                                   WHERE (SUBSTR(BAS_DT,1,4) || '년' = ? OR '전체' = ?)
                                     AND (SUBSTR(BAS_DT,6,2) || '월' = ? OR '전체' = ?)""",
                               (self.comboBox1.currentText(), self.comboBox1.currentText(),
                                self.comboBox2.currentText(), self.comboBox2.currentText()))
                conn.commit()
                QMessageBox.information(self, "Info", "데이터가 삭제되었습니다.")

    # 나가기 버튼 클릭 시
    def pushButton2Clicked(self):
        self.close()