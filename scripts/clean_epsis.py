"""EPSIS 월별 연료원별 표를 한 줄 머리글 · UTF-8 · 오래된 달부터로 바꿔 둔다.

원자료(data/raw/epsis_fuel_monthly.csv)는 그대로 두고 읽기만 한다.
원자료의 문제 셋 — (1) cp949라 편집기에서 글자가 깨진다 (2) 머리글이 두 줄로
쪼개져 있어 열 이름이 데이터와 안 맞는다 (3) 최신 달이 맨 위다.
결과: data/interim/epsis_fuel_monthly.csv
"""
import os
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data", "raw", "epsis_fuel_monthly.csv")
DST = os.path.join(ROOT, "data", "interim", "epsis_fuel_monthly.csv")

# 두 줄짜리 머리글(대분류 + 중분류)을 한 줄 이름으로 펼친 것
COLS = ["기간", "원자력", "유연탄", "무연탄", "석탄계", "유류", "LNG", "양수",
        "연료전지", "석탄가스화", "태양", "풍력", "수력", "해양", "바이오", "폐기물",
        "신재생계", "기타", "전력시장계", "PPA계", "합계"]

ep = pd.read_csv(SRC, encoding="cp949", skiprows=2, header=None, names=COLS)
ep["기간"] = pd.to_datetime(ep["기간"], format="%Y/%m").dt.strftime("%Y-%m")
ep = ep.sort_values("기간").reset_index(drop=True)          # 오래된 달부터

# 열 이름이 제자리인지 — 합계 항등식 셋으로 검산한다. 한 칸이라도 밀리면 여기서 걸린다
재생 = ["연료전지", "석탄가스화", "태양", "풍력", "수력", "해양", "바이오", "폐기물"]
시장 = ["원자력", "석탄계", "유류", "LNG", "양수", "신재생계", "기타"]
assert (ep["석탄계"] - ep[["유연탄", "무연탄"]].sum(axis=1)).abs().max() < 1
assert (ep["신재생계"] - ep[재생].sum(axis=1)).abs().max() < 1
assert (ep["전력시장계"] - ep[시장].sum(axis=1)).abs().max() < 1

os.makedirs(os.path.dirname(DST), exist_ok=True)
ep.round(3).to_csv(DST, index=False, encoding="utf-8-sig")  # BOM — 엑셀에서도 안 깨진다
print(f"{DST}\n{len(ep)}행 · {ep['기간'].iloc[0]} ~ {ep['기간'].iloc[-1]} · 열 {len(ep.columns)}개")
