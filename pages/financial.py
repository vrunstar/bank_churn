import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import KPI_STYLE, churn_rate

st.markdown(KPI_STYLE, unsafe_allow_html=True)
df = st.session_state.df

st.title("Financial Analysis")
st.markdown("#### Churn breakdown by financial indicators")
st.divider()

# Filters
col1, col2, col3 = st.columns(3)
with col1:
    geo_filter = st.multiselect("Geography", df['geography'].unique(), default=df['geography'].unique())
with col2:
    active_filter = st.multiselect("Active Member", [0, 1], default=[0, 1],
                                    format_func=lambda x: "Active" if x == 1 else "Inactive")
with col3:
    card_filter = st.multiselect("Card Type", df['card_type'].unique(), default=df['card_type'].unique())

filtered = df[
    df['geography'].isin(geo_filter) &
    df['isactivemember'].isin(active_filter) &
    df['card_type'].isin(card_filter)
]

st.divider()

# Balance box plot + Num of products
fig = make_subplots(rows=1, cols=2,
                    subplot_titles=("Balance Distribution by Churn", "Churn Rate by No. of Products"))

fig.add_trace(go.Box(
    x=filtered['exited'].map({0: 'Retained', 1: 'Churned'}),
    y=filtered['balance'],
    marker_color='steelblue',
    name='Balance'
), row=1, col=1)

prod = churn_rate(filtered, 'numofproducts')
fig.add_trace(go.Bar(
    x=prod['numofproducts'].astype(str), y=prod['churn_rate'],
    marker_color='coral', name='Products'
), row=1, col=2)

fig.update_layout(height=450, showlegend=False,
                  paper_bgcolor='rgba(0,0,0,0)',
                  plot_bgcolor='rgba(0,0,0,0)',
                  font_color='white')
fig.update_yaxes(title_text="Balance", row=1, col=1)
fig.update_yaxes(title_text="Churn Rate %", row=1, col=2)
st.plotly_chart(fig, use_container_width=True)

# Credit score + Active member
fig2 = make_subplots(rows=1, cols=2,
                     subplot_titles=("Churn Rate by Credit Score Bracket", "Churn Rate by Active Membership"))

credit = churn_rate(filtered, 'credit_bracket')
fig2.add_trace(go.Bar(
    x=credit['credit_bracket'].astype(str), y=credit['churn_rate'],
    marker_color='mediumpurple', name='Credit'
), row=1, col=1)

active = churn_rate(filtered, 'isactivemember')
active['label'] = active['isactivemember'].map({0: 'Inactive', 1: 'Active'})
fig2.add_trace(go.Bar(
    x=active['label'], y=active['churn_rate'],
    marker_color=['tomato', 'steelblue'], name='Active'
), row=1, col=2)

fig2.update_layout(height=450, showlegend=False,
                   paper_bgcolor='rgba(0,0,0,0)',
                   plot_bgcolor='rgba(0,0,0,0)',
                   font_color='white')
fig2.update_yaxes(title_text="Churn Rate %")
st.plotly_chart(fig2, use_container_width=True)

# Balance to salary ratio scatter
st.markdown("#### Balance-to-Salary Ratio vs Churn")
fig3 = go.Figure()
fig3.add_trace(go.Scatter(
    x=filtered[filtered['exited']==0]['balance_salary_ratio'],
    y=filtered[filtered['exited']==0]['value_score'],
    mode='markers', name='Retained',
    marker=dict(color='steelblue', opacity=0.4, size=5)
))
fig3.add_trace(go.Scatter(
    x=filtered[filtered['exited']==1]['balance_salary_ratio'],
    y=filtered[filtered['exited']==1]['value_score'],
    mode='markers', name='Churned',
    marker=dict(color='tomato', opacity=0.4, size=5)
))
fig3.update_layout(height=450,
                   paper_bgcolor='rgba(0,0,0,0)',
                   plot_bgcolor='rgba(0,0,0,0)',
                   font_color='white',
                   xaxis_title='Balance / Salary Ratio',
                   yaxis_title='Value Score')
st.plotly_chart(fig3, use_container_width=True)