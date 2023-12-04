import json
import os
import sqlite3
import uuid
import time
import requests
from PyQt5.QtWidgets import *

# OCR 윈도우
class ocrDialog(QDialog):
    def __init__(self, mainWindowLeft, mainWindowTop):
        super().__init__()

        # 윈도우 센터에 위치 시키기, 타이틀 지정, Modal 지정
        self.tableWidget = None
        self.saveDataButton = None
        self.selectImageButton = None
        self.extractedData = None
        dialogLeft = mainWindowLeft + 130
        dialogTop = mainWindowTop + 60
        dialogWidth = 740
        dialogHeight = 590
        self.setGeometry(dialogLeft, dialogTop, dialogWidth, dialogHeight)
        self.setFixedSize(dialogWidth, dialogHeight)
        self.setWindowTitle("영수증 처리")
        self.setModal(True)

        # 스타일시트 적용
        self.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50; /* 녹색 배경 */
                    color: white; /* 흰색 글씨 */
                    border: none;
                    padding: 10px 20px;
                    border-radius: 4px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #45a049; /* 버튼에 마우스를 올렸을 때 더 진한 녹색 */
                }
                QTableWidget {
                    border: 1px solid #ddd; /* 연한 회색 테두리 */
                    font-size: 14px;
                }
                QTextEdit {
                    border: 1px solid #ddd;
                    font-size: 14px;
                }
                QStatusBar {
                    background-color: #f2f2f2; /* 연한 회색 배경 */
                    color: black;
                }
            """)

        # 상태 표시줄
        self.statusBar = QStatusBar(self)

        # 상세 UI 셋업 호출
        self.setupUI()

    def setupUI(self):
        # 레이아웃 설정
        layout = QVBoxLayout(self)

        # 이미지 선택 버튼
        self.selectImageButton = QPushButton("영수증 이미지 선택", self)
        self.selectImageButton.clicked.connect(self.selectImage)
        self.selectImageButton.setToolTip("영수증 이미지를 선택합니다.")
        layout.addWidget(self.selectImageButton)

        # OCR 결과 테이블 표시
        self.tableWidget = QTableWidget(self)
        self.tableWidget.setColumnCount(5)  # 예: 이름, 수량, 단가, 총액
        self.tableWidget.setHorizontalHeaderLabels(["날짜","항목 이름", "수량", "단가", "총액"])
        self.tableWidget.setEditTriggers(QAbstractItemView.AllEditTriggers)

        # 테이블 레이아웃 조정
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tableWidget)

        # 데이터 저장 버튼
        self.saveDataButton = QPushButton("데이터 저장", self)
        self.saveDataButton.clicked.connect(self.saveData)
        self.saveDataButton.setToolTip("수정한 데이터를 저장합니다.")
        layout.addWidget(self.saveDataButton)

        # 상태 표시줄 설정
        self.statusBar = QStatusBar(self)
        self.statusBar.showMessage("영수증 이미지를 선택해주세요.")
        layout.addWidget(self.statusBar)

        self.setLayout(layout)

    def selectImage(self):
        try:
            filename, _ = QFileDialog.getOpenFileName(self, "영수증 이미지 선택", "", "Image Files (*.png *.jpg *.jpeg)")
            if filename:
                self.processOCR(filename)
        except Exception as e:
            QMessageBox.warning(self, "오류", f"오류 발생: {e}")
            print(f"오류: {e}")

    def processOCR(self, image_path):
        # 이미지 형식 추출 (예: 'jpg', 'png')
        image_format = os.path.splitext(image_path)[-1].strip('.').lower()

        # NAVER CLOVA OCR API 설정
        url = "https://bv8u2jijp9.apigw.ntruss.com/custom/v1/26712/53d262ab4f04283c1a01e5cdaab8650c1931380ad0cd43df1f8d5a4a07c7a3be/document/receipt"
        secret_key = "Y3ZNdGRTcGZWa1NzS21QcGpyQmhUU2Z3aGRuRlN2WFo="

        request_json = {
            'images': [{'format': image_format, 'name': 'demo'}],
            'requestId': str(uuid.uuid4()),
            'version': 'V2',
            'timestamp': int(round(time.time() * 1000))
        }

        payload = {'message': json.dumps(request_json).encode('UTF-8')}
        files = [('file', open(image_path, 'rb'))]
        headers = {'X-OCR-SECRET': secret_key}

        try:
            response = requests.request("POST", url, headers=headers, data=payload, files=files)
            response.raise_for_status()  # 오류 응답을 확인하고 예외를 발생시킵니다.
            result = response.json()
            self.handleOCRResult(result)
            self.statusBar.showMessage("OCR 처리 완료")
        except requests.exceptions.RequestException as e:
            self.statusBar.showMessage("OCR 처리 중 오류 발생: " + str(e))
            print(f"OCR처리 중 오류: {e}")

    def handleOCRResult(self, result):
        try:
            # 필요한 정보 추출
            store_name = result["images"][0]["receipt"]["result"]["storeInfo"]["name"]["text"]
            date_text = result["images"][0]["receipt"]["result"]["paymentInfo"]["date"]["text"]

            # 항목 정보 추출 및 테이블에 채우기
            items = result["images"][0]["receipt"]["result"]["subResults"][0]["items"]
            self.tableWidget.setRowCount(len(items))

            for i, item in enumerate(result["images"][0]["receipt"]["result"]["subResults"][0]["items"]):
                name = item["name"]["text"]
                count = item.get("count", {}).get("text", "1")  # count가 없는 경우 기본값으로 '1'을 사용
                unit_price = item["price"]["unitPrice"]["text"].replace(",", "")
                quantity = int(count)
                unit_price_item = int(unit_price)
                price = quantity * unit_price_item

                self.tableWidget.insertRow(i)
                self.tableWidget.setItem(i, 0, QTableWidgetItem(date_text))
                self.tableWidget.setItem(i, 1, QTableWidgetItem(name))
                self.tableWidget.setItem(i, 2, QTableWidgetItem(count))
                self.tableWidget.setItem(i, 3, QTableWidgetItem(unit_price))
                self.tableWidget.setItem(i, 4, QTableWidgetItem(str(price)))

            # 추출된 데이터 저장
            self.extractedData = {
                "date": date_text,
                "amount": str(price),
                "note": store_name
            }

        except Exception as e:
            QMessageBox.warning(self, "오류", f"OCR 결과 처리 중 오류 발생: {e}")

    def saveData(self):
        if self.extractedData:
            try:
                # 데이터베이스에 연결
                conn = sqlite3.connect('cashbook.db')  # 데이터베이스 파일명에 맞게 조정
                cursor = conn.cursor()

                # INSERT 쿼리 실행
                cursor.execute("""
                    INSERT INTO JCASHBOOK_MAIN_DATA (BAS_DT, INC_EXP_CLS, INC_EXP_DTL_CLS, NOTE, AMT)
                    VALUES (?, ?, ?, ?, ?)
                """, (self.extractedData["date"], '지출', '영수증', self.extractedData["note"], self.extractedData["amount"]))

                conn.commit()
                QMessageBox.information(self, "성공", "데이터가 성공적으로 저장되었습니다.")
            except Exception as e:
                QMessageBox.warning(self, "오류", f"데이터 저장 중 오류 발생: {e}")
            finally:
                if conn:
                    conn.close()
        else:
            QMessageBox.warning(self, "경고", "저장할 데이터가 없습니다.")
