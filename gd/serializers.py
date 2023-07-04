from rest_framework import serializers
from .models import Post, Tip, Donation, Comment

class TipSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    first_name = serializers.ReadOnlyField(source='user.first_name')
    last_name = serializers.ReadOnlyField(source='user.last_name')
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Tip
        fields = ('user', 'first_name', 'last_name', 'avatar', 'amount', 'is_hidden')
    
    def get_avatar(self, obj):
        if obj.user.avatar:
            return obj.user.avatar.url
        return None

class DonorSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    first_name = serializers.ReadOnlyField(source='user.first_name')
    last_name = serializers.ReadOnlyField(source='user.last_name')
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Donation
        fields = ('user', 'first_name', 'last_name', 'avatar', 'amount', 'is_hidden')
    
    def get_avatar(self, obj):
        if obj.user.avatar:
            return obj.user.avatar.url
        return None

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    first_name = serializers.ReadOnlyField(source='user.first_name')
    last_name = serializers.ReadOnlyField(source='user.last_name')
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('user', 'first_name', 'last_name', 'avatar', 'content', 'created_at', 'is_hidden')

    def get_avatar(self, obj):
        if obj.user.avatar:
            return obj.user.avatar.url
        return None

    
class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = '__all__'
        
    def create(self, validated_data):
        # Assign the logged-in user to the user field
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


