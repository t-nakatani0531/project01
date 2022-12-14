#import欄
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import math as math
import numpy as np
import plotly.express as px
import plotly.io as pio
import datetime
import plotly.graph_objects as go


#目次の作成
st.set_page_config(layout="wide")
#ページのタイトル
st.sidebar.title("生産データ分析")

#セレクトボックスのリストを作成
pagelist = ["➀人のことを知りたい","　1.(ヒストグラム)作業時間[個人]","　2.(ヒストグラム)作業時間[複数]","　3.(棒グラフ)期間内の各人作業量",#人の能力
            "➁設備や人の空きを知りたい","　1.(ガントチャート)人の空き","　2.(ガントチャート)設備の空き",#場所・時間・人の有効活用
            "➂製品を知りたい","　1.(折れ線)仕掛品の推移",
            "➃集計表","　1.(集計表)作業時間統計量"]#無駄なものを作りたくない
#サイドバーにセレクトボックスを配置
selector=st.sidebar.selectbox( "ページ選択",pagelist)
st.sidebar.write("-----")

left_column, center_column ,right_column = st.columns(3)
#製造データの取り込み
uploaded_file=st.sidebar.file_uploader("製造データの取り込み",type="xlsx")
if uploaded_file is not None:
    st.session_state.df=pd.read_excel(uploaded_file)
    
    #空の列作成
    st.session_state.df["開始日時"]=0
    st.session_state.df["完了日時"]=0
    #処理時間が０のものを除外
    st.session_state.df=st.session_state.df[st.session_state.df["処理時間"]!=0]

    #開始日時、完了日時の作成（時間と日付の結合）
    for index,row in st.session_state.df.iterrows():
    #作成（開始日時）
        time1=row["工程開始時間"]
        day1=row["工程開始日"]
        dateti1= datetime.datetime.combine(day1,time1)
    #作成（完了日時）
        time2=row["工程完了時間"]
        day2=row["工程完了日"]
        dateti2= datetime.datetime.combine(day2,time2)
    #追加
        st.session_state.df.at[index,'開始日時'] = pd.to_datetime(dateti1)
        st.session_state.df.at[index,'完了日時'] = pd.to_datetime(dateti2)

    #標準時間の取り込み
    uploaded_file1=st.sidebar.file_uploader("標準時間の取り込み",type="xlsx")
    if uploaded_file1 is not None:
        st.session_state.df_time=pd.read_excel(uploaded_file1)
        #標準時間の設定
        base_time = pd.to_datetime('00:00:0', format='%M:%S:%f')
        st.session_state.df_time['標準時間1']=pd.to_datetime(st.session_state.df_time['標準時間1'], format='%M:%S:%f') - base_time
        st.session_state.df_time['標準時間1']=st.session_state.df_time["標準時間1"].dt.total_seconds()
        st.session_state.df_time['標準時間2']=pd.to_datetime(st.session_state.df_time['標準時間2'], format='%M:%S:%f') - base_time
        st.session_state.df_time['標準時間2']=st.session_state.df_time["標準時間2"].dt.total_seconds()
    
#================================================================================================================================
if selector=="　1.(ガントチャート)人の空き":
    st.title("1.(ガントチャート)人の空き")
    left_column, center_column ,right_column = st.columns(3)
    day_num = sorted(list(set(st.session_state.df["工程完了日"])))
    d = left_column.selectbox(
         "工程完了日",
         (day_num))
    
    d_num=st.session_state.df[(st.session_state.df["工程完了日"]==d)&(st.session_state.df["工程開始日"] == d)]
    d_num=d_num.sort_values(["工程開始時間"])
    d_num=d_num.reset_index()
    
    d_num=d_num[(d_num["処理時間"] != 1)]
    
    if len(d_num)!=0:
            if len(d_num)!=1:#???分析開始ボタンの妨げになっている
                d_num["工程開始時間"] = pd.to_datetime(d_num["工程開始時間"], format="%H:%M:%S")
                d_num["工程完了時間"] = pd.to_datetime(d_num["工程完了時間"], format="%H:%M:%S")
                
                answer = st.button('分析開始')
                if answer == True:
                    
                    graph_num=pd.DataFrame()
                    t_list = sorted(list(set(d_num["担当者"])))
                    for t in t_list:
                        aki_time=0
                        t_num =d_num[d_num['担当者']==t]
                        t_num=t_num.sort_values("開始日時")
                        
                        #余裕率の計算、隙間時間
                        
                        sta_num=[]
                        end_num=[]
                        t_col=t_num.columns.values
                        for row in t_num.itertuples():
                            sta_num.append(row.開始日時)
                            end_num.append(row.完了日時)
                        
                        zentai_num=end_num[-1]-sta_num[0]
                        zentai_num=zentai_num.seconds
                        for i in range(len(t_num)-1):
                            a=sta_num[i+1]-end_num[i]
                            a=a.seconds
                            aki_time+=a
                            
                            df3 =pd.DataFrame(columns =t_col )
                            df2 = pd.DataFrame({"担当者":t,"工程名称":"隙間時間","開始日時":end_num[i], "完了日時":sta_num[i+1]},index=['time'])
                            
                            df3.loc[0,'担当者'] = t
                            df3.loc[0,'工程名称'] = "隙間時間"
                            df3.loc[0,'開始日時'] = end_num[i]+ datetime.timedelta(seconds=1)
                            df3.loc[0,'完了日時'] = sta_num[i+1]+ datetime.timedelta(seconds=-1)
                            
                            df3_num=sta_num[i+1]-end_num[i]
                            d3= df3_num.seconds
                            df3.loc[0,'処理時間'] = round(d3/60)
                            t_num=pd.concat([t_num, df3], axis=0)
                        
                        st.write("----------")
                        yoyuritu_num=(aki_time/zentai_num)*100
                        yoyuritu_num=round(yoyuritu_num, 2)
                        st.write(""" #### 担当者：""",t)
#                         st.write("空き時間の合計（秒）")
#                         st.write(aki_time)
#                         st.write("総作業時間（秒）")
#                         st.write(zentai_num)
                        
                        
                        t_num=t_num.sort_values("開始日時")
                        st.write(""" #### """,t,"""の稼働状況""",)
                        fig = go.Figure(px.timeline(t_num, x_start="開始日時", x_end="完了日時",y="工程名称",color="工程名称",text="処理時間"))
                        fig.update_traces(textposition='inside', orientation="h")
                        st.plotly_chart(fig)
                        graph_num=graph_num.append(t_num)
                        st.write(""" #### 余裕率：""",str(yoyuritu_num),""" % """)
  
                    st.write("--------")
                    st.write(""" #### 一日の全体の稼働状況""")
                    fig = go.Figure(px.timeline(graph_num, x_start="開始日時", x_end="完了日時",y="担当者",color="工程名称",text="処理時間"))
                    fig.update_traces(textposition='inside', orientation="h")
                    st.plotly_chart(fig)
                    
                    
                    #================================================================================================================================
elif selector=="　2.(ガントチャート)設備の空き":
    st.title("2.(ガントチャート)設備の空き")
    left_column, center_column ,right_column = st.columns(3)
    day_num = sorted(list(set(st.session_state.df["工程完了日"])))
    d = left_column.selectbox(
         "工程完了日",
         (day_num))
    
    d_num=st.session_state.df[(st.session_state.df["工程開始日"]==d)&(st.session_state.df["工程完了日"]==d)]
    
    d_num["工程開始時間"] = pd.to_datetime(d_num["工程開始時間"], format="%H:%M:%S")
    d_num["工程完了時間"] = pd.to_datetime(d_num["工程完了時間"], format="%H:%M:%S")
    kikai_num = list(set(d_num["号機名称"]))
    
    answer = st.button('分析開始')
    if answer == True:
        st.write("--------")
        st.write(""" #### 全体の稼働状況""")
        fig = go.Figure(px.timeline(d_num, x_start="開始日時", x_end="完了日時",text="処理時間",y="号機名称",color="号機名称"))
        fig.update_traces(textposition='inside', orientation="h")
        st.plotly_chart(fig)
        
        for k in kikai_num:
            k_num=d_num[d_num["号機名称"]==k]
            k_num=k_num.sort_values(["開始日時"])
            if len(k_num) >=1:
                st.write("--------")
                st.write(""" #### ・""",k,"""の稼働状況""")

                fig = go.Figure(px.timeline(k_num, x_start="開始日時", x_end="完了日時",text="処理時間",y="担当者",color="担当者", color_continuous_scale='Jet'))
                fig.update_traces(textposition='inside', orientation="h")
                fig.update_yaxes(autorange='reversed')
                st.plotly_chart(fig)
    #================================================================================================================================

elif selector=="　1.(ヒストグラム)作業時間[個人]":
    
    st.title("1.(ヒストグラム)作業時間[個人]")
    st.session_state.df['開始日時']=pd.to_datetime(st.session_state.df['開始日時'])
    #曜日の設定
    st.session_state.df["曜日"]=st.session_state.df["工程開始日"].dt.weekday
    #月の設定
    st.session_state.df["月"]=st.session_state.df["工程開始日"].dt.month
    #年の設定
    st.session_state.df["年"]=st.session_state.df["工程開始日"].dt.year
    #時刻の設定
    st.session_state.df["時刻"]=st.session_state.df["開始日時"].dt.hour
    st.session_state.df.loc[st.session_state.df['時刻'] <= 7, '時刻'] = 0
    st.session_state.df.loc[(st.session_state.df['時刻'] <= 9) & (st.session_state.df['時刻'] >= 8), '時刻'] = 1
    st.session_state.df.loc[(st.session_state.df['時刻'] <= 12) & (st.session_state.df['時刻'] >= 10), '時刻'] = 2
    st.session_state.df.loc[(st.session_state.df['時刻'] <= 14) & (st.session_state.df['時刻'] >= 13), '時刻'] = 3
    st.session_state.df.loc[(st.session_state.df['時刻'] <= 16) & (st.session_state.df['時刻'] >= 15), '時刻'] = 4
    st.session_state.df.loc[(st.session_state.df['時刻'] >= 17), '時刻'] = 5
    
    left_column, center_column ,right_column = st.columns(3)
    #担当の選択
    t_list = sorted(list(set(st.session_state.df["担当者"])))
    t = left_column.selectbox(
         "担当者",
         (t_list))
    x_num=st.session_state.df[(st.session_state.df["担当者"]==t)]#dfからzで選んだ図番のデータ
    k_list = sorted(list(set(x_num["工程名称"])))
    
    #工程の選択
    k = center_column.selectbox(
         "工程名称",
         (k_list))  
    x_k_num=x_num[(x_num["担当者"]==t) & (x_num["工程名称"]==k)]
    z_list = sorted(list(set(x_k_num["図番"])))
    
    #図番の選択
    z = right_column.selectbox(
         "図番",
         (z_list))
    
    #フィルター選択
    y_list = ["なし","曜日","月","年","時刻"]
    f_num = left_column.selectbox("期間グループ分け",(y_list))
    
    #データ分析開始
    answer = st.button('分析開始')
    if answer == True:
        
        data_num=st.session_state.df[(st.session_state.df["図番"]==z)&(st.session_state.df["工程名称"]==k)]#図番と工程名称でデータを絞る
        dosu_num=0#度数の空の変数

        y_num=st.session_state.df[(st.session_state.df["図番"]==z)&(st.session_state.df["工程名称"]==k)&(st.session_state.df["担当者"] == t)]#図番、工程名称、担当者でデータを絞る
        y_num=y_num["処理時間"]#処理時間だけ抜出
        
        #y軸の上限値
        x,y,_= plt.hist(y_num)#x軸、y軸、度数
        if dosu_num<max(x):#度数の比較（最大値）
            dosu_num=max(x)#（最大値）


        s_num=data_num['処理時間']#図番と工程名称で絞ったデータの処理時間を抜き出し

        q1=data_num['処理時間'].describe().loc['25%']#第一四分位範囲
        q3=data_num['処理時間'].describe().loc['75%']#第三四分位範囲

        iqr=q3-q1#四分位範囲
        upper_num=q3+(1.5*iqr)#上限
        lower_num=q1-(1.5*iqr)#下限

        upper_num2=round(upper_num) #きりあげ（上限）見やすくする用
        lower_num2=math.floor(lower_num)#きりおとし（下限）見やすくする用
        dif_num=upper_num2-lower_num2#差
        dif_num3=0

        if dif_num%10!=0:#もし切り上げ切り落としした差が10で割れなかった
            dif_num2=math.ceil((dif_num/10))*10
            dif_num3=(dif_num2-dif_num)/2
        upper_num2=upper_num2+dif_num3
        lower_num2=lower_num2-dif_num3
        dif_num=upper_num2-lower_num2#差
        if dif_num <= 10:
            dif_num=10
            lower_num2=lower_num2-5
            upper_num2=upper_num2+5

        hazure=data_num[data_num["処理時間"]<=upper_num]#外れ値の除外
        hazure=hazure[hazure["処理時間"]>=lower_num]

        #ヒストグラムの作成
        #データの整理
        scores=hazure[(hazure["図番"]==z)&(hazure["工程名称"]==k)&(hazure["担当者"]==t)]#選択したデータ（外れ値）
        
        y_scores=st.session_state.df_time[(st.session_state.df_time["図番"]==z)&(st.session_state.df_time["工程名称"]==k)]#標準時間のデータ
        
        hyozyun1=y_scores["標準時間1"]
        hyozyun2=y_scores["標準時間2"]
        
       
        #描画領域を用意する
        fig = plt.figure()
        ax = fig.add_subplot()

        plt.xlim([lower_num2,upper_num2])                        # X軸範囲
        plt.ylim([0,dosu_num+10])                      # Y軸範囲
        ax.set_title("chart")
        ax.set_xlabel("time")                # x軸ラベル
        plt.ylabel("count")               # y軸ラベル
        plt.grid(True)
        plt.axvline(x=int(hyozyun1),color = "crimson")#標準時間の表記（赤軸）
        plt.axvline(x=int(hyozyun2),color = "Blue")#標準時間の表記（軸）
        plt.xticks(np.arange(lower_num2, upper_num2,dif_num/10))
        labels = ax.get_xticklabels()
        plt.setp(labels, rotation=45, fontsize=10)
            
        if f_num=="なし":
            dd=scores["処理時間"]#選択したデータの処理時間
            
            ax.hist(dd,bins=10,range=(lower_num2,upper_num2))
            # Matplotlib の Figure を指定して可視化する
            st.write("--------")
            st.write("""#### -----担当者:[""",t,"""]-------工程名称:[""",k,"""]-------図番:[""",z,"""]-------データ件数:[""",str(len(scores)),"""]-----""")
            
            left_column, right_column = st.columns(2)
            left_column.pyplot(fig)

            num=pd.DataFrame(scores.groupby(['担当者',"図番","工程名称"])['処理時間'].agg(["count","mean", "median", "min", "max"]))
            pvit=num.set_axis(['件数', '平均', '中央値', '最小', '最大'], axis=1)
            pvit.insert(0, '総件数', len(y_num))
            pvit["標準時間1"]=int(hyozyun1)
            pvit["標準時間2"]=int(hyozyun2)
            st.write(pvit) 

        elif f_num=="曜日":
            you_list = sorted(list(set(scores["曜日"])))
            for you in you_list:
                scores=hazure[(hazure["図番"]==z)&(hazure["工程名称"]==k)&(hazure["担当者"]==t)&(hazure["曜日"]==you)]#選択したデータ（外れ値）
                dd=scores["処理時間"]#選択したデータの処理時間
                #描画領域を用意する
                fig = plt.figure()
                ax = fig.add_subplot()

                plt.xlim([lower_num2,upper_num2])                        # X軸範囲
                plt.ylim([0,dosu_num+10])                      # Y軸範囲
                ax.set_title("chart")
                ax.set_xlabel("time")                # x軸ラベル
                plt.ylabel("count")               # y軸ラベル
                plt.grid(True)
                plt.axvline(x=int(hyozyun1),color = "crimson")#標準時間の表記（赤軸）
                plt.axvline(x=int(hyozyun2),color = "Blue")#標準時間の表記（軸）
                plt.xticks(np.arange(lower_num2, upper_num2,dif_num/10))
                labels = ax.get_xticklabels()
                plt.setp(labels, rotation=45, fontsize=10)
                
                ax.hist(dd,bins=10,range=(lower_num2,upper_num2))
                youbi=["月","火","水","木","金","土","日"]
                # Matplotlib の Figure を指定して可視化する
                st.write("--------")
                st.write("""#### -----担当者:[""",t,"""]-------工程名称:[""",k,"""]-------図番:[""",z,"""]-------データ件数:[""",str(len(scores)),"""]-------曜日:[""",youbi[you],"""]-----""")
                left_column, right_column = st.columns(2)
                left_column.pyplot(fig)

                num=pd.DataFrame(scores.groupby(['担当者',"図番","工程名称"])['処理時間'].agg(["count","mean", "median", "min", "max"]))
                pvit=num.set_axis(['件数', '平均', '中央値', '最小', '最大'], axis=1)
                pvit.insert(0, '総件数', len(y_num))
                pvit["標準時間1"]=int(hyozyun1)
                pvit["標準時間2"]=int(hyozyun2)
                st.write(pvit)

        elif f_num=="月":
            tuki_list = sorted(list(set(scores["月"])))
            for tuki in tuki_list:
                scores=hazure[(hazure["図番"]==z)&(hazure["工程名称"]==k)&(hazure["担当者"]==t)&(hazure["月"]==tuki)]#選択したデータ（外れ値）
                dd=scores["処理時間"]#選択したデータの処理時間
                
                #描画領域を用意する
                fig = plt.figure()
                ax = fig.add_subplot()

                plt.xlim([lower_num2,upper_num2])                        # X軸範囲
                plt.ylim([0,dosu_num+10])                      # Y軸範囲
                ax.set_title("chart")
                ax.set_xlabel("time")                # x軸ラベル
                plt.ylabel("count")               # y軸ラベル
                plt.grid(True)
                plt.axvline(x=int(hyozyun1),color = "crimson")#標準時間の表記（赤軸）
                plt.axvline(x=int(hyozyun2),color = "Blue")#標準時間の表記（軸）
                plt.xticks(np.arange(lower_num2, upper_num2,dif_num/10))
                labels = ax.get_xticklabels()
                plt.setp(labels, rotation=45, fontsize=10)
                ax.hist(dd,bins=10,range=(lower_num2,upper_num2))
                # Matplotlib の Figure を指定して可視化する
                st.write("--------")
                
                st.write("""#### -----担当者:[""",t,"""]-------工程名称:[""",k,"""]-------図番:[""",z,"""]-------データ件数:[""",str(len(scores)),"""]-------月:[""",str(tuki),"""]-----""")
                left_column, right_column = st.columns(2)
                left_column.pyplot(fig)

                num=pd.DataFrame(scores.groupby(['担当者',"図番","工程名称"])['処理時間'].agg(["count","mean", "median", "min", "max"]))
                pvit=num.set_axis(['件数', '平均', '中央値', '最小', '最大'], axis=1)
                pvit.insert(0, '総件数', len(y_num))
                pvit["標準時間1"]=int(hyozyun1)
                pvit["標準時間2"]=int(hyozyun2)
                st.write(pvit)

        elif f_num=="年":
            nen_list = sorted(list(set(scores["年"])))
            for nen in nen_list:
                scores=hazure[(hazure["図番"]==z)&(hazure["工程名称"]==k)&(hazure["担当者"]==t)&(hazure["年"]==nen)]#選択したデータ（外れ値）
                dd=scores["処理時間"]#選択したデータの処理時間
                
                #描画領域を用意する
                fig = plt.figure()
                ax = fig.add_subplot()

                plt.xlim([lower_num2,upper_num2])                        # X軸範囲
                plt.ylim([0,dosu_num+10])                      # Y軸範囲
                ax.set_title("chart")
                ax.set_xlabel("time")                # x軸ラベル
                plt.ylabel("count")               # y軸ラベル
                plt.grid(True)
                plt.axvline(x=int(hyozyun1),color = "crimson")#標準時間の表記（赤軸）
                plt.axvline(x=int(hyozyun2),color = "Blue")#標準時間の表記（軸）
                plt.xticks(np.arange(lower_num2, upper_num2,dif_num/10))
                labels = ax.get_xticklabels()
                plt.setp(labels, rotation=45, fontsize=10)
                ax.hist(dd,bins=10,range=(lower_num2,upper_num2))
                # Matplotlib の Figure を指定して可視化する
                st.write("--------")
                
                st.write("""#### -----担当者:[""",t,"""]-------工程名称:[""",k,"""]-------図番:[""",z,"""]-------データ件数:[""",str(len(scores)),"""]-------年:[""",str(nen),"""]-----""")
                left_column, right_column = st.columns(2)
                left_column.pyplot(fig)

                num=pd.DataFrame(scores.groupby(['担当者',"図番","工程名称"])['処理時間'].agg(["count","mean", "median", "min", "max"]))
                pvit=num.set_axis(['件数', '平均', '中央値', '最小', '最大'], axis=1)
                pvit.insert(0, '総件数', len(y_num))
                pvit["標準時間1"]=int(hyozyun1)
                pvit["標準時間2"]=int(hyozyun2)
                st.write(pvit)

        elif f_num=="時刻":
            jkoku_list = sorted(list(set(scores["時刻"])))
            for i in jkoku_list:
                scores=hazure[(hazure["図番"]==z)&(hazure["工程名称"]==k)&(hazure["担当者"]==t)&(hazure["時刻"]==i)]#選択したデータ（外れ値）
                dd=scores["処理時間"]#選択したデータの処理時間
                
                #描画領域を用意する
                fig = plt.figure()
                ax = fig.add_subplot()

                plt.xlim([lower_num2,upper_num2])                        # X軸範囲
                plt.ylim([0,dosu_num+10])                      # Y軸範囲
                ax.set_title("chart")
                ax.set_xlabel("time")                # x軸ラベル
                plt.ylabel("count")               # y軸ラベル
                plt.grid(True)
                plt.axvline(x=int(hyozyun1),color = "crimson")#標準時間の表記（赤軸）
                plt.axvline(x=int(hyozyun2),color = "Blue")#標準時間の表記（軸）
                plt.xticks(np.arange(lower_num2, upper_num2,dif_num/10))
                labels = ax.get_xticklabels()
                plt.setp(labels, rotation=45, fontsize=10)
                ax.hist(dd,bins=10,range=(lower_num2,upper_num2))
                jikoku=["～７時","８時～１０時","１０時～１２時","１３時～１５時","１５時～１７時","１７時～"]
                # Matplotlib の Figure を指定して可視化する
                st.write("--------")
                
                st.write("""#### -----担当者:[""",t,"""]-------工程名称:[""",k,"""]-------図番:[""",z,"""]-------データ件数:[""",str(len(scores)),"""]-------時刻:[""",jikoku[i],"""]-----""")
                left_column, right_column = st.columns(2)
                left_column.pyplot(fig)

#=======================================================================================================================================================
elif selector=="　2.(ヒストグラム)作業時間[複数]":
    
    st.title("2.(ヒストグラム)作業時間[複数]")
    st.session_state.df['開始日時']=pd.to_datetime(st.session_state.df['開始日時'])
    #曜日の設定
    st.session_state.df["曜日"]=st.session_state.df["工程開始日"].dt.weekday
    #月の設定
    st.session_state.df["月"]=st.session_state.df["工程開始日"].dt.month
    #年の設定
    st.session_state.df["年"]=st.session_state.df["工程開始日"].dt.year
    #時刻の設定
    st.session_state.df["時刻"]=st.session_state.df["開始日時"].dt.hour
    st.session_state.df.loc[st.session_state.df['時刻'] <= 7, '時刻'] = 0
    st.session_state.df.loc[(st.session_state.df['時刻'] <= 9) & (st.session_state.df['時刻'] >= 8), '時刻'] = 1
    st.session_state.df.loc[(st.session_state.df['時刻'] <= 12) & (st.session_state.df['時刻'] >= 10), '時刻'] = 2
    st.session_state.df.loc[(st.session_state.df['時刻'] <= 14) & (st.session_state.df['時刻'] >= 13), '時刻'] = 3
    st.session_state.df.loc[(st.session_state.df['時刻'] <= 16) & (st.session_state.df['時刻'] >= 15), '時刻'] = 4
    st.session_state.df.loc[(st.session_state.df['時刻'] >= 17), '時刻'] = 5
    
    left_column, center_column ,right_column = st.columns(3)
   
    #図番の選択
    z_list = sorted(list(set(st.session_state.df["図番"])))
    z = left_column.selectbox(
         "図番",
         (z_list))
    x_num=st.session_state.df[(st.session_state.df["図番"]==z)]#dfからzで選んだ図番のデータ
    #工程の選択
    k_list = sorted(list(set(x_num["工程名称"])))
    k = center_column.selectbox(
         "工程名称",
         (k_list))
    x_num=st.session_state.df[(st.session_state.df["図番"]==z)&(st.session_state.df["工程名称"] == k)]#dfからz,kで選んだ図番,工程のデータ
    #担当の選択
    t_list = sorted(list(set(x_num["担当者"])))
    t = right_column.multiselect(
         "担当者",
         (t_list))
    
    #フィルター選択
    y_list = ["なし","曜日","月","年","時刻"]
    f_num = left_column.selectbox(
         "期間グループ分け",
         (y_list))
    
    #データ分析開始
    answer = st.button('分析開始')
    if answer == True:
        st.write("--------")
        #上限値、下限値のdata
        data_num=st.session_state.df[(st.session_state.df["図番"]==z)&(st.session_state.df["工程名称"]==k)]
        dosu_num=0
        
        for t_num in t_list:
            y_num=st.session_state.df[(st.session_state.df["図番"]==z)&(st.session_state.df["工程名称"]==k)&(st.session_state.df["担当者"] == t_num)]
            y_num=y_num["処理時間"]
            #y軸の上限値
            x,y,_= plt.hist(y_num)
            if dosu_num<max(x):#tが2個以上の時に比較する
                dosu_num=max(x)
        
        #処理時間の抜き出し
#         data_num=data_num.rename(columns={'処理時間': 'processing_time'}) 
        s_num=data_num['処理時間']
        
        # 描画領域を用意する
#         fig = plt.figure()
#         ax = fig.add_subplot()
#         ax.boxplot(s_num)#箱髭図作成
#         # Matplotlib の Figure を指定して可視化する
#         st.pyplot(fig)
        st.write("""### 箱ひげ図""")
        fig = go.Figure(px.box(s_num))
        st.plotly_chart(fig, use_container_width=True)
        
        syosai_num=data_num['処理時間'].describe()#データの詳細データ
        syosai_num = pd.DataFrame(syosai_num)
        syosai_num=syosai_num.set_axis(["個数","平均","標準偏差","最小値","第一四分位数","第二四分位数","第三四分位数","最大値"], axis=0)
        st.write(syosai_num.T)
        
        q1=data_num['処理時間'].describe().loc['25%']#第一四分位範囲
        q3=data_num['処理時間'].describe().loc['75%']#第三四分位範囲
                
        iqr=q3-q1#四分位範囲
        upper_num=q3+(1.5*iqr)#上限
        lower_num=q1-(1.5*iqr)#下限
        upper_num2=round(upper_num) #きりあげ
        lower_num2=math.floor(lower_num)#きりおとし
        dif_num=upper_num2-lower_num2#差
        dif_num3=0
        
        
        if dif_num%10!=0:#もし切り上げ切り落としした差が10で割れなかった
            dif_num2=math.ceil((dif_num/10))*10
            dif_num3=(dif_num2-dif_num)/2
        upper_num2=upper_num2+dif_num3
        lower_num2=lower_num2-dif_num3
        if dif_num <= 10:
            dif_num=10
            lower_num2=lower_num2-5
            upper_num2=upper_num2+5
        dif_num2=upper_num2-lower_num2#差
        hazure=data_num[data_num["処理時間"]<=upper_num]
        hazure=hazure[hazure["処理時間"]>=lower_num]
        
        hazure_num=data_num[(data_num["処理時間"]>upper_num) | (data_num["処理時間"]<lower_num)]
        hazure_num2=data_num[data_num["処理時間"]<lower_num]
        
        st.write("""### ＝＝＝外れ値のデータ＝＝＝""")
        st.write(hazure_num)#外れ値（データベース）の表示
        
#         st.write('第一四分位数は%.1fです'%q1)
#         st.write('第三四分位数は%.1fです'%q3)
#         st.write('四分位範囲は%.1fです'%iqr)
#         st.write('上限値は%.1fです'%upper_num)
#         st.write('下限値は%.1fです'%lower_num)
#         st.write('差は%.1fです'%dif_num)
#         st.write('差は%.1fです'%dif_num2)
#         st.write('外れてない数の割合は%d/%dです'%(len(hazure),len(data_num)))
#         st.write('上限値は%.1fです'%upper_num2)
#         st.write('下限値は%.1fです'%lower_num2)
        
        #全体のヒストグラムの作成
        zentai_x_num=st.session_state.df[(st.session_state.df["図番"]==z)&(st.session_state.df["工程名称"]==k)]
        zentai_scores=hazure[(hazure["図番"]==z)&(hazure["工程名称"]==k)]#選択したデータ
        zentai_dd=zentai_scores["処理時間"]#選択したデータの処理時間
        y_scores=st.session_state.df_time[(st.session_state.df_time["図番"]==z)&(st.session_state.df_time["工程名称"] ==k)]
        hyozyun1=y_scores["標準時間1"]
        hyozyun2=y_scores["標準時間2"]
        
        # 描画領域を用意する
        fig = plt.figure()
        ax = fig.add_subplot()
        
        plt.xlim([lower_num2,upper_num2])                        # X軸範囲
        plt.ylim([0,dosu_num+10])                      # Y軸範囲
        ax.set_title("chart")
        ax.set_xlabel("time")                # x軸ラベル
        plt.ylabel("count")               # y軸ラベル
        plt.grid(True)
        plt.axvline(x=int(hyozyun1),color = "crimson")#標準時間の表記（赤軸）
        plt.axvline(x=int(hyozyun2),color = "Blue")#標準時間の表記（軸）
        plt.xticks(np.arange(lower_num2, upper_num2,dif_num2/10))
        labels = ax.get_xticklabels()
        plt.setp(labels, rotation=45, fontsize=10)
        ax.hist(zentai_dd,bins=10,range=(lower_num2,upper_num2),rwidth=dif_num2/10)
        st.write("--------")
        st.write("""### ＝＝＝""",k,"""の社全体のグラフ＝＝＝""")
        left_column, right_column = st.columns(2)
        left_column.pyplot(fig)
        num=pd.DataFrame(zentai_scores.groupby(["図番","工程名称"])['処理時間'].agg(["count","mean", "median", "min", "max"]))
        pvit=num.set_axis(['件数', '平均', '中央値', '最小', '最大'], axis=1)
        pvit.insert(0, '総件数', len(zentai_x_num))
        pvit["標準時間1"]=int(hyozyun1)
        pvit["標準時間2"]=int(hyozyun2)
       
            
        if f_num=="なし":
            #ヒストグラムの作成
            for i in t:
                #データの整理
                x_num=st.session_state.df[(st.session_state.df["図番"]==z)&(st.session_state.df["工程名称"]==k)&(st.session_state.df["担当者"] == i)]
                scores=hazure[(hazure["図番"]==z)&(hazure["工程名称"]==k)&(hazure["担当者"]==i)]#選択したデータ

                dd=scores["処理時間"]#選択したデータの処理時間

                # 描画領域を用意する
                fig = plt.figure()
                ax = fig.add_subplot()

                plt.xlim([lower_num2,upper_num2])                        # X軸範囲
                plt.ylim([0,dosu_num+10])                      # Y軸範囲
                ax.set_title("chart")
                ax.set_xlabel("time")                # x軸ラベル
                plt.ylabel("count")               # y軸ラベル
                plt.grid(True)
                plt.axvline(x=int(hyozyun1),color = "crimson")#標準時間の表記（赤軸）
                plt.axvline(x=int(hyozyun2),color = "Blue")#標準時間の表記（軸）
                plt.xticks(np.arange(lower_num2, upper_num2,dif_num2/10))
                labels = ax.get_xticklabels()
                plt.setp(labels, rotation=45, fontsize=10)

                ax.hist(dd,bins=10,range=(lower_num2,upper_num2),rwidth=dif_num2/10)


                # Matplotlib の Figure を指定して可視化する
                st.write("--------")
                st.write("""#### -----担当者名：[""",i,"""]----------データ件数：[""",str(len(dd)),"""]-----""")
                
                left_column, right_column = st.columns(2)
                left_column.pyplot(fig)
                num=pd.DataFrame(scores.groupby(['担当者',"図番","工程名称"])['処理時間'].agg(["count","mean", "median", "min", "max"]))
                pvit=num.set_axis(['件数', '平均', '中央値', '最小', '最大'], axis=1)
                pvit.insert(0, '総件数', len(x_num))
                pvit["標準時間1"]=int(hyozyun1)
                pvit["標準時間2"]=int(hyozyun2)
                st.write(pvit)
            
        elif f_num=="曜日":
            #ヒストグラムの作成
            zen_list=pd.DataFrame()
            for i in t:
                kari_num=hazure[(hazure["図番"]==z)&(hazure["工程名称"]==k)&(hazure["担当者"]==i)]#選択したデータ
                zen_list=zen_list.append(kari_num)
            you_list = sorted(list(set(zen_list["曜日"])))
            for y in you_list:
                st.write("--------")
                for i in t:
                    #データの整理
                    x_num=st.session_state.df[(st.session_state.df["図番"]==z)&(st.session_state.df["工程名称"]==k)&(st.session_state.df["担当者"] == i)&(st.session_state.df["曜日"] == y)]
                    scores=hazure[(hazure["図番"]==z)&(hazure["工程名称"]==k)&(hazure["担当者"]==i)&(hazure["曜日"]==y)]#選択したデータ

                    dd=scores["処理時間"]#選択したデータの処理時間
                    
                    # 描画領域を用意する
                    fig = plt.figure()
                    ax = fig.add_subplot()

                    plt.xlim([lower_num2,upper_num2])                        # X軸範囲
                    plt.ylim([0,dosu_num+10])                      # Y軸範囲
                    ax.set_title("chart")
                    ax.set_xlabel("time")                # x軸ラベル
                    plt.ylabel("count")               # y軸ラベル
                    plt.grid(True)
                    plt.axvline(x=int(hyozyun1),color = "crimson")#標準時間の表記（赤軸）
                    plt.axvline(x=int(hyozyun2),color = "Blue")#標準時間の表記（軸）
                    plt.xticks(np.arange(lower_num2, upper_num2,dif_num2/10))
                    labels = ax.get_xticklabels()
                    plt.setp(labels, rotation=45, fontsize=10)

                    ax.hist(dd,bins=10,range=(lower_num2,upper_num2),rwidth=dif_num2/10)

                    youbi=["月","火","水","木","金","土","日"]
                    # Matplotlib の Figure を指定して可視化する
                    st.write("""#### -----担当者名：[""",i,"""]----------データ件数：[""",str(len(dd)),"""]----------曜日：[""",youbi[y],"""]-----""")
                    
                    left_column, right_column = st.columns(2)
                    left_column.pyplot(fig)
                    num=pd.DataFrame(scores.groupby(['担当者',"図番","工程名称"])['処理時間'].agg(["count","mean", "median", "min", "max"]))
                    pvit=num.set_axis(['件数', '平均', '中央値', '最小', '最大'], axis=1)
                    pvit.insert(0, '総件数', len(x_num))
                    pvit["標準時間1"]=int(hyozyun1)
                    pvit["標準時間2"]=int(hyozyun2)
                    st.write(pvit)
            
        elif f_num=="月":
            #ヒストグラムの作成
            zen_list=pd.DataFrame()
            for i in t:
                kari_num=hazure[(hazure["図番"]==z)&(hazure["工程名称"]==k)&(hazure["担当者"]==i)]#選択したデータ
                zen_list=zen_list.append(kari_num)
            tuki_list = sorted(list(set(zen_list["月"])))
            for tu in tuki_list:
                st.write("-----")
                for i in t:
                    #データの整理
                    x_num=st.session_state.df[(st.session_state.df["図番"]==z)&(st.session_state.df["工程名称"]==k)&(st.session_state.df["担当者"] == i)&(st.session_state.df["月"]==tu)]
                    scores=hazure[(hazure["図番"]==z)&(hazure["工程名称"]==k)&(hazure["担当者"]==i)&(hazure["月"]==tu)]#選択したデータ

                    dd=scores["処理時間"]#選択したデータの処理時間
                    # 描画領域を用意する
                    fig = plt.figure()
                    ax = fig.add_subplot()

                    plt.xlim([lower_num2,upper_num2])                        # X軸範囲
                    plt.ylim([0,dosu_num+10])                      # Y軸範囲
                    ax.set_title("chart")
                    ax.set_xlabel("time")                # x軸ラベル
                    plt.ylabel("count")               # y軸ラベル
                    plt.grid(True)
                    plt.axvline(x=int(hyozyun1),color = "crimson")#標準時間の表記（赤軸）
                    plt.axvline(x=int(hyozyun2),color = "Blue")#標準時間の表記（軸）
                    plt.xticks(np.arange(lower_num2, upper_num2,dif_num2/10))
                    labels = ax.get_xticklabels()
                    plt.setp(labels, rotation=45, fontsize=10)

                    
                    ax.hist(dd,bins=10,range=(lower_num2,upper_num2),rwidth=dif_num2/10)

                    # Matplotlib の Figure を指定して可視化する
                    st.write("""#### -----担当者名：[""",i,"""]----------データ件数：[""",str(len(dd)),"""]----------月：[""",str(tu),"""]-----""")
                   
                    left_column, right_column = st.columns(2)
                    left_column.pyplot(fig)
                    num=pd.DataFrame(scores.groupby(['担当者',"図番","工程名称"])['処理時間'].agg(["count","mean", "median", "min", "max"]))
                    pvit=num.set_axis(['件数', '平均', '中央値', '最小', '最大'], axis=1)
                    pvit.insert(0, '総件数', len(x_num))
                    pvit["標準時間1"]=int(hyozyun1)
                    pvit["標準時間2"]=int(hyozyun2)
                    st.write(pvit)
            
        elif f_num=="年":
            
            #ヒストグラムの作成
            zen_list=pd.DataFrame()
            for i in t:
                kari_num=hazure[(hazure["図番"]==z)&(hazure["工程名称"]==k)&(hazure["担当者"]==i)]#選択したデータ
                zen_list=zen_list.append(kari_num)
            nen_list = sorted(list(set(zen_list["年"])))
            for n in nen_list:
                st.write("-----")
                for i in t:
                    #データの整理
                    x_num=st.session_state.df[(st.session_state.df["図番"]==z)&(st.session_state.df["工程名称"]==k)&(st.session_state.df["担当者"] == i)&(st.session_state.df["年"] == n)]
                    scores=hazure[(hazure["図番"]==z)&(hazure["工程名称"]==k)&(hazure["担当者"]==i)&(hazure["年"]==n)]#選択したデータ

                    dd=scores["処理時間"]#選択したデータの処理時間
                        # 描画領域を用意する
                    fig = plt.figure()
                    ax = fig.add_subplot()

                    plt.xlim([lower_num2,upper_num2])                        # X軸範囲
                    plt.ylim([0,dosu_num+10])                      # Y軸範囲
                    ax.set_title("chart")
                    ax.set_xlabel("time")                # x軸ラベル
                    plt.ylabel("count")               # y軸ラベル
                    plt.grid(True)
                    plt.axvline(x=int(hyozyun1),color = "crimson")#標準時間の表記（赤軸）
                    plt.axvline(x=int(hyozyun2),color = "Blue")#標準時間の表記（軸）
                    plt.xticks(np.arange(lower_num2, upper_num2,dif_num2/10))
                    labels = ax.get_xticklabels()
                    plt.setp(labels, rotation=45, fontsize=10)

                    ax.hist(dd,bins=10,range=(lower_num2,upper_num2),rwidth=dif_num2/10)

                    # Matplotlib の Figure を指定して可視化する
                    st.write("""#### -----担当者名：[""",i,"""]----------データ個数：[""",str(len(dd)),"""]----------年：[""",str(n),"""]-----""")
                   
                    left_column, right_column = st.columns(2)
                    left_column.pyplot(fig)
                    num=pd.DataFrame(scores.groupby(['担当者',"図番","工程名称"])['処理時間'].agg(["count","mean", "median", "min", "max"]))
                    pvit=num.set_axis(['件数', '平均', '中央値', '最小', '最大'], axis=1)
                    pvit.insert(0, '総件数', len(x_num))
                    pvit["標準時間1"]=int(hyozyun1)
                    pvit["標準時間2"]=int(hyozyun2)
                    st.write(pvit)
            
        elif f_num=="時刻":
            #ヒストグラムの作成
            zen_list=pd.DataFrame()
            for i in t:
                kari_num=hazure[(hazure["図番"]==z)&(hazure["工程名称"]==k)&(hazure["担当者"]==i)]#選択したデータ
                zen_list=zen_list.append(kari_num)
            jikoku_list = sorted(list(set(zen_list["時刻"])))
            for j in jikoku_list:
                st.write("-----")
                for i in t:
                    #データの整理
                    x_num=st.session_state.df[(st.session_state.df["図番"]==z)&(st.session_state.df["工程名称"]==k)&(st.session_state.df["担当者"] == i)&(st.session_state.df["時刻"] == j)]
                    scores=hazure[(hazure["図番"]==z)&(hazure["工程名称"]==k)&(hazure["担当者"]==i)&(hazure["時刻"]==j)]#選択したデータ

                    dd=scores["処理時間"]#選択したデータの処理時間
                    # 描画領域を用意する
                    fig = plt.figure()
                    ax = fig.add_subplot()

                    plt.xlim([lower_num2,upper_num2])                        # X軸範囲
                    plt.ylim([0,dosu_num+10])                      # Y軸範囲
                    ax.set_title("chart")
                    ax.set_xlabel("time")                # x軸ラベル
                    plt.ylabel("count")               # y軸ラベル
                    plt.grid(True)
                    plt.axvline(x=int(hyozyun1),color = "crimson")#標準時間の表記（赤軸）
                    plt.axvline(x=int(hyozyun2),color = "Blue")#標準時間の表記（軸）
                    plt.xticks(np.arange(lower_num2, upper_num2,dif_num2/10))
                    labels = ax.get_xticklabels()
                    plt.setp(labels, rotation=45, fontsize=10)

                    ax.hist(dd,bins=10,range=(lower_num2,upper_num2),rwidth=dif_num2/10)

                    jikoku=["～７時","８時～１０時","１０時～１２時","１３時～１５時","１５時～１７時","１７時～"]
                    # Matplotlib の Figure を指定して可視化する
                    st.write("""#### -----担当者名：[""",i,"""]----------データ件数：[""",str(len(dd)),"""]----------時間帯：[""",jikoku[j],"""]-----""")
                    
                    left_column, right_column = st.columns(2)
                    left_column.pyplot(fig)
                    num=pd.DataFrame(scores.groupby(['担当者',"図番","工程名称"])['処理時間'].agg(["count","mean", "median", "min", "max"]))
                    pvit=num.set_axis(['件数', '平均', '中央値', '最小', '最大'], axis=1)
                    pvit.insert(0, '総件数', len(x_num))
                    pvit["標準時間1"]=int(hyozyun1)
                    pvit["標準時間2"]=int(hyozyun2)
                    st.write(pvit)
            
            
#================================================================================================================================
elif selector=="　1.(折れ線)仕掛品の推移":
    
    st.title("1.(折れ線)仕掛品の推移")
    left_column, center_column ,right_column = st.columns(3)
    day_num = sorted(list(set(st.session_state.df["工程完了日"])))#日付の抜出
    d_start = left_column.selectbox(#開始日の選択
         "開始日",
         (day_num))
    d_end = center_column.selectbox(#終了日の選択
         "終了日",
         (day_num))
    dt = d_end-d_start#開始日と終了日の差の計算
    dt= dt.days#int
    d_start1=d_start
    
    answer = st.button('分析開始')
    if answer == True:
        st.write("-------")
        k_list = sorted(list(set(st.session_state.df["工程名称"])))#全体データ（加工なし）から工程名称の抜出
        date_num = pd.DataFrame(columns=k_list)#列名だけ入れた表データ
        pvit_data=pd.DataFrame(index=k_list)
        
        #ガントチャート（総社内滞在時間）
        d_num=pd.DataFrame()
        for d in range(dt+1):#日のデータの追加文
            kari_num=st.session_state.df[(st.session_state.df["工程開始日"]==d_start)&(st.session_state.df["工程完了日"]==d_start)]
            d_num=d_num.append(kari_num)
            date_koutei_num=pd.DataFrame()#表データに入れる空データ
            s_list = sorted(list(set(d_num["製造番号"])))
            
            #製造番号で抜き出し
            for s in s_list:
                s_num=d_num[(d_num["製造番号"]==s)]
                s_num=s_num.sort_values(["完了日時"])
                date_koutei_num=date_koutei_num.append(s_num.tail(1))#期間内の最終工程の抜粋

            num=pd.DataFrame(date_koutei_num.groupby(["工程名称"])['作成数'].agg(["count"]))
            
            m=str(d_start.month)
            d=str(d_start.day)
            
            st.write("""#### --""",str(d_start.month),"""月""",str(d_start.day),"""日--""")
            pvit=num.set_axis([d_start], axis=1)
#             st.write(pvit)
            pvit_data=pd.merge(pvit_data,pvit, right_index=True, left_index=True, how='outer')
            
            #日ごとのガントチャート
            fig = go.Figure(px.bar(kari_num,x="製造番号",y="作成数",color="工程名称",text="担当者"))
            st.plotly_chart(fig, use_container_width=True)
            
            d_start = d_start + datetime.timedelta(days=1)
        
        #滞在時間
        zentai_list=pd.DataFrame(columns=["図番","総滞在時間"])
        
        end_num=d_num[(d_num["工程名称"]=="配送")]
        sei_list = sorted(list(set(end_num["製造番号"])))
        for s in sei_list:
            sei_num=d_num[(d_num["製造番号"]==s)]
            sta_num=[]
            end_num=[]
            for row in sei_num.itertuples():
                sta_num.append(row.開始日時)
                end_num.append(row.完了日時)
         
#             zentai_num=end_num[-1]-sta_num[0]
#             zen_num=pd.DataFrame(data={"図番":1,"総滞在時間":zentai_num}])
#             zentai_list=zentai_list.append(zen_num)
            
#         st.write(zentai_list)
        #仕掛表
        pvit_data=pvit_data.T
        pvit_data=pvit_data.fillna(0)
        
        #仕掛品の折れ線グラフ
        st.write("""#### 仕掛品の折れ線グラフ""")
        fig = px.line(pvit_data)
        st.plotly_chart(fig,use_container_width=True)
        
        #総社内滞在時間ガントチャート
        st.write("""#### 総社内滞在時間""")
        fig = go.Figure(px.timeline(d_num, x_start="開始日時", x_end="完了日時",text="処理時間",y="製造番号",color="工程名称"))
        fig.update_traces(textposition='inside', orientation="h")
        fig.update_yaxes(autorange='reversed')
        st.plotly_chart(fig,use_container_width=True)
        
 #================================================================================================================================      
#工程の画面
elif selector=="　1.(集計表)作業時間統計量":
    
    st.title("1.(集計表)作業時間統計量")
    left_column, center_column ,right_column = st.columns(3)
    
    #================データの選択（期間）
    day_num = sorted(list(set(st.session_state.df["工程開始日"])))#日付の抜出
    d_start = left_column.selectbox(#開始日の選択
         "開始日",
         (day_num))
    d_end = center_column.selectbox(#終了日の選択
         "終了日",
         (day_num))
    dt = d_end-d_start#開始日と終了日の差の計算
    dt= dt.days#int
    #===============
    left_column, center_column ,right_column = st.columns(3)
    num_list = ["工程名称","担当者","図番",]
    num_1 = left_column.selectbox(
         "1つ目",
         (num_list))
    num_2 = center_column.selectbox(
         "2つ目",
         (num_list))
    num_3= right_column.selectbox(
         "3つ目",
         (num_list))
    
    
    answer = st.button('分析開始')
    if answer == True:
        st.write("-------")
        #日のデータの追加文
        d_num=pd.DataFrame()
        for d in range(dt+1):
            kari_num=st.session_state.df[(st.session_state.df["工程開始日"]==d_start)&(st.session_state.df["工程完了日"]==d_start)]
            d_num=d_num.append(kari_num)
            d_start = d_start + datetime.timedelta(days=1)
        
        
        graph_num=pd.DataFrame()
        list_1=sorted(list(set(d_num[num_1])))
        for hazure_num1 in list_1:
            x_num=d_num[(d_num[num_1]==hazure_num1)]
            
            list_2=sorted(list(set(x_num[num_2])))
            for hazure_num2 in list_2:
                y_num=x_num[(x_num[num_2]==hazure_num2)]
                
                list_3 = sorted(list(set(y_num[num_3])))
                for hazure_num3 in list_3:
                    z_num=y_num[(y_num[num_3]==hazure_num3)]
                    

                    q1=z_num["処理時間"].describe().loc['25%']#第一四分位範囲
                    q3=z_num['処理時間'].describe().loc['75%']#第三四分位範囲
                    iqr=q3-q1#四分位範囲
                    upper_num=q3+(1.5*iqr)#上限
                    lower_num=q1-(1.5*iqr)#下限

                    hazure=z_num[z_num["処理時間"]<=upper_num]#外れ値の除外
                    hazure=hazure[hazure["処理時間"]>=lower_num]

                    Nohazure_num=len(hazure)
                    zentai_num=len(z_num)
                    Yeshazure_num=(zentai_num-Nohazure_num)

                    num=pd.DataFrame(hazure.groupby([num_1,num_2,num_3])['処理時間'].agg(["count","mean", "median", "min", "max"]))
                    pvit=num.set_axis(['件数', '平均', '中央値', '最小', '最大'], axis=1)
                    pvit.insert(0, '総件数', zentai_num)
                    
                   
#                     hyozyun1=z_num2["標準時間1"]
#                     hyozyun2=z_num2["標準時間2"]
#                     pvit["標準時間1"]=int(hyozyun1)
#                     pvit["標準時間2"]=int(hyozyun2)
                    graph_num=pd.concat([graph_num, pvit], axis=0)        
           
        st.write("""### 集計表""")
        st.dataframe(graph_num)
 #===============================================================================================================================================
elif selector=="　3.(棒グラフ)期間内の各人作業量":
    
    st.title("3.(棒グラフ)期間内の各人作業量")
    left_column, center_column ,right_column = st.columns(3)
    day_num = sorted(list(set(st.session_state.df["工程完了日"])))#日付の抜出
    d_start = left_column.selectbox(#開始日の選択
         "開始日",
         (day_num))
    d_end = center_column.selectbox(#終了日の選択
         "終了日",
         (day_num))
    dt = d_end-d_start#開始日と終了日の差の計算
    dt= dt.days#int
    d_start1=d_start
    
    #日のデータの追加文
    n_num=pd.DataFrame()
    for d in range(dt+1):
        kari_num=st.session_state.df[(st.session_state.df["工程開始日"]==d_start)&(st.session_state.df["工程完了日"]==d_start)]
        n_num=n_num.append(kari_num)
        d_start = d_start + datetime.timedelta(days=1)
        
    
    t_list = sorted(list(set(n_num["担当コード"])))
    
    hito_list = sorted(list(set(st.session_state.df["担当者"])))
    ko_list = sorted(list(set(st.session_state.df["工程名称"])))
    bar_num1=pd.DataFrame(columns=["担当者","工程名称","%"] )
    
    for t in hito_list:
        t_num=n_num[(n_num["担当者"]==t)]
        k_list = sorted(list(set(t_num["工程名称"])))
        for k in k_list:
            k_num=t_num[(t_num["工程名称"]==k)]
            r=round(100 * len(k_num) / len(t_num), 1)
            fruit_list = [ (t, k, r )]
            app_num = pd.DataFrame(fruit_list, columns = ["担当者","工程名称","%"])
            bar_num1=bar_num1.append(app_num,ignore_index=True)
            
    bar_num1=bar_num1.sort_values('担当者')
    n_num=n_num.sort_values('担当者')
    answer = st.button('分析開始')
    
    if answer == True:
        st.write("-------")
        #描画領域を用意する
        left_column, right_column = st.columns(2)
        st.write("""## 作業件数""")
 
        fig = go.Figure(px.bar(n_num,x="担当者",y="作成数",color="工程名称",text="図番"))
        st.plotly_chart(fig, use_container_width=True)
        
        st.write("""## 作業時間""")
        fig = go.Figure(px.bar(n_num,x="担当者",y="処理時間",color="工程名称",text="図番"))
        st.plotly_chart(fig, use_container_width=True)
        
        num=pd.DataFrame(n_num.groupby(["担当者","工程名称","図番"])['処理時間'].agg(["count","mean", "median", "min", "max"]))
        
        pvit=num.set_axis(['件数', '平均', '中央値', '最小', '最大'], axis=1)
        st.write("""### 集計表""")
        st.dataframe(pvit)
#         hyo_num=n_num[["図番","担当者","工程名称","号機名称","処理時間","開始日時","完了日時"]]
#         st.write("上記のグラフのデータベース")
#         st.dataframe(hyo_num)
#         st.write("各人一日の仕事量の％")
#         st.dataframe(bar_num1)
#         fig = go.Figure(px.bar(bar_num1,x="担当者",y="%",text="%",color="工程名称"))
#         st.plotly_chart(fig, use_container_width=True)
        