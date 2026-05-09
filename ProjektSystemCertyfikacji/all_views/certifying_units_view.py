from django.shortcuts import render

from ..models import Certifying_unit


def list_certifying_units(request):
    certifying_units = Certifying_unit.objects.filter(is_approved=True).order_by("name")

    context = {
        "certifying_units": certifying_units,
    }
    return render(request, "certifying_units/list_certifying_units.html", context)
