from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Product_batch, Company, Certificate
from datetime import datetime
from django.http import JsonResponse


def _is_company_or_admin(user, company_types=None):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    try:
        company = Company.objects.get(user=user, is_approved=True)
        if company_types is not None:
            return company.company_type in company_types
        return True
    except Company.DoesNotExist:
        return False


def _get_user_company(user):
    if not user or not user.is_authenticated:
        return None
    try:
        return Company.objects.get(user=user, is_approved=True)
    except Company.DoesNotExist:
        return None


@login_required
def list_product_batches(request):
    if not _is_company_or_admin(request.user):
        return render(request, 'product_batches/error.html', {
            'msg': 'Brak uprawnień - dostęp tylko dla firm lub adminów'
        })

    if request.user.is_superuser:
        batches = Product_batch.objects.all()
    else:
        company = _get_user_company(request.user)
        if company:
            batches = Product_batch.objects.filter(
                certificate_id__holder_company_id=company
            )
        else:
            batches = Product_batch.objects.none()

    search = request.GET.get("search", "")
    category = request.GET.get("category", "")
    status = request.GET.get("status", "")
    sort_by = request.GET.get("sort_by", "production_date")
    sort_order = request.GET.get("sort_order", "asc")

    if search:
        batches = batches.filter(name__icontains=search)
    if category:
        batches = batches.filter(category=category)
    if status:
        batches = batches.filter(status=status)
    if sort_order == "desc":
        sort_by = "-" + sort_by

    batches = batches.order_by(sort_by)

    return render(request, 'product_batches/list_product_batches.html', {
        "product_batches": batches,
        "current_search": search,
        "current_category": category,
        "current_status": status,
        "current_sort": request.GET.get("sort_by", "production_date"),
        "current_order": sort_order,
        "category_choices": list(Product_batch.objects.values_list("category", flat=True).distinct()),
        "status_choices": Product_batch.STATUS,
    })


@login_required
def add_product_batch(request):
    if not _is_company_or_admin(request.user):
        return render(request, 'product_batches/error.html', {
            'msg': 'Brak uprawnień - dostęp tylko dla firm lub adminów'
        })

    if request.method == 'POST':
        try:
            certificate_id = request.POST.get('certificate_id')
            if not certificate_id:
                messages.error(request, 'Nie wybrano certyfikatu')
                return render(request, 'product_batches/add_product_batch.html')

            try:
                certificate = Certificate.objects.get(certificate_id=certificate_id, status='valid')
            except Certificate.DoesNotExist:
                messages.error(request, 'Wybrany certyfikat nie istnieje lub jest nieważny')
                return render(request, 'product_batches/add_product_batch.html')

            if not request.user.is_superuser:
                company = _get_user_company(request.user)
                if not company:
                    messages.error(request, 'Nie znaleziono konta firmowego')
                    return redirect('list_product_batches')
                if certificate.holder_company_id != company:
                    messages.error(request, 'Nie masz uprawnień do tego certyfikatu')
                    return redirect('list_product_batches')

            prod_date_str = request.POST.get('production_date')
            exp_date_str = request.POST.get('expiration_date')
            production_date = datetime.strptime(prod_date_str, "%Y-%m-%d").date() if prod_date_str else None
            expiration_date = datetime.strptime(exp_date_str, "%Y-%m-%d").date() if exp_date_str else None

            product_batch = Product_batch(
                name=request.POST.get('name'),
                category=request.POST.get('category'),
                cn_code=request.POST.get('cn_code'),
                quantity=request.POST.get('quantity'),
                unit_of_measure=request.POST.get('unit_of_measure'),
                status='waiting',
                storage_conditions=request.POST.get('storage_conditions', ''),
                transport_temperature=request.POST.get('transport_temperature', 0),
                production_date=production_date,
                expiration_date=expiration_date,
                certificate_id=certificate,
                certifying_unit_id=certificate.issued_by_certifying_unit_id
            )
            product_batch.save()
            messages.success(request, f'Partia produktów {product_batch.name} została pomyślnie dodana')
            return redirect('product_batch_detail', batch_id=product_batch.batch_id)

        except Exception as e:
            messages.error(request, f'Błąd podczas dodawania partii produktów: {str(e)}')
            return render(request, 'product_batches/add_product_batch.html')

    return render(request, 'product_batches/add_product_batch.html')


@login_required
def product_batch_detail(request, batch_id):
    if not _is_company_or_admin(request.user):
        return render(request, 'product_batches/error.html', {
            'msg': 'Brak uprawnień - dostęp tylko dla firm lub adminów'
        })

    try:
        if request.user.is_superuser:
            product_batch = Product_batch.objects.get(batch_id=batch_id)
        else:
            company = _get_user_company(request.user)
            if not company:
                raise Company.DoesNotExist
            product_batch = Product_batch.objects.get(
                batch_id=batch_id,
                certificate_id__holder_company_id=company
            )
    except (Product_batch.DoesNotExist, Company.DoesNotExist):
        return render(request, 'product_batches/error.html', {
            'msg': 'Partia produktów nie znaleziona lub brak uprawnień do jej wyświetlenia'
        })

    return render(request, 'product_batches/product_batch_detail.html', {
        'product_batch': product_batch
    })


@login_required
def edit_product_batch(request, batch_id):
    if not _is_company_or_admin(request.user):
        return render(request, 'product_batches/error.html', {
            'msg': 'Brak uprawnień - dostęp tylko dla firm lub adminów'
        })

    try:
        if request.user.is_superuser:
            product_batch = Product_batch.objects.get(batch_id=batch_id)
        else:
            company = _get_user_company(request.user)
            if not company:
                raise Company.DoesNotExist
            product_batch = Product_batch.objects.get(
                batch_id=batch_id,
                certificate_id__holder_company_id=company
            )
    except (Product_batch.DoesNotExist, Company.DoesNotExist):
        return render(request, 'product_batches/error.html', {
            'msg': 'Partia produktów nie znaleziona lub brak uprawnień do jej edycji'
        })

    if request.method == 'POST':
        try:
            certificate_id = request.POST.get('certificate_id')
            if certificate_id:
                certificate = Certificate.objects.get(certificate_id=certificate_id, status='valid')
                if not request.user.is_superuser:
                    company = _get_user_company(request.user)
                    if not company or certificate.holder_company_id != company:
                        messages.error(request, 'Nie masz uprawnień do tego certyfikatu')
                        return redirect('edit_product_batch', batch_id=batch_id)
                product_batch.certificate_id = certificate
                product_batch.certifying_unit_id = certificate.issued_by_certifying_unit_id

            product_batch.name = request.POST.get('name', product_batch.name)
            product_batch.category = request.POST.get('category', product_batch.category)
            product_batch.cn_code = request.POST.get('cn_code', product_batch.cn_code)
            product_batch.quantity = request.POST.get('quantity', product_batch.quantity)
            product_batch.unit_of_measure = request.POST.get('unit_of_measure', product_batch.unit_of_measure)
            product_batch.storage_conditions = request.POST.get('storage_conditions', product_batch.storage_conditions)
            product_batch.transport_temperature = request.POST.get('transport_temperature',
                                                                    product_batch.transport_temperature)
            prod_date_str = request.POST.get('production_date')
            exp_date_str = request.POST.get('expiration_date')
            if prod_date_str:
                product_batch.production_date = datetime.strptime(prod_date_str, "%Y-%m-%d").date()
            if exp_date_str:
                product_batch.expiration_date = datetime.strptime(exp_date_str, "%Y-%m-%d").date()

            product_batch.save()
            messages.success(request, 'Partia produktów została zaktualizowana')
            return redirect('product_batch_detail', batch_id=product_batch.batch_id)

        except Certificate.DoesNotExist:
            messages.error(request, 'Wybrany certyfikat nie istnieje lub jest nieważny')
        except Exception as e:
            messages.error(request, f'Błąd podczas aktualizacji partii produktów: {str(e)}')

    return render(request, 'product_batches/edit_product_batch.html', {
        'product_batch': product_batch
    })


@login_required
def delete_product_batch(request, batch_id):
    if not _is_company_or_admin(request.user):
        return render(request, 'product_batches/error.html', {
            'msg': 'Brak uprawnień - dostęp tylko dla firm lub adminów'
        })

    try:
        if request.user.is_superuser:
            product_batch = Product_batch.objects.get(batch_id=batch_id)
        else:
            company = _get_user_company(request.user)
            if not company:
                raise Company.DoesNotExist
            product_batch = Product_batch.objects.get(
                batch_id=batch_id,
                certificate_id__holder_company_id=company
            )

        if request.method == 'POST':
            name = product_batch.name
            product_batch.delete()
            messages.success(request, f'Partia produktów "{name}" została trwale usunięta')
            return redirect('list_product_batches')

        return render(request, 'product_batches/delete_product_batch.html', {
            'product_batch': product_batch
        })

    except (Product_batch.DoesNotExist, Company.DoesNotExist):
        messages.error(request, 'Partia produktów nie znaleziona lub brak uprawnień')
        return redirect('list_product_batches')


@login_required
def recall_product_batch(request, batch_id):
    if not _is_company_or_admin(request.user):
        return render(request, 'product_batches/error.html', {
            'msg': 'Brak uprawnień - dostęp tylko dla firm lub adminów'
        })

    try:
        if request.user.is_superuser:
            product_batch = Product_batch.objects.get(batch_id=batch_id)
        else:
            company = _get_user_company(request.user)
            if not company:
                raise Company.DoesNotExist
            product_batch = Product_batch.objects.get(
                batch_id=batch_id,
                certificate_id__holder_company_id=company
            )

        product_batch.status = 'recalled'
        product_batch.save()
        messages.success(request, f'Partia produktów "{product_batch.name}" została oznaczona jako wycofana')

    except (Product_batch.DoesNotExist, Company.DoesNotExist):
        messages.error(request, 'Partia produktów nie znaleziona lub brak uprawnień')

    return redirect('list_product_batches')


@login_required
def get_certificates_for_batch(request):
    user = request.user
    try:
        if user.is_staff:
            certificates = Certificate.objects.filter(
                status='valid'
            ).select_related('holder_company_id', 'issued_by_certifying_unit_id')
        else:
            company = _get_user_company(user)
            if not company:
                return JsonResponse({'certificates': [], 'error': 'Nie znaleziono konta firmowego'})
            certificates = Certificate.objects.filter(
                holder_company_id=company,
                status='valid'
            ).select_related('holder_company_id', 'issued_by_certifying_unit_id')

        cert_list = [
            {
                'id': cert.certificate_id,
                'number': cert.certificate_number,
                'company': cert.holder_company_id.name,
                'valid_to': cert.valid_to.strftime('%Y-%m-%d'),
                'status': cert.get_status_display(),
                'issued_by': cert.issued_by_certifying_unit_id.name
            }
            for cert in certificates
        ]

        return JsonResponse({'certificates': cert_list})

    except Exception as e:
        return JsonResponse({'certificates': [], 'error': str(e)})