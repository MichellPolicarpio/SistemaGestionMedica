# 📧 Email Configuration
# Configure your email settings here

# Real Email Configuration (Gmail with regular password)
EMAIL_CONFIG = {
    'smtp_server': 'smtp-mail.outlook.com',
    'smtp_port': 465,
    'sender_email': 'samuelfernandomoraocampo@outlook.com',  # Your Outlook
    'sender_password': 'ortsbntilbomdmrm',  # Your app password
    'use_tls': False,
    'use_ssl': True
}

# Alternative: Use Outlook/Hotmail (Easier setup)
# EMAIL_CONFIG = {
#     'smtp_server': 'smtp-mail.outlook.com',
#     'smtp_port': 587,
#     'sender_email': 'your-email@outlook.com',
#     'sender_password': 'your-password',
#     'use_tls': True
# }

# Alternative: Use Yahoo
# EMAIL_CONFIG = {
#     'smtp_server': 'smtp.mail.yahoo.com',
#     'smtp_port': 587,
#     'sender_email': 'your-email@yahoo.com',
#     'sender_password': 'your-password',
#     'use_tls': True
# }

# Alternative: Use a custom SMTP server
# EMAIL_CONFIG = {
#     'smtp_server': 'your-smtp-server.com',
#     'smtp_port': 587,
#     'sender_email': 'your-email@your-domain.com',
#     'sender_password': 'your-password',
#     'use_tls': True
# } 