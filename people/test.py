import numpy as np
import pandas as pd
from pykrx import stock
import FinanceDataReader as fdr
import matplotlib.pyplot as plt
from adjustText import adjust_text
import os

# pandas 설정: 최대 행, 열 출력 설정
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# 날짜 범위 및 종목 코드 설정
start_date = "20211031"
end_date = "20240426"
stock_code = "012450"

def calculate_returns(df, days):
    return df['Close'].shift(-days) / df['Close'] - 1

# 주식 거래 데이터 가져오기
df = stock.get_market_trading_value_by_date(start_date, end_date, stock_code, detail=False)
df = df.drop(columns=['전체']).copy()
df = df.astype(float) / 100000000  # 백만원 단위로 변환
df = df.astype(int)  # 정수형 변환

print(df)

# 52주 고점 및 저점 계산
for column in df.columns:
    high_col_name = f'{column}_52_high'
    is_high_col_name = f'is_{column}_52_high'
    low_col_name = f'{column}_52_low'
    is_low_col_name = f'is_{column}_52_low'

    df[high_col_name] = df[column].rolling(window=240, min_periods=1).max()
    df[is_high_col_name] = np.where((df[column] == df[high_col_name]) & (df[high_col_name] > 0), 1, '')

    df[low_col_name] = df[column].rolling(window=240, min_periods=1).min()
    df[is_low_col_name] = np.where((df[column] == df[low_col_name]) & (df[low_col_name] < 0), -1, '')


# FinanceDataReader를 사용하여 종가 및 변동률 데이터 가져오기
df_stock = fdr.DataReader(stock_code, start_date, end_date)

# 데이터 병합
merge_df = pd.merge(df_stock[['Close', 'Change']], df, left_index=True, right_index=True, how='left')

# 고점과 저점의 인덱스
merge_df['is_외국인합계_52_high'] = pd.to_numeric(merge_df['is_외국인합계_52_high'], errors='coerce')
merge_df['is_외국인합계_52_low'] = pd.to_numeric(merge_df['is_외국인합계_52_low'], errors='coerce')
high_indices = merge_df[merge_df['is_외국인합계_52_high'] == 1].index
low_indices = merge_df[merge_df['is_외국인합계_52_low'] == -1].index


# 수익률 열 초기화
merge_df['Return_5_high'] = np.nan
merge_df['Return_20_high'] = np.nan
merge_df['Return_60_high'] = np.nan
merge_df['Return_5_low'] = np.nan
merge_df['Return_20_low'] = np.nan
merge_df['Return_60_low'] = np.nan

# 고점과 저점에서의 수익률 계산
merge_df.loc[high_indices, 'Return_5_high'] = calculate_returns(merge_df, 5)
merge_df.loc[high_indices, 'Return_20_high'] = calculate_returns(merge_df, 20)
merge_df.loc[high_indices, 'Return_60_high'] = calculate_returns(merge_df, 60)
merge_df.loc[low_indices, 'Return_5_low'] = calculate_returns(merge_df, 5)
merge_df.loc[low_indices, 'Return_20_low'] = calculate_returns(merge_df, 20)
merge_df.loc[low_indices, 'Return_60_low'] = calculate_returns(merge_df, 60)

# print(merge_df)
# merge_df.to_excel('output.xlsx', index=False)

plt.figure(figsize=(12, 6))
plt.plot(merge_df['Close'], label='종가')  # 종가 선 그래프
plt.scatter(high_indices, merge_df.loc[high_indices, 'Close'], color='red', s=50, label='고점')
plt.scatter(low_indices, merge_df.loc[low_indices, 'Close'], color='blue', s=50, label='저점')

texts = []
# 고점에 대한 주석 추가
for idx in high_indices:
    text = f'5d: {merge_df.loc[idx, "Return_5_high"]:.2%}\n20d: {merge_df.loc[idx, "Return_20_high"]:.2%}\n60d: {merge_df.loc[idx, "Return_60_high"]:.2%}'
    texts.append(plt.text(idx, merge_df.loc[idx, 'Close'], text, ha='center', color='black'))

# 저점에 대한 주석 추가
for idx in low_indices:
    text = f'5d: {merge_df.loc[idx, "Return_5_low"]:.2%}\n20d: {merge_df.loc[idx, "Return_20_low"]:.2%}\n60d: {merge_df.loc[idx, "Return_60_low"]:.2%}'
    texts.append(plt.text(idx, merge_df.loc[idx, 'Close'], text, ha='center', color='black'))

adjust_text(texts, arrowprops=dict(arrowstyle='->', color='gray'))

plt.title('종가 차트 및 고점 및 저점의 수익률')
plt.xlabel('시간')
plt.ylabel('종가')
plt.legend()
plt.show()
