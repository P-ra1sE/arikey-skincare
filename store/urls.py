from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('home.html', views.home, name='home-page'),

    path('shopnow.html', views.shop, name='shop'),

    path('ourstory.html', views.our_story, name='our-story'),

    path('contactus.html', views.contact, name='contact'),

    path(
        'product-details.html',
        views.product_details,
        name='product-details'
    ),

    path('cart.html', views.cart, name='cart'),

    path('checkout.html', views.checkout, name='checkout'),
    
    path(
    'api/create-order/',
    views.create_order,
    name='create-order'
),
    path(
    'payment/callback/',
    views.payment_callback,
    name='payment-callback'
),

path(
    'order-success.html',
    views.order_success,
    name='order-success'
),
path(
    'payment/webhook/',
    views.paystack_webhook,
    name='paystack-webhook'
),
]