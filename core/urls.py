from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Accounts
    path('accounts/', views.accounts_list, name='accounts_list'),
    path('accounts/new/', views.account_create, name='account_create'),
    path('accounts/<int:pk>/', views.account_detail, name='account_detail'),
    path('accounts/<int:pk>/edit/', views.account_edit, name='account_edit'),

    # Contacts
    path('contacts/', views.contacts_list, name='contacts_list'),
    path('contacts/new/', views.contact_create, name='contact_create'),
    path('contacts/<int:pk>/', views.contact_detail, name='contact_detail'),
    path('contacts/<int:pk>/edit/', views.contact_edit, name='contact_edit'),

    # Opportunities
    path('opportunities/', views.opportunities_list, name='opportunities_list'),
    path('opportunities/new/', views.opportunity_create, name='opportunity_create'),
    path('opportunities/<int:pk>/', views.opportunity_detail, name='opportunity_detail'),
    path('opportunities/<int:pk>/edit/', views.opportunity_edit, name='opportunity_edit'),

    # Events
    path('events/', views.events_list, name='events_list'),
    path('events/new/', views.event_create, name='event_create'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),
    path('events/<int:pk>/edit/', views.event_edit, name='event_edit'),

    # Admin Deletes
    path('accounts/<int:pk>/delete/', views.account_delete, name='account_delete'),
    path('contacts/<int:pk>/delete/', views.contact_delete, name='contact_delete'),
    path('opportunities/<int:pk>/delete/', views.opportunity_delete, name='opportunity_delete'),
    path('events/<int:pk>/delete/', views.event_delete, name='event_delete'),
]