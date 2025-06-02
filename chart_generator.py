import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
import streamlit as st

class ChartGenerator:
    """Generate optimized Plotly charts for different data types"""
    
    def __init__(self):
        self.standard_width = 700
        self.standard_height = 500
        self.grid_height = 300  # Reduced height for grid view
        self.margin_config = dict(l=60, r=60, t=60, b=60)
        
        # Dark theme configuration
        self.dark_theme = {
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'font': {'color': '#ffffff', 'size': 11},
            'xaxis': {
                'showgrid': True,
                'gridwidth': 1,
                'gridcolor': 'rgba(255,255,255,0.2)',
                'showline': True,
                'linewidth': 1,
                'linecolor': 'rgba(255,255,255,0.3)',
                'color': '#ffffff'
            },
            'yaxis': {
                'showgrid': True,
                'gridwidth': 1,
                'gridcolor': 'rgba(255,255,255,0.2)',
                'showline': True,
                'linewidth': 1,
                'linecolor': 'rgba(255,255,255,0.3)',
                'color': '#ffffff'
            }
        }
    
    def validate_data(self, df: pd.DataFrame, table_name: str) -> bool:
        """Validate data before creating charts"""
        if df is None or df.empty:
            st.warning(f"⚠️ Tabla {table_name}: Sin datos para graficar")
            return False
        
        if len(df) < 2:
            st.warning(f"⚠️ Tabla {table_name}: Insuficientes puntos de datos ({len(df)})")
            return False
        
        # Check for required columns
        if 'ValueX' not in df.columns or 'ValueY' not in df.columns:
            st.warning(f"⚠️ Tabla {table_name}: Faltan columnas ValueX/ValueY")
            return False
        
        # Check for valid numeric data
        if df['ValueX'].isna().all() or df['ValueY'].isna().all():
            st.warning(f"⚠️ Tabla {table_name}: Datos no numéricos")
            return False
        
        # Check for reasonable data ranges
        x_range = df['ValueX'].max() - df['ValueX'].min()
        y_range = df['ValueY'].max() - df['ValueY'].min()
        
        if x_range == 0 and y_range == 0:
            st.warning(f"⚠️ Tabla {table_name}: Datos constantes (sin variación)")
            return False
        
        return True
    
    def optimize_data_for_plotting(self, df: pd.DataFrame, max_points: int = 5000) -> pd.DataFrame:
        """Optimize data for plotting by sampling if necessary"""
        if len(df) <= max_points:
            return df
        
        # For large datasets, use intelligent sampling
        if len(df) > max_points:
            # Sort by ValueX to maintain data structure
            df_sorted = df.sort_values('ValueX')
            
            # Use systematic sampling to preserve data distribution
            step = len(df_sorted) // max_points
            sampled_df = df_sorted.iloc[::step].copy()
            
            # Always include first and last points
            if df_sorted.iloc[0].name not in sampled_df.index:
                sampled_df = pd.concat([df_sorted.iloc[[0]], sampled_df])
            if df_sorted.iloc[-1].name not in sampled_df.index:
                sampled_df = pd.concat([sampled_df, df_sorted.iloc[[-1]]])
            
            st.info(f"📊 Datos optimizados: {len(df):,} → {len(sampled_df):,} puntos")
            return sampled_df.sort_values('ValueX')
        
        return df
    
    def create_waveform_chart(self, df: pd.DataFrame, table_name: str, height: int = None) -> go.Figure:
        """Create optimized waveform chart"""
        height = height or self.standard_height
        
        # Optimize data
        df_optimized = self.optimize_data_for_plotting(df)
        
        # Create line chart with optimizations
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_optimized['ValueX'],
            y=df_optimized['ValueY'],
            mode='lines',
            name=table_name,
            line=dict(
                width=1.5,
                color='#667eea'
            ),
            hovertemplate='<b>Tiempo:</b> %{x:.4f}s<br><b>Amplitud:</b> %{y:.4f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(
                text=f"🌊 {table_name}",
                x=0.5,
                font=dict(size=14, color='#ffffff')
            ),
            width=self.standard_width,
            height=height,
            margin=self.margin_config,
            showlegend=False,
            xaxis_title="Tiempo (s)",
            yaxis_title="Amplitud",
            **self.dark_theme
        )
        
        return fig
    
    def create_spectrum_hz_chart(self, df: pd.DataFrame, table_name: str, height: int = None) -> go.Figure:
        """Create optimized spectrum Hz chart"""
        height = height or self.standard_height
        
        # Sort and optimize data
        df_sorted = df.sort_values('ValueX')
        df_optimized = self.optimize_data_for_plotting(df_sorted, max_points=1000)  # Fewer points for bar charts
        
        # Create bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df_optimized['ValueX'].astype(str),
            y=df_optimized['ValueY'],
            name=table_name,
            marker=dict(
                color='#17a2b8',
                line=dict(width=0.5, color='#138496')
            ),
            hovertemplate='<b>Frecuencia:</b> %{x} Hz<br><b>Magnitud:</b> %{y:.4f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(
                text=f"🔊 {table_name}",
                x=0.5,
                font=dict(size=14, color='#ffffff')
            ),
            width=self.standard_width,
            height=height,
            margin=self.margin_config,
            showlegend=False,
            xaxis_title="Frecuencia (Hz)",
            yaxis_title="Magnitud",
            bargap=0.1,
            **self.dark_theme
        )
        
        fig.update_xaxes(type='category')
        
        return fig
    
    def create_spectrum_order_chart(self, df: pd.DataFrame, table_name: str, height: int = None) -> go.Figure:
        """Create optimized spectrum order chart"""
        height = height or self.standard_height
        
        # Sort and optimize data
        df_sorted = df.sort_values('ValueX')
        df_optimized = self.optimize_data_for_plotting(df_sorted, max_points=1000)
        
        # Create bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df_optimized['ValueX'].astype(str),
            y=df_optimized['ValueY'],
            name=table_name,
            marker=dict(
                color='#28a745',
                line=dict(width=0.5, color='#20c997')
            ),
            hovertemplate='<b>Orden:</b> %{x}<br><b>Magnitud:</b> %{y:.4f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(
                text=f"🎵 {table_name}",
                x=0.5,
                font=dict(size=14, color='#ffffff')
            ),
            width=self.standard_width,
            height=height,
            margin=self.margin_config,
            showlegend=False,
            xaxis_title="Orden",
            yaxis_title="Magnitud",
            bargap=0.1,
            **self.dark_theme
        )
        
        fig.update_xaxes(type='category')
        
        return fig
    
    def create_generic_chart(self, df: pd.DataFrame, table_name: str, height: int = None) -> go.Figure:
        """Create optimized generic scatter chart"""
        height = height or self.standard_height
        
        # Optimize data
        df_optimized = self.optimize_data_for_plotting(df, max_points=2000)
        
        # Create scatter chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_optimized['ValueX'],
            y=df_optimized['ValueY'],
            mode='markers',
            name=table_name,
            marker=dict(
                size=4,
                color='#ffc107',
                opacity=0.7,
                line=dict(width=1, color='#e0a800')
            ),
            hovertemplate='<b>X:</b> %{x:.4f}<br><b>Y:</b> %{y:.4f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(
                text=f"📈 {table_name}",
                x=0.5,
                font=dict(size=14, color='#ffffff')
            ),
            width=self.standard_width,
            height=height,
            margin=self.margin_config,
            showlegend=False,
            xaxis_title="Valor X",
            yaxis_title="Valor Y",
            **self.dark_theme
        )
        
        return fig
    
    def create_chart(self, df: pd.DataFrame, table_name: str, chart_type: str, height: int = None) -> Optional[go.Figure]:
        """Create chart based on type with validation and optimization"""
        
        # Validate data first
        if not self.validate_data(df, table_name):
            return None
        
        try:
            # Create chart based on type
            if chart_type == 'waveform':
                return self.create_waveform_chart(df, table_name, height)
            elif chart_type == 'spectrum_hz':
                return self.create_spectrum_hz_chart(df, table_name, height)
            elif chart_type == 'spectrum_order':
                return self.create_spectrum_order_chart(df, table_name, height)
            else:
                return self.create_generic_chart(df, table_name, height)
                
        except Exception as e:
            st.error(f"❌ Error creando gráfico para {table_name}: {e}")
            return None
    
    def get_chart_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get chart information and statistics"""
        if df is None or df.empty:
            return {}
        
        info = {
            'data_points': len(df),
            'x_range': (df['ValueX'].min(), df['ValueX'].max()) if 'ValueX' in df.columns else None,
            'y_range': (df['ValueY'].min(), df['ValueY'].max()) if 'ValueY' in df.columns else None,
            'x_mean': df['ValueX'].mean() if 'ValueX' in df.columns else None,
            'y_mean': df['ValueY'].mean() if 'ValueY' in df.columns else None,
            'has_nulls': df.isnull().any().any()
        }
        
        return info 