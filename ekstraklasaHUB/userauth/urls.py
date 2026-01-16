from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('', views.main_view, name="main_view"),
    path('api/search/', views.search_clubs_api, name='search_clubs_api'),
    path('club/<int:club_id>/stats/', views.club_stats_view, name='club_stats'),
    path('api/predict/', views.predict_match, name='predict_match'),
]   