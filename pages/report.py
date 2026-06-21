import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import KPI_STYLE
st.markdown(KPI_STYLE, unsafe_allow_html=True)

st.title("Project Report")
st.markdown("#### Bank Customer Churn — Behavior Analysis")
st.divider()

conn = sqlite3.connect("bank_churn.db")

@st.cache_data
def run_query(query):
    return pd.read_sql_query(query, conn)

PLOT_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font_color='white',
    height=380
)

# ── Section 1 — Project Overview ──
st.markdown("## 1. Project Overview")
st.markdown("""
This project performs an industry-standard, end-to-end data analysis of bank customer
churn behavior using a dataset of 10,000 customers. The workflow spans data cleaning and
feature engineering in Python, business question analysis in SQL (SQLite), and an
interactive Streamlit dashboard for stakeholder reporting.
""")
tools = pd.DataFrame({
    "Phase": ["Data Preparation", "Data Analysis", "Visualization", "Reporting"],
    "Tool": ["Python (Pandas, NumPy)", "SQL (SQLite)", "Plotly + Streamlit", "ReportLab"],
    "Purpose": ["Cleaning, EDA, Feature Engineering", "Business Question Answering",
                "Interactive Dashboard", "PDF Report Generation"]
})
st.dataframe(tools, use_container_width=True, hide_index=True)
st.divider()

# ── Section 2 — Dataset Summary ──
st.markdown("## 2. Dataset Summary")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Rows", "10,000")
col2.metric("Total Columns", "18")
col3.metric("Missing Values", "0")
col4.metric("Target Variable", "Exited")
st.markdown("""
**Key Features:**
- Customer demographics: Age, Gender, Geography
- Financial info: Balance, Credit Score, Estimated Salary, Num of Products
- Behavioral: Is Active Member, Has Credit Card, Tenure
- Engineered: Age Group, Tenure Bucket, Value Score, Balance-Salary Ratio
""")
st.divider()

# ── Section 3 — Key Findings ──
st.markdown("## 3. Key Findings")

summary = run_query("""
    SELECT COUNT(*) AS total, SUM(exited) AS churned,
           ROUND(SUM(exited)*100.0/COUNT(*), 2) AS churn_rate,
           ROUND(AVG(CASE WHEN exited=1 THEN balance END), 2) AS avg_churned_balance,
           ROUND(AVG(CASE WHEN exited=0 THEN balance END), 2) AS avg_retained_balance,
           ROUND(AVG(CASE WHEN exited=1 THEN age END), 1) AS avg_churned_age,
           SUM(high_value_churned) AS high_value_churned
    FROM customers
""").iloc[0]

# 3.1 Overall Churn
st.markdown("### 3.1 Overall Churn")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Customers", f"{int(summary['total']):,}")
c2.metric("Churned", f"{int(summary['churned']):,}")
c3.metric("Churn Rate", f"{summary['churn_rate']}%")
c4.metric("High-Value Churned", f"{int(summary['high_value_churned']):,}")

fig = make_subplots(rows=1, cols=2,
                    subplot_titles=("Churn Distribution", "Avg Balance: Churned vs Retained"),
                    specs=[[{"type": "domain"}, {"type": "xy"}]])
fig.add_trace(go.Pie(
    labels=['Retained', 'Churned'],
    values=[int(summary['total']) - int(summary['churned']), int(summary['churned'])],
    hole=0.6, marker_colors=['steelblue', 'tomato'],
    textinfo='label+percent'
), row=1, col=1)
fig.add_trace(go.Bar(
    x=['Churned', 'Retained'],
    y=[summary['avg_churned_balance'], summary['avg_retained_balance']],
    marker_color=['tomato', 'steelblue'],
    text=[f"${summary['avg_churned_balance']:,.0f}", f"${summary['avg_retained_balance']:,.0f}"],
    textposition='outside'
), row=1, col=2)
fig.update_layout(**PLOT_LAYOUT, showlegend=False)
fig.update_yaxes(title_text="Avg Balance ($)", row=1, col=2)
st.plotly_chart(fig, use_container_width=True)

# 3.2 Geography
st.markdown("### 3.2 Churn by Geography")
geo = run_query("""
    SELECT geography, COUNT(*) AS total_customers, SUM(exited) AS churned,
           ROUND(SUM(exited)*100.0/COUNT(*), 2) AS churn_rate
    FROM customers GROUP BY geography ORDER BY churn_rate DESC
""")
st.dataframe(geo, use_container_width=True, hide_index=True)

fig2 = go.Figure(go.Bar(
    x=geo['geography'], y=geo['churn_rate'],
    marker_color=['tomato', 'steelblue', 'coral'],
    text=geo['churn_rate'].astype(str) + '%',
    textposition='outside'
))
fig2.update_layout(**PLOT_LAYOUT, showlegend=False,
                   xaxis_title='Geography', yaxis_title='Churn Rate %')
st.plotly_chart(fig2, use_container_width=True)

# 3.3 Products
st.markdown("### 3.3 Churn by Number of Products")
prod = run_query("""
    SELECT numofproducts AS num_of_products, COUNT(*) AS total,
           SUM(exited) AS churned,
           ROUND(SUM(exited)*100.0/COUNT(*), 2) AS churn_rate
    FROM customers GROUP BY numofproducts ORDER BY numofproducts
""")
st.dataframe(prod, use_container_width=True, hide_index=True)

fig3 = go.Figure(go.Bar(
    x=prod['num_of_products'].astype(str), y=prod['churn_rate'],
    marker_color='mediumpurple',
    text=prod['churn_rate'].astype(str) + '%',
    textposition='outside'
))
fig3.update_layout(**PLOT_LAYOUT, showlegend=False,
                   xaxis_title='Number of Products', yaxis_title='Churn Rate %')
st.plotly_chart(fig3, use_container_width=True)

# 3.4 Avg Metrics
st.markdown("### 3.4 Avg Metrics: Churned vs Retained")
metrics = run_query("""
    SELECT CASE WHEN exited=1 THEN 'Churned' ELSE 'Retained' END AS status,
           ROUND(AVG(balance), 2) AS avg_balance,
           ROUND(AVG(estimatedsalary), 2) AS avg_salary,
           ROUND(AVG(creditscore), 2) AS avg_credit_score,
           ROUND(AVG(age), 1) AS avg_age
    FROM customers GROUP BY exited
""")
st.dataframe(metrics, use_container_width=True, hide_index=True)

fig4 = make_subplots(rows=1, cols=3,
                     subplot_titles=("Avg Credit Score", "Avg Age", "Avg Salary"))
for col, metric, color in zip([1, 2, 3],
                               ['avg_credit_score', 'avg_age', 'avg_salary'],
                               ['steelblue', 'coral', 'mediumpurple']):
    fig4.add_trace(go.Bar(
        x=metrics['status'], y=metrics[metric],
        marker_color=color,
        text=metrics[metric].astype(str),
        textposition='outside'
    ), row=1, col=col)
fig4.update_layout(**PLOT_LAYOUT, showlegend=False)
st.plotly_chart(fig4, use_container_width=True)

# 3.5 Tenure
st.markdown("### 3.5 Churn by Tenure Bucket")
tenure = run_query("""
    SELECT tenure_bucket, COUNT(*) AS total, SUM(exited) AS churned,
           ROUND(SUM(exited)*100.0/COUNT(*), 2) AS churn_rate
    FROM customers GROUP BY tenure_bucket ORDER BY churn_rate DESC
""")
st.dataframe(tenure, use_container_width=True, hide_index=True)

fig5 = go.Figure(go.Bar(
    x=tenure['tenure_bucket'], y=tenure['churn_rate'],
    marker_color='steelblue',
    text=tenure['churn_rate'].astype(str) + '%',
    textposition='outside'
))
fig5.update_layout(**PLOT_LAYOUT, showlegend=False,
                   xaxis_title='Tenure Bucket', yaxis_title='Churn Rate %')
st.plotly_chart(fig5, use_container_width=True)

# 3.6 Age Group
st.markdown("### 3.6 Churn by Age Group")
age = run_query("""
    SELECT age_group, COUNT(*) AS total, SUM(exited) AS churned,
           ROUND(SUM(exited)*100.0/COUNT(*), 2) AS churn_rate
    FROM customers GROUP BY age_group ORDER BY age_group
""")
st.dataframe(age, use_container_width=True, hide_index=True)

fig6 = go.Figure(go.Scatter(
    x=age['age_group'], y=age['churn_rate'],
    mode='lines+markers',
    line=dict(color='tomato', width=3),
    marker=dict(size=10),
    text=age['churn_rate'].astype(str) + '%',
    textposition='top center'
))
fig6.update_layout(**PLOT_LAYOUT, showlegend=False,
                   xaxis_title='Age Group', yaxis_title='Churn Rate %')
st.plotly_chart(fig6, use_container_width=True)

# 3.7 Gender
st.markdown("### 3.7 Churn by Gender")
gender = run_query("""
    SELECT gender, COUNT(*) AS total, SUM(exited) AS churned,
           ROUND(SUM(exited)*100.0/COUNT(*), 2) AS churn_rate
    FROM customers GROUP BY gender ORDER BY churn_rate DESC
""")
st.dataframe(gender, use_container_width=True, hide_index=True)

fig7 = go.Figure(go.Bar(
    x=gender['gender'], y=gender['churn_rate'],
    marker_color=['steelblue', 'tomato'],
    text=gender['churn_rate'].astype(str) + '%',
    textposition='outside'
))
fig7.update_layout(**PLOT_LAYOUT, showlegend=False,
                   xaxis_title='Gender', yaxis_title='Churn Rate %')
st.plotly_chart(fig7, use_container_width=True)

# 3.8 High Value At-Risk
st.markdown("### 3.8 Top 10 High-Value At-Risk Customers")
atrisk = run_query("""
    SELECT customerid, surname, geography, age,
           ROUND(balance, 2) AS balance,
           ROUND(value_score, 4) AS value_score
    FROM customers WHERE exited=0 AND value_score > 0.7
    ORDER BY value_score DESC LIMIT 10
""")
st.dataframe(atrisk, use_container_width=True, hide_index=True)

fig8 = go.Figure(go.Bar(
    x=atrisk['surname'], y=atrisk['value_score'],
    marker_color='coral',
    text=atrisk['value_score'].astype(str),
    textposition='outside'
))
fig8.update_layout(**PLOT_LAYOUT, showlegend=False,
                   xaxis_title='Customer', yaxis_title='Value Score')
st.plotly_chart(fig8, use_container_width=True)

conn.close()
st.divider()

# ── Section 4 — Recommendations ──
st.markdown("## 4. Business Recommendations")
recommendations = [
    ("Target Germany with retention campaigns",
     "Germany has the highest churn rate. Introduce loyalty rewards, personalized offers, "
     "or dedicated relationship managers for German customers."),
    ("Re-engage inactive members",
     "Inactive members churn at a significantly higher rate. Trigger re-engagement campaigns "
     "via email or app notifications with personalized incentives."),
    ("Audit multi-product customers",
     "Customers with 3-4 products show extremely high churn. Review the product bundling "
     "strategy and ensure customers are not being over-sold."),
    ("Prioritize high-value at-risk retention",
     f"{int(summary['high_value_churned']):,} high-value customers have already churned. "
     "Implement an early warning system using value_score to flag at-risk customers before they leave."),
    ("Focus on the 41-50 age segment",
     "Middle-aged customers show the highest churn rates. This segment likely has more "
     "financial options and higher expectations — tailor premium offerings."),
]
for title, body in recommendations:
    with st.expander(title):
        st.markdown(body)

st.divider()

# ── Section 5 — Download PDF ──
st.markdown("## 5. Download Report")
import subprocess
from pathlib import Path

if st.button("Generate PDF Report"):
    subprocess.run(["python", "generate_report.py"])
    st.success("Report generated!")

pdf_path = Path("bank_churn_report.pdf")
if pdf_path.exists():
    with open(pdf_path, "rb") as f:
        st.download_button("⬇️ Download PDF", f,
                           file_name="bank_churn_report.pdf",
                           mime="application/pdf")
    with open(pdf_path, "rb") as f:
        import base64
        b64 = base64.b64encode(f.read()).decode()
        st.components.v1.html(
            f'<embed src="data:application/pdf;base64,{b64}" '
            f'width="100%" height="800px" type="application/pdf">',
            height=820
        )