from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import Order


@receiver(post_save, sender=Order)
def notify_staff_on_new_order(sender, instance, created, **kwargs):
    """Notun order create hole staff + Moderator group er shobar email e notification jay."""
    if not created:
        return

    User = get_user_model()
    recipient_emails = list(
        User.objects.filter(
            Q(is_staff=True) | Q(groups__name='Moderator')
        ).exclude(email='').values_list('email', flat=True).distinct()
    )

    if not recipient_emails:
        return

    subject = f"New order received — {instance.order_number}"
    message = (
        f"A new order has been placed.\n\n"
        f"Order number: {instance.order_number}\n"
        f"Customer: {instance.full_name} ({instance.phone})\n"
        f"Total: \u09f3{instance.total}\n"
        f"Payment method: {instance.get_payment_method_display()}\n\n"
        f"View it in the dashboard to confirm and process."
    )

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_emails,
            fail_silently=True,
        )
    except Exception:
        # Email backend na thakle o order creation fail kora uchit na
        pass
