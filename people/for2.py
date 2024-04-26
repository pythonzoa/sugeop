import numpy as np
import pandas as pd
from pykrx import stock
import FinanceDataReader as fdr
import yfinance
import matplotlib.pyplot as plt

# pandas 설정: 최대 행, 열 출력 설정
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# 날짜 범위 설정
start_date = "20211031"
end_date = "20231231"
stock_code = "005930"

df = stock.get_market_trading_value_by_date(start_date, end_date, stock_code, detail=False)
df = df.drop(columns=['전체']).copy()
df = df.astype(float)/100000000
df = df.astype(int)

for column in df.columns:
    high_col_name = f'{column}_52_high'
    is_high_col_name = f'is_{column}_52_high'
    low_col_name = f'{column}_52_low'
    is_low_col_name = f'is_{column}_52_low'

    df[high_col_name] = df[column].rolling(window=240,min_periods=1).max()
    df[is_high_col_name] = np.where((df[column]==df[high_col_name]) & (df[high_col_name] > 0),1,'')

    df[low_col_name] = df[column].rolling(window=240, min_periods=1).min()
    df[is_low_col_name] = np.where((df[column] == df[low_col_name]) & (df[low_col_name] < 0), -1, '')

df = pd.DataFrame(df)
print(df.head())

df_stock = fdr.DataReader(stock_code,start_date,end_date)
df_stock = pd.DataFrame(df_stock)
print(df_stock.head())

merge_df = pd.merge(df_stock[['Close','Change']],df,left_index=True,right_index=True,how='left')
print(merge_df.head())

plt_df = merge_df.loc["2022-12-31","2023-12-31"].copy()

# 선 그래프 생성
plt.figure(figsize=(10, 5))
plt.plot(plt_df['Close'], label='Close Price')

# 'is_high'가 1인 지점에 빨간 점 표시
plt_df['is_외국인합계_52_high'] = pd.to_numeric(plt_df['is_외국인합계_52_high'], errors='coerce')
high_points = plt_df[plt_df['is_외국인합계_52_high'] == 1]
plt.scatter(high_points.index, high_points['Close'], color='red', s=50, label='High Points')

# 'is_low'가 -1인 지점에 파란 점 표시
plt_df['is_외국인합계_52_low'] = pd.to_numeric(plt_df['is_외국인합계_52_low'], errors='coerce')
low_points = plt_df[plt_df['is_외국인합계_52_low'] == -1]
plt.scatter(low_points.index, low_points['Close'], color='blue', s=50, label='Low Points')

# 그래프 제목 및 레이블 설정
plt.title('Close Price Chart with High and Low Points')
plt.xlabel('Time')
plt.ylabel('Close Price')
plt.legend()

# 그래프 표시
plt.savefig()
plt.show()

###################################
# ## KRX 상장 회사 목록을 불러옴
# krx_list = fdr.StockListing('KRX')
#
# # 시가총액 기준 필터링 조건 적용
# kospi_tickers = krx_list[(krx_list['Market'] == 'KOSPI') & (krx_list['Marcap'] >= 5e12)]['Code'].tolist()
# kosdaq_tickers = krx_list[(krx_list['Market'] == 'KOSDAQ') & (krx_list['Marcap'] >= 0.8e12)]['Code'].tolist()
#
# print(len(kospi_tickers))
# print(len(kosdaq_tickers))
###################################

