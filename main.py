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
import sqlite3
import sys
import openpyxl
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


# 메인 윈도우
class cashbookWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 윈도우 센터에 위치 시키기, 타이틀 지정, Modal 지정
        # 해상도 구하기 (sg = QDesktopWidget().screenGeometry())
        self.tableWidget1 = None
        ag = QDesktopWidget().availableGeometry()
        mainWindowWidth = 1000
        mainWindowHeight = 740
        mainWindowLeft = int((ag.width() - mainWindowWidth) / 2)
        mainWindowTop = int((ag.height() - mainWindowHeight) / 2)
        self.setGeometry(mainWindowLeft, mainWindowTop, mainWindowWidth, mainWindowHeight)
        self.setFixedSize(mainWindowWidth, mainWindowHeight)
        self.setWindowTitle("팀 얼랑뚱땅 - 가계부")

        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #B2DFDB, stop:1 #80CBC4); /* 민트색 그라데이션 */
            }

            QPushButton {
                background-color: #4DD0E1; /* 청량한 하늘색 배경 */
                border: none;
                color: white;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 14px;
                margin: 4px 2px;
                cursor: pointer;
                border-radius: 4px;
                transition: background-color 0.3s;
            }

            QPushButton:hover {
                background-color: #26C6DA; /* 좀 더 진한 하늘색 배경 */
            }

            QLabel, QCheckBox, QComboBox, QDateEdit {
                font-size: 14px;
                color: #00838F; /* 진한 하늘색 텍스트 */
            }

            QLineEdit {
                border: 1px solid #4DB6AC; /* 민트색 테두리 */
                border-radius: 4px;
                padding: 5px;
                color: #00695C; /* 진한 민트색 텍스트 */
            }

            QTableWidget {
                border: 1px solid #26A69A; /* 중간 민트색 테두리 */
                selection-background-color: #B2EBF2; /* 연한 하늘색 배경 */
                selection-color: black;
            }

            QHeaderView::section {
                background-color: #80DEEA; /* 연한 하늘색 배경 */
                padding: 4px;
                border: 1px solid #4DD0E1; /* 하늘색 테두리 */
                font-size: 14px;
            }

            QStatusBar {
                background: #00C6FF; /* 스카이블루 배경 */
                color: black;
            }
        """)

        # 상세 UI 셋업 호출
        self.setupUI()

    def setupUI(self):
        # 년월 조건 라벨
        self.label1 = QLabel('조회조건:', self)
        self.label1.move(15, 33)
        self.label1.setFont(QFont('Arial', 10))

        # 년월 조건 날짜 선택기
        self.dateEdit1 = QDateEdit(self)
        self.dateEdit1.move(95, 35)
        self.dateEdit1.resize(100, 25)
        self.dateEdit1.setFont(QFont('Arial', 10))
        self.dateEdit1.setDisplayFormat("yyyy-MM")
        self.dateEdit1.setDate(QDate.currentDate())

        # 수입/지출 조건 콤보 박스
        self.comboBox1 = QComboBox(self)
        self.comboBox1.setGeometry(210, 35, 100, 25)
        self.comboBox1.setFont(QFont('Arial', 10))
        self.comboBox1.addItem("전체")
        self.comboBox1.addItem("수입")
        self.comboBox1.addItem("지출")
        self.comboBox1.setCurrentIndex(0)
        self.comboBox1.activated[str].connect(self.comboBox1Activated)

        # 항목 상세 조건 콤보 박스
        self.comboBox2 = QComboBox(self)
        self.comboBox2.setGeometry(325, 35, 120, 25)
        self.comboBox2.setFont(QFont('Arial', 10))
        self.comboBox2.addItem("전체")

        # 적요 조건 텍스트 필드
        self.lineEdit1 = QLineEdit(self)
        self.lineEdit1.setGeometry(460, 35, 120, 25)
        self.lineEdit1.setFont(QFont('Arial', 10))
        self.lineEdit1.setMaxLength(20)

        # 정렬 조건 라벨
        self.label3 = QLabel('정렬방식:', self)
        self.label3.move(590, 33)
        self.label3.setFont(QFont('Arial', 10))

        # 정렬 조건 콤보 박스
        self.comboBox3 = QComboBox(self)
        self.comboBox3.setGeometry(670, 35, 100, 25)
        self.comboBox3.setFont(QFont('Arial', 10))
        self.comboBox3.addItem("일자")
        self.comboBox3.addItem("수입/지출")
        self.comboBox3.addItem("세부항목")
        self.comboBox3.addItem("적요")
        self.comboBox3.addItem("금액")
        self.comboBox3.setCurrentIndex(0)

        # 내림차순 체크박스
        self.checkBox3 = QCheckBox("내림차순", self)
        self.checkBox3.setChecked(True)
        self.checkBox3.setGeometry(780, 35, 100, 25)
        self.checkBox3.setFont(QFont('Arial', 10))

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
        self.tableWidget1.setGridStyle(Qt.SolidLine)
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
        helpAct = QAction('도움말', self)
        menuBar.addAction(helpAct)
        helpAct.triggered.connect(self.helpActTriggered)

        # 최상위 'OCR' 메뉴
        ocrAct = QAction('OCR', self)
        menuBar.addAction(ocrAct)
        ocrAct.triggered.connect(self.ocrActTriggered)

        # 최상위 '피드백' 메뉴
        feedAct = QAction('피드백', self)
        menuBar.addAction(feedAct)
        feedAct.triggered.connect(self.feedActTriggered)

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
        except Exception as e:
            # 테이블 및 시퀀스 생성, ROW_ID 컬럼은 AUTOINCREMENT

            print("Error during database operation:", e)

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
        from Insert import InsertDialog
        insertDialog = InsertDialog(sg.left(), sg.top(), '2', [])  # dmlCls --> 1 : 수정/삭제, 2 : 입력
        insertDialog.dataChanged.connect(self.selectMainData)
        insertDialog.exec_()

        # 수입/지출 조건 변경 시 세부 항목 리스트 초기화

    def comboBox1Activated(self):
        self.comboBox2.clear()
        self.selectIncExpDtlSetInfo()

        # 테이블위젯 "더블클릭" --> 수정/삭제 창 띄우기

    def tableWidget1DoubleClicked(self, row, column):
        try:
            tableWidget1RowData = []
            for i in range(6):
                tableWidget1RowData.append(self.tableWidget1.item(row, i).text())
            sg = self.geometry()
            from Insert import InsertDialog
            insertDialog = InsertDialog(sg.left(), sg.top(), '1',
                                        tuple(tableWidget1RowData))  # dmlCls --> 1 : 수정/삭제, 2 : 입력
            insertDialog.dataChanged.connect(self.selectMainData)
            insertDialog.exec_()
        except Exception as e:
            print("Error in tableWidget1DoubleClicked: ", e)

        # 엑셀 내보내기 메뉴

    def excelOutActTriggered(self):
        sg = self.geometry()
        from excelOut import excelOutDialog
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
        from delData import delDataDialog
        setDlg = delDataDialog(sg.left(), sg.top())
        setDlg.exec_()

        # 차트1 메뉴

    def chart1ActTriggered(self):
        sg = self.geometry()
        from chart1 import chart1Dialog
        setDlg = chart1Dialog(sg.left(), sg.top())
        setDlg.exec_()

        # 차트2 메뉴

    def chart2ActTriggered(self):
        sg = self.geometry()
        from chart2 import chart2Dialog
        setDlg = chart2Dialog(sg.left(), sg.top())
        setDlg.exec_()

        # 도움말 메뉴

    def helpActTriggered(self):
        sg = self.geometry()
        from help import helpDialog
        setDlg = helpDialog(sg.left(), sg.top())
        setDlg.exec_()

        # 수입/지출 세부 항목 설정 메뉴 --> setDialog 창 띄움

    def setIncExpDtlActTriggered(self):
        sg = self.geometry()
        from setDialog import setDialog
        setDlg = setDialog(sg.left(), sg.top())
        setDlg.exec_()

    def ocrActTriggered(self):
        sg = self.geometry()
        from OCR import ocrDialog
        setDlg = ocrDialog(sg.left(), sg.top())
        setDlg.exec_()

    def feedActTriggered(self):
        try:
            sg = self.geometry()
            from feed import feedDialog
            setDlg = feedDialog(sg.left(), sg.top())
            setDlg.exec_()
        except Exception as e:
            print(f"오류: {e}")

if __name__ == "__main__":  #현재 스크립트가 직접 실행될 때만 아래의 코드를 실행하도록
    app = QApplication(sys.argv)
    cashbookWindow = cashbookWindow()
    cashbookWindow.show()
    app.exec_()