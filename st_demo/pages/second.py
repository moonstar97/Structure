import folium
import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import requests
import json
from streamlit_folium import st_folium

st.set_page_config(
    # page_title="Likelion AI School",
    layout="wide",
)

###########################################################################################################################################
DATA_URL = "https://raw.githubusercontent.com/wumusill/Structure/main/dataset_eda/seoul_stop_school.csv"


@st.cache(allow_output_mutation=True)
def load_data():
    data = pd.read_csv(DATA_URL)
    data.index = ["2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020"]
    data = data.astype("float")
    return data


data = load_data()


# 학교 조건
selected_school = st.selectbox("학교", ["초등학교", "중학교", "고등학교"])
condition = data.columns.str.contains(f"{selected_school} 학업중단율")
school_data = data.loc[:, condition]

if st.checkbox('Show data'):
    st.subheader('data')
    st.write(school_data)


# 연도 조건
year_to_filter = st.slider('연도', 2011, 2020, 2015)
year_condition = school_data.index == str(year_to_filter)
year_school_data = school_data[year_condition].T

df_temp = year_school_data
df_temp = df_temp.reset_index()
df_temp = df_temp.rename(columns={'index':'name'})
df_temp = df_temp.drop(0)
df_temp["name"] = df_temp["name"].map(lambda x: x.split()[0])
# df_temp


m = folium.Map(location=[37.566345, 126.977893],
    zoom_start = 11,
    tiles = 'Stamen Terrain')

# 구별 위경도 json
geo_url = 'https://raw.githubusercontent.com/southkorea/seoul-maps/master/kostat/2013/json/seoul_municipalities_geo_simple.json'
response = requests.get(geo_url)
geo_json = json.loads(response.content)


folium.GeoJson(geo_json,
              name="지역구").add_to(m)


# 행정구역 경계 표시, 중단율 색칠
m.choropleth(geo_data=geo_json,
                 name="지역구",
                 data=df_temp,
                 columns=[df_temp.columns[0], df_temp.columns[1]],
                 key_on="properties.name",
                 fill_color='YlGn',
                 fill_opacity=0.7,
                 line_opacity=0.2
                 )


# 출력
st_data = st_folium(m, width=2100)

###########################################################################################################################################
# 사교육비 데이터 로드
@st.cache(allow_output_mutation=True)
def load_private_data():
    data = pd.read_csv("https://raw.githubusercontent.com/wumusill/Structure/main/dataset/seoul_private.csv")
    data = data.drop([0, 1, 2])
    return data


private_data = load_private_data()
private_data.columns = ["시점", "평균 사교육비", "평균 사교육 참여율(%)", 
                    "초등학교 사교육비", "초등 사교육 참여율(%)", 
                    "중학교 사교육비", "중등 사교육 참여율(%)", 
                    "고등학교 사교육비", "고등 사교육 참여율(%)", 
                    "일반고 사교육비", "일반고 사교육 참여율(%)"]
private_data = private_data.astype('float')

condition = private_data.columns.str.contains("사교육비")
ratio_df = private_data.loc[:, ~condition]
ratio_df.index = ["11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21"]

cost_df = private_data.loc[:, condition]
cost_df.index = ["11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21"]



# 1인당 평균 사교육비 그래프
fig = plt.figure(figsize=(10, 3))
# fig, axs = plt.subplots(nrows=1, ncols=1)
sns.lineplot(data=cost_df, x=cost_df.index, y="평균 사교육비", label="평균")
sns.lineplot(data=cost_df, x=cost_df.index, y="초등학교 사교육비", label="초등학교")
sns.lineplot(data=cost_df, x=cost_df.index, y="중학교 사교육비", label="중학교")
sns.lineplot(data=cost_df, x=cost_df.index, y="고등학교 사교육비", label="고등학교")
sns.lineplot(data=cost_df, x=cost_df.index, y="일반고 사교육비", label="일반고")
plt.legend(bbox_to_anchor=(1, 1))
plt.title("1인당 평균 사교육비 (만원)")
plt.axvline(x = '15',linestyle='--')
plt.axvline(x = '19',linestyle='--')
st.pyplot(fig)

# 사교육 참여율 그래프
fig = plt.figure(figsize=(10, 3))
# fig, axs = plt.subplots(nrows=2, ncols=1)
sns.lineplot(data=ratio_df, x=ratio_df.index, y="평균 사교육 참여율(%)", label="평균")
sns.lineplot(data=ratio_df, x=ratio_df.index, y="초등 사교육 참여율(%)", label="초등")
sns.lineplot(data=ratio_df, x=ratio_df.index, y="중등 사교육 참여율(%)", label="중등")
sns.lineplot(data=ratio_df, x=ratio_df.index, y="고등 사교육 참여율(%)", label="고등")
sns.lineplot(data=ratio_df, x=ratio_df.index, y="일반고 사교육 참여율(%)", label="일반고")
plt.legend(bbox_to_anchor=(1, 1))
plt.title("사교육 참여율 (%)")
plt.axvline(x = '15',linestyle='--')
plt.axvline(x = '19',linestyle='--')
st.pyplot(fig)

###########################################################################################################################################
# 국제 학업성취도 성적
# 국어 로드
@st.cache(allow_output_mutation=True)
def load_national_reading():
    data = pd.read_excel("https://raw.githubusercontent.com/wumusill/Structure/main/dataset/international_test.xls", sheet_name=0)
    return data

national_reading = load_national_reading()
national_reading[["Average", "Standard Error"]] = national_reading[["Average", "Standard Error"]].astype("float")


# 수학 로드
@st.cache(allow_output_mutation=True)
def load_national_math():
    data = pd.read_excel("https://raw.githubusercontent.com/wumusill/Structure/main/dataset/international_test.xls", sheet_name=1)
    return data

national_math = load_national_math()
national_math[["Average", "Standard Error"]] = national_math[["Average", "Standard Error"]].astype("float")


# 과학 로드
@st.cache(allow_output_mutation=True)
def load_national_science():
    data = pd.read_excel("https://raw.githubusercontent.com/wumusill/Structure/main/dataset/international_test.xls", sheet_name=2)
    return data

national_science = load_national_science()
national_science[["Average", "Standard Error"]] = national_science[["Average", "Standard Error"]].astype("float")

# 읽기 top5
reading_top5 = national_reading.sort_values(["Year/Study", "Average"], ascending=[True, False])
reading_top5 = reading_top5.groupby("Year/Study").head()

# 수학 top5
math_top5 = national_math.sort_values(["Year/Study", "Average"], ascending=[True, False])
math_top5 = math_top5.groupby("Year/Study").head()

# 과학 top5
science_top5 = national_science.sort_values(["Year/Study", "Average"], ascending=[True, False])
science_top5 = science_top5.groupby("Year/Study").head()

# 읽기 시각화
fig, ax = plt.subplots(figsize=(10, 3))
lm_reading = sns.lmplot(data=reading_top5, x="Year/Study", y="Average", hue='Jurisdiction', ci=None)
st.pyplot(lm_reading)

# 수학 시각화
fig, ax = plt.subplots(figsize=(10, 3))
lm_math = sns.lmplot(data=math_top5, x="Year/Study", y="Average", hue='Jurisdiction', ci=None)
st.pyplot(lm_math)

# 과학 시각화
fig, ax = plt.subplots(figsize=(10, 3))
lm_science = sns.lmplot(data=science_top5, x="Year/Study", y="Average", hue='Jurisdiction', ci=None)
st.pyplot(lm_science)

# 국내 학업성취도 성적

