from django.urls import path
from users.views import SendPasswordResetEmailView, UserChangePasswordView, UserLoginView, UserProfileView, UserRegistrationView, UserRegistrationVerifyView, UserPasswordResetView, TokenRefreshView, BillingAddressView, UserProfileView, UserProfileDetailView

urlpatterns = [
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('verify-email/<str:otp>/', UserRegistrationVerifyView.as_view(), name='verify-email'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('changepassword/', UserChangePasswordView.as_view(), name='changepassword'),
    path('send-reset-password-email/', SendPasswordResetEmailView.as_view(), name='send-reset-password-email'),
    path('reset-password/<uid>/<token>/', UserPasswordResetView.as_view(), name='reset-password'),
    path('billing-address/', BillingAddressView.as_view(), name='get-create-billing-address'),
    path('billing-address/update/', BillingAddressView.as_view(), name='update-billing-address'),
    path('profile/detail/', UserProfileDetailView.as_view(), name='user-profile-detail'),
    path('profile/update/', UserProfileView.as_view(), name='update-user-profile'),
]