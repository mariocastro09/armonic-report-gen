#!/usr/bin/env python3
"""
Demo script for the Enhanced Harmonic Spectrum Analyzer v3.0

This script demonstrates the new features:
- Dark theme UI
- Session management with SQLite storage
- Optimized chart rendering for large datasets
- Search and filtering capabilities
- Pagination for handling 300+ charts
- Improved performance and user experience

Usage:
    python demo.py
    
Then open your browser to: http://localhost:8501
"""

import os
import sys
import subprocess
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path

def create_demo_database():
    """Create a demo database with various types of data for testing"""
    print("🔧 Creating demo database...")
    
    # Create demo database
    db_path = "demo_harmonic_data.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Generate sample data for different chart types
    np.random.seed(42)  # For reproducible results
    
    # 1. Waveform data (time series)
    print("  📊 Generating waveform data...")
    for i in range(5):
        table_name = f"Cable_RMU{i+1}_Waveform_{13600+i}"
        
        # Generate realistic waveform data
        time_points = np.linspace(0, 1, 2000)  # 1 second of data
        frequency = 50 + i * 10  # Different frequencies
        amplitude = np.sin(2 * np.pi * frequency * time_points) + \
                   0.1 * np.sin(2 * np.pi * frequency * 3 * time_points) + \
                   0.05 * np.random.normal(0, 1, len(time_points))
        
        df = pd.DataFrame({
            'ValueX': time_points,
            'ValueY': amplitude,
            'Phase': np.random.uniform(0, 360, len(time_points)),
            'Quality': np.random.choice(['Good', 'Fair'], len(time_points))
        })
        
        df.to_sql(table_name, conn, if_exists='replace', index=False)
    
    # 2. Spectrum Hz data (frequency analysis)
    print("  🔊 Generating spectrum Hz data...")
    for i in range(8):
        table_name = f"Cable_RMU{i+1}_Spectrum_Hz_{13600+i}"
        
        # Generate frequency spectrum data
        frequencies = np.array([50, 100, 150, 200, 250, 300, 350, 400, 450, 500])
        magnitudes = np.array([100, 45, 20, 15, 8, 5, 3, 2, 1, 0.5]) * (1 + i * 0.1)
        magnitudes += np.random.normal(0, magnitudes * 0.05)  # Add noise
        
        df = pd.DataFrame({
            'ValueX': frequencies,
            'ValueY': magnitudes,
            'THD': np.random.uniform(1, 5, len(frequencies)),
            'Phase': np.random.uniform(0, 360, len(frequencies))
        })
        
        df.to_sql(table_name, conn, if_exists='replace', index=False)
    
    # 3. Spectrum Order data (harmonic analysis)
    print("  🎵 Generating spectrum order data...")
    for i in range(6):
        table_name = f"Cable_RMU{i+1}_Spectrum_Order_{13600+i}"
        
        # Generate harmonic order data
        orders = np.arange(1, 21)  # 1st to 20th harmonic
        magnitudes = 100 / orders  # Typical harmonic decay
        magnitudes[0] = 100  # Fundamental
        magnitudes += np.random.normal(0, magnitudes * 0.1)  # Add noise
        magnitudes = np.maximum(magnitudes, 0.1)  # Ensure positive values
        
        df = pd.DataFrame({
            'ValueX': orders,
            'ValueY': magnitudes,
            'Limit': 100 / orders * 0.8,  # Regulatory limits
            'Status': np.random.choice(['OK', 'Warning'], len(orders))
        })
        
        df.to_sql(table_name, conn, if_exists='replace', index=False)
    
    # 4. Generic data (other measurements)
    print("  📈 Generating generic measurement data...")
    for i in range(3):
        table_name = f"Temperature_Sensor_{i+1}_Data"
        
        # Generate temperature vs time data
        time_hours = np.linspace(0, 24, 100)  # 24 hours
        temperature = 20 + 10 * np.sin(2 * np.pi * time_hours / 24) + \
                     np.random.normal(0, 2, len(time_hours))
        
        df = pd.DataFrame({
            'ValueX': time_hours,
            'ValueY': temperature,
            'Humidity': np.random.uniform(40, 80, len(time_hours)),
            'Location': f'Sensor_{i+1}'
        })
        
        df.to_sql(table_name, conn, if_exists='replace', index=False)
    
    # 5. Add some tables to be omitted (system tables)
    cursor.execute("""
        CREATE TABLE DeviceID_IID (
            DeviceID TEXT,
            IID INTEGER
        )
    """)
    
    cursor.execute("""
        CREATE TABLE SystemFrequency (
            Frequency REAL,
            Timestamp TEXT
        )
    """)
    
    conn.commit()
    conn.close()
    
    print(f"✅ Demo database created: {db_path}")
    print(f"   📊 Total tables: 22 (17 data tables + 5 waveforms + 8 spectrum Hz + 6 spectrum order + 3 generic)")
    print(f"   📈 Estimated total data points: ~50,000")
    
    return db_path

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'streamlit',
        'pandas',
        'plotly',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All dependencies are installed!")
    return True

def run_streamlit_app():
    """Run the Streamlit application"""
    print("\n🚀 Starting Enhanced Harmonic Spectrum Analyzer v3.0...")
    print("   🌐 Opening browser at: http://localhost:8501")
    print("   ⏹️  Press Ctrl+C to stop the application")
    print("\n" + "="*60)
    print("NEW FEATURES IN v3.0:")
    print("="*60)
    print("🎨 Complete dark theme - no more white backgrounds!")
    print("💾 Session management - save and load analysis sessions")
    print("🔍 Advanced search and filtering for charts")
    print("📄 Pagination for handling 300+ charts efficiently")
    print("⚡ Optimized rendering for large datasets")
    print("🎯 Smart data sampling for better performance")
    print("📊 Enhanced chart viewer with grid layout")
    print("🔄 Easy navigation between analysis sessions")
    print("="*60)
    print("\nTry these features:")
    print("1. Upload the demo database (demo_harmonic_data.db)")
    print("2. Analyze the data and see the optimized rendering")
    print("3. Use search and filters to navigate charts")
    print("4. Start a new analysis to see session management")
    print("5. Check the session history to see saved analyses")
    print("6. Generate HTML reports with dark theme")
    print("\n")
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Streamlit: {e}")
        print("Make sure Streamlit is installed: pip install streamlit")

def main():
    """Main demo function"""
    print("🎯 Enhanced Harmonic Spectrum Analyzer v3.0 - Demo")
    print("="*60)
    
    # Check if we're in the right directory
    if not Path("streamlit_app.py").exists():
        print("❌ streamlit_app.py not found!")
        print("Please run this script from the project directory.")
        return
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Create demo database
    demo_db = create_demo_database()
    
    print(f"\n📁 Demo database ready: {demo_db}")
    print("   You can upload this file in the Streamlit app to test all features")
    
    # Ask user if they want to start the app
    response = input("\n🚀 Start the Streamlit app now? (y/n): ").lower().strip()
    
    if response in ['y', 'yes', '']:
        run_streamlit_app()
    else:
        print("\n📝 To start the app manually, run:")
        print("   streamlit run streamlit_app.py")
        print(f"\n📁 Demo database: {demo_db}")

if __name__ == "__main__":
    main() 