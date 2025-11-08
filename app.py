import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

from src.climate_processor import ClimateDataProcessor
from src.scenario_generator import ScenarioGenerator
from src.impact_assessor import ImpactAssessor

# Page configuration
st.set_page_config(
    page_title="Climate-Smart Agriculture Planner",
    page_icon="🌾",
    layout="wide"
)

# Initialize components
@st.cache_resource
def initialize_components():
    climate_processor = ClimateDataProcessor()
    scenario_generator = ScenarioGenerator(climate_processor)
    impact_assessor = ImpactAssessor()
    return climate_processor, scenario_generator, impact_assessor

climate_processor, scenario_generator, impact_assessor = initialize_components()

# Title and introduction
st.title("🌾 Climate-Change Driven Agricultural Yield Prediction using CMIP6 Data")
st.markdown("""
### Explore Future Agricultural Scenarios Under Climate Change
This tool analyzes how different socioeconomic pathways (SSPs) will affect African agriculture through 2100.
""")

# Sidebar
st.sidebar.header("🔧 Analysis Parameters")

# Scenario selection
selected_ssps = st.sidebar.multiselect(
    "SSP Scenarios to Compare",
    ['SSP1-2.6', 'SSP2-4.5', 'SSP3-7.0', 'SSP5-8.5'],
    default=['SSP1-2.6', 'SSP2-4.5', 'SSP5-8.5']
)

# Region selection
selected_regions = st.sidebar.multiselect(
    "Regions",
    ['West Africa', 'East Africa', 'Southern Africa', 'Central Africa'],
    default=['West Africa', 'East Africa', 'Southern Africa']
)

# Time period
start_year, end_year = st.sidebar.slider(
    "Analysis Period",
    2020, 2100, (2030, 2080)
)

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Scenario Overview", 
    "🌡️ Climate Impacts", 
    "🌾 Yield Projections", 
    "🎯 Policy Insights"
])

with tab1:
    st.header("SSP Scenario Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Radiative Forcing Comparison")
        
        # Forcing comparison chart
        forcing_data = []
        for ssp in selected_ssps:
            info = climate_processor.ssp_definitions[ssp]
            forcing_data.append({
                'Scenario': ssp,
                'Radiative Forcing (W/m²)': info['forcing'],
                'Description': info['description'],
                'Color': info['color']
            })
        
        forcing_df = pd.DataFrame(forcing_data)
        
        fig = px.bar(
            forcing_df, 
            x='Scenario', 
            y='Radiative Forcing (W/m²)',
            color='Scenario',
            color_discrete_map={row['Scenario']: row['Color'] for row in forcing_data},
            title="Radiative Forcing by SSP Scenario"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Scenario Narratives")
        
        for ssp in selected_ssps:
            info = climate_processor.ssp_definitions[ssp]
            with st.expander(f"{ssp}: {info['name']}"):
                st.write(f"**Radiative Forcing:** {info['forcing']} W/m²")
                st.write(f"**Description:** {info['description']}")
                
                # Agricultural implications
                implications = {
                    'SSP1-2.6': "• Sustainable intensification\n• Organic farming growth\n• Reduced food waste\n• Plant-based diets",
                    'SSP2-4.5': "• Moderate technological progress\n• Mixed farming systems\n• Gradual yield improvements",
                    'SSP3-7.0': "• Low investment in agriculture\n• Food insecurity risks\n• Trade barriers\n• Conflict impacts", 
                    'SSP5-8.5': "• High-input agriculture\n• Technological solutions\n• Energy-intensive systems\n• Land use change"
                }
                
                st.write("**Agricultural Implications:**")
                st.write(implications[ssp])

with tab2:
    st.header("Climate Change Projections")
    
    # Generate and display climate data
    if st.button("Generate Climate Scenarios", type="primary"):
        with st.spinner("Generating climate projections..."):
            all_climate_data = []
            
            for ssp in selected_ssps:
                climate_data = climate_processor.load_cmip6_data(ssp)
                climate_data = climate_processor.calculate_climate_anomalies(climate_data)
                all_climate_data.append(climate_data)
            
            climate_df = pd.concat(all_climate_data, ignore_index=True)
            
            # Filter for selected period
            climate_df = climate_df[
                (climate_df['year'] >= start_year) & 
                (climate_df['year'] <= end_year)
            ]
            
            # Create climate visualization
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Temperature Anomalies', 'Precipitation Changes'),
                vertical_spacing=0.1
            )
            
            for ssp in selected_ssps:
                ssp_data = climate_df[climate_df['scenario'] == ssp]
                info = climate_processor.ssp_definitions[ssp]
                
                # Temperature anomalies
                fig.add_trace(
                    go.Scatter(
                        x=ssp_data['year'], 
                        y=ssp_data['temp_anomaly'],
                        name=f"{ssp} Temperature",
                        line=dict(color=info['color']),
                        legendgroup=ssp
                    ),
                    row=1, col=1
                )
                
                # Precipitation anomalies
                fig.add_trace(
                    go.Scatter(
                        x=ssp_data['year'],
                        y=ssp_data['precip_anomaly'], 
                        name=f"{ssp} Precipitation",
                        line=dict(color=info['color'], dash='dash'),
                        legendgroup=ssp,
                        showlegend=False
                    ),
                    row=2, col=1
                )
            
            fig.update_layout(height=600, title_text="Climate Projections for African Regions")
            fig.update_yaxes(title_text="Temperature Anomaly (°C)", row=1, col=1)
            fig.update_yaxes(title_text="Precipitation Anomaly (%)", row=2, col=1)
            
            st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("Crop Yield Projections")
    
    if st.button("Generate Yield Projections", type="primary"):
        with st.spinner("Calculating yield impacts..."):
            # Generate agricultural scenarios
            all_scenarios = []
            for ssp in selected_ssps:
                scenario_data = scenario_generator.generate_agricultural_scenarios(ssp, 'Maize')
                all_scenarios.append(scenario_data)
            
            scenarios_df = pd.concat(all_scenarios, ignore_index=True)
            
            # Filter for selected period
            scenarios_df = scenarios_df[
                (scenarios_df['year'] >= start_year) & 
                (scenarios_df['year'] <= end_year)
            ]
            
            # Calculate impacts
            impacts_df = impact_assessor.calculate_impacts(scenarios_df)
            
            # Display yield projections
            st.subheader("Maize Yield Projections by Region")
            
            for region in selected_regions:
                region_data = scenarios_df[scenarios_df['region'] == region]
                
                fig = px.line(
                    region_data,
                    x='year',
                    y='yield', 
                    color='scenario',
                    color_discrete_map={ssp: climate_processor.ssp_definitions[ssp]['color'] 
                                      for ssp in selected_ssps},
                    title=f"Maize Yield Projections: {region}",
                    labels={'yield': 'Yield (tons/ha)', 'year': 'Year'}
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Show impacts table
            st.subheader("Climate Impact Assessment")
            
            vulnerability = impact_assessor.assess_vulnerability(impacts_df, (2050, 2070))
            
            # Color code vulnerability levels
            def color_vulnerability(val):
                if val == 'Extreme': return 'background-color: #FF6B6B'
                elif val == 'High': return 'background-color: #FFA500' 
                elif val == 'Medium': return 'background-color: #FFD700'
                elif val == 'Low': return 'background-color: #90EE90'
                else: return 'background-color: #32CD32'
            
            styled_vulnerability = vulnerability.style.applymap(
                color_vulnerability, subset=['vulnerability_level']
            )
            
            st.dataframe(styled_vulnerability, use_container_width=True)

with tab4:
    st.header("Policy Recommendations")
    
    st.subheader("Adaptation Strategies by Scenario")
    
    adaptation_strategies = {
        'SSP1-2.6': [
            "Invest in sustainable intensification",
            "Promote agroecological practices", 
            "Develop climate-resilient crop varieties",
            "Enhance soil carbon sequestration",
            "Support smallholder innovation"
        ],
        'SSP2-4.5': [
            "Mixed adaptation portfolio",
            "Moderate irrigation expansion",
            "Improved fertilizer management",
            "Climate information services",
            "Risk transfer mechanisms"
        ],
        'SSP3-7.0': [
            "Focus on food security safety nets",
            "Emergency response capacity",
            "Conflict-sensitive adaptation",
            "Local seed systems preservation",
            "Community-based resilience"
        ],
        'SSP5-8.5': [
            "High-tech irrigation systems",
            "Precision agriculture technologies",
            "Genetic engineering investments",
            "Large-scale infrastructure",
            "Private sector engagement"
        ]
    }
    
    for ssp in selected_ssps:
        with st.expander(f"Adaptation Priorities: {ssp}"):
            for strategy in adaptation_strategies[ssp]:
                st.write(f"• {strategy}")
    
    st.subheader("Investment Prioritization")
    
    st.info("""
    **Key Investment Areas Across All Scenarios:**
    1. **Climate Information Services** - Early warning systems
    2. **Drought-Resistant Varieties** - Genetic improvement programs  
    3. **Water Management** - Efficient irrigation and rainwater harvesting
    4. **Soil Health** - Conservation agriculture and organic matter
    5. **Market Access** - Reduced post-harvest losses and better prices
    """)

# Footer
st.markdown("---")
st.markdown("""
**Data Sources:**
- Climate Projections: CMIP6 ensemble
- Socioeconomic Scenarios: Shared Socioeconomic Pathways (SSPs)
- Agricultural Data: HarvestStat Africa, FAOSTAT

**Methodology:** Integrated assessment modeling combining climate projections with agricultural impact functions.
""")
