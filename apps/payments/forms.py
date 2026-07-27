from django import forms


class MpesaPaymentForm(forms.Form):
    phone = forms.CharField(
        max_length=15,
        label='M-Pesa Phone Number',
        help_text='Enter your Safaricom number e.g. 0712345678',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '0712 345 678',
        })
    )

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip().replace(' ', '')
        # Basic KE number validation
        if not (phone.startswith('07') or phone.startswith('01') or
                phone.startswith('254')):
            raise forms.ValidationError('Enter a valid Safaricom Kenya number.')
        return phone