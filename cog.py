import numpy as np
import pandas as pd


class Cog:

    #초기화
    def __init__(self, file_url, fixed_point):
        self.file = file_url
        self.fixed_point = fixed_point

    # 엑셀 데이터 로드
    def load_excel_data(self):

        data = pd.read_excel(self.file)
        return data

    # 곡률값 계산 및 정렬
    def cal_curvature_value(self, df):

        df['경도 곡률값'] = df['경도\n(Longitude)'] * 3600
        df['위도 곡률값'] = df['위도\n(Latitude)'] * 3600
        df = df.sort_values(by='Demand\n(Vi)', ascending=False)
        df = df.reset_index()
        return df


    # 고정된 거점 곡률값과 정한 거점 곡률값 리스트 생성
    # 동적 정할 거점 개수 = count
    def make_position(self, df, count):
        point_list = []
        position_list = [  (df.loc[i, '위도 곡률값'], df.loc[i, '경도 곡률값'])  for i in range(count) ]
        point_list.extend(position_list)
        point_list.extend(self.fixed_point)
        return point_list


    def classified_position(self, df , point_list):

        for i in range(len(point_list)):
            df['거점'+ str(i+1)] = np.sqrt((df['위도 곡률값'] - point_list[i][0]) ** 2 + (df['경도 곡률값'] - point_list[i][1]) ** 2)

        name_list = ["거점"+str(i+1) for i in range(len(point_list))]
        df['선택'] = df.loc[:,  name_list].fillna(0).idxmin(axis=1)


    def cal_standard_curvature_value(self, df):
        df['위도간 거리(기준)_곡률값'] = min(df['위도\n(Latitude)']) * 3600
        df['경도간 거리(기준)_곡률값'] = min(df['경도\n(Longitude)']) * 3600

        df['위도간 거리(Y좌표 거리)'] = abs(df['위도\n(Latitude)'] * 3600 - df['위도간 거리(기준)_곡률값']) * 0.0245
        df['경도간 거리(X좌표 거리)'] = abs(df['경도\n(Longitude)'] * 3600 - df['경도간 거리(기준)_곡률값']) * 0.0306

        # 박스당 단가*물량 = VR
        df['VR'] = df['지역별 박스당 단가'] * df['Demand\n(Vi)']

        # .columns  박스당 단가* 물량*경도간 거리(X좌표 거리) = VRX
        df['VRX'] = df['지역별 박스당 단가'] * df['Demand\n(Vi)'] * df['경도간 거리(X좌표 거리)']

        # .columns  박스당 단가* 물량*위도간 거리(Y좌표 거리) = VRY
        df['VRY'] = df['지역별 박스당 단가'] * df['Demand\n(Vi)'] * df['위도간 거리(Y좌표 거리)']



    def cal_point_result(self, df, point_list, d_count):

        s_df =pd.DataFrame()
        price_list = 150000000
        
        count = len(point_list)
        for i in range(len(point_list)):

            d_s = df[df['선택'] == '거점'+str(i+1)]
            # .(Y-Yi)^2 = 가상 센터에서 거래처 간의 거리
            VRX_Total = d_s['VRX'].sum()
            VRY_Total = d_s['VRY'].sum()
            VR_Total = d_s['VR'].sum()
            # VRX_SUM = d_3['VRX'].SUM()
            # VR_SUM = d_3['VR'].SUM()
            d_s['가상 거점_x'] = VRX_Total / VR_Total
            d_s['가상 거점_y'] = VRY_Total / VR_Total
            d_s['가상 거점_x(곡률값)'] = d_s['가상 거점_x'] / 0.0306 + d_s['경도간 거리(기준)_곡률값']
            d_s['가상 거점_y(곡률값)'] = d_s['가상 거점_y'] / 0.0245 + d_s['위도간 거리(기준)_곡률값']

            
            if( count > d_count):
                d_s['위경도 좌표_x'] = point_list[i][1]/3600
                d_s['위경도 좌표_y'] = point_list[i][0]/3600
            else:
                d_s['위경도 좌표_x'] = d_s['가상 거점_x(곡률값)']/3600
                d_s['위경도 좌표_y'] = d_s['가상 거점_y(곡률값)']/3600

            
            
            
            
            d_s['거래처수'] = d_s['선택'].count()

            # (Y-Yi)^2 = 가상 센터에서 거래처 간의 거리
            d_s['(Y-Yi)^2'] = (d_s['위도간 거리(Y좌표 거리)'] - d_s['가상 거점_y']) ** 2
            # (X-Xi)^2 = 가상 센터에서 거래처 간의 거리
            d_s['(X-Xi)^2'] = (d_s['경도간 거리(X좌표 거리)'] - d_s['가상 거점_x']) ** 2
            d_s['(Y-Yi)^2 + (X-Xi)^2'] = np.sqrt(d_s['(X-Xi)^2'] + d_s['(Y-Yi)^2'])
            d_s['X_곡률걊'] = d_s['가상 거점_x'] / 0.0306 + d_s['경도간 거리(기준)_곡률값']
            d_s['Y_곡률걊'] = d_s['가상 거점_y'] / 0.0245 + d_s['위도간 거리(기준)_곡률값']

            d_s['경도 좌표_X'] = d_s['X_곡률걊'] / 3600
            d_s['위도 좌표_Y'] = d_s['Y_곡률걊'] / 3600
            d_s['TC'] = d_s['VR'] * d_s['(Y-Yi)^2 + (X-Xi)^2']
            d_s['Transport Cost'] = d_s['TC'].sum()
            b = d_s['Demand\n(Vi)'].sum()
            d_s['총수량'] = int(b)

            s_df =pd.concat([s_df, d_s])

            d_s.to_csv("../result/총_" +str(len(point_list)) +"_거점별_데이터_"+str(i+1)+"번째 거점.csv", encoding='cp949')
            
            count-=1
            

        s_df.to_excel('../result/거점_'+ str(len(point_list))+'_시뮬레시션_raw(전주공장픽스).xlsx')

        s_df = s_df.loc[:, ['위경도 좌표_y', '위경도 좌표_x', '거래처수', '총수량', 'Transport Cost']]

        
        s_df = s_df.drop_duplicates()
        s_df = s_df.reset_index(drop=False)


        s_df['Warehous_Cost'] = price_list
        s_df['Total Cost'] = s_df['Transport Cost'] + s_df['Warehous_Cost'] * np.sqrt(1)

        return s_df


