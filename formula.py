from pykrx import stock

# 날짜 범위 설정
start_date = "20210115"
end_date = "20210122"

# 월별로 가져오기 (일 : "d", 년 : "y")
df = stock.get_market_ohlcv_by_date("20220420", "20220610", "005930", "m")
print(df.head())

# 전체 종목의 펀더멘탈 지표(PER, PBR, EPS, BPS, DIV, DPS) 가져오기
df = stock.get_market_fundamental_by_ticker(date='20220617', market="ALL")
print(df.head())

# 투자자별 일자별 거래실적
# 투자자 :금융투자 / 보험 / 투신 / 사모 / 은행 / 기타금융 / 연기금 / 기관합계 / 기타법인 / 개인 / 외국인 / 기타외국인 / 전체
df = stock.get_market_trading_value_by_date("20210115", "20210122","005930",detail=True)
print(df.head())

# 종목별 공매도 현황
df = stock.get_shorting_status_by_date("20181210", "20181212", "005930")
print(df)

# 기업정보 API
df = stock.get_stock_major_changes("005930")
print(df.head())