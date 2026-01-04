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
    
    # Supply Chain Track & Trace API
    path('api/blockchain/supply-chain/<int:batch_id>/history/',
         views.get_supply_chain_history,
         name='get_supply_chain_history'),
    
    path('api/blockchain/supply-chain/<int:batch_id>/map/',
         views.get_supply_chain_map,
         name='get_supply_chain_map'),
    
    path('api/blockchain/subchain/<int:batch_id>/address/',
         views.get_subchain_address,
         name='get_subchain_address'),
    
    path('api/blockchain/subchains/',
         views.get_all_subchains,
         name='get_all_subchains'),
    
    path('api/blockchain/supply-chain/production/',
         views.register_production,
         name='register_production'),
    
    path('api/blockchain/supply-chain/processing/',
         views.register_processing,
         name='register_processing'),
    
    path('api/blockchain/supply-chain/distribution/',
         views.register_distribution,
         name='register_distribution'),
    
    path('api/blockchain/supply-chain/retail/',
         views.register_retail,
         name='register_retail'),
]