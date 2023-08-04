from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from users.serializers import SendPasswordResetEmailSerializer, SendAdminPasswordResetEmailSerializer, UserChangePasswordSerializer, UserLoginSerializer, UserPasswordResetSerializer, UserProfileSerializer, UserRegistrationSerializer, UserRegistrationVerifySerializer, BillingAddressSerializer, UserProfileSerializer, VolunteerSerializer
from django.contrib.auth import authenticate
from users.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.permissions import IsAuthenticated
from users.models import User, Volunteer
from rest_framework import generics
import pyotp
from rest_framework.parsers import MultiPartParser, FormParser
from users.utils import Util

# Generate Token Manually
def get_tokens_for_user(user):
  refresh = RefreshToken.for_user(user)
  return {
      'refresh': str(refresh),
      'access': str(refresh.access_token),
  }

class TokenRefreshView(TokenRefreshView):
    pass

class UserRegistrationView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, format=None):
    serializer = UserRegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return Response({'msg':'Please activate your account.'}, status=status.HTTP_201_CREATED)
  
class UserRegistrationVerifyView(APIView):

    def post(self, request, otp, format=None):
        try:
            user = User.objects.get(otp=otp, is_active=False)
            serializer = UserRegistrationVerifySerializer(data=request.data, context={'user': user})

            if serializer.is_valid():
                activation_key = user.activation_key
                totp = pyotp.TOTP(activation_key, interval=86400)
                verify = totp.verify(serializer.validated_data['otp'])

                if verify:
                    user.is_active = True
                    user.save()
                    token = get_tokens_for_user(user)
                    return Response({'token':token, 'msg':'Your account has been successfully activated!'}, status=status.HTTP_201_CREATED)

                else:
                    return Response({"message": "Given OTP has expired!"}, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({"message": "Invalid OTP or no inactive user found for the given OTP."}, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, format=None):
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.data.get('email')
    password = serializer.data.get('password')
    user = authenticate(email=email, password=password)
    if user is not None:
      token = get_tokens_for_user(user)
      return Response({'token':token, 'msg':'Login Success'}, status=status.HTTP_200_OK)
    else:
      return Response({'errors':{'non_field_errors':['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)

class AdminLoginView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        user = authenticate(email=email, password=password)
        
        if user is not None and (user.is_admin or user.is_staff):
            # Generate and send the verification code to the user's email
            verification_code = generate_verification_code(user)
            send_verification_code(email, verification_code)
            return Response({'msg': 'Verification code sent to your email'}, status=status.HTTP_200_OK)
        else:
            return Response({'errors': {'non_field_errors': ['Email or Password is not valid']}}, status=status.HTTP_404_NOT_FOUND)

class AdminCodeVerificationView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        email = request.data.get('email')
        code = request.data.get('code')

        # Verify the code against the user's email
        user = User.objects.filter(email=email).first()
        if user is not None and (user.is_admin or user.is_staff) and verify_verification_code(user, code):
        # if user is not None and (user.is_admin or user.is_staff) and verify_verification_code(user, code):
            token = get_tokens_for_user(user)
            return Response({'token': token, 'msg': 'Login Success'}, status=status.HTTP_200_OK)
        else:
            return Response({'errors': {'non_field_errors': ['Invalid verification code']}}, status=status.HTTP_404_NOT_FOUND)
        

class generateKey:
    @staticmethod
    def return_value():
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret, interval=86400)
        otp = totp.now()
        return {"totp": secret, "OTP": otp}
    
def generate_verification_code(user):
    key = generateKey.return_value()
    otp = key['OTP']
    activation_key=key['totp']
    user.otp = otp
    user.activation_key = activation_key
    user.save()
    return otp

def verify_verification_code(user, code):
    activation_key = user.activation_key
    totp = pyotp.TOTP(activation_key, interval=86400)
    return totp.verify(code)

def send_verification_code(email, code):
    body = f"""
            Hi,

            Please use the following OTP to verify 
            that it's really you:
            OTP: {code}

            Regards,
            Admin
        """
    data = {
        'subject': 'Admin Login Verification Code',
        'body': body,
        'to_email': email
    }
    Util.send_email(data)

class SendAdminPasswordResetEmailView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, format=None):
    serializer = SendAdminPasswordResetEmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response({'msg':'Password Reset link send. Please check your Email'}, status=status.HTTP_200_OK)

class UserProfileView(APIView):
  renderer_classes = [UserRenderer]
  permission_classes = [IsAuthenticated]
  def get(self, request, format=None):
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)

class UserChangePasswordView(APIView):
  renderer_classes = [UserRenderer]
  permission_classes = [IsAuthenticated]
  def post(self, request, format=None):
    serializer = UserChangePasswordSerializer(data=request.data, context={'user':request.user})
    serializer.is_valid(raise_exception=True)
    return Response({'msg':'Password Changed Successfully'}, status=status.HTTP_200_OK)

class SendPasswordResetEmailView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, format=None):
    serializer = SendPasswordResetEmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response({'msg':'Password Reset link send. Please check your Email'}, status=status.HTTP_200_OK)

class UserPasswordResetView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, uid, token, format=None):
    serializer = UserPasswordResetSerializer(data=request.data, context={'uid':uid, 'token':token})
    serializer.is_valid(raise_exception=True)
    return Response({'msg':'Password Reset Successfully'}, status=status.HTTP_200_OK)

class BillingAddressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        billing_address = user.billing_address

        if not billing_address:
            return Response({"message": "Billing address does not exist."}, status=404)

        serializer = BillingAddressSerializer(billing_address)
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        serializer = BillingAddressSerializer(data=request.data)

        if serializer.is_valid():
            billing_address = serializer.save(user=user)

            # Assign the billing address to the user's billing_address field
            user.billing_address = billing_address
            user.save()

            return Response({"message": "Billing address saved successfully."})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        user = request.user
        billing_address = user.billing_address

        if not billing_address:
            return Response({"message": "Billing address does not exist."}, status=404)

        serializer = BillingAddressSerializer(billing_address, data=request.data)

        if serializer.is_valid():
            billing_address = serializer.save()
            updated_data = BillingAddressSerializer(billing_address).data
            return Response({"message": "Billing address updated successfully.", "data": updated_data})

        return Response(serializer.errors, status=400)
    
class VolunteerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        volunteer_information = user.volunteer_information

        if not volunteer_information:
            return Response({"message": "Volunteer information does not exist."}, status=404)

        serializer = VolunteerSerializer(volunteer_information)
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        volunteer_information = user.volunteer_information

        if volunteer_information:
            return Response({"message": "You have already sent your volunteer information. Go to your dashboard to update it."}, status=status.HTTP_409_CONFLICT)
       
        serializer = VolunteerSerializer(data=request.data)

        if serializer.is_valid():
            volunteer_information = serializer.save(user=user)

            # Assign the volunteer information to the user's volunteer_information field
            user.volunteer_information = volunteer_information
            user.save()

            return Response({"message": "Volunteer information saved successfully."})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        user = request.user
        volunteer_information = user.volunteer_information

        if not volunteer_information:
            return Response({"message": "Volunteer information does not exist."}, status=404)

        serializer = VolunteerSerializer(volunteer_information, data=request.data)

        if serializer.is_valid():
            volunteer_information = serializer.save()
            updated_data = VolunteerSerializer(volunteer_information).data
            return Response({"message": "Volunteer information updated successfully.", "data": updated_data})

        return Response(serializer.errors, status=400)
    
    def delete(self, request):
        user = request.user
        volunteer_information = user.volunteer_information

        if not volunteer_information:
            return Response({"message": "Volunteer information does not exist."}, status=status.HTTP_404_NOT_FOUND)

        volunteer_information.delete()
        return Response({"message": "Volunteer information deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class AllVolunteerView(APIView):
    def get(self, request):
        try:
            volunteers = Volunteer.objects.filter(status='Approved')
            serializer = VolunteerSerializer(volunteers, many=True)
            return Response(serializer.data)
        except Volunteer.DoesNotExist:
            return Response({'message': 'No volunteers found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class UserProfileView(generics.UpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        return self.request.user
    
class UserProfileDetailView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user