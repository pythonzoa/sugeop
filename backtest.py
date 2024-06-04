import pandas as pd
import numpy as np
from pykrx import stock
import FinanceDataReader as fdr
import datetime

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

pd.set_option('display.max_colwidth', None)

# 데이터 불러오기
start_date = '20120901'
end_date = '20241231'

print("데이터 불러오는 중...")
# KRX 리스트 가져오기
krx_list = fdr.StockListing('KRX')
kospi_list = fdr.StockListing('KOSPI')[['Code', 'Name']]
kosdaq_list = fdr.StockListing('KOSDAQ')[['Code', 'Name']]
print("데이터 불러오기 완료.")

# 코스피, 코스닥 구분
print("코스피와 코스닥 구분 중...")
krx_list['Market'] = np.where(krx_list['Code'].isin(kospi_list['Code']), 'KOSPI',
                              np.where(krx_list['Code'].isin(kosdaq_list['Code']), 'KOSDAQ', 'Unknown'))
print("코스피와 코스닥 구분 완료.")

# 데이터프레임 초기화
kospi_results = []
kosdaq_results = []


# 함수 정의
def process_market_data(stock_cap, market_name):
    results = []
    random_stock_codes = stock_cap['Code'].tolist()

    print(f"{market_name} 데이터 처리 시작. 종목 수: {len(random_stock_codes)}")
    # 구간별 데이터프레임 초기화
    merged_all_df = pd.DataFrame()

    for stock_code in random_stock_codes:
        try:
            print(f"{stock_code} 데이터 처리 중...")
            # KRX 데이터를 통해 외국인합계 순매수량 가져오기
            df = stock.get_market_trading_value_by_date(start_date, end_date, stock_code)
            df['시가총액'] = stock.get_market_cap_by_date(start_date, end_date, stock_code)['시가총액']
            columns_to_drop = ["기타법인", "전체", "개인"]
            df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])
            df.replace('', 0, inplace=True)

            if '외국인합계' in df.columns:
                df['52w_high'] = df['외국인합계'].rolling(window=224, min_periods=1).max()
                df['52w_high'] = df['52w_high'].apply(lambda x: x if x > 0 else None)
                df['is_high'] = (df['외국인합계'] == df['52w_high']).astype(int)
            else:
                print(f"'외국인합계' 열이 {stock_code} 데이터프레임에 존재하지 않습니다.")
                df['is_high'] = 0
                df['외국인합계'] = 0

            price_df = stock.get_market_ohlcv_by_date(start_date, end_date, stock_code)
            price_df = price_df.drop(columns=['시가', '고가', '저가', '거래량'])

            merged_df = pd.merge(price_df, df[['외국인합계', 'is_high', '시가총액']], left_index=True, right_index=True,
                                 how='left')
            merged_df['return_5'] = merged_df['종가'].shift(-5).rolling(window=5).mean() / merged_df['종가'] - 1
            merged_df['return_20'] = merged_df['종가'].shift(-20).rolling(window=20).mean() / merged_df['종가'] - 1
            merged_df['return_60'] = merged_df['종가'].shift(-60).rolling(window=60).mean() / merged_df['종가'] - 1
            merged_df['종목명'] = stock_cap[stock_cap['Code'] == stock_code]['Name'].values[0]
            merged_df['Market'] = stock_cap[stock_cap['Code'] == stock_code]['Market'].values[0]

            merged_all_df = pd.concat([merged_all_df, merged_df])
        except Exception as e:
            print(f"Error processing {stock_code}: {e}")

    if 'is_high' in merged_all_df.columns:
        # is_high가 1인 경우 필터링하여 데이터프레임 생성
        high_df = merged_all_df[merged_all_df['is_high'] == 1]
        if market_name == '코스피':
            high_df = high_df[high_df['시가총액'] >= 2e12]
            high_df['시가총액_구간'] = pd.qcut(high_df['시가총액'], 10, labels=[f'{i+1}구간' for i in range(10)])
        elif market_name == '코스닥':
            high_df = high_df[high_df['시가총액'] >= 5e11]
            high_df['시가총액_구간'] = pd.qcut(high_df['시가총액'], 10, labels=[f'{i+1}구간' for i in range(10)])

        output_df = high_df[['종목명', 'Market', 'return_5', 'return_20', 'return_60', '시가총액', '시가총액_구간']]
        results.append(output_df)
        print(f"{market_name} 데이터 처리 완료.")
    else:
        print(f"'is_high' 컬럼이 존재하지 않습니다.")

    return results


# 코스피와 코스닥 데이터 처리
def get_market_data(market, threshold):
    market_cap = krx_list[(krx_list['Market'] == market) & (krx_list['Marcap'] >= threshold)]
    return market_cap


print("코스피 데이터 가져오는 중...")
kospi_stock_cap = get_market_data('KOSPI', 2e11)
print("코스닥 데이터 가져오는 중...")
kosdaq_stock_cap = get_market_data('KOSDAQ', 2e11)

# 데이터 처리
kospi_results = process_market_data(kospi_stock_cap, "코스피")
kosdaq_results = process_market_data(kosdaq_stock_cap, "코스닥")

# 결과 합치기
if kospi_results:
    kospi_final_df = pd.concat(kospi_results)

if kosdaq_results:
    kosdaq_final_df = pd.concat(kosdaq_results)

# 결과 출력 및 저장
today = datetime.today().strftime('%Y%m%d')
print("결과를 엑셀 파일로 저장하는 중...")
with pd.ExcelWriter(f'stockfore{today}.xlsx') as writer:
    if kospi_results:
        kospi_final_df.to_excel(writer, sheet_name='KOSPI', index=True)
    if kosdaq_results:
        kosdaq_final_df.to_excel(writer, sheet_name='KOSDAQ', index=True)
print("엑셀 파일 저장 완료.")
