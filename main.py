import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(
    page_title="서울 연평균 기온 변화",
    page_icon="🌡️",
    layout="wide"
)

# 제목
st.title("🌡️ 서울의 연평균 기온 변화")
st.write(
    "서울의 기온 데이터를 이용해 약 100년 동안 "
    "연평균 기온이 어떻게 변해왔는지 살펴봅니다."
)

# 데이터 주소
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"


# 데이터 불러오기
@st.cache_data
def load_data():

    df = pd.read_csv(
        DATA_URL,
        encoding="utf-8"
    )

    # 날짜 변환
    df["날짜"] = pd.to_datetime(
        df["날짜"],
        errors="coerce"
    )

    # 평균기온 숫자로 변환
    df["평균기온"] = pd.to_numeric(
        df["평균기온"],
        errors="coerce"
    )

    # 날짜와 평균기온이 모두 있는 데이터만 사용
    df = df.dropna(
        subset=["날짜", "평균기온"]
    )

    return df


try:

    # 데이터 불러오기
    df = load_data()

    # 연도 추출
    df["연도"] = df["날짜"].dt.year

    # --------------------------------------
    # 연도별 평균기온 계산
    # --------------------------------------
    yearly_temp = (
        df.groupby("연도")["평균기온"]
        .mean()
        .reset_index()
    )

    # 연도순 정렬
    yearly_temp = yearly_temp.sort_values("연도")

    # --------------------------------------
    # 데이터가 실제로 존재하는 연도만 사용
    # --------------------------------------
    yearly_temp["평균기온"] = pd.to_numeric(
        yearly_temp["평균기온"],
        errors="coerce"
    )

    yearly_temp = yearly_temp.dropna(
        subset=["평균기온"]
    )

    # --------------------------------------
    # 상단 정보
    # --------------------------------------
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "데이터 시작 연도",
            f"{int(yearly_temp['연도'].min())}년"
        )

    with col2:
        st.metric(
            "데이터 마지막 연도",
            f"{int(yearly_temp['연도'].max())}년"
        )

    with col3:
        st.metric(
            "연평균 기온 최고값",
            f"{yearly_temp['평균기온'].max():.1f}℃"
        )

    st.divider()

    # --------------------------------------
    # 그래프
    # --------------------------------------
    st.subheader("📈 연도별 연평균 기온")

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=yearly_temp["연도"],
            y=yearly_temp["평균기온"],
            mode="lines+markers",
            name="연평균 기온",

            # 없는 데이터를 임의로 연결하지 않음
            connectgaps=False,

            hovertemplate=(
                "연도 %{x}년<br>"
                "평균기온 %{y:.1f}℃"
                "<extra></extra>"
            )
        )
    )

    fig.update_layout(
        xaxis_title="연도",
        yaxis_title="평균기온 (℃)",

        height=500,

        hovermode="x",

        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.caption(
        "※ 기온 데이터가 없는 연도는 그래프에서 제외했습니다."
    )

    # --------------------------------------
    # 데이터 표
    # --------------------------------------
    with st.expander("📋 연도별 기온 데이터 보기"):

        display_data = yearly_temp.copy()

        display_data["평균기온"] = display_data[
            "평균기온"
        ].round(1)

        display_data.columns = [
            "연도",
            "연평균 기온 (℃)"
        ]

        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True
        )


except Exception as e:

    st.error(
        "데이터를 불러오는 중 문제가 발생했습니다."
    )

    st.info(
        "인터넷 연결 또는 데이터 주소를 확인해주세요."
    )

    st.code(str(e))
