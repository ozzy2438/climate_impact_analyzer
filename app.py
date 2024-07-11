import streamlit as st
import folium
from streamlit_folium import folium_static
import plotly.express as px
import pandas as pd
import geopandas as gpd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
import base64
import ssl
import openai
from map_visualizer import MapVisualizer, get_map_style
from data_handler import DataHandler

ssl._create_default_https_context = ssl._create_unverified_context

st.set_page_config(layout="wide", page_title="Küresel İklim Değişikliği Etki Analizörü")

# Custom CSS
st.markdown("""
<style>
    .reportview-container {
        background: linear-gradient(to right, #FFFFFF, #E0F7FA);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(to bottom, #4CAF50, #2196F3);
    }
    h1 {
        color: #1565C0;
        font-family: 'Helvetica', sans-serif;
        font-weight: bold;
        text-align: center;
        padding: 20px;
        border-bottom: 2px solid #1565C0;
    }
    .stButton>button {
        color: #ffffff;
        background-color: #4CAF50;
        border-radius: 5px;
    }
    .stSelectbox {
        color: #1565C0;
    }
</style>
""", unsafe_allow_html=True)

openai.api_key = "sk-proj-1hyuWddhOwZgNJHHS9x7T3BlbkFJelhnlFpXxcYFJcnefCur"

@st.cache_data
def load_data():
    data_handler = DataHandler()
    data_handler.preprocess_data()
    return data_handler.get_data()

def add_ml_prediction(data):
    X = data[['CO2_Emissions', 'Sea_Level_Rise']]
    y = data['Temperature_Change']
    model = LinearRegression().fit(X, y)
    data['Predicted_Temperature_Change'] = model.predict(X)
    return data

def get_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="iklim_verisi.csv">CSV Dosyasını İndir</a>'
    return href

def generate_climate_scenario(country, temperature_change, co2_emissions, sea_level_rise):
    prompt = f"""
    Ülke: {country}
    Sıcaklık Değişimi: {temperature_change}°C
    CO2 Emisyonları: {co2_emissions} metrik ton
    Deniz Seviyesi Yükselmesi: {sea_level_rise} metre

    Bu verilere dayanarak, gelecek 50 yıl için olası bir iklim senaryosu oluşturun ve bu senaryoya karşı alınabilecek 3 önlem önerin.
    Lütfen yanıtınızı şu formatta verin:
    Senaryo: [senaryo metni]
    Önlemler:
    1. [önlem 1]
    2. [önlem 2]
    3. [önlem 3]
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Sen bir iklim uzmanısın."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        n=1,
        temperature=0.7,
    )

    return response.choices[0].message['content'].strip()

def main():
    st.title("Küresel İklim Değişikliği Etki Analizörü")
    
    data = load_data()
    data = add_ml_prediction(data)
    map_viz = MapVisualizer(data)
    
    st.sidebar.header("Filtreler")
    selected_indicator = st.sidebar.selectbox("Gösterge Seçin", ['Temperature_Change', 'CO2_Emissions', 'Sea_Level_Rise', 'Predicted_Temperature_Change'])
    
    map_style = get_map_style()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Küresel Etki Haritası")
        m = map_viz.create_impact_map(map_style=map_style)
        folium_static(m, width=800, height=500)
    
    with col2:
        st.subheader("En Çok Etkilenen 10 Ülke")
        top_10 = data.nlargest(10, selected_indicator)
        fig = px.bar(top_10, x='NAME', y=selected_indicator, title=f"{selected_indicator} için En Yüksek 10 Ülke")
        st.plotly_chart(fig)
    
    st.subheader("Korelasyon Analizi")
    correlation_matrix = data[['Temperature_Change', 'CO2_Emissions', 'Sea_Level_Rise', 'Predicted_Temperature_Change']].corr()
    fig = px.imshow(correlation_matrix, text_auto=True, aspect="auto")
    st.plotly_chart(fig)
    
    st.subheader("Etkileşimli Dağılım Grafiği")
    x_axis = st.selectbox("X-ekseni", ['Temperature_Change', 'CO2_Emissions', 'Sea_Level_Rise', 'Predicted_Temperature_Change'])
    y_axis = st.selectbox("Y-ekseni", ['Temperature_Change', 'CO2_Emissions', 'Sea_Level_Rise', 'Predicted_Temperature_Change'])
    fig = px.scatter(data, x=x_axis, y=y_axis, hover_name='NAME', title=f"{x_axis} ve {y_axis}")
    st.plotly_chart(fig)
    
    st.subheader("Veriyi İndir")
    st.markdown(get_download_link(data), unsafe_allow_html=True)

    st.subheader("İklim Senaryosu Üreteci")
    selected_country = st.selectbox("Ülke Seçin", data['NAME'].unique())
    if st.button("Senaryo Üret"):
        country_data = data[data['NAME'] == selected_country].iloc[0]
        scenario = generate_climate_scenario(
            selected_country,
            country_data['Temperature_Change'],
            country_data['CO2_Emissions'],
            country_data['Sea_Level_Rise']
        )
        
        st.write(scenario)
        
        # Senaryo sonuçlarını haritada göster
        m = map_viz.create_impact_map(map_style=map_style)
        folium.Marker(
            location=[country_data['geometry'].centroid.y, country_data['geometry'].centroid.x],
            popup=scenario,
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
        folium_static(m, width=800, height=500)
        
        # İlgili kaynaklar
        st.subheader("İlgili Kaynaklar")
        st.markdown("""
        - [IPCC Raporları](https://www.ipcc.ch/reports/)
        - [NASA İklim Değişikliği](https://climate.nasa.gov/)
        - [Dünya Meteoroloji Örgütü](https://public.wmo.int/en)
        - [Birleşmiş Milletler İklim Değişikliği](https://unfccc.int/)
        """)

if __name__ == "__main__":
    main()
