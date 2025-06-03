import os
import webbrowser
from typing import List, Dict, Callable
import streamlit as st
import plotly.io as pio
import base64
from io import BytesIO
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import plotly.graph_objects as go

class ReportGenerator:
    """Generate professional HTML reports with optimized performance and progress tracking"""
    
    def __init__(self):
        self.standard_width = 600  # Reduced for faster processing
        self.standard_height = 400  # Reduced for faster processing
        self.max_workers = 4  # Parallel processing
        self.conversion_timeout = 30  # Timeout per chart conversion
        
    def generate_html_report(self, charts_data: List[Dict], db_name: str, output_filename: str, 
                           background_color: str = "#ffffff", use_static_images: bool = False,
                           progress_callback: Callable = None) -> bool:
        """Generate an optimized HTML report for PDF printing with interactive charts"""
        try:
            if not charts_data:
                st.error("❌ No hay gráficos para generar el reporte")
                return False
            
            total_charts = len(charts_data)
            start_time = time.time()
            
            # Initialize progress
            if progress_callback:
                progress_callback(0, total_charts, "Iniciando generación de HTML...", 0)
            
            # Force interactive mode for PDF printing optimization
            use_static_images = False
            st.info("📄 Generando reporte HTML optimizado para impresión en PDF")
            
            # Calculate statistics quickly
            total_points = sum(chart['info'].get('data_points', 0) for chart in charts_data)
            type_counts = {}
            for chart in charts_data:
                chart_type = chart['type']
                type_counts[chart_type] = type_counts.get(chart_type, 0) + 1
            
            if progress_callback:
                progress_callback(10, total_charts, "Preparando estructura HTML...", time.time() - start_time)
            
            # Process charts for HTML (no conversion needed)
            processed_charts = charts_data
            
            if progress_callback:
                progress_callback(50, total_charts, "Aplicando estilos y optimizaciones...", time.time() - start_time)
            
            # Generate HTML content optimized for printing
            html_content = self._generate_html_structure(
                db_name, total_charts, total_points, type_counts, processed_charts, 
                background_color, use_static_images
            )
            
            if progress_callback:
                progress_callback(90, total_charts, "Escribiendo archivo HTML...", time.time() - start_time)
            
            # Write to file
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            if progress_callback:
                elapsed = time.time() - start_time
                progress_callback(total_charts, total_charts, f"Completado en {elapsed:.1f}s", elapsed)
            
            st.success(f"✅ Reporte HTML generado: {output_filename}")
            st.info("📋 Para convertir a PDF: Abrir en navegador → Ctrl+P → Guardar como PDF")
            return True
            
        except Exception as e:
            st.error(f"❌ Error generando reporte: {e}")
            return False
    
    def _convert_charts_parallel(self, charts_data: List[Dict], progress_callback: Callable, start_time: float) -> List[Dict]:
        """Convert charts to images with improved error handling"""
        processed_charts = []
        completed_count = 0
        total_charts = len(charts_data)
        failed_count = 0
        
        # First try a few charts sequentially to test conversion
        test_charts = charts_data[:3]  # Test first 3 charts
        st.info("🧪 Probando conversión con algunos gráficos...")
        
        test_success = 0
        for i, chart in enumerate(test_charts):
            result = self._convert_single_chart(chart, i)
            if result:
                test_success += 1
        
        # If test conversion fails, use interactive mode
        if test_success == 0:
            st.warning("⚠️ Conversión de imágenes falló en pruebas, usando modo interactivo")
            return charts_data
        
        st.success(f"✅ Conversión de prueba exitosa ({test_success}/{len(test_charts)})")
        
        # Use threading for parallel processing with smaller batches
        batch_size = min(self.max_workers, 8)  # Limit batch size
        
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            # Process in smaller batches to avoid memory issues
            for batch_start in range(0, total_charts, batch_size * 2):
                batch_end = min(batch_start + batch_size * 2, total_charts)
                batch_charts = charts_data[batch_start:batch_end]
                
                # Submit batch for processing
                future_to_chart = {
                    executor.submit(self._convert_single_chart, chart, batch_start + i): (chart, batch_start + i) 
                    for i, chart in enumerate(batch_charts)
                }
                
                # Process completed tasks in this batch
                for future in as_completed(future_to_chart):
                    chart, chart_index = future_to_chart[future]
                    completed_count += 1
                    
                    try:
                        # Get result with timeout
                        result = future.result(timeout=15)  # Reduced timeout
                        if result:
                            processed_charts.append(result)
                        else:
                            # Fallback to original chart
                            processed_charts.append(chart)
                            failed_count += 1
                            
                    except Exception as e:
                        # Fallback to original chart on error
                        processed_charts.append(chart)
                        failed_count += 1
                    
                    # Update progress
                    if progress_callback:
                        elapsed = time.time() - start_time
                        avg_time_per_chart = elapsed / completed_count if completed_count > 0 else 0
                        remaining_charts = total_charts - completed_count
                        eta = remaining_charts * avg_time_per_chart
                        
                        status = f"Procesando gráfico {completed_count}/{total_charts}: {chart['table_name'][:25]}..."
                        progress_callback(completed_count, total_charts, status, eta)
        
        # Sort by original index to maintain order
        processed_charts.sort(key=lambda x: next(
            (i for i, c in enumerate(charts_data) if c['table_name'] == x['table_name']), 0
        ))
        
        # Show conversion statistics
        success_count = total_charts - failed_count
        success_rate = (success_count / total_charts) * 100 if total_charts > 0 else 0
        
        if failed_count > 0:
            st.warning(f"⚠️ {failed_count} gráficos no se pudieron convertir ({success_rate:.1f}% éxito)")
        else:
            st.success(f"✅ Todos los gráficos convertidos exitosamente")
        
        return processed_charts
    
    def _convert_single_chart(self, chart: Dict, index: int) -> Dict:
        """Convert a single chart to image format with comprehensive error handling"""
        chart_name = chart.get('table_name', f'Chart_{index}')
        
        try:
            # Get the original figure
            original_figure = chart['figure']
            
            # Create a clean copy with minimal data
            figure_copy = go.Figure()
            
            # Copy only essential data with limits
            for trace in original_figure.data:
                try:
                    if hasattr(trace, 'x') and hasattr(trace, 'y'):
                        # Limit data points for memory efficiency
                        max_points = 1000
                        x_data = trace.x[:max_points] if len(trace.x) > max_points else trace.x
                        y_data = trace.y[:max_points] if len(trace.y) > max_points else trace.y
                        
                        # Create simple scatter trace
                        figure_copy.add_trace(go.Scatter(
                            x=x_data,
                            y=y_data,
                            mode='lines',
                            name='',
                            line=dict(color='#2c3e50', width=1),
                            showlegend=False
                        ))
                except Exception:
                    continue  # Skip problematic traces
            
            # If no traces were added, skip this chart
            if len(figure_copy.data) == 0:
                return None
            
            # Apply minimal layout
            figure_copy.update_layout(
                title=dict(text=chart_name[:40], font=dict(size=12, color='#2c3e50')),
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(size=9, color='#2c3e50'),
                width=self.standard_width,
                height=self.standard_height,
                margin=dict(l=50, r=20, t=50, b=40),
                showlegend=False,
                xaxis=dict(showgrid=True, gridcolor='#e0e0e0', color='#2c3e50'),
                yaxis=dict(showgrid=True, gridcolor='#e0e0e0', color='#2c3e50')
            )
            
            # Try conversion with different approaches
            conversion_attempts = [
                {'format': 'png', 'scale': 1.0, 'width': self.standard_width, 'height': self.standard_height},
                {'format': 'png', 'scale': 0.8, 'width': int(self.standard_width * 0.8), 'height': int(self.standard_height * 0.8)},
                {'format': 'png', 'scale': 0.6, 'width': int(self.standard_width * 0.6), 'height': int(self.standard_height * 0.6)}
            ]
            
            for attempt in conversion_attempts:
                try:
                    img_bytes = figure_copy.to_image(
                        format=attempt['format'],
                        width=attempt['width'],
                        height=attempt['height'],
                        scale=attempt['scale'],
                        engine="kaleido"
                    )
                    
                    if img_bytes and len(img_bytes) > 500:  # Valid image check
                        img_base64 = base64.b64encode(img_bytes).decode()
                        img_data = f"data:image/{attempt['format']};base64,{img_base64}"
                        
                        # Return successful conversion
                        result_chart = chart.copy()
                        result_chart['image_data'] = img_data
                        return result_chart
                        
                except Exception as conv_err:
                    continue  # Try next approach
            
            # All conversion attempts failed
            return None
            
        except Exception as e:
            return None
    
    def _test_conversion_capability(self) -> bool:
        """Test if image conversion is working properly with detailed logging"""
        st.info("🔧 [Test Conversion] Attempting to import plotly.graph_objects and plotly.io...")
        try:
            import plotly.graph_objects as go
            import plotly.io as pio
            st.success("✅ [Test Conversion] Successfully imported Plotly libraries.")
        except ImportError as e:
            st.error(f"❌ [Test Conversion] Failed to import Plotly libraries: {e}")
            return False

        st.info("🔧 [Test Conversion] Checking for Kaleido engine availability...")
        try:
            if not hasattr(pio, 'kaleido'):
                st.error("❌ [Test Conversion] pio.kaleido attribute not found. Kaleido might not be configured correctly with Plotly.")
                return False
            
            st.info("🔧 [Test Conversion] pio.kaleido attribute found. Checking pio.kaleido.scope...")
            if pio.kaleido.scope is None:
                st.warning("⚠️ [Test Conversion] pio.kaleido.scope is None. Attempting to initialize.")
                try:
                    from kaleido.scopes.plotly import PlotlyScope
                    # Default parameters for PlotlyScope might try to download plotly.js if not found locally
                    # or specified. Plotly.py should handle providing its own plotly.js.
                    # Forcing a basic scope initialization:
                    pio.kaleido.scope = PlotlyScope()
                    st.success("✅ [Test Conversion] Successfully initialized pio.kaleido.scope.")
                except Exception as e_scope:
                    st.error(f"❌ [Test Conversion] Failed to initialize pio.kaleido.scope: {e_scope}")
                    import traceback
                    st.error(f"Traceback: {traceback.format_exc()}")
                    return False
            else:
                st.success("✅ [Test Conversion] pio.kaleido.scope is already available.")
        except Exception as e:
            st.error(f"❌ [Test Conversion] Error accessing or initializing Kaleido scope: {e}")
            import traceback
            st.error(f"Traceback: {traceback.format_exc()}")
            return False

        st.info("🔧 [Test Conversion] Creating a simple test figure...")
        try:
            test_fig = go.Figure(data=go.Scatter(x=[1, 2, 3], y=[1, 4, 2]))
            test_fig.update_layout(width=300, height=200, title="Kaleido Test")
            st.success("✅ [Test Conversion] Test figure created.")
        except Exception as e:
            st.error(f"❌ [Test Conversion] Error creating test figure: {e}")
            return False

        st.info("⏳ [Test Conversion] Attempting to convert test figure to PNG using Kaleido... (This may take a moment)")
        img_bytes = None
        try:
            img_bytes = test_fig.to_image(format="png", width=300, height=200, engine="kaleido")
            st.success("✅ [Test Conversion] test_fig.to_image() call completed.")
        except Exception as e:
            st.error(f"❌ [Test Conversion] Error during test_fig.to_image(): {e}")
            import traceback
            st.error(f"Traceback: {traceback.format_exc()}")
            return False

        if img_bytes and len(img_bytes) > 100:
            st.success("🎉 [Test Conversion] Kaleido image conversion test successful. Image bytes received.")
            return True
        elif img_bytes is not None:
            st.error(f"❌ [Test Conversion] Kaleido image conversion test produced an empty or too small image (size: {len(img_bytes)} bytes). Check Kaleido installation and dependencies.")
            return False
        else:
            st.error("❌ [Test Conversion] Kaleido image conversion test failed: to_image() returned None. Check Kaleido logs or run a simple Kaleido script outside Streamlit.")
            return False
    
    def _convert_figure_to_image(self, figure, format='png') -> str:
        """Legacy method for backwards compatibility - now optimized"""
        try:
            # Optimize figure for print compatibility
            figure.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': '#2c3e50', 'size': 10},
                title={'font': {'color': '#2c3e50', 'size': 12}},
                xaxis={'color': '#2c3e50', 'gridcolor': 'rgba(44,62,80,0.2)', 'linecolor': '#2c3e50'},
                yaxis={'color': '#2c3e50', 'gridcolor': 'rgba(44,62,80,0.2)', 'linecolor': '#2c3e50'},
                width=self.standard_width,
                height=self.standard_height
            )
            
            # Always use PNG for speed
            img_bytes = figure.to_image(format="png", width=self.standard_width, height=self.standard_height, scale=1.5)
            img_base64 = base64.b64encode(img_bytes).decode()
            return f"data:image/png;base64,{img_base64}"
                
        except Exception as e:
            st.warning(f"⚠️ Error convirtiendo gráfico a imagen: {e}")
            return None
    
    def _get_professional_colors(self, background_color: str) -> Dict[str, str]:
        """Get professional color palette based on background"""
        # Determine if background is dark or light
        bg_color = background_color.lower()
        is_dark = bg_color in ['#000000', '#1a1a1a', '#2c3e50', '#34495e'] or 'dark' in bg_color
        
        if is_dark:
            return {
                'text_primary': '#ecf0f1',
                'text_secondary': '#bdc3c7',
                'accent_primary': '#3498db',
                'accent_secondary': '#2980b9',
                'success': '#27ae60',
                'warning': '#f39c12',
                'border': 'rgba(236, 240, 241, 0.2)',
                'card_bg': 'rgba(255, 255, 255, 0.1)',
                'header_bg': 'linear-gradient(135deg, #2c3e50 0%, #34495e 100%)'
            }
        else:
            return {
                'text_primary': '#2c3e50',
                'text_secondary': '#7f8c8d',
                'accent_primary': '#2980b9',
                'accent_secondary': '#3498db',
                'success': '#27ae60',
                'warning': '#e67e22',
                'border': 'rgba(44, 62, 80, 0.2)',
                'card_bg': 'rgba(44, 62, 80, 0.05)',
                'header_bg': 'linear-gradient(135deg, #34495e 0%, #2c3e50 100%)'
            }
    
    def _generate_html_structure(self, db_name: str, total_charts: int, 
                                total_points: int, type_counts: Dict, charts_data: List[Dict],
                                background_color: str = "#ffffff", use_static_images: bool = False) -> str:
        """Generate the complete HTML structure optimized for PDF printing"""
        
        colors = self._get_professional_colors(background_color)
        
        # Determine if we need dark or light theme for optimal contrast
        is_dark_background = self._is_dark_background(background_color)
        text_color = colors['text_primary']
        secondary_text_color = colors['text_secondary']
        
        # HTML header with PDF-optimized styling
        html_start = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reporte de Espectros Armónicos - {db_name}</title>
            <script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
            <style>
                /* PDF Print Optimized Styles */
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                @page {{
                    margin: 0.5in 0.75in;
                    size: A4 portrait;
                }}
                
                body {{
                    font-family: 'Segoe UI', 'Arial', sans-serif;
                    background-color: {background_color} !important;
                    color: {text_color};
                    line-height: 1.3;
                    font-size: 11pt;
                    -webkit-print-color-adjust: exact;
                    print-color-adjust: exact;
                }}
                
                .container {{
                    background-color: {background_color} !important;
                    min-height: 100vh;
                    width: 100%;
                }}
                
                /* Header section - stays on first page */
                .header {{
                    background: {colors['header_bg']} !important;
                    padding: 3rem;
                    border-radius: 6px;
                    margin-bottom: 2rem;
                    text-align: center;
                    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
                    page-break-inside: avoid;
                    page-break-after: always;
                    min-height: 40vh;
                    -webkit-print-color-adjust: exact;
                    print-color-adjust: exact;
                }}
                
                .header h1 {{
                    font-size: 24pt;
                    margin-bottom: 1rem;
                    color: #ffffff !important;
                    font-weight: 600;
                }}
                
                .header p {{
                    font-size: 12pt;
                    color: rgba(255, 255, 255, 0.9) !important;
                    margin: 0.5rem 0;
                }}
                
                /* Statistics grid */
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(4, 1fr);
                    gap: 1rem;
                    margin-bottom: 2rem;
                    page-break-inside: avoid;
                    page-break-after: always;
                    background-color: {background_color} !important;
                }}
                
                .stat-card {{
                    background: {colors['card_bg']} !important;
                    padding: 1.5rem;
                    border-radius: 6px;
                    text-align: center;
                    border: 1px solid {colors['border']};
                    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
                    -webkit-print-color-adjust: exact;
                    print-color-adjust: exact;
                }}
                
                .stat-number {{
                    font-size: 18pt;
                    font-weight: 700;
                    color: {colors['accent_primary']} !important;
                    margin-bottom: 0.5rem;
                    display: block;
                }}
                
                .stat-label {{
                    font-size: 10pt;
                    color: {secondary_text_color} !important;
                    font-weight: 500;
                }}
                
                /* Chart containers - optimized for A4 pages */
                .chart-container {{
                    background: {background_color} !important;
                    border: 1px solid {colors['border']};
                    border-radius: 6px;
                    padding: 1.5rem;
                    margin: 0;
                    page-break-before: always;
                    page-break-inside: avoid;
                    page-break-after: avoid;
                    height: calc(100vh - 2in);
                    max-height: 9.5in;
                    min-height: 8in;
                    display: flex;
                    flex-direction: column;
                    box-sizing: border-box;
                    width: 100%;
                    -webkit-print-color-adjust: exact;
                    print-color-adjust: exact;
                }}
                
                .chart-container:first-child {{
                    page-break-before: auto;
                }}
                
                .chart-header {{
                    margin-bottom: 1.5rem;
                    padding-bottom: 1rem;
                    border-bottom: 1px solid {colors['border']};
                    flex-shrink: 0;
                    padding-top: 1rem;
                }}
                
                .chart-title {{
                    font-size: 14pt;
                    font-weight: 600;
                    margin-bottom: 0.8rem;
                    color: {text_color};
                    word-wrap: break-word;
                    line-height: 1.3;
                }}
                
                .chart-meta {{
                    display: flex;
                    gap: 1rem;
                    font-size: 10pt;
                    color: {secondary_text_color};
                    align-items: center;
                    flex-wrap: wrap;
                    justify-content: space-between;
                    width: 100%;
                }}
                
                .chart-badge {{
                    background: {colors['accent_primary']};
                    color: white;
                    padding: 0.3rem 0.8rem;
                    border-radius: 12px;
                    font-size: 9pt;
                    font-weight: 600;
                    white-space: nowrap;
                }}
                
                .chart-plot {{
                    flex: 1;
                    width: 100%;
                    height: 450px;
                    margin: 1rem 0 0 0;
                    border-radius: 4px;
                    padding-top: 0.5rem;
                }}
                
                .chart-plot > div {{
                    width: 100%;
                    height: 100%;
                }}
                
                /* Search section - hidden in print */
                .search-container {{
                    background: {colors['card_bg']} !important;
                    padding: 2rem;
                    border-radius: 6px;
                    margin-bottom: 2rem;
                    border: 1px solid {colors['border']};
                    page-break-inside: avoid;
                    page-break-after: always;
                    -webkit-print-color-adjust: exact;
                    print-color-adjust: exact;
                }}
                
                .search-container h3 {{
                    margin-bottom: 1rem;
                    color: {text_color} !important;
                    font-size: 14pt;
                    font-weight: 600;
                }}
                
                .search-input {{
                    width: 100%;
                    padding: 0.8rem;
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    background: {background_color} !important;
                    color: {text_color} !important;
                    font-size: 11pt;
                }}
                
                .filter-buttons {{
                    display: flex;
                    gap: 0.6rem;
                    margin-top: 1rem;
                    flex-wrap: wrap;
                }}
                
                .filter-btn {{
                    padding: 0.6rem 1rem;
                    border: 1px solid {colors['border']};
                    border-radius: 12px;
                    background: {colors['card_bg']} !important;
                    color: {text_color} !important;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    font-size: 10pt;
                    font-weight: 500;
                }}
                
                .filter-btn:hover, .filter-btn.active {{
                    background: {colors['accent_primary']} !important;
                    border-color: {colors['accent_primary']};
                    color: white !important;
                }}
                
                /* Footer */
                .footer {{
                    background: {colors['header_bg']} !important;
                    padding: 1rem;
                    border-radius: 6px;
                    text-align: center;
                    margin-top: 1rem;
                    color: white !important;
                    page-break-inside: avoid;
                    -webkit-print-color-adjust: exact;
                    print-color-adjust: exact;
                }}
                
                .footer h3 {{
                    font-size: 12pt;
                    margin-bottom: 0.4rem;
                }}
                
                .footer p {{
                    font-size: 9pt;
                    margin: 0.2rem 0;
                }}
                
                /* Print-specific styles */
                @media print {{
                    body {{
                        background: white !important;
                        color: #000 !important;
                        -webkit-print-color-adjust: exact;
                        print-color-adjust: exact;
                        margin: 0;
                        padding: 0;
                    }}
                    
                    /* Hide loading overlay in print */
                    #loadingOverlay {{
                        display: none !important;
                    }}
                    
                    .search-container {{
                        display: none !important;
                    }}
                    
                    .header {{
                        background: #2c3e50 !important;
                        -webkit-print-color-adjust: exact;
                        print-color-adjust: exact;
                        page-break-after: always !important;
                        min-height: 60vh;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                    }}
                    
                    .stats-grid {{
                        page-break-after: always !important;
                        margin-top: 2rem;
                    }}
                
                    .chart-container {{
                        page-break-before: always;
                        margin: 0;
                        padding: 1.5rem;
                        border: 1px solid #ddd;
                        background: white !important;
                        height: 100vh;
                        width: 7.5in;
                        max-width: 7.5in;
                        box-shadow: none;
                        display: flex;
                        flex-direction: column;
                    }}
                    
                    .chart-container:first-child {{
                        page-break-before: always;
                    }}
                    
                    .chart-header {{
                        flex-shrink: 0;
                        height: 100px;
                        margin-bottom: 1rem;
                        padding-bottom: 0.8rem;
                        padding-top: 1rem;
                        border-bottom: 1px solid #ddd;
                    }}
                    
                    .chart-plot {{
                        flex: 1;
                        width: 100%;
                        height: calc(100vh - 180px);
                        margin: 0;
                        padding-top: 0.5rem;
                    }}
                    
                    .chart-plot > div {{
                        width: 100%;
                        height: 100%;
                    }}
                    
                    .chart-title {{
                        color: #000 !important;
                        font-size: 11pt !important;
                        margin-bottom: 0.5rem;
                    }}
                    
                    .chart-meta {{
                        color: #666 !important;
                        font-size: 8pt !important;
                        gap: 0.8rem;
                    }}
                    
                    .chart-badge {{
                        background: #2c3e50 !important;
                        color: white !important;
                        padding: 0.2rem 0.5rem !important;
                        font-size: 7pt !important;
                    }}
                    
                    .footer {{
                        background: #2c3e50 !important;
                        -webkit-print-color-adjust: exact;
                        print-color-adjust: exact;
                    }}
                    
                    .stat-card {{
                        border: 1px solid #ddd !important;
                        background: white !important;
                        padding: 0.5rem !important;
                    }}
                    
                    .stat-number {{
                        color: #2c3e50 !important;
                        font-size: 12pt !important;
                    }}
                    
                    .stat-label {{
                        color: #666 !important;
                        font-size: 7pt !important;
                    }}
                    
                    /* Ensure proper page breaks */
                    .header, .stats-grid {{
                        page-break-after: always !important;
                    }}
                    
                    /* Ensure charts don't break */
                    .chart-container * {{
                        page-break-inside: avoid !important;
                    }}
                }}
                
                /* Mobile responsiveness */
                @media (max-width: 768px) {{
                    .stats-grid {{
                        grid-template-columns: repeat(2, 1fr);
                    }}
                    
                    .chart-meta {{
                        flex-direction: column;
                        align-items: flex-start;
                        gap: 0.4rem;
                    }}
                    
                    .chart-plot {{
                        height: 300px;
                    }}
                }}
            </style>
        </head>
        <body>
            <!-- Loading overlay -->
            <div id="loadingOverlay" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
                 background: rgba(44, 62, 80, 0.9); color: white; display: flex; align-items: center; 
                 justify-content: center; z-index: 9999; font-family: Arial;">
                <div style="text-align: center;">
                    <div style="font-size: 24px; margin-bottom: 20px;">📊 Cargando Reporte</div>
                    <div style="font-size: 16px; opacity: 0.8;">Preparando {total_charts} gráficos para impresión...</div>
                    <div style="margin-top: 20px; width: 200px; height: 4px; background: rgba(255,255,255,0.3); border-radius: 2px;">
                        <div id="loadingBar" style="height: 100%; background: #3498db; width: 0%; border-radius: 2px; transition: width 0.3s;"></div>
                    </div>
                    <div style="margin-top: 10px; font-size: 12px; opacity: 0.7;">El reporte se mostrará automáticamente al completarse</div>
                </div>
            </div>
            
            <div class="container" id="mainContent" style="opacity: 0; transition: opacity 0.5s; background-color: {background_color} !important; min-height: 100vh;">
                <div class="header">
                    <h1>📊 Reporte de Espectros Armónicos</h1>
                    <p>Análisis generado desde: <strong>{db_name}</strong></p>
                    <p>Generado el {self._get_current_datetime()}</p>
                    <p>Optimizado para impresión PDF • Un gráfico por página</p>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <span class="stat-number">{total_charts:,}</span>
                        <div class="stat-label">Total de Gráficos</div>
                    </div>
                    <div class="stat-card">
                        <span class="stat-number">{total_points:,}</span>
                        <div class="stat-label">Puntos de Datos</div>
                    </div>
                    <div class="stat-card">
                        <span class="stat-number">{len(type_counts)}</span>
                        <div class="stat-label">Tipos de Análisis</div>
                    </div>
                    <div class="stat-card">
                        <span class="stat-number">{total_points // total_charts if total_charts > 0 else 0:,}</span>
                        <div class="stat-label">Promedio por Gráfico</div>
                    </div>
                </div>
                
                <div class="search-container">
                    <h3>🔍 Navegación y Filtros (Solo en pantalla)</h3>
                    <input type="text" id="searchInput" class="search-input" placeholder="Buscar por nombre de tabla...">
                    <div class="filter-buttons">
                        <button class="filter-btn active" onclick="filterCharts('all')">Todos</button>
        """
        
        # Add filter buttons for each chart type
        chart_type_emoji = {
            'waveform': '📈',
            'spectrum_hz': '📊',
            'spectrum_order': '📊',
            'generic': '📊'
        }
        
        for chart_type in type_counts.keys():
            emoji = chart_type_emoji.get(chart_type, '📊')
            display_name = chart_type.replace('_', ' ').title()
            html_start += f'<button class="filter-btn" onclick="filterCharts(\'{chart_type}\')">{emoji} {display_name} ({type_counts[chart_type]})</button>\n'
        
        html_start += """
                    </div>
                </div>
                
                <div id="chartsContainer" class="charts-grid">
        """
        
        # Generate chart containers optimized for printing
        charts_html = ""
        for i, chart in enumerate(charts_data):
            chart_type = chart['type']
            table_name = chart['table_name']
            info = chart['info']
            figure = chart['figure']
            
            emoji = chart_type_emoji.get(chart_type, '📊')
            
            # Optimize figure for printing with proper colors and integer formatting
            figure_copy = figure
            figure_copy.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color=text_color, size=10, family='Arial'),
                title=dict(
                    text=f"{emoji} {table_name}",
                    font=dict(color=text_color, size=12),
                    x=0.5,
                    xanchor='center',
                    y=0.95,
                    yanchor='top'
                ),
                xaxis=dict(
                    color=text_color,
                    gridcolor=colors['border'],
                    linecolor=text_color,
                    tickfont=dict(color=text_color, size=9),
                    title_font=dict(size=10),
                    tickformat='.0f'  # Show integers only
                ),
                yaxis=dict(
                    color=text_color,
                    gridcolor=colors['border'],
                    linecolor=text_color,
                    tickfont=dict(color=text_color, size=9),
                    title_font=dict(size=10),
                    tickformat='.0f'  # Show integers only
                ),
                legend=dict(
                    font=dict(color=text_color, size=9),
                    x=0.98,
                    xanchor='right',
                    y=0.98,
                    yanchor='top'
                ),
                margin=dict(l=50, r=30, t=50, b=40),
                height=400,  # Fixed height for consistency
                width=700,   # Fixed width that fits in A4
                showlegend=True if len(figure.data) > 1 else False,
                autosize=False
            )
            
            # Since data is now rounded at source, just ensure hover templates are clean
            for trace in figure_copy.data:
                if hasattr(trace, 'hovertemplate') and trace.hovertemplate:
                    # Data is already rounded, just ensure format is clean
                    continue
                elif hasattr(trace, 'type'):
                    # Set appropriate hover templates based on chart type
                    if trace.type == 'scatter' and hasattr(trace, 'mode') and 'lines' in str(trace.mode):
                        trace.hovertemplate = '<b>Tiempo:</b> %{x}s<br><b>Amplitud:</b> %{y}<extra></extra>'
                    elif trace.type == 'bar':
                        if 'hz' in table_name.lower() or 'freq' in table_name.lower():
                            trace.hovertemplate = '<b>Frecuencia:</b> %{x} Hz<br><b>Magnitud:</b> %{y}<extra></extra>'
                        elif 'order' in table_name.lower() or 'orden' in table_name.lower():
                            trace.hovertemplate = '<b>Orden:</b> %{x}<br><b>Magnitud:</b> %{y}<extra></extra>'
                        else:
                            trace.hovertemplate = '<b>X:</b> %{x}<br><b>Y:</b> %{y}<extra></extra>'
                    else:
                        trace.hovertemplate = '<b>X:</b> %{x}<br><b>Y:</b> %{y}<extra></extra>'
            
            # Configure for web display (responsive, no mode bar)
            figure_copy.update_layout(
                modebar={'remove': ['zoom', 'pan', 'select', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d', 'toImage', 'sendDataToCloud']}
            )
            
            # Update trace colors for better contrast
            for trace in figure_copy.data:
                if hasattr(trace, 'line') and trace.line:
                    if not trace.line.color or trace.line.color in ['blue', 'red', 'green']:
                        trace.line.color = colors['accent_primary']
                if hasattr(trace, 'marker') and trace.marker:
                    if not trace.marker.color:
                        trace.marker.color = colors['accent_primary']
            
            charts_html += f"""
                <div class="chart-container" data-type="{chart_type}" data-name="{table_name.lower()}">
                    <div class="chart-header">
                        <div class="chart-title">{table_name}</div>
                        <div class="chart-meta">
                            <span class="chart-badge">{chart_type.replace('_', ' ').title()}</span>
                            <span>📊 {info.get('data_points', 0):,} puntos de datos</span>
                            <span style="margin-left: auto;">📄 Página {i + 2} de {len(charts_data) + 1}</span>
                        </div>
                    </div>
                    <div class="chart-plot" id="chart-{i}">
                        {figure_copy.to_html(full_html=False, include_plotlyjs=False, div_id=f"chart-plot-{i}")}
                    </div>
                </div>
            """
        
        # HTML footer with JavaScript for interactivity
        html_end = f"""
                </div>
                
                <div class="footer">
                    <h3>🚀 Analizador de Espectros Armónicos</h3>
                    <p>Reporte optimizado para PDF • {total_charts} gráficos • {total_points:,} puntos de datos • {total_charts + 1} páginas totales</p>
                    <p>Para imprimir: Ctrl+P → Más configuraciones → Gráficos en color → Guardar como PDF</p>
                    <p>© 2024 • Versión 3.1 • PDF Print Optimized</p>
                </div>
            </div>
            
            <script>
                let chartsLoaded = 0;
                const totalCharts = {total_charts};
                
                // Update loading progress
                function updateProgress() {{
                    const progress = (chartsLoaded / totalCharts) * 100;
                    document.getElementById('loadingBar').style.width = progress + '%';
                    
                    if (chartsLoaded >= totalCharts) {{
                        setTimeout(() => {{
                            document.getElementById('loadingOverlay').style.display = 'none';
                            document.getElementById('mainContent').style.opacity = '1';
                        }}, 500);
                    }}
                }}
                
                // Wait for all charts to load
                document.addEventListener('DOMContentLoaded', function() {{
                    const searchInput = document.getElementById('searchInput');
                    const charts = document.querySelectorAll('.chart-container');
                    
                    // Monitor chart loading
                    const chartDivs = document.querySelectorAll('[id^="chart-plot-"]');
                    
                    if (chartDivs.length === 0) {{
                        // No charts, hide loading immediately
                        document.getElementById('loadingOverlay').style.display = 'none';
                        document.getElementById('mainContent').style.opacity = '1';
                        return;
                    }}
                    
                    // Auto-hide loading after shorter time for better UX
                    setTimeout(() => {{
                        document.getElementById('loadingOverlay').style.display = 'none';
                        document.getElementById('mainContent').style.opacity = '1';
                    }}, 3000);  // Reduced from 10 seconds to 3 seconds
                    
                    // Check for Plotly charts loading
                    const checkInterval = setInterval(() => {{
                        let loadedCount = 0;
                        chartDivs.forEach(div => {{
                            if (div.querySelector('.plotly-graph-div')) {{
                                loadedCount++;
                            }}
                        }});
                        
                        chartsLoaded = loadedCount;
                        updateProgress();
                        
                        // Hide loading when 80% of charts are loaded for better responsiveness
                        if (loadedCount >= totalCharts * 0.8) {{
                            clearInterval(checkInterval);
                            setTimeout(() => {{
                                document.getElementById('loadingOverlay').style.display = 'none';
                                document.getElementById('mainContent').style.opacity = '1';
                            }}, 100);
                        }}
                    }}, 50);  // Check more frequently
                    
                    // Search functionality
                    if (searchInput) {{
                        searchInput.addEventListener('input', function() {{
                            const searchTerm = this.value.toLowerCase();
                            filterChartsBySearch(searchTerm);
                        }});
                    }}
                    
                    // Initialize chart numbering
                    updateChartNumbers();
                    
                    // Ensure charts are properly sized
                    setTimeout(resizeCharts, 500);
                    
                    // Handle window resize
                    window.addEventListener('resize', resizeCharts);
                }});
                
                function resizeCharts() {{
                    // Force Plotly charts to resize
                    const chartDivs = document.querySelectorAll('[id^="chart-plot-"]');
                    chartDivs.forEach(function(div) {{
                        if (window.Plotly && window.Plotly.Plots.resize) {{
                            window.Plotly.Plots.resize(div);
                        }}
                    }});
                }}
                
                function filterCharts(type) {{
                    const charts = document.querySelectorAll('.chart-container');
                    const buttons = document.querySelectorAll('.filter-btn');
                    
                    // Update active button
                    buttons.forEach(btn => btn.classList.remove('active'));
                    event.target.classList.add('active');
                    
                    // Filter charts
                    charts.forEach(chart => {{
                        if (type === 'all' || chart.dataset.type === type) {{
                            chart.style.display = 'flex';
                        }} else {{
                            chart.style.display = 'none';
                        }}
                    }});
                    
                    updateChartNumbers();
                    setTimeout(resizeCharts, 100);
                }}
                
                function filterChartsBySearch(searchTerm) {{
                    const charts = document.querySelectorAll('.chart-container');
                    
                    charts.forEach(chart => {{
                        const name = chart.dataset.name;
                        if (searchTerm === '' || name.includes(searchTerm)) {{
                            chart.style.display = 'flex';
                        }} else {{
                            chart.style.display = 'none';
                        }}
                    }});
                    
                    updateChartNumbers();
                    setTimeout(resizeCharts, 100);
                }}
                
                function updateChartNumbers() {{
                    const visibleCharts = document.querySelectorAll('.chart-container[style*="flex"], .chart-container:not([style*="none"])');
                    const totalPages = visibleCharts.length + 1; // +1 for header page
                    
                    visibleCharts.forEach((chart, index) => {{
                        const meta = chart.querySelector('.chart-meta');
                        const pageSpan = meta.querySelector('span:last-child');
                        if (pageSpan) {{
                            pageSpan.textContent = `📄 Página ${{index + 2}} de ${{totalPages}}`;
                        }}
                    }});
                }}
                
                // Print optimization
                window.addEventListener('beforeprint', function() {{
                    // Ensure all charts are visible for printing
                    document.querySelectorAll('.chart-container').forEach(chart => {{
                        chart.style.display = 'flex';
                    }});
                    
                    // Update page numbers for print
                    updateChartNumbers();
                    
                    // Force chart resize before printing
                    setTimeout(resizeCharts, 100);
                }});
                
                window.addEventListener('afterprint', function() {{
                    // Restore any filters after printing
                    setTimeout(resizeCharts, 100);
                }});
            </script>
        </body>
        </html>
        """
        
        return html_start + charts_html + html_end
    
    def _is_dark_background(self, background_color: str) -> bool:
        """Determine if a background color is dark"""
        # Convert hex to RGB and calculate luminance
        hex_color = background_color.lstrip('#')
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            # Calculate relative luminance
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            return luminance < 0.5
        return False
    
    def _get_current_datetime(self) -> str:
        """Get current datetime formatted"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def open_report(self, report_path: str) -> None:
        """Open the report in the default browser"""
        try:
            webbrowser.open(f"file://{os.path.abspath(report_path)}")
        except Exception as e:
            st.error(f"❌ Error abriendo el reporte: {e}") 