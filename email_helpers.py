# email_helpers.py

import smtplib
from email.message import EmailMessage


def send_mail(**kwargs):
    required = ['from_email', 'to', 'subject', 'body', 'config']
    for field in required:
        if field not in kwargs:
            return False, f"{field} is mandatory"

    required_config = ['mail_host', 'mail_port', 'username', 'password']
    for field in required_config:
        if field not in kwargs.get('config'):
            return False, f"{field} is mandatory configuration field"

    msg = EmailMessage()
    msg['Subject'] = kwargs.get('subject')
    msg['From'] = kwargs.get('from_email')
    msg['To'] = kwargs.get('to')

    msg.set_content(kwargs.get('body'))

    if kwargs.get('config').get('mail_port') == 465:
        with smtplib.SMTP_SSL(kwargs.get('config').get('mail_host'), kwargs.get('config').get('mail_port')) as smtp:
            smtp.login(kwargs.get('config').get('username'), kwargs.get('config').get('password'))
            smtp.send_message(msg)
    elif kwargs.get('config').get('mail_port') == 587:
        with smtplib.SMTP(kwargs.get('config').get('mail_host'), kwargs.get('config').get('mail_port')) as smtp:
            smtp.starttls()
            smtp.login(kwargs.get('config').get('username'), kwargs.get('config').get('password'))
            smtp.send_message(msg)
