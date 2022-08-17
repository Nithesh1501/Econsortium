"""djangoproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from econsortium import views
from django.contrib.auth import views as auth_views 
from django.urls import path, include
from rest_framework import routers
router = routers.DefaultRouter()
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView

from django.views.static import serve
from django.urls import re_path


urlpatterns = [
    path('', views.home, name='home'),
    path('list_item/', views.list_item, name='list_item'),
    path('add_items/', views.add_items, name='add_items'),
    path('update_items/<str:pk>/', views.update_items, name="update_items"),
    path('delete_items/<str:pk>/', views.delete_items, name="delete_items"),
    path('asset_detail/<str:pk>/', views.asset_detail, name="asset_detail"),
    path('issue_items/<str:pk>/', views.issue_items, name="issue_items"),
    path('user_issue_items/<str:pk>/', views.user_issue_items, name="user_issue_items"),
    path('receive_items/<str:pk>/', views.receive_items, name="receive_items"),
    path('reorder_level/<str:pk>/', views.reorder_level, name="reorder_level"),
    path('admin/', admin.site.urls),
    path('logout', LogoutView.as_view()),
    #path('api', views.ChartData.as_view()),
    path("accounts/login/", views.login_request, name="login"),
    #path("accounts/accounts/google/login//", views.glogin_request, name="login"),
    path("register", views.register_request, name="register"),
    path("accounts/register/", views.login_request, name="register"),
    path('list_history/', views.list_history, name='list_history'),
    path("login", views.login_request, name="login"),
    path('accounts/', include('allauth.urls')),
    path('add_category/', views.add_category, name='add_category'),
    path("logout", views.logout_request, name= "logout"),
    path("accounts/logout", views.logout_request, name= "logout"),
    path('pie_chart/', views.pie_chart, name='pie_chart'),
    path('bar_chart/', views.bar_chart, name='bar_chart'),
    path('radar_chart/', views.radar_chart, name='radar_chart'),
    path('polar_chart/', views.polar_chart, name='polar_chart'),
    path('line_chart/', views.line_chart, name='line_chart'),
    path('upload/', views.upload_csv, name='upload'),
    path('linear/', views.linear, name='linear'),
    path('api/', include(router.urls)),
    path('api/', include(router.urls))

]

