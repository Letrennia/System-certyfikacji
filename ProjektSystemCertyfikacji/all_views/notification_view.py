from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from ProjektSystemCertyfikacji.models import Certificate


@login_required
def show_notifications(request):
    user = request.user
    today = timezone.now()

    if hasattr(user, 'company_user'):
        cert = Certificate.objects.filter(holder_company_id=user.company_user,valid_to__gte=today,
                                          valid_to__lte=today+timedelta(days=3)) #trzy dni do wygasniecia
        return render(request, 'notification_tab.html', {'cert': cert})

    elif hasattr(user, 'certifying_unit'):
        cert = Certificate.objects.filter(issued_by_certifying_unit_id=user.certifying_unit, valid_to__gte=today,
                                          valid_to__lte=today+timedelta(days=3)) #trzy dni do wygasniecia
        return render(request, 'notification_tab.html', {'cert': cert})

