import numpy as np
import pandas as pd
from pykrx import stock
import FinanceDataReader as fdr
import yfinance

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

    df[high_col_name] = df[column].rolling(window=240,min_periods=1).max()
    df[is_high_col_name] = np.where((df[column]==df[high_col_name]) & (df[high_col_name] > 0),0,'')

print(df.head())

df_stock = fdr.DataReader(stock_code,start_date,end_date)
print(df_stock.head())

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

