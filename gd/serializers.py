from rest_framework import serializers
from .models import Post, Tip, Donation, Comment

class TipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tip
        fields = '__all__'

class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    tips = TipSerializer(many=True, read_only=True)
    raised = DonationSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = '__all__'
        
    def create(self, validated_data):
        # Assign the logged-in user to the user field
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


