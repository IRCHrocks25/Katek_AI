from django.contrib import admin
from django.urls import path
from myApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('onboarding/', views.onboarding, name='onboarding'),
    path('api/onboarding/save/', views.onboarding_save, name='onboarding_save'),
    path('api/onboarding/ai-help/', views.onboarding_ai_help, name='onboarding_ai_help'),
    
    # Dashboard routes
    path('dashboard/', views.dashboard_overview, name='dashboard_overview'),
    path('dashboard/sessions/', views.dashboard_sessions, name='dashboard_sessions'),
    path('dashboard/sessions/<int:session_id>/', views.dashboard_session_detail, name='dashboard_session_detail'),
    path('dashboard/sessions/<int:session_id>/update-status/', views.dashboard_update_status, name='dashboard_update_status'),
    path('dashboard/sessions/<int:session_id>/assign/', views.dashboard_assign, name='dashboard_assign'),
    path('dashboard/sessions/<int:session_id>/add-note/', views.dashboard_add_note, name='dashboard_add_note'),
    path('dashboard/sessions/<int:session_id>/generate-summary/', views.dashboard_generate_ai_summary, name='dashboard_generate_ai_summary'),
    path('dashboard/export/csv/', views.dashboard_export_csv, name='dashboard_export_csv'),
]