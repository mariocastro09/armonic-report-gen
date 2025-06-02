# 🚀 Enhanced Harmonic Spectrum Analyzer v3.0

A powerful, modern web application for analyzing harmonic spectra and waveforms from SQLite databases. Built with Streamlit, featuring a complete dark theme, session management, and optimized rendering for large datasets.

## ✨ What's New in v3.0

### 🎨 Complete Dark Theme

- **No more white backgrounds!** Fully dark UI with gradient backgrounds
- Modern glassmorphism design with backdrop blur effects
- Enhanced visual hierarchy and improved readability
- Dark-themed charts and reports

### 💾 Session Management

- **Automatic session saving** - never lose your analysis work
- **Session history** - view and reload previous analyses
- **SQLite-based storage** - persistent data management
- **Easy navigation** between current and historical sessions

### ⚡ Performance Optimizations

- **Smart data sampling** for large datasets (5000+ points)
- **Pagination system** for handling 300+ charts efficiently
- **Optimized rendering** with reduced chart heights in grid view
- **Memory management** with automatic cleanup

### 🔍 Advanced Search & Filtering

- **Real-time search** by table name
- **Filter by chart type** (Waveform, Spectrum Hz, Spectrum Order, Generic)
- **Sort options** (Name, Type, Data points)
- **Interactive pagination** with page navigation

### 📊 Enhanced Chart Viewer

- **Grid layout** with 2-column responsive design
- **Chart statistics** with detailed metrics
- **Type-specific emojis** for easy identification
- **Expandable details** for each chart

### 📄 Professional Reports

- **Dark-themed HTML reports** with modern styling
- **Interactive search and filtering** in reports
- **Pagination** for large report navigation
- **Responsive design** for all devices

## 🎯 Key Features

- **📁 Multi-format Support**: `.db`, `.sqlite`, `.sqlite3`, `.HA1S`, `.hfpdb`
- **📊 Chart Types**: Waveforms, Frequency Spectra, Harmonic Analysis, Generic Data
- **🔄 Real-time Processing**: Live progress tracking with detailed status
- **💾 Session Persistence**: Automatic saving and loading of analysis sessions
- **🔍 Smart Navigation**: Search, filter, and paginate through large datasets
- **📱 Responsive Design**: Works on desktop, tablet, and mobile devices
- **⚡ High Performance**: Optimized for datasets with millions of data points

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd harmonic-spectrum-analyzer

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Demo

```bash
# Create demo database and start the application
python demo.py
```

This will:

- ✅ Check all dependencies
- 🔧 Create a demo database with sample data
- 🚀 Launch the Streamlit application
- 🌐 Open your browser to `http://localhost:8501`

### 3. Manual Start

```bash
# Start the application manually
streamlit run streamlit_app.py
```

## 📋 Requirements

- **Python 3.8+**
- **Streamlit 1.28.0+**
- **Pandas 2.0.0+**
- **Plotly 5.17.0+**
- **NumPy 1.24.0+**

## 🏗️ Architecture

The application follows a modular architecture for maintainability and extensibility:

```
📦 Project Structure
├── 🎯 streamlit_app.py      # Main Streamlit application
├── 🗄️ database_handler.py   # SQLite database operations
├── 🔧 data_processor.py     # Data validation and preparation
├── 📊 chart_generator.py    # Optimized Plotly chart creation
├── 📄 report_generator.py   # HTML report generation
├── 💾 session_manager.py    # Session storage and management
├── 👁️ chart_viewer.py       # Advanced chart viewing with pagination
├── 🚀 demo.py              # Demo script with sample data
├── 📋 requirements.txt     # Python dependencies
└── 📖 README.md           # This file
```

## 🎮 Usage Guide

### 1. **New Analysis**

- 📁 Upload your SQLite database file
- 🔍 Click "Analyze Database" to process
- 📊 View charts with real-time generation
- 💾 Session automatically saved

### 2. **Session Management**

- 📚 View "Session History" to see all saved analyses
- 👁️ Load previous sessions without re-processing
- 🗑️ Delete old sessions to save space
- 📄 Generate reports from any session

### 3. **Chart Navigation**

- 🔍 Use search bar to find specific tables
- 🎯 Filter by chart type for focused analysis
- 📄 Navigate through pages for large datasets
- 📊 View detailed statistics for each chart

### 4. **Report Generation**

- 🚀 Generate professional HTML reports
- ⬇️ Download reports for sharing
- 🔍 Interactive search and filtering in reports
- 📱 Mobile-responsive design

## 🎨 Supported Chart Types

| Type                  | Description             | Visual           | Use Case                       |
| --------------------- | ----------------------- | ---------------- | ------------------------------ |
| **🌊 Waveform**       | Time-series line charts | Continuous lines | Temporal signal analysis       |
| **🔊 Spectrum Hz**    | Frequency bar charts    | Vertical bars    | Frequency domain analysis      |
| **🎵 Spectrum Order** | Harmonic bar charts     | Vertical bars    | Harmonic distortion analysis   |
| **📈 Generic**        | Scatter plots           | Point clouds     | General X-Y data relationships |

## 🔧 Configuration

### Database Requirements

- **Format**: SQLite database files
- **Required Columns**: `ValueX`, `ValueY` (numeric)
- **Optional Columns**: Any additional metadata
- **Table Naming**: Automatic type detection based on table names

### Performance Settings

- **Max Points per Chart**: 5,000 (automatically sampled)
- **Charts per Page**: 8 (configurable in `chart_viewer.py`)
- **Session Storage**: Local SQLite database (`analysis_sessions.db`)

## 🚀 Performance Features

### Smart Data Sampling

- **Systematic sampling** preserves data distribution
- **Always includes** first and last data points
- **Configurable limits** per chart type
- **Visual feedback** when sampling is applied

### Memory Optimization

- **Lazy loading** of chart data
- **Automatic cleanup** of temporary files
- **Session state management** for efficient memory usage
- **Optimized chart rendering** with reduced heights

### Large Dataset Handling

- **Pagination** for 300+ charts
- **Progressive loading** of chart content
- **Search indexing** for fast filtering
- **Background processing** with progress tracking

## 🎯 Best Practices

### For Large Datasets

1. **Use search and filters** to focus on specific data
2. **Generate reports in batches** for very large analyses
3. **Clean up old sessions** periodically to save space
4. **Monitor memory usage** during processing

### For Better Performance

1. **Close unused browser tabs** during analysis
2. **Use specific search terms** instead of browsing all charts
3. **Generate reports offline** for sharing
4. **Restart the app** if memory usage becomes high

## 🐛 Troubleshooting

### Common Issues

**Charts appear blank:**

- ✅ Check that tables have `ValueX` and `ValueY` columns
- ✅ Verify data is numeric (not text)
- ✅ Ensure data has variation (not all constant values)

**Performance is slow:**

- ✅ Use search and filters to reduce visible charts
- ✅ Check available system memory
- ✅ Restart the application if needed

**Session not saving:**

- ✅ Check write permissions in the application directory
- ✅ Ensure sufficient disk space
- ✅ Verify SQLite is properly installed

**File upload fails:**

- ✅ Confirm file is a valid SQLite database
- ✅ Check file size (recommended < 200MB)
- ✅ Verify file extension is supported

## 🔮 Future Enhancements

- **🔄 Real-time data streaming** for live monitoring
- **📊 Advanced analytics** with statistical analysis
- **🎨 Custom themes** and color schemes
- **📤 Export options** (PDF, Excel, CSV)
- **🔗 API integration** for external data sources
- **👥 Multi-user support** with user sessions
- **📈 Trend analysis** and historical comparisons

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines for:

- 🐛 Bug reports and feature requests
- 💻 Code contributions and pull requests
- 📖 Documentation improvements
- 🧪 Testing and quality assurance

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Streamlit** - For the amazing web app framework
- **Plotly** - For interactive visualization capabilities
- **Pandas** - For powerful data manipulation
- **NumPy** - For efficient numerical computing

---

<div align="center">

**🚀 Enhanced Harmonic Spectrum Analyzer v3.0**

_Developed with ❤️ for electrical engineers and data analysts_

[🌐 Live Demo](http://localhost:8501) | [📖 Documentation](README.md) | [🐛 Issues](issues) | [💬 Discussions](discussions)

</div>
