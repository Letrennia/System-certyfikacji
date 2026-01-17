from django.shortcuts import render

def account_type(request):
    return render(request, 'entity_log_dir/choose_acc_type.html')
