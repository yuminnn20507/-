import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(
    page_title="서울 연평균 기온 변화",
    page_icon="🌡️",
    layout="wide"
)

st.title("📈 연도별 연평균 기온")
st.write("서울의 연평균 기온 변화를 확인해보세요.")

# 데이터 주소
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"


# -----------------------------
# 데이터 불러오기
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL, encoding="utf-8-sig")

    # 날짜 변환
    df["날짜"] = pd.to_datetime(
        df["날짜"],
        errors="coerce"
    )

    # 평균기온을 숫자로 변환
    df["평균기온"] = pd.to_numeric(
        df["평균기온"],
        errors="coerce"
    )

    # 날짜와 기온이 모두 정상인 데이터만 사용
    df = df.dropna(
        subset=["날짜", "평균기온"]
    )

    # 연도 만들기
    df["연도"] = df["날짜"].dt.year

    return df


# -----------------------------
# 데이터 처리
# -----------------------------
try:
    df = load_data()

    # 연도별 유효한 데이터 개수
    yearly_count = (
        df.groupby("연도")["평균기온"]
        .count()
        .reset_index(name="데이터수")
    )

    # 연도별 평균기온
    yearly_temp = (
        df.groupby("연도")["평균기온"]
        .mean()
        .reset_index()
    )

    # 데이터 개수 합치기
    yearly_temp = yearly_temp.merge(
        yearly_count,
        on="연도",
        how="left"
    )

    # --------------------------------
    # 데이터가 부족한 연도는 비우기
    # --------------------------------
    # 1년 데이터가 최소 300일 이상 있는 경우만
    # 연평균 기온으로 인정
    MIN_DAYS = 300

    yearly_temp.loc[
        yearly_temp["데이터수"] < MIN_DAYS,
        "평균기온"
    ] = None

    yearly_temp = yearly_temp.sort_values("연도")

    # 데이터가 존재하는 연도 범위
    valid_years = yearly_temp[
        yearly_temp["평균기온"].notna()
    ]

    # -----------------------------
    # 상단 정보
    # -----------------------------
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "데이터 시작 연도",
            f"{int(valid_years['연도'].min())}년"
        )

    with col2:
        st.metric(
            "데이터 마지막 연도",
            f"{int(valid_years['연도'].max())}년"
        )

    with col3:
        st.metric(
            "가장 높은 연평균 기온",
            f"{valid_years['평균기온'].max():.1f}℃"
        )

    st.divider()

    # -----------------------------
    # 그래프
    # -----------------------------
    st.subheader("🌡️ 서울 연도별 연평균 기온")

    fig = go.Figure()

    # 모든 연도를 순서대로 확인하면서
    # 데이터가 끊긴 곳에서는 선을 새로 시작
    segment_years = []
    segment_temps = []

    for _, row in yearly_temp.iterrows():

        year = int(row["연도"])
        temp = row["평균기온"]

        # 데이터가 없는 연도
        if pd.isna(temp):

            # 지금까지의 선이 있으면 추가
            if segment_years:
                fig.add_trace(
                    go.Scatter(
                        x=segment_years,
                        y=segment_temps,
                        mode="lines+markers",
                        name="연평균 기온",
                        showlegend=False,
                        hovertemplate=(
                            "연도 %{x}년<br>"
                            "평균기온 %{y:.1f}℃"
                            "<extra></extra>"
                        )
                    )
                )

                segment_years = []
                segment_temps = []

        # 데이터가 충분한 연도
        else:
            segment_years.append(year)
            segment_temps.append(float(temp))

    # 마지막 구간 추가
    if segment_years:
        fig.add_trace(
           go.Scatter(
    x=segment_years,
    y=segment_temps,
    mode="lines+markers",
    line=dict(color="#0066CC"),
    marker=dict(color="#0066CC"),
                name="연평균 기온",
                showlegend=False,
                hovertemplate=(
                    "연도 %{x}년<br>"
                    "평균기온 %{y:.1f}℃"
                    "<extra></extra>"
                )
            )
        )

    # 그래프 설정
    fig.update_layout(
        xaxis_title="연도",
        yaxis_title="평균기온 (℃)",
        height=500,
        hovermode="x unified",
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
        "※ 연평균 기온은 유효한 기온 데이터가 300일 이상인 연도만 표시합니다. "
        "데이터가 없거나 부족한 연도는 그래프에서 비워둡니다."
    )

    # -----------------------------
    # 데이터 표
    # -----------------------------
    with st.expander("📋 연도별 데이터 보기"):

        display_data = yearly_temp.copy()

        display_data["평균기온"] = display_data[
            "평균기온"
        ].round(1)

        display_data.columns = [
            "연도",
            "연평균 기온 (℃)",
            "유효 데이터 수"
        ]

        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True
        )

except Exception as e:

    st.error("데이터를 불러오는 중 문제가 발생했습니다.")

    st.info(
        "인터넷 연결 또는 데이터 주소를 확인해주세요."
    )

    st.code(str(e))
