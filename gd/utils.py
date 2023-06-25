from .models import Post

def get_post_countries():
    post_countries = Post.objects.filter(status='Approved').values_list('country', flat=True).distinct()
    return post_countries