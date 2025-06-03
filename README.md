# 🚀 Enhanced Harmonic Spectrum Analyzer v3.1

A powerful, modern web application for analyzing harmonic spectra and waveforms from SQLite databases. Built with Streamlit, featuring a complete dark theme, session management, and optimized rendering for large datasets.

## ✨ What's New in v3.1

### 📝 Enhanced Session Management

- **Unique session names** with automatic suggestions based on filename and timestamp
- **Editable session names** during creation with optional custom naming
- **Santiago timezone support** for accurate timestamp recording
- **Improved session persistence** with better organization

### 📄 PDF-Optimized Reports

- **Enhanced PDF spacing** with proper header positioning for print conversion
- **Improved chart layout** with better margins and spacing for A4 pages
- **Consistent theming** between main screen and session list reports
- **Professional color schemes** optimized for printing

### 🎯 Streamlined File Support

- **Focused on .hfpdb format** for specialized harmonic analysis databases
- **Simplified interface** with clear file format requirements
- **Professional icons** replacing music/sound symbols with neutral chart icons

### 🔧 Technical Improvements

- **Rounded numbers** in chart displays for better readability
- **Consistent theming** across all report generation methods
- **Better PDF conversion** with proper page breaks and spacing
- **Santiago timezone** integration for accurate session timestamps

## 🎯 Key Features

- **📁 Specialized Format Support**: `.hfpdb` (SQLite-based harmonic analysis databases)
- **📊 Chart Types**: Waveforms, Frequency Spectra, Harmonic Analysis, Generic Data
- **🔄 Real-time Processing**: Live progress tracking with detailed status
- **💾 Advanced Session Management**: Custom naming, timezone support, and persistence
- **🔍 Smart Navigation**: Search, filter, and paginate through large datasets
- **📱 Responsive Design**: Works on desktop, tablet, and mobile devices
- **⚡ High Performance**: Optimized for datasets with millions of data points
- **📄 PDF-Ready Reports**: Optimized HTML reports for professional PDF conversion

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
- **PyTZ 2023.3+** (for Santiago timezone support)

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

- 📁 Upload your .hfpdb database file
- 📝 Customize session name (optional)
- 🔍 Click "Analyze Database" to process
- 📊 View charts with real-time generation
- 💾 Session automatically saved with custom name

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

### 4. **PDF Report Generation**

- 🚀 Generate professional HTML reports
- 🎨 Choose color schemes optimized for printing
- ⬇️ Download reports for sharing
- 🖨️ Convert to PDF using browser print function
- 📱 Mobile-responsive design

## 🎨 Supported Chart Types

| Type                  | Description             | Visual           | Use Case                       |
| --------------------- | ----------------------- | ---------------- | ------------------------------ |
| **📈 Waveform**       | Time-series line charts | Continuous lines | Temporal signal analysis       |
| **📊 Spectrum Hz**    | Frequency bar charts    | Vertical bars    | Frequency domain analysis      |
| **📊 Spectrum Order** | Harmonic bar charts     | Vertical bars    | Harmonic distortion analysis   |
| **📊 Generic**        | Scatter plots           | Point clouds     | General X-Y data relationships |

## 🔧 Configuration

### Database Requirements

- **Format**: .hfpdb (SQLite-based harmonic analysis database)
- **Required Columns**: `ValueX`, `ValueY` (numeric)
- **Optional Columns**: Any additional metadata
- **Table Naming**: Automatic type detection based on table names

### Performance Settings

- **Max Points per Chart**: 5,000 (automatically sampled)
- **Charts per Page**: 8 (configurable in `chart_viewer.py`)
- **Session Storage**: Local SQLite database (`analysis_sessions.db`)
- **Timezone**: America/Santiago for session timestamps

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

- ✅ Confirm file is a valid .hfpdb database
- ✅ Check file size (recommended < 200MB)
- ✅ Verify file extension is .hfpdb

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
- **PyTZ** - For timezone support

---

<div align="center">

**🚀 Enhanced Harmonic Spectrum Analyzer v3.1**

_Developed with ❤️ for electrical engineers and data analysts_

[🌐 Live Demo](http://localhost:8501) | [📖 Documentation](README.md) | [🐛 Issues](issues) | [💬 Discussions](discussions)

</div>
