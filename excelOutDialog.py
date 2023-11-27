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

#엑셀 내보내기
class excelOutDialog(QDialog):
    def __init__(self, mainWindowLeft, mainWindowTop):
        super().__init__()

        # 윈도우 센터에 위치 시키기, 타이틀 지정, Modal 지정
        dialogLeft = mainWindowLeft + 290  # 가로위치
        dialogTop = mainWindowTop + 120  # 세로위치
        dialogWidth = 400  # 가로길이
        dialogHeight = 150  # 세로길이
        self.setGeometry(dialogLeft, dialogTop, dialogWidth, dialogHeight)  # 윈도우 위치 지정
        self.setFixedSize(dialogWidth, dialogHeight)  # 윈도우 크기 고정시키기
        self.setWindowTitle("엑셀 내보내기")  # 윈도우 타이틀 지정
        self.setModal(True)  # Modal 창 지정

        # 상세 UI 셋업 호출
        self.setupUI()

    def setupUI(self):

        # 그룹 박스
        self.groupBox1 = QGroupBox("범위 선택", self)
        self.groupBox1.setGeometry(30, 20, 340, 50)

        # 엑셀 내보내기 범위 선택
        self.radio1 = QRadioButton("현재 조회한 데이터", self)
        self.radio1.move(50, 40)
        self.radio1.setChecked(True)
        self.radio2 = QRadioButton("cashbook 전체 데이터", self)
        self.radio2.move(200, 40)

        # 내보내기 버튼
        self.pushButton6 = QPushButton("내보내기", self)
        self.pushButton6.setGeometry(90, 90, 90, 30)
        self.pushButton6.clicked.connect(self.pushButton6Clicked)

        # 나가기 버튼
        self.pushButton7 = QPushButton("나가기", self)
        self.pushButton7.setGeometry(220, 90, 90, 30)
        self.pushButton7.clicked.connect(self.pushButton7Clicked)

    # 엑세 내보내기 클릭 시
    def pushButton6Clicked(self):
        # 엑셀 컨트롤 시작
        wb = openpyxl.workbook.Workbook()  # 워크북 생성
        ws1 = wb.active  # 현재 Active Sheet 얻기
        ws1.title = "Jcashbook_Data"  # Active Sheet 타이틀 지정
        # 헤더 출력
        ws1["A1"] = "일자"
        ws1["B1"] = "수입/지출"
        ws1["C1"] = "세부항목"
        ws1["D1"] = "적요"
        ws1["E1"] = "금액"
        # 출력할 cashbook 데이터셋 만들기
        if self.radio1.isChecked():
            excelOutData = cashbookWindow.selectMainDataResults
        elif self.radio2.isChecked():
            conn = sqlite3.connect('cashbook.db')
            with conn:
                cursor = conn.cursor()
                cursor.execute("""SELECT BAS_DT, INC_EXP_CLS, INC_EXP_DTL_CLS, NOTE, AMT
                                    FROM JCASHBOOK_MAIN_DATA 
                                   ORDER BY BAS_DT, INC_EXP_CLS, INC_EXP_DTL_CLS, NOTE, AMT""")
                excelOutData = cursor.fetchall()
        # 엑셀 cell 출력
        i = 2
        for row in excelOutData:
            j = 1
            for col in row:
                if j == 6:
                    break
                ws1.cell(row=i, column=j, value=col)
                j = j + 1
            i = i + 1
        # 파일 저장
        wb.save("Jcashbook_Data.xlsx")
        QMessageBox.information(self, "Info", '엑셀 내보내기를 완료했습니다. 현재 폴더에서 "Jcashbook_Data.xlsx" 파일을 확인하세요.')

    # 나가기 버튼 클릭 시
    def pushButton7Clicked(self):
        self.close()