import sqlite3
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
        url = "http://clovaocr-api-kr.ncloud.com/external/v1/26549/c588e771a4153b59cc1bab82d1513e325b87352e3255bdc8e323a61aa85550d3"  # NAVER CLOVA OCR API URL
        headers = {
            "X-OCR-SECRET": "aGlPUUNzSkJKbHV3ZXpHd2lLS1dIZ2NGVklCaWlRYUk="  # API 키
        }

        # 파일을 'rb' 모드로 열어 바이너리 데이터를 준비합니다.
        files = {'image': open(image_path, 'rb')}

        try:
            response = requests.post(url, headers=headers, files=files)
            response.raise_for_status()  # 요청 실패 시 예외 발생

            # 여기에서 API 응답을 처리합니다.
            ocr_result = response.json()
            self.handleOCRResult(ocr_result)

        except requests.exceptions.HTTPError as err:
            QMessageBox.warning(self, "API 요청 실패", f"HTTP 요청 에러: {err}")
        except Exception as e:
            QMessageBox.warning(self, "오류 발생", f"오류: {e}")

    def handleOCRResult(self, result):
        # OCR 결과에서 필요한 정보 추출
        store_name = result["result"]["storeInfo"]["name"]["text"]
        date_text = result["result"]["paymentInfo"]["date"]["text"]
        total_price = result["result"]["totalPrice"]["price"]["formatted"]["value"]

        # 날짜 형식 변환 (예시: '2019/06/02' -> '2019-06-02')
        date_formatted = datetime.strptime(date_text, "%Y/%m/%d").strftime("%Y-%m-%d")

        # 추출된 데이터 저장
        self.extractedData = {
            "date": date_formatted,
            "note": store_name,
            "amount": total_price
        }

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