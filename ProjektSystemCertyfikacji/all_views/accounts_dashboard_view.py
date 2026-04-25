from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import render, redirect

from ProjektSystemCertyfikacji.models import RegistrationCode


@login_required
def account_dashboard(request):
    if not request.user.is_superuser:
        return render(request, 'product_all_accounts/error.html', {
            'msg': 'Brak uprawnień - dostęp tylko dla adminów'
        })

    registration_codes = RegistrationCode.objects.all()

    search = request.GET.get("search", "")
    is_used = request.GET.get("is_used", "")
    sort_by = request.GET.get("sort_by", "created_at")
    sort_order = request.GET.get("sort_order", "asc")

    if search:
        registration_codes = registration_codes.filter(code__icontains=search)
    if is_used is not None:
        if is_used.lower() == 'true':
            registration_codes = registration_codes.filter(is_used=True)
        elif is_used.lower() == 'false':
            registration_codes = registration_codes.filter(is_used=False)
    if sort_order == "desc":
        sort_by = "-" + sort_by

    registration_codes = registration_codes.order_by(sort_by)



    if request.method == "POST":
        action = request.POST.get("action")

        if action == 'add':
            new_code = request.POST.get("code", "").strip()
            if new_code:
                try:
                    RegistrationCode.objects.create(code=new_code)
                except IntegrityError:
                    pass
        elif action == 'delete':
            pk = request.POST.get("pk")
            RegistrationCode.objects.filter(id=pk).delete()
        elif action == 'edit':
            pk = request.POST.get("pk")
            new_code = request.POST.get("code", "").strip()
            is_used = request.POST.get("is_used") == 'true'

            RegistrationCode.objects.filter(id==pk).update(code=new_code, is_used=is_used)





    return render(request, 'acc_management/account_dashboard.html', {
        'current_search': search,
        'registration_codes': registration_codes,
        'current_sort': sort_by,
        'current_is_used': is_used,
        'current_sort_order': sort_order,

    })