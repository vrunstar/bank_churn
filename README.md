# Bank Customer Churn Analysis

An end-to-end data analytics portfolio project analyzing customer churn behavior across 10,000 bank customers using Python, SQL, and Streamlit.

---

## Project Overview

This project mirrors an industry-standard data analytics workflow — from raw data to interactive dashboard and PDF report — covering every phase a professional analyst would handle.

**Inspired by:** [Customer Shopping Trends Analysis](https://github.com/amlanmohanty1/customer-trends-data-analysis-SQL-Python-PowerBI)

---

## Business Problem

A bank is experiencing customer churn and needs to understand:
- Who is churning and why?
- Which customer segments are most at risk?
- What actions can reduce churn?

---

## Project Structure
```
bank_churn_app/
│
├── app.py                           # Streamlit entry point
├── utils.py                         # Shared data loader + styles
├── report.py                        # ReportLab PDF generator
├── bank_churn_final.csv             # Cleaned dataset
├── bank_churn.db                    # SQLite database
│
└── pages/
├───────── overview.py               # KPIs + churn distribution
├───────── demographics.py           # Age, gender, geography
├───────── financial.py              # Balance, products, credit score
├───────── sql_insights.py           # SQL business questions
└───────── report.py                 # Full report with plots + PDF
```
---

## Tech Stack

| Phase | Tool |
|---|---|
| Data Preparation | Python, Pandas, NumPy |
| Data Analysis | SQL (SQLite) |
| Visualization | Plotly |
| Dashboard | Streamlit |
| PDF Report | ReportLab, Kaleido |

---

## Workflow

### Phase 1 — Python EDA
- Loaded Kaggle Bank Churn dataset (10,000 rows, 18 features)
- Cleaned and standardized column names
- Engineered features:
  - `age_group` — binned age brackets
  - `credit_bracket` — credit score tiers
  - `tenure_bucket` — customer tenure segments
  - `balance_salary_ratio` — financial health indicator
  - `value_score` — composite customer value (balance + salary)
  - `high_value_churned` — flag for high-value lost customers

### Phase 2 — SQL Analysis (SQLite)
Answered 8 business questions:
1. Overall churn rate
2. Churn by geography
3. Churn by gender & geography
4. Churn by number of products
5. High-value at-risk customers
6. Churn by tenure bucket
7. Avg balance & salary by churn status
8. Churn by satisfaction score

### Phase 3 — Streamlit Dashboard
5-page interactive app:
- **Overview** — KPI cards, churn distribution, card type, satisfaction
- **Demographics** — age group, gender, geography heatmap, age histogram
- **Financial** — balance, products, credit score, activity, scatter plot
- **SQL Insights** — all business questions visualized + at-risk table
- **Report** — full written report with plots + PDF download

### Phase 4 — PDF Report
- Generated with ReportLab + Kaleido
- Includes all charts, tables, findings, and recommendations
- Downloadable directly from the Streamlit app

---

## Key Findings

| Finding | Insight |
|---|---|
| Overall Churn Rate | 20.38% |
| Highest Churn Geography | Germany (~32%) |
| Worst Product Count | 3-4 products (>80% churn) |
| Most At-Risk Age Group | 41-50 years |
| Inactive Member Churn | Significantly higher than active |
| High-Value Churned | 592 customers lost |

---

## Business Recommendations

1. **Target Germany** with dedicated retention campaigns and loyalty rewards
2. **Re-engage inactive members** via personalized email/app campaigns
3. **Audit multi-product strategy** — over-selling drives churn
4. **Early warning system** using `value_score` to flag at-risk customers
5. **Premium offerings** tailored to the 41-50 age segment

---

## How to Run

1. Clone the repo
```bash
git clone https://github.com/yourusername/bank-churn-analysis.git
cd bank-churn-analysis
```

2. Install dependencies
```bash
pip install streamlit pandas numpy plotly reportlab kaleido sqlite3
```

3. Download the dataset
Get `Customer-Churn-Records.csv` from [Kaggle](https://www.kaggle.com/datasets/radheshyamkollipara/bank-customer-churn) and place it in the project root.

4. Run the Colab notebook
Open `Bank_Churn_Analysis.ipynb` in Google Colab and run all cells to generate:
- `bank_churn_final.csv`
- `bank_churn.db`

5. Launch the app
```bash
streamlit run app.py
```

6. Generate PDF Report
```bash
python generate_report.py
```

---

## 📜 License

MIT — free to fork, star, and use in your portfolio.

---

## 🙌 Acknowledgements

- Dataset: [Kaggle — Bank Customer Churn](https://www.kaggle.com/datasets/radheshyamkollipara/bank-customer-churn)
- Project structure inspired by [Amlan Mohanty](https://github.com/amlanmohanty1/customer-trends-data-analysis-SQL-Python-PowerBI)
