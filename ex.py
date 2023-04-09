



import numpy as np
import pandas as pd
from cog import Cog



url = "C:/Users/justi/Desktop/COG거점_시뮬레이션/거점_raw.xlsx"
#위도 , 경도 순서
fix_p = [(36.6424341*3600, 127.4890319*3600), (36.6424341*3600, 127.4890319*3600), (129049.48296, 457546.66416)]
test_a = Cog(url, fix_p)
data = test_a.load_excel_data()
df = test_a.cal_curvature_value(data)
test_list = test_a.make_position(df, 0)
test_a.classified_position(df, test_list)


def func(dt) :
    for i in range(len(test_list)):
        if dt == "거점"+str(i+1):
            return test_list[i][0]
        else:
            return "오류"


def func1(dt) :
    for i in range(len(test_list)):
        if dt == "거점"+str(i+1):
            return test_list[i][1]
        else:
            return "오류"


df['선택거점_위도'] = df['선택'].apply(func)
df['선택거점_경도'] = df['선택'].apply(func1)

test_a.cal_standard_curvature_value(df)
result_df = test_a.cal_point_result(df, test_list)


result_df.to_excel('거점'+ str(len(test_list)) +'청주 시뮬레시션1(전주공장픽스).xlsx')
