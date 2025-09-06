# Data Analysis Dashboard

A modern data analysis dashboard built with Streamlit, featuring data upload, analysis, visualization, and API integration capabilities.

## Features

- **Data Upload**: Support for CSV and Excel files
- **Data Analysis**: Interactive data exploration with summary statistics
- **Data Visualization**: Multiple chart types (scatter, line, bar, histogram)
- **API Integration**: Connect and fetch data from external APIs
- **Modern UI**: Clean, responsive interface
- **Performance Optimized**: Caching for data operations and API calls

## Project Structure

```
.
├── .streamlit/
│   └── config.toml      # Streamlit configuration
├── utils/
│   ├── data_helpers.py  # Data processing utilities
│   └── api_clients.py   # API integration utilities
├── requirements.txt     # Project dependencies
├── Procfile            # Heroku deployment config
├── streamlit_app.py    # Main application
└── README.md          # Documentation
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
Create a `.env` file with:
```
API_KEY=your_api_key
API_BASE_URL=your_api_base_url
```

4. Run the application:
```bash
streamlit run streamlit_app.py
```

## Usage

### Data Upload
- Navigate to "Data Upload" page
- Upload CSV or Excel files
- View data loading confirmation

### Analysis
- Switch to "Analysis" page
- View summary statistics
- Explore numeric and categorical distributions

### Visualization
- Go to "Visualization" page
- Choose visualization type
- Select data columns for axes
- Optional grouping for enhanced insights

### API Integration
- Access "API Integration" page
- Enter API endpoint
- Add query parameters if needed
- View and optionally convert API data to DataFrame

## Deployment

### Local Development
```bash
streamlit run streamlit_app.py
```

### Heroku Deployment
```bash
git push heroku main
```

## Dependencies

- streamlit==1.27.0
- pandas==2.1.0
- numpy==1.24.3
- plotly==5.16.1
- requests==2.31.0
- python-dotenv==1.0.0
- openpyxl==3.1.2
