import numpy as np
import pandas as pd
import io
import itertools
from google.colab import files
import matplotlib.pyplot as plt
import seaborn as sns

class ABC_analysis:
  def __init__(self, url, string_type, myfile):
    self.url = url
    self.string_type = string_type
    self.myfile = myfile
  
  def load_data(self): 
    df = pd.DataFrame()

    if self.string_type == "stock":
      try: 
        df = pd.read_excel(io.BytesIO(self.myfile[self.url]))
      except:
        df = pd.read_excel('/content/logistic/재고_DATA.xlsx')


    if self.string_type == "release":
      try: 
        df = pd.read_excel(io.BytesIO(self.myfile[self.url]))
      except:
        df = pd.read_excel('/content/logistic/출고_DATA.xlsx')


    if self.string_type == "order":
      try: 
        df = pd.read_excel(io.BytesIO(self.myfile[self.url]))
      except:
        df = pd.read_excel('/content/logistic/주문_DATA.xlsx')


    return df


  def sum_and_sort_data(self, df):
    if self.string_type == "stock":
      #내림차순
      df = df.sort_values(by='일평균 재고수량',ascending=False)
      #'일평균 재고수량'의 합계
      Total = df['일평균 재고수량'].sum()

      #df['비율(%)'] = df['일평균 재고수량']/'Total'
      df['비율'] = df['일평균 재고수량']/Total

    if self.string_type == "release":
      #내림차순
      df = df.sort_values(by='평균 출고금액',ascending=False)
      Total = df['평균 출고금액'].sum()
      df['비율'] = df['평균 출고금액']/Total
    return df


  def cal_total_rate(self, df):

    df['누계비율'] = list(itertools.accumulate(df['비율']))
    df['누계비율(%)'] = df['누계비율'] * 100.0
    df = df.round(2)

    return df
  
  def func(self, ar) : 
      if ar < 80 : 
          return "A"
      elif ar >= 90: 
          return "C"
      else:
          return "B"

  def cal_ABC(self, df):
    if self.string_type == "stock":
      df['stock level'] = df['누계비율(%)'].apply(self.func)

    if self.string_type == "release":
      df['release level'] = df['누계비율(%)'].apply(self.func)
    return df

  def pivot_data(self, df):

    if self.string_type == "stock":
      df_pivot = pd.pivot_table(df, columns = ['stock level'], values = ['코드'],aggfunc =['count'])

    if self.string_type == "release":
      df = df.groupby(['release level'])[['release level']].count()
      df_pivot = df.transpose()

    return df_pivot

  def join_data(self, stock_df, release_df):
    df_join = stock_df.join(release_df.set_index('코드')['release level'], on='코드')
    return df_join

  def wanted_data(self, df):
    df = df.loc[:,['코드', '단위','stock level', 'release level']]
    return df

  def final_pivot_data(self, df):
    df_1 = pd.pivot_table(df, index = ['stock level'], columns = ['release level'], values = ['코드'],aggfunc =['count'])
    df_1_p = df_1.rename(columns={'코드':'code'})

    df_1_p = df_1_p.reset_index()

    return df_1_p
