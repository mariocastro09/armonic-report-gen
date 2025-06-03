import streamlit as st
import os
import tempfile
from pathlib import Path
import time
from database_handler import DatabaseHandler
from data_processor import DataProcessor
from chart_generator import ChartGenerator
from report_generator import ReportGenerator
from session_manager import SessionManager
from chart_viewer import ChartViewer

# Page configuration
st.set_page_config(
    page_title="Analizador de Espectros Armónicos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for complete professional theme
st.markdown("""
<style>
    /* Professional and sober color scheme */

    /* Remove all white backgrounds */
    .stApp > div {
        background: transparent !important;
    }
    
    .main .block-container {
        background: transparent !important;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Professional sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%) !important;
    }
    
    /* Professional input fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div,
    .stFileUploader > div {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #ecf0f1 !important;
        border: 1px solid rgba(236, 240, 241, 0.2) !important;
        border-radius: 6px;
    }
    
    /* Professional file uploader */
    .stFileUploader > div > div {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 2px dashed #3498db !important;
        border-radius: 8px;
        color: #ecf0f1 !important;
    }
    
    /* Professional expanders */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #ecf0f1 !important;
        border-radius: 6px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        border: 1px solid rgba(236, 240, 241, 0.1);
    }
    
    .streamlit-expanderContent {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(236, 240, 241, 0.1) !important;
        border-radius: 0 0 6px 6px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Professional color picker */
    .stColorPicker > div > div > input {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(236, 240, 241, 0.2) !important;
        border-radius: 6px;
    }
    
    .main-header {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        padding: 3rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        margin-bottom: 0.8rem;
        font-weight: 600;
        color: #ecf0f1;
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin: 0;
        color: #bdc3c7;
    }
    
    .feature-card {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
        margin-bottom: 1rem;
        border-left: 3px solid #3498db;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        color: #ecf0f1 !important;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    }
    
    .step-indicator {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        border-left: 3px solid #27ae60;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
        color: #ecf0f1 !important;
    }
    
    .step-number {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        color: white;
        border-radius: 50%;
        width: 35px;
        height: 35px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        margin-right: 12px;
        font-size: 1.1em;
        box-shadow: 0 2px 8px rgba(44, 62, 80, 0.3);
    }
    
    .status-success {
        background: rgba(39, 174, 96, 0.15) !important;
        color: #2ecc71 !important;
        padding: 1.2rem;
        border-radius: 6px;
        border: 1px solid rgba(39, 174, 96, 0.3);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .status-error {
        background: rgba(231, 76, 60, 0.15) !important;
        color: #e74c3c !important;
        padding: 1.2rem;
        border-radius: 6px;
        border: 1px solid rgba(231, 76, 60, 0.3);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 3px 15px rgba(44, 62, 80, 0.25);
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(44, 62, 80, 0.35);
    }
    
    .info-badge {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: 500;
        margin: 0.2rem;
        display: inline-block;
        box-shadow: 0 2px 6px rgba(52, 152, 219, 0.25);
    }
    
    .success-message {
        background: rgba(39, 174, 96, 0.15) !important;
        color: #2ecc71 !important;
        padding: 1.2rem;
        border-radius: 6px;
        margin: 1.5rem 0;
        font-weight: 500;
        box-shadow: 0 2px 10px rgba(39, 174, 96, 0.15);
        border: 1px solid rgba(39, 174, 96, 0.3);
    }
    
    .warning-message {
        background: rgba(241, 196, 15, 0.15) !important;
        color: #f1c40f !important;
        padding: 1.2rem;
        border-radius: 6px;
        margin: 1.5rem 0;
        font-weight: 500;
        box-shadow: 0 2px 10px rgba(241, 196, 15, 0.15);
        border: 1px solid rgba(241, 196, 15, 0.3);
    }
    
    /* Professional button styling */
    .stButton > button {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 6px;
        padding: 0.8rem 1.8rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 3px 12px rgba(44, 62, 80, 0.25);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(44, 62, 80, 0.35) !important;
    }
    
    .stButton > button[data-baseweb="button"][kind="primary"] {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%) !important;
    }
    
    .stButton > button[data-baseweb="button"][kind="secondary"] {
        background: linear-gradient(135deg, #7f8c8d 0%, #95a5a6 100%) !important;
    }
    
    /* Progress bar styling */
    .stProgress > div > div {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%) !important;
        border-radius: 8px;
    }
    
    /* Search and filter styling */
    .search-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        padding: 1.8rem;
        border-radius: 8px;
        margin-bottom: 2.5rem;
        border: 1px solid rgba(236, 240, 241, 0.1);
        box-shadow: 0 2px 15px rgba(0, 0, 0, 0.1);
    }
    
    .chart-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
        gap: 1.5rem;
        margin-top: 1.5rem;
    }
    
    .chart-card {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px);
        border-radius: 8px;
        padding: 1.5rem;
        border: 1px solid rgba(236, 240, 241, 0.1);
        transition: transform 0.2s ease;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    }
    
    .chart-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    
    /* Session management */
    .session-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 6px;
        margin-bottom: 1.5rem;
        border-left: 3px solid #3498db;
        color: #ecf0f1;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    
    /* Pagination */
    .pagination-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 1.5rem;
        margin: 2.5rem 0;
        padding: 1.2rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 6px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Professional scrollbars */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.3);
    }

    /* Ensure plot backgrounds are transparent */
    .js-plotly-plot .plotly {
        background-color: rgba(0,0,0,0) !important;
    }
    .js-plotly-plot .plotly .main-svg {
        background-color: rgba(0,0,0,0) !important;
    }
     
    /* Report options styling */
    .report-options {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid rgba(236, 240, 241, 0.1);
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
    }
     
    /* Color picker container */
    .color-picker-container {
        background: rgba(255, 255, 255, 0.03);
        padding: 1rem;
        border-radius: 6px;
        border: 1px solid rgba(236, 240, 241, 0.1);
        margin: 0.5rem 0;
    }

</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'processing_status' not in st.session_state:
        st.session_state.processing_status = "ready"
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'charts_generated' not in st.session_state:
        st.session_state.charts_generated = []
    if 'report_path' not in st.session_state:
        st.session_state.report_path = None
    if 'current_session_id' not in st.session_state:
        st.session_state.current_session_id = None
    if 'session_manager' not in st.session_state:
        st.session_state.session_manager = SessionManager()
    if 'chart_viewer' not in st.session_state:
        st.session_state.chart_viewer = ChartViewer(charts_per_page=8)  # Reduced for better performance
    if 'view_mode' not in st.session_state:
        st.session_state.view_mode = "new_analysis"  # "new_analysis", "view_session", "session_list"

def render_header():
    """Render the main header"""
    st.markdown("""
    <div class="main-header">
        <h1>📊 Analizador de Espectros Armónicos</h1>
        <p>Herramienta avanzada para análisis de formas de onda y espectros de frecuencia</p>
    </div>
    """, unsafe_allow_html=True)

def render_navigation():
    """Render navigation tabs"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🆕 Nuevo Análisis", use_container_width=True, 
                    type="primary" if st.session_state.view_mode == "new_analysis" else "secondary"):
            st.session_state.view_mode = "new_analysis"
            st.rerun()
    
    with col2:
        if st.button("📊 Ver Sesión Actual", use_container_width=True,
                    type="primary" if st.session_state.view_mode == "view_session" else "secondary",
                    disabled=not st.session_state.charts_generated):
            st.session_state.view_mode = "view_session"
            st.rerun()
    
    with col3:
        if st.button("📚 Historial de Sesiones", use_container_width=True,
                    type="primary" if st.session_state.view_mode == "session_list" else "secondary"):
            st.session_state.view_mode = "session_list"
            st.rerun()
    
    with col4:
        # Session stats
        stats = st.session_state.session_manager.get_session_stats()
        st.metric("💾 Sesiones Guardadas", stats['total_sessions'])

def render_sidebar():
    """Render the sidebar with information"""
    with st.sidebar:
        st.markdown("### ℹ️ Información del Sistema")
        
        # Session statistics
        stats = st.session_state.session_manager.get_session_stats()
        
        st.markdown(f"""
        <div class="session-card">
            <h4>📊 Estadísticas Globales</h4>
            <p><strong>Sesiones:</strong> {stats['total_sessions']}</p>
            <p><strong>Gráficos:</strong> {stats['total_charts']:,}</p>
            <p><strong>Datos:</strong> {stats['total_data_points']:,} puntos</p>
            <p><strong>Promedio:</strong> {stats['avg_charts_per_session']} gráficos/sesión</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h4>🔧 Características Principales</h4>
            <ul style="margin: 0; padding-left: 1.2rem;">
                <li>✨ Análisis automático de bases de datos SQLite</li>
                <li>📊 Gráficos interactivos optimizados</li>
                <li>💾 Gestión de sesiones persistente</li>
                <li>🔍 Búsqueda y filtrado avanzado</li>
                <li>📄 Reportes HTML profesionales</li>
                <li>⚡ Renderizado optimizado para grandes datasets</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h4>📊 Tipos de Análisis</h4>
            <div style="margin: 0.5rem 0;">
                <span class="info-badge">📈 Formas de Onda</span><br>
                <small>Señales temporales y patrones</small>
            </div>
            <div style="margin: 0.5rem 0;">
                <span class="info-badge">📊 Espectro Hz</span><br>
                <small>Análisis de frecuencia</small>
            </div>
            <div style="margin: 0.5rem 0;">
                <span class="info-badge">📊 Espectro Orden</span><br>
                <small>Análisis de armónicos</small>
            </div>
            <div style="margin: 0.5rem 0;">
                <span class="info-badge">📊 Datos Genéricos</span><br>
                <small>Gráficos de dispersión</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Current session status
        if st.session_state.processing_status == "processing":
            st.markdown("""
            <div class="warning-message">
                🔄 <strong>Procesando datos...</strong><br>
                <small>Por favor espere mientras analizamos su base de datos</small>
            </div>
            """, unsafe_allow_html=True)
        elif st.session_state.processing_status == "completed":
            chart_count = len(st.session_state.charts_generated)
            st.markdown(f"""
            <div class="success-message">
                ✅ <strong>Análisis completado</strong><br>
                <small>{chart_count} gráficos generados exitosamente</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Help section
        st.markdown("""
        <div class="feature-card">
            <h4>🆘 Ayuda Rápida</h4>
            <details>
                <summary><strong>¿Qué archivos puedo subir?</strong></summary>
                <p style="margin: 0.5rem 0; font-size: 0.9rem;">
                    Archivos de base de datos SQLite con extensión .hfpdb
                </p>
            </details>
            <details>
                <summary><strong>¿Cómo funciona la gestión de sesiones?</strong></summary>
                <p style="margin: 0.5rem 0; font-size: 0.9rem;">
                    Cada análisis se guarda automáticamente. Puedes ver sesiones 
                    anteriores sin perder el trabajo actual.
                </p>
            </details>
            <details>
                <summary><strong>¿Hay límite de rendimiento?</strong></summary>
                <p style="margin: 0.5rem 0; font-size: 0.9rem;">
                    El sistema optimiza automáticamente grandes datasets 
                    mediante muestreo inteligente y paginación.
                </p>
            </details>
        </div>
        """, unsafe_allow_html=True)

def render_file_upload():
    """Render file upload section"""
    st.markdown("""
    <div class="step-indicator">
        <span class="step-number">1</span>
        <strong>Seleccionar Base de Datos .hfpdb</strong>
    </div>
    """, unsafe_allow_html=True)
    
    # Add information about supported file types
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <p>📁 <strong>Formato de base de datos soportado:</strong></p>
        <span class="info-badge">.hfpdb</span>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Seleccione su archivo de base de datos .hfpdb",
        type=['hfpdb'],
        help="Formato soportado: .hfpdb (base de datos SQLite especializada)"
    )
    
    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file
        
        # Success message
        st.markdown(f"""
        <div class="success-message">
            ✅ <strong>Archivo cargado exitosamente:</strong> {uploaded_file.name}
        </div>
        """, unsafe_allow_html=True)
        
        # Display file info with enhanced cards
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h4>📁 Archivo</h4>
                <p style="word-break: break-all;">{uploaded_file.name}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            file_size = len(uploaded_file.getvalue()) / 1024 / 1024  # MB
            st.markdown(f"""
            <div class="metric-card">
                <h4>📏 Tamaño</h4>
                <p>{file_size:.2f} MB</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # Determine file type
            file_ext = uploaded_file.name.split('.')[-1].upper()
            file_type_map = {
                'DB': 'SQLite estándar',
                'SQLITE': 'SQLite estándar', 
                'SQLITE3': 'SQLite v3',
                'HA1S': 'SQLite (HA1S)',
                'HFPDB': 'SQLite (HFPDB)'
            }
            file_type = file_type_map.get(file_ext, 'SQLite')
            
            st.markdown(f"""
            <div class="metric-card">
                <h4>🔧 Tipo</h4>
                <p>{file_type}</p>
            </div>
            """, unsafe_allow_html=True)
        
        return True
    
    return False

def process_database(uploaded_file):
    """Process the uploaded database file with optimizations"""
    # Save uploaded file to temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        temp_db_path = tmp_file.name
    
    try:
        # Initialize components
        db_handler = DatabaseHandler(temp_db_path)
        data_processor = DataProcessor()
        chart_generator = ChartGenerator()
        
        # Connect to database
        if not db_handler.connect():
            st.error("❌ No se pudo conectar a la base de datos")
            return False
        
        # Get tables
        table_names = db_handler.get_table_names()
        if not table_names:
            st.error("❌ No se encontraron tablas en la base de datos")
            return False
        
        # Enhanced info display
        st.markdown(f"""
        <div class="success-message">
            🔍 <strong>Base de datos analizada exitosamente</strong><br>
            <small>Encontradas {len(table_names)} tablas para procesar</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Sort tables
        sorted_tables = data_processor.get_sorted_table_list(table_names)
        
        # Progress tracking with enhanced visuals
        st.markdown("### 🔄 Procesando Tablas")
        progress_container = st.container()
        
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            progress_info = st.empty()
            
        charts_data = []
        processed_count = 0
        skipped_count = 0
        
        # Process each table with optimizations
        for i, table_name in enumerate(sorted_tables):
            progress = (i + 1) / len(sorted_tables)
            progress_bar.progress(progress)
            status_text.markdown(f"**📊 Procesando:** `{table_name}` ({i+1}/{len(sorted_tables)})")
            progress_info.markdown(f"**Progreso:** {progress*100:.1f}% completado")
            
            # Read table data
            df = db_handler.read_table(table_name)
            if df is None:
                skipped_count += 1
                continue
            
            # Prepare data for plotting
            df_prepared, is_valid = data_processor.prepare_dataframe_for_plotting(df, table_name)
            if not is_valid:
                skipped_count += 1
                continue
            
            # Determine chart type
            chart_type = data_processor.get_table_type(table_name)
            
            # Create chart with grid height for better performance
            figure = chart_generator.create_chart(df_prepared, table_name, chart_type, height=300)
            if figure is None:
                skipped_count += 1
                continue
            
            # Get chart info
            chart_info = chart_generator.get_chart_info(df_prepared)
            
            # Store chart data
            charts_data.append({
                'table_name': table_name,
                'figure': figure,
                'type': chart_type,
                'info': chart_info
            })
            
            processed_count += 1
        
        # Clean up
        db_handler.disconnect()
        os.unlink(temp_db_path)
        
        # Update session state
        st.session_state.charts_generated = charts_data
        st.session_state.processing_status = "completed"
        
        # Save session automatically
        session_data = {
            'filename': uploaded_file.name,
            'file_size': len(uploaded_file.getvalue()),
            'charts_generated': charts_data
        }
        
        # Use custom session name if provided
        custom_name = getattr(st.session_state, 'custom_session_name', None)
        session_id = st.session_state.session_manager.save_session(session_data, custom_name)
        if session_id:
            st.session_state.current_session_id = session_id
            st.success(f"💾 Sesión guardada automáticamente (ID: {session_id[:8]}...)")
        
        # Clean up the custom name
        if hasattr(st.session_state, 'custom_session_name'):
            delattr(st.session_state, 'custom_session_name')
        
        # Final status
        progress_bar.progress(1.0)
        status_text.markdown("**✅ Procesamiento completado**")
        
        # Summary message
        st.markdown(f"""
        <div class="success-message">
            🎉 <strong>Análisis completado exitosamente</strong><br>
            <small>
                📊 {processed_count} gráficos generados • 
                ⏭️ {skipped_count} tablas omitidas • 
                💾 Sesión guardada automáticamente
            </small>
        </div>
        """, unsafe_allow_html=True)
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error durante el procesamiento: {e}")
        # Clean up
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)
        return False

def render_new_analysis():
    """Render new analysis workflow"""
    st.markdown("### 🆕 Nuevo Análisis")
    
    # Option to start fresh
    if st.session_state.charts_generated:
        st.markdown("""
        <div class="warning-message">
            ⚠️ <strong>Ya tienes un análisis en curso</strong><br>
            <small>Iniciar un nuevo análisis guardará el actual automáticamente</small>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Continuar con Análisis Actual", use_container_width=True):
                st.session_state.view_mode = "view_session"
                st.rerun()
        with col2:
            if st.button("🆕 Iniciar Nuevo Análisis", use_container_width=True, type="primary"):
                # Clear current session
                st.session_state.charts_generated = []
                st.session_state.processing_status = "ready"
                st.session_state.uploaded_file = None
                st.session_state.current_session_id = None
                st.rerun()
    
    # File upload
    file_uploaded = render_file_upload()
    
    # Processing
    if file_uploaded and st.session_state.processing_status == "ready":
        st.markdown("""
        <div class="step-indicator">
            <span class="step-number">2</span>
            <strong>Procesar y Generar Gráficos</strong>
        </div>
        """, unsafe_allow_html=True)
        
        # Add guidance
        st.markdown("""
        <div style="background: rgba(23, 162, 184, 0.1); 
                    padding: 1rem; border-radius: 8px; margin: 1rem 0; 
                    border-left: 4px solid #17a2b8;">
            <h5 style="margin: 0; color: #17a2b8;">📋 Antes de procesar:</h5>
            <ul style="margin: 0.5rem 0; color: #ffffff;">
                <li>✅ Archivo SQLite cargado correctamente</li>
                <li>📊 Se analizarán todas las tablas con columnas ValueX/ValueY</li>
                <li>⚡ Optimización automática para datasets grandes</li>
                <li>💾 La sesión se guardará automáticamente</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Center the analyze button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Session name input
            suggested_name = st.session_state.session_manager.generate_session_name_suggestion(
                st.session_state.uploaded_file.name
            )
            
            session_name = st.text_input(
                "📝 Nombre de la sesión (opcional)",
                value=suggested_name,
                help="Deja el nombre sugerido o personalízalo como prefieras",
                key="session_name_input"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("🔍 Analizar Base de Datos", type="primary", use_container_width=True):
                st.session_state.processing_status = "processing"
                # Store the custom session name
                st.session_state.custom_session_name = session_name if session_name.strip() else None
                success = process_database(st.session_state.uploaded_file)
                if success:
                    st.session_state.processing_status = "completed"
                    st.session_state.view_mode = "view_session"
                    st.rerun()
                else:
                    st.session_state.processing_status = "ready"

def render_session_view():
    """Render current session view with optimized chart display"""
    if not st.session_state.charts_generated:
        st.warning("📊 No hay gráficos en la sesión actual. Inicia un nuevo análisis.")
        return
    
    st.markdown("### 📊 Sesión Actual")
    
    # Session info
    if st.session_state.current_session_id:
        st.markdown(f"""
        <div class="success-message">
            💾 <strong>Sesión guardada:</strong> ID {st.session_state.current_session_id[:8]}...
        </div>
        """, unsafe_allow_html=True)
    
    # Chart statistics
    st.session_state.chart_viewer.render_chart_statistics(st.session_state.charts_generated)
    
    st.markdown("---")
    
    # Optimized chart viewer
    st.session_state.chart_viewer.render_charts_overview(st.session_state.charts_generated)
    
    # Report generation
    st.markdown("---")
    render_report_generation()

def render_session_list():
    """Render list of saved sessions"""
    st.markdown("### 📚 Historial de Sesiones")
    
    sessions = st.session_state.session_manager.get_sessions()
    
    if not sessions:
        st.info("📝 No hay sesiones guardadas aún. Realiza tu primer análisis para comenzar.")
        return
    
    # Search and filter sessions
    col1, col2 = st.columns([2, 1])
    with col1:
        search_term = st.text_input("🔍 Buscar sesiones", placeholder="Nombre de archivo, fecha...")
    with col2:
        sort_by = st.selectbox("🔄 Ordenar por", ["Fecha (reciente)", "Fecha (antigua)", "Nombre", "Gráficos"])
    
    # Filter sessions
    filtered_sessions = sessions
    if search_term:
        filtered_sessions = [
            s for s in sessions 
            if search_term.lower() in s['session_name'].lower() or 
               search_term.lower() in s['original_filename'].lower()
        ]
    
    # Sort sessions
    if sort_by == "Fecha (reciente)":
        filtered_sessions.sort(key=lambda x: x['created_at'], reverse=True)
    elif sort_by == "Fecha (antigua)":
        filtered_sessions.sort(key=lambda x: x['created_at'])
    elif sort_by == "Nombre":
        filtered_sessions.sort(key=lambda x: x['session_name'])
    elif sort_by == "Gráficos":
        filtered_sessions.sort(key=lambda x: x['charts_count'], reverse=True)
    
    st.markdown(f"**Mostrando {len(filtered_sessions)} de {len(sessions)} sesiones**")
    
    # Display sessions
    for session in filtered_sessions:
        with st.expander(f"📊 {session['session_name']}", expanded=False):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📁 Archivo", session['original_filename'])
            with col2:
                st.metric("📊 Gráficos", session['charts_count'])
            with col3:
                st.metric("📈 Puntos", f"{session['total_data_points']:,}")
            with col4:
                file_size_mb = session['file_size'] / 1024 / 1024 if session['file_size'] else 0
                st.metric("📏 Tamaño", f"{file_size_mb:.1f} MB")
            
            # Chart types
            if session['chart_types']:
                st.markdown("**Tipos de gráficos:**")
                for chart_type, count in session['chart_types'].items():
                    st.markdown(f"- {chart_type.replace('_', ' ').title()}: {count}")
            
            # Actions
            action_col1, action_col2, action_col3 = st.columns(3)
            with action_col1:
                if st.button(f"👁️ Ver Sesión", key=f"view_{session['id']}"):
                    # Load session
                    session_data = st.session_state.session_manager.load_session(session['id'])
                    if session_data:
                        st.session_state.charts_generated = session_data['charts_generated']
                        st.session_state.current_session_id = session['id']
                        st.session_state.view_mode = "view_session"
                        st.rerun()
            
            with action_col2:
                if st.button(f"📄 Generar Reporte", key=f"report_{session['id']}"):
                    # Load session and generate report
                    session_data = st.session_state.session_manager.load_session(session['id'])
                    if session_data:
                        report_generator = ReportGenerator()
                        report_name = f"reporte_{session['id'][:8]}.html"
                        success = report_generator.generate_html_report(
                            session_data['charts_generated'],
                            session_data['filename'],
                            report_name,
                            "#ffffff",  # Default white background
                            False       # Use interactive charts for PDF compatibility
                        )
                        if success:
                            with open(report_name, 'rb') as file:
                                st.download_button(
                                    label="⬇️ Descargar",
                                    data=file.read(),
                                    file_name=report_name,
                                    mime="text/html",
                                    key=f"download_{session['id']}"
                                )
            
            with action_col3:
                if st.button(f"🗑️ Eliminar", key=f"delete_{session['id']}", type="secondary"):
                    if st.session_state.session_manager.delete_session(session['id']):
                        st.success("Sesión eliminada")
                        st.rerun()

def render_report_generation():
    """Render report generation section optimized for PDF printing"""
    if not st.session_state.charts_generated:
        return False
    
    st.markdown("""
    <div class="step-indicator">
        <span class="step-number">3</span>
        <strong>Generar Reporte HTML Optimizado para PDF</strong>
    </div>
    """, unsafe_allow_html=True)
    
    # Report options in a professional container
    st.markdown("""
    <div class="report-options">
        <h4>📄 Configuración del Reporte PDF</h4>
        <p style="margin: 0.5rem 0; color: #bdc3c7; font-size: 0.9rem;">
            Genera un reporte HTML optimizado para convertir a PDF con un gráfico por página
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        report_name = st.text_input(
            "📝 Nombre del reporte",
            value="reporte_espectros_armonicos.html",
            help="El archivo HTML se optimizará automáticamente para impresión PDF"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        total_charts = len(st.session_state.charts_generated)
        st.metric("📊 Gráficos", f"{total_charts}")
    
    # Background color selection
    st.markdown("""
    <div class="color-picker-container">
        <h5 style="margin-bottom: 0.5rem;">🎨 Esquema de Color para Impresión</h5>
        <p style="font-size: 0.9rem; color: #bdc3c7; margin-bottom: 1rem;">
            Selecciona el esquema de color. Los textos y gráficos se ajustarán automáticamente para óptima legibilidad.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Professional color presets for printing
    col1, col2, col3, col4 = st.columns(4)
    
    color_presets = {
        "Blanco Clásico": "#ffffff",
        "Gris Suave": "#f8f9fa", 
        "Azul Ejecutivo": "#2c3e50",
        "Negro Elegante": "#1a1a1a"
    }
    
    selected_preset = None
    with col1:
        if st.button("⚪ Blanco Clásico", use_container_width=True, help="Ideal para impresión estándar"):
            selected_preset = "#ffffff"
    with col2:
        if st.button("🔘 Gris Suave", use_container_width=True, help="Reduce el contraste, ahorra tinta"):
            selected_preset = "#f8f9fa"
    with col3:
        if st.button("🔵 Azul Ejecutivo", use_container_width=True, help="Presentaciones profesionales"):
            selected_preset = "#2c3e50"
    with col4:
        if st.button("⚫ Negro Elegante", use_container_width=True, help="Máximo contraste"):
            selected_preset = "#1a1a1a"
    
    # Color picker
    if 'selected_bg_color' not in st.session_state:
        st.session_state.selected_bg_color = "#ffffff"
    
    if selected_preset:
        st.session_state.selected_bg_color = selected_preset
    
    background_color = st.color_picker(
        "🎨 Color personalizado",
        value=st.session_state.selected_bg_color,
        help="O selecciona un color personalizado"
    )
    
    st.session_state.selected_bg_color = background_color
    
    # Color preview and contrast info
    is_dark = _is_dark_background(background_color)
    text_color = "#ecf0f1" if is_dark else "#2c3e50"
    
    st.markdown(f"""
    <div style="background: {background_color}; 
                padding: 1.5rem; 
                border-radius: 8px; 
                border: 2px solid rgba(236, 240, 241, 0.2);
                margin: 1rem 0;
                text-align: center;">
        <span style="color: {text_color}; font-weight: 600; font-size: 1.1rem;">
            📄 Vista previa del reporte impreso
        </span><br>
        <small style="color: {text_color}; opacity: 0.8;">
            Esquema: {"Oscuro" if is_dark else "Claro"} • 
            Texto: {text_color} • 
            {"✅ Óptimo para impresión" if background_color in ["#ffffff", "#f8f9fa"] else "⚠️ Verificar contraste al imprimir"}
        </small>
    </div>
    """, unsafe_allow_html=True)
    
    # PDF printing instructions
    st.markdown("""
    <div class="success-message">
        📋 <strong>Instrucciones para Conversión a PDF:</strong><br>
        <small>
            1. 📁 Descargar el archivo HTML generado<br>
            2. 🌐 Abrir en cualquier navegador web<br>
            3. 🖨️ Presionar Ctrl+P (Cmd+P en Mac)<br>
            4. ⚙️ Seleccionar "Más configuraciones" → "Gráficos en color"<br>
            5. 💾 Elegir "Guardar como PDF" como destino<br>
            6. ✅ Resultado: Un PDF con un gráfico por página
        </small>
    </div>
    """, unsafe_allow_html=True)
    
    # Advanced options (collapsed)
    with st.expander("⚙️ Opciones Avanzadas"):
        st.markdown("**🎯 Optimizaciones aplicadas automáticamente:**")
        st.markdown("""
        - ✅ **Un gráfico por página:** Saltos de página automáticos para PDF
        - ✅ **Colores optimizados:** Ajuste automático de contraste para impresión
        - ✅ **Tamaño fijo:** Gráficos de 450px de altura para consistencia
        - ✅ **Fuentes legibles:** Arial 11pt optimizado para impresión
        - ✅ **Navegación web:** Filtros y búsqueda para visualización en pantalla
        - ✅ **Márgenes PDF:** 0.75 pulgadas en todos los lados
        """)
        
        chart_count = len(st.session_state.charts_generated)
        pages_estimate = chart_count + 1  # Header page + charts (no separate footer page)
        st.info(f"📊 **Estimación:** {pages_estimate} páginas PDF (1 página de información + {chart_count} gráficos)")
    
    # Generate button
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Generar Reporte PDF-Ready", type="primary", use_container_width=True):
            return generate_html_report(report_name, background_color, False)  # Always use interactive charts
    
    return False

def _is_dark_background(background_color: str) -> bool:
    """Helper function to determine if background is dark"""
    hex_color = background_color.lstrip('#')
    if len(hex_color) == 6:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return luminance < 0.5
    return False

def generate_html_report(report_name: str, background_color: str = "#ffffff", use_static_images: bool = False) -> bool:
    """Generate the HTML report optimized for PDF printing"""
    if not st.session_state.charts_generated:
        st.error("❌ No hay gráficos para generar el reporte")
        return False
    
    try:
        # Ensure .html extension
        if not report_name.endswith('.html'):
            report_name += '.html'
        
        # Create report generator
        report_generator = ReportGenerator()
        
        # Progress tracking containers
        total_charts = len(st.session_state.charts_generated)
        
        # Create progress UI
        progress_container = st.container()
        with progress_container:
            st.markdown(f"""
            <div class="success-message">
                📄 <strong>Generando reporte HTML optimizado para PDF</strong><br>
                <small>📊 {total_charts} gráficos • 🎨 Fondo: {background_color} • ⚡ Modo interactivo</small>
            </div>
            """, unsafe_allow_html=True)
            
            # Progress elements
            progress_bar = st.progress(0)
            status_text = st.empty()
            eta_text = st.empty()
        
        # Progress callback function
        def update_progress(completed: int, total: int, status: str, eta_seconds: float):
            progress = completed / total if total > 0 else 0
            progress_bar.progress(progress)
            status_text.markdown(f"**📊 Estado:** {status}")
            
            if eta_seconds > 0 and completed < total:
                eta_text.markdown(f"**⏱️ Progreso:** {progress*100:.0f}% completado")
            else:
                eta_text.markdown("**✅ Completado**")
        
        # Start timing
        import time
        start_time = time.time()
        
        # Generate report with progress tracking
        db_name = st.session_state.uploaded_file.name if st.session_state.uploaded_file else "Base de datos"
        
        success = report_generator.generate_html_report(
            st.session_state.charts_generated,
            db_name,
            report_name,
            background_color,
            use_static_images,  # Always False for PDF optimization
            progress_callback=update_progress
        )
        
        if success:
            st.session_state.report_path = report_name
            elapsed_time = time.time() - start_time
            
            # Clear progress UI and show success
            progress_container.empty()
            
            # Enhanced success message
            st.markdown(f"""
            <div class="success-message">
                ✅ <strong>Reporte HTML generado exitosamente en {elapsed_time:.1f} segundos</strong><br>
                <small>
                    📄 Optimizado para PDF • 
                    🎨 Esquema: {background_color} • 
                    📊 {total_charts} gráficos • 
                    📋 Un gráfico por página
                </small>
            </div>
            """, unsafe_allow_html=True)
            
            # Provide download link and instructions
            with open(report_name, 'rb') as file:
                st.download_button(
                    label="⬇️ Descargar Reporte HTML",
                    data=file.read(),
                    file_name=report_name,
                    mime="text/html",
                    type="primary"
                )
            
            # PDF conversion instructions
            st.markdown("""
            <div style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); 
                        padding: 1.5rem; border-radius: 8px; margin: 1rem 0; color: white;">
                <h5 style="margin: 0 0 1rem 0; color: white;">🖨️ Conversión a PDF:</h5>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                    <div>
                        <strong>1. Abrir archivo</strong><br>
                        <small>Doble clic en el HTML descargado</small>
                    </div>
                    <div>
                        <strong>2. Imprimir</strong><br>
                        <small>Ctrl+P (Cmd+P en Mac)</small>
                    </div>
                    <div>
                        <strong>3. Configurar</strong><br>
                        <small>Destino: "Guardar como PDF"</small>
                    </div>
                    <div>
                        <strong>4. Opciones</strong><br>
                        <small>Activar "Gráficos en color"</small>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            return True
        else:
            progress_container.empty()
            return False
        
    except Exception as e:
        st.error(f"❌ Error generando el reporte: {e}")
        return False

def main():
    """Main application with improved navigation and session management"""
    initialize_session_state()
    render_header()
    render_navigation()
    
    # Main content based on view mode
    if st.session_state.view_mode == "new_analysis":
        render_new_analysis()
    elif st.session_state.view_mode == "view_session":
        render_session_view()
    elif st.session_state.view_mode == "session_list":
        render_session_list()
    
    # Sidebar
    render_sidebar()
    
    # Enhanced Footer
    st.markdown("---")
    st.markdown("""
    <div style="background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); 
                padding: 2rem; border-radius: 8px; text-align: center; color: white; margin-top: 2rem;
                box-shadow: 0 4px 20px rgba(44, 62, 80, 0.25);">
        <h4 style="margin: 0 0 1rem 0; color: #ecf0f1;">🚀 Analizador de Espectros Armónicos v3.0</h4>
        <p style="margin: 0 0 1rem 0; color: #bdc3c7;">
            Desarrollado con ❤️ • Arquitectura Modular • Gestión de Sesiones • Renderizado Optimizado
        </p>
        <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
            <div style="color: white; text-decoration: none;">
                <strong>📱 Streamlit</strong><br>
                <small style="color: #bdc3c7;">Framework de aplicaciones</small>
            </div>
            <div style="color: white; text-decoration: none;">
                <strong>📊 Plotly</strong><br>
                <small style="color: #bdc3c7;">Visualización optimizada</small>
            </div>
            <div style="color: white; text-decoration: none;">
                <strong>💾 SQLite</strong><br>
                <small style="color: #bdc3c7;">Gestión de sesiones</small>
            </div>
        </div>
        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(236,240,241,0.2);">
            <small style="color: #bdc3c7;">© 2024 • Versión 3.0 • Optimizado para PDF y Reportes Profesionales</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 