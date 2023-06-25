from django.contrib import admin
from django.utils.html import format_html, mark_safe
from django.conf import settings
from .models import Order
from utils import Util
from .models import Transaction
from django.contrib.postgres import fields
from django_json_widget.widgets import JSONEditorWidget
from django import forms
from django_admin_json_editor import JSONEditorWidget
from django.contrib.auth.models import Group

class OrderAdminForm(forms.ModelForm):
    demo = forms.JSONField(
        widget=JSONEditorWidget(
            schema={
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'url': {'type': 'string'},
                        'description': {'type': 'string'}
                    }
                }
            }
        ),
        required=False
    )

    class Meta:
        model = Order
        fields = '__all__'

 

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderAdminForm
    list_display = ('title', 'user', 'total_price', 'status')
    list_filter = ('status',)
    search_fields = ('title', 'user__username')


    def design_file_link(self, obj):
        if obj.design_file:
            file_url = self._get_design_file_url(obj.design_file)
            file_name = obj.design_file.name
            return format_html('<a href="{}" download="{}">{}</a>', file_url, file_name, file_name)
        return '-'
    design_file_link.short_description = 'Design File'

    def save_model(self, request, obj, form, change):
        # Save the model instance
        super().save_model(request, obj, form, change)

        # Check if the order is being updated by an admin
        if change:
            # Retrieve the updated fields
            updated_fields = form.changed_data

            # Exclude the 'design_file' field from the updated fields
            updated_fields = [field for field in updated_fields if field != 'design_file']
            
           # Retrieve the user associated with the order
            user = obj.user

            # Construct the email message with the updated field values
            subject = "Order Update Notification"
            message = f"Dear {user.email},<br><br>" \
                      f"Your order with ID {obj.pk} has been updated.<br><br>" \
                      f"The following fields were modified:<br><br>"

            for field in updated_fields:
                field_value = getattr(obj, field)
                field_name = self.model._meta.get_field(field).verbose_name
                message += f"<strong>{field_name}:</strong> {field_value}<br>"

            data = {
                'subject': subject,
                'body': '',
                'html_body': message,
                'to_email': user.email
            }
            Util.send_email(data)



@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'order__title')

    def get_order(self, obj):
        return obj.order.title

    get_order.short_description = 'Order'

admin.site.unregister(Group)