from django import forms
from django.forms import inlineformset_factory
from apps.products.models import Product, ProductImage
from apps.orders.models import Order


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # ── Exact fields from your Product model ──────────────────────────
        fields = [
            'name',
            'slug',
            'category',
            'description',
            'price',
            'stock',
            'is_active',
            'is_featured',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'slug': forms.TextInput(attrs={
                'placeholder': 'auto-generated if left blank'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                # Checkboxes get a different Bootstrap class
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs.setdefault('class', 'form-control')


# Inline formset — manage multiple images per product in one form
ProductImageFormSet = inlineformset_factory(
    Product,
    ProductImage,
    fields=['image', 'alt_text', 'is_primary'],
    extra=3,
    can_delete=True,
    widgets={
        'alt_text': forms.TextInput(attrs={'class': 'form-control'}),
        'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    }
)


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status', 'mpesa_code', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'mpesa_code': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }