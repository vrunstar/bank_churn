import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import KPI_STYLE, churn_rate

st.markdown(KPI_STYLE, unsafe_allow_html=True)
df = st.session_state.df

st.title("Bank Churn Analysis")
st.markdown("#### Overview Dashboard")
st.divider()

# KPI Cards
total = len(df)
churned = df['exited'].sum()
churn_pct = churned / total * 100
high_val_churned = df['high_value_churned'].sum()
avg_balance = df['balance'].mean()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Customers", f"{total:,}")
c2.metric("Churned", f"{churned:,}")
c3.metric("Churn Rate", f"{churn_pct:.2f}%")
c4.metric("High-Value Churned", f"{int(high_val_churned):,}")
c5.metric("Avg Balance", f"${avg_balance:,.0f}")

st.divider()

# Row 1 — Donut + Geography + Gender
fig1 = make_subplots(rows=1, cols=3,
                     subplot_titles=("Churn Distribution", "Churn Rate by Geography", "Churn Rate by Gender"),
                     specs=[[{"type": "domain"}, {"type": "xy"}, {"type": "xy"}]])

fig1.add_trace(go.Pie(
    labels=['Retained', 'Churned'],
    values=[total - churned, churned],
    hole=0.6,
    marker_colors=['steelblue', 'tomato'],
    textinfo='label+percent'
), row=1, col=1)

geo = churn_rate(df, 'geography')
fig1.add_trace(go.Bar(x=geo['geography'], y=geo['churn_rate'],
                      marker_color='tomato'), row=1, col=2)

gender = churn_rate(df, 'gender')
fig1.add_trace(go.Bar(x=gender['gender'], y=gender['churn_rate'],
                      marker_color=['steelblue', 'coral']), row=1, col=3)

fig1.update_layout(height=400, showlegend=False,
                   paper_bgcolor='rgba(0,0,0,0)',
                   plot_bgcolor='rgba(0,0,0,0)',
                   font_color='white')
fig1.update_yaxes(title_text="Churn Rate %", row=1, col=2)
fig1.update_yaxes(title_text="Churn Rate %", row=1, col=3)
st.plotly_chart(fig1, use_container_width=True)

# Row 2 — Card Type + Satisfaction Score + Tenure Bucket
fig2 = make_subplots(rows=1, cols=3,
                     subplot_titles=("Churn Rate by Card Type",
                                     "Churn Rate by Satisfaction Score",
                                     "Churn Rate by Tenure Bucket"))

card = churn_rate(df, 'card_type')
fig2.add_trace(go.Bar(x=card['card_type'], y=card['churn_rate'],
                      marker_color='mediumpurple'), row=1, col=1)

sat = churn_rate(df, 'satisfaction_score')
fig2.add_trace(go.Bar(x=sat['satisfaction_score'].astype(str), y=sat['churn_rate'],
                      marker_color='steelblue'), row=1, col=2)

tenure = churn_rate(df, 'tenure_bucket')
fig2.add_trace(go.Bar(x=tenure['tenure_bucket'].astype(str), y=tenure['churn_rate'],
                      marker_color='coral'), row=1, col=3)

fig2.update_layout(height=400, showlegend=False,
                   paper_bgcolor='rgba(0,0,0,0)',
                   plot_bgcolor='rgba(0,0,0,0)',
                   font_color='white')
fig2.update_yaxes(title_text="Churn Rate %")
st.plotly_chart(fig2, use_container_width=True)

# Row 3 — Age group line + Active member donut
fig3 = make_subplots(rows=1, cols=2,
                     subplot_titles=("Churn Rate by Age Group", "Active vs Inactive Churn"),
                     specs=[[{"type": "xy"}, {"type": "domain"}]])

age = churn_rate(df, 'age_group')
fig3.add_trace(go.Scatter(x=age['age_group'].astype(str), y=age['churn_rate'],
                           mode='lines+markers',
                           line=dict(color='tomato', width=3),
                           marker=dict(size=8)), row=1, col=1)

active = churn_rate(df, 'isactivemember')
fig3.add_trace(go.Pie(
    labels=['Inactive', 'Active'],
    values=active['churned'].tolist(),
    hole=0.6,
    marker_colors=['tomato', 'steelblue'],
    textinfo='label+percent'
), row=1, col=2)

fig3.update_layout(height=400, showlegend=False,
                   paper_bgcolor='rgba(0,0,0,0)',
                   plot_bgcolor='rgba(0,0,0,0)',
                   font_color='white')
fig3.update_yaxes(title_text="Churn Rate %", row=1, col=1)
st.plotly_chart(fig3, use_container_width=True)