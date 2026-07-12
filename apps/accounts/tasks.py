from django.core.mail import EmailMultiAlternatives

from config.celery import app


@app.task(name="task_send_email")
def task_send_email(subject, message, recipients):
    return EmailMultiAlternatives(subject=subject, body=message, to=[recipients]).send()
