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
import excelOutDialog

# 데이터 삭제하기
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


# 차트1 윈도우
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


# 차트1 만들기
class Plot1Canvas(FigureCanvas):

    def __init__(self, parent=None, width=6, height=5, dpi=100, whereStr1='2017'):
        fig = Figure(figsize=(width, height), dpi=dpi)
        # self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.plot(whereStr1)

    def plot(self, whereStr1):
        # 개별 폰트
        font_path = 'C:/Windows/Fonts/malgun.ttf'
        fontprop1 = fm.FontProperties(fname=font_path, size=14)
        fontprop2 = fm.FontProperties(fname=font_path, size=12)
        # 전체 폰트
        font_name = fm.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
        rc('font', family=font_name)

        # 데이터 조회
        incMon = []
        incAmt = []
        expMon = []
        expAmt = []
        conn = sqlite3.connect('cashbook.db')
        with conn:
            cursor = conn.cursor()
            # 수입 합계 구하기
            cursor.execute("""SELECT A.MONTH
                                   , CASE WHEN B.AMT IS NULL THEN 0 ELSE B.AMT END 
                                FROM JCASHBOOK_MONTH A
                                LEFT OUTER
                                JOIN (
                                      SELECT SUBSTR(BAS_DT,6,2) AS MONTH
                                           , SUM(AMT) AS AMT
                                        FROM JCASHBOOK_MAIN_DATA
                                       WHERE SUBSTR(BAS_DT,1,4) = ?
                                         AND INC_EXP_CLS = '수입'
                                       GROUP BY SUBSTR(BAS_DT,6,2)
                                     ) B
                                  ON A.MONTH = B.MONTH
                               ORDER BY A.MONTH""", (whereStr1,))
            self.selectResults = cursor.fetchall()
            for row in self.selectResults:
                incMon.append(row[0])
                incAmt.append(row[1])
            # 지출 합계 구하기
            cursor.execute("""SELECT A.MONTH
                                   , CASE WHEN B.AMT IS NULL THEN 0 ELSE B.AMT END 
                                FROM JCASHBOOK_MONTH A
                                LEFT OUTER
                                JOIN (
                                      SELECT SUBSTR(BAS_DT,6,2) AS MONTH
                                           , SUM(AMT) AS AMT
                                        FROM JCASHBOOK_MAIN_DATA
                                       WHERE SUBSTR(BAS_DT,1,4) = ?
                                         AND INC_EXP_CLS = '지출'
                                       GROUP BY SUBSTR(BAS_DT,6,2)
                                     ) B
                                  ON A.MONTH = B.MONTH
                               ORDER BY A.MONTH""", (whereStr1,))
            self.selectResults = cursor.fetchall()
            for row in self.selectResults:
                expMon.append(row[0])
                expAmt.append(row[1])
        # 인덱스 및 간격
        ind = np.arange(12)
        width = 0.35
        # ax 객체 생성 및 차트 그리기
        ax = self.figure.add_subplot(111)
        ax.cla()
        ax.bar(ind, incAmt, width=0.3, align='center', label='수입')
        ax.bar(ind + width, expAmt, width=0.3, align='center', label='지출')
        ax.set_title('월별 수입/지출 현황 분석', fontproperties=fontprop1)
        ax.set_xlabel('년월', fontproperties=fontprop2)
        ax.set_ylabel('금액', fontproperties=fontprop2)
        ax.set_xticks(ind + width / 2.)
        ax.set_xticklabels(('1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'))
        ax.legend()
        self.draw()


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


# 차트2 만들기
class Plot2Canvas(FigureCanvas):

    def __init__(self, parent=None, width=6, height=5, dpi=100, whereStr1='2017', whereStr2='전체', whereStr3='수입'):
        fig = Figure(figsize=(width, height), dpi=dpi)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.plot(whereStr1, whereStr2, whereStr3)

    def plot(self, whereStr1, whereStr2, whereStr3):
        # 개별 폰트
        font_path = 'C:/Windows/Fonts/malgun.ttf'
        fontprop1 = fm.FontProperties(fname=font_path, size=14)
        fontprop2 = fm.FontProperties(fname=font_path, size=12)
        # 전체 폰트
        font_name = fm.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
        rc('font', family=font_name)
        # 데이터 조회
        incExpDtlCls = []
        amt = []
        conn = sqlite3.connect('cashbook.db')
        with conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT CASE WHEN INC_EXP_DTL_CLS = '' THEN '선택안함' ELSE INC_EXP_DTL_CLS END
                                   , SUM(AMT) AS AMT
                                FROM JCASHBOOK_MAIN_DATA
                               WHERE SUBSTR(BAS_DT,1,4) = ?
                                 AND (SUBSTR(BAS_DT,6,2) = ? OR '전체' = ?)
                                 AND INC_EXP_CLS = ?
                               GROUP BY CASE WHEN INC_EXP_DTL_CLS = '' THEN '선택안함' ELSE INC_EXP_DTL_CLS END
                               ORDER BY 1""", (whereStr1, whereStr2, whereStr2, whereStr3))
            self.selectResults = cursor.fetchall()
            for row in self.selectResults:
                incExpDtlCls.append(row[0])
                amt.append(row[1])
        # 인덱스 및 기본 개수(5) 채우기
        def_cnt = 5
        sel_cnt = len(incExpDtlCls)
        if len(incExpDtlCls) < def_cnt:
            ind = np.arange(5)
            while sel_cnt != def_cnt:
                incExpDtlCls.append('')
                amt.append(0)
                sel_cnt = sel_cnt + 1
        else:
            ind = np.arange(len(incExpDtlCls))
        # ax 객체 생성 및 차트 그리기
        ax = self.figure.add_subplot(111)
        ax.cla()
        ax.barh(ind, amt, height=0.3, align='center')
        ax.set_yticklabels(incExpDtlCls)
        ax.invert_yaxis()
        ax.set_title('수입/지출 세부 항목별 분석', fontproperties=fontprop1)
        ax.set_xlabel('금액', fontproperties=fontprop2)
        ax.set_ylabel('세부항목', fontproperties=fontprop2)
        ax.set_yticks(ind)
        ax.set_yticklabels(incExpDtlCls)
        ax.legend()
        self.draw()


# 도움말 윈도우
class helpDialog(QDialog):
    def __init__(self, mainWindowLeft, mainWindowTop):
        super().__init__()

        # 윈도우 센터에 위치 시키기, 타이틀 지정, Modal 지정
        dialogLeft = mainWindowLeft + 130
        dialogTop = mainWindowTop + 60
        dialogWidth = 740
        dialogHeight = 590
        self.setGeometry(dialogLeft, dialogTop, dialogWidth, dialogHeight)
        self.setFixedSize(dialogWidth, dialogHeight)
        self.setWindowTitle("도움말")
        self.setModal(True)

        # 상세 UI 셋업 호출
        self.setupUI()

    def setupUI(self):
        # cashbook 설명
        self.label1 = QLabel("""        
▣ 설명
   - 수입과 지출 내역을 입력/조회/수정/삭제할 수 있는 금전출납부 또는 가계부 프로그램 입니다.
   - '일자/수입지출구분/세부항목/적요/금액' 5개 항목만을 관리합니다.

▣ 기본 기능
   1. '설정'
      - '남편급여/아내급여/기타수입', '교통비/의료비/통신비' 등의 수입/지출 세부 항목을 설정합니다.
      - 세부 항목을 설정하고 가계부 데이터를 입력하면 차트 메뉴를 통해 세부 항목별 데이터 분석이 가능합니다.
      - 세부 항목을 설정하지 않고 사용할 수도 있습니다.
   2. '입력'
      - 화면 오른쪽의 '입력' 버튼을 사용하여 가계부 데이터를 입력합니다.
      - 데이터 입력 후 '입력' 버튼 클릭 시 바로 데이터가 저장됩니다.
      - 잘 못 입력한 값이 저장되었다면 수정/삭제 기능을 이용하세요.
   3. '조회' 
      - 화면 오른쪽의 '조회' 버튼을 사용하여 입력한 데이터를 조회할 수 있습니다.
      - 데이터 건별 조회는 '월' 단위로만 가능합니다. 더 많은 데이터가 필요하면 '엑셀 내보내기' 기능을 이용하세요.
      - '수입/지출, 세부항목, 적요' 등의 다양한 조건 및 정렬 기능으로 원하는 데이터를 조회할 수 있습니다. 
   4. '수정/삭제'
      - 조회된 결과를 "더블클릭" 하여 건별 데이터를 수정하거나 삭제할 수 있습니다.
      - 많은 데이터를 삭제할 때는 '데이터 삭제하기' 기능을 이용하세요.

▣ 부가 기능 (파일 메뉴)
   1. 엑셀 불러오기
      - 엑셀 데이터를 cashbook 으로 가져올 수 있습니다.
      - 엑셀 내보내기 시 만들어지는 양식을 사용하세요.
   2. 엑셀 내보내기
      - cashbook 데이터를 엑셀 파일로 내보낼 수 있습니다.
      - 가계부 실행파일이 존재하는 위치에 'cashbook_Data.xlsx' 파일이 만들어집니다.
   3. 데이터 삭제하기
      - 전체/년도/월 단위로 데이터를 삭제할 수 있습니다.

▣ 차트 기능 (차트 메뉴)
   1. 월별 수입/지출 현황 분석
      - 1년 동안의 월별 수입과 지출 현황을 분석할 수 있습니다.
   2. 수입/지출 세부 항목별 분석
      - 수입과 지출의 세부 항목별 현황을 분석할 수 있습니다.

        """, self)
        self.label1.move(10, 0)
        self.label1.setFont(QFont('굴림체', 9))

# 수입/지출 세부항목 설정
class setDialog(QDialog):
    def __init__(self, mainWindowLeft, mainWindowTop):
        super().__init__()

        # 윈도우 센터에 위치 시키기, 타이틀 지정, Modal 지정
        dialogLeft = mainWindowLeft + 275
        dialogTop = mainWindowTop + 120
        dialogWidth = 450
        dialogHeight = 330
        self.setGeometry(dialogLeft, dialogTop, dialogWidth, dialogHeight)
        self.setFixedSize(dialogWidth, dialogHeight)
        self.setWindowTitle("수입/지출 세부 항목 설정")
        self.setModal(True)

        # 상세 UI 셋업 호출
        self.setupUI()

    def setupUI(self):

        # 수입/지출 구분
        self.label1 = QLabel('수입/지출 : ', self)
        self.label1.move(40, 35)
        self.label1.setFont(QFont('굴림체', 10))
        self.comboBox1 = QComboBox(self)
        self.comboBox1.setGeometry(130, 30, 150, 25)
        self.comboBox1.addItem("수입")
        self.comboBox1.addItem("지출")
        self.comboBox1.setCurrentIndex(0)
        self.comboBox1.activated[str].connect(self.comboBox1Activated)
        # self.comboBox1.setEnabled(False)

        # 세부 항목 리스트
        self.label2 = QLabel('세부 항목 : ', self)
        self.label2.move(40, 85)
        self.label2.setFont(QFont('굴림체', 10))
        self.listWidget2 = QListWidget(self)
        self.listWidget2.setGeometry(130, 80, 150, 115)
        self.pushButton2 = QPushButton("수정", self)
        self.pushButton2.setGeometry(300, 80, 100, 25)
        self.pushButton2.clicked.connect(self.pushButton2Clicked)
        self.pushButton3 = QPushButton("삭제", self)
        self.pushButton3.setGeometry(300, 120, 100, 25)
        self.pushButton3.clicked.connect(self.pushButton3Clicked)

        # 세부 항목 추가
        self.label4 = QLabel('항목 추가 : ', self)
        self.label4.move(40, 225)
        self.label4.setFont(QFont('굴림체', 10))
        self.lineEdit4 = QLineEdit(self)
        self.lineEdit4.setGeometry(130, 220, 150, 25)
        self.lineEdit4.setMaxLength(20)
        self.pushButton4 = QPushButton("입력", self)
        self.pushButton4.setGeometry(300, 220, 100, 25)
        self.pushButton4.clicked.connect(self.pushButton4Clicked)

        # 나가기 버튼
        self.pushButton5 = QPushButton("나가기", self)
        self.pushButton5.setGeometry(160, 270, 100, 25)
        self.pushButton5.clicked.connect(self.pushButton5Clicked)

        # 세부 항목 설정 정보 조회
        self.selectIncExpDtlSetInfo()

        # 디폴트 위치 지정
        self.pushButton4.setFocus()
        self.lineEdit4.setFocus()

    # 세부 항목 설정 정보 조회
    def selectIncExpDtlSetInfo(self):
        self.listWidget2.clear()
        conn = sqlite3.connect('cashbook.db')
        with conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT * 
                                FROM JCASHBOOK_INC_EXP_DTL 
                               WHERE INC_EXP_CLS = ? 
                               ORDER BY INC_EXP_DTL_CLS""", (str(self.comboBox1.currentIndex() + 1)))
            self.selectIncExpDtlResults = cursor.fetchall()
            for row in self.selectIncExpDtlResults:
                self.listWidget2.addItem(row[2])
            self.listWidget2.setCurrentRow(0)

    # 수입/지출 값 변경 시 세부 항목 리스트 새로 고침
    def comboBox1Activated(self):
        self.selectIncExpDtlSetInfo()

    # 수정 버튼 클릭 시
    def pushButton2Clicked(self):
        # 수정할 항목이 없을 때
        currRow = self.listWidget2.currentRow()
        if currRow == -1:
            QMessageBox.information(self, "Info", "수정할 항목이 없습니다.")
            return
        # 기 존재하는 항목인지 확인
        text, ok = QInputDialog.getText(self, '수정할 항목명', '수정할 항목명을 입력하세요.')
        for row in self.selectIncExpDtlResults:
            if row[2] == text:
                QMessageBox.information(self, "Info", "이미 등록된 세부항목이 존재합니다.")
                return
        # 데이터베이스 처리
        rowId = self.selectIncExpDtlResults[currRow][0]
        if ok:
            conn = sqlite3.connect('cashbook.db')
            with conn:
                cursor = conn.cursor()
                cursor.execute("""UPDATE JCASHBOOK_INC_EXP_DTL 
                                     SET INC_EXP_DTL_CLS = ? 
                                   WHERE ROW_ID = ?""", (text, rowId))
                conn.commit()
                QMessageBox.information(self, "Info", "데이터가 수정되었습니다.")
        # 새로 고침
        self.selectIncExpDtlSetInfo()
        self.listWidget2.setCurrentRow(currRow)

    # 삭제 버튼 클릭 시
    def pushButton3Clicked(self):
        # 삭제할 항목이 없을 때
        currRow = self.listWidget2.currentRow()
        if currRow == -1:
            QMessageBox.information(self, "Info", "삭제할 항목이 없습니다.")
            return
        rowId = self.selectIncExpDtlResults[currRow][0]
        # 삭제 확인 받기
        messageReply = QMessageBox.question(self, '삭제 확인', "정말로 삭제하시겠습니까?",
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        # 삭제 처리
        if messageReply == QMessageBox.Yes:
            conn = sqlite3.connect('cashbook.db')
            with conn:
                cursor = conn.cursor()
                cursor.execute("""DELETE FROM JCASHBOOK_INC_EXP_DTL 
                                    WHERE ROW_ID = ?""", (rowId,))    # 튜플 형태로 인자를 넘겨주어야 함
                conn.commit()
                QMessageBox.information(self, "Info", "데이터가 삭제되었습니다.")
        else:
            return
        # 새로 고침
        self.selectIncExpDtlSetInfo()
        self.listWidget2.setCurrentRow(currRow)

    # 입력 버튼 클릭 시
    def pushButton4Clicked(self):
        # 항목명 입력 체크
        if self.lineEdit4.text() == "":
            QMessageBox.information(self, "Info", "항목명을 입력하세요.")
            self.lineEdit4.setFocus()
            return
        # 기 존재하는 항목인지 확인
        for row in self.selectIncExpDtlResults:
            if row[2] == self.lineEdit4.text():
                QMessageBox.information(self, "Info", "이미 등록된 세부항목이 존재합니다.")
                return
        # 데이터베이스 입력
        conn = sqlite3.connect('cashbook.db')
        with conn:
            cursor = conn.cursor()
            sql = "INSERT INTO JCASHBOOK_INC_EXP_DTL (INC_EXP_CLS, INC_EXP_DTL_CLS) VALUES (?, ?)"
            cursor.execute(sql, (str(self.comboBox1.currentIndex() + 1), self.lineEdit4.text()))
            conn.commit()
            QMessageBox.information(self, "Info", "데이터가 저장되었습니다.")
        # 새로 고침
        self.selectIncExpDtlSetInfo()
        self.lineEdit4.setText("")
        self.lineEdit4.setFocus()

    # 나가기
    def pushButton5Clicked(self):
        self.close()


# 가계부 데이터 입력
class InsertDialog(QDialog):
    def __init__(self, mainWindowLeft, mainWindowTop, dmlCls, tableWidget1RowData):
        super().__init__()

        # 윈도우 센터에 위치 시키기, 타이틀 지정, Modal 지정
        dialogLeft = mainWindowLeft + 200
        dialogTop = mainWindowTop + 120
        dialogWidth = 600
        dialogHeight = 450
        self.setGeometry(dialogLeft, dialogTop, dialogWidth, dialogHeight)
        self.setFixedSize(dialogWidth, dialogHeight)
        self.setWindowTitle("cashbook 데이터 입력")
        self.setModal(True)

        # 변수 지정
        self.dmlCls = dmlCls
        self.tableWidget1RowData = tableWidget1RowData

        # 상세 UI 셋업 호출
        self.setupUI()

    def setupUI(self):

        # 일자 입력
        self.label1 = QLabel('일     자 : ', self)
        self.label1.move(40, 35)
        self.label1.setFont(QFont('굴림체', 10))
        self.dateEdit1 = QDateEdit(self)
        self.dateEdit1.setGeometry(130, 30, 150, 25)     # setGeometry --> move + resize
        self.dateEdit1.setDisplayFormat("yyyy-MM-dd")    # 년월일 포맷 지정
        self.dateEdit1.setDate(QDate.currentDate())      # 현재일자 출력
        self.dateEdit1.setCurrentSectionIndex(2)         # 2 : 디폴트로 "일"이 증가되도록 함, 1 : 월 증가, 0 : 년도 증가
        # self.dateEdit1.setCurrentSection(QDateTimeEdit.DaySection)

        # 수입/지출 구분 입력
        self.label2 = QLabel('수입/지출 : ', self)
        self.label2.move(40, 85)
        self.label2.setFont(QFont('굴림체', 10))
        self.comboBox2 = QComboBox(self)
        self.comboBox2.setGeometry(130, 80, 150, 25)
        self.comboBox2.addItem("수입")
        self.comboBox2.addItem("지출")
        self.comboBox2.setCurrentIndex(1)
        self.comboBox2.activated[str].connect(self.comboBox2Activated)

        # 항목 상세 입력
        self.label3 = QLabel('지출 상세 : ', self)
        self.label3.move(40, 135)
        self.label3.setFont(QFont('굴림체', 10))
        self.listWidget3 = QListWidget(self)
        self.listWidget3.setGeometry(130, 130, 150, 115)
        self.listWidget3.addItem("선택안함")
        self.label3_1 = QLabel('(설정 메뉴)', self)
        self.label3_1.move(35, 155)
        self.label3_1.setFont(QFont('굴림체', 10))

        # 적요 입력
        self.label4 = QLabel('적     요 : ', self)
        self.label4.move(40, 275)
        self.label4.setFont(QFont('굴림체', 10))
        self.lineEdit4 = QLineEdit(self)
        self.lineEdit4.setGeometry(130, 270, 430, 25)
        self.lineEdit4.setMaxLength(60)
        self.lineEdit4.returnPressed.connect(self.lineEdit4ReturnPressed)

        # 금액 입력
        self.label5 = QLabel('금     액 : ', self)
        self.label5.move(40, 325)
        self.label5.setFont(QFont('굴림체', 10))
        self.lineEdit5 = QLineEdit(self)
        self.lineEdit5.setGeometry(130, 320, 150, 25)
        self.lineEdit5.setMaxLength(15)
        self.validator = QDoubleValidator()            # 숫자만 입력 가능한 validator 생성
        self.lineEdit5. setValidator(self.validator)    # validator를 lineEdit5에 적용

        # 수정/삭제/입력 버튼
        if self.dmlCls == '1':
            # 수정 버튼
            self.pushButton4 = QPushButton("수정", self)
            self.pushButton4.setGeometry(150, 375, 80, 30)
            self.pushButton4.clicked.connect(self.pushButton4Clicked)
            # 삭제 버튼
            self.pushButton4 = QPushButton("삭제", self)
            self.pushButton4.setGeometry(260, 375, 80, 30)
            self.pushButton4.clicked.connect(self.pushButton5Clicked)
            # 나가기 버튼
            self.pushButton7 = QPushButton("나가기", self)
            self.pushButton7.setGeometry(370, 375, 80, 30)
            self.pushButton7.clicked.connect(self.pushButton7Clicked)
        else:
            # 입력 버튼
            self.pushButton6 = QPushButton("입력", self)
            self.pushButton6.setGeometry(200, 375, 80, 30)
            self.pushButton6.clicked.connect(self.pushButton6Clicked)
            # 나가기 버튼
            self.pushButton7 = QPushButton("나가기", self)
            self.pushButton7.setGeometry(330, 375, 80, 30)
            self.pushButton7.clicked.connect(self.pushButton7Clicked)

        # 수입/지출 세부 항목 조회
        self.selectIncExpDtlSetInfo()

        # 수정/삭제 호출일 때
        if self.dmlCls == '1':
            self.appryTableWidget1RowData()

        # 디폴트 위치 지정
        self.lineEdit4.setFocus()

    # QDialog 슈퍼클래스의 closeEvent 오버라이딩
    def closeEvent(self, evnt):
        cashbookWindow.selectMainData()
        return QDialog.closeEvent(self, evnt)

    # 수입/지출 세부 항목 조회
    def selectIncExpDtlSetInfo(self):
        self.listWidget3.clear()
        self.listWidget3.addItem("선택안함")
        conn = sqlite3.connect('cashbook.db')
        with conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT * 
                                FROM JCASHBOOK_INC_EXP_DTL
                               WHERE INC_EXP_CLS = ? 
                               ORDER BY INC_EXP_DTL_CLS""", (str(self.comboBox2.currentIndex() + 1),))
            self.selectIncExpDtlResults = cursor.fetchall()
            for row in self.selectIncExpDtlResults:
                self.listWidget3.addItem(row[2])
            self.listWidget3.setCurrentRow(0)

    # 메인 화면에서 전달받은 데이터를 입력 화면에 적용
    def appryTableWidget1RowData(self):
        # 일자
        self.dateEdit1.setDate(datetime.datetime.strptime(self.tableWidget1RowData[0],'%Y-%m-%d'))
        # 수입/지출
        if self.tableWidget1RowData[1] == '수입':
            self.comboBox2.setCurrentIndex(0)
        else:
            self.comboBox2.setCurrentIndex(1)
        # 세부 항목
        self.selectIncExpDtlSetInfo()
        self.listWidget3.setCurrentRow(0)
        i = 0
        for row in self.selectIncExpDtlResults:
            i = i + 1
            if row[2] == self.tableWidget1RowData[2]:
                self.listWidget3.setCurrentRow(i)
                break
        # 적요
        self.lineEdit4.setText(self.tableWidget1RowData[3])
        # 금액
        self.lineEdit5.setText(self.tableWidget1RowData[4].replace(',',''))

    # 입력 항목 오류 점검
    def validateInputItem(self):
        # 세부 항목
        if self.listWidget3.currentItem().text() == "선택안함":
            self.listWidget3Text = ""
        else:
            self.listWidget3Text = self.listWidget3.currentItem().text()
        # 금액 입력값 없을 때
        if self.lineEdit5.text() == "":
            QMessageBox.information(self, "Info", "금액은 필수 입력 항목입니다.")
            self.lineEdit5.setFocus()
            return -1
        # 금액 음수/소수점 체크
        amt = self.lineEdit5.text()
        try:
            amt2 = int(amt)
        except Exception:
            QMessageBox.information(self, "Info", '0 또는 자연수만 입력할 수 있습니다.')
            return -1
        if amt2 < 0:
            QMessageBox.information(self, "Info", '0 또는 자연수만 입력할 수 있습니다.')
            return -1
        return 0

    # 수입/지출 구분값이 바뀌었을 때 레이블 변경 및 세부 항목 초기화
    def comboBox2Activated(self):
        if self.comboBox2.currentIndex() == 0:
            self.label3.setText("수입 상세 : ")
        else:
            self.label3.setText("지출 상세 : ")
        self.listWidget3.clear()
        self.listWidget3.addItem("선택안함")
        self.selectIncExpDtlSetInfo()

    # 적요에서 엔터키 입력 시
    def lineEdit4ReturnPressed(self):
        self.lineEdit5.setFocus()

    # 수정 버튼 클릭 시
    def pushButton4Clicked(self):
        # 입력 항목 오류 체크
        validateReturn = self.validateInputItem()
        if validateReturn == -1:
            return
        # 데이터베이스 처리
        conn = sqlite3.connect('cashbook.db')
        with conn:
            cursor = conn.cursor()
            cursor.execute("""UPDATE JCASHBOOK_MAIN_DATA
                                 SET BAS_DT = ?
                                   , INC_EXP_CLS = ?
                                   , INC_EXP_DTL_CLS = ?
                                   , NOTE = ?
                                   , AMT = ?
                               WHERE ROW_ID = ?""",
                           (self.dateEdit1.date().toString('yyyy-MM-dd'), self.comboBox2.currentText(), self.listWidget3Text,
                            self.lineEdit4.text(), int(self.lineEdit5.text()), self.tableWidget1RowData[5]))
            conn.commit()
            QMessageBox.information(self, "Info", "데이터가 수정되었습니다. 다시 조회합니다.")
        self.close()

    # 삭제 버튼 클릭 시
    def pushButton5Clicked(self):
        messageReply = QMessageBox.question(self, '삭제 확인', "정말로 삭제하시겠습니까?",
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if messageReply == QMessageBox.Yes:
            # 데이터베이스 처리
            conn = sqlite3.connect('cashbook.db')
            with conn:
                cursor = conn.cursor()
                cursor.execute("""DELETE FROM JCASHBOOK_MAIN_DATA
                                   WHERE ROW_ID = ?""", (self.tableWidget1RowData[5],))
                conn.commit()
                QMessageBox.information(self, "Info", "데이터가 삭제되었습니다.")
            self.close()

    # 입력 버튼 클릭 시
    def pushButton6Clicked(self):
        # 입력 항목 오류 체크
        validateReturn = self.validateInputItem()
        if validateReturn == -1:
            return
        # 데이터베이스 저장
        conn = sqlite3.connect('cashbook.db')
        with conn:
            cursor = conn.cursor()
            sql = "INSERT INTO JCASHBOOK_MAIN_DATA (BAS_DT, INC_EXP_CLS, INC_EXP_DTL_CLS, NOTE, AMT) VALUES (?, ?, ?, ?, ?)"
            cursor.execute(sql, (self.dateEdit1.date().toString('yyyy-MM-dd'), self.comboBox2.currentText(),
                                 self.listWidget3Text, self.lineEdit4.text(), int(self.lineEdit5.text())))
            conn.commit()
            QMessageBox.information(self, "Info", "데이터가 저장되었습니다.")
        # 항목 초기화
        self.lineEdit4.setText("")
        self.lineEdit5.setText("")
        self.lineEdit4.setFocus()

    # 나가기 버튼 클릭 시
    def pushButton7Clicked(self):
        self.close()
        cashbookWindow.selectMainData()

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
        self.comboBox1.activated[str].connect(self.comboBox1Activated)

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
        self.pushButton1.clicked.connect(self.pushButton1Clicked)

        # 입력 버튼
        self.pushButton2 = QPushButton("입력", self)
        self.pushButton2.move(885, 32)
        self.pushButton2.clicked.connect(self.pushButton2Clicked)

        # 수입 합계
        self.label4 = QLabel('수입합계 : ', self)
        self.label4.move(15, 68)
        self.label4.setFont(QFont('굴림체', 10))
        self.lineEdit4 = QLineEdit(self)
        self.lineEdit4.setGeometry(95, 70, 120, 25)
        self.lineEdit4.setMaxLength(20)
        self.lineEdit4.setEnabled(False)
        self.lineEdit4.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        # 지출 합계
        self.label5 = QLabel('지출합계 : ', self)
        self.label5.move(230, 68)
        self.label5.setFont(QFont('굴림체', 10))
        self.lineEdit5 = QLineEdit(self)
        self.lineEdit5.setGeometry(310, 70, 120, 25)
        self.lineEdit5.setMaxLength(20)
        self.lineEdit5.setEnabled(False)
        self.lineEdit5.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        # 잔액
        self.label6 = QLabel('잔액 : ', self)
        self.label6.move(450, 68)
        self.label6.setFont(QFont('굴림체', 10))
        self.lineEdit6 = QLineEdit(self)
        self.lineEdit6.setGeometry(500, 70, 120, 25)
        self.lineEdit6.setMaxLength(20)
        self.lineEdit6.setEnabled(False)
        self.lineEdit6.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        # 테이블 구성
        self.tableWidget1 = QTableWidget(self)
        self.tableWidget1.setGeometry(15, 110, 970, 605)
        # self.tableWidget1.setGridStyle(Qt.SolidLine)
        self.tableWidget1.setRowCount(1)
        self.tableWidget1.setColumnCount(6)
        self.tableWidget1.setColumnWidth(0, 110)
        self.tableWidget1.setColumnWidth(1, 100)
        self.tableWidget1.setColumnWidth(2, 140)
        self.tableWidget1.setColumnWidth(3, 440)
        self.tableWidget1.setColumnWidth(4, 120)
        self.tableWidget1.setColumnWidth(5, 20)
        self.tableWidget1.setColumnHidden(5, True)  # ROW_ID 컬럼은 화면에 보이지 않도록 함
        self.tableWidget1.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 테이블에서 직접 데이터를 수정하지 못하도록 함
        self.tableWidget1.cellDoubleClicked.connect(self.tableWidget1DoubleClicked)

        # 메뉴바 생성
        menuBar = self.menuBar()
        menuBar.setFont(QFont('돋움', 11))

        # 최상위 '파일' 메뉴
        fileMenu = menuBar.addMenu('파일')
        fileMenu.setFont(QFont('돋움', 11))
        # '파일' --> '엑셀 불러오기'
        excelInAct = QAction('엑셀 불러오기', self)
        fileMenu.addAction(excelInAct)
        excelInAct.triggered.connect(self.excelInActTriggered)
        # '파일' --> '엑셀 내보내기'
        excelOutAct = QAction('엑셀 내보내기', self)
        fileMenu.addAction(excelOutAct)
        excelOutAct.triggered.connect(self.excelOutActTriggered)
        # '파일' --> '데이터 삭제하기'
        deleteDataAct = QAction('데이터 삭제하기', self)
        fileMenu.addAction(deleteDataAct)
        deleteDataAct.triggered.connect(self.deleteDataActActTriggered)
        # '파일' --> '종료'
        fileExitAct = QAction('종료', self)
        fileExitAct.setShortcut('Ctrl+Q')
        fileExitAct.setStatusTip("가계부를 종료합니다")
        fileMenu.addAction(fileExitAct)
        fileExitAct.triggered.connect(QCoreApplication.instance().quit)

        # 최상위 '차트' 메뉴
        chartMenu = menuBar.addMenu('차트')
        chartMenu.setFont(QFont('돋움', 11))
        # '차트' --> '월별 수입/지출 현황 분석'
        chart1Act = QAction('월별 수입/지출 현황 분석', self)
        chartMenu.addAction(chart1Act)
        chart1Act.triggered.connect(self.chart1ActTriggered)
        # '차트' --> '수입/지출 세부 항목별 분석'
        chart2Act = QAction('수입/지출 세부 항목별 분석', self)
        chartMenu.addAction(chart2Act)
        chart2Act.triggered.connect(self.chart2ActTriggered)

        # 최상위 '설정' 메뉴
        setMenu = menuBar.addMenu('설정')
        setMenu.setFont(QFont('돋움', 11))
        # '설정' --> '수입/지출 세부 항목 설정'
        setIncExpDtlAct = QAction('수입/지출 세부 항목 설정', self)
        setMenu.addAction(setIncExpDtlAct)
        setIncExpDtlAct.triggered.connect(self.setIncExpDtlActTriggered)

        # 최상위 '도움말' 메뉴
        # helpMenu = menuBar.addMenu('도움말')
        # helpMenu.setFont(QFont('돋움', 11))
        helpAct = QAction('도움말', self)
        menuBar.addAction(helpAct)
        helpAct.triggered.connect(self.helpActTriggered)

        # 상태표시줄
        statusBar = self.statusBar()
        statusBar.setFont(QFont('돋움', 11))
        statusBar.showMessage("cashbook 가계부 프로그램입니다.")
        self.statusBar().showMessage("cashbook 가계부 프로그램입니다.")

        # 가계부 데이터 조회
        self.selectMainData()

        # 디폴트 커서 위치 지정
        self.pushButton1.setFocus()

        # 가계부 MAIN DATA 조회
    def selectMainData(self):
        # tableWidget1 상단 레이블
        self.tableWidget1.setHorizontalHeaderLabels(('일자', '수입/지출', '세부항목', '적요', '금액', 'ROWID'))
        # ORDER BY 구문 생성
        orderBy = self.comboBox3.currentText()
        if self.checkBox3.isChecked() == True:
            desc = " DESC "
        else:
            desc = " "
        if orderBy == "일자":
            orderBy = " ORDER BY BAS_DT" + desc + ", INC_EXP_CLS, INC_EXP_DTL_CLS, NOTE, AMT"
        elif orderBy == "수입/지출":
            orderBy = " ORDER BY INC_EXP_CLS" + desc + ", BAS_DT, INC_EXP_DTL_CLS, NOTE, AMT"
        elif orderBy == "세부항목":
            orderBy = " ORDER BY INC_EXP_DTL_CLS" + desc + ", BAS_DT, INC_EXP_CLS, NOTE, AMT"
        elif orderBy == "적요":
            orderBy = " ORDER BY NOTE" + desc + ", INC_EXP_DTL_CLS, BAS_DT, INC_EXP_CLS, AMT"
        elif orderBy == "금액":
            orderBy = " ORDER BY AMT" + desc + ", INC_EXP_DTL_CLS, BAS_DT, INC_EXP_CLS, NOTE"
        # 가계부 메인 데이터 조회
        try:
            # 최초로 가계부 메인 데이터 조회 시에는 테이블이 존재하지 않으므로 except절로 분기해서 테이블을 생성함
            conn = sqlite3.connect('cashbook.db')
            cursor = conn.cursor()
            # 합계 구하기
            cursor.execute("""SELECT SUM(CASE WHEN INC_EXP_CLS = '수입' THEN AMT ELSE 0 END) AS INC_SUM
                                           , SUM(CASE WHEN INC_EXP_CLS = '지출' THEN AMT ELSE 0 END) AS EXP_SUM
                                           , SUM(CASE WHEN INC_EXP_CLS = '수입' THEN AMT ELSE 0 END)
                                           - SUM(CASE WHEN INC_EXP_CLS = '지출' THEN AMT ELSE 0 END) AS BAL_SUM
                                        FROM JCASHBOOK_MAIN_DATA
                                       WHERE BAS_DT LIKE ?
                                         AND (INC_EXP_CLS = ? OR '전체' = ?)
                                         AND (INC_EXP_DTL_CLS = ? OR '전체' = ?)
                                         AND (NOTE LIKE ? OR '' = ?)""" + orderBy,
                           (self.dateEdit1.date().toString('yyyy-MM') + '%',
                            self.comboBox1.currentText(), self.comboBox1.currentText(),
                            self.comboBox2.currentText(), self.comboBox2.currentText(),
                            '%' + self.lineEdit1.text() + '%', self.lineEdit1.text()))
            selectSumAmtResults = cursor.fetchone()
            # 결과 row가 1건도 없을 때 오류 발생하므로 "if"문 처리해 주어야 함
            if selectSumAmtResults[0] == None:
                self.lineEdit4.setText('0')
                self.lineEdit5.setText('0')
                self.lineEdit6.setText('0')
            else:
                self.lineEdit4.setText(str(format(selectSumAmtResults[0], ',')))
                self.lineEdit5.setText(str(format(selectSumAmtResults[1], ',')))
                self.lineEdit6.setText(str(format(selectSumAmtResults[2], ',')))
            # 가계부 메인 데이터 가져오기
            # (쿼리 주의) ROW_ID 컬럼이 마지막에 위치함, ROW_ID 컬럼은 화면에 안 보이고 수정/삭제 시에만 사용됨
            cursor.execute("""SELECT BAS_DT, INC_EXP_CLS, INC_EXP_DTL_CLS, NOTE, AMT, ROW_ID
                                        FROM JCASHBOOK_MAIN_DATA 
                                       WHERE BAS_DT LIKE ? 
                                         AND (INC_EXP_CLS = ? OR '전체' = ?)
                                         AND (INC_EXP_DTL_CLS = ? OR '전체' = ?)
                                         AND (NOTE LIKE ? OR '' = ?)""" + orderBy,
                           (self.dateEdit1.date().toString('yyyy-MM') + '%',
                            self.comboBox1.currentText(), self.comboBox1.currentText(),
                            self.comboBox2.currentText(), self.comboBox2.currentText(),
                            '%' + self.lineEdit1.text() + '%', self.lineEdit1.text()))
            self.selectMainDataResults = cursor.fetchall()
            # 데이터베이스 테이블에서 조회한 데이터를 tableWidget1 위젯에 디스플레이
            self.tableWidget1.setRowCount(len(self.selectMainDataResults))
            i = 0
            for row in self.selectMainDataResults:
                j = 0
                for col in row:
                    # 금액 콤마(,) 처리
                    if j in (0, 1, 2, 3, 5):
                        col2 = col
                    else:
                        col2 = format(col, ',')
                    # 테이블위젯아이템 생성
                    item = QTableWidgetItem(str(col2))
                    # 테이블위젯아이템 정렬
                    if j in (0, 1):
                        item.setTextAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
                    elif j in (2, 3):
                        item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                    else:
                        item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
                    self.tableWidget1.setItem(i, j, item)
                    j = j + 1
                i = i + 1
        except:
            # 테이블 및 시퀀스 생성, ROW_ID 컬럼은 AUTOINCREMENT
            cursor.execute("""CREATE TABLE JCASHBOOK_INC_EXP_DTL (
                                             ROW_ID INTEGER PRIMARY KEY AUTOINCREMENT
                                           , INC_EXP_CLS TEXT
                                           , INC_EXP_DTL_CLS TEXT)""")
            cursor.execute("""UPDATE SQLITE_SEQUENCE
                                         SET SEQ = 0 
                                       WHERE NAME = 'JCASHBOOK_INC_EXP_DTL'""")
            cursor.execute("""CREATE TABLE JCASHBOOK_MAIN_DATA (
                                             ROW_ID INTEGER PRIMARY KEY AUTOINCREMENT
                                           , BAS_DT TEXT
                                           , INC_EXP_CLS TEXT
                                           , INC_EXP_DTL_CLS TEXT
                                           , NOTE TEXT
                                           , AMT INTEGER)""")
            cursor.execute("""UPDATE SQLITE_SEQUENCE 
                                         SET SEQ = 0
                                       WHERE NAME = 'JCASHBOOK_MAIN_DATA'""")
            cursor.execute("""CREATE TABLE JCASHBOOK_MONTH (
                                             MONTH TEXT)""")
            cursor.execute("""INSERT INTO JCASHBOOK_MONTH VALUES('01')""")
            cursor.execute("""INSERT INTO JCASHBOOK_MONTH VALUES('02')""")
            cursor.execute("""INSERT INTO JCASHBOOK_MONTH VALUES('03')""")
            cursor.execute("""INSERT INTO JCASHBOOK_MONTH VALUES('04')""")
            cursor.execute("""INSERT INTO JCASHBOOK_MONTH VALUES('05')""")
            cursor.execute("""INSERT INTO JCASHBOOK_MONTH VALUES('06')""")
            cursor.execute("""INSERT INTO JCASHBOOK_MONTH VALUES('07')""")
            cursor.execute("""INSERT INTO JCASHBOOK_MONTH VALUES('08')""")
            cursor.execute("""INSERT INTO JCASHBOOK_MONTH VALUES('09')""")
            cursor.execute("""INSERT INTO JCASHBOOK_MONTH VALUES('10')""")
            cursor.execute("""INSERT INTO JCASHBOOK_MONTH VALUES('11')""")
            cursor.execute("""INSERT INTO JCASHBOOK_MONTH VALUES('12')""")
            conn.commit()
        finally:
            conn.close()

        # 수입/지출 세부 항목 조회

    def selectIncExpDtlSetInfo(self):
        self.comboBox2.addItem("전체")
        conn = sqlite3.connect('cashbook.db')
        with conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT * 
                                        FROM JCASHBOOK_INC_EXP_DTL 
                                       WHERE INC_EXP_CLS = ?
                                       ORDER BY INC_EXP_DTL_CLS""", (str(self.comboBox1.currentIndex())))
            self.selectIncExpDtlResults = cursor.fetchall()
            for row in self.selectIncExpDtlResults:
                self.comboBox2.addItem(row[2])
            self.comboBox2.setCurrentIndex(0)

        # 조회 버튼 클릭 시

    def pushButton1Clicked(self):
        self.tableWidget1.clear()
        self.selectMainData()

        # 입력 버튼 클릭 시

    def pushButton2Clicked(self):
        sg = self.geometry()
        insertDialog = InsertDialog(sg.left(), sg.top(), '2', [])  # dmlCls --> 1 : 수정/삭제, 2 : 입력
        insertDialog.exec_()

        # 수입/지출 조건 변경 시 세부 항목 리스트 초기화

    def comboBox1Activated(self):
        self.comboBox2.clear()
        self.selectIncExpDtlSetInfo()

        # 테이블위젯 "더블클릭" --> 수정/삭제 창 띄우기

    def tableWidget1DoubleClicked(self, row, column):
        tableWidget1RowData = []
        for i in range(6):
            tableWidget1RowData.append(self.tableWidget1.item(row, i).text())
        sg = self.geometry()
        insertDialog = InsertDialog(sg.left(), sg.top(), '1',
                                    tuple(tableWidget1RowData))  # dmlCls --> 1 : 수정/삭제, 2 : 입력
        insertDialog.exec_()

        # 엑셀 내보내기 메뉴

    def excelOutActTriggered(self):
        sg = self.geometry()
        setDlg = excelOutDialog(sg.left(), sg.top())
        setDlg.exec_()

        # 엑셀 불러오기 메뉴

    def excelInActTriggered(self):
        # 엑셀 불러오기 시작
        excelInFileName = QFileDialog.getOpenFileName(self)
        if not excelInFileName[0]:
            return
        wb = openpyxl.load_workbook(excelInFileName[0])
        ws = wb.active
        # 엑셀 데이터를 리스트 변수에 저장
        excelIndata = []
        for row in ws.rows:
            excelIndata.append([str(row[0].value)[0:10], row[1].value, row[2].value, row[3].value, row[4].value])
        del excelIndata[0]  # 헤더 삭제
        # 데이터베이스 저장
        conn = sqlite3.connect('cashbook.db')
        with conn:
            cursor = conn.cursor()
            cursor.executemany(
                "INSERT INTO JCASHBOOK_MAIN_DATA (BAS_DT, INC_EXP_CLS, INC_EXP_DTL_CLS, NOTE, AMT) VALUES (?,?,?,?,?)",
                excelIndata)
            # for row in excelIndata:
            #     cursor.execute("INSERT INTO JCASHBOOK_MAIN_DATA (BAS_DT, INC_EXP_CLS, INC_EXP_DTL_CLS, NOTE, AMT) VALUES (?,?,?,?,?)", tuple(row))
            conn.commit()
            QMessageBox.information(self, "Info", "엑셀 불러오기가 완료되었습니다.")

        # 데이터 삭제하기 메뉴

    def deleteDataActActTriggered(self):
        sg = self.geometry()
        setDlg = delDataDialog(sg.left(), sg.top())
        setDlg.exec_()

        # 차트1 메뉴

    def chart1ActTriggered(self):
        sg = self.geometry()
        setDlg = chart1Dialog(sg.left(), sg.top())
        setDlg.exec_()

        # 차트2 메뉴

    def chart2ActTriggered(self):
        sg = self.geometry()
        setDlg = chart2Dialog(sg.left(), sg.top())
        setDlg.exec_()

        # 도움말 메뉴

    def helpActTriggered(self):
        sg = self.geometry()
        setDlg = helpDialog(sg.left(), sg.top())
        setDlg.exec_()

        # 수입/지출 세부 항목 설정 메뉴 --> setDialog 창 띄움

    def setIncExpDtlActTriggered(self):
        sg = self.geometry()
        setDlg = setDialog(sg.left(), sg.top())
        setDlg.exec_()

if __name__ == "__main__":  #현재 스크립트가 직접 실행될 때만 아래의 코드를 실행하도록
    app = QApplication(sys.argv)
    cashbookWindow = cashbookWindow()
    cashbookWindow.show()
    app.exec_()