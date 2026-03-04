from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('accounts/', views.accounts_list, name='accounts_list'),
    path('contacts/', views.contacts_list, name='contacts_list'),
    path('opportunities/', views.opportunities_list, name='opportunities_list'),
]