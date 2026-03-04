from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Account(models.Model):

    VERTICAL_CHOICES = [
        ('retail', 'Retail'),
        ('manufacturing', 'Manufacturing'),
        ('technology', 'Technology'),
        ('healthcare', 'Healthcare'),
        ('financial_services', 'Financial Services'),
        ('education', 'Education'),
        ('energy', 'Energy'),
        ('non_profit', 'Non-Profit'),
        ('entertainment', 'Entertainment'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('prospect', 'Prospect'),
        ('customer', 'Customer'),
        ('inactive', 'Inactive'),
    ]

    # Identity
    name             = models.CharField(max_length=255)
    description      = models.TextField(blank=True, null=True)
    vertical         = models.CharField(max_length=50, choices=VERTICAL_CHOICES, blank=True, null=True)
    website          = models.URLField(blank=True, null=True)
    hq_phone         = models.CharField(max_length=50, blank=True, null=True)
    general_email    = models.EmailField(blank=True, null=True)
    billing_email    = models.EmailField(blank=True, null=True)
    billing_address  = models.CharField(max_length=255, blank=True, null=True)
    tax_id           = models.CharField(max_length=100, blank=True, null=True)
    employee_count   = models.IntegerField(blank=True, null=True)

    # Location
    hq_address       = models.CharField(max_length=255, blank=True, null=True)
    city             = models.CharField(max_length=100, blank=True, null=True)
    state_province   = models.CharField(max_length=100, blank=True, null=True)
    country          = models.CharField(max_length=100, blank=True, null=True)

    # CRM
    status           = models.CharField(max_length=50, choices=STATUS_CHOICES, default='prospect')
    arr              = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    account_owner    = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='accounts')
    outreach_history = models.TextField(blank=True, null=True)
    notes            = models.TextField(blank=True, null=True)
    tags             = models.ManyToManyField('Tag', blank=True)

    # Timestamps
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Contact(models.Model):

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    # Identity
    first_name       = models.CharField(max_length=100)
    last_name        = models.CharField(max_length=100)
    preferred_name   = models.CharField(max_length=100, blank=True, null=True)
    title            = models.CharField(max_length=100, blank=True, null=True)
    email            = models.EmailField(blank=True, null=True)
    email2           = models.EmailField(blank=True, null=True)
    email3           = models.EmailField(blank=True, null=True)
    mobile_phone     = models.CharField(max_length=50, blank=True, null=True)
    home_phone       = models.CharField(max_length=50, blank=True, null=True)
    work_phone       = models.CharField(max_length=50, blank=True, null=True)
    linkedin         = models.URLField(blank=True, null=True)
    address          = models.CharField(max_length=255, blank=True, null=True)
    city             = models.CharField(max_length=100, blank=True, null=True)
    state_province   = models.CharField(max_length=100, blank=True, null=True)
    country          = models.CharField(max_length=100, blank=True, null=True)

    # Relationships
    # opportunities are accessed via contact.opportunities.all() — no field needed here
    account          = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='contacts')
    contact_owner    = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='contacts')

    # CRM
    status           = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active')
    is_primary       = models.BooleanField(default=False)
    follow_up_date   = models.DateField(blank=True, null=True)
    notes            = models.TextField(blank=True, null=True)
    outreach_history = models.TextField(blank=True, null=True)
    tags             = models.ManyToManyField('Tag', blank=True)

    # Timestamps
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Opportunity(models.Model):

    STAGE_CHOICES = [
        ('prospecting', 'Prospecting'),
        ('interest_shown', 'Interest Shown'),
        ('meeting_booked', 'Meeting Booked'),
        ('qualified', 'Qualified'),
        ('proposal', 'Proposal'),
        ('negotiating', 'Negotiating'),
        ('closed_won', 'Closed Won'),
        ('closed_lost', 'Closed Lost'),
    ]

    SOURCE_CHOICES = [
        ('inbound_cold', 'Inbound Cold'),
        ('inbound_warm', 'Inbound Warm'),
        ('outbound', 'Outbound'),
        ('referral', 'Referral'),
        ('event', 'Event'),
        ('other', 'Other'),
    ]
    BOOTH_SIZE_CHOICES = [
        ('none', 'No Booth'),
        ('table_top', 'Table Top'),
        ('10x10', '10x10'),
        ('10x20', '10x20'),
        ('20x20', '20x20'),
        ('20x30', '20x30'),
        ('20x40', '20x40'),
        ('custom', 'Custom'),
    ]
    FORECAST_CHOICES = [
        ('in_forecast', 'In Forecast'),
        ('out_of_forecast', 'Out of Forecast'),
        ('stretch', 'Stretch'),
        ('unlikely', 'Unlikely'),
    ]

    OPPORTUNITY_TYPE_CHOICES = [
        ('vendor', 'Vendor'),
        ('food_vendor', 'Food Vendor'),
        ('guest_appearance', 'Guest Appearance'),
        ('panel', 'Panel'),
        ('photo_op', 'Photo Op'),
        ('signing', 'Signing'),
        ('activity_room', 'Activity Room'),
        ('custom_room', 'Custom Room'),
        ('sponsor', 'Sponsor'),
        ('other', 'Other'),
    ]

    opportunity_type  = models.CharField(max_length=50, choices=OPPORTUNITY_TYPE_CHOICES, blank=True, null=True)
    forecast_category = models.CharField(max_length=50, choices=FORECAST_CHOICES, blank=True, null=True)
    # Identity
    name             = models.CharField(max_length=255)
    description      = models.TextField(blank=True, null=True)

    # Relationships
    # contact is required, account is optional
    contact          = models.ForeignKey(Contact, on_delete=models.PROTECT, related_name='opportunities')
    account          = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='opportunities')
    owner            = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='opportunities')

    # CRM
    stage            = models.CharField(max_length=50, choices=STAGE_CHOICES, default='prospecting')
    arr              = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    close_date       = models.DateField(blank=True, null=True)
    source           = models.CharField(max_length=50, choices=SOURCE_CHOICES, blank=True, null=True)
    follow_up_date   = models.DateField(blank=True, null=True)
    notes            = models.TextField(blank=True, null=True)
    outreach_history = models.TextField(blank=True, null=True)
    tags             = models.ManyToManyField('Tag', blank=True)
    booth_size       = models.CharField(max_length=50, choices=BOOTH_SIZE_CHOICES, blank=True, null=True)
    booth_number     = models.CharField(max_length=50, blank=True, null=True)
    booth_location   = models.CharField(max_length=255, blank=True, null=True)

    event            = models.ForeignKey('Event', on_delete=models.SET_NULL, null=True, blank=True, related_name='opportunities')

    # Timestamps
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class Event(models.Model):

    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ]

    # Identity
    name                    = models.CharField(max_length=255)
    description             = models.TextField(blank=True, null=True)
    location                = models.CharField(max_length=255, blank=True, null=True)
    start_date              = models.DateField(blank=True, null=True)
    end_date                = models.DateField(blank=True, null=True)
    status                  = models.CharField(max_length=50, choices=STATUS_CHOICES, default='planning')

    # Attendance
    total_attendance_cap    = models.IntegerField(blank=True, null=True)

    # Vendor capacity
    vendor_capacity         = models.IntegerField(blank=True, null=True)
    food_vendor_capacity    = models.IntegerField(blank=True, null=True)

    # Guest / celebrity capacity
    guest_capacity          = models.IntegerField(blank=True, null=True)

    # Special attractions / rooms
    panel_room_capacity     = models.IntegerField(blank=True, null=True)
    photo_op_capacity       = models.IntegerField(blank=True, null=True)
    activity_room_capacity  = models.IntegerField(blank=True, null=True)
    signing_capacity        = models.IntegerField(blank=True, null=True)

    # Flexible overflow for anything that doesnt fit above
    # e.g "D&D room", "Draw with the Pros", "Kids Zone"
    custom_room_1_name      = models.CharField(max_length=100, blank=True, null=True)
    custom_room_1_capacity  = models.IntegerField(blank=True, null=True)
    custom_room_2_name      = models.CharField(max_length=100, blank=True, null=True)
    custom_room_2_capacity  = models.IntegerField(blank=True, null=True)
    custom_room_3_name      = models.CharField(max_length=100, blank=True, null=True)
    custom_room_3_capacity  = models.IntegerField(blank=True, null=True)
    custom_room_4_name      = models.CharField(max_length=100, blank=True, null=True)
    custom_room_4_capacity  = models.IntegerField(blank=True, null=True)

    # Ownership
    event_manager           = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='events')

    # Timestamps
    created_at              = models.DateTimeField(auto_now_add=True)
    updated_at              = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name