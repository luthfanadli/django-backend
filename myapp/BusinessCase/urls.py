from django.urls import path
from BusinessCase import views

urlpatterns = [
    path('product', views.product),
    path('product/<int:id>', views.product),
    path('register', views.register_user),
    path('register/location', views.register_user_location),
    path('login', views.login_user),
    path('user/<int:id>', views.delete_user),  
    path('users', views.view_all_users),
    path('order', views.create_order),
    path('order-history/<int:user_id>', views.get_order_history)
]
