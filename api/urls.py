from django.urls import path, include
from rest_framework import routers
from .views import (
    UserViewSet, SubjectViewSet, ActivityViewSet, TopicViewSet, 
    completed_activity, progress_topics, pending_reviews, profile, study_activity
)

from .views import send_verification_code, verify_email

from .views import forgot_password, reset_password


router = routers.DefaultRouter()
router.register(r'user', UserViewSet, basename='user')
router.register(r'subject', SubjectViewSet, basename='subject')
router.register(r'activity', ActivityViewSet, basename='activity')
router.register(r'topics', TopicViewSet, basename='topic')

urlpatterns = [
    path('', include(router.urls)),
    path('activities/<int:pk>/complete/', completed_activity),
    path('reviews/pending/', pending_reviews),
    path('progress/', progress_topics),
    path('profile/', profile),
    path('activities/<int:pk>/study/', study_activity),
    path('auth/send-code/', send_verification_code),
    path('auth/verify/', verify_email),
    path('auth/forgot-password/', forgot_password),
    path('auth/reset-password/', reset_password),
    
]