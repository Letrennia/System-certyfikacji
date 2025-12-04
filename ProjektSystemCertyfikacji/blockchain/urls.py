from django.urls import path
from . import views

urlpatterns = [
    path('api/blockchain/status/', views.blockchain_status, name='blockchain_status'),
    path('api/blockchain/chain/', views.get_full_chain, name='get_full_chain'),
    path('api/blockchain/validate/', views.validate_blockchain, name='validate_blockchain'),

    path('api/blockchain/verify/certificate/<str:certificate_id>/',
         views.verify_certificate_blockchain,
         name='verify_certificate_blockchain'),

    path('api/blockchain/batch/<int:batch_id>/history/',
         views.get_batch_history_blockchain,
         name='get_batch_history_blockchain'),

    path('api/blockchain/certificate/<str:certificate_id>/batches/',
         views.get_certificate_batches_blockchain,
         name='get_certificate_batches_blockchain'),

    path('api/blockchain/transfer/', views.register_transfer, name='register_transfer'),
]