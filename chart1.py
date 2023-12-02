import sqlite3
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *
from Plot1Canvas import Plot1Canvas


# 차트1 윈도우
# 월별/수입 지출 현황 분석
class chart1Dialog(QDialog):
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

        #스타일 지정
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #B2DFDB, stop:1 #80CBC4); /* 민트색 그라데이션 */
            }

            QLabel {
                font-size: 14px;
                color: #00838F; /* 진한 하늘색 텍스트 */
            }

            QComboBox {
                background-color: #4DD0E1; /* 청량한 하늘색 배경 */
                color: white;
                border-radius: 4px;
                padding: 5px;
                min-height: 25px;
            }

            QComboBox QAbstractItemView {
                background: #B2DFDB; /* 민트색 배경 */
                selection-background-color: #80CBC4; /* 좀 더 진한 민트색 */
            }

            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 1px;
                border-left-color: #4DB6AC; /* 민트색 테두리 */
                border-left-style: solid; /* 선이 단단한 스타일 */
                border-top-right-radius: 3px; /* 위 오른쪽 모서리 둥글게 */
                border-bottom-right-radius: 3px; /* 아래 오른쪽 모서리 둥글게 */
            }
        """)

        # 상세 UI 셋업 호출
        self.setupUI()

    def setupUI(self):
        # 년도 선택
        self.label1 = QLabel('년도를 선택하세요', self)
        self.label1.move(780, 20)
        self.label1.setFont(QFont('굴림체', 9))
        self.comboBox1 = QComboBox(self)
        self.comboBox1.setGeometry(780, 40, 105, 25)
        self.comboBox1.activated[str].connect(self.comboBox1Activated)

        # 년도 조회 호출
        self.selectDistinctYears()

        # 차트 클래스 호출
        self.chart1 = Plot1Canvas(self, width=7.5, height=5, whereStr1=self.comboBox1.currentText()[0:4])
        self.chart1.move(15, 15)

    def setupUI2(self):
        # 년도 선택
        self.label1 = QLabel('년도를 선택하세요', self)
        self.label1.move(780, 20)
        self.label1.setFont(QFont('굴림체', 9))
        self.comboBox1 = QComboBox(self)
        self.comboBox1.setGeometry(780, 40, 105, 25)
        self.comboBox1.activated[str].connect(self.comboBox1Activated)

        # 월 선택
        self.label2 = QLabel('월을 선택하세요', self)
        self.label2.move(780, 80)
        self.label2.setFont(QFont('굴림체', 9))
        self.comboBox2 = QComboBox(self)
        self.comboBox2.setGeometry(780, 100, 105, 25)
        self.comboBox2.activated[str].connect(self.comboBox2Activated)

        # 년도 조회 호출
        self.selectDistinctYears()

        # 월 조회 호출
        self.selectDistinctMonths()

        # 차트 클래스 호출
        self.chart2 = Plot1Canvas(self, width=7.5, height=5, whereStr1=self.comboBox1.currentText()[0:4])
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

    # 년도 선택 시
    def comboBox1Activated(self):
        self.chart1.plot(self.comboBox1.currentText()[0:4])