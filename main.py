import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(
    page_title="서울 연평균 기온 변화",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 서울 연도별 연평균 기온")
st.write("서울의 연평균 기온 변화를 확인하고, 데이터가 이상한 연도도 쉽게 찾아보세요.")

# 데이터 주소
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"


# ==================================================
# 데이터 불러오기
# ==================================================
@st.cache_data
def load_data():

    df = pd.read_csv(
        DATA_URL,
        encoding="utf-8-sig"
    )

    # 날짜 변환
    df["날짜"] = pd.to_datetime(
        df["날짜"],
        errors="coerce"
    )

    # 평균기온 숫자 변환
    df["평균기온"] = pd.to_numeric(
        df["평균기온"],
        errors="coerce"
    )

    # 날짜와 평균기온이 모두 있는 데이터만 사용
    df = df.dropna(
        subset=["날짜", "평균기온"]
    )

    # 연도 생성
    df["연도"] = df["날짜"].dt.year

    return df


# ==================================================
# 데이터 처리
# ==================================================
try:

    df = load_data()

    # ----------------------------------------------
    # 연도별 유효 데이터 개수
    # ----------------------------------------------
    yearly_count = (
        df.groupby("연도")["평균기온"]
        .count()
        .reset_index(name="데이터수")
    )

    # ----------------------------------------------
    # 연도별 평균기온
    # ----------------------------------------------
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

    yearly_temp = yearly_temp.sort_values("연도")


    # ==================================================
    # 데이터가 부족한 연도 설정
    # ==================================================

    # 1년에 최소 300일 이상의 데이터가 있어야
    # 연평균 기온으로 인정
    MIN_DAYS = 300

    yearly_temp.loc[
        yearly_temp["데이터수"] < MIN_DAYS,
        "평균기온"
    ] = None


    # ==================================================
    # 모든 연도 만들기
    # ==================================================

    min_year = int(yearly_temp["연도"].min())
    max_year = int(yearly_temp["연도"].max())

    all_years = list(
        range(
            min_year,
            max_year + 1
        )
    )

    graph_data = (
        yearly_temp
        .set_index("연도")
        .reindex(all_years)
    )

    graph_data.index.name = "연도"


    # ==================================================
    # 유효한 데이터만 추출
    # ==================================================

    valid_data = graph_data[
        graph_data["평균기온"].notna()
    ].copy()


    # ==================================================
    # 유난히 낮은 연도 찾기
    # ==================================================

    # 전체 연평균 기온의 평균
    overall_mean = valid_data["평균기온"].mean()

    # 표준편차
    overall_std = valid_data["평균기온"].std()

    # 평균보다 1.5 표준편차 이상 낮으면
    # "유난히 낮은 연도"로 판단
    LOW_THRESHOLD = overall_mean - (1.5 * overall_std)

    low_years = valid_data[
        valid_data["평균기온"] < LOW_THRESHOLD
    ].copy()


    # ==================================================
    # 상단 정보
    # ==================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "데이터 시작 연도",
            f"{int(valid_data.index.min())}년"
        )

    with col2:

        st.metric(
            "데이터 마지막 연도",
            f"{int(valid_data.index.max())}년"
        )

    with col3:

        st.metric(
            "가장 높은 연평균 기온",
            f"{valid_data['평균기온'].max():.1f}℃"
        )

    with col4:

        st.metric(
            "유난히 낮은 연도",
            f"{len(low_years)}개"
        )


    st.divider()


    # ==================================================
    # 그래프
    # ==================================================

    st.subheader("📈 서울 연도별 연평균 기온")

    fig = go.Figure()


    # --------------------------------------------------
    # 1. 데이터가 충분한 구간만 파란색 선으로 연결
    # --------------------------------------------------

    segment_years = []
    segment_temps = []

    for year in all_years:

        temp = graph_data.loc[year, "평균기온"]

        # 데이터가 없는 경우
        if pd.isna(temp):

            if segment_years:

                fig.add_trace(
                    go.Scatter(
                        x=segment_years,
                        y=segment_temps,

                        mode="lines+markers",

                        name="연평균 기온",

                        showlegend=False,

                        line=dict(
                            color="#0066CC",
                            width=2
                        ),

                        marker=dict(
                            color="#0066CC",
                            size=6
                        ),

                        hovertemplate=(
                            "연도 %{x}년<br>"
                            "평균기온 %{y:.1f}℃"
                            "<extra></extra>"
                        )
                    )
                )

                segment_years = []
                segment_temps = []

        else:

            segment_years.append(year)
            segment_temps.append(float(temp))


    # 마지막 구간
    if segment_years:

        fig.add_trace(
            go.Scatter(
                x=segment_years,
                y=segment_temps,

                mode="lines+markers",

                name="연평균 기온",

                showlegend=False,

                line=dict(
                    color="#0066CC",
                    width=2
                ),

                marker=dict(
                    color="#0066CC",
                    size=6
                ),

                hovertemplate=(
                    "연도 %{x}년<br>"
                    "평균기온 %{y:.1f}℃"
                    "<extra></extra>"
                )
            )
        )


    # ==================================================
    # 2. 유난히 낮은 연도 빨간색으로 표시
    # ==================================================

    if len(low_years) > 0:

        fig.add_trace(
            go.Scatter(
                x=low_years.index,
                y=low_years["평균기온"],

                mode="markers+text",

                name="유난히 낮은 연도",

                text=[
                    f"{int(year)}년"
                    for year in low_years.index
                ],

                textposition="bottom center",

                textfont=dict(
                    color="#E53935",
                    size=12
                ),

                marker=dict(
                    color="#E53935",
                    size=12,
                    line=dict(
                        color="white",
                        width=2
                    )
                ),

                hovertemplate=(
                    "⚠️ 유난히 낮은 연도<br>"
                    "연도: %{x}년<br>"
                    "평균기온: %{y:.1f}℃"
                    "<extra></extra>"
                )
            )
        )


    # ==================================================
    # 3. 데이터가 부족한 연도 표시
    # ==================================================

    # 그래프의 아래쪽에 표시할 위치
    y_min = valid_data["평균기온"].min()

    # 데이터가 부족한 연도 찾기
    missing_years = []

    for year in all_years:

        if pd.isna(
            graph_data.loc[year, "평균기온"]
        ):

            missing_years.append(year)


    # 데이터 부족 연도를 회색 영역으로 표시
    for year in missing_years:

        fig.add_vrect(
            x0=year - 0.45,
            x1=year + 0.45,

            fillcolor="lightgray",
            opacity=0.45,

            line_width=0,

            layer="below"
        )


    # ==================================================
    # 그래프 설정
    # ==================================================

    fig.update_layout(

        xaxis_title="연도",

        yaxis_title="평균기온 (℃)",

        height=550,

        hovermode="x unified",

        margin=dict(
            l=20,
            r=20,
            t=40,
            b=20
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )


    # ==================================================
    # 그래프 출력
    # ==================================================

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # ==================================================
    # 범례 설명
    # ==================================================

    st.markdown(
        """
        **그래프 읽는 방법**

        🔵 파란색 선·점 → 정상적으로 계산된 연평균 기온

        🔴 빨간색 큰 점 → 전체 데이터에서 유난히 낮은 연도

        ▫️ 회색 세로 영역 → 데이터가 없거나 300일 미만인 연도
        """
    )


    st.caption(
        f"※ 유효 데이터가 {MIN_DAYS}일 미만인 연도는 연평균 기온을 계산하지 않고 비워두었습니다."
    )


    # ==================================================
    # 유난히 낮은 연도 표
    # ==================================================

    st.divider()

    st.subheader("⚠️ 유난히 낮은 연도 확인")

    if len(low_years) > 0:

        low_table = low_years.reset_index()

        low_table.columns = [
            "연도",
            "연평균 기온 (℃)",
            "유효 데이터 수"
        ]

        low_table["연평균 기온 (℃)"] = (
            low_table["연평균 기온 (℃)"]
            .round(1)
        )

        st.dataframe(
            low_table,
            use_container_width=True,
            hide_index=True
        )

        st.info(
            f"기준: {LOW_THRESHOLD:.1f}℃보다 낮은 연도를 "
            "유난히 낮은 연도로 표시했습니다."
        )

    else:

        st.success(
            "유난히 낮은 연도가 발견되지 않았습니다."
        )


    # ==================================================
    # 데이터 부족 연도 표
    # ==================================================

    st.subheader("▫️ 데이터가 없거나 부족한 연도")

    if len(missing_years) > 0:

        st.write(
            "다음 연도는 데이터가 없거나 "
            f"{MIN_DAYS}일 미만이라 그래프에서 비워두었습니다."
        )

        # 한 줄에 여러 연도 표시
        st.write(
            ", ".join(
                f"{year}년"
                for year in missing_years
            )
        )

    else:

        st.success(
            "데이터가 부족한 연도가 없습니다."
        )


    # ==================================================
    # 전체 데이터 표
    # ==================================================

    with st.expander("📋 전체 연도별 데이터 보기"):

        display_data = graph_data.reset_index()

        display_data["평균기온"] = (
            display_data["평균기온"]
            .round(1)
        )

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


# ==================================================
# 오류 처리
# ==================================================

except Exception as e:

    st.error(
        "데이터를 불러오는 중 문제가 발생했습니다."
    )

    st.info(
        "인터넷 연결 또는 데이터 주소를 확인해주세요."
    )

    st.code(str(e))
