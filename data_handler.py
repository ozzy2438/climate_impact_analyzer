import geopandas as gpd
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

class DataHandler:
    def __init__(self):
        url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
        self.world = gpd.read_file(url)
        self.climate_data = pd.DataFrame({
            'Country': self.world['NAME'],
            'Temperature_Change': np.random.uniform(0, 2, len(self.world)),
            'CO2_Emissions': np.random.uniform(0, 1000, len(self.world)),
            'Sea_Level_Rise': np.random.uniform(0, 0.5, len(self.world))
        })
        
    def preprocess_data(self):
        self.merged_data = self.world.merge(self.climate_data, how='left', left_on=['NAME'], right_on=['Country'])
        self.merged_data.fillna(0, inplace=True)
        
        scaler = MinMaxScaler()
        numerical_columns = ['Temperature_Change', 'CO2_Emissions', 'Sea_Level_Rise']
        self.merged_data[numerical_columns] = scaler.fit_transform(self.merged_data[numerical_columns])
        
    def get_data(self):
        return self.merged_data
