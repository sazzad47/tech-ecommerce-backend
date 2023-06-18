from django import forms
from django.contrib.auth import get_user_model
from .models import Order

User = get_user_model()

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['title', 'total_price', 'advance_price', 'advance_percentage', 'status', 'design_file']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Store the user in the instance
        super().__init__(*args, **kwargs)
        if self.user and not self.user.is_staff:
            # User is not staff, exclude certain fields
            self.fields['total_price'].widget.attrs['readonly'] = True
            self.fields['advance_price'].widget.attrs['readonly'] = True
            self.fields['advance_percentage'].widget.attrs['readonly'] = True
            self.fields['status'].widget.attrs['readonly'] = True
            self.fields['design_file'].widget.attrs['readonly'] = True

    def clean(self):
        cleaned_data = super().clean()
        if self.user and not self.user.is_staff:
            # User is not staff, restrict access to certain fields
            if 'total_price' in cleaned_data:
                del cleaned_data['total_price']
            if 'advance_price' in cleaned_data:
                del cleaned_data['advance_price']
            if 'advance_percentage' in cleaned_data:
                del cleaned_data['advance_percentage']
            if 'status' in cleaned_data:
                del cleaned_data['status']
            if 'design_file' in cleaned_data:
                del cleaned_data['design_file']

        return cleaned_data