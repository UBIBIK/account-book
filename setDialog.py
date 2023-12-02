import sqlite3
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *


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

        #스타일 지정
        # 스타일 지정
        self.setStyleSheet("""
                    QDialog {
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

                    QLineEdit, QListWidget {
                        border: 1px solid #4DB6AC; /* 민트색 테두리 */
                        border-radius: 4px;
                        padding: 5px;
                        color: #00695C; /* 진한 민트색 텍스트 */
                    }
                """)

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