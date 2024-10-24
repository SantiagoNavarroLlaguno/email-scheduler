from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('send-email/', views.send_email, name='send-email'),
    path('view-emails/', views.view_emails, name='view-emails'),
    path('view-emails/<int:folder_id>/', views.view_emails, name='view-emails-by-folder'),
    path('manage-contact-list/', views.manage_contact_list, name='manage-contact-list'),
    path('manage-folders/', views.manage_folders, name='manage-folders'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('email-success/', views.email_success, name='email-success'),
    path('test/', views.test, name='test')
]
