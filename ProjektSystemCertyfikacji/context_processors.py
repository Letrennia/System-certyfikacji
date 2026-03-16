from .models import Certificate, Company


def global_stats(request):
    try:
        total_certificates = Certificate.objects.filter(status='valid').count()
        total_companies = Company.objects.count()
    except Exception:
        total_certificates = 0
        total_companies = 0

    return {
        'total_certificates': total_certificates,
        'total_companies': total_companies,
    }