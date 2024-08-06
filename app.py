import streamlit as st

st.title('Steamlit 시각화')
st.write('This is a simple Streamlit app connected with GitHub.')
#%%
import streamlit as st  # Streamlit 패키지
import plotly.express as px 
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore')

# * 페이지 설정 및 데이터 프레임 정의
st.set_page_config(page_title="2013-2023 동해 해표면 온도", page_icon=":bar_chart:", layout="wide")
st.title(":bar_chart: 2013-2023 동해 해표면 온도")
st.markdown('<style>div.block-container{padding-top:3rem;}</style>', unsafe_allow_html=True)

# 데이터 파일 읽기
df1 = pd.read_csv("./2013-2023_동해관측정보.csv", encoding="utf-8-sig")
df2 = pd.read_csv("./2013-2023년 냉수대속보데이터.csv", encoding="utf-8-sig")
df3 = pd.read_csv("./2023년_동해관측정보.csv", encoding="utf-8-sig")
df4 = pd.read_csv("./2023년06월_냉수대속보데이터.csv", encoding="utf-8-sig")

# 날짜 형식 변환
df1['OBVP_DATE'] = pd.to_datetime(df1['OBVP_DATE'], format='ISO8601')

df2['CP_ISSUED_YMD'] = df2['CP_ISSUED_YMD'].astype(str)
df2['CP_WTCH_YMD'] = df2['CP_WTCH_YMD'].astype(str)
df3['OBVP_DATE'] = df3['OBVP_DATE'].astype(str)


df2['CP_ISSUED_YMD'] = df2['CP_ISSUED_YMD'].apply(lambda x: x.split('.')[0])
df2['CP_WTCH_YMD'] = df2['CP_WTCH_YMD'].apply(lambda x: x.split('.')[0])
df3['OBVP_DATE'] = df3['OBVP_DATE'].apply(lambda x: x.split('.')[0])


df2['CP_ISSUED_YMD'] = pd.to_datetime(df2['CP_ISSUED_YMD'], format='%Y%m%d')
df2['CP_WTCH_YMD'] = pd.to_datetime(df2['CP_WTCH_YMD'], format='%Y%m%d')

# 데이터 카운트 및 정렬
df2['Data_Count'] = df2.groupby('CP_OBVP_NM')['CP_OBVP_NM'].transform('size')
df2['Name_Count_Str'] = df2.apply(lambda row: f"{row['CP_OBVP_NM']} ({row['Data_Count']})", axis=1)
df2 = df2.sort_values(by=['CP_ISSUED_SAR_NM', 'CP_OBVP_NM'], ascending=[False, False])

# * 페이지 레이아웃
startDate = pd.to_datetime(df2["CP_WTCH_YMD"]).min()
endDate = pd.to_datetime(df2["CP_WTCH_YMD"]).max()

date1 = pd.to_datetime(st.sidebar.date_input("Start Date", startDate))
date2 = pd.to_datetime(st.sidebar.date_input("End Date", endDate))

df2 = df2[(df2["CP_WTCH_YMD"] >= date1) & (df2["CP_WTCH_YMD"] <= date2)].copy()

st.sidebar.header("Choose your filter: ")

# 지역 선택 필터
sar = st.sidebar.multiselect("Pick your Sar", df2["CP_ISSUED_SAR_NM"].unique())
if not sar:
    df22 = df2.copy()
else:
    df22 = df2[df2["CP_ISSUED_SAR_NM"].isin(sar)]

# 관측소 선택 필터
obvp1 = st.sidebar.multiselect("Pick the Observatory", df1["OBVP_NM"].unique())
if not obvp1:
    df222 = df22.copy()
else:
    df222 = df22[df22["CP_OBVP_NM"].isin(obvp1)]

obvp2 = st.sidebar.multiselect("Pick the Observatory", df2["CP_OBVP_NM"].unique())
if not obvp2:
    df222 = df22.copy()
else:
    df222 = df22[df22["CP_OBVP_NM"].isin(obvp2)]

# 탭 생성
tab1, tab2 = st.tabs(["Tab 1", "Tab 2"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader('냉수대 주의보 관측소 위치 및 데이터 시각화')

        # Ensure Data_Count is not empty before calculating max
        if df2['Data_Count'].empty:
            sizeref = 1  # Default sizeref value
        else:
            sizeref = 2.0 * max(df2['Data_Count']) / (30 ** 2)
        
        fig1 = go.Figure(go.Scattermapbox(
            lat=df222['CP_OBVP_LAT'],
            lon=df222['CP_OBVP_LON'],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=df222['Data_Count'],
                sizeref=sizeref,
                sizemode='area',
                color=df222['CP_WTEM'],
                colorscale='RdBu_r',
                cmin=10,  # 색상 범위 최소값 설정
                cmax=30, 
                opacity=1,
                colorbar=dict(
                    title='최저 온도',
                    tickvals=[10, 15, 20, 25, 30],  # 눈금값 설정
                    ticktext=['10°C', '15°C', '20°C', '25°C', '30°C']  # 눈금 텍스트 설정
                    ),
            ),
            text=df222['Name_Count_Str'].astype(str),
            hoverinfo='text',
        ))

        fig1.update_layout(
            mapbox=dict(
                style='carto-positron',
                center=dict(lat=df2['CP_OBVP_LAT'].mean(), lon=df2['CP_OBVP_LON'].mean()-1),
                zoom=6.5
            ),
            margin=dict(l=10, r=50, t=0, b=50),
            autosize=False, width=600, height=900
        )

        st.plotly_chart(fig1)

    with col2:
        st.subheader("2024학년도 해양과학 빅데이터 직무연수")
        img1 = st.image("./직무연수 표지.png", width=600)

with tab2:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader('2013-2023년 동해 해수면 온도 변화')
        fig2 = make_subplots(rows=1, cols=1)
        color_map = {station: color for station, color in zip(df1['OBVP_NM'].unique(), px.colors.qualitative.Plotly)}

        for station in df1['OBVP_NM'].unique():
            station_data = df1[df1['OBVP_NM'] == station]
            fig2.add_trace(go.Scatter(
                x=station_data['OBVP_DATE'],
                y=station_data['MEAN_TEMP'],
                mode='lines+markers',
                marker=dict(color=color_map[station], opacity=0.5),
                name=station
            ))

        fig2.update_layout(
            xaxis_title='날짜',
            yaxis_title='평균 온도',
            showlegend=True,
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label='1년', step='year', stepmode='backward'),
                        dict(count=3, label='3년', step='year', stepmode='backward'),
                        dict(count=5, label='5년', step='year', stepmode='backward'),
                        dict(step='all'),
                    ])
                ),
                rangeslider=dict(visible=True),
                type='date'
            ),
            margin=dict(l=10, r=50, t=50, b=50)
        )

        st.plotly_chart(fig2)

    with col2:
        st.subheader('2023년 6월 동해 해수면 온도 변화')
        fig3 = make_subplots(rows=1, cols=1)

        unique_observation_points = df4['OBVP_NM'].unique()

        for observation_point in unique_observation_points:
            observation_data = df4[df4['OBVP_NM'] == observation_point]
            if not observation_data.empty:
                fig3.add_trace(go.Scatter(
                    x=observation_data['OBVP_DATE'],
                    y=observation_data['MEAN_TEMP'],
                    mode='lines+markers',
                    name=observation_point
                ))

        fig3.update_layout(
            xaxis_title="날짜",
            yaxis_title="수온",
            margin=dict(l=50, r=50, t=50, b=50)
        )
        st.plotly_chart(fig3)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader('냉수대 발령 해수면 온도 분포도')

        histograms = []
        categories = df2['CP_ISSUED_SAR_NM'].unique()
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink']

        for i, category in enumerate(categories):
            category_data = df2[df2['CP_ISSUED_SAR_NM'] == category]['CP_WTEM']
            histograms.append(go.Histogram(
                x=category_data,
                name=category,
                marker=dict(color=colors[i]),
                opacity=0.75
            ))

        layout = go.Layout(
            xaxis_title="온도",
            yaxis_title="개수",
            barmode='overlay'
        )

        fig4 = go.Figure(data=histograms, layout=layout)
        st.plotly_chart(fig4)

    with col2:
        st.subheader('관측소별 관측수온 분포도')

        box_plots = []
        categories = df2['CP_ISSUED_SAR_NM'].unique()
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink']

        for i, category in enumerate(categories):
            category_data = df2[df2['CP_ISSUED_SAR_NM'] == category]['CP_WTEM']
            box_plots.append(go.Box(
                y=category_data,
                name=category,
                marker=dict(color=colors[i])
            ))

        layout = go.Layout(
            xaxis_title="관측소",
            yaxis_title="온도",
        )

        fig5 = go.Figure(data=box_plots, layout=layout)
        st.plotly_chart(fig5)

# %%
