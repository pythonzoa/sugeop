from pykrx import stock
import pandas as pd

pd.set_option('display.max_rows', None)  # 표시할 최대 행 수
pd.set_option('display.max_columns', None)  # 표시할 최대 열 수
pd.set_option('display.width', None)  # 한 줄에 출력할 최대 문자 수
pd.set_option('display.max_colwidth', None)  # 열 너비

#지정된 기간 동안의 전체 주식 종목에 대한 순매수 대금을 조회
df = stock.get_market_net_purchases_of_equities("20210115", "20210122")
print(df.head())

#특정 종목의 일별 거래량을 조회
df2 = stock.get_market_trading_volume_by_date("20210115", "20210122", "005930")
print(df2.head())

#특정 종목의 일별 거래량을 보다 상세히 조회
df3 = stock.get_market_trading_volume_by_date("20210115", "20210122", "005930", detail=True)
print(df3.head())

#특정 종목의 일별 거래 대금
df4 = stock.get_market_trading_value_by_date("20210115", "20210122", "005930")
print(df4.head())

#특정 종목의 일별 거래 대금을 상세히 조회
df5 = stock.get_market_trading_value_by_date("20210115", "20210122", "005930", detail=True)
print(df5.head())
