# signals.py

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from .models import Inquiry

# Store previous state before saving
@receiver(pre_save, sender=Inquiry)
def capture_old_inquiry(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old = Inquiry.objects.get(pk=instance.pk)
        except Inquiry.DoesNotExist:
            instance._old = None
    else:
        instance._old = None


# Handle response sending after saving
@receiver(post_save, sender=Inquiry)
def send_admin_response_email(sender, instance, created, **kwargs):
    if created:
        return  # Skip for new inquiries

    # Get old version from pre_save
    old_instance = getattr(instance, '_old', None)

    if not old_instance:
        return  # Can't compare if no old data

    print(f"[DEBUG] Old response: '{old_instance.response}'")
    print(f"[DEBUG] New response: '{instance.response}'")
    print(f"[DEBUG] Has changed: {old_instance.response != instance.response}")

    # Only proceed if response was added or changed
    if not instance.response:
        return  # No response yet

    if old_instance.response == instance.response:
        return  # No change in response

    print("...........................................................................................................")

    # At this point, we know the admin has added or updated the response

    # Prepare email context
    client_name = instance.name or "Client"
    property_title = instance.property.title if instance.property else "your inquiry"

    context = {
        'client_name': client_name,
        'property_title': property_title,
        'response': instance.response,
        'company_name': "Seven Flags Real Estate",
        'logo_url': staticfiles_storage.url('images/logo.png')
    }

    # Render content
    html_content = render_to_string('core/emails/inquiry_response.html', context)
    text_content = f"""Dear {client_name},

Thank you for your inquiry about {property_title}.

Our Response:
{instance.response}

Best regards,
Seven Flags Team"""

    # Send email
    email = EmailMultiAlternatives(
        subject=f"Re: Your Inquiry About {property_title}",
        body=text_content,
        from_email=settings.EMAIL_HOST_USER,
        to=[instance.email],
        reply_to=[settings.EMAIL_HOST_USER]
    )
    email.attach_alternative(html_content, "text/html")
    email.send()

    # Update responded flag without triggering signal
    Inquiry.objects.filter(pk=instance.pk).update(responded=True)