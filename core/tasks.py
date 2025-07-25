import requests
from celery import shared_task
from decimal import Decimal
from .models import ExchangeRate, Newsletter, NewsletterSubscriber, NewsletterDelivery
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

@shared_task
def update_currency_rates():
    print("Updating currency rates...")
    try:
        response = requests.get("https://open.er-api.com/v6/latest/KES")
        data = response.json()
        if data.get("result") == "success":
            rates = data.get("rates", {})
            for code, rate in rates.items():
                if code == "KES":
                    continue  
                ExchangeRate.objects.update_or_create(
                    target_currency=code,
                    defaults={"kes_to_currency": Decimal(rate)}
                )
            print("Currency rates updated successfully.")
        else:
            print("Failed to fetch currency rates.")
    except Exception as e:
        print("Error while updating currency rates:", e)


@shared_task
def send_newsletter_task(newsletter_id):
    try: 
        newsletter = Newsletter.objects.get(id=newsletter_id)

    except Newsletter.DoesNotExist:
        return
    
    subscribers = NewsletterSubscriber.objects.all()

    for subscriber in subscribers:
        html_content = newsletter.content
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject=newsletter.title,
            body=text_content,
            from_email=settings.EMAIL_HOST_USER,
            to=[subscriber.email],
        )

        email.attach_alternative(html_content, "text/html")
        email.send()

        NewsletterDelivery.objects.create(
            subscriber=subscriber,
            newsletter=newsletter
        )

    return f"Sent newsletter: '{newsletter.title}' to {subscribers.count()} subscribers."