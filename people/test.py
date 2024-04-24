from pykrx import stock

# 날짜 범위 설정
start_date = "20210115"
end_date = "20210122"

# 개인 투자자와 기관 합계 투자자의 유형 리스트
investor_types = ['개인', '기관합계',"외국인"]
# 금융투자 / 보험 / 투신 / 사모 / 은행 / 기타금융 / 연기금 / 기관합계 / 기타법인 / 개인 / 외국인 / 기타외국인 / 전체

for investor_type in investor_types:
    # 해당 유형의 데이터 가져오기
    df = stock.get_market_net_purchases_of_equities(start_date, end_date, investor=investor_type)
    df_result = df[['종목명', '순매수거래대금']]
    df_result['순매수거래대금'] = df_result['순매수거래대금'].astype(int)/10
    # 변경된 데이터프레임 출력
    print(f"{investor_type}(단위 : 억):\n{df_result}")

    # 데이터 간 구분을 위한 공백 출력
    print()