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

    # 순매수 여부 계산 (양수면 1, 아니면 0)
    df['positive_buy'] = (df['외국인합계'] > 0).astype(int)

    # 연속 순매수 일수 계산
    df['continuous_buy_days'] = df['positive_buy'] * (df['positive_buy'].groupby((df['positive_buy'] != df['positive_buy'].shift()).cumsum()).cumcount() + 1)

    # 5일 이상 순매수 후 끊기는 날 찾기
    df['break_days'] = (df['continuous_buy_days'] >= 5) & (df['positive_buy'].shift(-1) == 0)

    # 기준일 설정 및 연속 순매수 일수 표기
    df['buy_days_until_break'] = df['continuous_buy_days'].shift(1).where(df['break_days'])

    # 주식 가격 데이터 가져오기
    price_df = stock.get_market_ohlcv_by_date(start_date, end_date, stock_code)
    price_df = price_df.drop(columns=['시가', '고가', '저가', '거래량'])

    # 데이터 병합
    merged_df = pd.merge(price_df, df[['외국인합계', 'continuous_buy_days','buy_days_until_break']], left_index=True, right_index=True, how='left')

    # 투자 전략 시뮬레이션: 매수 후 20일, 60일 후 수익률 계산
    merged_df['return_5'] = merged_df['종가'].shift(-5) / merged_df['종가'] - 1
    merged_df['return_20'] = merged_df['종가'].shift(-20) / merged_df['종가'] - 1
    merged_df['return_60'] = merged_df['종가'].shift(-60) / merged_df['종가'] - 1

    # 종목명 추가
    merged_df['종목명'] = stock_cap[stock_cap['Code'] == stock_code]['Name'].values[0]

    # 데이터프레임 추가
    merged_all_df = pd.concat([merged_all_df, merged_df])

    # is_continuous_buy가 1인 경우 필터링하여 데이터프레임 생성
    continuous_buy_df = merged_all_df[(merged_all_df['continuous_buy_days'] >= 5) & merged_all_df['buy_days_until_break'] > 0]


# 결과 출력 또는 파일 저장
output_df = continuous_buy_df[['종목명', 'continuous_buy_days', 'return_5', 'return_20', 'return_60']]
output_df.to_excel('continuous_buy_analysis.xlsx', index=True)





