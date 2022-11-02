from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView

from api_yamdb.api.views import TokenView, UserRegView

urlpatterns = [
    path('v1/auth/', include([
        path('signup/', UserRegView.as_view()),
        path('token/', TokenView.as_view())
    ])),
    path('token/', TokenObtainPairView.as_view())
]
