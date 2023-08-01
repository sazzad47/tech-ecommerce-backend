from django.contrib import admin
from .models import Post, Tip, Donation, Comment
from django_json_widget.widgets import JSONEditorWidget
from django import forms
from django_admin_json_editor import JSONEditorWidget

class PostAdminForm(forms.ModelForm):
    suggested_donations = forms.JSONField(
        widget=JSONEditorWidget(
            schema={
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'amount': {'type': 'number'}
                    }
                }
            }
        ),
        required=False
    )
    suggested_company_tips = forms.JSONField(
        widget=JSONEditorWidget(
            schema={
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'amount': {'type': 'number'}
                    }
                }
            }
        ),
        required=False
    )
    suggested_volunteer_tips = forms.JSONField(
        widget=JSONEditorWidget(
            schema={
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'amount': {'type': 'number'}
                    }
                }
            }
        ),
        required=False
    )

    class Meta:
        model = Post
        fields = '__all__'

class TipInline(admin.TabularInline):
    model = Tip
    extra = 0

class DonationInline(admin.TabularInline):
    model = Donation
    extra = 0

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    inlines = [TipInline, DonationInline, CommentInline]
    list_display = ['application_for', 'category', 'time_limit']
    list_filter = ['application_for', 'category']
    search_fields = ['application_for', 'category', 'first_name', 'last_name']

@admin.register(Tip)
class TipAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'company_tips', 'volunteer_tips']
    list_filter = ['user', 'post']
    search_fields = ['user__email', 'post__application_for']

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'amount']
    list_filter = ['user', 'post']
    search_fields = ['user__email', 'post__application_for']

@admin.register(Comment)
class CommentInline(admin.ModelAdmin):
    list_display = ['user', 'post', 'content']
    list_filter = ['user', 'post']
    search_fields = ['user__email', 'post__application_for']

