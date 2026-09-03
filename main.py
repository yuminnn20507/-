import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(
    page_title="서울 연도별 연평균 기온",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 서울 연도별 연평균 기온")
st.write("서울의 연평균 기온 변화를 확인하고, 이상한 데이터도 쉽게 찾아보세요.")

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

    df["날짜"] = pd.to_datetime(
        df["날짜"],
        errors="coerce"
    )

    df["평균기온"] = pd.to_numeric(
        df["평균기온"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["날짜", "평균기온"]
    )

    df["연도"] = df["날짜"].dt.year

    return df


try:

    df = load_data()

    # ==================================================
    # 연도별 데이터 수
    # ==================================================
    yearly_count = (
        df.groupby("연도")["평균기온"]
        .count()
        .reset_index(name="데이터수")
    )

    # ==================================================
    # 연도별 평균기온
    # ==================================================
    yearly_temp = (
        df.groupby("연도")["평균기온"]
        .mean()
        .reset_index()
    )

    yearly_temp = yearly_temp.merge(
        yearly_count,
        on="연도",
        how="left"
    )

    yearly_temp = yearly_temp.sort_values("연도")

    # 300일 미만인 연도는 연평균으로 사용하지 않음
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
        range(min_year, max_year + 1)
    )

    graph_data = (
        yearly_temp
        .set_index("연도")
        .reindex(all_years)
    )

    # ==================================================
    # 유효한 데이터
    # ==================================================
    valid_data = graph_data[
        graph_data["평균기온"].notna()
    ].copy()

    # ==================================================
    # 유난히 낮은 연도 찾기
    # ==================================================
    overall_mean = valid_data["평균기온"].mean()
    overall_std = valid_data["평균기온"].std()

    LOW_THRESHOLD = (
        overall_mean - 1.5 * overall_std
    )

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
    # 정상 데이터 선
    # --------------------------------------------------
    segment_years = []
    segment_temps = []

    for year in all_years:

        temp = graph_data.loc[year, "평균기온"]

        if pd.isna(temp):

            if segment_years:

                fig.add_trace(
                    go.Scatter(
                        x=segment_years,
                        y=segment_temps,
                        mode="lines+markers",

                        line=dict(
                            color="#0066CC",
                            width=2
                        ),

                        marker=dict(
                            color="#0066CC",
                            size=6
                        ),

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

                line=dict(
                    color="#0066CC",
                    width=2
                ),

                marker=dict(
                    color="#0066CC",
                    size=6
                ),

                showlegend=False,

                hovertemplate=(
                    "연도 %{x}년<br>"
                    "평균기온 %{y:.1f}℃"
                    "<extra></extra>"
                )
            )
        )

    # --------------------------------------------------
    # 유난히 낮은 연도
    # --------------------------------------------------
    if len(low_years) > 0:

        fig.add_trace(
            go.Scatter(
                x=low_years.index,
                y=low_years["평균기온"],

                mode="markers+text",

                name="⚠️ 유난히 낮은 연도",

                text=[
                    f"{int(year)}년"
                    for year in low_years.index
                ],

                textposition="top center",

                textfont=dict(
                    color="#E53935",
                    size=10
                ),

                marker=dict(
                    color="#E53935",
                    size=11,
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
    # 데이터 부족 연도 찾기
    # ==================================================
    missing_years = []

    for year in all_years:

        if pd.isna(
            graph_data.loc[year, "평균기온"]
        ):
            missing_years.append(year)

    # ==================================================
    # 연속된 데이터 부족 연도를 묶기
    # ==================================================
    missing_ranges = []

    if missing_years:

        start = missing_years[0]
        end = missing_years[0]

        for year in missing_years[1:]:

            if year == end + 1:
                end = year

            else:
                missing_ranges.append(
                    (start, end)
                )

                start = year
                end = year

        missing_ranges.append(
            (start, end)
        )

    # ==================================================
    # 데이터 부족 구간 회색 표시
    # ==================================================
    for start, end in missing_ranges:

        fig.add_vrect(
            x0=start - 0.5,
            x1=end + 0.5,

            fillcolor="gray",
            opacity=0.12,

            line_width=0,

            layer="below"
        )

        middle = (start + end) / 2

        if start == end:

            label = (
                f"{start}년<br>"
                "데이터 부족"
            )

        else:

            label = (
                f"{start}~{end}년<br>"
                "데이터 부족"
            )

        fig.add_annotation(
            x=middle,
            y=1,
            yref="paper",

            text=label,

            showarrow=False,

            font=dict(
                size=10,
                color="gray"
            ),

            bgcolor="rgba(255,255,255,0.8)",

            bordercolor="lightgray",
            borderwidth=1,
            borderpad=3
        )

    # ==================================================
    # 그래프 설정
    # ==================================================
    fig.update_layout(

        xaxis=dict(
            title="연도",

            # 실제 연도 간격을 사용
            type="linear",

            # 10년 단위 눈금
            dtick=10,

            range=[
                min_year - 2,
                max_year + 2
            ]
        ),

        yaxis=dict(
            title="평균기온 (℃)"
        ),

        # 가로로 넓게 보이도록 세로를 줄임
        height=420,

        hovermode="x unified",

        margin=dict(
            l=60,
            r=30,
            t=70,
            b=60
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
        ### 🔎 그래프 확인 방법

        🔵 **파란색** → 정상적으로 계산된 연평균 기온

        🔴 **빨간색 큰 점** → 유난히 낮은 연도

        ▫️ **회색 영역** → 데이터가 없거나 부족한 연도
        """
    )

    st.caption(
        f"※ 유효 데이터가 {MIN_DAYS}일 미만인 연도는 "
        "연평균 기온을 계산하지 않고 비워두었습니다."
    )

    # ==================================================
    # 유난히 낮은 연도
    # ==================================================
    st.divider()

    st.subheader("⚠️ 유난히 낮은 연도")

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
            f"현재 기준: {LOW_THRESHOLD:.1f}℃보다 낮은 연도"
        )

    else:

        st.success(
            "유난히 낮은 연도가 없습니다."
        )

    # ==================================================
    # 데이터 부족 연도
    # ==================================================
    st.subheader("▫️ 데이터가 없거나 부족한 연도")

    if missing_years:

        st.write(
            f"유효 데이터가 {MIN_DAYS}일 미만인 연도:"
        )

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
    # 전체 데이터
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
