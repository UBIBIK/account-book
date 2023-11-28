import sqlite3
import numpy as np
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import rc
import matplotlib.font_manager as fm

#차트 2 만들기
class Plot2Canvas(FigureCanvas):

    def __init__(self, parent=None, width=6, height=5, dpi=100, whereStr1='2017', whereStr2='전체', whereStr3='수입'):
        fig = Figure(figsize=(width, height), dpi=dpi)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.plot(whereStr1, whereStr2, whereStr3)

    def plot(self, whereStr1, whereStr2, whereStr3):
        # 개별 폰트
        font_path = 'C:/Windows/Fonts/malgun.ttf'
        fontprop1 = fm.FontProperties(fname=font_path, size=14)
        fontprop2 = fm.FontProperties(fname=font_path, size=12)
        # 전체 폰트
        font_name = fm.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
        rc('font', family=font_name)
        # 데이터 조회
        incExpDtlCls = []
        amt = []
        conn = sqlite3.connect('cashbook.db')
        with conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT CASE WHEN INC_EXP_DTL_CLS = '' THEN '선택안함' ELSE INC_EXP_DTL_CLS END
                                   , SUM(AMT) AS AMT
                                FROM JCASHBOOK_MAIN_DATA
                               WHERE SUBSTR(BAS_DT,1,4) = ?
                                 AND (SUBSTR(BAS_DT,6,2) = ? OR '전체' = ?)
                                 AND INC_EXP_CLS = ?
                               GROUP BY CASE WHEN INC_EXP_DTL_CLS = '' THEN '선택안함' ELSE INC_EXP_DTL_CLS END
                               ORDER BY 1""", (whereStr1, whereStr2, whereStr2, whereStr3))
            self.selectResults = cursor.fetchall()
            for row in self.selectResults:
                incExpDtlCls.append(row[0])
                amt.append(row[1])
        # 인덱스 및 기본 개수(5) 채우기
        def_cnt = 5
        sel_cnt = len(incExpDtlCls)
        if len(incExpDtlCls) < def_cnt:
            ind = np.arange(5)
            while sel_cnt != def_cnt:
                incExpDtlCls.append('')
                amt.append(0)
                sel_cnt = sel_cnt + 1
        else:
            ind = np.arange(len(incExpDtlCls))
        # ax 객체 생성 및 차트 그리기
        ax = self.figure.add_subplot(111)
        ax.cla()
        ax.barh(ind, amt, height=0.3, align='center')
        ax.set_yticklabels(incExpDtlCls)
        ax.invert_yaxis()
        ax.set_title('수입/지출 세부 항목별 분석', fontproperties=fontprop1)
        ax.set_xlabel('금액', fontproperties=fontprop2)
        ax.set_ylabel('세부항목', fontproperties=fontprop2)
        ax.set_yticks(ind)
        ax.set_yticklabels(incExpDtlCls)
        ax.legend()
        self.draw()