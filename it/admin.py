from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings
from .models import Order
from utils import Util
from .models import Transaction

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'total_price', 'status', 'design_file_link')
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

            # Retrieve the user associated with the order
            user = obj.user

            # Construct the email message with the updated field values
            subject = "Order Update Notification"
            message = f"Dear {user.email},<br><br>" \
                      f"Your order with ID {obj.pk} has been updated.<br><br>" \
                      f"The following fields were modified:<br><br>"

            for field in updated_fields:
                field_value = getattr(obj, field)
                if field == 'design_file':
                    file_url = self._get_design_file_url(obj.design_file)
                    file_name = obj.design_file.name
                    field_value = format_html('<a href="{}" download="{}">{}</a>', file_url, file_name, file_name)
                field_name = self.model._meta.get_field(field).verbose_name
                message += f"<strong>{field_name}:</strong> {field_value}<br>"

            data = {
                'subject': subject,
                'body': '',
                'html_body': message,
                'to_email': user.email
            }
            Util.send_email(data)

    def _get_design_file_url(self, design_file):
        root_url = settings.BASE_URL
        file_url = design_file.url
        return f"{root_url}{file_url}"


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'order__title')

    def get_order(self, obj):
        return obj.order.title

    get_order.short_description = 'Order'

