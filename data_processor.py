import pandas as pd
import re
from collections import defaultdict
from typing import List, Dict, Tuple
import streamlit as st

class DataProcessor:
    """Handle data validation and processing"""
    
    def __init__(self):
        self.MAX_POINTS = 10000
        self.tables_to_omit = ["DeviceID_IID", "SystemFrequency"]
        self.type_priority = {"hz": 1, "order": 2, "waveform": 3, "other": 4}
        self.suffix_patterns = [
            (re.compile(r"^(.*?)_Spectrum_Hz_?\d*$", re.IGNORECASE), "hz"),
            (re.compile(r"^(.*?)_Spectrum_Order_?\d*$", re.IGNORECASE), "order"),
            (re.compile(r"^(.*?)_Waveform_?\d*$", re.IGNORECASE), "waveform"),
        ]
    
    def validate_and_prepare_data(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """Validate and prepare DataFrame for plotting"""
        if df.empty:
            return df
        
        # Check data points
        if len(df) < 2:
            st.warning(f"Table {table_name} has only {len(df)} data points. Plot may not be meaningful.")
        
        # Remove negative values for spectrum data
        if "spectrum" in table_name.lower():
            if 'ValueX' in df.columns:
                negative_x = df['ValueX'] < 0
                if negative_x.any():
                    removed_count = negative_x.sum()
                    st.info(f"Removed {removed_count} negative ValueX values from {table_name}")
                    df = df[~negative_x]
                    if df.empty:
                        st.warning(f"Table {table_name} became empty after removing negative values")
                        return df
        
        # Sample data if too large
        if len(df) > self.MAX_POINTS:
            st.info(f"Sampling {self.MAX_POINTS} points from {len(df)} total points in {table_name}")
            df = df.sample(n=self.MAX_POINTS, random_state=42).sort_values('ValueX')
        
        return df
    
    def get_sorted_table_list(self, table_names: List[str]) -> List[str]:
        """Sort tables by priority and type"""
        tables_to_omit_lower = [name.lower() for name in self.tables_to_omit]
        grouped_tables = defaultdict(list)
        processed_tables = set()
        other_tables_to_plot = []
        
        # Group tables by pattern
        for table_name in table_names:
            if table_name.lower() in tables_to_omit_lower:
                continue
            
            matched = False
            for pattern, type_key in self.suffix_patterns:
                match = pattern.match(table_name)
                if match:
                    prefix = match.group(1)
                    if table_name not in processed_tables:
                        grouped_tables[prefix].append(
                            (self.type_priority[type_key], type_key, table_name)
                        )
                        processed_tables.add(table_name)
                    matched = True
                    break
            
            if not matched and table_name not in processed_tables:
                other_tables_to_plot.append(table_name)
        
        # Sort within groups
        for prefix in grouped_tables:
            grouped_tables[prefix].sort(key=lambda x: x[0])
        
        # Create final ordered list
        sorted_prefixes = sorted(grouped_tables.keys())
        final_ordered_tables = []
        
        for prefix in sorted_prefixes:
            for priority, type_key, full_table_name in grouped_tables[prefix]:
                final_ordered_tables.append(full_table_name)
        
        # Add other tables
        for table_name in other_tables_to_plot:
            if table_name not in final_ordered_tables:
                final_ordered_tables.append(table_name)
        
        return final_ordered_tables if final_ordered_tables else table_names
    
    def prepare_dataframe_for_plotting(self, df: pd.DataFrame, table_name: str) -> Tuple[pd.DataFrame, bool]:
        """Prepare DataFrame for plotting with validation"""
        if df.empty:
            st.warning(f"Table {table_name} is empty initially")
            return df, False
        
        # Check required columns
        required_cols = ['ValueX', 'ValueY']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            st.error(f"Table {table_name} is missing required columns: {', '.join(missing_cols)}")
            st.info(f"Available columns: {df.columns.tolist()}")
            return df, False
        
        # Convert to numeric
        df['ValueX'] = pd.to_numeric(df['ValueX'], errors='coerce')
        df['ValueY'] = pd.to_numeric(df['ValueY'], errors='coerce')
        
        # Remove NaN values
        df.dropna(subset=['ValueX', 'ValueY'], inplace=True)
        
        # Validate and prepare
        df = self.validate_and_prepare_data(df, table_name)
        
        if df.empty:
            st.warning(f"Table {table_name} is empty after data validation")
            return df, False
        
        return df, True
    
    def get_table_type(self, table_name: str) -> str:
        """Determine the type of table based on name"""
        table_name_lower = table_name.lower()
        
        if "waveform" in table_name_lower:
            return "waveform"
        elif "spectrum_hz" in table_name_lower:
            return "spectrum_hz"
        elif "spectrum_order" in table_name_lower:
            return "spectrum_order"
        else:
            return "generic" 