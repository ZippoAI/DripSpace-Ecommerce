from .views import get_or_create_cart

def cart_context(request):
    """Add cart item count to all template contexts"""
    try:
        cart = get_or_create_cart(request)
        cart_item_count = cart.get_total_items()
    except:
        cart_item_count = 0
    
    return {
        'cart_item_count': cart_item_count
    }