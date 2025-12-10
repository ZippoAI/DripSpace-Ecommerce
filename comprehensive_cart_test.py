#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from app.models import CartItem, Product, Size, ShoeSize, CustomUser, Cart

def test_comprehensive_cart_functionality():
    """Test the cart functionality for both footwear and clothing products"""
    print("Testing comprehensive cart functionality...")
    
    # Create a test user
    try:
        user = CustomUser.objects.get(username='testuser')
    except CustomUser.DoesNotExist:
        user = CustomUser.objects.create_user(username='testuser', password='testpass123')
    
    # Create a test cart
    cart, created = Cart.objects.get_or_create(user=user)
    
    # Test 1: Footwear product
    print("\n--- Testing Footwear Product ---")
    footwear_products = Product.objects.filter(category__head_category__name='Footwear')
    if footwear_products.exists():
        footwear_product = footwear_products.first()
        print(f"Testing with footwear product: {footwear_product.name}")
        
        # Check if the product has available shoe sizes
        available_shoe_sizes = footwear_product.available_shoe_sizes.all()
        if available_shoe_sizes.exists():
            shoe_size = available_shoe_sizes.first()
            print(f"Using shoe size: {shoe_size.size}")
            
            # Create a cart item for the footwear product
            try:
                cart_item = CartItem.objects.create(
                    cart=cart,
                    product=footwear_product,
                    shoe_size=shoe_size,
                    size=None,  # Should be None for footwear products
                    quantity=1
                )
                print(f"✓ Successfully created cart item for footwear product: {cart_item.display_size}")
                
                # Test that we can retrieve the cart item
                retrieved_item = CartItem.objects.get(id=cart_item.id)
                print(f"✓ Successfully retrieved cart item: {retrieved_item.display_size}")
                
                # Clean up
                cart_item.delete()
                print("✓ Cleaned up footwear cart item")
            except Exception as e:
                print(f"✗ Error creating cart item for footwear product: {e}")
        else:
            print("No shoe sizes available for footwear product")
    else:
        print("No footwear products found")
    
    # Test 2: Clothing product
    print("\n--- Testing Clothing Product ---")
    clothing_products = Product.objects.exclude(category__head_category__name='Footwear')
    if clothing_products.exists():
        clothing_product = clothing_products.first()
        print(f"Testing with clothing product: {clothing_product.name}")
        
        # Check if the product has available sizes
        available_sizes = clothing_product.available_sizes.all()
        if available_sizes.exists():
            size = available_sizes.first()
            print(f"Using clothing size: {size.name}")
            
            # Create a cart item for the clothing product
            try:
                cart_item = CartItem.objects.create(
                    cart=cart,
                    product=clothing_product,
                    size=size,
                    shoe_size=None,  # Should be None for clothing products
                    quantity=1
                )
                print(f"✓ Successfully created cart item for clothing product: {cart_item.display_size}")
                
                # Test that we can retrieve the cart item
                retrieved_item = CartItem.objects.get(id=cart_item.id)
                print(f"✓ Successfully retrieved cart item: {retrieved_item.display_size}")
                
                # Clean up
                cart_item.delete()
                print("✓ Cleaned up clothing cart item")
            except Exception as e:
                print(f"✗ Error creating cart item for clothing product: {e}")
        else:
            print("No sizes available for clothing product")
    else:
        print("No clothing products found")
    
    # Test 3: Validation - Try to create invalid cart items
    print("\n--- Testing Validation ---")
    
    # Try to create a footwear product with a clothing size (should fail)
    if footwear_products.exists() and Size.objects.exists():
        footwear_product = footwear_products.first()
        clothing_size = Size.objects.first()
        
        try:
            cart_item = CartItem.objects.create(
                cart=cart,
                product=footwear_product,
                size=clothing_size,  # This should fail validation
                shoe_size=None,
                quantity=1
            )
            print("✗ ERROR: Cart item was created with clothing size for footwear product!")
            cart_item.delete()
        except Exception as e:
            print(f"✓ Correctly prevented creation of invalid cart item: {e}")
    
    # Try to create a clothing product with a shoe size (should fail)
    if clothing_products.exists() and ShoeSize.objects.exists():
        clothing_product = clothing_products.first()
        shoe_size = ShoeSize.objects.first()
        
        try:
            cart_item = CartItem.objects.create(
                cart=cart,
                product=clothing_product,
                size=None,
                shoe_size=shoe_size,  # This should fail validation
                quantity=1
            )
            print("✗ ERROR: Cart item was created with shoe size for clothing product!")
            cart_item.delete()
        except Exception as e:
            print(f"✓ Correctly prevented creation of invalid cart item: {e}")
    
    print("\n--- Test Complete ---")

if __name__ == "__main__":
    test_comprehensive_cart_functionality()