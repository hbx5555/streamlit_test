import pandas as pd
import streamlit as st
from typing import Dict, Any, Optional, List
import numpy as np

@st.cache_data(ttl=3600)
def load_data(uploaded_file) -> pd.DataFrame:
    """
    Load data from uploaded file with caching.
    
    Args:
        uploaded_file: Streamlit UploadedFile object or file path string
        
    Returns:
        pd.DataFrame: Loaded data
    """
    # Handle Streamlit UploadedFile object
    if hasattr(uploaded_file, 'name'):
        file_name = uploaded_file.name
        if file_name.endswith('.csv'):
            return pd.read_csv(uploaded_file)
        elif file_name.endswith('.xlsx'):
            return pd.read_excel(uploaded_file)
        else:
            raise ValueError(f"Unsupported file format: {file_name}")
    
    # Handle file path string (for backward compatibility)
    elif isinstance(uploaded_file, str):
        if uploaded_file.endswith('.csv'):
            return pd.read_csv(uploaded_file)
        elif uploaded_file.endswith('.xlsx'):
            return pd.read_excel(uploaded_file)
        else:
            raise ValueError(f"Unsupported file format: {uploaded_file}")
    
    else:
        raise ValueError("Invalid file input type")

@st.cache_data
def process_data(df: pd.DataFrame, operations: Dict[str, Any]) -> pd.DataFrame:
    """
    Process dataframe with specified operations.
    
    Args:
        df (pd.DataFrame): Input dataframe
        operations (Dict[str, Any]): Dictionary of operations to perform
        
    Returns:
        pd.DataFrame: Processed dataframe
    """
    processed_df = df.copy()
    
    for op, params in operations.items():
        if op == 'filter':
            for col, value in params.items():
                processed_df = processed_df[processed_df[col] == value]
        elif op == 'group':
            processed_df = processed_df.groupby(params['by']).agg(params['agg'])
        elif op == 'sort':
            processed_df = processed_df.sort_values(
                by=params['by'],
                ascending=params.get('ascending', True)
            )
            
    return processed_df

@st.cache_data
def generate_summary_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate summary statistics for the dataframe.
    
    Args:
        df (pd.DataFrame): Input dataframe
        
    Returns:
        Dict[str, Any]: Dictionary containing summary statistics
    """
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    
    stats = {
        'row_count': len(df),
        'column_count': len(df.columns),
        'numeric_columns': numeric_cols.tolist(),
        'categorical_columns': categorical_cols.tolist(),
        'missing_values': df.isnull().sum().to_dict(),
        'numeric_summary': df[numeric_cols].describe().to_dict() if len(numeric_cols) > 0 else {},
        'categorical_summary': {
            col: df[col].value_counts().to_dict() 
            for col in categorical_cols
        } if len(categorical_cols) > 0 else {}
    }
    
    return stats

@st.cache_data
def create_visualization_data(df: pd.DataFrame, viz_type: str, 
                            x_col: str, y_col: Optional[str] = None,
                            group_by: Optional[str] = None) -> Dict[str, Any]:
    """
    Prepare data for visualization.
    
    Args:
        df (pd.DataFrame): Input dataframe
        viz_type (str): Type of visualization ('scatter', 'line', 'bar', etc.)
        x_col (str): Column for x-axis
        y_col (Optional[str]): Column for y-axis
        group_by (Optional[str]): Column to group by
        
    Returns:
        Dict[str, Any]: Prepared data and metadata for visualization
    """
    plot_data = df.copy()
    
    if viz_type in ['scatter', 'line']:
        if not y_col:
            raise ValueError(f"{viz_type} plot requires y_col")
        
        data = {
            'x': plot_data[x_col],
            'y': plot_data[y_col],
            'type': viz_type
        }
        
        if group_by:
            data['color'] = plot_data[group_by]
            
    elif viz_type == 'bar':
        if y_col:
            data = plot_data.groupby(x_col)[y_col].sum().reset_index()
        else:
            data = plot_data[x_col].value_counts().reset_index()
            data.columns = [x_col, 'count']
            
    elif viz_type == 'histogram':
        data = {
            'x': plot_data[x_col],
            'type': 'histogram'
        }
        
    return data
