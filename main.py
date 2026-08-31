import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(
    page_title="서울 연평균 기온 변화",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 서울의 연평균 기온 변화")
st.write("서울의 기온 데이터를 이용해 약 100년 동안 연평균 기온이 어떻게 변해왔는지 살펴봅니다.")

# 데이터 주소
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"


# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL, encoding="utf-8")

    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")
    df["평균기온"] = pd.to_numeric(df["평균기온"], errors="coerce")

    df = df.dropna(subset=["날짜", "평균기온"])

    return df


try:
    df = load_data()

    # 연도 추출
    df["연도"] = df["날짜"].dt.year

    # 연도별 평균기온 계산
    yearly_temp = (
        df.groupby("연도")["평균기온"]
        .mean()
        .reset_index()
    )

    # 연도순 정렬
    yearly_temp = yearly_temp.sort_values("연도")

    # -----------------------------------------
    # 중요!
    # 데이터가 없는 연도도 포함시키고
    # 해당 연도의 기온을 NaN으로 설정
    # -----------------------------------------

    start_year = int(yearly_temp["연도"].min())
    end_year = int(yearly_temp["연도"].max())

    all_years = pd.DataFrame({
        "연도": range(start_year, end_year + 1)
    })

    yearly_temp = all_years.merge(
        yearly_temp,
        on="연도",
        how="left"
    )

    # 연도를 인덱스로 설정
    chart_data = yearly_temp.set_index("연도")

    # 기본 정보
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "데이터 시작 연도",
            f"{start_year}년"
        )

    with col2:
        st.metric(
            "데이터 마지막 연도",
            f"{end_year}년"
        )

    with col3:
        st.metric(
            "연평균 기온 최고값",
            f"{yearly_temp['평균기온'].max():.1f}℃"
        )

    st.divider()

    # 그래프
    st.subheader("📈 연도별 연평균 기온")

    st.line_chart(
        chart_data,
        y="평균기온",
        x_label="연도",
        y_label="평균기온 (℃)",
        height=500
    )

    st.caption(
        "※ 데이터가 없는 연도는 그래프에서 선이 연결되지 않습니다."
    )

    # 데이터 표
    with st.expander("📋 연도별 기온 데이터 보기"):
        display_data = yearly_temp.copy()
        display_data["평균기온"] = display_data["평균기온"].round(1)
        display_data.columns = ["연도", "연평균 기온 (℃)"]

        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True
        )

except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.info("인터넷 연결 또는 데이터 주소를 확인해주세요.")
    st.code(str(e))
