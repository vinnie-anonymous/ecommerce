# apps/payments/mpesa.py

import requests
import base64
from datetime import datetime
from django.conf import settings
from django.core.cache import cache
from apps.orders.models import Order
import logging

logger = logging.getLogger(__name__)

class MpesaAPI:
    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.passkey = settings.MPESA_PASSKEY
        self.shortcode = settings.MPESA_SHORTCODE
        self.environment = settings.MPESA_ENVIRONMENT
        
        if self.environment == 'sandbox':
            self.base_url = 'https://sandbox.safaricom.co.ke'
        else:
            self.base_url = 'https://api.safaricom.co.ke'
        
        self.access_token = None
        self.token_expiry = None
    
    def get_access_token(self):
        """Get OAuth access token from M-PESA"""
        # Check cache first
        token = cache.get('mpesa_access_token')
        if token:
            return token
        
        try:
            auth = base64.b64encode(f"{self.consumer_key}:{self.consumer_secret}".encode()).decode()
            
            response = requests.get(
                f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials",
                headers={
                    'Authorization': f'Basic {auth}',
                    'Content-Type': 'application/json'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                if token:
                    # Cache token for 3500 seconds (less than 1 hour expiry)
                    cache.set('mpesa_access_token', token, 3500)
                    return token
            
            logger.error(f"Failed to get M-PESA token: {response.text}")
            return None
        
        except Exception as e:
            logger.error(f"Error getting M-PESA token: {str(e)}")
            return None
    
    def stk_push(self, phone_number, amount, account_reference, transaction_desc):
        """
        Initiate STK Push payment
        """
        access_token = self.get_access_token()
        if not access_token:
            return {
                'success': False,
                'message': 'Failed to authenticate with M-PESA'
            }
        
        # Format phone number: 254XXXXXXXXX
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        elif phone_number.startswith('+'):
            phone_number = phone_number[1:]
        
        # Generate timestamp
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # Generate password
        password_str = f"{self.shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(password_str.encode()).decode()
        
        payload = {
            'BusinessShortCode': self.shortcode,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': str(amount),
            'PartyA': phone_number,
            'PartyB': self.shortcode,
            'PhoneNumber': phone_number,
            'CallBackURL': settings.MPESA_CALLBACK_URL,
            'AccountReference': account_reference,
            'TransactionDesc': transaction_desc[:50]  # Max 50 chars
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/mpesa/stkpush/v1/processrequest",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                },
                json=payload
            )
            
            data = response.json()
            
            if response.status_code == 200 and data.get('ResponseCode') == '0':
                return {
                    'success': True,
                    'message': data.get('CustomerMessage', 'Payment initiated successfully'),
                    'checkout_request_id': data.get('CheckoutRequestID'),
                    'response_code': data.get('ResponseCode'),
                    'merchant_request_id': data.get('MerchantRequestID')
                }
            else:
                logger.error(f"M-PESA STK Push error: {data}")
                return {
                    'success': False,
                    'message': data.get('ResponseDescription', 'Payment failed'),
                    'error_code': data.get('errorCode'),
                    'error_message': data.get('errorMessage')
                }
        
        except Exception as e:
            logger.error(f"Error initiating STK Push: {str(e)}")
            return {
                'success': False,
                'message': 'Payment service unavailable'
            }
    
    def query_status(self, checkout_request_id):
        """
        Query the status of an STK Push transaction
        """
        access_token = self.get_access_token()
        if not access_token:
            return {
                'success': False,
                'message': 'Failed to authenticate with M-PESA'
            }
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password_str = f"{self.shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(password_str.encode()).decode()
        
        payload = {
            'BusinessShortCode': self.shortcode,
            'Password': password,
            'Timestamp': timestamp,
            'CheckoutRequestID': checkout_request_id
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/mpesa/stkpushquery/v1/query",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                },
                json=payload
            )
            
            data = response.json()
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'status': data.get('ResultCode') == '0',
                    'message': data.get('ResultDesc'),
                    'data': data
                }
            
            return {
                'success': False,
                'message': 'Failed to query payment status'
            }
        
        except Exception as e:
            logger.error(f"Error querying payment status: {str(e)}")
            return {
                'success': False,
                'message': 'Payment status check failed'
            }