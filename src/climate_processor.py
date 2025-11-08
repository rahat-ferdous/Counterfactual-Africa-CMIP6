import xarray as xr
import pandas as pd
import numpy as np

class ClimateDataProcessor:
    def __init__(self):
        self.ssp_definitions = {
            'SSP1-2.6': {
                'name': 'Sustainability',
                'forcing': 2.6,
                'description': 'Green growth, low challenges',
                'color': '#2E8B57'  # SeaGreen
            },
            'SSP2-4.5': {
                'name': 'Middle Road', 
                'forcing': 4.5,
                'description': 'Historical patterns continue',
                'color': '#FFA500'  # Orange
            },
            'SSP3-7.0': {
                'name': 'Regional Rivalry',
                'forcing': 7.0, 
                'description': 'High challenges, fragmentation',
                'color': '#DC143C'  # Crimson
            },
            'SSP5-8.5': {
                'name': 'Fossil-fueled Development',
                'forcing': 8.5,
                'description': 'Rapid growth, high emissions',
                'color': '#8B0000'  # DarkRed
            }
        }
    
    def load_cmip6_data(self, ssp_scenario, variable='tas', region='Africa'):
        """Load CMIP6 climate projections for a specific SSP"""
        # For demo, we create synthetic data. Replace with actual CMIP6 data later.
        
        years = np.arange(2020, 2101)
        
        # Base climate with SSP-specific warming trends
        warming_rates = {
            'SSP1-2.6': 0.01,  # °C/year
            'SSP2-4.5': 0.02,
            'SSP3-7.0': 0.03, 
            'SSP5-8.5': 0.04
        }
        
        base_temp = 25.0  # Base temperature for Africa
        temperatures = base_temp + warming_rates[ssp_scenario] * (years - 2020)
        
        # Add realistic interannual variability
        np.random.seed(42)  # For reproducible results
        noise = np.random.normal(0, 0.5, len(years))
        temperatures += noise
        
        # Precipitation changes (SSP-specific)
        precip_trends = {
            'SSP1-2.6': -0.5,    # mm/year
            'SSP2-4.5': -1.0,
            'SSP3-7.0': -2.0,
            'SSP5-8.5': -3.0
        }
        
        base_precip = 800  # mm/year base
        precipitation = base_precip + precip_trends[ssp_scenario] * (years - 2020)
        precip_noise = np.random.normal(0, 50, len(years))
        precipitation = np.maximum(200, precipitation + precip_noise)  # Minimum 200mm
        
        return pd.DataFrame({
            'year': years,
            'temperature': temperatures,
            'precipitation': precipitation,
            'scenario': ssp_scenario,
            'forcing': self.ssp_definitions[ssp_scenario]['forcing']
        })
    
    def calculate_climate_anomalies(self, scenario_data, baseline_period=(1991, 2020)):
        """Calculate climate anomalies relative to baseline"""
        baseline_mask = (scenario_data['year'] >= baseline_period[0]) & (scenario_data['year'] <= baseline_period[1])
        baseline_temp = scenario_data[baseline_mask]['temperature'].mean()
        baseline_precip = scenario_data[baseline_mask]['precipitation'].mean()
        
        scenario_data['temp_anomaly'] = scenario_data['temperature'] - baseline_temp
        scenario_data['precip_anomaly'] = (scenario_data['precipitation'] - baseline_precip) / baseline_precip * 100
        
        return scenario_data
