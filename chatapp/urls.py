

from django.urls import path
from .views import chat_view, chat_api, scholar_profiles

app_name = 'chatapp'

urlpatterns = [
    path('', chat_view, name='chat'),
    path('api/chat/', chat_api, name='chat_api'),
    path('api/scholar/', scholar_profiles, name='scholar_profiles'),
]
