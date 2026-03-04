from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def accounts_list(request):
    return render(request, 'accounts/list.html')

@login_required
def contacts_list(request):
    return render(request, 'contacts/list.html')

@login_required
def opportunities_list(request):
    return render(request, 'opportunities/list.html')