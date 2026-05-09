from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from ..models import Certifying_unit, Company
from django.db.models import Q

@login_required
def acc_dashboard(request):
    if not request.user.is_superuser:
        return render(request, 'product_all_accounts/error.html', {
            'msg': 'Brak uprawnień - dostęp tylko dla adminów'
        })

    cert_units = Certifying_unit.objects.all()
    company_units = Company.objects.all()

    cert_search = request.GET.get('cert_search', '')

    cert_user = request.GET.get('cert_user', '')
    cert_name = request.GET.get('cert_name', '')
    cert_address = request.GET.get('cert_address', '')
    cert_unit_code = request.GET.get('cert_unit_code', '')
    cert_is_approved = request.GET.get('cert_is_approved', '')

    company_search = request.GET.get('company_search', '')

    company_user = request.GET.get('company_user', '')
    company_name = request.GET.get('company_name', '')
    company_type = request.GET.get('company_type', '')
    company_email = request.GET.get('company_email', '')
    company_country = request.GET.get('company_country', '')
    company_address = request.GET.get('company_address', '')
    company_registration_number = request.GET.get('company_registration_number', '')
    company_website = request.GET.get('company_website', '')
    company_is_approved = request.GET.get('company_is_approved', '')


    if cert_search:
        cert_units = cert_units.filter(Q(name__icontains=cert_search) | Q(user__username__icontains=cert_search))
    if cert_is_approved != '':
        if cert_is_approved.lower() == 'true':
            cert_units = cert_units.filter(is_approved=True)
        elif cert_is_approved.lower() == 'false':
            cert_units = cert_units.filter(is_approved=False)

    if company_search:
        company_units = company_units.filter(Q(name__icontains=company_search) | Q(user__username__icontains=company_search))
    if company_is_approved != '':
        if company_is_approved.lower() == 'true':
            company_units = company_units.filter(is_approved=True)
        elif company_is_approved.lower() == 'false':
            company_units = company_units.filter(is_approved=False)


    if request.method == 'POST':
        action = request.POST.get('action')
        pk = request.POST.get('pk')
        if action == 'delete_cert':
            Certifying_unit.objects.filter(certifying_unit_id=pk).delete()

        elif action == 'edit_cert':
            is_approved = request.POST.get('is_approved') == 'true'
            cert = Certifying_unit.objects.filter(certifying_unit_id=pk).first()
            if cert:
                cert.is_approved = is_approved
                cert.save()
                cert.user.is_active = is_approved
                cert.user.save()

        elif action == 'delete_company':
            Company.objects.filter(company_id=pk).delete()

        elif action == 'edit_company':
            is_approved = request.POST.get('is_approved') == 'true'
            company = Company.objects.filter(company_id=pk).first()
            if company:
                company.is_approved = is_approved
                company.save()
                company.user.is_active = is_approved
                company.user.save()


    

    return render(request, 'acc_management/acc_dashboard.html', {
        'current_cert_search': cert_search,

        'cert_user': cert_user,
        'current_cert_units': cert_units,
        'current_cert_name': cert_name,
        'current_cert_address': cert_address,
        'current_cert_unit_code': cert_unit_code,
        'current_is_approved': cert_is_approved,

        'company_search': company_search,
        'company_user': company_user,
        'current_company_units': company_units,
        'current_company_name': company_name,
        'company_type': company_type,
        'current_company_email': company_email,
        'current_company_country': company_country,
        'current_company_address': company_address,
        'current_company_registration_number': company_registration_number,
        'company_website': company_website,
        'current_company_is_approved': company_is_approved,
    })