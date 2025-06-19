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
    
    /* Session card specific styling */
    .session-card-container {
        transition: all 0.3s ease;
    }
    
    .session-card-container:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.5) !important;
    }
    
    .favorite-star {
        filter: drop-shadow(0 0 8px rgba(251, 191, 36, 0.6));
    }
    
    .session-metrics-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.5rem;
        margin: 1rem 0;
    }
    
    .metric-item {
        text-align: center;
        padding: 0.5rem;
        border-radius: 6px;
        transition: all 0.2s ease;
    }
    
    .metric-item:hover {
        transform: scale(1.05);
    }
    
    .session-actions {
        display: flex;
        gap: 0.3rem;
        margin-top: 1rem;
    }
    
    .session-actions button {
        flex: 1;
        border-radius: 6px !important;
        transition: all 0.2s ease !important;
        font-size: 0.9rem !important;
    }
    
    .session-actions button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Enhanced stats bar */
    .stats-bar {
        background: linear-gradient(90deg, #1f2937 0%, #374151 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(75, 85, 99, 0.3);
    }
    
    .stats-item {
        text-align: center;
        padding: 0.5rem;
        transition: transform 0.2s ease;
    }
    
    .stats-item:hover {
        transform: scale(1.1);
    }
    
    .stats-number {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .stats-label {
        font-size: 0.9rem;
        opacity: 0.9;
        font-weight: 500;
    }
    
    /* Empty state styling */
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
        border-radius: 16px;
        margin: 2rem 0;
        border: 2px dashed #4b5563;
    }
    
    .empty-state-icon {
        font-size: 4rem;
        margin-bottom: 1.5rem;
        opacity: 0.6;
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
            <p><strong>Favoritas:</strong> ⭐ {stats['favorites_count']}</p>
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
    """Render list of saved sessions with compact cards and favorites pinned on top"""
    st.markdown("### 📚 Historial de Sesiones")
    
    sessions = st.session_state.session_manager.get_sessions()
    
    if not sessions:
        st.info("📝 No hay sesiones guardadas aún. Realiza tu primer análisis para comenzar.")
        return
    
    # Enhanced search and filter UI
    st.markdown("---")
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        search_term = st.text_input("🔍 Buscar sesiones", placeholder="Nombre de archivo, fecha...", label_visibility="collapsed")
    with col2:
        filter_type = st.selectbox("📁", ["Todas", "⭐ Favoritas", "📄 Regulares"], label_visibility="collapsed")
    with col3:
        sort_by = st.selectbox("🔄", ["⭐ Favoritos primero", "📅 Más recientes", "📅 Más antiguas", "🔤 Nombre A-Z", "📊 + Gráficos"], label_visibility="collapsed")
    
    # Filter sessions based on selection
    if filter_type == "⭐ Favoritas":
        filtered_sessions = [s for s in sessions if s['is_favorite']]
    elif filter_type == "📄 Regulares":
        filtered_sessions = [s for s in sessions if not s['is_favorite']]
    else:
        filtered_sessions = sessions
    
    # Apply search filter
    if search_term:
        filtered_sessions = [
            s for s in filtered_sessions 
            if search_term.lower() in s['session_name'].lower() or 
               search_term.lower() in s['original_filename'].lower()
        ]
    
    # Sort sessions
    if sort_by == "⭐ Favoritos primero":
        filtered_sessions.sort(key=lambda x: (not x['is_favorite'], x['created_at']), reverse=True)
    elif sort_by == "📅 Más recientes":
        filtered_sessions.sort(key=lambda x: x['created_at'], reverse=True)
    elif sort_by == "📅 Más antiguas":
        filtered_sessions.sort(key=lambda x: x['created_at'])
    elif sort_by == "🔤 Nombre A-Z":
        filtered_sessions.sort(key=lambda x: x['session_name'])
    elif sort_by == "📊 + Gráficos":
        filtered_sessions.sort(key=lambda x: x['charts_count'], reverse=True)
    
    # Separate favorites and regular sessions for better display
    favorite_sessions = [s for s in filtered_sessions if s['is_favorite']]
    regular_sessions = [s for s in filtered_sessions if not s['is_favorite']]
    
    # Display session statistics with modern design
    stats = st.session_state.session_manager.get_session_stats()
    
    # Enhanced stats bar with new CSS classes
    stats_html = f"""
    <div class="stats-bar" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div class="stats-item" style="min-width: 120px;">
            <div class="stats-number" style="color: #60a5fa;">{stats['total_sessions']}</div>
            <div class="stats-label" style="color: #d1d5db;">Total Sesiones</div>
        </div>
        <div class="stats-item" style="min-width: 120px;">
            <div class="stats-number favorite-star" style="color: #fbbf24;">{stats['favorites_count']}</div>
            <div class="stats-label" style="color: #d1d5db;">⭐ Favoritas</div>
        </div>
        <div class="stats-item" style="min-width: 120px;">
            <div class="stats-number" style="color: #34d399;">{stats['total_charts']:,}</div>
            <div class="stats-label" style="color: #d1d5db;">📊 Gráficos</div>
        </div>
        <div class="stats-item" style="min-width: 120px;">
            <div class="stats-number" style="color: #f472b6;">{stats['avg_charts_per_session']}</div>
            <div class="stats-label" style="color: #d1d5db;">📈 Promedio</div>
        </div>
    </div>
    """
    st.markdown(stats_html, unsafe_allow_html=True)
    
    # Results counter
    if search_term or filter_type != "Todas":
        st.markdown(f"**📋 Mostrando {len(filtered_sessions)} de {len(sessions)} sesiones**")
    
    # Display Favorites Section (Pinned on Top)
    if favorite_sessions:
        st.markdown("### ⭐ Sesiones Favoritas")
        render_session_cards(favorite_sessions, is_favorites_section=True)
        st.markdown("---")
    
    # Display Regular Sessions
    if regular_sessions:
        if favorite_sessions:  # Only show header if there are favorites above
            st.markdown("### 📄 Otras Sesiones")
        render_session_cards(regular_sessions, is_favorites_section=False)
    
    # Empty state for filtered results
    if not filtered_sessions:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">🔍</div>
            <h3 style="color: #9ca3af; margin-bottom: 0.5rem;">No se encontraron sesiones</h3>
            <p style="color: #6b7280;">Intenta ajustar los filtros o términos de búsqueda</p>
        </div>
        """, unsafe_allow_html=True)

def render_session_cards(sessions, is_favorites_section=False):
    """Render compact session cards in a grid layout"""
    
    # Display sessions in rows of 2 cards
    for i in range(0, len(sessions), 2):
        cols = st.columns(2, gap="medium")
        
        for j, col in enumerate(cols):
            session_idx = i + j
            if session_idx < len(sessions):
                session = sessions[session_idx]
                
                with col:
                    render_single_session_card(session, is_favorites_section)

def render_single_session_card(session, is_favorites_section):
    """Render a single compact session card using Streamlit components"""
    
    # Card styling based on favorite status
    if session['is_favorite']:
        card_style = "background: linear-gradient(135deg, #1f2937 0%, #374151 100%); border-left: 4px solid #fbbf24; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);"
        favorite_icon = "⭐"
        star_color = "#fbbf24"
    else:
        card_style = "background: linear-gradient(135deg, #1f2937 0%, #374151 100%); border-left: 4px solid #374151; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);"
        favorite_icon = "☆"
        star_color = "#6b7280"
    
    # Calculate file size in MB
    file_size_mb = session['file_size'] / 1024 / 1024 if session['file_size'] else 0
    
    # Format creation date
    try:
        from datetime import datetime
        created_date = datetime.fromisoformat(session['created_at'].replace(' Chile/Continental', ''))
        formatted_date = created_date.strftime("%d/%m/%Y %H:%M")
    except:
        formatted_date = session['created_at'][:16]  # Fallback
    
    # Chart types summary
    chart_types_summary = ""
    if session['chart_types']:
        types_list = []
        for chart_type, count in list(session['chart_types'].items())[:3]:  # Show max 3 types
            type_display = chart_type.replace('_', ' ').title()
            types_list.append(f"{type_display}: {count}")
        chart_types_summary = " • ".join(types_list)
        if len(session['chart_types']) > 3:
            chart_types_summary += "..."
    
    # Create the card container
    with st.container():
        st.markdown(f'<div style="{card_style}">', unsafe_allow_html=True)
        
        # Header with name and favorite star
        col_name, col_star = st.columns([8, 1])
        with col_name:
            st.markdown(f"<h4 style='margin: 0; color: #f9fafb; font-size: 1.1rem; font-weight: 600;'>{session['session_name']}</h4>", unsafe_allow_html=True)
        with col_star:
            st.markdown(f"<div style='color: {star_color}; font-size: 1.3rem; text-align: center;'>{favorite_icon}</div>", unsafe_allow_html=True)
        
        # File info
        st.markdown(f"<div style='color: #9ca3af; font-size: 0.9rem; margin: 0.5rem 0;'>📁 {session['original_filename'][:30]}{'...' if len(session['original_filename']) > 30 else ''}</div>", unsafe_allow_html=True)
        
        # Metrics row using Streamlit columns
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div style="text-align: center; background: rgba(96, 165, 250, 0.1); padding: 0.5rem; border-radius: 6px;">
                <div style="font-size: 1.3rem; font-weight: bold; color: #60a5fa;">{session['charts_count']}</div>
                <div style="font-size: 0.7rem; color: #9ca3af;">Gráficos</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="text-align: center; background: rgba(52, 211, 153, 0.1); padding: 0.5rem; border-radius: 6px;">
                <div style="font-size: 1.3rem; font-weight: bold; color: #34d399;">{session['total_data_points']:,}</div>
                <div style="font-size: 0.7rem; color: #9ca3af;">Puntos</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="text-align: center; background: rgba(168, 85, 247, 0.1); padding: 0.5rem; border-radius: 6px;">
                <div style="font-size: 1.3rem; font-weight: bold; color: #a855f7;">{file_size_mb:.1f}</div>
                <div style="font-size: 0.7rem; color: #9ca3af;">MB</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Chart types
        st.markdown(f"""
        <div style="color: #d1d5db; font-size: 0.8rem; margin: 0.5rem 0; 
                    background: rgba(107, 114, 128, 0.1); padding: 0.5rem; border-radius: 6px;">
            📊 {chart_types_summary if chart_types_summary else 'Sin tipos específicos'}
        </div>
        """, unsafe_allow_html=True)
        
        # Date
        st.markdown(f"<div style='color: #6b7280; font-size: 0.75rem; margin-bottom: 0.5rem;'>🕐 {formatted_date}</div>", unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Action buttons below the card
    render_session_actions(session)

def render_session_actions(session):
    """Render action buttons for a session in a compact layout"""
    
    # Action buttons in a compact row
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    
    with col1:
        if st.button("👁️", key=f"view_{session['id']}", help="Ver Sesión", use_container_width=True):
            session_data = st.session_state.session_manager.load_session(session['id'])
            if session_data:
                st.session_state.charts_generated = session_data['charts_generated']
                st.session_state.current_session_id = session['id']
                st.session_state.view_mode = "view_session"
                st.rerun()
    
    with col2:
        star_icon = "☆" if session['is_favorite'] else "⭐"
        star_help = "Quitar de favoritas" if session['is_favorite'] else "Marcar como favorita"
        if st.button(star_icon, key=f"fav_{session['id']}", help=star_help, use_container_width=True):
            if st.session_state.session_manager.toggle_favorite(session['id']):
                st.success("✅ Favorito actualizado")
                st.rerun()
    
    with col3:
        if st.button("✏️", key=f"edit_{session['id']}", help="Editar nombre", use_container_width=True):
            st.session_state[f"edit_mode_{session['id']}"] = True
            st.rerun()
    
    with col4:
        if st.button("📋", key=f"duplicate_{session['id']}", help="Duplicar", use_container_width=True):
            session_data = st.session_state.session_manager.load_session(session['id'])
            if session_data:
                duplicate_name = f"{session['session_name']} - Copia"
                new_id = st.session_state.session_manager.save_session(session_data, duplicate_name)
                if new_id:
                    st.success("✅ Sesión duplicada")
                    st.rerun()
    
    with col5:
        if st.button("🗑️", key=f"delete_{session['id']}", help="Eliminar", use_container_width=True, type="secondary"):
            # Simple confirmation using session state
            confirm_key = f"confirm_delete_{session['id']}"
            if st.session_state.get(confirm_key, False):
                if st.session_state.session_manager.delete_session(session['id']):
                    st.success("✅ Sesión eliminada")
                    if confirm_key in st.session_state:
                        del st.session_state[confirm_key]
                    st.rerun()
            else:
                st.session_state[confirm_key] = True
                st.warning("⚠️ Clic nuevamente para confirmar eliminación")
                st.rerun()
    
    # Name editing modal
    if st.session_state.get(f"edit_mode_{session['id']}", False):
        with st.form(key=f"edit_form_{session['id']}"):
            st.markdown("##### ✏️ Editar nombre de sesión")
            new_name = st.text_input(
                "Nuevo nombre:", 
                value=session['session_name'],
                key=f"new_name_{session['id']}"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Guardar", type="primary", use_container_width=True):
                    if new_name.strip() and new_name != session['session_name']:
                        if st.session_state.session_manager.update_session_name(session['id'], new_name.strip()):
                            st.success("✅ Nombre actualizado")
                            st.session_state[f"edit_mode_{session['id']}"] = False
                            st.rerun()
            with col2:
                if st.form_submit_button("❌ Cancelar", use_container_width=True):
                    st.session_state[f"edit_mode_{session['id']}"] = False
                    st.rerun()
    
    # Add spacing between sessions
    st.markdown("<br>", unsafe_allow_html=True)

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
    
    # Main container with modern design
    st.markdown("""
    <div class="report-options">
        <h4 style="margin-bottom: 1.5rem;">📄 Configuración del Reporte PDF</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Report name and basic info
    col1, col2 = st.columns([3, 1])
    
    with col1:
        report_name = st.text_input(
            "📝 Nombre del reporte",
            value="reporte_espectros_armonicos.html",
            help="El archivo HTML se optimizará automáticamente para impresión PDF"
        )
    
    with col2:
        total_charts = len(st.session_state.charts_generated)
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); 
                    color: white; padding: 1rem; border-radius: 8px; text-align: center; margin-top: 1.8rem;">
            <div style="font-size: 1.5rem; font-weight: bold;">{total_charts}</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">📊 Gráficos</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Color theme selection with beautiful presets
    st.markdown("""
    <div style="margin: 2rem 0 1rem 0;">
        <h5 style="color: #ecf0f1; margin-bottom: 1rem;">🎨 Seleccionar Tema de Color</h5>
        <p style="font-size: 0.9rem; color: #bdc3c7; margin-bottom: 1.5rem;">
            Elige el esquema de color perfecto para tu reporte profesional
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Professional color presets with enhanced design
    color_presets = [
        {
            "name": "📄 Clásico Blanco",
            "bg": "#ffffff",
            "text": "#2c3e50",
            "accent": "#3498db",
            "description": "Ideal para impresión estándar y presentaciones formales",
            "icon": "📄"
        },
        {
            "name": "🌙 Ejecutivo Azul",
            "bg": "#2c3e50", 
            "text": "#ecf0f1",
            "accent": "#3498db",
            "description": "Elegante y profesional, perfecto para presentaciones corporativas",
            "icon": "🌙"
        },
        {
            "name": "🌟 Moderno Gris",
            "bg": "#34495e",
            "text": "#ecf0f1", 
            "accent": "#f39c12",
            "description": "Equilibrio perfecto entre elegancia y modernidad",
            "icon": "🌟"
        }
    ]
    
    # Initialize selected theme
    if 'selected_theme' not in st.session_state:
        st.session_state.selected_theme = 0
    
    # Theme selection with beautiful cards
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    
    for i, preset in enumerate(color_presets):
        with cols[i]:
            is_selected = st.session_state.selected_theme == i
            border_style = "border: 3px solid #3498db;" if is_selected else "border: 2px solid rgba(255,255,255,0.1);"
            
            if st.button(
                f"{preset['icon']} {preset['name']}", 
                key=f"theme_{i}",
                use_container_width=True,
                type="primary" if is_selected else "secondary"
            ):
                st.session_state.selected_theme = i
                st.rerun()
            
            # Theme preview card
            st.markdown(f"""
            <div style="background: {preset['bg']}; {border_style}
                        padding: 1.5rem; border-radius: 8px; margin: 0.5rem 0;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.15); transition: all 0.3s ease;">
                <div style="color: {preset['text']}; font-weight: 600; margin-bottom: 0.5rem;">
                    Vista Previa
                </div>
                <div style="color: {preset['accent']}; font-size: 0.9rem; margin-bottom: 0.5rem;">
                    ■ Gráfico de Espectro
                </div>
                <div style="color: {preset['text']}; font-size: 0.8rem; opacity: 0.8;">
                    {preset['description']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Selected theme details
    selected_preset = color_presets[st.session_state.selected_theme]
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Chart preview with actual data
    st.markdown("""
    <div style="margin: 2rem 0 1rem 0;">
        <h5 style="color: #ecf0f1; margin-bottom: 1rem;">👁️ Vista Previa del Reporte</h5>
        <p style="font-size: 0.9rem; color: #bdc3c7; margin-bottom: 1rem;">
            Así se verá tu reporte con el tema seleccionado
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create a preview chart with the selected theme
    if st.session_state.charts_generated:
        preview_chart = st.session_state.charts_generated[0]['figure']
        preview_chart_copy = preview_chart
        
        # Apply the selected theme to the preview
        preview_chart_copy.update_layout(
            plot_bgcolor=selected_preset['bg'],
            paper_bgcolor=selected_preset['bg'],
            font=dict(color=selected_preset['text'], size=11, family='Arial'),
            title=dict(
                text=f"{selected_preset['icon']} Vista Previa - {st.session_state.charts_generated[0]['table_name']}",
                font=dict(color=selected_preset['text'], size=14),
                x=0.5
            ),
            xaxis=dict(
                color=selected_preset['text'],
                gridcolor=f"rgba(100,100,100,0.2)" if selected_preset['bg'] != "#ffffff" else "rgba(200,200,200,0.3)",
                linecolor=selected_preset['text'],
                tickformat='d'
            ),
            yaxis=dict(
                color=selected_preset['text'],
                gridcolor=f"rgba(100,100,100,0.2)" if selected_preset['bg'] != "#ffffff" else "rgba(200,200,200,0.3)",
                linecolor=selected_preset['text'],
                tickformat='g'
            ),
            height=350,
            margin=dict(l=50, r=30, t=60, b=40)
        )
        
        # Update trace colors to match theme
        for trace in preview_chart_copy.data:
            if hasattr(trace, 'line') and trace.line:
                trace.line.color = selected_preset['accent']
            if hasattr(trace, 'marker') and trace.marker and hasattr(trace.marker, 'color'):
                if isinstance(trace.marker.color, str):
                    trace.marker.color = selected_preset['accent']
        
        # Display the preview in a themed container
        st.markdown(f"""
        <div style="background: {selected_preset['bg']}; 
                    padding: 1.5rem; border-radius: 12px; 
                    border: 2px solid {selected_preset['accent']};
                    box-shadow: 0 8px 25px rgba(0,0,0,0.15); margin: 1rem 0;">
        """, unsafe_allow_html=True)
        
        st.plotly_chart(preview_chart_copy, use_container_width=True, key="preview_chart")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Theme summary
        st.markdown(f"""
        <div style="background: rgba(52, 152, 219, 0.1); 
                    padding: 1rem; border-radius: 8px; margin: 1rem 0;
                    border-left: 4px solid {selected_preset['accent']};">
            <strong style="color: {selected_preset['accent']};">
                {selected_preset['name']} Seleccionado
            </strong><br>
            <small style="color: #bdc3c7;">
                {selected_preset['description']}
            </small>
        </div>
        """, unsafe_allow_html=True)
    
    # PDF printing instructions
    st.markdown("""
    <div style="background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%); 
                padding: 1.5rem; border-radius: 12px; margin: 2rem 0; color: white;">
        <h5 style="margin: 0 0 1rem 0; color: white;">📋 Conversión a PDF Profesional</h5>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
            <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px;">
                <strong>1. 📁 Descargar</strong><br>
                <small>Archivo HTML optimizado</small>
            </div>
            <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px;">
                <strong>2. 🌐 Abrir</strong><br>
                <small>En cualquier navegador</small>
            </div>
            <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px;">
                <strong>3. 🖨️ Imprimir</strong><br>
                <small>Ctrl+P → Guardar como PDF</small>
            </div>
            <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px;">
                <strong>4. ⚙️ Configurar</strong><br>
                <small>Activar "Gráficos en color"</small>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Advanced options (collapsed)
    with st.expander("⚙️ Opciones Avanzadas y Detalles Técnicos"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🎯 Optimizaciones Aplicadas:**")
            st.markdown("""
            - ✅ Un gráfico por página para PDF
            - ✅ Fuentes Arial optimizadas 
            - ✅ Márgenes profesionales (0.75")
            - ✅ Colores ajustados automáticamente
            - ✅ Navegación web interactiva
            """)
        
        with col2:
            chart_count = len(st.session_state.charts_generated)
            pages_estimate = chart_count + 1
            st.markdown("**📊 Estadísticas del Reporte:**")
            st.markdown(f"""
            - 📄 **Páginas estimadas:** {pages_estimate}
            - 📊 **Gráficos incluidos:** {chart_count}
            - 🎨 **Tema:** {selected_preset['name']}
            - 📐 **Formato:** A4 Portrait
            - 🔧 **Tipo:** HTML interactivo → PDF
            """)
    
    # Generate button with enhanced design
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "🚀 Generar Reporte Profesional", 
            type="primary", 
            use_container_width=True,
            help="Genera un reporte HTML optimizado para conversión a PDF"
        ):
            return generate_html_report(report_name, selected_preset['bg'], False)
    
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
        
        # Create progress UI with modern design
        progress_container = st.container()
        with progress_container:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); 
                        padding: 2rem; border-radius: 12px; margin: 1rem 0; color: white; text-align: center;">
                <h4 style="margin: 0 0 1rem 0; color: white;">🚀 Generando Reporte Profesional</h4>
                <div style="display: flex; justify-content: center; align-items: center; gap: 2rem; flex-wrap;">
                    <div>
                        <div style="font-size: 1.5rem; font-weight: bold;">{total_charts}</div>
                        <div style="font-size: 0.9rem; opacity: 0.9;">📊 Gráficos</div>
                    </div>
                    <div>
                        <div style="font-size: 1.5rem; font-weight: bold;">{background_color}</div>
                        <div style="font-size: 0.9rem; opacity: 0.9;">🎨 Tema</div>
                    </div>
                    <div>
                        <div style="font-size: 1.5rem; font-weight: bold;">PDF</div>
                        <div style="font-size: 0.9rem; opacity: 0.9;">📄 Formato</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Progress elements with modern styling
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
            use_static_images,
            progress_callback=update_progress
        )
        
        if success:
            st.session_state.report_path = report_name
            elapsed_time = time.time() - start_time
            
            # Clear progress UI and show success with enhanced design
            progress_container.empty()
            
            # Success message with beautiful design
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%); 
                        padding: 2rem; border-radius: 12px; margin: 2rem 0; color: white; text-align: center;
                        box-shadow: 0 8px 25px rgba(39, 174, 96, 0.3);">
                <h3 style="margin: 0 0 1rem 0; color: white;">
                    ✅ ¡Reporte Generado Exitosamente!
                </h3>
                <div style="display: flex; justify-content: center; align-items: center; gap: 2rem; flex-wrap; margin-bottom: 1.5rem;">
                    <div style="background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 8px;">
                        <div style="font-size: 1.3rem; font-weight: bold;">{elapsed_time:.1f}s</div>
                        <div style="font-size: 0.9rem;">⚡ Tiempo</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 8px;">
                        <div style="font-size: 1.3rem; font-weight: bold;">{total_charts}</div>
                        <div style="font-size: 0.9rem;">📊 Gráficos</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 8px;">
                        <div style="font-size: 1.3rem; font-weight: bold;">PDF</div>
                        <div style="font-size: 0.9rem;">📄 Listo</div>
                    </div>
                </div>
                <p style="margin: 0; font-size: 1.1rem; opacity: 0.9;">
                    Tu reporte está optimizado para conversión a PDF profesional
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Enhanced download and open options
            st.markdown("""
            <div style="margin: 2rem 0 1rem 0;">
                <h5 style="color: #ecf0f1; margin-bottom: 1rem;">📁 Descargar Reporte</h5>
            </div>
            """, unsafe_allow_html=True)
            
            # Download button with enhanced styling
            with open(report_name, 'rb') as file:
                st.download_button(
                    label="⬇️ Descargar Reporte HTML",
                    data=file.read(),
                    file_name=report_name,
                    mime="text/html",
                    type="primary",
                    use_container_width=True,
                    help="Descarga el archivo HTML para convertir a PDF localmente"
                )
            
            # Quick actions section
            st.markdown("""
            <div style="margin: 2rem 0 1rem 0;">
                <h5 style="color: #ecf0f1; margin-bottom: 1rem;">⚡ Acciones Rápidas</h5>
            </div>
            """, unsafe_allow_html=True)
            
            quick_col1, quick_col2, quick_col3 = st.columns(3)
            
            with quick_col1:
                if st.button("🔄 Generar Otro Tema", use_container_width=True):
                    # Reset to allow generating with different theme
                    st.rerun()
            
            with quick_col2:
                if st.button("📊 Ver Gráficos", use_container_width=True):
                    st.session_state.view_mode = "view_session"
                    st.rerun()
            
            with quick_col3:
                if st.button("🆕 Nuevo Análisis", use_container_width=True):
                    st.session_state.view_mode = "new_analysis"
                    st.rerun()
            
            # PDF conversion instructions with modern design
            st.markdown("""
            <div style="background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%); 
                        padding: 2rem; border-radius: 12px; margin: 2rem 0; color: white;">
                <h5 style="margin: 0 0 1.5rem 0; color: white; text-align: center;">
                    🖨️ Guía Rápida: HTML → PDF Profesional
                </h5>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem;">
                    <div style="background: rgba(255,255,255,0.15); padding: 1.2rem; border-radius: 8px; text-align: center;">
                        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📁</div>
                        <strong>1. Descargar</strong><br>
                        <small>Usar botón arriba</small>
                    </div>
                    <div style="background: rgba(255,255,255,0.15); padding: 1.2rem; border-radius: 8px; text-align: center;">
                        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🌐</div>
                        <strong>2. Abrir HTML</strong><br>
                        <small>Doble clic archivo</small>
                    </div>
                    <div style="background: rgba(255,255,255,0.15); padding: 1.2rem; border-radius: 8px; text-align: center;">
                        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🖨️</div>
                        <strong>3. Imprimir</strong><br>
                        <small>Ctrl+P en navegador</small>
                    </div>
                    <div style="background: rgba(255,255,255,0.15); padding: 1.2rem; border-radius: 8px; text-align: center;">
                        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">⚙️</div>
                        <strong>4. Configurar</strong><br>
                        <small>"Más configuraciones"</small>
                    </div>
                    <div style="background: rgba(255,255,255,0.15); padding: 1.2rem; border-radius: 8px; text-align: center;">
                        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🎨</div>
                        <strong>5. Activar Colores</strong><br>
                        <small>"Gráficos en color" ✅</small>
                    </div>
                    <div style="background: rgba(255,255,255,0.15); padding: 1.2rem; border-radius: 8px; text-align: center;">
                        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">✅</div>
                        <strong>6. Guardar PDF</strong><br>
                        <small>Destino: PDF</small>
                    </div>
                </div>
                <div style="text-align: center; margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.2);">
                    <strong>📋 Resultado:</strong> Un PDF profesional con {total_charts + 1} páginas 
                    (portada + 1 gráfico por página)
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Important note about browser settings for background colors
            st.markdown("""
            <div style="background: rgba(231, 76, 60, 0.15); 
                        padding: 1.5rem; border-radius: 8px; margin: 1rem 0;
                        border-left: 4px solid #e74c3c;">
                <h6 style="color: #e74c3c; margin-bottom: 0.5rem;">
                    ⚠️ IMPORTANTE: Para que se impriman los colores de fondo
                </h6>
                <div style="color: #ecf0f1; font-size: 0.9rem;">
                    <strong>En el paso 5, DEBE activar "Gráficos en color" o "Background graphics":</strong><br><br>
                    
                    <strong>🌐 Chrome/Edge:</strong> Más configuraciones → Activar "Gráficos en color"<br>
                    <strong>🦊 Firefox:</strong> Más configuraciones → Activar "Imprimir fondos"<br>
                    <strong>🍎 Safari:</strong> Mostrar detalles → Activar "Imprimir fondos"<br><br>
                    
                    <small style="opacity: 0.8;">
                        Sin esta configuración, el PDF se verá con fondo blanco en lugar del tema seleccionado.
                    </small>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            return True
        else:
            progress_container.empty()
            st.error("❌ Error generando el reporte. Por favor intenta nuevamente.")
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
            <small style="color: #bdc3c7;">© 2025 • Versión 3.2 • Optimizado para PDF y Reportes Profesionales</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 