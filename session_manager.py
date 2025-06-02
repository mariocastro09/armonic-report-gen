import sqlite3
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional
import streamlit as st
import os
import plotly.graph_objects as go
import plotly.io as pio

class SessionManager:
    """Manage analysis sessions in SQLite database"""
    
    def __init__(self, db_path: str = "analysis_sessions.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the sessions database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_sessions (
                    id TEXT PRIMARY KEY,
                    session_name TEXT NOT NULL,
                    original_filename TEXT NOT NULL,
                    file_size INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    charts_count INTEGER DEFAULT 0,
                    total_data_points INTEGER DEFAULT 0,
                    chart_types TEXT,
                    charts_data TEXT,
                    status TEXT DEFAULT 'completed'
                )
            """)
            
            conn.commit()
            conn.close()
        except Exception as e:
            st.error(f"Error initializing session database: {e}")
    
    def _serialize_chart_data(self, charts_data: List[Dict]) -> str:
        """Serialize chart data with proper Plotly figure handling"""
        serializable_data = []
        
        for chart in charts_data:
            chart_copy = chart.copy()
            
            # Convert Plotly figure to JSON
            if 'figure' in chart_copy and hasattr(chart_copy['figure'], 'to_json'):
                chart_copy['figure_json'] = chart_copy['figure'].to_json()
                del chart_copy['figure']  # Remove the original figure object
            
            serializable_data.append(chart_copy)
        
        return json.dumps(serializable_data, default=str)
    
    def _deserialize_chart_data(self, charts_json: str) -> List[Dict]:
        """Deserialize chart data and reconstruct Plotly figures"""
        try:
            charts_data = json.loads(charts_json)
            
            for chart in charts_data:
                # Reconstruct Plotly figure from JSON
                if 'figure_json' in chart:
                    chart['figure'] = pio.from_json(chart['figure_json'])
                    del chart['figure_json']  # Clean up
            
            return charts_data
        except Exception as e:
            st.error(f"Error deserializing chart data: {e}")
            return []
    
    def save_session(self, session_data: Dict) -> str:
        """Save a new analysis session"""
        try:
            session_id = str(uuid.uuid4())
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Prepare chart types summary
            chart_types = {}
            total_points = 0
            
            for chart in session_data.get('charts_generated', []):
                chart_type = chart.get('type', 'unknown')
                chart_types[chart_type] = chart_types.get(chart_type, 0) + 1
                total_points += chart.get('info', {}).get('data_points', 0)
            
            # Serialize chart data properly
            charts_json = self._serialize_chart_data(session_data.get('charts_generated', []))
            
            cursor.execute("""
                INSERT INTO analysis_sessions 
                (id, session_name, original_filename, file_size, charts_count, 
                 total_data_points, chart_types, charts_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                session_data.get('session_name', f"Session {datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                session_data.get('filename', 'Unknown'),
                session_data.get('file_size', 0),
                len(session_data.get('charts_generated', [])),
                total_points,
                json.dumps(chart_types),
                charts_json
            ))
            
            conn.commit()
            conn.close()
            
            return session_id
            
        except Exception as e:
            st.error(f"Error saving session: {e}")
            return None
    
    def get_sessions(self) -> List[Dict]:
        """Get all saved sessions"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, session_name, original_filename, file_size, 
                       created_at, charts_count, total_data_points, chart_types
                FROM analysis_sessions 
                ORDER BY created_at DESC
            """)
            
            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    'id': row[0],
                    'session_name': row[1],
                    'original_filename': row[2],
                    'file_size': row[3],
                    'created_at': row[4],
                    'charts_count': row[5],
                    'total_data_points': row[6],
                    'chart_types': json.loads(row[7]) if row[7] else {}
                })
            
            conn.close()
            return sessions
            
        except Exception as e:
            st.error(f"Error loading sessions: {e}")
            return []
    
    def load_session(self, session_id: str) -> Optional[Dict]:
        """Load a specific session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT session_name, original_filename, charts_data
                FROM analysis_sessions 
                WHERE id = ?
            """, (session_id,))
            
            row = cursor.fetchone()
            if row:
                # Deserialize chart data properly
                charts_data = self._deserialize_chart_data(row[2]) if row[2] else []
                
                return {
                    'session_name': row[0],
                    'filename': row[1],
                    'charts_generated': charts_data
                }
            
            conn.close()
            return None
            
        except Exception as e:
            st.error(f"Error loading session: {e}")
            return None
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM analysis_sessions WHERE id = ?", (session_id,))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            st.error(f"Error deleting session: {e}")
            return False
    
    def get_session_stats(self) -> Dict:
        """Get overall session statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_sessions,
                    SUM(charts_count) as total_charts,
                    SUM(total_data_points) as total_data_points,
                    AVG(charts_count) as avg_charts_per_session
                FROM analysis_sessions
            """)
            
            row = cursor.fetchone()
            conn.close()
            
            return {
                'total_sessions': row[0] or 0,
                'total_charts': row[1] or 0,
                'total_data_points': row[2] or 0,
                'avg_charts_per_session': round(row[3] or 0, 1)
            }
            
        except Exception as e:
            st.error(f"Error getting session stats: {e}")
            return {
                'total_sessions': 0,
                'total_charts': 0,
                'total_data_points': 0,
                'avg_charts_per_session': 0
            } 