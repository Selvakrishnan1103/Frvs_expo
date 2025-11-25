from django.urls import path
from .views import RegisterParent, VerifyFace

urlpatterns = [
    path('register/', RegisterParent.as_view()),
    path('verify/', VerifyFace.as_view()),
]
