from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def add_certificate(request):
    return render(request, 'company/add_certificate.html')