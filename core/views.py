from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth import login
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import timedelta, date
from .models import Account, Contact, Opportunity, Event, ActivityLog


# ===== HELPERS =====
def get_user_role(user):
    if user.is_superuser:
        return 'admin'
    groups = user.groups.values_list('name', flat=True)
    if 'admin' in groups:
        return 'admin'
    if 'manager' in groups:
        return 'manager'
    if 'event_manager' in groups:
        return 'event_manager'
    return 'sales_rep'


def is_viewer(user):
    if not user.is_authenticated:
        return True
    return user.groups.filter(name='viewer').exists() and not user.is_superuser


def log_activity(action, description, performed_by, account=None, contact=None, opportunity=None, event=None):
    ActivityLog.objects.create(
        action=action,
        description=description,
        performed_by=performed_by,
        account=account,
        contact=contact,
        opportunity=opportunity,
        event=event,
    )


def get_opportunity_changes(old, new_data):
    changes = []
    fields = [
        ('stage', 'Stage'),
        ('arr', 'ARR'),
        ('forecast_category', 'Forecast'),
        ('close_date', 'Close Date'),
        ('opportunity_type', 'Type'),
        ('booth_size', 'Booth Size'),
        ('booth_number', 'Booth Number'),
    ]
    for field, label in fields:
        old_val = getattr(old, field)
        new_val = new_data.get(field)
        if str(old_val) != str(new_val):
            changes.append(f"{label} changed from '{old_val}' to '{new_val}'")
    return changes


def get_account_changes(old, new_data):
    changes = []
    fields = [
        ('status', 'Status'),
        ('arr', 'ARR'),
        ('account_owner', 'Owner'),
        ('vertical', 'Vertical'),
    ]
    for field, label in fields:
        old_val = getattr(old, field)
        new_val = new_data.get(field)
        if str(old_val) != str(new_val):
            changes.append(f"{label} changed from '{old_val}' to '{new_val}'")
    return changes


def get_contact_changes(old, new_data):
    changes = []
    fields = [
        ('status', 'Status'),
        ('follow_up_date', 'Follow Up Date'),
        ('contact_owner', 'Owner'),
        ('title', 'Title'),
    ]
    for field, label in fields:
        old_val = getattr(old, field)
        new_val = new_data.get(field)
        if str(old_val) != str(new_val):
            changes.append(f"{label} changed from '{old_val}' to '{new_val}'")
    return changes


# ===== AUTH =====
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            return render(request, 'auth/register.html', {'error': 'Passwords do not match'})

        if User.objects.filter(username=username).exists():
            return render(request, 'auth/register.html', {'error': 'Username already taken'})

        user = User.objects.create_user(username=username, email=email, password=password1)
        viewer_group = Group.objects.get(name='viewer')
        user.groups.add(viewer_group)
        login(request, user)
        return redirect('dashboard')

    return render(request, 'auth/register.html')


# ===== DASHBOARD =====
@login_required
def dashboard(request):
    user = request.user
    role = get_user_role(user)
    today = date.today()
    ninety_days = today + timedelta(days=90)
    ninety_days_ago = today - timedelta(days=90)

    if role in ['admin', 'manager']:
        open_opps = Opportunity.objects.exclude(stage__in=['closed_won', 'closed_lost'])
        forecast_arr = Opportunity.objects.filter(
            close_date__range=[today, ninety_days]
        ).exclude(stage='closed_lost').aggregate(Sum('arr'))['arr__sum'] or 0

        pipeline_by_rep = []
        for rep in User.objects.all():
            rep_open = Opportunity.objects.filter(
                owner=rep
            ).exclude(stage__in=['closed_won', 'closed_lost'])
            rep_total = rep_open.aggregate(Sum('arr'))['arr__sum'] or 0
            if rep_total > 0:
                pipeline_by_rep.append({
                    'name': rep.get_full_name() or rep.username,
                    'total': rep_total,
                    'count': rep_open.count(),
                })

        overdue_followups = Contact.objects.filter(
            follow_up_date__lte=today
        ).order_by('follow_up_date')[:10]

        upcoming_events = Event.objects.filter(
            status__in=['open', 'planning']
        ).order_by('start_date')[:5]

        context = {
            'role': role,
            'is_viewer': is_viewer(user),
            'forecast_arr': forecast_arr,
            'open_opps_count': open_opps.count(),
            'open_opps_value': open_opps.aggregate(Sum('arr'))['arr__sum'] or 0,
            'pipeline_by_rep': pipeline_by_rep,
            'overdue_followups': overdue_followups,
            'upcoming_events': upcoming_events,
        }

    else:
        my_opps = Opportunity.objects.filter(owner=user).exclude(stage__in=['closed_won', 'closed_lost'])
        my_forecast = Opportunity.objects.filter(
            owner=user,
            close_date__range=[today, ninety_days]
        ).exclude(stage='closed_lost').aggregate(Sum('arr'))['arr__sum'] or 0

        my_closed_won = Opportunity.objects.filter(
            owner=user, stage='closed_won'
        ).aggregate(Sum('arr'))['arr__sum'] or 0

        my_followups = Contact.objects.filter(
            contact_owner=user,
            follow_up_date__lte=today
        ).order_by('follow_up_date')[:10]

        pipeline_by_stage = []
        for value, label in Opportunity.STAGE_CHOICES:
            if value not in ['closed_won', 'closed_lost']:
                stage_opps = my_opps.filter(stage=value)
                total = stage_opps.aggregate(Sum('arr'))['arr__sum'] or 0
                pipeline_by_stage.append({
                    'stage': label,
                    'count': stage_opps.count(),
                    'total': total,
                })

        context = {
            'role': role,
            'is_viewer': is_viewer(user),
            'my_forecast': my_forecast,
            'my_closed_won': my_closed_won,
            'my_open_count': my_opps.count(),
            'my_open_value': my_opps.aggregate(Sum('arr'))['arr__sum'] or 0,
            'my_followups': my_followups,
            'pipeline_by_stage': pipeline_by_stage,
        }

    return render(request, 'dashboard.html', context)


# ===== ACCOUNTS =====
def accounts_list(request):
    accounts = Account.objects.all().order_by('-created_at')

    query = request.GET.get('q')
    if query:
        accounts = accounts.filter(
            Q(name__icontains=query) |
            Q(city__icontains=query) |
            Q(general_email__icontains=query) |
            Q(vertical__icontains=query)
        )

    status = request.GET.get('status')
    if status:
        accounts = accounts.filter(status=status)

    vertical = request.GET.get('vertical')
    if vertical:
        accounts = accounts.filter(vertical=vertical)

    owner = request.GET.get('owner')
    if owner:
        accounts = accounts.filter(account_owner__id=owner)

    context = {
        'accounts': accounts,
        'query': query or '',
        'selected_status': status or '',
        'selected_vertical': vertical or '',
        'selected_owner': owner or '',
        'status_choices': Account.STATUS_CHOICES,
        'vertical_choices': Account.VERTICAL_CHOICES,
        'owners': User.objects.filter(accounts__isnull=False).distinct(),
        'is_viewer': is_viewer(request.user),
    }
    return render(request, 'accounts/list.html', context)


@login_required
def account_create(request):
    if request.method == 'POST':
        new_data = request.POST
        account = Account.objects.create(
            name=new_data.get('name'),
            description=new_data.get('description') or None,
            vertical=new_data.get('vertical') or None,
            website=new_data.get('website') or None,
            hq_phone=new_data.get('hq_phone') or None,
            general_email=new_data.get('general_email') or None,
            billing_email=new_data.get('billing_email') or None,
            billing_address=new_data.get('billing_address') or None,
            tax_id=new_data.get('tax_id') or None,
            employee_count=new_data.get('employee_count') or None,
            hq_address=new_data.get('hq_address') or None,
            city=new_data.get('city') or None,
            state_province=new_data.get('state_province') or None,
            country=new_data.get('country') or None,
            status=new_data.get('status') or 'prospect',
            arr=new_data.get('arr') or None,
            notes=new_data.get('notes') or None,
            outreach_history=new_data.get('outreach_history') or None,
            account_owner=User.objects.get(pk=new_data.get('account_owner')) if new_data.get('account_owner') else None,
        )
        log_activity(
            action='created',
            description=f'Account created by {request.user.username}',
            performed_by=request.user,
            account=account,
        )
        return redirect('account_detail', pk=account.pk)

    context = {
        'vertical_choices': Account.VERTICAL_CHOICES,
        'status_choices': Account.STATUS_CHOICES,
        'users': User.objects.all(),
        'is_viewer': is_viewer(request.user),
    }
    return render(request, 'accounts/create.html', context)


def account_detail(request, pk):
    account = get_object_or_404(Account, pk=pk)
    contacts = account.contacts.all()
    opportunities = account.opportunities.all().order_by('-created_at')
    activity_logs = account.activity_logs.all().order_by('-created_at')[:50]

    total_arr = opportunities.filter(stage='closed_won').aggregate(Sum('arr'))['arr__sum'] or 0
    open_pipeline = opportunities.exclude(
        stage__in=['closed_won', 'closed_lost']
    ).aggregate(Sum('arr'))['arr__sum'] or 0

    context = {
        'account': account,
        'contacts': contacts,
        'opportunities': opportunities,
        'activity_logs': activity_logs,
        'total_arr': total_arr,
        'open_pipeline': open_pipeline,
        'is_viewer': is_viewer(request.user),
    }
    return render(request, 'accounts/detail.html', context)


@login_required
def account_edit(request, pk):
    account = get_object_or_404(Account, pk=pk)

    if request.method == 'POST':
        old = Account.objects.get(pk=pk)
        new_data = request.POST
        changes = get_account_changes(old, new_data)

        account.name = new_data.get('name', account.name)
        account.description = new_data.get('description') or None
        account.vertical = new_data.get('vertical') or None
        account.website = new_data.get('website') or None
        account.hq_phone = new_data.get('hq_phone') or None
        account.general_email = new_data.get('general_email') or None
        account.billing_email = new_data.get('billing_email') or None
        account.billing_address = new_data.get('billing_address') or None
        account.tax_id = new_data.get('tax_id') or None
        account.employee_count = new_data.get('employee_count') or None
        account.hq_address = new_data.get('hq_address') or None
        account.city = new_data.get('city') or None
        account.state_province = new_data.get('state_province') or None
        account.country = new_data.get('country') or None
        account.status = new_data.get('status', account.status)
        account.arr = new_data.get('arr') or None
        account.notes = new_data.get('notes') or None
        account.outreach_history = new_data.get('outreach_history') or None

        owner_id = new_data.get('account_owner')
        account.account_owner = User.objects.get(pk=owner_id) if owner_id else None
        account.save()

        if changes:
            log_activity(
                action='updated',
                description=' | '.join(changes),
                performed_by=request.user,
                account=account,
            )
        return redirect('account_detail', pk=pk)

    context = {
        'account': account,
        'vertical_choices': Account.VERTICAL_CHOICES,
        'status_choices': Account.STATUS_CHOICES,
        'users': User.objects.all(),
        'is_viewer': is_viewer(request.user),
    }
    return render(request, 'accounts/edit.html', context)

@login_required
def account_delete(request, pk):
    if not request.user.is_superuser and not get_user_role(request.user) == 'admin':
        return redirect('account_detail', pk=pk)
    account = get_object_or_404(Account, pk=pk)
    if request.method == 'POST':
        account.delete()
        return redirect('accounts_list')
    return redirect('account_detail', pk=pk)

# ===== CONTACTS =====
def contacts_list(request):
    contacts = Contact.objects.all().order_by('-created_at')

    query = request.GET.get('q')
    if query:
        contacts = contacts.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(title__icontains=query) |
            Q(account__name__icontains=query)
        )

    status = request.GET.get('status')
    if status:
        contacts = contacts.filter(status=status)

    owner = request.GET.get('owner')
    if owner:
        contacts = contacts.filter(contact_owner__id=owner)

    context = {
        'contacts': contacts,
        'query': query or '',
        'selected_status': status or '',
        'selected_owner': owner or '',
        'status_choices': Contact.STATUS_CHOICES,
        'owners': User.objects.filter(contacts__isnull=False).distinct(),
        'is_viewer': is_viewer(request.user),
    }
    return render(request, 'contacts/list.html', context)


@login_required
def contact_create(request):
    if request.method == 'POST':
        new_data = request.POST
        contact = Contact.objects.create(
            first_name=new_data.get('first_name'),
            last_name=new_data.get('last_name'),
            preferred_name=new_data.get('preferred_name') or None,
            title=new_data.get('title') or None,
            email=new_data.get('email') or None,
            email2=new_data.get('email2') or None,
            email3=new_data.get('email3') or None,
            mobile_phone=new_data.get('mobile_phone') or None,
            work_phone=new_data.get('work_phone') or None,
            home_phone=new_data.get('home_phone') or None,
            linkedin=new_data.get('linkedin') or None,
            address=new_data.get('address') or None,
            city=new_data.get('city') or None,
            state_province=new_data.get('state_province') or None,
            country=new_data.get('country') or None,
            status=new_data.get('status') or 'active',
            is_primary=new_data.get('is_primary') == 'on',
            follow_up_date=new_data.get('follow_up_date') or None,
            notes=new_data.get('notes') or None,
            outreach_history=new_data.get('outreach_history') or None,
            account=Account.objects.get(pk=new_data.get('account')) if new_data.get('account') else None,
            contact_owner=User.objects.get(pk=new_data.get('contact_owner')) if new_data.get('contact_owner') else None,
        )
        log_activity(
            action='created',
            description=f'Contact created by {request.user.username}',
            performed_by=request.user,
            contact=contact,
        )
        return redirect('contact_detail', pk=contact.pk)

    context = {
        'status_choices': Contact.STATUS_CHOICES,
        'users': User.objects.all(),
        'accounts': Account.objects.all().order_by('name'),
        'is_viewer': is_viewer(request.user),
    }
    return render(request, 'contacts/create.html', context)


def contact_detail(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    opportunities = contact.opportunities.all().order_by('-created_at')
    activity_logs = contact.activity_logs.all().order_by('-created_at')[:50]

    context = {
        'contact': contact,
        'opportunities': opportunities,
        'activity_logs': activity_logs,
        'is_viewer': is_viewer(request.user),
    }
    return render(request, 'contacts/detail.html', context)


@login_required
def contact_edit(request, pk):
    contact = get_object_or_404(Contact, pk=pk)

    if request.method == 'POST':
        old = Contact.objects.get(pk=pk)
        new_data = request.POST
        changes = get_contact_changes(old, new_data)

        contact.first_name = new_data.get('first_name', contact.first_name)
        contact.last_name = new_data.get('last_name', contact.last_name)
        contact.preferred_name = new_data.get('preferred_name') or None
        contact.title = new_data.get('title') or None
        contact.email = new_data.get('email') or None
        contact.email2 = new_data.get('email2') or None
        contact.email3 = new_data.get('email3') or None
        contact.mobile_phone = new_data.get('mobile_phone') or None
        contact.home_phone = new_data.get('home_phone') or None
        contact.work_phone = new_data.get('work_phone') or None
        contact.linkedin = new_data.get('linkedin') or None
        contact.address = new_data.get('address') or None
        contact.city = new_data.get('city') or None
        contact.state_province = new_data.get('state_province') or None
        contact.country = new_data.get('country') or None
        contact.status = new_data.get('status', contact.status)
        contact.is_primary = new_data.get('is_primary') == 'on'
        contact.follow_up_date = new_data.get('follow_up_date') or None
        contact.notes = new_data.get('notes') or None
        contact.outreach_history = new_data.get('outreach_history') or None
        contact.account = Account.objects.get(pk=new_data.get('account')) if new_data.get('account') else None
        contact.contact_owner = User.objects.get(pk=new_data.get('contact_owner')) if new_data.get('contact_owner') else None
        contact.save()

        if changes:
            log_activity(
                action='updated',
                description=' | '.join(changes),
                performed_by=request.user,
                contact=contact,
            )
        return redirect('contact_detail', pk=pk)

    context = {
        'contact': contact,
        'status_choices': Contact.STATUS_CHOICES,
        'users': User.objects.all(),
        'accounts': Account.objects.all().order_by('name'),
        'is_viewer': is_viewer(request.user),
    }
    return render(request, 'contacts/edit.html', context)

@login_required
def contact_delete(request, pk):
    if not request.user.is_superuser and not get_user_role(request.user) == 'admin':
        return redirect('contact_detail', pk=pk)
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == 'POST':
        contact.delete()
        return redirect('contacts_list')
    return redirect('contact_detail', pk=pk)

# ===== OPPORTUNITIES =====
def opportunities_list(request):
    opportunities = Opportunity.objects.all().order_by('-created_at')

    query = request.GET.get('q')
    if query:
        opportunities = opportunities.filter(
            Q(name__icontains=query) |
            Q(account__name__icontains=query) |
            Q(contact__first_name__icontains=query) |
            Q(contact__last_name__icontains=query)
        )

    stage = request.GET.get('stage')
    if stage:
        opportunities = opportunities.filter(stage=stage)

    forecast = request.GET.get('forecast')
    if forecast:
        opportunities = opportunities.filter(forecast_category=forecast)

    opp_type = request.GET.get('type')
    if opp_type:
        opportunities = opportunities.filter(opportunity_type=opp_type)

    event = request.GET.get('event')
    if event:
        opportunities = opportunities.filter(event__id=event)

    owner = request.GET.get('owner')
    if owner:
        opportunities = opportunities.filter(owner__id=owner)

    context = {
        'opportunities': opportunities,
        'query': query or '',
        'selected_stage': stage or '',
        'selected_forecast': forecast or '',
        'selected_type': opp_type or '',
        'selected_event': event or '',
        'selected_owner': owner or '',
        'stage_choices': Opportunity.STAGE_CHOICES,
        'forecast_choices': Opportunity.FORECAST_CHOICES,
        'type_choices': Opportunity.OPPORTUNITY_TYPE_CHOICES,
        'events': Event.objects.all().order_by('start_date'),
        'owners': User.objects.filter(opportunities__isnull=False).distinct(),
        'is_viewer': is_viewer(request.user),
    }
    return render(request, 'opportunities/list.html', context)


@login_required
def opportunity_create(request):
    if request.method == 'POST':
        new_data = request.POST
        opportunity = Opportunity.objects.create(
            name=new_data.get('name'),
            description=new_data.get('description') or None,
            stage=new_data.get('stage') or 'prospecting',
            forecast_category=new_data.get('forecast_category') or None,
            opportunity_type=new_data.get('opportunity_type') or None,
            arr=new_data.get('arr') or None,
            close_date=new_data.get('close_date') or None,
            follow_up_date=new_data.get('follow_up_date') or None,
            source=new_data.get('source') or None,
            booth_size=new_data.get('booth_size') or None,
            booth_number=new_data.get('booth_number') or None,
            booth_location=new_data.get('booth_location') or None,
            notes=new_data.get('notes') or None,
            outreach_history=new_data.get('outreach_history') or None,
            contact=Contact.objects.get(pk=new_data.get('contact')),
            account=Account.objects.get(pk=new_data.get('account')) if new_data.get('account') else None,
            owner=User.objects.get(pk=new_data.get('owner')) if new_data.get('owner') else None,
            event=Event.objects.get(pk=new_data.get('event')) if new_data.get('event') else None,
        )
        log_activity(
            action='created',
            description=f'Opportunity created by {request.user.username}',
            performed_by=request.user,
            opportunity=opportunity,
        )
        return redirect('opportunity_detail', pk=opportunity.pk)

    context = {
        'stage_choices': Opportunity.STAGE_CHOICES,
        'forecast_choices': Opportunity.FORECAST_CHOICES,
        'type_choices': Opportunity.OPPORTUNITY_TYPE_CHOICES,
        'source_choices': Opportunity.SOURCE_CHOICES,
        'booth_size_choices': Opportunity.BOOTH_SIZE_CHOICES,
        'users': User.objects.all(),
        'events': Event.objects.all().order_by('start_date'),
        'contacts': Contact.objects.all().order_by('last_name'),
        'accounts': Account.objects.all().order_by('name'),
        'is_viewer': is_viewer(request.user),
    }
    return render(request, 'opportunities/create.html', context)


def opportunity_detail(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk)
    activity_logs = opportunity.activity_logs.all().order_by('-created_at')[:50]

    context = {
        'opportunity': opportunity,
        'activity_logs': activity_logs,
        'is_viewer': is_viewer(request.user),
    }
    return render(request, 'opportunities/detail.html', context)


@login_required
def opportunity_edit(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk)

    if request.method == 'POST':
        old = Opportunity.objects.get(pk=pk)
        new_data = request.POST
        changes = get_opportunity_changes(old, new_data)

        opportunity.name = new_data.get('name', opportunity.name)
        opportunity.description = new_data.get('description') or None
        opportunity.stage = new_data.get('stage', opportunity.stage)
        opportunity.forecast_category = new_data.get('forecast_category') or None
        opportunity.opportunity_type = new_data.get('opportunity_type') or None
        opportunity.arr = new_data.get('arr') or None
        opportunity.close_date = new_data.get('close_date') or None
        opportunity.follow_up_date = new_data.get('follow_up_date') or None
        opportunity.source = new_data.get('source') or None
        opportunity.booth_size = new_data.get('booth_size') or None
        opportunity.booth_number = new_data.get('booth_number') or None
        opportunity.booth_location = new_data.get('booth_location') or None
        opportunity.notes = new_data.get('notes') or None
        opportunity.outreach_history = new_data.get('outreach_history') or None
        opportunity.contact = Contact.objects.get(pk=new_data.get('contact')) if new_data.get('contact') else opportunity.contact
        opportunity.account = Account.objects.get(pk=new_data.get('account')) if new_data.get('account') else None
        opportunity.owner = User.objects.get(pk=new_data.get('owner')) if new_data.get('owner') else None
        opportunity.event = Event.objects.get(pk=new_data.get('event')) if new_data.get('event') else None
        opportunity.save()

        action = 'stage_changed' if any('Stage changed' in c for c in changes) else 'updated'
        if changes:
            log_activity(
                action=action,
                description=' | '.join(changes),
                performed_by=request.user,
                opportunity=opportunity,
            )
        return redirect('opportunity_detail', pk=pk)

    context = {
        'opportunity': opportunity,
        'stage_choices': Opportunity.STAGE_CHOICES,
        'forecast_choices': Opportunity.FORECAST_CHOICES,
        'type_choices': Opportunity.OPPORTUNITY_TYPE_CHOICES,
        'source_choices': Opportunity.SOURCE_CHOICES,
        'booth_size_choices': Opportunity.BOOTH_SIZE_CHOICES,
        'users': User.objects.all(),
        'events': Event.objects.all().order_by('start_date'),
        'contacts': Contact.objects.all().order_by('last_name'),
        'accounts': Account.objects.all().order_by('name'),
        'is_viewer': is_viewer(request.user),
    }
    return render(request, 'opportunities/edit.html', context)

@login_required
def opportunity_delete(request, pk):
    if not request.user.is_superuser and not get_user_role(request.user) == 'admin':
        return redirect('opportunity_detail', pk=pk)
    opportunity = get_object_or_404(Opportunity, pk=pk)
    if request.method == 'POST':
        opportunity.delete()
        return redirect('opportunities_list')
    return redirect('opportunity_detail', pk=pk)

# ===== EVENTS =====
def events_list(request):
    events = Event.objects.all().order_by('-start_date')

    query = request.GET.get('q')
    if query:
        events = events.filter(
            Q(name__icontains=query) |
            Q(location__icontains=query)
        )

    status = request.GET.get('status')
    if status:
        events = events.filter(status=status)

    context = {
        'events': events,
        'query': query or '',
        'selected_status': status or '',
        'status_choices': Event.STATUS_CHOICES,
        'is_viewer': is_viewer(request.user),
    }
    return render(request, 'events/list.html', context)


@login_required
def event_create(request):
    if request.method == 'POST':
        new_data = request.POST
        event = Event.objects.create(
            name=new_data.get('name'),
            description=new_data.get('description') or None,
            location=new_data.get('location') or None,
            start_date=new_data.get('start_date') or None,
            end_date=new_data.get('end_date') or None,
            status=new_data.get('status') or 'planning',
            total_attendance_cap=new_data.get('total_attendance_cap') or None,
            vendor_capacity=new_data.get('vendor_capacity') or None,
            food_vendor_capacity=new_data.get('food_vendor_capacity') or None,
            guest_capacity=new_data.get('guest_capacity') or None,
            panel_room_capacity=new_data.get('panel_room_capacity') or None,
            photo_op_capacity=new_data.get('photo_op_capacity') or None,
            signing_capacity=new_data.get('signing_capacity') or None,
            activity_room_capacity=new_data.get('activity_room_capacity') or None,
            custom_room_1_name=new_data.get('custom_room_1_name') or None,
            custom_room_1_capacity=new_data.get('custom_room_1_capacity') or None,
            custom_room_2_name=new_data.get('custom_room_2_name') or None,
            custom_room_2_capacity=new_data.get('custom_room_2_capacity') or None,
            custom_room_3_name=new_data.get('custom_room_3_name') or None,
            custom_room_3_capacity=new_data.get('custom_room_3_capacity') or None,
            custom_room_4_name=new_data.get('custom_room_4_name') or None,
            custom_room_4_capacity=new_data.get('custom_room_4_capacity') or None,
            event_manager=User.objects.get(pk=new_data.get('event_manager')) if new_data.get('event_manager') else None,
        )
        log_activity(
            action='created',
            description=f'Event created by {request.user.username}',
            performed_by=request.user,
            event=event,
        )
        return redirect('event_detail', pk=event.pk)

    context = {
        'status_choices': Event.STATUS_CHOICES,
        'users': User.objects.all(),
        'is_viewer': is_viewer(request.user),
    }
    return render(request, 'events/create.html', context)


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    opportunities = event.opportunities.all().order_by('-created_at')
    activity_logs = event.activity_logs.all().order_by('-created_at')[:50]

    won_vendors = opportunities.filter(stage='closed_won', opportunity_type='vendor').count()
    won_food_vendors = opportunities.filter(stage='closed_won', opportunity_type='food_vendor').count()
    won_guests = opportunities.filter(stage='closed_won', opportunity_type='guest_appearance').count()
    won_signings = opportunities.filter(stage='closed_won', opportunity_type='signing').count()
    won_panels = opportunities.filter(stage='closed_won', opportunity_type='panel').count()
    won_photo_ops = opportunities.filter(stage='closed_won', opportunity_type='photo_op').count()

    total_revenue = opportunities.filter(stage='closed_won').aggregate(Sum('arr'))['arr__sum'] or 0
    open_pipeline = opportunities.exclude(stage__in=['closed_won', 'closed_lost']).aggregate(Sum('arr'))['arr__sum'] or 0

    context = {
        'event': event,
        'opportunities': opportunities,
        'activity_logs': activity_logs,
        'won_vendors': won_vendors,
        'won_food_vendors': won_food_vendors,
        'won_guests': won_guests,
        'won_signings': won_signings,
        'won_panels': won_panels,
        'won_photo_ops': won_photo_ops,
        'total_revenue': total_revenue,
        'open_pipeline': open_pipeline,
        'is_viewer': is_viewer(request.user),
    }
    return render(request, 'events/detail.html', context)


@login_required
def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if request.method == 'POST':
        new_data = request.POST
        event.name = new_data.get('name', event.name)
        event.description = new_data.get('description') or None
        event.location = new_data.get('location') or None
        event.start_date = new_data.get('start_date') or None
        event.end_date = new_data.get('end_date') or None
        event.status = new_data.get('status', event.status)
        event.total_attendance_cap = new_data.get('total_attendance_cap') or None
        event.vendor_capacity = new_data.get('vendor_capacity') or None
        event.food_vendor_capacity = new_data.get('food_vendor_capacity') or None
        event.guest_capacity = new_data.get('guest_capacity') or None
        event.panel_room_capacity = new_data.get('panel_room_capacity') or None
        event.photo_op_capacity = new_data.get('photo_op_capacity') or None
        event.signing_capacity = new_data.get('signing_capacity') or None
        event.activity_room_capacity = new_data.get('activity_room_capacity') or None
        event.custom_room_1_name = new_data.get('custom_room_1_name') or None
        event.custom_room_1_capacity = new_data.get('custom_room_1_capacity') or None
        event.custom_room_2_name = new_data.get('custom_room_2_name') or None
        event.custom_room_2_capacity = new_data.get('custom_room_2_capacity') or None
        event.custom_room_3_name = new_data.get('custom_room_3_name') or None
        event.custom_room_3_capacity = new_data.get('custom_room_3_capacity') or None
        event.custom_room_4_name = new_data.get('custom_room_4_name') or None
        event.custom_room_4_capacity = new_data.get('custom_room_4_capacity') or None
        event.event_manager = User.objects.get(pk=new_data.get('event_manager')) if new_data.get('event_manager') else None
        event.save()

        log_activity(
            action='updated',
            description=f'Event updated by {request.user.username}',
            performed_by=request.user,
            event=event,
        )
        return redirect('event_detail', pk=pk)

    context = {
        'event': event,
        'status_choices': Event.STATUS_CHOICES,
        'users': User.objects.all(),
        'is_viewer': is_viewer(request.user),
    }
    return render(request, 'events/edit.html', context)

@login_required
def event_delete(request, pk):
    if not request.user.is_superuser and not get_user_role(request.user) == 'admin':
        return redirect('event_detail', pk=pk)
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.delete()
        return redirect('events_list')
    return redirect('event_detail', pk=pk)