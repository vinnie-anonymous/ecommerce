from django import forms
from apps.orders.models import Order

KENYAN_COUNTIES = [
    ('', 'Select County'),
    ('Nairobi', 'Nairobi'), ('Mombasa', 'Mombasa'), ('Kisumu', 'Kisumu'),
    ('Nakuru', 'Nakuru'), ('Eldoret', 'Eldoret'), ('Kiambu', 'Kiambu'),
    ('Machakos', 'Machakos'), ('Meru', 'Meru'), ('Nyeri', 'Nyeri'),
    ('Kakamega', 'Kakamega'), ('Garissa', 'Garissa'), ('Kisii', 'Kisii'),
    ('Kilifi', 'Kilifi'), ('Lamu', 'Lamu'), ('Malindi', 'Malindi'),
    ('Other', 'Other'),
]


class CheckoutForm(forms.ModelForm):
    county = forms.ChoiceField(
        choices=KENYAN_COUNTIES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'address', 'city', 'county', 'postal_code', 'notes',
        ]
        widgets = {
            'first_name':   forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':    forms.TextInput(attrs={'class': 'form-control'}),
            'email':        forms.EmailInput(attrs={'class': 'form-control'}),
            'phone':        forms.TextInput(attrs={'class': 'form-control', 'placeholder': '07XXXXXXXX'}),
            'address':      forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city':         forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code':  forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'notes':        forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, user=None, **kwargs):
        # Remove 'user' from kwargs before passing to super()
        # because ModelForm doesn't know about it
        kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # postal_code not required
        self.fields['postal_code'].required = False
        self.fields['notes'].required = False
        self.fields['county'].required = False