import streamlit as st
import pandas as pd
from utils.data_helpers import (
    load_data, 
    process_data, 
    generate_summary_stats
)
from utils.api_clients import APIClient
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Data Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'api_client' not in st.session_state:
    api_key = os.getenv('API_KEY')
    api_base_url = os.getenv('API_BASE_URL')
    st.session_state.api_client = APIClient(api_base_url, api_key) if api_key and api_base_url else None

def render_sidebar() -> str:
    """Render sidebar and return selected page"""
    with st.sidebar:
        st.title("Navigation")
        page = st.radio(
            "Choose a page",
            ["Upload", "Analysis", "API Data"]
        )
        
        if st.session_state.data is not None:
            st.subheader("Data Filters")
            cols = st.session_state.data.columns.tolist()
            col = st.selectbox("Filter by column", cols)
            values = st.session_state.data[col].unique().tolist()
            selected_value = st.selectbox("Select value", values)
            
            if st.button("Apply Filter"):
                st.session_state.data = process_data(
                    st.session_state.data,
                    {'filter': {col: selected_value}}
                )
                st.success("Filter applied successfully!")
        
        return page

def render_upload_page():
    """Render data upload page"""
    st.header("Data Upload")
    st.write("Upload your data file (CSV or Excel) to begin analysis.")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['csv', 'xlsx'],
        help="Upload a CSV or Excel file containing your data"
    )
    
    if uploaded_file:
        try:
            st.session_state.data = load_data(uploaded_file)
            st.success(f"Successfully loaded data with {len(st.session_state.data)} rows")
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")

def render_analysis_page():
    """Render data analysis page"""
    if st.session_state.data is None:
        st.warning("Please upload data first!")
        return
    
    st.header("Data Analysis")
    
    # Summary statistics
    stats = generate_summary_stats(st.session_state.data)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Rows", stats['row_count'])
    with col2:
        st.metric("Total Columns", stats['column_count'])
    with col3:
        st.metric("Numeric Columns", len(stats['numeric_columns']))
    with col4:
        st.metric("Missing Values", sum(stats['missing_values'].values()))
    
    # Detailed statistics
    st.subheader("Numeric Column Statistics")
    if stats['numeric_summary']:
        st.dataframe(pd.DataFrame(stats['numeric_summary']))
    else:
        st.info("No numeric columns found in the data")
    
    if stats['categorical_summary']:
        st.info(f"Found {len(stats['categorical_summary'])} categorical columns")
    else:
        st.info("No categorical columns found in the data")


def render_api_page():
    """Render API integration page"""
    st.header("API Integration")
    
    if st.session_state.api_client is None:
        st.warning(
            "API client not configured. Please set API_KEY and API_BASE_URL "
            "in your environment variables or .env file."
        )
        return
    
    # API endpoint input
    endpoint = st.text_input(
        "API Endpoint",
        help="Enter the API endpoint path (e.g., 'users' or 'data/stats')"
    )
    
    # Query parameters
    st.subheader("Query Parameters (Optional)")
    col1, col2 = st.columns(2)
    with col1:
        param_key = st.text_input("Parameter Name")
    with col2:
        param_value = st.text_input("Parameter Value")
    
    params = {param_key: param_value} if param_key and param_value else None
    
    if st.button("Fetch Data", disabled=not endpoint):
        try:
            # Use cached get for better performance
            response = st.session_state.api_client.cached_get(endpoint, params)
            
            # Display response
            st.subheader("API Response")
            st.json(response)
            
            # Option to convert to DataFrame
            if isinstance(response, (list, dict)):
                if st.button("Convert to DataFrame"):
                    df = pd.json_normalize(response)
                    st.session_state.data = df
                    st.success("API response converted to DataFrame!")
                    st.dataframe(df)
            
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")

def main():
    """Main application entry point"""
    page = render_sidebar()
    
    if page == "Upload":
        render_upload_page()
    elif page == "Analysis":
        render_analysis_page()
    else:  # API Data
        render_api_page()

if __name__ == "__main__":
    main()
