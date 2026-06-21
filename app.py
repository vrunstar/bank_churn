import streamlit as st
from utils import load_data, KPI_STYLE

st.set_page_config(page_title="Bank Churn Analysis", layout="wide", initial_sidebar_state="auto")

# Pages
overview = st.Page("pages/overview.py", title="Overview")
demographics = st.Page("pages/demographics.py", title="Demographics")
financial = st.Page("pages/financial.py", title="Financial")
sql_insights = st.Page("pages/sql_insights.py", title="SQL Insights")
report = st.Page("pages/report.py", title="Report")

nav = st.navigation([overview, demographics, financial, sql_insights, report])

# Shared state
if "df" not in st.session_state:
    st.session_state.df = load_data()

nav.run()