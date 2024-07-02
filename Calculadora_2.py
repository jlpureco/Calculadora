# -*- coding: utf-8 -*-
"""
Created on Sun Jun 30 16:49:51 2024

@author: jlpur
"""

import streamlit as st
import pandas as pd
import numpy as np
import base64
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime
import locale
import json
import os
from pathlib import Path

locale.setlocale(locale.LC_ALL, '')

USUARIOS_FILE = "Datos/usuarios.json"

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

def load_users():
    if os.path.exists(USUARIOS_FILE):
        with open(USUARIOS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USUARIOS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def check_password(username, password):
    users = load_users()
    if username in users and users[username]['password'] == password:
        return users[username]
    return None

def add_user(username, password, user_type, nombre, telefono):
    users = load_users()
    if username not in users:
        users[username] = {
            "password": password,
            "type": user_type,
            "nombre": nombre,
            "telefono": telefono
        }
        save_users(users)
        return True
    return False

def login():
    st.title("Iniciar Sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        user = check_password(username, password)
        if user:
            st.session_state['logged_in'] = True
            st.session_state['user'] = user
            st.success("¡Sesión iniciada exitosamente!")
            st.experimental_rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

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
            'Mes': int(month),  # Asegurarse de que el mes sea un entero
            'Capital': f"{monthly_principal:,.2f}",
            'Interés': f"{monthly_interest:,.2f}",
            'IVA': f"{monthly_iva:,.2f}",
            'Pago Total': f"{total_payment:,.2f}",
            'Saldo Restante': f"{remaining_balance:,.2f}"
        })

    return pd.DataFrame(schedule)

def get_table_download_link(df, filename, file_label, principal, monthly_rate, months):
    fecha_cotizacion = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    header_info = f"Monto del Préstamo: ${principal:,.2f}\n" \
                  f"Tasa de Interés Mensual: {monthly_rate:.2f}%\n" \
                  f"Plazo: {months} meses\n" \
                  f"Fecha de Cotización: {fecha_cotizacion}\n\n"

    if file_label == 'CSV':
        csv = header_info + df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">Descargar archivo CSV</a>'
    elif file_label == 'PDF':
        pdf = generate_pdf(df, header_info)
        b64 = base64.b64encode(pdf).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}.pdf">Descargar archivo PDF</a>'
    return href


def generate_pdf(df, header_info):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Add header
    styles = getSampleStyleSheet()
    header_para = Paragraph(header_info.replace('\n', '<br/>'), styles['Normal'])
    elements.append(header_para)

    # Add table
    data = [df.columns.tolist()] + df.values.tolist()
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(t)
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def main_app():
    st.title('Calculadora de Préstamos')

    user = st.session_state['user']
    st.write(f"Bienvenido, {user['nombre']} ({user['type']})")
    st.write(f"Teléfono de contacto: {user['telefono']}")
    
    principal = st.number_input('Monto del Préstamo', min_value=1000, value=100000)
    monthly_rate = st.number_input('Tasa de Interés Mensual (%)', min_value=0.01, max_value=10.0, value=0.5, step=0.01)

    scenarios = [3, 6, 12, 18, 24, 30, 36, 48, 60]

    if st.button('Calcular Todos los Escenarios'):
        for months in scenarios:
            st.header(f'Escenario a {months} Meses')
            
            schedule = generate_payment_schedule(principal, monthly_rate, months)
            
            st.write(f'Pago Mensual de Capital: ${schedule["Capital"].iloc[0]}')
            st.write(f'Pago Mensual de Interés: ${schedule["Interés"].iloc[0]}')
            st.write(f'IVA Mensual: ${schedule["IVA"].iloc[0]}')
            st.write(f'Pago Mensual Total: ${schedule["Pago Total"].iloc[0]}')
            
            st.dataframe(schedule)
            
            total_principal = sum(float(x.replace(',', '')) for x in schedule['Capital'])
            total_interest = sum(float(x.replace(',', '')) for x in schedule['Interés'])
            total_iva = sum(float(x.replace(',', '')) for x in schedule['IVA'])
            total_payments = sum(float(x.replace(',', '')) for x in schedule['Pago Total'])
            
            st.write(f'Total de Capital Pagado: ${total_principal:,.2f}')
            st.write(f'Total de Interés Pagado: ${total_interest:,.2f}')
            st.write(f'Total de IVA Pagado: ${total_iva:,.2f}')
            st.write(f'Monto Total Pagado: ${total_payments:,.2f}')
            
            st.markdown(get_table_download_link(schedule, f'calendario_pagos_{months}meses', 'CSV', principal, monthly_rate, months), unsafe_allow_html=True)
            st.markdown(get_table_download_link(schedule, f'calendario_pagos_{months}meses', 'PDF', principal, monthly_rate, months), unsafe_allow_html=True)
            
            st.divider()  # Add a divider between scenarios



    if user['type'] == 'administrador':
        if st.button("Agregar nuevo usuario"):
            add_new_user()


def add_new_user():
    st.subheader("Agregar nuevo usuario")
    new_username = st.text_input("Nuevo usuario")
    new_password = st.text_input("Nueva contraseña", type="password")
    user_type = st.selectbox("Tipo de usuario", ["vendedor", "administrador"])
    nombre = st.text_input("Nombre completo")
    telefono = st.text_input("Teléfono de contacto")
    
    if st.button("Guardar nuevo usuario"):
        if add_user(new_username, new_password, user_type, nombre, telefono):
            st.success("Usuario agregado exitosamente")
        else:
            st.error("El nombre de usuario ya existe")

# Main app logic
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    login()
else:
    main_app()
    if st.button("Cerrar Sesión"):
        st.session_state['logged_in'] = False
        st.session_state.pop('user', None)
        st.experimental_rerun()

# Inicializar usuarios si el archivo no existe
if not os.path.exists(USUARIOS_FILE):
    initial_users = {
        "Andres.Lira": {
            "password": "admin01",
            "type": "administrador",
            "nombre": "Andrés Lira",
            "telefono": "1234567890"
        },
        "Nadia.Lira": {
            "password": "admin01",
            "type": "administrador",
            "nombre": "Nadia Lira",
            "telefono": "0987654321"
        }
    }
    save_users(initial_users)
