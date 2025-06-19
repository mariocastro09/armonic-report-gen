import sqlite3
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional
import streamlit as st
import os
import plotly.graph_objects as go
import plotly.io as pio
import pytz

class SessionManager:
    """Manage analysis sessions in SQLite database"""
    
    def __init__(self, db_path: str = "analysis_sessions.db"):
        self.db_path = db_path
        self.timezone = pytz.timezone('America/Santiago')
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
                    status TEXT DEFAULT 'completed',
                    is_favorite INTEGER DEFAULT 0
                )
            """)
            
            # Add favorites column to existing databases
            try:
                cursor.execute("ALTER TABLE analysis_sessions ADD COLUMN is_favorite INTEGER DEFAULT 0")
            except sqlite3.OperationalError:
                # Column already exists
                pass
            
            conn.commit()
            conn.close()
        except Exception as e:
            st.error(f"Error initializing session database: {e}")
    
    def generate_session_name_suggestion(self, filename: str) -> str:
        """Generate a unique session name suggestion"""
        # Clean filename
        clean_filename = filename.replace('.hfpdb', '').replace('.db', '').replace('.sqlite', '')
        clean_filename = clean_filename.replace('_', ' ').replace('-', ' ')
        
        # Get current time in Santiago timezone
        now = datetime.now(self.timezone)
        timestamp = now.strftime("%Y%m%d_%H%M")
        
        # Create suggestion
        suggestion = f"{clean_filename} - {timestamp}"
        
        # Check if name exists and make it unique
        existing_names = self.get_existing_session_names()
        counter = 1
        original_suggestion = suggestion
        
        while suggestion in existing_names:
            suggestion = f"{original_suggestion} ({counter})"
            counter += 1
        
        return suggestion
    
    def get_existing_session_names(self) -> List[str]:
        """Get all existing session names"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT session_name FROM analysis_sessions")
            names = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            return names
            
        except Exception as e:
            st.error(f"Error getting session names: {e}")
            return []
    
    def _get_santiago_timestamp(self) -> str:
        """Get current timestamp in Santiago timezone"""
        now = datetime.now(self.timezone)
        return now.strftime("%Y-%m-%d %H:%M:%S %Z")
    
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
    
    def save_session(self, session_data: Dict, session_name: str = None) -> str:
        """Save a new analysis session with custom name"""
        try:
            session_id = str(uuid.uuid4())
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Use provided name or generate default
            if not session_name:
                filename = session_data.get('filename', 'Unknown')
                session_name = self.generate_session_name_suggestion(filename)
            
            # Prepare chart types summary
            chart_types = {}
            total_points = 0
            
            for chart in session_data.get('charts_generated', []):
                chart_type = chart.get('type', 'unknown')
                chart_types[chart_type] = chart_types.get(chart_type, 0) + 1
                total_points += chart.get('info', {}).get('data_points', 0)
            
            # Serialize chart data properly
            charts_json = self._serialize_chart_data(session_data.get('charts_generated', []))
            
            # Get Santiago timestamp
            santiago_timestamp = self._get_santiago_timestamp()
            
            cursor.execute("""
                INSERT INTO analysis_sessions 
                (id, session_name, original_filename, file_size, created_at, charts_count, 
                 total_data_points, chart_types, charts_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                session_name,
                session_data.get('filename', 'Unknown'),
                session_data.get('file_size', 0),
                santiago_timestamp,
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
                       created_at, charts_count, total_data_points, chart_types, is_favorite
                FROM analysis_sessions 
                ORDER BY is_favorite DESC, created_at DESC
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
                    'chart_types': json.loads(row[7]) if row[7] else {},
                    'is_favorite': bool(row[8])
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
        """Get session statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get total sessions
            cursor.execute("SELECT COUNT(*) FROM analysis_sessions")
            total_sessions = cursor.fetchone()[0]
            
            # Get total charts
            cursor.execute("SELECT SUM(charts_count) FROM analysis_sessions")
            total_charts = cursor.fetchone()[0] or 0
            
            # Get total data points
            cursor.execute("SELECT SUM(total_data_points) FROM analysis_sessions")
            total_data_points = cursor.fetchone()[0] or 0
            
            # Get average charts per session
            avg_charts = total_charts / total_sessions if total_sessions > 0 else 0
            
            # Get favorites count
            cursor.execute("SELECT COUNT(*) FROM analysis_sessions WHERE is_favorite = 1")
            favorites_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_sessions': total_sessions,
                'total_charts': total_charts,
                'total_data_points': total_data_points,
                'avg_charts_per_session': round(avg_charts, 1),
                'favorites_count': favorites_count
            }
            
        except Exception as e:
            st.error(f"Error getting session statistics: {e}")
            return {
                'total_sessions': 0,
                'total_charts': 0,
                'total_data_points': 0,
                'avg_charts_per_session': 0,
                'favorites_count': 0
            }
    
    def update_session_name(self, session_id: str, new_name: str) -> bool:
        """Update session name"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE analysis_sessions 
                SET session_name = ? 
                WHERE id = ?
            """, (new_name, session_id))
            
            success = cursor.rowcount > 0
            conn.commit()
            conn.close()
            
            return success
            
        except Exception as e:
            st.error(f"Error updating session name: {e}")
            return False
    
    def toggle_favorite(self, session_id: str) -> bool:
        """Toggle favorite status of a session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get current favorite status
            cursor.execute("SELECT is_favorite FROM analysis_sessions WHERE id = ?", (session_id,))
            result = cursor.fetchone()
            
            if result is None:
                conn.close()
                return False
            
            current_status = bool(result[0])
            new_status = not current_status
            
            # Update favorite status
            cursor.execute("""
                UPDATE analysis_sessions 
                SET is_favorite = ? 
                WHERE id = ?
            """, (int(new_status), session_id))
            
            success = cursor.rowcount > 0
            conn.commit()
            conn.close()
            
            return success
            
        except Exception as e:
            st.error(f"Error toggling favorite: {e}")
            return False
    
    def get_favorite_sessions(self) -> List[Dict]:
        """Get only favorite sessions"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, session_name, original_filename, file_size, 
                       created_at, charts_count, total_data_points, chart_types, is_favorite
                FROM analysis_sessions 
                WHERE is_favorite = 1
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
                    'chart_types': json.loads(row[7]) if row[7] else {},
                    'is_favorite': bool(row[8])
                })
            
            conn.close()
            return sessions
            
        except Exception as e:
            st.error(f"Error getting favorite sessions: {e}")
            return [] 