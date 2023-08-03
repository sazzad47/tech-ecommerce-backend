from rest_framework import serializers
from users.models import User, BillingAddress, Volunteer
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from users.utils import Util
import pyotp
from app.settings import BASE_CLIENT_URL

class generateKey:
    @staticmethod
    def return_value():
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret, interval=86400)
        otp = totp.now()
        return {"totp": secret, "OTP": otp}
    
class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError("Password and Confirm Password don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')

        key = generateKey.return_value()

        user = User(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            intro=validated_data.get('intro', ''),
            place_of_birth=validated_data.get('place_of_birth', ''),
            current_location=validated_data.get('current_location', ''),
            education=validated_data.get('education', ''),
            profession=validated_data.get('profession', ''),
            expertise=validated_data.get('expertise', ''),
            biography=validated_data.get('biography', ''),
            social_links=validated_data.get('social_links', []),
            avatar=validated_data.get('avatar', None),
            otp=key['OTP'],
            activation_key=key['totp']
        )

        user.set_password(validated_data['password'])
        user.is_active = False
        user.save()

        body = f"""
            Hi {user.first_name} {user.last_name},

            Thank you for signing up! Please use the 
            following OTP to verify your account:
            OTP: {user.otp}

            Regards,
            Sazzad Hossen
        """
        data = {
            'subject': 'Account Activation',
            'body': body,
            'to_email': user.email
        }
        Util.send_email(data)

        return user
    

class UserRegistrationVerifySerializer(serializers.Serializer):
    otp = serializers.IntegerField()

    def validate_otp(self, value):
        user = self.context['user']
        otp = user.otp
        if value != otp:
            raise serializers.ValidationError("Invalid OTP")
        return value

        
class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = User
        fields = ['email', 'password']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_admin', 'is_staff', 'is_volunteer', 'funds']

class UserChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
    password2 = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        user = self.context.get('user')
        if password != password2:
            raise serializers.ValidationError("Password and Confirm Password don't match")
        user.set_password(password)
        user.save()
        return attrs

class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            link = BASE_CLIENT_URL +'/' + 'reset-password' + '/'+ uid+ '/'+ token
            body = 'Click the following link to reset your password: '+link
            data = {
                'subject': 'Reset Your Password',
                'body': body,
                'to_email': user.email
            }
            Util.send_email(data)
            return attrs
        else:
            raise serializers.ValidationError('You are not a registered user')

class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
    password2 = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            password2 = attrs.get('password2')
            uid = self.context.get('uid')
            token = self.context.get('token')
            if password != password2:
                raise serializers.ValidationError("Password and Confirm Password don't match")
            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError('Token is not valid or expired')
            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user, token)
            raise serializers.ValidationError('Token is not valid or expired')


class BillingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingAddress
        fields = ['first_name', 'last_name', 'email', 'phone', 'country', 'province', 'city', 'zip', 'address']   

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'intro', 'place_of_birth', 'current_location', 'education', 'profession', 'expertise', 'biography', "avatar", 'social_links', 'is_admin', 'is_staff', 'is_volunteer', 'funds', 'pending_withdrawal_donations', 'pending_withdrawal_tips', 'tips']

class VolunteerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Volunteer
        fields = [
            'first_name',
            'last_name',
            'fathers_name',
            'mothers_name',
            'country',
            'province',
            'city',
            'zip',
            'address',
            'marital_status',
            'specific_marital_status',
            'date_of_birth',
            'sex',
            'specific_sex',
            'blood_group',
            'occupation',
            'email',
            'phone',
            'identification_card',
            'photo',
            'status',
        ]