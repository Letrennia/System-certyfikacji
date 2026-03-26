from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render
from django.utils import timezone

from ProjektSystemCertyfikacji.models import Certificate, Fraud_report

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

    elif user.is_staff:
        frauds = Fraud_report.objects.order_by('-created_at')
        paginator = Paginator(frauds, 5)
        page_number = request.GET.get('page', 1)
        frauds = paginator.get_page(page_number)
        return render(request, 'notifications/notification_list.html', {'frauds': frauds})
