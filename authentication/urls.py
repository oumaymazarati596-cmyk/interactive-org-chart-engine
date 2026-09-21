from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),                    
    path('home/', views.home_view, name='home'),                  
    path('management/', views.user_management_view, name='user_management'), 
    path('profile/<int:user_id>/', views.profile_view, name='profile'),
    path('stickman/', views.stickman_view, name='stickman'),
    path('logout/', views.logout_view, name='logout'),            
]