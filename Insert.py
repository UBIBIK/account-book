import sqlite3

from PyQt5.QtCore import QDate, pyqtSignal
from PyQt5.QtGui import QFont, QDoubleValidator
from PyQt5.QtWidgets import *

from main import cashbookWindow


# 가계부 데이터 입력
class InsertDialog(QDialog):
    dataChanged = pyqtSignal()
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
            self.pushButton5 = QPushButton("삭제", self)
            self.pushButton5.setGeometry(260, 375, 80, 30)
            self.pushButton5.clicked.connect(self.pushButton5Clicked)
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
        # 대화 상자가 닫힐 때 신호 발생
        self.dataChanged.emit()
        super().closeEvent(evnt)

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
        from datetime import datetime
        self.dateEdit1.setDate(datetime.strptime(self.tableWidget1RowData[0],'%Y-%m-%d'))
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
        #데이터 저장 후 신호 발생
        self.dataChanged.emit()
        self.close()

    # 나가기 버튼 클릭 시
    def pushButton7Clicked(self):
        self.close()