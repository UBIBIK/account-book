import base64
import json
import os
import sqlite3
import uuid
import time
from datetime import datetime
import requests
from PyQt5.QtWidgets import *

# OCR 윈도우
class ocrDialog(QDialog):
    def __init__(self, mainWindowLeft, mainWindowTop):
        super().__init__()

        # 윈도우 센터에 위치 시키기, 타이틀 지정, Modal 지정
        self.saveDataButton = None
        self.ocrResultText = None
        self.selectImageButton = None
        dialogLeft = mainWindowLeft + 130
        dialogTop = mainWindowTop + 60
        dialogWidth = 740
        dialogHeight = 590
        self.setGeometry(dialogLeft, dialogTop, dialogWidth, dialogHeight)
        self.setFixedSize(dialogWidth, dialogHeight)
        self.setWindowTitle("영수증 처리")
        self.setModal(True)

        # 상세 UI 셋업 호출
        self.setupUI()

    def setupUI(self):
        # 이미지 선택 버튼
        self.selectImageButton = QPushButton("영수증 이미지 선택", self)
        self.selectImageButton.clicked.connect(self.selectImage)

        # OCR 결과 표시
        self.ocrResultText = QTextEdit(self)
        self.ocrResultText.setReadOnly(True)

        # 데이터 저장 버튼
        self.saveDataButton = QPushButton("데이터 저장", self)
        self.saveDataButton.clicked.connect(self.saveData)

        # 레이아웃 설정
        layout = QVBoxLayout(self)
        layout.addWidget(self.selectImageButton)
        layout.addWidget(self.ocrResultText)
        layout.addWidget(self.saveDataButton)

    def selectImage(self):
        # 사용자가 이미지 선택
        filename, _ = QFileDialog.getOpenFileName(self, "영수증 이미지 선택", "", "Image Files (*.png *.jpg *.jpeg)")
        if filename:
            self.processOCR(filename)

    def processOCR(self, image_path):
        # NAVER CLOVA OCR API URL과 API 키
        url = "https://vlh98m0hhc.apigw.ntruss.com/custom/v1/26549/c588e771a4153b59cc1bab82d1513e325b87352e3255bdc8e323a61aa85550d3/general"
        secret_key = "dW1ab2h2WGVtZGhYa2JGaElySWtkUE5KbHJNS0luTm8="

        request_json = {
            'images': [
                {
                    'format': 'jpg',
                    'name': 'demo'
                }
            ],
            'requestId': str(uuid.uuid4()),
            'version': 'V2',
            'timestamp': int(round(time.time() * 1000))
        }

        payload = {'message': json.dumps(request_json).encode('UTF-8')}
        files = [
            ('file', open(image_path, 'rb'))
        ]
        headers = {
            'X-OCR-SECRET': secret_key
        }

        response = requests.request("POST", url, headers=headers, data=payload, files=files)

        print(response.text.encode('utf8'))

        result = response.json()

        print(result)

        text = ""
        for field in result['images'][0]['fields']:
            text += field['inferText']
        print(text)

    def handleOCRResult(self, result):
        # 필요한 정보 추출
        store_name = result["result"]["storeInfo"]["name"]["text"]
        address = result["result"]["storeInfo"]["address"][0]["text"]
        date_text = result["result"]["paymentInfo"]["date"]["text"]
        total_price = result["result"]["totalPrice"]["price"]["formatted"]["value"]

        # 항목 정보 추출
        items = []
        for item in result["result"]["subResults"][0]["items"]:
            name = item["name"]["text"]
            count = item["count"]["text"]
            price = item["priceInfo"]["price"]["formatted"]["value"]
            unit_price = item["priceInfo"]["unitPrice"]["formatted"]["value"]

            items.append(f"항목: {name}, 수량: {count}, 금액: {price}, 단가: {unit_price}")

        # 결과 문자열 생성
        ocr_text = f"매장 이름: {store_name}\n주소: {address}\n날짜: {date_text}\n총 금액: {total_price}\n"
        for item_text in items:
            ocr_text += item_text + "\n"

        # OCR 결과 표시
        self.ocrResultText.setText(ocr_text)

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