from django.urls import path
from .views import chat_view, chat_api

app_name = 'chatapp'

urlpatterns = [
    path('', chat_view, name='chat'),
    path('api/chat/', chat_api, name='chat_api'),
    path('chat_api/', chat_api, name='chat_api_direct'),
    path('api/scholar/', chat_api, name='scholar_profiles'),
    path('api/scholar/csv/', chat_api, name='scholar_profiles_csv'),
    # path('api/scholar/', scholar_profiles, name='scholar_profiles'),
    # path('api/scholar/csv/', scholar_profiles_csv, name='scholar_profiles_csv'),

]
