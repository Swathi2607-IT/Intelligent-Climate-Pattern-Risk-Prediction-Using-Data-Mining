"""
Climate Data Visualization Module
Generates publication-quality visualizations using Matplotlib and Plotly
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.gridspec import GridSpec
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ClimateVisualizer:
    """
    Creates comprehensive visualizations for climate data analysis.
    """
    
    def __init__(self, data_path: str, output_dir: str = "./output"):
        """
        Initialize visualizer.
        
        Args:
            data_path (str): Path to climate data CSV
            output_dir (str): Directory to save visualizations
        """
        self.data_path = data_path
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load data
        self.df = pd.read_csv(data_path)
        logger.info(f"Loaded data: {len(self.df)} records")
    
    def temperature_anomaly_chart(self, save=True):
        """Create temperature anomaly line chart."""
        logger.info("Creating temperature anomaly visualization")
        
        fig = go.Figure()
        
        # Add temperature line
        fig.add_trace(go.Scatter(
            x=self.df['year'],
            y=self.df['global_temp_anomaly'] if 'global_temp_anomaly' in self.df.columns else self.df['temp_anomaly_c'],
            mode='lines+markers',
            name='Temperature Anomaly',
            line=dict(color='#FF4444', width=2.5),
            marker=dict(size=4),
            fill='tozeroy',
            fillcolor='rgba(255,68,68,0.1)'
        ))
        
        # Add zero reference line
        fig.add_hline(y=0, line_dash="dash", line_color="gray", 
                     annotation_text="Baseline", annotation_position="right")
        
        fig.update_layout(
            title='Global Temperature Anomaly (1924-2023)',
            xaxis_title='Year',
            yaxis_title='Temperature Anomaly (°C)',
            hovermode='x unified',
            template='plotly_white',
            height=600,
            font=dict(size=14),
            title_font=dict(size=20)
        )
        
        if save:
            filepath = os.path.join(self.output_dir, 'temperature_anomaly.html')
            fig.write_html(filepath)
            logger.info(f"Saved: {filepath}")
        
        return fig
    
    def co2_concentration_chart(self, save=True):
        """Create CO2 concentration chart."""
        logger.info("Creating CO2 concentration visualization")
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=self.df['year'],
            y=self.df['co2_ppm'],
            mode='lines',
            name='CO₂ Concentration',
            line=dict(color='#22AA44', width=3),
            fill='tozeroy',
            fillcolor='rgba(34,170,68,0.2)'
        ))
        
        fig.update_layout(
            title='Atmospheric CO₂ Concentration (1924-2023)',
            xaxis_title='Year',
            yaxis_title='CO₂ Concentration (ppm)',
            hovermode='x unified',
            template='plotly_white',
            height=600,
            font=dict(size=14),
            title_font=dict(size=20)
        )
        
        if save:
            filepath = os.path.join(self.output_dir, 'co2_concentration.html')
            fig.write_html(filepath)
            logger.info(f"Saved: {filepath}")
        
        return fig
    
    def methane_levels_chart(self, save=True):
        """Create methane levels chart."""
        logger.info("Creating methane levels visualization")
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=self.df['year'],
            y=self.df['methane_ppb'],
            mode='lines',
            name='CH₄ Concentration',
            line=dict(color='#FF8800', width=2.5),
            fill='tozeroy',
            fillcolor='rgba(255,136,0,0.15)'
        ))
        
        fig.update_layout(
            title='Atmospheric Methane (CH₄) Concentration (1924-2023)',
            xaxis_title='Year',
            yaxis_title='CH₄ Concentration (ppb)',
            hovermode='x unified',
            template='plotly_white',
            height=600,
            font=dict(size=14),
            title_font=dict(size=20)
        )
        
        if save:
            filepath = os.path.join(self.output_dir, 'methane_levels.html')
            fig.write_html(filepath)
            logger.info(f"Saved: {filepath}")
        
        return fig
    
    def sea_level_rise_chart(self, save=True):
        """Create sea level rise chart."""
        logger.info("Creating sea level rise visualization")
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=self.df['year'],
            y=self.df['sea_level_mm'],
            mode='lines',
            name='Sea Level Rise',
            line=dict(color='#0066CC', width=2.5),
            fill='tozeroy',
            fillcolor='rgba(0,102,204,0.15)'
        ))
        
        fig.update_layout(
            title='Global Sea Level Rise (1924-2023)',
            xaxis_title='Year',
            yaxis_title='Sea Level Rise (mm above baseline)',
            hovermode='x unified',
            template='plotly_white',
            height=600,
            font=dict(size=14),
            title_font=dict(size=20)
        )
        
        if save:
            filepath = os.path.join(self.output_dir, 'sea_level_rise.html')
            fig.write_html(filepath)
            logger.info(f"Saved: {filepath}")
        
        return fig
    
    def correlation_heatmap(self, save=True):
        """Create correlation heatmap."""
        logger.info("Creating correlation heatmap")
        
        # Select numeric columns
        temp_col = 'global_temp_anomaly' if 'global_temp_anomaly' in self.df.columns else 'temp_anomaly_c'
        features = [temp_col, 'co2_ppm', 'methane_ppb', 'sea_level_mm']
        
        # Calculate correlation
        corr_matrix = self.df[features].corr()
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=['Temperature', 'CO₂', 'CH₄', 'Sea Level'],
            y=['Temperature', 'CO₂', 'CH₄', 'Sea Level'],
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.values.round(3),
            texttemplate='%{text}',
            textfont={"size": 16},
            colorbar=dict(title=dict(text="Correlation<br>Coefficient", side="right"))
        ))
        
        fig.update_layout(
            title='Correlation Matrix: Climate Indicators',
            height=700,
            width=800,
            font=dict(size=14),
            title_font=dict(size=20)
        )
        
        if save:
            filepath = os.path.join(self.output_dir, 'correlation_heatmap.html')
            fig.write_html(filepath)
            logger.info(f"Saved: {filepath}")
        
        return fig
    
    def comprehensive_dashboard(self, save=True):
        """Create comprehensive 4-panel dashboard."""
        logger.info("Creating comprehensive dashboard")
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Temperature Anomaly', 'CO₂ Concentration',
                          'Methane Levels', 'Sea Level Rise'),
            vertical_spacing=0.12,
            horizontal_spacing=0.10
        )
        
        temp_col = 'global_temp_anomaly' if 'global_temp_anomaly' in self.df.columns else 'temp_anomaly_c'
        
        # Temperature
        fig.add_trace(
            go.Scatter(x=self.df['year'], y=self.df[temp_col],
                      name='Temperature', line=dict(color='red', width=2),
                      showlegend=False),
            row=1, col=1
        )
        
        # CO2
        fig.add_trace(
            go.Scatter(x=self.df['year'], y=self.df['co2_ppm'],
                      name='CO₂', line=dict(color='green', width=2),
                      showlegend=False),
            row=1, col=2
        )
        
        # Methane
        fig.add_trace(
            go.Scatter(x=self.df['year'], y=self.df['methane_ppb'],
                      name='Methane', line=dict(color='orange', width=2),
                      showlegend=False),
            row=2, col=1
        )
        
        # Sea Level
        fig.add_trace(
            go.Scatter(x=self.df['year'], y=self.df['sea_level_mm'],
                      name='Sea Level', line=dict(color='blue', width=2),
                      showlegend=False),
            row=2, col=2
        )
        
        # Update axes
        fig.update_xaxes(title_text="Year", row=1, col=1)
        fig.update_xaxes(title_text="Year", row=1, col=2)
        fig.update_xaxes(title_text="Year", row=2, col=1)
        fig.update_xaxes(title_text="Year", row=2, col=2)
        
        fig.update_yaxes(title_text="°C", row=1, col=1)
        fig.update_yaxes(title_text="ppm", row=1, col=2)
        fig.update_yaxes(title_text="ppb", row=2, col=1)
        fig.update_yaxes(title_text="mm", row=2, col=2)
        
        fig.update_layout(
            title_text="Climate Change Indicators Dashboard (1924-2023)",
            title_font=dict(size=22),
            height=900,
            template='plotly_white'
        )
        
        if save:
            filepath = os.path.join(self.output_dir, 'climate_dashboard.html')
            fig.write_html(filepath)
            logger.info(f"Saved: {filepath}")
        
        return fig
    
    def create_all_visualizations(self):
        """Generate all visualization types."""
        logger.info("Generating all visualizations...")
        
        self.temperature_anomaly_chart()
        self.co2_concentration_chart()
        self.methane_levels_chart()
        self.sea_level_rise_chart()
        self.correlation_heatmap()
        self.comprehensive_dashboard()
        
        logger.info(f"All visualizations saved to: {self.output_dir}")


def main():
    """Main execution function."""
    # Use sample data
    data_path = "../data/sample/climate_sample.csv"
    output_dir = "../visualizations/output"
    
    visualizer = ClimateVisualizer(data_path, output_dir)
    visualizer.create_all_visualizations()
    
    logger.info("Visualization generation complete!")


if __name__ == "__main__":
    main()
