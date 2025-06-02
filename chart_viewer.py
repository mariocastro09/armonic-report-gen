import streamlit as st
import plotly.graph_objects as go
from typing import List, Dict, Tuple
import re
from math import ceil

class ChartViewer:
    """Optimized chart viewer with search, filtering, and pagination"""
    
    def __init__(self, charts_per_page: int = 12):
        self.charts_per_page = charts_per_page
        
    def render_search_and_filters(self, charts_data: List[Dict]) -> Tuple[str, str, List[str]]:
        """Render search bar and filters with professional styling"""
        st.markdown("""
        <div class="search-container">
            <h4 margin-bottom: 1rem;">🔍 Buscar y Filtrar Gráficos</h4>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_term = st.text_input(
                "🔍 Buscar por nombre de tabla",
                placeholder="Ej: RMU, Spectrum, Waveform...",
                key="chart_search"
            )
        
        with col2:
            # Get unique chart types
            chart_types = list(set([chart['type'] for chart in charts_data]))
            chart_type_filter = st.selectbox(
                "📊 Filtrar por tipo",
                ["Todos"] + chart_types,
                key="chart_type_filter"
            )
        
        with col3:
            # Sort options
            sort_options = [
                "Nombre (A-Z)",
                "Nombre (Z-A)", 
                "Tipo",
                "Puntos de datos (↑)",
                "Puntos de datos (↓)"
            ]
            sort_by = st.selectbox(
                "🔄 Ordenar por",
                sort_options,
                key="chart_sort"
            )
        
        return search_term, chart_type_filter, sort_by
    
    def filter_and_sort_charts(self, charts_data: List[Dict], search_term: str, 
                              chart_type_filter: str, sort_by: str) -> List[Dict]:
        """Filter and sort charts based on criteria"""
        filtered_charts = charts_data.copy()
        
        # Apply search filter
        if search_term:
            filtered_charts = [
                chart for chart in filtered_charts
                if re.search(search_term, chart['table_name'], re.IGNORECASE)
            ]
        
        # Apply type filter
        if chart_type_filter != "Todos":
            filtered_charts = [
                chart for chart in filtered_charts
                if chart['type'] == chart_type_filter
            ]
        
        # Apply sorting
        if sort_by == "Nombre (A-Z)":
            filtered_charts.sort(key=lambda x: x['table_name'])
        elif sort_by == "Nombre (Z-A)":
            filtered_charts.sort(key=lambda x: x['table_name'], reverse=True)
        elif sort_by == "Tipo":
            filtered_charts.sort(key=lambda x: x['type'])
        elif sort_by == "Puntos de datos (↑)":
            filtered_charts.sort(key=lambda x: x['info'].get('data_points', 0))
        elif sort_by == "Puntos de datos (↓)":
            filtered_charts.sort(key=lambda x: x['info'].get('data_points', 0), reverse=True)
        
        return filtered_charts
    
    def render_pagination_controls(self, total_charts: int, current_page: int, key_suffix: str = "") -> int:
        """Render pagination controls"""
        total_pages = ceil(total_charts / self.charts_per_page)
        
        if total_pages <= 1:
            return current_page
        
        st.markdown("""
        <div class="pagination-container">
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
        
        with col1:
            if st.button("⏮️ Primera", disabled=current_page <= 1, key=f"pagination_first{key_suffix}"):
                current_page = 1
        
        with col2:
            if st.button("◀️ Anterior", disabled=current_page <= 1, key=f"pagination_prev{key_suffix}"):
                current_page -= 1
        
        with col3:
            st.markdown(f"""
            <div style="text-align: center; padding: 0.5rem;">
                <strong>Página {current_page} de {total_pages}</strong><br>
                <small>Mostrando {min(self.charts_per_page, total_charts - (current_page-1)*self.charts_per_page)} de {total_charts} gráficos</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            if st.button("▶️ Siguiente", disabled=current_page >= total_pages, key=f"pagination_next{key_suffix}"):
                current_page += 1
        
        with col5:
            if st.button("⏭️ Última", disabled=current_page >= total_pages, key=f"pagination_last{key_suffix}"):
                current_page = total_pages
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        return current_page
    
    def render_chart_grid(self, charts_data: List[Dict], page: int) -> None:
        """Render charts in an optimized grid layout"""
        start_idx = (page - 1) * self.charts_per_page
        end_idx = start_idx + self.charts_per_page
        page_charts = charts_data[start_idx:end_idx]
        
        if not page_charts:
            st.warning("🔍 No se encontraron gráficos que coincidan con los criterios de búsqueda.")
            return
        
        # Chart type emojis with professional styling
        chart_type_emoji = {
            'waveform': '📈',
            'spectrum_hz': '🔊', 
            'spectrum_order': '🎵',
            'generic': '📊'
        }
        
        # Create grid layout
        cols_per_row = 2
        for i in range(0, len(page_charts), cols_per_row):
            cols = st.columns(cols_per_row)
            
            for j, col in enumerate(cols):
                if i + j < len(page_charts):
                    chart = page_charts[i + j]
                    
                    with col:
                        # Chart card container with professional styling
                        with st.container():
                            st.markdown(f"""
                            <div class="chart-card">
                                <h5 margin-bottom: 0.8rem;">
                                    {chart_type_emoji.get(chart['type'], '📊')} {chart['table_name']}
                                </h5>
                                <div style="display: flex; gap: 1rem; margin-bottom: 1rem; align-items: center;">
                                    <span style="background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); 
                                                color: white; padding: 0.3rem 0.8rem; border-radius: 12px; 
                                                font-size: 0.8rem; font-weight: 500;">
                                        {chart['type'].replace('_', ' ').title()}
                                    </span>
                                    <span style="color: #7f8c8d; font-weight: 500;">
                                        📊 {chart['info'].get('data_points', 0):,} puntos
                                    </span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Render chart with reduced height for grid view
                            chart_figure = chart['figure']
                            chart_figure.update_layout(
                                height=300,
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                font={'color': '#2c3e50', 'size': 11},
                                title={'font': {'color': '#2c3e50', 'size': 14}},
                                xaxis={'color': '#2c3e50', 'gridcolor': 'rgba(44,62,80,0.2)', 'linecolor': '#7f8c8d'},
                                yaxis={'color': '#2c3e50', 'gridcolor': 'rgba(44,62,80,0.2)', 'linecolor': '#7f8c8d'}
                            )
                            
                            st.plotly_chart(
                                chart_figure, 
                                use_container_width=True,
                                key=f"chart_{start_idx + i + j}"
                            )
                            
                            # Chart details in expander with professional styling
                            with st.expander("📊 Detalles del gráfico"):
                                info = chart['info']
                                
                                detail_col1, detail_col2 = st.columns(2)
                                with detail_col1:
                                    st.metric("📊 Puntos de datos", f"{info.get('data_points', 0):,}")
                                    if info.get('x_range'):
                                        x_min, x_max = info.get('x_range')
                                        st.metric("📏 Rango X", f"{x_min:.2f} - {x_max:.2f}")
                                
                                with detail_col2:
                                    st.metric("🎯 Tipo", chart['type'].replace('_', ' ').title())
                                    if info.get('y_range'):
                                        y_min, y_max = info.get('y_range')
                                        st.metric("📐 Rango Y", f"{y_min:.2f} - {y_max:.2f}")
    
    def render_charts_overview(self, charts_data: List[Dict]) -> None:
        """Render complete chart viewer with all features"""
        if not charts_data:
            st.warning("📊 No hay gráficos para mostrar.")
            return
        
        # Initialize session state for pagination
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 1
        
        # Search and filters
        search_term, chart_type_filter, sort_by = self.render_search_and_filters(charts_data)
        
        # Filter and sort charts
        filtered_charts = self.filter_and_sort_charts(
            charts_data, search_term, chart_type_filter, sort_by
        )
        
        # Reset page if filters changed
        if len(filtered_charts) != len(charts_data):
            st.session_state.current_page = 1
        
        # Show results summary
        st.markdown(f"""
        <div class="success-message">
            📊 <strong>Mostrando {len(filtered_charts)} de {len(charts_data)} gráficos</strong>
        </div>
        """, unsafe_allow_html=True)
        
        if not filtered_charts:
            return
        
        # Pagination controls (top)
        st.session_state.current_page = self.render_pagination_controls(
            len(filtered_charts), st.session_state.current_page, "_top"
        )
        
        # Render chart grid
        self.render_chart_grid(filtered_charts, st.session_state.current_page)
        
        # Pagination controls (bottom)
        if len(filtered_charts) > self.charts_per_page:
            st.markdown("---")
            st.session_state.current_page = self.render_pagination_controls(
                len(filtered_charts), st.session_state.current_page, "_bottom"
            )
    
    def render_chart_statistics(self, charts_data: List[Dict]) -> None:
        """Render chart statistics with professional styling"""
        if not charts_data:
            return
        
        # Calculate statistics
        total_charts = len(charts_data)
        total_points = sum(chart['info'].get('data_points', 0) for chart in charts_data)
        
        # Chart type distribution
        type_counts = {}
        for chart in charts_data:
            chart_type = chart['type']
            type_counts[chart_type] = type_counts.get(chart_type, 0) + 1
        
        # Display statistics with professional styling
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <div style="font-size: 1.8rem; font-weight: 700; color: #ecf0f1; margin-bottom: 0.3rem;">
                    {total_charts:,}
                </div>
                <div style="font-size: 0.9rem; color: #bdc3c7;">📊 Total Gráficos</div>
            </div>
            """.format(total_charts=total_charts), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <div style="font-size: 1.8rem; font-weight: 700; color: #ecf0f1; margin-bottom: 0.3rem;">
                    {total_points:,}
                </div>
                <div style="font-size: 0.9rem; color: #bdc3c7;">📈 Puntos de Datos</div>
            </div>
            """.format(total_points=total_points), unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <div style="font-size: 1.8rem; font-weight: 700; color: #ecf0f1; margin-bottom: 0.3rem;">
                    {unique_types}
                </div>
                <div style="font-size: 0.9rem; color: #bdc3c7;">🎯 Tipos Únicos</div>
            </div>
            """.format(unique_types=len(type_counts)), unsafe_allow_html=True)
        
        with col4:
            avg_points = total_points / total_charts if total_charts > 0 else 0
            st.markdown("""
            <div class="metric-card">
                <div style="font-size: 1.8rem; font-weight: 700; color: #ecf0f1; margin-bottom: 0.3rem;">
                    {avg_points:,.0f}
                </div>
                <div style="font-size: 0.9rem; color: #bdc3c7;">📊 Promedio/Gráfico</div>
            </div>
            """.format(avg_points=avg_points), unsafe_allow_html=True)
        
        # Type distribution with professional styling
        if type_counts:
            st.markdown("""
            <div style="margin-top: 2rem; margin-bottom: 1rem;">
                <h4 margin-bottom: 1rem;">📊 Distribución por Tipo</h4>
            </div>
            """, unsafe_allow_html=True)
            
            for chart_type, count in sorted(type_counts.items()):
                percentage = (count / total_charts) * 100
                st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.05); 
                            padding: 0.8rem; border-radius: 6px; margin: 0.5rem 0;
                            border-left: 3px solid #3498db;">
                    <strong style="color: #2c3e50;">
                        {chart_type.replace('_', ' ').title()}:
                    </strong> 
                    <span style="color: #7f8c8d;">
                        {count} gráficos ({percentage:.1f}%)
                    </span>
                </div>
                """, unsafe_allow_html=True) 