from flask import render_template, current_app
from app.email import send_email

def send_password_reset_email(user):
    expires_in = 600
    token = user.get_reset_password_token(expires_in)
    expires_in_minutes = expires_in // 60
    send_email('[Projet] Reset your password',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token,
                                         expires_in=expires_in_minutes),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token,
                                         expires_in=expires_in_minutes))