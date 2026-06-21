import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
import pandas as pd
from utils import KPI_STYLE, churn_rate

st.markdown(KPI_STYLE, unsafe_allow_html=True)

st.title("SQL Insights")
st.markdown("#### Business questions answered via SQL queries")
st.divider()

@st.cache_data
def run_query(query):
    conn = sqlite3.connect("bank_churn.db")
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Q1 — Churn by geography
q1 = run_query("""
    SELECT geography,
           COUNT(*) AS total,
           SUM(exited) AS churned,
           ROUND(SUM(exited)*100.0/COUNT(*), 2) AS churn_rate
    FROM customers GROUP BY geography ORDER BY churn_rate DESC
""")

# Q2 — Churn by num of products
q2 = run_query("""
    SELECT numofproducts,
           COUNT(*) AS total,
           SUM(exited) AS churned,
           ROUND(SUM(exited)*100.0/COUNT(*), 2) AS churn_rate
    FROM customers GROUP BY numofproducts ORDER BY numofproducts
""")

# Q3 — Churn by tenure bucket
q3 = run_query("""
    SELECT tenure_bucket,
           COUNT(*) AS total,
           SUM(exited) AS churned,
           ROUND(SUM(exited)*100.0/COUNT(*), 2) AS churn_rate
    FROM customers GROUP BY tenure_bucket ORDER BY churn_rate DESC
""")

# Q4 — Avg metrics by churn status
q4 = run_query("""
    SELECT CASE WHEN exited=1 THEN 'Churned' ELSE 'Retained' END AS status,
           ROUND(AVG(balance), 2) AS avg_balance,
           ROUND(AVG(estimatedsalary), 2) AS avg_salary,
           ROUND(AVG(creditscore), 2) AS avg_credit_score,
           ROUND(AVG(age), 1) AS avg_age
    FROM customers GROUP BY exited
""")

# Q5 — Churn by gender x geography
q5 = run_query("""
    SELECT geography, gender,
           ROUND(SUM(exited)*100.0/COUNT(*), 2) AS churn_rate
    FROM customers GROUP BY geography, gender ORDER BY churn_rate DESC
""")

# Q6 — High value at risk
q6 = run_query("""
    SELECT customerid, surname, geography, age,
           ROUND(balance, 2) AS balance,
           ROUND(value_score, 4) AS value_score
    FROM customers
    WHERE exited=0 AND value_score > 0.7
    ORDER BY value_score DESC
    LIMIT 10
""")

# Visualize Q1, Q2, Q3
fig = make_subplots(rows=1, cols=3,
                    subplot_titles=("Churn Rate by Geography",
                                    "Churn Rate by No. of Products",
                                    "Churn Rate by Tenure Bucket"))

fig.add_trace(go.Bar(x=q1['geography'], y=q1['churn_rate'],
                     marker_color='tomato'), row=1, col=1)

fig.add_trace(go.Bar(x=q2['numofproducts'].astype(str), y=q2['churn_rate'],
                     marker_color='mediumpurple'), row=1, col=2)

fig.add_trace(go.Bar(x=q3['tenure_bucket'], y=q3['churn_rate'],
                     marker_color='steelblue'), row=1, col=3)

fig.update_layout(height=400, showlegend=False,
                  paper_bgcolor='rgba(0,0,0,0)',
                  plot_bgcolor='rgba(0,0,0,0)',
                  font_color='white')
fig.update_yaxes(title_text="Churn Rate %")
st.plotly_chart(fig, use_container_width=True)

# Avg metrics table
st.markdown("#### Avg Metrics: Churned vs Retained")
st.dataframe(q4, use_container_width=True)

# Gender x Geography churn
st.markdown("#### Churn Rate by Gender & Geography")
fig2 = go.Figure(go.Bar(
    x=q5['geography'] + ' — ' + q5['gender'],
    y=q5['churn_rate'],
    marker_color='coral'
))
fig2.update_layout(height=400,
                   paper_bgcolor='rgba(0,0,0,0)',
                   plot_bgcolor='rgba(0,0,0,0)',
                   font_color='white',
                   xaxis_title='Segment',
                   yaxis_title='Churn Rate %')
st.plotly_chart(fig2, use_container_width=True)

# High value at risk table
st.markdown("#### Top 10 High-Value At-Risk Customers")
st.dataframe(q6, use_container_width=True)