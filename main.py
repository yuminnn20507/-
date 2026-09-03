fig.update_layout(

    xaxis=dict(
        title="연도",

        # 연도는 실제 숫자 간격을 사용
        type="linear",

        # 연도 눈금 간격
        dtick=10,

        # 좌우 여백
        range=[
            min_year - 2,
            max_year + 2
        ]
    ),

    yaxis=dict(
        title="평균기온 (℃)"
    ),

    # 세로를 조금 줄여서 가로로 긴 형태
    height=420,

    # 그래프 좌우 여백
    margin=dict(
        l=60,
        r=30,
        t=60,
        b=60
    ),

    hovermode="x unified",

    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)
