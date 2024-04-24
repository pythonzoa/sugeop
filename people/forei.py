from pykrx import stock
import pandas as pd

pd.set_option('display.max_rows', None)  # 표시할 최대 행 수
pd.set_option('display.max_columns', None)  # 표시할 최대 열 수
pd.set_option('display.width', None)  # 한 줄에 출력할 최대 문자 수
pd.set_option('display.max_colwidth', None)  # 열 너비

# 전체 종목 순매수대금
df = stock.get_market_net_purchases_of_equities("20210115", "20210122")
print(df.head())

df2 = stock.get_market_trading_volume_by_date("20210115", "20210122", "005930")
print(df2.head())

df3 = stock.get_market_trading_volume_by_date("20210115", "20210122", "005930", detail=True)
print(df3.head())

df4 = stock.get_market_trading_value_by_date("20210115", "20210122", "005930")
print(df4.head())

df5 = stock.get_market_trading_value_by_date("20210115", "20210122", "005930", detail=True)
print(df5.head())