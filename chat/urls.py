from django.urls import path, include
from chat import views as chat_views
from django.contrib.auth.views import LoginView, LogoutView


urlpatterns = [
    path("discussion/<str:pk>/<str:room_name>/", chat_views.chatPage, name="chat-page"),
    path('chat/<str:pk>/<str:room_name>/', chat_views.ClubChat, name='club-chat'),
    path('clear-club-chats/<str:pk>/<str:room_name>/', chat_views.clearClubChatMessage, name='clear-club-chats'),
    path('clear-group-chats/<str:pk>/<str:room_name>/', chat_views.clearGroupChatMessage, name='clear-group-chats'),
    # # login-section
    # path("auth/login/", LoginView.as_view
    #      (template_name="chat/login.html"), name="login-user"),
    # path("auth/logout/", chat_views.logoutUser, name="logout-user"),
]