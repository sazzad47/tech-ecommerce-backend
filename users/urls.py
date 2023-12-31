from django.urls import path, include
from users.views import SendPasswordResetEmailView, VolunteerViewSet, GeVolunteersByStatusView, SendAdminPasswordResetEmailView, UserChangePasswordView, UserLoginView, UserProfileView, UserRegistrationView, UserRegistrationVerifyView, UserPasswordResetView, TokenRefreshView, BillingAddressView, UserProfileView, UserProfileDetailView, AdminLoginView, AdminCodeVerificationView, VolunteerView, AllVolunteerView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'admin-volunteers', VolunteerViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('verify-email/<str:otp>/', UserRegistrationVerifyView.as_view(), name='verify-email'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('changepassword/', UserChangePasswordView.as_view(), name='changepassword'),
    path('send-reset-password-email/', SendPasswordResetEmailView.as_view(), name='send-reset-password-email'),
    path('reset-password/<uid>/<token>/', UserPasswordResetView.as_view(), name='reset-password'),
    path('billing-address/', BillingAddressView.as_view(), name='get-create-billing-address'),
    path('billing-address/update/', BillingAddressView.as_view(), name='update-billing-address'),
    path('volunteer-information/', VolunteerView.as_view(), name='get-create-volunteer-information'),
    path('volunteer-information/update/', VolunteerView.as_view(), name='update-volunteer-information'),
    path('volunteers/', AllVolunteerView.as_view(), name='all-volunteers'),
    path('volunteers/<str:status>/', GeVolunteersByStatusView.as_view(), name='admin_all_volunteers'),
    path('profile/detail/', UserProfileDetailView.as_view(), name='user-profile-detail'),
    path('profile/update/', UserProfileView.as_view(), name='update-user-profile'),
    path('admin/verify/', AdminLoginView.as_view(), name='admin-verify'),
    path('admin/login/', AdminCodeVerificationView.as_view(), name='admin-login'),
    path('send-admin-reset-password-email/', SendAdminPasswordResetEmailView.as_view(), name='send-admin-reset-password-email'),
]