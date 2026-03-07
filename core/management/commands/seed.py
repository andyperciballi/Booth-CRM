from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.conf import settings
from core.models import Tag, Account, Contact, Opportunity, Event
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Seed the database with realistic test data'

    def handle(self, *args, **kwargs):
        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR('Seed command disabled in production!'))
            return
        # Clear existing data
        Opportunity.objects.all().delete()
        Contact.objects.all().delete()
        Account.objects.all().delete()
        Event.objects.all().delete()
        Tag.objects.all().delete()

        # ===== USERS =====
        # Use existing superuser and create some reps
        admin = User.objects.first()

        rep1, _ = User.objects.get_or_create(username='sarah_rep', defaults={
            'first_name': 'Sarah', 'last_name': 'Rodriguez', 'email': 'sarah@boothcrm.com'
        })
        rep2, _ = User.objects.get_or_create(username='kenji_rep', defaults={
            'first_name': 'Kenji', 'last_name': 'Lee', 'email': 'kenji@boothcrm.com'
        })
        rep3, _ = User.objects.get_or_create(username='amanda_rep', defaults={
            'first_name': 'Amanda', 'last_name': 'Morris', 'email': 'amanda@boothcrm.com'
        })

        users = [admin, rep1, rep2, rep3]

        # ===== TAGS =====
        tag_names = ['Priority', 'Repeat Vendor', 'New Vendor', 'VIP', 
                     'Needs Follow Up', 'High Value', 'Referred', 'Cold']
        tags = [Tag.objects.create(name=t) for t in tag_names]

        # ===== EVENTS =====
        event1 = Event.objects.create(
            name='Fan Expo 2026',
            description='Annual fan convention covering comics, sci-fi, horror, anime and gaming.',
            location='Metro Toronto Convention Centre',
            start_date=date(2026, 8, 27),
            end_date=date(2026, 8, 30),
            status='open',
            total_attendance_cap=100000,
            vendor_capacity=180,
            food_vendor_capacity=20,
            guest_capacity=50,
            panel_room_capacity=30,
            photo_op_capacity=25,
            signing_capacity=40,
            activity_room_capacity=10,
            custom_room_1_name='Draw with the Pros',
            custom_room_1_capacity=8,
            custom_room_2_name='D&D Room',
            custom_room_2_capacity=6,
            custom_room_3_name='Kids Zone',
            custom_room_3_capacity=1,
            event_manager=admin,
        )

        event2 = Event.objects.create(
            name='Fan Expo 2025',
            description='Previous years fan convention.',
            location='Metro Toronto Convention Centre',
            start_date=date(2025, 8, 28),
            end_date=date(2025, 8, 31),
            status='closed',
            total_attendance_cap=95000,
            vendor_capacity=175,
            food_vendor_capacity=18,
            guest_capacity=45,
            panel_room_capacity=28,
            photo_op_capacity=22,
            signing_capacity=38,
            activity_room_capacity=8,
            event_manager=admin,
        )

        event3 = Event.objects.create(
            name='Comic Con Toronto 2026',
            description='Spring comic convention.',
            location='Enercare Centre, Toronto',
            start_date=date(2026, 3, 20),
            end_date=date(2026, 3, 22),
            status='planning',
            total_attendance_cap=40000,
            vendor_capacity=80,
            food_vendor_capacity=10,
            guest_capacity=20,
            panel_room_capacity=12,
            photo_op_capacity=10,
            signing_capacity=15,
            event_manager=rep1,
        )

        events = [event1, event2, event3]

        # ===== ACCOUNTS =====
        accounts_data = [
            {
                'name': 'Artisan Goods Co.',
                'vertical': 'retail',
                'status': 'customer',
                'arr': 42800,
                'city': 'Toronto',
                'state_province': 'Ontario',
                'country': 'Canada',
                'hq_phone': '416-555-0101',
                'general_email': 'info@artisangoods.com',
                'website': 'https://artisangoods.com',
                'account_owner': rep1,
            },
            {
                'name': 'Pacific Candles LLC',
                'vertical': 'retail',
                'status': 'customer',
                'arr': 22600,
                'city': 'Vancouver',
                'state_province': 'British Columbia',
                'country': 'Canada',
                'hq_phone': '604-555-0192',
                'general_email': 'info@pacificcandles.com',
                'website': 'https://pacificcandles.com',
                'account_owner': rep2,
            },
            {
                'name': 'Heritage Leatherworks',
                'vertical': 'retail',
                'status': 'customer',
                'arr': 36200,
                'city': 'Austin',
                'state_province': 'Texas',
                'country': 'USA',
                'hq_phone': '512-555-0144',
                'general_email': 'info@heritageleather.com',
                'website': 'https://heritageleather.com',
                'account_owner': rep3,
            },
            {
                'name': 'Bloom & Grow Botanicals',
                'vertical': 'retail',
                'status': 'customer',
                'arr': 18400,
                'city': 'Seattle',
                'state_province': 'Washington',
                'country': 'USA',
                'hq_phone': '206-555-0177',
                'general_email': 'hello@bloomgrow.com',
                'website': 'https://bloomgrow.com',
                'account_owner': rep1,
            },
            {
                'name': 'Wild Honey Studio',
                'vertical': 'retail',
                'status': 'customer',
                'arr': 9800,
                'city': 'Denver',
                'state_province': 'Colorado',
                'country': 'USA',
                'hq_phone': '720-555-0133',
                'general_email': 'studio@wildhoney.com',
                'account_owner': rep2,
            },
            {
                'name': 'Coastal Prints & Design',
                'vertical': 'retail',
                'status': 'prospect',
                'arr': 7200,
                'city': 'San Diego',
                'state_province': 'California',
                'country': 'USA',
                'hq_phone': '619-555-0155',
                'general_email': 'hello@coastalprints.com',
                'account_owner': rep3,
            },
            {
                'name': 'John Boyega — Special Guest',
                'vertical': 'entertainment',
                'status': 'customer',
                'arr': 85000,
                'city': 'London',
                'state_province': 'England',
                'country': 'UK',
                'general_email': 'bookings@unitedtalent.com',
                'account_owner': admin,
            },
            {
                'name': 'Felicia Day — Special Guest',
                'vertical': 'entertainment',
                'status': 'customer',
                'arr': 45000,
                'city': 'Los Angeles',
                'state_province': 'California',
                'country': 'USA',
                'general_email': 'felicia@paradigmagency.com',
                'account_owner': admin,
            },
            {
                'name': 'NovaTech Gaming',
                'vertical': 'technology',
                'status': 'prospect',
                'arr': 15000,
                'city': 'Montreal',
                'state_province': 'Quebec',
                'country': 'Canada',
                'general_email': 'events@novatech.com',
                'account_owner': rep2,
            },
            {
                'name': 'Dragon Scale Comics',
                'vertical': 'retail',
                'status': 'customer',
                'arr': 12400,
                'city': 'Toronto',
                'state_province': 'Ontario',
                'country': 'Canada',
                'general_email': 'info@dragonscale.com',
                'account_owner': rep1,
            },
        ]

        accounts = []
        for data in accounts_data:
            owner = data.pop('account_owner')
            acc = Account.objects.create(account_owner=owner, **data)
            acc.tags.add(random.choice(tags), random.choice(tags))
            accounts.append(acc)

        # ===== CONTACTS =====
        contacts_data = [
            {
                'first_name': 'Maria', 'last_name': 'Chen',
                'title': 'Owner', 'email': 'maria@artisangoods.com',
                'mobile_phone': '416-555-0201', 'account': accounts[0],
                'contact_owner': rep1, 'is_primary': True, 'status': 'active',
                'follow_up_date': date.today() + timedelta(days=2),
            },
            {
                'first_name': 'Tom', 'last_name': 'Rodriguez',
                'title': 'Sales Director', 'email': 'tom@pacificcandles.com',
                'mobile_phone': '604-555-0202', 'account': accounts[1],
                'contact_owner': rep2, 'is_primary': True, 'status': 'active',
                'follow_up_date': date.today(),
            },
            {
                'first_name': 'James', 'last_name': 'Wu',
                'title': 'Owner', 'email': 'james@heritageleather.com',
                'mobile_phone': '512-555-0203', 'account': accounts[2],
                'contact_owner': rep3, 'is_primary': True, 'status': 'active',
                'follow_up_date': date.today() - timedelta(days=3),
            },
            {
                'first_name': 'Priya', 'last_name': 'Nair',
                'title': 'Founder', 'email': 'priya@bloomgrow.com',
                'mobile_phone': '206-555-0204', 'account': accounts[3],
                'contact_owner': rep1, 'is_primary': True, 'status': 'active',
                'follow_up_date': date.today() + timedelta(days=5),
            },
            {
                'first_name': 'Elena', 'last_name': 'Park',
                'title': 'Creative Director', 'email': 'elena@wildhoney.com',
                'mobile_phone': '720-555-0205', 'account': accounts[4],
                'contact_owner': rep2, 'is_primary': True, 'status': 'active',
                'follow_up_date': date.today() - timedelta(days=1),
            },
            {
                'first_name': 'Anna', 'last_name': 'Kowalski',
                'title': 'Owner', 'email': 'anna@coastalprints.com',
                'mobile_phone': '619-555-0206', 'account': accounts[5],
                'contact_owner': rep3, 'is_primary': True, 'status': 'active',
                'follow_up_date': date.today() + timedelta(days=7),
            },
            {
                'first_name': 'John', 'last_name': 'Boyega',
                'title': 'Actor', 'email': 'bookings@unitedtalent.com',
                'mobile_phone': '44-555-0207', 'account': accounts[6],
                'contact_owner': admin, 'is_primary': True, 'status': 'active',
                'follow_up_date': date.today() + timedelta(days=14),
            },
            {
                'first_name': 'Felicia', 'last_name': 'Day',
                'title': 'Actor / Writer', 'email': 'felicia@paradigmagency.com',
                'mobile_phone': '310-555-0208', 'account': accounts[7],
                'contact_owner': admin, 'is_primary': True, 'status': 'active',
                'follow_up_date': date.today() + timedelta(days=10),
            },
            {
                'first_name': 'Marcus', 'last_name': 'Webb',
                'title': 'Events Manager', 'email': 'marcus@novatech.com',
                'mobile_phone': '514-555-0209', 'account': accounts[8],
                'contact_owner': rep2, 'is_primary': True, 'status': 'active',
                'follow_up_date': date.today() + timedelta(days=3),
            },
            {
                'first_name': 'Lisa', 'last_name': 'Tran',
                'title': 'Owner', 'email': 'lisa@dragonscale.com',
                'mobile_phone': '416-555-0210', 'account': accounts[9],
                'contact_owner': rep1, 'is_primary': True, 'status': 'active',
                'follow_up_date': date.today() - timedelta(days=2),
            },
        ]

        contacts = []
        for data in contacts_data:
            c = Contact.objects.create(**data)
            contacts.append(c)

        # ===== OPPORTUNITIES =====
        opportunities_data = [
            {
                'name': 'Artisan Goods — Fan Expo 2026 Booth',
                'contact': contacts[0], 'account': accounts[0],
                'owner': rep1, 'event': event1,
                'stage': 'negotiating', 'forecast_category': 'in_forecast',
                'opportunity_type': 'vendor', 'booth_size': '10x10',
                'booth_number': 'B-14', 'arr': 3200,
                'close_date': date.today() + timedelta(days=14),
                'source': 'referral',
            },
            {
                'name': 'Pacific Candles — Fan Expo 2026 Booth',
                'contact': contacts[1], 'account': accounts[1],
                'owner': rep2, 'event': event1,
                'stage': 'proposal', 'forecast_category': 'in_forecast',
                'opportunity_type': 'vendor', 'booth_size': 'table_top',
                'arr': 1800,
                'close_date': date.today() + timedelta(days=30),
                'source': 'outbound',
            },
            {
                'name': 'Heritage Leatherworks — Fan Expo 2026 Corner Booth',
                'contact': contacts[2], 'account': accounts[2],
                'owner': rep3, 'event': event1,
                'stage': 'qualified', 'forecast_category': 'stretch',
                'opportunity_type': 'vendor', 'booth_size': '10x20',
                'arr': 5000,
                'close_date': date.today() + timedelta(days=45),
                'source': 'outbound',
            },
            {
                'name': 'Bloom & Grow — Fan Expo 2026 Booth',
                'contact': contacts[3], 'account': accounts[3],
                'owner': rep1, 'event': event1,
                'stage': 'meeting_booked', 'forecast_category': 'in_forecast',
                'opportunity_type': 'vendor', 'booth_size': '10x10',
                'arr': 2400,
                'close_date': date.today() + timedelta(days=21),
                'source': 'inbound_warm',
            },
            {
                'name': 'Wild Honey Studio — Fan Expo 2026',
                'contact': contacts[4], 'account': accounts[4],
                'owner': rep2, 'event': event1,
                'stage': 'closed_won', 'forecast_category': 'in_forecast',
                'opportunity_type': 'food_vendor', 'booth_size': '10x10',
                'booth_number': 'F-03', 'arr': 1600,
                'close_date': date.today() - timedelta(days=5),
                'source': 'inbound_cold',
            },
            {
                'name': 'John Boyega — Fan Expo 2026 Appearance',
                'contact': contacts[6], 'account': accounts[6],
                'owner': admin, 'event': event1,
                'stage': 'negotiating', 'forecast_category': 'in_forecast',
                'opportunity_type': 'guest_appearance',
                'arr': 85000,
                'close_date': date.today() + timedelta(days=60),
                'source': 'outbound',
            },
            {
                'name': 'Felicia Day — Fan Expo 2026 Panel + Signing',
                'contact': contacts[7], 'account': accounts[7],
                'owner': admin, 'event': event1,
                'stage': 'closed_won', 'forecast_category': 'in_forecast',
                'opportunity_type': 'signing',
                'arr': 45000,
                'close_date': date.today() - timedelta(days=10),
                'source': 'referral',
            },
            {
                'name': 'NovaTech Gaming — Sponsor Package',
                'contact': contacts[8], 'account': accounts[8],
                'owner': rep2, 'event': event1,
                'stage': 'interest_shown', 'forecast_category': 'unlikely',
                'opportunity_type': 'sponsor',
                'arr': 15000,
                'close_date': date.today() + timedelta(days=90),
                'source': 'outbound',
            },
            {
                'name': 'Dragon Scale Comics — Fan Expo 2026 Booth',
                'contact': contacts[9], 'account': accounts[9],
                'owner': rep1, 'event': event1,
                'stage': 'closed_won', 'forecast_category': 'in_forecast',
                'opportunity_type': 'vendor', 'booth_size': '10x10',
                'booth_number': 'A-22', 'arr': 2800,
                'close_date': date.today() - timedelta(days=7),
                'source': 'inbound_warm',
            },
            {
                'name': 'Coastal Prints — Comic Con Toronto 2026',
                'contact': contacts[5], 'account': accounts[5],
                'owner': rep3, 'event': event3,
                'stage': 'prospecting', 'forecast_category': 'out_of_forecast',
                'opportunity_type': 'vendor', 'booth_size': 'table_top',
                'arr': 1200,
                'close_date': date.today() + timedelta(days=75),
                'source': 'outbound',
            },
        ]

        for data in opportunities_data:
            opp = Opportunity.objects.create(**data)
            opp.tags.add(random.choice(tags))

        self.stdout.write(self.style.SUCCESS(
            f'Done! Created {len(accounts)} accounts, {len(contacts)} contacts, {len(opportunities_data)} opportunities, {Event.objects.count()} events.'
        ))