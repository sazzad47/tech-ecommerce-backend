from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from users.models import User, BillingAddress, Volunteer

class UserModelAdmin(BaseUserAdmin):
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserModelAdmin
    # that reference specific fields on auth.User.
    def billing_address_link(self, obj):
        if obj.billing_address:
            url = reverse('admin:authentication_billingaddress_change', args=[obj.billing_address.id])
            return format_html('<a href="{}">{}</a>', url, obj.billing_address)
        return None

    billing_address_link.short_description = 'Billing Address'

    list_display = ('id', 'email', 'first_name', 'last_name', 'is_admin', 'is_staff', 'billing_address_link', 'is_volunteer', 'funds')
    list_filter = ('is_admin', 'is_staff', 'is_volunteer')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_admin', 'is_staff', 'is_active', 'is_volunteer')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ()

# Now register the new UserModelAdmin...
admin.site.register(User, UserModelAdmin)
admin.site.register(BillingAddress)
admin.site.register(Volunteer)
