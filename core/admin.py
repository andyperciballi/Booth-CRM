from django.contrib import admin
from .models import Tag, Account, Contact, Opportunity, Event

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'vertical', 'status', 'arr', 'account_owner', 'city', 'country', 'created_at')
    list_filter = ('status', 'vertical', 'country')
    search_fields = ('name', 'general_email', 'city')
    ordering = ('-created_at',)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'title', 'email', 'account', 'contact_owner', 'status', 'follow_up_date')
    list_filter = ('status', 'is_primary')
    search_fields = ('first_name', 'last_name', 'email', 'account__name')
    ordering = ('-created_at',)


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('name', 'account', 'contact', 'stage', 'forecast_category', 'opportunity_type', 'arr', 'close_date', 'owner')
    list_filter = ('stage', 'forecast_category', 'opportunity_type', 'source')
    search_fields = ('name', 'account__name', 'contact__first_name', 'contact__last_name')
    ordering = ('-created_at',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'start_date', 'end_date', 'location', 'vendor_capacity', 'guest_capacity', 'event_manager')
    list_filter = ('status',)
    search_fields = ('name', 'location')
    ordering = ('-start_date',)