from django.shortcuts import render

def p_main_page(request):
    return render(request, 'producer_main_page.html')