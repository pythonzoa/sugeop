import pandas as pd
import numpy as np
from pykrx import stock
import matplotlib.pyplot as plt
import FinanceDataReader as fdr
import random

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# 데이터 불러오기
start_date = '20190901'
end_date = '20240427'

# 랜덤으로 30개 종목 선택
krx_list = fdr.StockListing('KRX')
stock_cap = krx_list[krx_list['Marcap'] >= 1e12][['Code', 'Name']]
random_stock_codes = random.sample(stock_cap['Code'].tolist(), 30)

# 데이터프레임 초기화
merged_all_df = pd.DataFrame()

for stock_code in random_stock_codes:
    # KRX 데이터를 통해 외국인 순매수량 가져오기
    df = stock.get_market_trading_value_by_date(start_date, end_date, stock_code)
    df = df.drop(columns=["기타법인", "전체", "개인"])

    # 빈 값을 0으로 대체
    df.replace('', 0, inplace=True)

    # 52주 고점 계산
    df['52w_high'] = df['외국인합계'].rolling(window=240, min_periods=1).max()

    # 신고점 도달일
    df['is_high'] = (df['외국인합계'] == df['52w_high']).astype(int)

    # 주식 가격 데이터 가져오기
    price_df = stock.get_market_ohlcv_by_date(start_date, end_date, stock_code)
    price_df = price_df.drop(columns=['시가', '고가', '저가', '거래량'])

    # 데이터 병합
    merged_df = pd.merge(price_df, df[['외국인합계', 'is_high']], left_index=True, right_index=True, how='left')

    # 투자 전략 시뮬레이션: 매수 후 20일, 60일 후 수익률 계산
    merged_df['return_5'] = merged_df['종가'].shift(-5) / merged_df['종가'] - 1
    merged_df['return_20'] = merged_df['종가'].shift(-20) / merged_df['종가'] - 1
    merged_df['return_60'] = merged_df['종가'].shift(-60) / merged_df['종가'] - 1

    # 종목명 추가
    merged_df['종목명'] = stock_cap[stock_cap['Code'] == stock_code]['Name'].values[0]

    # 데이터프레임 추가
    merged_all_df = pd.concat([merged_all_df, merged_df])

# is_high가 1인 경우 필터링하여 데이터프레임 생성
high_df = merged_all_df[merged_all_df['is_high'] == 1]

# 필요한 컬럼만 선택하여 엑셀 파일로 저장
output_df = high_df[['종목명', 'return_5', 'return_20', 'return_60']]
output_df.to_excel('high_returns_all.xlsx', index=True)