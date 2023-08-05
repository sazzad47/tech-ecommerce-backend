from rest_framework import serializers
from .models import Post, Tip, Donation, Comment, DonationsWithdrawalRequest, TipsWithdrawalRequest, Company, GlobalLocation, SocialLink, PaymentOption, FooterPage

class TipSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    first_name = serializers.ReadOnlyField(source='user.first_name')
    last_name = serializers.ReadOnlyField(source='user.last_name')
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Tip
        fields = ('id', 'created_at', 'user', 'post', 'first_name', 'last_name', 'avatar', 'company_tips', 'volunteer_tips', 'is_hidden')
    
    def get_avatar(self, obj):
        if obj.user.avatar:
            return obj.user.avatar
        return None

class DonorSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    first_name = serializers.ReadOnlyField(source='user.first_name')
    last_name = serializers.ReadOnlyField(source='user.last_name')
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Donation
        fields = ('id', 'created_at', 'user', 'post', 'first_name', 'last_name', 'avatar', 'amount', 'is_hidden')
    
    def get_avatar(self, obj):
        if obj.user.avatar:
            return obj.user.avatar
        return None

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    first_name = serializers.ReadOnlyField(source='user.first_name')
    last_name = serializers.ReadOnlyField(source='user.last_name')
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'created_at', 'user', 'post', 'first_name', 'last_name', 'avatar', 'content', 'is_hidden')

    def get_avatar(self, obj):
        if obj.user.avatar:
            return obj.user.avatar
        return None

    
class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = '__all__'
        
    def create(self, validated_data):
        # Assign the logged-in user to the user field
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
class PostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'created_at', 'status', 'donation_needed', 'total_donations']

class PostItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        exclude = ('user', )

class DonationsWithdrawalRequestSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    class Meta:
        model = DonationsWithdrawalRequest
        fields = ['id', 'user', 'amount', 'account_number', 'bank_name', 'routing_number', 'other_information', 'status']

class TipsWithdrawalRequestSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    class Meta:
        model = TipsWithdrawalRequest
        fields = ['id', 'user', 'amount', 'account_number', 'bank_name', 'routing_number', 'other_information', 'status']

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class GlobalLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalLocation
        fields = '__all__'

class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialLink
        fields = '__all__'

class PaymentOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentOption
        fields = '__all__'

class FooterPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FooterPage
        fields = '__all__'