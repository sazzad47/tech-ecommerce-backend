from rest_framework import viewsets
from .models import Post, Tip, Donation, Comment
from .serializers import PostSerializer, TipSerializer, DonationSerializer, CommentSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from .utils import get_post_countries
from django.http import JsonResponse


class CustomPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(status='Approved').order_by('-created_at')
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['category', 'country']
    search_fields = [
        '^mode', '^category', '^first_name', '^last_name',
        '^country', '^province', '^city', '^zip', '^address', '^name_of_employment', '^written_description'
    ]
    ordering_fields = ['created_at']  # Replace with your desired field for sorting
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        # Assign the logged-in user to the user field
        serializer.save(user=self.request.user)


    def get_queryset(self):
        queryset = super().get_queryset()
        emergency = self.request.query_params.get('emergency')
        if emergency == 'true':
            queryset = queryset.filter(mode='emergency')
        elif emergency == 'false':
            queryset = queryset.filter(mode='normal')

        return queryset.filter(status='Approved')
    

class TipViewSet(viewsets.ModelViewSet):
    queryset = Tip.objects.all()
    serializer_class = TipSerializer

class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

def get_post_countries_view(request):
    post_countries = get_post_countries()

    # Convert the QuerySet to a list
    post_countries_list = list(post_countries)

    # Return as JSON response
    data = {'countries': post_countries_list}
    return JsonResponse(data)
