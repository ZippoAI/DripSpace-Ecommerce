from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.userLogin, name='login'),
    path('register/', views.userRegister, name='register'),
    path('logout/', views.userLogout, name='logout'),
    path('productInfo/<slug:slug>/', views.productInfo, name='productDetail'),
    path('category/<slug:category_slug>/', views.category_products, name='category_products'),
    path('search/', views.search_products, name='search_products'),
    path('search/suggestions/', views.search_suggestions, name='search_suggestions'),
    path('userProfile/', views.userProfile, name='userProfile'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/count/', views.get_cart_count, name='get_cart_count'),
    path('checkout/', views.checkout, name='checkout'),
    path('process-checkout/', views.process_checkout, name='process_checkout'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('update-cart-item/', views.update_cart_item, name='update_cart_item'),
    path('remove-cart-item/', views.remove_cart_item, name='remove_cart_item'),

    #Extra Page URLs
    path('faq/', views.faq, name='faq'),
    path('size-guide/', views.sizeGuide, name='sizeGuide'),
    path('store-locations/', views.storeLocations, name='storeLocations'),
    path('care-instruction/', views.careInstruction, name='careInstruction'),
    path('return-&-exchanges/', views.returnExchanges, name='returnExchanges'),
    path('sustainability/' , views.sustainability , name='sustainability'),
    path('press/' , views.press , name='press'),
    path('ourstory/' , views.ourstory , name='ourstory'),
    path('thank-you/' , views.paymentdone , name='paymentdone'),


    # Social Page URLs
    path('DripSpace-instagram/', views.instagram, name='instagram'),


    #------------ Product URLs -----------------
    path('DripSpace-AllProduct/', views.AllProduct, name='AllProduct'),
    path('new-arrivals/', views.newArrival, name='newArrival')
]

if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)