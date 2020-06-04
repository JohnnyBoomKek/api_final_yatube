from django.urls import path, include

from rest_framework.authtoken import views as rest_views
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('posts', views.PostViewSet, basename='posts')
router.register(r'posts/(?P<post_id>\d+)/comments',
                views.CommentViewSet, basename="comments")
router.register('group', views.GroupViewSet)
router.register('follow', views.FollowViewSet, basename='follow')


urlpatterns = [
    path('', include(router.urls)),

]
