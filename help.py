from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *

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