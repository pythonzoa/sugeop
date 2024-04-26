import pandas as pd
import numpy as np
from pykrx import stock
import matplotlib.pyplot as plt

# 데이터 불러오기
start_date = '20200101'
end_date = '20231231'
stock_code = '005930'  # 예: 삼성전자

# KRX 데이터를 통해 외국인 순매수량 가져오기
df = stock.get_market_trading_value_by_date(start_date, end_date, stock_code)
df = df.drop(columns=["기타법인","전체","개인",])
# 52주 고점 계산
df['52w_high'] = df['외국인합계'].rolling(window=240, min_periods=1).max()

# 신고점 도달일
df['is_high'] = (df['외국인합계'] == df['52w_high']).astype(int)


# 주식 가격 데이터 가져오기
price_df = stock.get_market_ohlcv_by_date(start_date, end_date, stock_code)
price_df = price_df.drop(columns=['시가','고가','저가','거래량'])

# 데이터 병합
merged_df = pd.merge(price_df, df[['외국인합계', 'is_high']], left_index=True, right_index=True, how='left')

# 투자 전략 시뮬레이션: 매수 후 20일, 60일 후 수익률 계산
merged_df['return_5'] = merged_df['종가'].shift(-5) / merged_df['종가'] - 1
merged_df['return_20'] = merged_df['종가'].shift(-20) / merged_df['종가'] - 1
merged_df['return_60'] = merged_df['종가'].shift(-60) / merged_df['종가'] - 1

print(merged_df)