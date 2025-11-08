import pandas as pd
import numpy as np

class ScenarioGenerator:
    def __init__(self, climate_processor):
        self.climate_processor = climate_processor
        self.regions = ['West Africa', 'East Africa', 'Southern Africa', 'Central Africa']
        
    def generate_agricultural_scenarios(self, ssp_scenario, crop_type='Maize'):
        """Generate comprehensive agricultural scenarios for each SSP"""
        
        # Get climate projections
        climate_data = self.climate_processor.load_cmip6_data(ssp_scenario)
        climate_data = self.climate_processor.calculate_climate_anomalies(climate_data)
        
        # SSP-specific agricultural assumptions
        ag_assumptions = self._get_agricultural_assumptions(ssp_scenario, crop_type)
        
        scenarios = []
        for region in self.regions:
            region_scenario = self._generate_region_scenario(
                climate_data, ag_assumptions, region, crop_type
            )
            scenarios.append(region_scenario)
        
        return pd.concat(scenarios, ignore_index=True)
    
    def _get_agricultural_assumptions(self, ssp_scenario, crop_type):
        """Get SSP-specific agricultural development assumptions"""
        
        assumptions = {
            'SSP1-2.6': {
                'tech_growth': 0.02,  # 2% annual yield improvement from technology
                'water_management': 'efficient',
                'fertilizer_use': 'moderate',
                'mechanization': 'medium',
                'trade_openness': 'high',
                'conflict_risk': 'low'
            },
            'SSP2-4.5': {
                'tech_growth': 0.015,
                'water_management': 'moderate', 
                'fertilizer_use': 'high',
                'mechanization': 'medium',
                'trade_openness': 'medium',
                'conflict_risk': 'medium'
            },
            'SSP3-7.0': {
                'tech_growth': 0.008,
                'water_management': 'poor',
                'fertilizer_use': 'low', 
                'mechanization': 'low',
                'trade_openness': 'low',
                'conflict_risk': 'high'
            },
            'SSP5-8.5': {
                'tech_growth': 0.025,
                'water_management': 'high_tech',
                'fertilizer_use': 'very_high',
                'mechanization': 'high',
                'trade_openness': 'medium',
                'conflict_risk': 'medium'
            }
        }
        
        return assumptions[ssp_scenario]
    
    def _generate_region_scenario(self, climate_data, ag_assumptions, region, crop_type):
        """Generate scenario for a specific region"""
        
        scenario_data = climate_data.copy()
        scenario_data['region'] = region
        scenario_data['crop_type'] = crop_type
        
        # Regional climate modifiers
        region_modifiers = {
            'West Africa': {'temp_modifier': 1.0, 'precip_modifier': 0.9},
            'East Africa': {'temp_modifier': 0.8, 'precip_modifier': 0.7},
            'Southern Africa': {'temp_modifier': 1.2, 'precip_modifier': 0.6},
            'Central Africa': {'temp_modifier': 0.9, 'precip_modifier': 1.1}
        }
        
        mod = region_modifiers[region]
        scenario_data['temperature'] *= mod['temp_modifier']
        scenario_data['precipitation'] *= mod['precip_modifier']
        
        # Calculate yield impacts
        scenario_data = self._calculate_yield_impacts(scenario_data, ag_assumptions)
        
        return scenario_data
    
    def _calculate_yield_impacts(self, scenario_data, ag_assumptions):
        """Calculate crop yield impacts under climate change"""
        
        # Base yield (tons/ha)
        base_yield = 2.5  # Average maize yield in Africa
        
        # Climate impact function
        temp_effect = np.where(
            scenario_data['temperature'] <= 30,
            1.0 - 0.05 * (scenario_data['temperature'] - 25)**2,
            1.0 - 0.05 * (scenario_data['temperature'] - 25)**2 - 0.1 * (scenario_data['temperature'] - 30)
        )
        
        precip_effect = np.where(
            (scenario_data['precipitation'] >= 400) & (scenario_data['precipitation'] <= 800),
            1.0,
            1.0 - 0.001 * np.abs(scenario_data['precipitation'] - 600)
        )
        
        # Technological improvement over time
        years_from_base = scenario_data['year'] - 2020
        tech_improvement = (1 + ag_assumptions['tech_growth']) ** years_from_base
        
        # Calculate final yield
        scenario_data['yield'] = base_yield * temp_effect * precip_effect * tech_improvement
        
        # Apply bounds (realistic yield range)
        scenario_data['yield'] = np.clip(scenario_data['yield'], 0.5, 6.0)
        
        return scenario_data
