from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Count, Q, Sum, Avg
from django.utils import timezone
from datetime import timedelta
import json
from ..models import (
    Certificate, Product_batch, Alert, 
    Consumer_verification, Fraud_report, Company
)
from ..blockchain.core import get_blockchain
from ..utils.qr_code_generator import generate_qr_code
from ..utils.redirect_certificate_url import decrypt_certificate_id
from ..models import encrypt_certificate_id
from ..forms.rating_form import ConsumerRatingForm
from ..forms.report_form import FraudReportForm


def main_page(request):
    """Główna strona z dashboardem i funkcjonalnościami"""
    
    # Statystyki dla dashboardu
    total_certificates = Certificate.objects.count()
    active_certificates = Certificate.objects.filter(status='valid').count()
    total_batches = Product_batch.objects.count()
    active_alerts = Alert.objects.filter(status__in=['new', 'waiting']).count()
    
    # Ostatnie certyfikaty
    recent_certificates_raw = Certificate.objects.order_by('-certificate_id')[:5]
    recent_certificates = []
    for cert in recent_certificates_raw:
        # Generuj token dla każdego certyfikatu
        token = encrypt_certificate_id(cert.certificate_id)
        recent_certificates.append({
            'certificate': cert,
            'token': token,
            'detail_url': f'/certificate/{token}/',  # URL do szczegółów certyfikatu
            'report_url': f'/report_fraud/{token}/',  # URL do zgłoszenia fałszerstwa
        })

    # Ostatnie alerty
    recent_alerts = Alert.objects.order_by('-alert_id')[:5]
    
    # Statystyki blockchain
    blockchain = get_blockchain()
    blockchain_status = {
        'chain_length': len(blockchain.chain),
        'is_valid': blockchain.is_chain_valid(),
        'total_subchains': len(blockchain.subchains)
    }
    
    # Popularne produkty
    popular_batches = Product_batch.objects.annotate(
        verification_count=Count('consumer_verification')
    ).order_by('-verification_count')[:5]
    
    context = {
        'total_certificates': total_certificates,
        'active_certificates': active_certificates,
        'total_batches': total_batches,
        'active_alerts': active_alerts,
        'recent_certificates': recent_certificates,
        'recent_alerts': recent_alerts,
        'blockchain_status': blockchain_status,
        'popular_batches': popular_batches,
    }
    
    return render(request, 'main_page.html', context)

     #API DO WERYFIKACJI QR
def verify_qr_code_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            qr_data = data.get('qr_code_data')
            
            if not qr_data:
                return JsonResponse({
                    'success': False,
                    'error': 'Brak danych QR kodu'
                }, status=400)
            
            # Sprawdzenie czy to token szyfrowany
            try:
                certificate_id = decrypt_certificate_id(qr_data)
                certificate = Certificate.objects.get(certificate_id=certificate_id)
                
                blockchain = get_blockchain()
                blockchain_verified = blockchain.verify_certificate(str(certificate.certificate_id))
                
                product_history = None
                batches = Product_batch.objects.filter(certificate_id=certificate)
                if batches.exists():
                    batch = batches.first()
                    product_history = blockchain.get_batch_supply_chain_history(batch.batch_id)
                
                return JsonResponse({
                    'success': True,
                    'verified': True,
                    'blockchain_verified': blockchain_verified,
                    'certificate': {
                        'id': certificate.certificate_id,
                        'number': certificate.certificate_number,
                        'type': certificate.certificate_type,
                        'status': certificate.status,
                        'valid_from': str(certificate.valid_from),
                        'valid_to': str(certificate.valid_to),
                        'publisher': certificate.certificate_publisher,
                    },
                    'product_history': product_history
                })
                
            except (ValueError, Certificate.DoesNotExist):
                # Jeśli to nie token, sprawdź czy to bezpośredni numer certyfikatu
                try:
                    certificate = Certificate.objects.get(certificate_number=qr_data)
                    
                    blockchain = get_blockchain()
                    blockchain_verified = blockchain.verify_certificate(str(certificate.certificate_id))
                    
                    return JsonResponse({
                        'success': True,
                        'verified': True,
                        'blockchain_verified': blockchain_verified,
                        'certificate': {
                            'id': certificate.certificate_id,
                            'number': certificate.certificate_number,
                            'type': certificate.certificate_type,
                            'status': certificate.status,
                            'valid_from': str(certificate.valid_from),
                            'valid_to': str(certificate.valid_to),
                            'publisher': certificate.certificate_publisher,
                        }
                    })
                    
                except Certificate.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'verified': False,
                        'error': 'Certyfikat nie znaleziony'
                    }, status=404)
                    
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Nieprawidłowy format JSON'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Metoda nieobsługiwana'
    }, status=405)

# API DO ŚLEDZENIA PRODUKTU
def track_product_api(request):
    if request.method == 'GET':
        batch_id = request.GET.get('batch_id')
        certificate_id = request.GET.get('certificate_id')
        
        if not batch_id and not certificate_id:
            return JsonResponse({
                'success': False,
                'error': 'Podaj batch_id lub certificate_id'
            }, status=400)
        
        try:
            blockchain = get_blockchain()
            
            if batch_id:
                # Śledzenie przez batch_id
                try:
                    batch = Product_batch.objects.get(batch_id=batch_id)
                    
                    history = blockchain.get_batch_supply_chain_history(batch.batch_id)
                    map_data = blockchain.get_batch_supply_chain_map_data(batch.batch_id)
                    
                    return JsonResponse({
                        'success': True,
                        'batch': {
                            'id': batch.batch_id,
                            'name': batch.name,
                            'category': batch.category,
                            'quantity': float(batch.quantity),
                            'unit': batch.unit_of_measure,
                            'production_date': str(batch.production_date),
                            'harvest_date': str(batch.harvest_date) if batch.harvest_date else None,
                        },
                        'certificate': {
                            'id': batch.certificate_id.certificate_id,
                            'number': batch.certificate_id.certificate_number,
                            'type': batch.certificate_id.certificate_type,
                        },
                        'history': history,
                        'map_data': map_data
                    })
                    
                except Product_batch.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': 'Partia nie znaleziona'
                    }, status=404)
                    
            elif certificate_id:
                # Śledzenie przez certificate_id 
                try:
                    certificate = Certificate.objects.get(certificate_id=certificate_id)
                    batches = Product_batch.objects.filter(certificate_id=certificate)
                    
                    batch_data = []
                    for batch in batches:
                        history = blockchain.get_batch_supply_chain_history(batch.batch_id)
                        map_data = blockchain.get_batch_supply_chain_map_data(batch.batch_id)
                        
                        batch_data.append({
                            'batch_id': batch.batch_id,
                            'batch_name': batch.name,
                            'history': history,
                            'map_data': map_data
                        })
                    
                    return JsonResponse({
                        'success': True,
                        'certificate': {
                            'id': certificate.certificate_id,
                            'number': certificate.certificate_number,
                            'type': certificate.certificate_type,
                        },
                        'batches': batch_data,
                        'total_batches': len(batch_data)
                    })
                    
                except Certificate.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': 'Certyfikat nie znaleziony'
                    }, status=404)
                    
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Metoda nieobsługiwana'
    }, status=405)

# API DO SKŁADANIA OCEN PRODUKTÓW
def submit_rating_api(request):

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            rating_form = ConsumerRatingForm(data)
            if rating_form.is_valid():
                rating = rating_form.save(commit=False)
                
                certificate_id = data.get('certificate_id')
                if not certificate_id:
                    return JsonResponse({
                        'success': False,
                        'error': 'Brak certificate_id'
                    }, status=400)
                
                try:
                    certificate = Certificate.objects.get(certificate_id=certificate_id)
                    rating.certificate_id = certificate
                    
                    # Sprawdzenie czy użytkownik zweryfikował produkt
                    consumer_email = rating.consumer_email
                    exists_in_verification = Consumer_verification.objects.filter(
                        consumer_email=consumer_email
                    ).exists()
                    
                    rating.is_verified = 1 if exists_in_verification else 0
                    rating.save()
                    
                    return JsonResponse({
                        'success': True,
                        'message': 'Ocena została dodana',
                        'rating_id': rating.rating_id,
                        'is_verified': rating.is_verified
                    })
                    
                except Certificate.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': 'Certyfikat nie znaleziony'
                    }, status=404)
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Nieprawidłowe dane formularza',
                    'errors': rating_form.errors
                }, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Nieprawidłowy format JSON'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Metoda nieobsługiwana'
    }, status=405)

# API DO ZGŁASZANIA FRAUD REPORT
def submit_fraud_report_api(request):
    if request.method == 'POST':

        try:
            data = json.loads(request.body)
            
            fraud_form = FraudReportForm(data)
            if fraud_form.is_valid():
                fraud_report = fraud_form.save(commit=False)
                
                certificate_id = data.get('certificate_id')
                if not certificate_id:
                    return JsonResponse({
                        'success': False,
                        'error': 'Brak certificate_id'
                    }, status=400)
                
                try:
                    certificate = Certificate.objects.get(certificate_id=certificate_id)
                    fraud_report.certificate_id = certificate
                    
                    email = fraud_report.reporter_email
                    already_reported = Fraud_report.objects.filter(
                        certificate_id=certificate,
                        reporter_email=email
                    ).exists()
                    
                    if already_reported:
                        return JsonResponse({
                            'success': False,
                            'error': 'Ten certyfikat został już zgłoszony z tego adresu email'
                        }, status=400)
                    
                    # Znajdź partie związane z certyfikatem
                    batches = Product_batch.objects.filter(certificate_id=certificate)
                    
                    if batches.exists():
                        for batch in batches:
                            fraud_report.pk = None  # Reset primary key for each batch
                            fraud_report.batch_id = batch
                            fraud_report.save()
                            fraud_report.check_and_reject_spam()
                    else:
                        fraud_report.batch_id = None
                        fraud_report.save()
                        fraud_report.check_and_reject_spam()
                    
                    return JsonResponse({
                        'success': True,
                        'message': 'Zgłoszenie fałszerstwa zostało przyjęte',
                        'report_id': fraud_report.report_id
                    })
                    
                except Certificate.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': 'Certyfikat nie znaleziony'
                    }, status=404)
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Nieprawidłowe dane formularza',
                    'errors': fraud_form.errors
                }, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Nieprawidłowy format JSON'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Metoda nieobsługiwana'
    }, status=405)

# API Z STATYSTYKAMI SYSTEMU
def get_system_stats_api(request):
  
    if request.method == 'GET':
        try:
            # Podstawowe statystyki
            total_certificates = Certificate.objects.count()
            active_certificates = Certificate.objects.filter(status='valid').count()
            expired_certificates = Certificate.objects.filter(status='expired').count()
            total_batches = Product_batch.objects.count()
            
            # Statystyki alertów
            new_alerts = Alert.objects.filter(status='new').count()
            active_alerts = Alert.objects.filter(status__in=['new', 'waiting']).count()
            
            # Statystyki weryfikacji
            total_verifications = Consumer_verification.objects.count()
            authentic_verifications = Consumer_verification.objects.filter(
                verification_result='authentic'
            ).count()
            
            # Statystyki zgłoszeń
            total_fraud_reports = Fraud_report.objects.count()
            new_fraud_reports = Fraud_report.objects.filter(status='new').count()
            
            # Statystyki Blockchain 
            blockchain = get_blockchain()
            
            # Ostatnie aktywności
            recent_certificates = list(Certificate.objects.order_by('-certificate_id')[:10].values(
                'certificate_id', 'certificate_number', 'certificate_type', 'status'
            ))
            
            recent_alerts = list(Alert.objects.order_by('-alert_id')[:10].values(
                'alert_id', 'alert_type', 'severity', 'status', 'description'
            ))
            
            return JsonResponse({
                'success': True,
                'stats': {
                    'certificates': {
                        'total': total_certificates,
                        'active': active_certificates,
                        'expired': expired_certificates,
                    },
                    'batches': {
                        'total': total_batches,
                    },
                    'alerts': {
                        'total': Alert.objects.count(),
                        'new': new_alerts,
                        'active': active_alerts,
                    },
                    'verifications': {
                        'total': total_verifications,
                        'authentic': authentic_verifications,
                    },
                    'fraud_reports': {
                        'total': total_fraud_reports,
                        'new': new_fraud_reports,
                    },
                    'blockchain': {
                        'chain_length': len(blockchain.chain),
                        'subchains': len(blockchain.subchains),
                        'is_valid': blockchain.is_chain_valid(),
                    }
                },
                'recent_activity': {
                    'certificates': recent_certificates,
                    'alerts': recent_alerts,
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Metoda nieobsługiwana'
    }, status=405)

# API DO POBIERANIA SZCZEGÓŁÓW CERTYFIAKTU
def get_certificate_details_api(request):
   
    if request.method == 'GET':
        certificate_id = request.GET.get('certificate_id')
        certificate_number = request.GET.get('certificate_number')
        
        if not certificate_id and not certificate_number:
            return JsonResponse({
                'success': False,
                'error': 'Podaj certificate_id lub certificate_number'
            }, status=400)
        
        try:
            if certificate_id:
                certificate = Certificate.objects.get(certificate_id=certificate_id)
            else:
                certificate = Certificate.objects.get(certificate_number=certificate_number)
            
            # Pobranie ocen
            ratings = certificate.consumer_rating_set.filter(is_verified=1).order_by('-rating_id')
            avg_rating = ratings.aggregate(Avg('rating'))['rating__avg'] or 0
            
            # Pobranie powiązanych partii
            batches = Product_batch.objects.filter(certificate_id=certificate)
            
            # Sprawdzenie w blockchain
            blockchain = get_blockchain()
            blockchain_verified = blockchain.verify_certificate(str(certificate.certificate_id))
            
            # QR code data
            qr_code_url = None
            if certificate.qr_code_data:
                qr_code_url = certificate.qr_code_data
            
            return JsonResponse({
                'success': True,
                'certificate': {
                    'id': certificate.certificate_id,
                    'number': certificate.certificate_number,
                    'type': certificate.certificate_type,
                    'status': certificate.status,
                    'publisher': certificate.certificate_publisher,
                    'valid_from': str(certificate.valid_from),
                    'valid_to': str(certificate.valid_to),
                    'holder_company': {
                        'id': certificate.holder_company_id.company_id,
                        'name': certificate.holder_company_id.name,
                    } if certificate.holder_company_id else None,
                    'certifying_unit': {
                        'id': certificate.issued_by_certifying_unit_id.certifying_unit_id,
                        'name': certificate.issued_by_certifying_unit_id.name,
                    } if certificate.issued_by_certifying_unit_id else None,
                    'blockchain_verified': blockchain_verified,
                    'blockchain_address': certificate.blockchain_address,
                    'qr_code_url': qr_code_url,
                },
                'ratings': {
                    'average': float(avg_rating),
                    'total': ratings.count(),
                    'list': list(ratings.values('rating', 'comment', 'consumer_email'))
                },
                'batches': {
                    'total': batches.count(),
                    'list': list(batches.values('batch_id', 'name', 'category', 'status'))
                }
            })
            
        except Certificate.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Certyfikat nie znaleziony'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Metoda nieobsługiwana'
    }, status=405)