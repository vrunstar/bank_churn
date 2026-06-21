import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    df = pd.read_csv("bank_churn_final.csv")
    return df

def churn_rate(df, group_col):
    return (
        df.groupby(group_col, observed=True)
        .agg(total=('exited', 'count'), churned=('exited', 'sum'))
        .reset_index()
        .assign(churn_rate=lambda x: (x['churned'] / x['total'] * 100).round(2))
    )

KPI_STYLE = """
<style>
[data-testid="stMetric"] {
    background: #1e1e2e;
    border: 1px solid #3a3a5c;
    border-radius: 12px;
    padding: 16px;
}
[data-testid="stMetricLabel"] { color: #a0a0c0; font-size: 13px; }
[data-testid="stMetricValue"] { color: #ffffff; font-size: 28px; font-weight: 700; }
[data-testid="stMetricDelta"] { font-size: 12px; }
</style>
"""