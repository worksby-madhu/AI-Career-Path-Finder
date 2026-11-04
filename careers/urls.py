from django.urls import path
from . import views
urlpatterns = [
 path('', views.home, name='home'), path('task-progress/', views.toggle_task, name='toggle_task'),
 path('register/', views.register_view, name='register'), path('login/', views.login_view, name='login'), path('logout/', views.logout_view, name='logout'),
 path('dashboard/', views.dashboard, name='dashboard'), path('profiles/new/', views.create_profile, name='create_profile'),
 path('profiles/<int:profile_id>/edit/', views.profile_edit, name='profile_edit'), path('profiles/<int:profile_id>/history/', views.profile_history, name='profile_history'),
 path('analyses/<int:analysis_id>/', views.open_analysis, name='open_analysis'), path('analyses/<int:analysis_id>/pdf/', views.export_analysis_pdf, name='export_analysis_pdf'),
 path('compare/', views.compare_careers, name='compare_careers'),
]
