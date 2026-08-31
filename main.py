import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(
    page_title="서울 연평균 기온 변화",
    page_icon="🌡️",
    layout="wide"
)

# 데이터 주소
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"


@st.cache_data
def load_data():
    """서울 기온 데이터를 불러오고 연도별 평균기온을 계산합니다."""
    df = pd.read_csv(DATA_URL, encoding="utf-8-sig")

    # 날짜 변환
    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")

    # 평균기온 숫자형 변환
    df["평균기온"] = pd.to_numeric(df["평균기온"], errors="coerce")

    # 날짜와 평균기온이 없는 행 제거
    df = df.dropna(subset=["날짜", "평균기온"])

    # 연도별 평균기온 계산
    df["연도"] = df["날짜"].dt.year

    yearly = (
        df.groupby("연도", as_index=False)["평균기온"]
        .mean()
        .rename(columns={"평균기온": "연평균기온"})
    )

    return yearly


# 데이터 불러오기
try:
    yearly = load_data()
except Exception as e:
    st.error("기온 데이터를 불러오는 중 문제가 발생했습니다.")
    st.exception(e)
    st.stop()


# 제목
st.title("🌡️ 서울의 100년간 연평균 기온 변화")

st.markdown(
    "서울의 일별 평균기온 데이터를 연도별로 평균하여 "
    "장기간에 걸친 기온 변화를 살펴봅니다."
)

# 전체 기간
start_year = int(yearly["연도"].min())
end_year = int(yearly["연도"].max())

# 100년 범위 선택
st.sidebar.header("📊 그래프 설정")

default_start = max(start_year, end_year - 99)

start_year_selected, end_year_selected = st.sidebar.slider(
    "조회 기간",
    min_value=start_year,
    max_value=end_year,
    value=(default_start, end_year),
    step=1
)

# 선택 기간 데이터
chart_data = yearly[
    (yearly["연도"] >= start_year_selected)
    & (yearly["연도"] <= end_year_selected)
].copy()

# 연도별 기온 그래프
st.subheader(
    f"{start_year_selected}년 ~ {end_year_selected}년 연평균 기온"
)

st.line_chart(
    chart_data.set_index("연도")["연평균기온"],
    y_label="연평균 기온 (℃)",
    x_label="연도",
    use_container_width=True,
)

# 요약 정보
st.subheader("📌 기간 요약")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "조회 시작 연도",
        f"{start_year_selected}년"
    )

with col2:
    st.metric(
        "조회 종료 연도",
        f"{end_year_selected}년"
    )

with col3:
    temperature_change = (
        chart_data.iloc[-1]["연평균기온"]
        - chart_data.iloc[0]["연평균기온"]
    )

    st.metric(
        "시작 대비 변화",
        f"{temperature_change:+.1f}℃"
    )

# 데이터 표
with st.expander("연도별 연평균 기온 데이터 보기"):
    display_data = chart_data.copy()
    display_data["연평균기온"] = display_data["연평균기온"].round(2)

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )

st.caption(
    "자료: 제공된 서울 기온 데이터(seoul.csv) · 연평균 기온은 일별 평균기온의 연도별 평균입니다."
)
