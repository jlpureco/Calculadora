# -*- coding: utf-8 -*-
"""
Created on Sun Jun 30 16:49:51 2024

@author: jlpur
"""
import streamlit as st
import pandas as pd
import numpy as np
import base64

def generate_payment_schedule(principal, monthly_rate, months):
    monthly_interest = principal * monthly_rate / 100
    monthly_iva = monthly_interest * 0.16
    monthly_principal = principal / months
    
    schedule = []
    remaining_balance = principal
    
    for month in range(1, months + 1):
        if month == months:  # Last payment
            monthly_principal = remaining_balance
        
        total_payment = monthly_principal + monthly_interest + monthly_iva
        remaining_balance -= monthly_principal
        
        if remaining_balance < 0:
            remaining_balance = 0
        
        schedule.append({
            'Month': month,
            'Principal': monthly_principal,
            'Interest': monthly_interest,
            'IVA': monthly_iva,
            'Total Payment': total_payment,
            'Remaining Balance': remaining_balance
        })
    
    return pd.DataFrame(schedule)

def get_table_download_link(df, filename):
    csv = df.to_csv(index=False, float_format='%.2f')
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV file</a>'
    return href

st.title('Loan Payment Calculator')

principal = st.number_input('Loan Amount', min_value=1000, value=100000)
monthly_rate = st.number_input('Monthly Interest Rate (%)', min_value=0.01, max_value=10.0, value=0.5, step=0.01)

scenarios = [3, 6, 12, 18, 24, 30, 36]

if st.button('Calculate All Scenarios'):
    for months in scenarios:
        st.header(f'{months} Month Scenario')
        
        schedule = generate_payment_schedule(principal, monthly_rate, months)
        
        st.write(f'Monthly Principal Payment: ${schedule["Principal"].iloc[0]:.2f}')
        st.write(f'Monthly Interest Payment: ${schedule["Interest"].iloc[0]:.2f}')
        st.write(f'Monthly IVA: ${schedule["IVA"].iloc[0]:.2f}')
        st.write(f'Monthly Total Payment: ${schedule["Total Payment"].iloc[0]:.2f}')
        
        st.dataframe(schedule.style.format({
            'Principal': '${:.2f}',
            'Interest': '${:.2f}',
            'IVA': '${:.2f}',
            'Total Payment': '${:.2f}',
            'Remaining Balance': '${:.2f}'
        }))
        
        total_principal = schedule['Principal'].sum()
        total_interest = schedule['Interest'].sum()
        total_iva = schedule['IVA'].sum()
        total_payments = schedule['Total Payment'].sum()
        
        st.write(f'Total Principal Paid: ${total_principal:.2f}')
        st.write(f'Total Interest Paid: ${total_interest:.2f}')
        st.write(f'Total IVA Paid: ${total_iva:.2f}')
        st.write(f'Total Amount Paid: ${total_payments:.2f}')
        
        st.markdown(get_table_download_link(schedule, f'loan_schedule_{months}months.csv'), unsafe_allow_html=True)
        
        st.divider()  # Add a divider between scenarios