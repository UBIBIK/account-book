import sqlite3
import numpy as np
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import rc
import matplotlib.font_manager as fm

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