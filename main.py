import pandas as pd
import streamlit as st
import numpy as np
import altair as alt

## タイトル
st.title('なんちゃってDYNAMICS')

## サイドバー
st.sidebar.write("""
## Market Overview
""")

graph = st.sidebar.radio(
    "グラフの種類を選択してください",
    ('折れ線グラフ','積み上げ棒グラフ')
)

display = st.sidebar.radio(
    "どちらかを選択してください",
    ('患者数','シェア')
)

# st.sidebar.write("""
# ## 横軸幅選択
# """)
# mv_xmin , mv_xmax = st.sidebar.slider(
#     "範囲を指定してください",
#     '2019/04', '2021/04', ('2019/04', '2021/04')
#     )

st.sidebar.write("""
### （患者数）縦軸範囲選択
""")
mv_ymin , mv_ymax = st.sidebar.slider(
    "範囲を指定してください",
    0, 100000, (0, 25000), 500
    )


## データ取得関数
@st.cache
def get_mv_data():

    # csvデータ取得
    df = pd.read_csv('MV_DM1.csv')
    # 年月カラムを文字列型、スラッシュつける
    df["年月"] = df["年月"].astype(str)
    df["年月"] = df["年月"].str[:4] + "/" + df["年月"].str[-2:]
    # セグメントALLのデータを取得
    condition = (df.セグメント == 'ALL')
    df = df[condition]
    return df

@st.cache
def get_sob_data(level, target):

    if level == 'カテゴリ':
        st.info('すみません。対象データがありません')
    elif level == 'クラス':
        # csvデータ取得
        df2 = pd.read_csv('SOB_LEVEL2.csv')
        condition_sob = (df2.medicine_nm_2 == f'{target}')
    elif level == '成分':
        # csvデータ取得
        df2 = pd.read_csv('SOB_LEVEL3.csv')
        condition_sob = (df2.medicine_nm_3 == f'{target}')
    elif level == 'ブランド':
        # csvデータ取得
        df2 = pd.read_csv('SOB_LEVEL4.csv')
        condition_sob = (df2.medicine_nm_4 == f'{target}')
    else:
        st.error('何かおかしなことが起きてます')

    # 年月カラムを文字列型、スラッシュつける
    df2["年月"] = df2["年月"].astype(str)
    df2["年月"] = df2["年月"].str[:4] + "/" + df2["年月"].str[-2:]

    df_cond_sob = df2[condition_sob]
    return df_cond_sob



## 本体
# 領域選択
ryouiki_list = ["糖尿病"]
ryouiki_name = st.selectbox(
    '領域を選択してください',
    ryouiki_list)

st.write(ryouiki_name + '領域を選択しています')

# 分析レベル選択
level = st.radio(
    '分析レベルを選択してください',
    ('カテゴリ', 'クラス', '成分', 'ブランド'),
)

# 分析レベルのカラム名取得
if level == 'カテゴリ':
    col_nm = ''
    st.info('すみません。対象データがありません')
elif level == 'クラス':
    col_nm = 'medicine_nm_2'
elif level == '成分':
    col_nm = 'medicine_nm_3'
elif level == 'ブランド':
    col_nm = 'ブランド'
else:
    st.error('何かおかしなことが起きてます')

# カラム名が取得できた場合の処理
if col_nm != '': 

    #######
    # MV
    #######
    st.subheader('Market Overview')

    # MV：データ取得
    df = get_mv_data()

    # MV：分析レベルに場合分け
    df_mv = df[['年月', f'{col_nm}', '患者数']]

    ## 患者数
    if display == '患者数':
        # MV：グラフの表示
        df_sum = df_mv.groupby(['年月', f'{col_nm}']).sum()
        data = df_sum.reset_index()

        if graph == '折れ線グラフ':
            # 折れ線グラフ
            chart = (
                alt.Chart(data)
                .mark_line(opacity=0.8, clip=True)
                .encode(
                    x=alt.X('年月:N'),
                    y=alt.Y('患者数:Q', stack=None, scale=alt.Scale(domain=[mv_ymin,mv_ymax])),
                    color=f'{col_nm}:N',
                    tooltip=[f'{col_nm}','患者数']

                ).interactive()
            )
        else:
            # 積み上げ棒グラフ
            chart = (
                alt.Chart(data)
                .mark_bar(opacity=0.8, clip=True)
                .encode(
                    x=alt.X('年月:N'),
                    y=alt.Y('患者数:Q', scale=alt.Scale(domain=[mv_ymin,mv_ymax])),
                    color=f'{col_nm}:N',
                    tooltip=[f'{col_nm}','患者数']

                ).interactive()
            )

        st.altair_chart(chart, use_container_width=True)

        # MV：表の表示（総患者数がない。concatでつなげたりすればいけるか）
        df_mv_list = df_mv.pivot_table(index=[f'{col_nm}'], columns=['年月'], values='患者数', fill_value=0, aggfunc=np.sum)
        st.dataframe(df_mv_list)

    else:
        ## シェア
        # MV：グラフの表示
        df_mv_share = pd.crosstab(df_mv[f'{col_nm}'], df_mv['年月'], normalize='columns').round(3) * 100
        sdata = df_mv_share.T.reset_index()
        sdata = pd.melt(sdata, id_vars=['年月'])

        if graph == '折れ線グラフ':
            # 折れ線グラフ
            chart2 = (
                alt.Chart(sdata)
                .mark_line(opacity=0.8, clip=True)
                .encode(
                    x=alt.X('年月:N'),
                    y=alt.Y('value:Q', stack=None, scale=alt.Scale(domain=[0,100])),
                    color=f'{col_nm}:N',
                    tooltip=[f'{col_nm}','value']

                ).interactive()
            )
        else:
            # 積み上げ棒グラフ
            chart2 = (
                alt.Chart(sdata)
                .mark_bar(opacity=0.8, clip=True)
                .encode(
                    x=alt.X('年月:N'),
                    y=alt.Y('value:Q', scale=alt.Scale(domain=[0,100])),
                    color=f'{col_nm}:N',
                    tooltip=[f'{col_nm}','value']

                ).interactive()
            )

        st.altair_chart(chart2, use_container_width=True)

        # MV：表の表示（総患者数がない。表示桁数をかえたい。％をつけたい）
        df_mv_share = pd.crosstab(df_mv[f'{col_nm}'], df_mv['年月'], normalize='columns').round(3) * 100
        st.dataframe(df_mv_share)


    #######
    # SOB
    #######
    st.subheader('Source of Business')

    sob_list = df[f'{col_nm}'].unique()
    target = st.selectbox(
        f'対象の{level}を選択してください',
        sob_list
        )

    # SOB：データ取得
    df2 = get_sob_data(level, target)
    df_sob = df2[['年月', 'セグメント', '患者数']]
    df_sob_list = df_sob.pivot_table(index=['セグメント'], columns=['年月'], values='患者数', fill_value=0, aggfunc=np.sum)

    # SOB：グラフの表示
    st.write('＜ここにグラフ表示予定＞')

    # SOB：表の表示（総患者数がない／並び順の工夫がいる
    st.dataframe(df_sob_list)


    #######
    # 詳細
    #######
    st.subheader('Detail (Switch In To / Switch Out From / Add On)')

    detail_list = ['Switch In To', 'Switch Out From', 'Add On']
    detail = st.selectbox(
        '選択してください',
        detail_list
        )

    st.write('■選択内容■ ' + f'{detail}' + '：' + f'{target}')

    # 詳細：グラフの表示
    st.write('＜ここにグラフ表示予定＞')
    # 詳細：表の表示
    st.write('＜ここに表を表示予定＞')
