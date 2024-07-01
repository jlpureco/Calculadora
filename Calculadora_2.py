# -*- coding: utf-8 -*-
"""
Created on Sun Jun 30 16:49:51 2024

@author: jlpur
"""
import streamlit as st
import pandas as pd
import numpy as np
import base64
import hashlib

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

def check_password(username, password):
    # This is a simple example. In a real application, you'd check against a database
    # and use proper password hashing.
    correct_username = "admin"
    correct_password = "password123"
    return username == correct_username and password == correct_password

def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if check_password(username, password):
            st.session_state['logged_in'] = True
            st.success("Logged in successfully!")
        else:
            st.error("Incorrect username or password")

def generate_payment_schedule(principal, monthly_rate, months):
    # ... (rest of the function remains the same)

def get_table_download_link(df, filename):
    # ... (rest of the function remains the same)

def main_app():
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

# Main app logic
if not st.session_state['logged_in']:
    login()
else:
    main_app()
    if st.button("Logout"):
        st.session_state['logged_in'] = False
        st.experimental_rerun()
