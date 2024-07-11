import folium
from folium import plugins
import branca.colormap as cm
import streamlit as st

class MapVisualizer:
    def __init__(self, data):
        self.data = data
        
    def create_base_map(self, map_style='CartoDB positron'):
        if map_style == 'Stamen Terrain':
            m = folium.Map(
                location=[0, 0], 
                zoom_start=2, 
                tiles='Stamen Terrain', 
                attr='Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.'
            )
        else:
            m = folium.Map(location=[0, 0], zoom_start=2, tiles=map_style)
        return m
    
    def add_choropleth_layer(self, m, column, name, legend_name):
        folium.Choropleth(
            geo_data=self.data,
            name=name,
            data=self.data,
            columns=['NAME', column],
            key_on='feature.properties.NAME',
            fill_color='YlOrRd',
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name=legend_name,
            smooth_factor=0
        ).add_to(m)
        
    def add_bubble_layer(self, m, column, name, scale=5000):
        for idx, row in self.data.iterrows():
            folium.CircleMarker(
                location=[row['geometry'].centroid.y, row['geometry'].centroid.x],
                radius=scale * row[column],
                popup=f"{row['NAME']}: {row[column]:.2f}",
                color='blue',
                fill=True,
                fillColor='blue'
            ).add_to(m)
        
    def create_impact_map(self, map_style='CartoDB positron'):
        m = self.create_base_map(map_style)
        self.add_choropleth_layer(m, 'Temperature_Change', 'Sıcaklık Değişimi', 'Sıcaklık Değişimi')
        self.add_bubble_layer(m, 'CO2_Emissions', 'CO2 Emisyonları')
        folium.LayerControl().add_to(m)
        return m

def get_map_style():
    styles = {
        'Varsayılan': 'CartoDB positron',
        'Uydu': 'Stamen Terrain',
        'Karanlık': 'CartoDB dark_matter'
    }
    selected_style = st.sidebar.selectbox("Harita Stilini Seçin", list(styles.keys()))
    return styles[selected_style]
