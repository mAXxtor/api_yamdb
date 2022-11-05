from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView
from api_yamdb.api.views import TokenView, UserRegView
from rest_framework.routers import DefaultRouter
from .views import TitleViewSet, GenreViewSet, CategoryViewSet


router_v1 = DefaultRouter()
router_v1.register('titles', TitleViewSet)

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/genre/', GenreViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('v1/genre/<slug:slug>/', GenreViewSet.as_view({'delete': 'destroy'})),
    path('v1/category/', CategoryViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('v1/category/<slug:slug>/', CategoryViewSet.as_view({'delete': 'destroy'})),
    path('v1/auth/', include([
        path('signup/', UserRegView.as_view()),
        path('token/', TokenView.as_view())
    ])),
    path('token/', TokenObtainPairView.as_view())
]
