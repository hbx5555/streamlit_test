import requests
import streamlit as st
from typing import Dict, Any, Optional, Union
import os
from functools import wraps
import time
import json
from datetime import datetime

def retry_on_failure(max_retries: int = 3, delay: int = 1):
    """Decorator for retrying failed API calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        time.sleep(delay * (attempt + 1))  # Exponential backoff
            raise last_error
        return wrapper
    return decorator

class APIClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize API client with base URL and optional API key.
        
        Args:
            base_url (str): Base URL for the API
            api_key (Optional[str]): API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or os.getenv('API_KEY')
        if not self.api_key:
            st.warning("API key not found. Please set it in the environment variables.")
        
        self._init_session()

    @st.cache_resource
    def _init_session(self) -> None:
        """Initialize and cache the session"""
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            })

    @retry_on_failure()
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make GET request to API endpoint.
        
        Args:
            endpoint (str): API endpoint
            params (Optional[Dict[str, Any]]): Query parameters
            
        Returns:
            Dict[str, Any]: API response
        """
        url = f'{self.base_url}/{endpoint.lstrip("/")}'
        with st.spinner(f'Fetching data from {endpoint}...'):
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()

    @retry_on_failure()
    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make POST request to API endpoint.
        
        Args:
            endpoint (str): API endpoint
            data (Dict[str, Any]): Request payload
            
        Returns:
            Dict[str, Any]: API response
        """
        url = f'{self.base_url}/{endpoint.lstrip("/")}'
        with st.spinner(f'Sending data to {endpoint}...'):
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return response.json()

    def stream_data(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Stream data from an API endpoint.
        
        Args:
            endpoint (str): API endpoint
            params (Optional[Dict[str, Any]]): Query parameters
            
        Yields:
            Any: Data chunks from the API
        """
        url = f'{self.base_url}/{endpoint.lstrip("/")}'
        with self.session.get(url, params=params, stream=True) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    yield json.loads(line)

    @st.cache_data(ttl=3600)
    def cached_get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make cached GET request to API endpoint.
        
        Args:
            endpoint (str): API endpoint
            params (Optional[Dict[str, Any]]): Query parameters
            
        Returns:
            Dict[str, Any]: Cached API response
        """
        return self.get(endpoint, params)

    def health_check(self) -> bool:
        """
        Check API health status.
        
        Returns:
            bool: True if API is healthy
        """
        try:
            response = self.get('health')
            return response.get('status') == 'healthy'
        except:
            return False

    def __del__(self):
        """Cleanup session on deletion"""
        if hasattr(self, 'session'):
            self.session.close()
