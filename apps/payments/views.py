import json
import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages

from apps.orders.models import Order
from apps.payments.models import PaymentTransaction
from .mpesa import MpesaAPI
from .forms import MpesaPaymentForm

logger = logging.getLogger(__name__)


def mpesa_payment(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    if order.payment_status == 'completed':
        messages.info(request, f'Order {order.order_number} is already paid.')
        return redirect('orders:order_success', order_id=order.id)

    if request.method == 'POST':
        form = MpesaPaymentForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            client = MpesaAPI()

            try:
                result = client.stk_push(
                    phone_number=phone,
                    amount=int(order.total),
                    account_reference=order.order_number,
                    transaction_desc=f'Payment for {order.order_number}',
                )

                # ── Log the full result so we can see exactly what Daraja returned ──
                logger.info('STK Push result for order %s: %s', order.order_number, result)
                print('STK PUSH RESULT:', result)  # prints to Django terminal

                # Daraja sandbox returns ResponseCode '0' on success
                # Your MpesaAPI wraps it — check both possible response formats
                if result.get('success') or result.get('ResponseCode') == '0':
                    checkout_request_id = result.get(
                        'checkout_request_id',
                        result.get('CheckoutRequestID', '')
                    )
                    order.checkout_request_id = checkout_request_id
                    order.payment_method = 'mpesa'
                    order.save()

                    PaymentTransaction.objects.create(
                        order=order,
                        transaction_id=checkout_request_id,
                        amount=order.total,
                        phone_number=phone,
                        status='pending',
                    )
                    messages.success(
                        request,
                        'STK Push sent! Check your phone and enter your M-Pesa PIN.'
                    )
                    return render(request, 'payments/waiting.html', {'order': order})

                else:
                    # Show the actual error from Daraja
                    error_msg = (
                        result.get('message') or
                        result.get('errorMessage') or
                        result.get('ResultDesc') or
                        str(result)
                    )
                    logger.error('STK Push failed: %s', error_msg)
                    messages.error(request, f'M-Pesa error: {error_msg}')

            except Exception as e:
                logger.exception('STK Push exception for order %s', order_id)
                messages.error(request, f'Connection error: {str(e)}')

    else:
        form = MpesaPaymentForm(initial={'phone': order.phone})

    return render(request, 'payments/mpesa_payment.html', {
        'order': order,
        'form': form
    })


@csrf_exempt
@require_POST
def mpesa_callback(request):
    try:
        data = json.loads(request.body)
        callback = data['Body']['stkCallback']
        checkout_request_id = callback.get('CheckoutRequestID')
        result_code = callback.get('ResultCode')

        order = Order.objects.filter(checkout_request_id=checkout_request_id).first()
        if not order:
            logger.warning('No order for CheckoutRequestID: %s', checkout_request_id)
            return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})

        if result_code == 0:
            metadata = callback.get('CallbackMetadata', {}).get('Item', [])
            mpesa_code = next(
                (item['Value'] for item in metadata if item['Name'] == 'MpesaReceiptNumber'),
                '',
            )
            order.status = 'paid'
            order.payment_status = 'completed'
            order.mpesa_code = mpesa_code
            order.paid_at = timezone.now()
            order.save()
            PaymentTransaction.objects.filter(order=order).update(status='completed')
        else:
            order.payment_status = 'failed'
            order.save()
            PaymentTransaction.objects.filter(order=order).update(status='failed')

    except Exception as e:
        logger.error('M-Pesa callback error: %s', e)

    return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})


def payment_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'payments/payment_success.html', {'order': order})
