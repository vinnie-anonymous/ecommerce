from django import forms

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]


class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(
        choices=PRODUCT_QUANTITY_CHOICES,
        coerce=int,
        initial=1,
        widget=forms.Select(attrs={'class': 'form-select w-auto'})
    )
    # override=True → set quantity to this value (used by cart update)
    # override=False → add to existing quantity (used by Add to Cart button)
    override = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput
    )