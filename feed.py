
from PyQt5.QtWidgets import *


# 피드백 윈도우
class feedDialog(QDialog):
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
        self.setWindowTitle("피드백")
        self.setModal(True)

        # 상세 UI 셋업 호출
        self.setupUI()

    def setupUI(self):
        layout = QVBoxLayout(self)
