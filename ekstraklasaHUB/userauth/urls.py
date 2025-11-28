from django.urls import path
from .views import register_view, login_view, logout_view

from django.urls import path
from . import views  # importujemy widoki z pliku powyżej

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('', views.main_view, name="main_view")
]   