# 연도별 기온 그래프
st.subheader(
    f"{start_year_selected}년 ~ {end_year_selected}년 연평균 기온"
)

# 조회 기간의 모든 연도를 생성
all_years = pd.DataFrame({
    "연도": range(start_year_selected, end_year_selected + 1)
})

# 실제 데이터와 모든 연도를 합치기
chart_data_full = all_years.merge(
    chart_data,
    on="연도",
    how="left"
)

# 데이터가 없는 연도는 NaN으로 유지
# → Altair에서 선이 끊어짐
chart = (
    alt.Chart(chart_data_full)
    .mark_line(point=True)
    .encode(
        x=alt.X(
            "연도:Q",
            title="연도",
            axis=alt.Axis(format="d")
        ),
        y=alt.Y(
            "연평균기온:Q",
            title="연평균 기온 (℃)"
        ),
        tooltip=[
            alt.Tooltip("연도:Q", title="연도", format="d"),
            alt.Tooltip("연평균기온:Q", title="평균기온", format=".2f")
        ]
    )
    .properties(
        height=500
    )
)

st.altair_chart(
    chart,
    use_container_width=True
)
