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

st.set_page_config(layout="wide", page_title="Global Climate Change Impact Analyzer")

# Advanced CSS
st.markdown("""
<style>
    /* General style */
    body {
        font-family: 'Helvetica', sans-serif;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        color: #333;
    }
    
    /* Title style */
    h1 {
        color: #1565C0;
        font-weight: bold;
        text-align: center;
        padding: 20px;
        border-bottom: 2px solid #1565C0;
        shape-outside: circle(50%);
        float: left;
        width: 100%;
        height: 100px;
        margin-bottom: 20px;
    }
    
    /* Subtitle style */
    h2 {
        color: #4CAF50;
        text-align: left;
        padding: 10px;
        border-left: 5px solid #4CAF50;
        margin-top: 30px;
    }
    
    /* Button style */
    .stButton > button {
        color: #ffffff;
        background-color: #4CAF50;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton > button:hover {
        background-color: #45a049;
        box-shadow: 0 6px 8px rgba(0,0,0,0.15);
    }
    
    /* Selectbox style */
    .stSelectbox {
        color: #1565C0;
        background-color: #f1f8e9;
        border-radius: 5px;
        padding: 5px;
    }
    
    /* Text style */
    p {
        text-align: justify;
        line-height: 1.6;
        margin-bottom: 15px;
        hyphens: auto;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    
    /* Chart container style */
    .chart-container {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    /* Scrollbar style */
    ::-webkit-scrollbar {
        width: 12px;
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    ::-webkit-scrollbar-thumb {
        background-color: #888;
        border-radius: 6px;
        border: 3px solid #f1f1f1;
    }
    ::-webkit-scrollbar-thumb:hover {
        background-color: #555;
    }
    
    /* Animation */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    .fade-in {
        animation: fadeIn 1s ease-in;
    }
</style>
""", unsafe_allow_html=True)

openai.api_key = ""

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
    href = f'<a href="data:file/csv;base64,{b64}" download="climate_data.csv">Download CSV File</a>'
    return href

def generate_climate_scenario(country, temperature_change, co2_emissions, sea_level_rise):
    prompt = f"""
    Country: {country}
    Temperature Change: {temperature_change}°C
    CO2 Emissions: {co2_emissions} metric tons
    Sea Level Rise: {sea_level_rise} meters

    Based on this data, create a possible climate scenario for the next 50 years and suggest 3 measures for this scenario.
    Please provide your answer in the following format:
    Scenario: [scenario text]
    Measures:
    1. [measure 1]
    2. [measure 2]
    3. [measure 3]
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a climate expert."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        n=1,
        temperature=0.7,
    )

    return response.choices[0].message['content'].strip()

def main():
    st.title("Global Climate Change Impact Analyzer")
    
    data = load_data()
    data = add_ml_prediction(data)
    map_viz = MapVisualizer(data)
    
    st.sidebar.header("Filters")
    selected_indicator = st.sidebar.selectbox("Select Indicator", ['Temperature_Change', 'CO2_Emissions', 'Sea_Level_Rise', 'Predicted_Temperature_Change'])
    
    map_style = get_map_style()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Global Impact Map")
        m = map_viz.create_impact_map(map_style=map_style)
        folium_static(m, width=800, height=500)
    
    with col2:
        st.subheader("Top 10 Most Affected Countries")
        top_10 = data.nlargest(10, selected_indicator)
        fig = px.bar(top_10, x='NAME', y=selected_indicator, title=f"Top 10 Countries for {selected_indicator}")
        st.plotly_chart(fig)
    
    st.subheader("Correlation Analysis")
    correlation_matrix = data[['Temperature_Change', 'CO2_Emissions', 'Sea_Level_Rise', 'Predicted_Temperature_Change']].corr()
    fig = px.imshow(correlation_matrix, text_auto=True, aspect="auto")
    st.plotly_chart(fig)
    
    st.subheader("Interactive Scatter Plot")
    x_axis = st.selectbox("X-axis", ['Temperature_Change', 'CO2_Emissions', 'Sea_Level_Rise', 'Predicted_Temperature_Change'])
    y_axis = st.selectbox("Y-axis", ['Temperature_Change', 'CO2_Emissions', 'Sea_Level_Rise', 'Predicted_Temperature_Change'])
    fig = px.scatter(data, x=x_axis, y=y_axis, hover_name='NAME', title=f"{x_axis} vs {y_axis}")
    st.plotly_chart(fig)
    
    st.subheader("Data Download")
    st.markdown(get_download_link(data), unsafe_allow_html=True)

    st.subheader("Climate Scenario Generator")
    selected_country = st.selectbox("Select Country", data['NAME'].unique())
    if st.button("Generate Scenario"):
        country_data = data[data['NAME'] == selected_country].iloc[0]
        scenario = generate_climate_scenario(
            selected_country,
            country_data['Temperature_Change'],
            country_data['CO2_Emissions'],
            country_data['Sea_Level_Rise']
        )
        
        st.markdown('<p class="fade-in">{}</p>'.format(scenario), unsafe_allow_html=True)
        
        # Show scenario results on the map
        m = map_viz.create_impact_map(map_style=map_style)
        folium.Marker(
            location=[country_data['geometry'].centroid.y, country_data['geometry'].centroid.x],
            popup=scenario,
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
        folium_static(m, width=800, height=500)
        
        # Related resources
        st.subheader("Related Resources")
        st.markdown("""
        - [IPCC Reports](https://www.ipcc.ch/reports/)
        - [NASA Climate Change](https://climate.nasa.gov/)
        - [World Meteorological Organization](https://public.wmo.int/en)
        - [United Nations Climate Change](https://unfccc.int/)
        """)

    # Example: Shaped container
    st.markdown("""
    <div style="
        width: 200px;
        height: 200px;
        background-color: #4CAF50;
        clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
    ">
        Climate Change
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
