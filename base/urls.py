from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    path('profile/<str:pk>/', views.userProfile, name="profile"),
    path('settings/<str:pk>/', views.userSettings, name="settings"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerPage, name="register"),
    path('follow/<str:pk>', views.follow, name="follow"),
    path('create-topic/<str:pk>', views.createTopic, name="create-topic"),
    path('', views.home, name="home"),
    path('room/<str:pk>/', views.room, name="room"),
    path('create-room/', views.createRoom, name="create-room"),
    path('update-room/<str:pk>/', views.updateRoom, name="update-room"),
    path('delete-room/<str:pk>/', views.deleteRoom, name="delete-room"),
    path('delete-message/<str:pk>/', views.deleteMessage, name="delete-message"),
]
