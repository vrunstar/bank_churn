import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import KPI_STYLE, churn_rate

st.markdown(KPI_STYLE, unsafe_allow_html=True)
df = st.session_state.df

st.title("Demographics")
st.markdown("#### Churn breakdown by customer demographics")
st.divider()

# Filters
col1, col2 = st.columns(2)
with col1:
    geo_filter = st.multiselect("Geography", df['geography'].unique(), default=df['geography'].unique())
with col2:
    gender_filter = st.multiselect("Gender", df['gender'].unique(), default=df['gender'].unique())

filtered = df[df['geography'].isin(geo_filter) & df['gender'].isin(gender_filter)]

st.divider()

# Age group + Gender
fig = make_subplots(rows=1, cols=2,
                    subplot_titles=("Churn Rate by Age Group", "Churn Rate by Gender"))

age = churn_rate(filtered, 'age_group')
fig.add_trace(go.Bar(x=age['age_group'].astype(str), y=age['churn_rate'],
                     marker_color='mediumpurple', name='Age Group'), row=1, col=1)

gender = churn_rate(filtered, 'gender')
fig.add_trace(go.Bar(x=gender['gender'], y=gender['churn_rate'],
                     marker_color=['steelblue', 'tomato'], name='Gender'), row=1, col=2)

fig.update_layout(height=400, showlegend=False,
                  paper_bgcolor='rgba(0,0,0,0)',
                  plot_bgcolor='rgba(0,0,0,0)',
                  font_color='white')
fig.update_yaxes(title_text="Churn Rate %")
st.plotly_chart(fig, use_container_width=True)

# Geography + Gender heatmap
st.markdown("#### Churn Rate by Geography & Gender")
pivot = filtered.groupby(['geography', 'gender'])['exited'].mean().unstack() * 100

fig2 = go.Figure(go.Heatmap(
    z=pivot.values,
    x=pivot.columns.tolist(),
    y=pivot.index.tolist(),
    colorscale='RdBu_r',
    text=pivot.round(1).values,
    texttemplate='%{text}%',
    textfont={"size": 14}
))
fig2.update_layout(height=350,
                   paper_bgcolor='rgba(0,0,0,0)',
                   plot_bgcolor='rgba(0,0,0,0)',
                   font_color='white')
st.plotly_chart(fig2, use_container_width=True)

# Age distribution
st.markdown("#### Age Distribution: Churned vs Retained")
fig3 = go.Figure()
fig3.add_trace(go.Histogram(x=filtered[filtered['exited']==0]['age'],
                             name='Retained', marker_color='steelblue', opacity=0.7))
fig3.add_trace(go.Histogram(x=filtered[filtered['exited']==1]['age'],
                             name='Churned', marker_color='tomato', opacity=0.7))
fig3.update_layout(barmode='overlay', height=400,
                   paper_bgcolor='rgba(0,0,0,0)',
                   plot_bgcolor='rgba(0,0,0,0)',
                   font_color='white',
                   xaxis_title='Age', yaxis_title='Count')
st.plotly_chart(fig3, use_container_width=True)