from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Product_batch, Company, Certificate, Producer
from datetime import datetime


def _is_producer_or_admin(user):
    if user.is_superuser:
        return True
    try:
        producer = Producer.objects.get(user=user, is_approved=True)
        has_certificate = Certificate.objects.filter(
            holder_company_id__producer=producer,
            status='valid'
        ).exists()
        return has_certificate
    except Producer.DoesNotExist:
        return False


@login_required
def list_product_batches(request):
    if not _is_producer_or_admin(request.user):
        return render(request, 'product_batches/error.html', {
            'msg': 'Brak uprawnień - dostęp tylko dla producentów lub adminów'
        })

    if request.user.is_superuser:
        product_batches = Product_batch.objects.all()
    else:
        try:
            producer = Producer.objects.get(user=request.user)
            product_batches = Product_batch.objects.filter(
                certificate_id__holder_company_id__producer=producer,
                certificate_id__status='valid'
            )
        except Producer.DoesNotExist:
            product_batches = Product_batch.objects.none()

    return render(request, 'product_batches/list_product_batches.html', {
        'product_batches': product_batches
    })


@login_required
def add_product_batch(request):
    if not _is_producer_or_admin(request.user):
        return render(request, 'product_batches/error.html', {
            'msg': 'Brak uprawnień - dostęp tylko dla producentów lub adminów'
        })

    if request.method == 'POST':
        try:
            if request.user.is_superuser:
                certificate = Certificate.objects.filter(status='valid').first()
                if not certificate:
                    messages.error(request, 'Brak ważnego certyfikatu w systemie')
                    return redirect('list_product_batches')
            else:
                producer = Producer.objects.get(user=request.user, is_approved=True)
                certificate = Certificate.objects.filter(
                    holder_company_id__producer=producer,
                    status='valid'
                ).first()
                if not certificate:
                    messages.error(request, 'Brak ważnego certyfikatu dla producenta')
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

        except Producer.DoesNotExist:
            messages.error(request, 'Nie znaleziono konta producenta')
            return redirect('list_product_batches')
        except Exception as e:
            messages.error(request, f'Błąd podczas dodawania partii produktów: {str(e)}')

    return render(request, 'product_batches/add_product_batch.html')


@login_required
def product_batch_detail(request, batch_id):
    if not _is_producer_or_admin(request.user):
        return render(request, 'product_batches/error.html', {
            'msg': 'Brak uprawnień - dostęp tylko dla producentów lub adminów'
        })

    try:
        if request.user.is_superuser:
            product_batch = Product_batch.objects.get(batch_id=batch_id)
        else:
            producer = Producer.objects.get(user=request.user)
            product_batch = Product_batch.objects.get(
                batch_id=batch_id,
                certificate_id__holder_company_id__producer=producer,
                certificate_id__status='valid'
            )
    except (Product_batch.DoesNotExist, Producer.DoesNotExist):
        return render(request, 'product_batches/error.html', {
            'msg': 'Partia produktów nie znaleziona lub brak uprawnień do jej wyświetlenia'
        })

    return render(request, 'product_batches/product_batch_detail.html', {
        'product_batch': product_batch
    })


@login_required
def edit_product_batch(request, batch_id):
    if not _is_producer_or_admin(request.user):
        return render(request, 'product_batches/error.html', {
            'msg': 'Brak uprawnień - dostęp tylko dla producentów lub adminów'
        })

    try:
        if request.user.is_superuser:
            product_batch = Product_batch.objects.get(batch_id=batch_id)
        else:
            producer = Producer.objects.get(user=request.user)
            product_batch = Product_batch.objects.get(
                batch_id=batch_id,
                certificate_id__holder_company_id__producer=producer,
                certificate_id__status='valid'
            )
    except (Product_batch.DoesNotExist, Producer.DoesNotExist):
        return render(request, 'product_batches/error.html', {
            'msg': 'Partia produktów nie znaleziona lub brak uprawnień do jej edycji'
        })

    if request.method == 'POST':
        try:
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

        except Exception as e:
            messages.error(request, f'Błąd podczas aktualizacji partii produktów: {str(e)}')

    return render(request, 'product_batches/edit_product_batch.html', {
        'product_batch': product_batch
    })


@login_required
def delete_product_batch(request, batch_id):
    if not _is_producer_or_admin(request.user):
        return render(request, 'product_batches/error.html', {
            'msg': 'Brak uprawnień - dostęp tylko dla producentów lub adminów'
        })

    try:
        if request.user.is_superuser:
            product_batch = Product_batch.objects.get(batch_id=batch_id)
        else:
            producer = Producer.objects.get(user=request.user)
            product_batch = Product_batch.objects.get(
                batch_id=batch_id,
                certificate_id__holder_company_id__producer=producer,
                certificate_id__status='valid'
            )

        if request.method == 'POST':
            product_batch.delete()
            messages.success(request, f'Partia produktów "{product_batch.name}" została trwale usunięta')
            return redirect('list_product_batches')

        return render(request, 'product_batches/delete_product_batch.html', {
            'product_batch': product_batch
        })

    except (Product_batch.DoesNotExist, Producer.DoesNotExist):
        messages.error(request, 'Partia produktów nie znaleziona lub brak uprawnień')
        return redirect('list_product_batches')


@login_required
def recall_product_batch(request, batch_id):
    if not _is_producer_or_admin(request.user):
        return render(request, 'product_batches/error.html', {
            'msg': 'Brak uprawnień - dostęp tylko dla producentów lub adminów'
        })

    try:
        if request.user.is_superuser:
            product_batch = Product_batch.objects.get(batch_id=batch_id)
        else:
            producer = Producer.objects.get(user=request.user)
            product_batch = Product_batch.objects.get(
                batch_id=batch_id,
                certificate_id__holder_company_id__producer=producer,
                certificate_id__status='valid'
            )

        product_batch.status = 'recalled'
        product_batch.save()
        messages.success(request, f'Partia produktów "{product_batch.name}" została oznaczona jako wycofana')

    except (Product_batch.DoesNotExist, Producer.DoesNotExist):
        messages.error(request, 'Partia produktów nie znaleziona lub brak uprawnień')

    return redirect('list_product_batches')