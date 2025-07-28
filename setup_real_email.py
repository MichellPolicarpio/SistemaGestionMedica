#!/usr/bin/env python3
"""
Script para configurar envío real de emails
"""

import os
import sys

def print_banner():
    print("=" * 60)
    print("📧 CONFIGURACIÓN DE EMAIL REAL")
    print("=" * 60)
    print()

def get_email_provider():
    print("¿Qué proveedor de email quieres usar?")
    print("1. Gmail (Recomendado)")
    print("2. Outlook/Hotmail")
    print("3. Yahoo")
    print("4. Cancelar")
    
    while True:
        choice = input("\nSelecciona una opción (1-4): ").strip()
        if choice in ['1', '2', '3', '4']:
            return choice
        print("❌ Opción inválida. Intenta de nuevo.")

def get_gmail_config():
    print("\n📧 CONFIGURACIÓN GMAIL")
    print("-" * 30)
    print("Para Gmail necesitas:")
    print("1. Una cuenta Gmail")
    print("2. Verificación en 2 pasos activada")
    print("3. Una contraseña de aplicación")
    print()
    
    email = input("Ingresa tu email Gmail: ").strip()
    if not email or '@gmail.com' not in email:
        print("❌ Debe ser un email Gmail válido")
        return None
    
    password = input("Ingresa tu contraseña de aplicación (16 caracteres): ").strip()
    if len(password) != 16:
        print("❌ La contraseña de aplicación debe tener 16 caracteres")
        return None
    
    return {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'sender_email': email,
        'sender_password': password,
        'use_tls': True
    }

def get_outlook_config():
    print("\n📧 CONFIGURACIÓN OUTLOOK/HOTMAIL")
    print("-" * 35)
    print("Para Outlook/Hotmail usa tu cuenta existente")
    print()
    
    email = input("Ingresa tu email Outlook/Hotmail: ").strip()
    if not email or '@outlook.com' not in email and '@hotmail.com' not in email:
        print("❌ Debe ser un email Outlook/Hotmail válido")
        return None
    
    password = input("Ingresa tu contraseña: ").strip()
    if not password:
        print("❌ La contraseña no puede estar vacía")
        return None
    
    return {
        'smtp_server': 'smtp-mail.outlook.com',
        'smtp_port': 587,
        'sender_email': email,
        'sender_password': password,
        'use_tls': True
    }

def get_yahoo_config():
    print("\n📧 CONFIGURACIÓN YAHOO")
    print("-" * 25)
    print("Para Yahoo usa tu cuenta existente")
    print()
    
    email = input("Ingresa tu email Yahoo: ").strip()
    if not email or '@yahoo.com' not in email:
        print("❌ Debe ser un email Yahoo válido")
        return None
    
    password = input("Ingresa tu contraseña: ").strip()
    if not password:
        print("❌ La contraseña no puede estar vacía")
        return None
    
    return {
        'smtp_server': 'smtp.mail.yahoo.com',
        'smtp_port': 587,
        'sender_email': email,
        'sender_password': password,
        'use_tls': True
    }

def write_config(config):
    config_content = f'''# 📧 Email Configuration
# Configure your email settings here

# Real Email Configuration
EMAIL_CONFIG = {{
    'smtp_server': '{config['smtp_server']}',
    'smtp_port': {config['smtp_port']},
    'sender_email': '{config['sender_email']}',
    'sender_password': '{config['sender_password']}',
    'use_tls': {config['use_tls']}
}}

# Alternative configurations (commented out)
# EMAIL_CONFIG = {{
#     'smtp_server': 'smtp-mail.outlook.com',
#     'smtp_port': 587,
#     'sender_email': 'your-email@outlook.com',
#     'sender_password': 'your-password',
#     'use_tls': True
# }}
'''
    
    try:
        with open('email_config.py', 'w') as f:
            f.write(config_content)
        print("✅ Configuración guardada en email_config.py")
        return True
    except Exception as e:
        print(f"❌ Error guardando configuración: {e}")
        return False

def show_instructions():
    print("\n📋 INSTRUCCIONES ADICIONALES")
    print("-" * 35)
    print("Para Gmail:")
    print("1. Ve a https://accounts.google.com")
    print("2. Seguridad → Verificación en 2 pasos")
    print("3. Activa la verificación en 2 pasos")
    print("4. Seguridad → Contraseñas de aplicación")
    print("5. Selecciona 'Otra' → 'Sistema Pacientes'")
    print("6. Copia la contraseña de 16 caracteres")
    print()
    print("Para Outlook/Hotmail:")
    print("1. Usa tu contraseña normal")
    print("2. No necesitas configuración adicional")
    print()

def main():
    print_banner()
    
    choice = get_email_provider()
    
    if choice == '4':
        print("❌ Configuración cancelada")
        return
    
    config = None
    
    if choice == '1':
        config = get_gmail_config()
        if config:
            show_instructions()
    elif choice == '2':
        config = get_outlook_config()
    elif choice == '3':
        config = get_yahoo_config()
    
    if config:
        if write_config(config):
            print("\n🎉 ¡Configuración completada!")
            print("Ahora puedes enviar emails reales.")
            print("\nPara probar:")
            print("1. Reinicia la aplicación: python3 app.py")
            print("2. Ve a http://localhost:5001")
            print("3. Selecciona un paciente")
            print("4. Haz clic en 'Email Report'")
            print("5. Ingresa tu email personal")
            print("6. ¡Revisa tu bandeja de entrada!")
        else:
            print("❌ Error en la configuración")
    else:
        print("❌ Configuración incompleta")

if __name__ == "__main__":
    main() 