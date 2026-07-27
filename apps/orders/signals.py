# apps/orders/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from apps.orders.models import Order
import logging

logger = logging.getLogger(__name__)

def send_order_confirmation_email(order):
    """Send order confirmation email"""
    try:
        subject = f"Order Confirmation - {order.order_number}"
        
        # HTML email
        html_message = render_to_string('emails/order_confirmation_html.html', {
            'order': order,
            'items': order.items.all(),
            'total': order.total,
            'order_number': order.order_number
        })
        
        # Plain text email
        plain_message = render_to_string('emails/order_confirmation.txt', {
            'order': order,
            'items': order.items.all(),
            'total': order.total,
            'order_number': order.order_number
        })
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Order confirmation email sent to {order.email} for order {order.order_number}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to send order confirmation email: {str(e)}")
        return False

@receiver(post_save, sender=Order)
def order_status_updated(sender, instance, created, **kwargs):
    """Send email when order status changes to paid"""
    if not created and instance.status == 'paid':
        if instance.payment_status == 'completed':
            send_order_confirmation_email(instance)
    
    # Send shipping confirmation
    if not created and instance.status == 'shipped':
        try:
            subject = f"Order Shipped - {instance.order_number}"
            html_message = render_to_string('emails/order_shipped.html', {
                'order': instance,
                'order_number': instance.order_number
            })
            
            send_mail(
                subject=subject,
                message=f"Your order {instance.order_number} has been shipped.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Failed to send shipping email: {str(e)}")