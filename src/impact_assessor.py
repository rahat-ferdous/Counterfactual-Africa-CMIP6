import pandas as pd
import numpy as np

class ImpactAssessor:
    def __init__(self):
        self.metrics = {}
    
    def calculate_impacts(self, scenarios_df, baseline_scenario='SSP2-4.5'):
        """Calculate climate impacts relative to baseline scenario"""
        
        impacts = []
        
        for ssp in scenarios_df['scenario'].unique():
            if ssp == baseline_scenario:
                continue
                
            ssp_data = scenarios_df[scenarios_df['scenario'] == ssp].copy()
            baseline_data = scenarios_df[scenarios_df['scenario'] == baseline_scenario].copy()
            
            # Merge to compare same years and regions
            comparison = pd.merge(
                ssp_data, 
                baseline_data[['year', 'region', 'yield', 'temperature', 'precipitation']],
                on=['year', 'region'], 
                suffixes=('_ssp', '_baseline')
            )
            
            # Calculate impacts
            comparison['yield_impact'] = comparison['yield_ssp'] - comparison['yield_baseline']
            comparison['yield_impact_pct'] = (comparison['yield_impact'] / comparison['yield_baseline']) * 100
            comparison['temp_change'] = comparison['temperature_ssp'] - comparison['temperature_baseline']
            comparison['precip_change'] = comparison['precipitation_ssp'] - comparison['precipitation_baseline']
            
            impacts.append(comparison)
        
        return pd.concat(impacts, ignore_index=True)
    
    def assess_vulnerability(self, impacts_df, time_period=(2040, 2060)):
        """Assess regional vulnerability to climate change"""
        
        period_data = impacts_df[
            (impacts_df['year'] >= time_period[0]) & 
            (impacts_df['year'] <= time_period[1])
        ]
        
        vulnerability = period_data.groupby(['region', 'scenario']).agg({
            'yield_impact_pct': 'mean',
            'temp_change': 'mean',
            'precip_change': 'mean'
        }).reset_index()
        
        # Classify vulnerability
        vulnerability['vulnerability_level'] = pd.cut(
            vulnerability['yield_impact_pct'],
            bins=[-100, -20, -10, -5, 5, 100],
            labels=['Extreme', 'High', 'Medium', 'Low', 'Beneficial']
        )
        
        return vulnerability
