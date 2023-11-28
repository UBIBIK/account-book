import sqlite3
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *
from Plot2Canvas import Plot2Canvas


# 차트2 윈도우
class chart2Dialog(QDialog):
    def __init__(self, mainWindowLeft, mainWindowTop):
        super().__init__()

        # 윈도우 센터에 위치 시키기, 타이틀 지정, Modal 지정
        dialogLeft = mainWindowLeft + 50
        dialogTop = mainWindowTop + 80
        dialogWidth = 900
        dialogHeight = 550
        self.setGeometry(dialogLeft, dialogTop, dialogWidth, dialogHeight)
        self.setFixedSize(dialogWidth, dialogHeight)
        self.setWindowTitle("차트 / 분석")
        self.setModal(True)

        # 상세 UI 셋업 호출
        self.setupUI()

    def setupUI(self):

        # 년도 선택
        self.label1 = QLabel('년도 선택', self)
        self.label1.move(780, 20)
        self.label1.setFont(QFont('굴림체', 9))
        self.comboBox1 = QComboBox(self)
        self.comboBox1.setGeometry(780, 40, 105, 25)
        self.comboBox1.activated[str].connect(self.comboBox1Activated)

        # 월 선택
        self.label2 = QLabel('월 선택', self)
        self.label2.move(780, 80)
        self.label2.setFont(QFont('굴림체', 9))
        self.comboBox2 = QComboBox(self)
        self.comboBox2.setGeometry(780, 100, 105, 25)
        self.comboBox2.activated[str].connect(self.comboBox2Activated)

        # 수입/지출 선택
        self.label3 = QLabel('수입/지출 선택', self)
        self.label3.move(780, 140)
        self.label3.setFont(QFont('굴림체', 9))
        self.comboBox3 = QComboBox(self)
        self.comboBox3.setGeometry(780, 160, 105, 25)
        self.comboBox3.addItem("수입")
        self.comboBox3.addItem("지출")
        self.comboBox3.setCurrentIndex(0)
        self.comboBox3.activated[str].connect(self.comboBox3Activated)

        # 년도 조회 호출
        self.selectDistinctYears()

        # 월 조회 호출
        self.selectDistinctMonths()

        # 차트 클래스 호출
        self.chart2 = Plot2Canvas(self, width=7.5, height=5, whereStr1=self.comboBox1.currentText()[0:4],
                                  whereStr2=self.comboBox2.currentText()[0:2])
        self.chart2.move(15, 15)

    # 년도 조회
    def selectDistinctYears(self):
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
        conn = sqlite3.connect('cashbook.db')
        with conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT DISTINCT SUBSTR(BAS_DT,6,2) || '월' 
                                FROM JCASHBOOK_MAIN_DATA
                               WHERE SUBSTR(BAS_DT,1,4) = ?
                               ORDER BY SUBSTR(BAS_DT,6,2) DESC""", (self.comboBox1.currentText()[0:4],))
            self.selectDistinctMonthResults = cursor.fetchall()
            self.comboBox2.addItem('전체')
            for row in self.selectDistinctMonthResults:
                self.comboBox2.addItem(row[0])
            self.comboBox2.setCurrentIndex(0)

    # 년도 선택 시
    def comboBox1Activated(self):
        self.chart2.plot(self.comboBox1.currentText()[0:4], self.comboBox2.currentText()[0:2],
                         self.comboBox3.currentText())

    # 월 선택 시
    def comboBox2Activated(self):
        self.chart2.plot(self.comboBox1.currentText()[0:4], self.comboBox2.currentText()[0:2],
                         self.comboBox3.currentText())

    # 수입/지출 선택 시
    def comboBox3Activated(self):
        self.chart2.plot(self.comboBox1.currentText()[0:4], self.comboBox2.currentText()[0:2],
                         self.comboBox3.currentText())