import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
import rasterio
from PIL import Image
import numpy as np

rc('font', family='NanumGothic')
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="Urban Change Prediction", layout="wide")

# ---------------- Header ----------------
st.markdown("<h1 style='font-size:38px; font-weight:700;'>Urban Change Prediction</h1>", unsafe_allow_html=True)
st.caption("도시 변동 예측 AI 모델 결과 시각화")

col_input1, col_input2 = st.columns(2)
with col_input1:
    past_year = st.slider("연도 선택", min_value=2015, max_value=2030, value=2015, step=5)
with col_input2:
    region = st.selectbox("지역 선택", ["전주", "남원"])

# ---------------- 전주 픽셀 기반 도시/녹지 지표 ----------------
pixel_stats = {
    2015: {"urban": 813366 + 64655, "green": 178289 + 183969,
           "total": 813366 + 64655 + 178289 + 183969 + 3422921},
    2020: {"urban": 1527908 + 99917, "green": 283232 + 411598,
           "total": 1527908 + 99917 + 283232 + 411598 + 7274387},
    2025: {"urban": 1323417 + 74760, "green": 403307 + 55204,
           "total": 1323417 + 74760 + 403307 + 55204 + 2806512},
}

if region == "전주":
    if past_year in [2020, 2025]:
        prev_year = 2015 if past_year == 2020 else 2020

        curr_urban = pixel_stats[past_year]["urban"] / pixel_stats[past_year]["total"] * 100
        curr_green = pixel_stats[past_year]["green"] / pixel_stats[past_year]["total"] * 100
        prev_urban = pixel_stats[prev_year]["urban"] / pixel_stats[prev_year]["total"] * 100
        prev_green = pixel_stats[prev_year]["green"] / pixel_stats[prev_year]["total"] * 100

        diff_urban = curr_urban - prev_urban
        diff_green = curr_green - prev_green

        urban_icon = "📈" if diff_urban > 0 else "📉"
        green_icon = "📈" if diff_green > 0 else "📉"

        st.markdown(
            f"""
            <div style="display:flex; justify-content:center; gap:25px; margin:10px 0;">
                <div style="background:#f4f8ff; border-radius:10px; padding:12px; width:220px; text-align:center;">
                    <b>도시 확장률</b><br>
                    {curr_urban:.2f}% ({urban_icon} {diff_urban:+.2f}%p)
                </div>
                <div style="background:#f7fff4; border-radius:10px; padding:12px; width:220px; text-align:center;">
                    <b>녹지율</b><br>
                    {curr_green:.2f}% ({green_icon} {diff_green:+.2f}%p)
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.info("도시 확장률 / 녹지율 지표는 2020년 또는 2025년 선택 시 표시됩니다.")

st.markdown("---")

# ---------------- 이미지 경로 ----------------
pred_images = {
    "전주": {
        2015: "images/urban_pred/전주_2015.tif",
        2020: "images/urban_pred/전주_2020.tif",
        2025: "images/urban_pred/전주_2025.tif",
        2030: "images/urban_pred/전주_2030.png",
    },
    "남원": {
        2015: "images/urban_pred/남원_2015.png",
        2020: "images/urban_pred/남원_2021.png",
        2025: "images/urban_pred/남원_2025.png",
        2030: "images/urban_pred/남원_2030.png",
    }
}

aerial_images = {
    "전주": {
        2015: "images/aerial/전주_2015.tif",
        2020: "images/aerial/전주_2020.tif",
        2025: "images/aerial/전주_2025.tif",
    },
    "남원": {
        2015: "images/aerial/namwon_2015.tif",
        2020: "images/aerial/namwon_2021.tif",
        2025: "images/aerial/namwon_2025.tif",
    }
}

# ---------------- 인사이트 카드 ----------------
if region == "전주":
    insight_text = """
        <b>전주</b> 지역은 <b style='color:#0F9D58'>도시 확장세</b>를 보이고 있습니다.<br>
        외곽 지역으로 점차 확장되는 경향이 확인됩니다.
    """
    icon = "🌆"

elif region == "남원":
    insight_text = """
        <b>남원</b> 지역은 <b style='color:#DB4437'>도시 축소세</b>를 보이고 있습니다.<br>
        지속적인 인구 감소와 함께 도심 밀도가 낮아질 가능성이 있습니다.
    """
    icon = "🏘️"

st.markdown(
    f"""
    <div style='display:flex; align-items:center; justify-content:center;
                background-color:#f5f7fa; padding:15px 20px; border-radius:15px;
                box-shadow:0 2px 8px rgba(0,0,0,0.08); margin:15px 0;'>
        <span style='font-size:26px; margin-right:12px;'>{icon}</span>
        <span style='font-size:15px;'>{insight_text}</span>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")
# ---------------- Display Section ----------------
st.subheader("도시 변동 예측 & 인구 변화")

cols_compare = st.columns([1.2, 1])

with cols_compare[0]:
    try:
        with rasterio.open(pred_images[region][past_year]) as src:
            arr = src.read()
            img = np.transpose(arr, (1,2,0))
            st.image(img, caption=f"{region} 도시 예측 ({past_year})", use_container_width=True)
    except:
        st.warning("도시 예측 이미지 불러오기 실패")

with cols_compare[1]:
    if region == '전주':
        years = [2015, 2020, 2025]
        population = [652282, 657432, 629000]
    else:
        years = [2015, 2020, 2025]
        population = [84000, 77000, 74000]

    fig, ax = plt.subplots()
    ax.plot(years, population, marker="o", linewidth=5)
    ax.set_title(f"{region} 인구 변화")
    ax.grid(True)
    st.pyplot(fig)

st.markdown("---")

# ---------------- Aerial comparison ----------------
st.subheader("항공사진 비교")

colA, colB = st.columns(2)

with colA:
    if past_year == 2030:
        st.info(f"{region} {past_year}년 항공사진 준비중입니다 ⏳")
    else:
        st.image(aerial_images[region][past_year],
                 caption=f"{region} 항공사진 ({past_year})",
                 use_container_width=True)

with colB:
    st.image(aerial_images[region][2025],
             caption=f"{region} 항공사진 (2025)",
             use_container_width=True)

st.caption("Developed — Smart Farm Urban Change Prediction Project")
