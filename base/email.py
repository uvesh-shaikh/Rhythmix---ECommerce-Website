from django.conf import settings
from django.core.mail import send_mail

def sent_account_activation_mail(email, email_token):
    subject = "Activate your account"
    message = f"your activation token is http://127.0.0.1:8000/accounts/activate/{email_token}"
    email_from = settings.EMAIL_HOST_USER
    send_mail(subject, message, email_from, [email])
