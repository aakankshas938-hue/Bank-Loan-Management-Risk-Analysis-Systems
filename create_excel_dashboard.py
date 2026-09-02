import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import numpy as np

# ==========================================
# 1. Page Configuration
# ==========================================
st.set_page_config(page_title="Bank Loan Dashboard", layout="wide", page_icon="🏦")

# ==========================================
# 2. Database Connection & Data Fetching
# ==========================================
@st.cache_data
def load_data():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="BankLoanDB"
        )
        cursor = db.cursor()
        
        query = """
            SELECT c.name, c.city, c.annual_income, l.loan_amount, l.interest_rate, 
                   l.tenure_months, cp.cibil_score, ld.emi, ld.risk_category, ld.status
            FROM Customer c
            JOIN Loan l ON c.customer_id = l.customer_id
            JOIN CreditProfile cp ON c.customer_id = cp.customer_id
            JOIN LoanDecision ld ON l.loan_id = ld.loan_id;
        """
        
        cursor.execute(query)
        data = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(data, columns=columns)
        db.close()
        
        # SMART TRICK: Kaggle CSV मधून Education आणि Employment जोडणे
        df_csv = pd.read_csv("loan_approval_dataset.csv")
        df_csv.columns = df_csv.columns.str.strip()
        df['education'] = df_csv['education'].str.strip()
        df['self_employed'] = df_csv['self_employed'].str.strip()
        
        return df
        
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("No data found.")
    st.stop()

# Data Preprocessing for Charts
df['cibil_score'] = pd.to_numeric(df['cibil_score'])
df['annual_income'] = pd.to_numeric(df['annual_income'])
df['loan_amount'] = pd.to_numeric(df['loan_amount'])

# ==========================================
# 3. Dashboard Title & Filters (Sidebar)
# ==========================================
st.title("🏦 Loan Approval & Risk Analysis Dashboard")
st.markdown("---")

st.sidebar.header("🔍 Filters")
status_filter = st.sidebar.multiselect("Loan Status", options=df['status'].unique(), default=df['status'].unique())
edu_filter = st.sidebar.multiselect("Education", options=df['education'].unique(), default=df['education'].unique())
emp_filter = st.sidebar.multiselect("Employment", options=df['self_employed'].unique(), default=df['self_employed'].unique())

# Apply Filters
filtered_df = df[(df['status'].isin(status_filter)) & 
                 (df['education'].isin(edu_filter)) & 
                 (df['self_employed'].isin(emp_filter))]

# ==========================================
# 4. KPI Cards (Top Row)
# ==========================================
col1, col2, col3, col4, col5 = st.columns(5)

total_apps = len(filtered_df)
approved = len(filtered_df[filtered_df['status'] == 'Approved'])
rejected = len(filtered_df[filtered_df['status'] == 'Rejected'])
approval_rate = (approved / total_apps) * 100 if total_apps > 0 else 0
avg_cibil = filtered_df['cibil_score'].mean()

col1.metric("Total Loans", total_apps)
col2.metric("Approved", approved)
col3.metric("Rejected", rejected)
col4.metric("Approval Rate", f"{approval_rate:.2f}%")
col5.metric("Avg CIBIL", f"{avg_cibil:.0f}")

st.markdown("---")

# ==========================================
# 5. Charts (Row 1: CIBIL & Status)
# ==========================================
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("Approval Rate by CIBIL Score")
    # Creating CIBIL Bins
    bins = [300, 500, 650, 750, 900]
    labels = ['300-500', '500-650', '650-750', '750+']
    temp_df = filtered_df.copy()
    temp_df['CIBIL_Range'] = pd.cut(temp_df['cibil_score'], bins=bins, labels=labels)
    cibil_group = temp_df.groupby('CIBIL_Range')['status'].apply(lambda x: (x=='Approved').mean() * 100).reset_index()
    cibil_group.columns = ['CIBIL Range', 'Approval Rate (%)']
    
    fig_cibil = px.bar(cibil_group, x='CIBIL Range', y='Approval Rate (%)', 
                       text='Approval Rate (%)', color='Approval Rate (%)',
                       color_continuous_scale='Greens')
    fig_cibil.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    st.plotly_chart(fig_cibil, use_container_width=True)

with row1_col2:
    st.subheader("Loan Status Distribution")
    status_counts = filtered_df['status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    fig_pie = px.pie(status_counts, values='Count', names='Status', hole=0.4, color='Status',
                     color_discrete_map={'Approved':'#28a745', 'Rejected':'#dc3545', 'Pending Review':'#ffc107'})
    st.plotly_chart(fig_pie, use_container_width=True)

# ==========================================
# 6. Charts (Row 2: Financial & Segmentation)
# ==========================================
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("Income vs Loan Amount")
    fig_scatter = px.scatter(filtered_df, x='annual_income', y='loan_amount', color='status',
                            hover_data=['cibil_score', 'name'],
                            color_discrete_map={'Approved':'#28a745', 'Rejected':'#dc3545', 'Pending Review':'#ffc107'})
    st.plotly_chart(fig_scatter, use_container_width=True)

with row2_col2:
    st.subheader("Education & Employment vs Approval")
    # Grouping Education and Employment
    edu_emp_group = filtered_df.groupby(['education', 'self_employed'])['status'].apply(
        lambda x: (x=='Approved').count()).reset_index()
    edu_emp_group.columns = ['Education', 'Self Employed', 'Total Applications']
    
    fig_edu = px.bar(edu_emp_group, x='Education', y='Total Applications', color='Self Employed',
                    barmode='group', color_discrete_sequence=['#007bff', '#17a2b8'])
    st.plotly_chart(fig_edu, use_container_width=True)

# ==========================================
# 7. Bonus Chart (Row 3: CIBIL Distribution)
# ==========================================
st.markdown("---")
st.subheader("CIBIL Score Distribution by Loan Status")
fig_box = px.box(filtered_df, x='status', y='cibil_score', color='status',
                 color_discrete_map={'Approved':'#28a745', 'Rejected':'#dc3545', 'Pending Review':'#ffc107'})
st.plotly_chart(fig_box, use_container_width=True)

#
# 7. Raw Data Table (Bottom)
st.markdown("---")
st.subheader("Detailed Applicant Data")
st.dataframe (filtered_df, use_container_width=True)