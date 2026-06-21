import sqlite3
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Table, TableStyle, HRFlowable,
                                 PageBreak, Image as RLImage)

# ── Helpers ──
def query(sql):
    conn = sqlite3.connect("bank_churn.db")
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df

def fig_to_image(fig, width=6.5*inch, height=3*inch):
    buf = io.BytesIO(fig.to_image(format="png", width=900, height=420, scale=2))
    return RLImage(buf, width=width, height=height)

PLOT_BG = dict(
    paper_bgcolor='white',
    plot_bgcolor='#f9f9f9',
    font_color='#333333',
    height=420
)

def styled_bar(x, y, colors_list, title, xtitle, ytitle, text=None):
    fig = go.Figure(go.Bar(
        x=x, y=y, marker_color=colors_list,
        text=text, textposition='outside'
    ))
    fig.update_layout(**PLOT_BG, showlegend=False, title_text=title,
                      xaxis_title=xtitle, yaxis_title=ytitle)
    return fig

# ── Data ──
summary = query("""
    SELECT COUNT(*) AS total, SUM(exited) AS churned,
           ROUND(SUM(exited)*100.0/COUNT(*), 2) AS churn_rate,
           ROUND(AVG(CASE WHEN exited=1 THEN balance END), 2) AS avg_churned_balance,
           ROUND(AVG(CASE WHEN exited=0 THEN balance END), 2) AS avg_retained_balance,
           ROUND(AVG(CASE WHEN exited=1 THEN age END), 1) AS avg_churned_age,
           SUM(high_value_churned) AS high_value_churned
    FROM customers
""").iloc[0]

geo = query("""
    SELECT geography, COUNT(*) AS total_customers, SUM(exited) AS churned,
           ROUND(SUM(exited)*100.0/COUNT(*), 2) AS churn_rate
    FROM customers GROUP BY geography ORDER BY churn_rate DESC
""")

prod = query("""
    SELECT numofproducts, COUNT(*) AS total, SUM(exited) AS churned,
           ROUND(SUM(exited)*100.0/COUNT(*), 2) AS churn_rate
    FROM customers GROUP BY numofproducts ORDER BY numofproducts
""")

metrics = query("""
    SELECT CASE WHEN exited=1 THEN 'Churned' ELSE 'Retained' END AS status,
           ROUND(AVG(balance), 2) AS avg_balance,
           ROUND(AVG(estimatedsalary), 2) AS avg_salary,
           ROUND(AVG(creditscore), 2) AS avg_credit_score,
           ROUND(AVG(age), 1) AS avg_age
    FROM customers GROUP BY exited
""")

tenure = query("""
    SELECT tenure_bucket, COUNT(*) AS total, SUM(exited) AS churned,
           ROUND(SUM(exited)*100.0/COUNT(*), 2) AS churn_rate
    FROM customers GROUP BY tenure_bucket ORDER BY churn_rate DESC
""")

age = query("""
    SELECT age_group, COUNT(*) AS total, SUM(exited) AS churned,
           ROUND(SUM(exited)*100.0/COUNT(*), 2) AS churn_rate
    FROM customers GROUP BY age_group ORDER BY age_group
""")

gender = query("""
    SELECT gender, COUNT(*) AS total, SUM(exited) AS churned,
           ROUND(SUM(exited)*100.0/COUNT(*), 2) AS churn_rate
    FROM customers GROUP BY gender ORDER BY churn_rate DESC
""")

atrisk = query("""
    SELECT customerid, surname, geography, age,
           ROUND(balance, 2) AS balance,
           ROUND(value_score, 4) AS value_score
    FROM customers WHERE exited=0 AND value_score > 0.7
    ORDER BY value_score DESC LIMIT 10
""")

# ── Report ──
def build_report():
    doc = SimpleDocTemplate("bank_churn_report.pdf", pagesize=letter,
                            rightMargin=0.75*inch, leftMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('T', parent=styles['Title'], fontSize=24,
                                  textColor=colors.HexColor('#1a1a2e'), spaceAfter=6)
    h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=16,
                         textColor=colors.HexColor('#16213e'), spaceBefore=16, spaceAfter=6)
    h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=13,
                         textColor=colors.HexColor('#0f3460'), spaceBefore=10, spaceAfter=4)
    body = ParagraphStyle('B', parent=styles['Normal'], fontSize=10,
                           leading=16, textColor=colors.HexColor('#333333'))

    def hr():
        return HRFlowable(width="100%", thickness=1,
                          color=colors.HexColor('#cccccc'), spaceAfter=8)

    def make_table(data, col_widths, header_color='#1a1a2e'):
        t = Table(data, colWidths=col_widths)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(header_color)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [colors.HexColor('#f5f5f5'), colors.white]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ]))
        return t

    story = []

    # ── Title Page ──
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Bank Customer Churn", title_style))
    story.append(Paragraph("Behavior Analysis Report", title_style))
    story.append(HRFlowable(width="100%", thickness=2,
                             color=colors.HexColor('#e94560'), spaceAfter=12))
    story.append(Paragraph(
        "An end-to-end data analytics project using Python, SQL, and Streamlit.",
        body))
    story.append(Spacer(1, 0.3*inch))

    kpi_data = [
        ["Metric", "Value"],
        ["Total Customers", f"{int(summary['total']):,}"],
        ["Churned Customers", f"{int(summary['churned']):,}"],
        ["Overall Churn Rate", f"{summary['churn_rate']}%"],
        ["Avg Balance (Churned)", f"${summary['avg_churned_balance']:,.2f}"],
        ["Avg Balance (Retained)", f"${summary['avg_retained_balance']:,.2f}"],
        ["Avg Age of Churned Customer", f"{summary['avg_churned_age']}"],
        ["High-Value Churned", f"{int(summary['high_value_churned']):,}"],
    ]
    story.append(make_table(kpi_data, [3*inch, 3*inch]))
    story.append(PageBreak())

    # ── Section 1 ──
    story.append(Paragraph("1. Project Overview", h1))
    story.append(hr())
    story.append(Paragraph(
        "This project performs an industry-standard end-to-end data analysis of bank customer "
        "churn behavior using a dataset of 10,000 customers across data cleaning, feature "
        "engineering, SQL analysis, and interactive dashboard reporting.", body))
    story.append(Spacer(1, 0.15*inch))

    tools_data = [
        ["Phase", "Tool", "Purpose"],
        ["Data Preparation", "Python (Pandas, NumPy)", "Cleaning, EDA, Feature Engineering"],
        ["Data Analysis", "SQL (SQLite)", "Business Question Answering"],
        ["Visualization", "Plotly + Streamlit", "Interactive Dashboard"],
        ["Reporting", "ReportLab", "PDF Report Generation"],
    ]
    story.append(make_table(tools_data, [1.8*inch, 2.2*inch, 2.7*inch], '#0f3460'))
    story.append(PageBreak())

    # ── Section 2 ──
    story.append(Paragraph("2. Dataset Summary", h1))
    story.append(hr())
    story.append(Paragraph(
        "The dataset contains 10,000 bank customers with 18 features covering demographics, "
        "financial information, and behavioral attributes. No missing values were present after "
        "preprocessing. Key engineered features include age_group, tenure_bucket, value_score, "
        "and balance_salary_ratio.", body))
    story.append(PageBreak())

    # ── Section 3 ──
    story.append(Paragraph("3. Key Findings", h1))
    story.append(hr())

    # 3.1 Overall Churn
    story.append(Paragraph("3.1 Overall Churn Distribution", h2))
    story.append(Paragraph(
        f"The overall churn rate is {summary['churn_rate']}%, with {int(summary['churned']):,} "
        f"customers out of {int(summary['total']):,} having exited. Churned customers hold a "
        f"higher average balance (${summary['avg_churned_balance']:,.2f}) than retained ones "
        f"(${summary['avg_retained_balance']:,.2f}), suggesting financial dissatisfaction rather "
        f"than inability to maintain accounts.", body))
    story.append(Spacer(1, 0.1*inch))

    fig_churn = make_subplots(rows=1, cols=2,
                               subplot_titles=("Churn Distribution", "Avg Balance by Churn Status"),
                               specs=[[{"type": "domain"}, {"type": "xy"}]])
    fig_churn.add_trace(go.Pie(
        labels=['Retained', 'Churned'],
        values=[int(summary['total']) - int(summary['churned']), int(summary['churned'])],
        hole=0.6, marker_colors=['steelblue', 'tomato'], textinfo='label+percent'
    ), row=1, col=1)
    fig_churn.add_trace(go.Bar(
        x=['Churned', 'Retained'],
        y=[summary['avg_churned_balance'], summary['avg_retained_balance']],
        marker_color=['tomato', 'steelblue'],
        text=[f"${summary['avg_churned_balance']:,.0f}", f"${summary['avg_retained_balance']:,.0f}"],
        textposition='outside'
    ), row=1, col=2)
    fig_churn.update_layout(**PLOT_BG, showlegend=False)
    story.append(fig_to_image(fig_churn))
    story.append(Spacer(1, 0.2*inch))

    # 3.2 Geography
    story.append(Paragraph("3.2 Churn by Geography", h2))
    story.append(Paragraph(
        "Germany shows a significantly higher churn rate compared to France and Spain, "
        "suggesting region-specific service or competitive issues.", body))
    story.append(Spacer(1, 0.1*inch))

    geo_table_data = [["Geography", "Total Customers", "Churned", "Churn Rate"]] + \
                     [[r['geography'], str(r['total_customers']), str(r['churned']),
                       f"{r['churn_rate']}%"] for _, r in geo.iterrows()]
    story.append(make_table(geo_table_data, [1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch]))
    story.append(Spacer(1, 0.1*inch))

    fig_geo = styled_bar(geo['geography'], geo['churn_rate'],
                          ['tomato', 'steelblue', 'coral'],
                          "Churn Rate by Geography", "Geography", "Churn Rate %",
                          geo['churn_rate'].astype(str) + '%')
    story.append(fig_to_image(fig_geo))
    story.append(Spacer(1, 0.2*inch))

    # 3.3 Products
    story.append(Paragraph("3.3 Churn by Number of Products", h2))
    story.append(Paragraph(
        "Customers with 3-4 products churn at an extremely high rate, suggesting over-selling "
        "leads to dissatisfaction.", body))
    story.append(Spacer(1, 0.1*inch))

    prod_data = [["No. of Products", "Total", "Churned", "Churn Rate"]] + \
                [[str(r['numofproducts']), str(r['total']), str(r['churned']),
                  f"{r['churn_rate']}%"] for _, r in prod.iterrows()]
    story.append(make_table(prod_data, [1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch]))
    story.append(Spacer(1, 0.1*inch))

    fig_prod = styled_bar(prod['numofproducts'].astype(str), prod['churn_rate'],
                           'mediumpurple', "Churn Rate by No. of Products",
                           "Number of Products", "Churn Rate %",
                           prod['churn_rate'].astype(str) + '%')
    story.append(fig_to_image(fig_prod))
    story.append(PageBreak())

    # 3.4 Avg Metrics
    story.append(Paragraph("3.4 Avg Metrics: Churned vs Retained", h2))
    story.append(Paragraph(
        "Churned customers are on average older, with similar salary levels but notably "
        "different balance profiles compared to retained customers.", body))
    story.append(Spacer(1, 0.1*inch))

    met_data = [["Status", "Avg Balance", "Avg Salary", "Avg Credit Score", "Avg Age"]] + \
               [[r['status'], f"${r['avg_balance']:,.2f}", f"${r['avg_salary']:,.2f}",
                 str(r['avg_credit_score']), str(r['avg_age'])] for _, r in metrics.iterrows()]
    story.append(make_table(met_data, [1.2*inch, 1.4*inch, 1.4*inch, 1.5*inch, 1.2*inch]))
    story.append(Spacer(1, 0.1*inch))

    fig_met = make_subplots(rows=1, cols=3,
                             subplot_titles=("Avg Credit Score", "Avg Age", "Avg Salary"))
    for col, metric, color in zip([1, 2, 3],
                                   ['avg_credit_score', 'avg_age', 'avg_salary'],
                                   ['steelblue', 'coral', 'mediumpurple']):
        fig_met.add_trace(go.Bar(
            x=metrics['status'], y=metrics[metric],
            marker_color=color,
            text=metrics[metric].astype(str), textposition='outside'
        ), row=1, col=col)
    fig_met.update_layout(**PLOT_BG, showlegend=False)
    story.append(fig_to_image(fig_met))
    story.append(Spacer(1, 0.2*inch))

    # 3.5 Tenure
    story.append(Paragraph("3.5 Churn by Tenure Bucket", h2))
    story.append(Paragraph(
        "Churn is relatively consistent across tenure groups, indicating that even long-term "
        "customers are not immune to attrition.", body))
    story.append(Spacer(1, 0.1*inch))

    ten_data = [["Tenure Bucket", "Total", "Churned", "Churn Rate"]] + \
               [[r['tenure_bucket'], str(r['total']), str(r['churned']),
                 f"{r['churn_rate']}%"] for _, r in tenure.iterrows()]
    story.append(make_table(ten_data, [1.8*inch, 1.5*inch, 1.5*inch, 1.5*inch]))
    story.append(Spacer(1, 0.1*inch))

    fig_ten = styled_bar(tenure['tenure_bucket'], tenure['churn_rate'],
                          'steelblue', "Churn Rate by Tenure Bucket",
                          "Tenure Bucket", "Churn Rate %",
                          tenure['churn_rate'].astype(str) + '%')
    story.append(fig_to_image(fig_ten))
    story.append(PageBreak())

    # 3.6 Age Group
    story.append(Paragraph("3.6 Churn by Age Group", h2))
    story.append(Paragraph(
        "The 41-50 age group shows the highest churn rate, indicating mid-career customers "
        "are most likely to switch banks.", body))
    story.append(Spacer(1, 0.1*inch))

    age_data = [["Age Group", "Total", "Churned", "Churn Rate"]] + \
               [[r['age_group'], str(r['total']), str(r['churned']),
                 f"{r['churn_rate']}%"] for _, r in age.iterrows()]
    story.append(make_table(age_data, [1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch]))
    story.append(Spacer(1, 0.1*inch))

    fig_age = go.Figure(go.Scatter(
        x=age['age_group'], y=age['churn_rate'],
        mode='lines+markers',
        line=dict(color='tomato', width=3),
        marker=dict(size=10),
        text=age['churn_rate'].astype(str) + '%',
        textposition='top center'
    ))
    fig_age.update_layout(**PLOT_BG, showlegend=False, title_text="Churn Rate by Age Group",
                           xaxis_title="Age Group", yaxis_title="Churn Rate %")
    story.append(fig_to_image(fig_age))
    story.append(Spacer(1, 0.2*inch))

    # 3.7 Gender
    story.append(Paragraph("3.7 Churn by Gender", h2))
    story.append(Paragraph(
        "Female customers churn at a higher rate than male customers, suggesting gender-specific "
        "needs may not be fully addressed.", body))
    story.append(Spacer(1, 0.1*inch))

    gen_data = [["Gender", "Total", "Churned", "Churn Rate"]] + \
               [[r['gender'], str(r['total']), str(r['churned']),
                 f"{r['churn_rate']}%"] for _, r in gender.iterrows()]
    story.append(make_table(gen_data, [1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch]))
    story.append(Spacer(1, 0.1*inch))

    fig_gen = styled_bar(gender['gender'], gender['churn_rate'],
                          ['steelblue', 'tomato'],
                          "Churn Rate by Gender", "Gender", "Churn Rate %",
                          gender['churn_rate'].astype(str) + '%')
    story.append(fig_to_image(fig_gen))
    story.append(PageBreak())

    # 3.8 High Value At-Risk
    story.append(Paragraph("3.8 Top 10 High-Value At-Risk Customers", h2))
    story.append(Paragraph(
        f"{int(summary['high_value_churned']):,} high-value customers have already churned. "
        "The table and chart below show the top 10 currently retained customers most at risk "
        "based on their composite value score.", body))
    story.append(Spacer(1, 0.1*inch))

    risk_data = [["Customer ID", "Surname", "Geography", "Age", "Balance", "Value Score"]] + \
                [[str(r['customerid']), r['surname'], r['geography'], str(r['age']),
                  f"${r['balance']:,.2f}", str(r['value_score'])] for _, r in atrisk.iterrows()]
    story.append(make_table(risk_data,
                             [1*inch, 1.2*inch, 1.1*inch, 0.7*inch, 1.2*inch, 1.2*inch],
                             '#e94560'))
    story.append(Spacer(1, 0.1*inch))

    fig_risk = styled_bar(atrisk['surname'], atrisk['value_score'],
                           'coral', "Top 10 High-Value At-Risk Customers",
                           "Customer", "Value Score",
                           atrisk['value_score'].astype(str))
    story.append(fig_to_image(fig_risk))
    story.append(PageBreak())

    # ── Section 4 — Recommendations ──
    story.append(Paragraph("4. Business Recommendations", h1))
    story.append(hr())

    recommendations = [
        ("1. Target Germany with retention campaigns",
         "Germany has the highest churn rate. Introduce loyalty rewards, personalized offers, "
         "or dedicated relationship managers for German customers."),
        ("2. Re-engage inactive members",
         "Inactive members churn at a significantly higher rate. Trigger re-engagement campaigns "
         "via email or app notifications with personalized incentives."),
        ("3. Audit multi-product customers",
         "Customers with 3-4 products show extremely high churn. Review the product bundling "
         "strategy and ensure customers are not being over-sold."),
        ("4. Prioritize high-value at-risk retention",
         f"{int(summary['high_value_churned']):,} high-value customers have already churned. "
         "Implement an early warning system using value_score to flag at-risk customers."),
        ("5. Focus on the 41-50 age segment",
         "Middle-aged customers show the highest churn rates. Tailor premium offerings "
         "to meet their higher expectations."),
    ]
    for title, body_text in recommendations:
        story.append(Paragraph(title, h2))
        story.append(Paragraph(body_text, body))
        story.append(Spacer(1, 0.1*inch))

    story.append(PageBreak())

    # ── Section 5 — Conclusion ──
    story.append(Paragraph("5. Conclusion", h1))
    story.append(hr())
    story.append(Paragraph(
        "This project demonstrates a complete, industry-standard data analytics workflow applied "
        "to customer churn in banking. Through Python EDA, SQL analysis, and an interactive "
        "Streamlit dashboard, we identified key churn drivers including geography, product count, "
        "age group, and activity level. The engineered features provide a strong foundation for "
        "future machine learning churn prediction models.", body))

    doc.build(story)
    print("✅ bank_churn_report.pdf generated successfully.")

if __name__ == "__main__":
    build_report()