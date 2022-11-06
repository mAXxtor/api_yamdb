from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView

from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    ReviewViewSet, TitleViewSet, TokenView,
                    UserRegView, UsersViewSet,)

router_v1 = DefaultRouter()
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet, basename='reviews')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments')
router_v1.register('users', UsersViewSet, basename='users')

urlpatterns = [
    path('v1/auth/', include([
        path('signup/', UserRegView.as_view()),
        path('token/', TokenView.as_view())
    ])),
    path('v1/users/<slug:slug>/',
         UsersViewSet.as_view({'patch': 'update', 'get':'retrieve', 'delete': 'destroy'})),
    path('token/', TokenObtainPairView.as_view()),
    path('v1/', include(router_v1.urls)),
    path('v1/genres/',
         GenreViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('v1/genres/<slug:slug>/',
         GenreViewSet.as_view({'delete': 'destroy'})),
    path('v1/categories/',
         CategoryViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('v1/categories/<slug:slug>/',
         CategoryViewSet.as_view({'delete': 'destroy'})),
]
