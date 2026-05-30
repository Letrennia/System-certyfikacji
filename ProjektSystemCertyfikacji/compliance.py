from django.utils import timezone
from .models import Alert, Certificate


def create_alert(alert_type, severity, description, event=None, batch=None):
    open_alerts = Alert.objects.filter(
        alert_type=alert_type,
        status__in=['new', 'waiting', 'realising']
    )
    if event is not None:
        open_alerts = open_alerts.filter(event_id=event)
    if batch is not None:
        open_alerts = open_alerts.filter(batch_id=batch)
    if (event or batch) and open_alerts.exists():
        return open_alerts.first()
    if not event and not batch and open_alerts.filter(description=description).exists():
        return open_alerts.filter(description=description).first()
    return Alert.objects.create(
        alert_type=alert_type,
        severity=severity,
        description=description,
        status='new',
        event_id=event,
        batch_id=batch,
    )


def check_certificate_conditions(certificate, area, company):
    today = timezone.now().date()
    violations = []

    if certificate.status != 'valid' or not (certificate.valid_from <= today <= certificate.valid_to):
        violations.append({
            'type': 'compliance_breach',
            'severity': 'critical',
            'hard': True,
            'msg': f"Etap na nieważnym certyfikacie {certificate.certificate_number} (status: {certificate.get_status_display()}).",
        })

    if not certificate.activity_areas.filter(pk=area.pk).exists():
        violations.append({
            'type': 'compliance_breach',
            'severity': 'high',
            'hard': False,
            'msg': f"Obszar '{area.get_name_display()}' nie należy do zakresu certyfikatu {certificate.certificate_number}.",
        })
    else:
        company_has_cert = Certificate.objects.filter(
            holder_company_id=company,
            status='valid',
            activity_areas=area,
            valid_from__lte=today,
            valid_to__gte=today,
        ).exists()
        if not company_has_cert:
            violations.append({
                'type': 'compliance_breach',
                'severity': 'high',
                'hard': False,
                'msg': f"Firma '{company.name}' nie posiada własnego ważnego certyfikatu na obszar '{area.get_name_display()}'.",
            })

    if not company.is_approved:
        violations.append({
            'type': 'compliance_breach',
            'severity': 'medium',
            'hard': False,
            'msg': f"Etap zarejestrowany przez niezatwierdzoną firmę '{company.name}'.",
        })

    return violations
