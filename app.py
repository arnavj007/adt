# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import database as db
import os
from datetime import datetime
import uuid

# Set page configuration
st.set_page_config(
    page_title="911 Emergency Calls Analysis",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize the database
db.initialize_database()

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select a page",
    ["Dashboard", "Call Records", "Data Entry", "Analytics", "Advanced Queries"]
)

# Function to load data if not already loaded
def load_data():
    if st.sidebar.button("Load CSV Data"):
        csv_file = st.sidebar.file_uploader("Upload 911 Calls CSV file", type=["csv"])
        if csv_file is not None:
            # Save the uploaded CSV to a temporary file
            with open('temp_data.csv', 'wb') as f:
                f.write(csv_file.getbuffer())
            
            # Load the data into the database
            db.load_csv_to_database('temp_data.csv')
            st.sidebar.success("Data loaded successfully!")
            
            # Clean up temporary file
            if os.path.exists('temp_data.csv'):
                os.remove('temp_data.csv')

# Display data loading option in sidebar
load_data()

# Dashboard Page
if page == "Dashboard":
    st.title("911 Emergency Calls Dashboard")
    
    # Display summary statistics
    st.header("Summary Statistics")
    
    # Quick visualizations
    st.header("Quick Insights")
    
    # Create two columns for charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Calls by Priority")
        priority_df = db.get_calls_by_priority()
        if not priority_df.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(x='priority', y='call_count', data=priority_df, palette='viridis', ax=ax)
            ax.set_title('Emergency Calls by Priority')
            ax.set_xlabel('Priority Level')
            ax.set_ylabel('Number of Calls')
            st.pyplot(fig)
        else:
            st.info("No priority data available. Please load data first.")

# Add the other pages (Call Records, Data Entry, Analytics, Advanced Queries)
# Each page will display different functionality
