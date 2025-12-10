from django.shortcuts import render, redirect, get_object_or_404
from . models import CustomUser, HeadCategory, Category, Product, Size, Cart, CartItem, ShoeSize
from django.contrib.auth.models import AbstractUser
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import json

from django.contrib.auth import login, logout, authenticate, get_user_model
# Create your views here.


User = get_user_model()


def get_or_create_cart(request):
    """Get or create a cart for the current user or session"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


def get_cart_count(request):
    """API endpoint to get the current cart item count"""
    try:
        cart = get_or_create_cart(request)
        cart_count = cart.get_total_items()
        return JsonResponse({
            'success': True,
            'cart_total_items': cart_count
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


def get_head_categories():
    """Helper function to get all head categories with their subcategories"""
    return HeadCategory.objects.prefetch_related('categories').all()


def get_categories():
    """Helper function to get all categories"""
    return Category.objects.select_related('head_category').all()


def home(request):
    categories = get_categories()
    head_categories = get_head_categories()
    
    # Get new arrivals (latest 8 products)
    try:
        new_arrivals = Product.objects.all().order_by('-id')[:8]
    except:
        new_arrivals = []
    
    # Get all products for the slider (not just 8)
    try:
        all_products = Product.objects.all().order_by('-id')
    except:
        all_products = []
    
    # Get footwear categories
    footwear_categories = []
    footwear_products = []
    try:
        footwear_head_category = HeadCategory.objects.get(name='Footwear')
        footwear_categories = footwear_head_category.categories.all()
        # Get footwear products
        footwear_products = Product.objects.filter(
            category__in=footwear_categories
        ).order_by('-id')
    except HeadCategory.DoesNotExist:
        footwear_categories = []
        footwear_products = []
    except:
        footwear_categories = []
        footwear_products = []
    
    # Get Jacket products for the Drip section
    drip_products = []
    try:
        jacket_category = Category.objects.get(name='Jacket')
        drip_products = jacket_category.products.all().order_by('-id')[:8]
    except Category.DoesNotExist:
        drip_products = []
    except:
        drip_products = []
    
    context = {
        'categories': categories,
        'head_categories': head_categories,
        'new_arrivals': new_arrivals,
        'all_products': all_products,  # Add all products for slider
        'footwear_categories': footwear_categories,
        'footwear_products': footwear_products,  # Add footwear products
        'drip_products': drip_products
    }
    
    return render(request, 'app/pages/home.html', context)


def userLogin(request):
    categories = get_categories()
    head_categories = get_head_categories()
    
    # If user is already authenticated, redirect to home
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Validate input
        if not username or not password:
            messages.error(request, 'Please provide both username and password.')
            return render(request, 'app/auth/userLogin.html', {
                'categories': categories, 
                'head_categories': head_categories
            })
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            # Check if there's a next parameter to redirect to a specific page
            next_page = request.GET.get('next')
            if next_page:
                return redirect(next_page)
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials. Please check your username and password and try again.')
    
    return render(request, 'app/auth/userLogin.html', {
        'categories': categories, 
        'head_categories': head_categories
    })


def userRegister(request):
    categories = get_categories()
    head_categories = get_head_categories()
    
    # If user is already authenticated, redirect to home
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        email = request.POST.get('email').strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validate input
        if not username or not email or not password or not confirm_password:
            messages.error(request, 'All fields are required')
            return render(request, 'app/auth/userRegister.html', {
                'categories': categories, 
                'head_categories': head_categories
            })
            
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'app/auth/userRegister.html', {
                'categories': categories, 
                'head_categories': head_categories
            })
            
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters long')
            return render(request, 'app/auth/userRegister.html', {
                'categories': categories, 
                'head_categories': head_categories
            })
            
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username Already Exists')
            return render(request, 'app/auth/userRegister.html', {
                'categories': categories, 
                'head_categories': head_categories
            })
            
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email Already Exists')
            return render(request, 'app/auth/userRegister.html', {
                'categories': categories, 
                'head_categories': head_categories
            })
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # Create a profile for the new user
            from .models import Profile
            Profile.objects.create(user=user)
            
            # Authenticate and login the user
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Account created successfully! Welcome {user.username}!')
                return redirect('home')
            else:
                messages.success(request, 'Account created successfully! Please login.')
                return redirect('login')
                
        except Exception as e:
            messages.error(request, 'An error occurred during registration. Please try again.')
            return render(request, 'app/auth/userRegister.html', {
                'categories': categories, 
                'head_categories': head_categories
            })
        
    return render(request, 'app/auth/userRegister.html', {
        'categories': categories, 
        'head_categories': head_categories
    })


def userLogout(request):
    """Logout view to handle user logout"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')


def productInfo(request, slug):
    # Get the product by slug or return 404 if not found
    product = get_object_or_404(Product, slug=slug)
    # Get related products (same category, limit to 4)
    related_products = Product.objects.filter(category=product.category).exclude(slug=slug)[:4]
    # Get all possible sizes
    all_sizes = Size.objects.all().order_by('id')
    # Get all possible shoe sizes
    all_shoe_sizes = ShoeSize.objects.all().order_by('size')
    categories = get_categories()
    head_categories = get_head_categories()
    return render(request, 'app/product/productInfo.html', {
        'product': product,
        'related_products': related_products,
        'all_sizes': all_sizes,
        'all_shoe_sizes': all_shoe_sizes,
        'categories': categories,
        'head_categories': head_categories
    })


def userProfile(request):
    # Make sure user is authenticated
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to view your profile')
        return redirect('login')
    
    # Get or create user's profile
    try:
        profile = request.user.profile
    except:
        from .models import Profile
        profile = Profile.objects.create(user=request.user)
    
    if request.method == 'POST':
        # Update profile with form data
        profile.full_name = request.POST.get('full_name', profile.full_name)
        profile.gender = request.POST.get('gender', profile.gender)
        profile.address = request.POST.get('address', profile.address)
        profile.city = request.POST.get('city', profile.city)
        profile.state = request.POST.get('state', profile.state)
        profile.pincode = request.POST.get('pincode', profile.pincode)
        profile.size = request.POST.get('size', profile.size)
        
        # Update user's phone number
        phone_no = request.POST.get('phone_no')
        if phone_no:
            request.user.phone_no = phone_no
            request.user.save()
        
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        
        profile.save()
        
        # Add success message
        messages.success(request, 'Profile updated successfully!')
        
        # Redirect to prevent re-submission
        return redirect('userProfile')
    
    # Add choice dictionaries to profile for template access
    from .models import Profile as ProfileModel
    profile.GENDER_CHOICES_DICT = ProfileModel.GENDER_CHOICES_DICT
    profile.SIZE_CHOICES_DICT = ProfileModel.SIZE_CHOICES_DICT
    
    categories = get_categories()
    head_categories = get_head_categories()
    context = {
        'profile': profile,
        'categories': categories,
        'head_categories': head_categories
    }
    return render(request, 'app/pages/userProfile.html', context)

# ------------------------ Product Section -----------------------------------

def AllProduct(request):
    products = Product.objects.all()
    categories = get_categories()
    head_categories = get_head_categories()
    return render(request, 'app/product/AllProduct.html', {'products':products, 'categories': categories, 'head_categories': head_categories})


def newArrival(request):
    # Get products ordered by ID in descending order (newest first)
    products = Product.objects.all().order_by('-id')[:12]  # Limit to 12 newest products
    categories = get_categories()
    head_categories = get_head_categories()
    return render(request, 'app/product/newArrival.html', {'products':products, 'categories': categories, 'head_categories': head_categories})


def category_products(request, category_slug):
    # Get the category by slug or return 404 if not found
    category = get_object_or_404(Category, slug=category_slug)
    # Get all products in this category
    products = Product.objects.filter(category=category)
    categories = get_categories()
    head_categories = get_head_categories()
    return render(request, 'app/product/category_products.html', {
        'category': category,
        'products': products,
        'categories': categories,
        'head_categories': head_categories
    })


def search_products(request):
    """Search products by name, category, or other relevant fields"""
    query = request.GET.get('q', '')
    products = []
    
    # Debug: Print the query to see what we're receiving
    print(f"Search query received: '{query}'")
    
    if query:
        # Normalize the query for better matching
        normalized_query = query.strip()
        
        # Create multiple search variations
        search_terms = [normalized_query]
        
        # Add variation with hyphens instead of spaces
        if ' ' in normalized_query:
            search_terms.append(normalized_query.replace(' ', '-'))
        
        # Add variation with spaces instead of hyphens
        if '-' in normalized_query:
            search_terms.append(normalized_query.replace('-', ' '))
        
        # Add lowercase variations
        search_terms.append(normalized_query.lower())
        search_terms.append(normalized_query.title())
        search_terms.append(normalized_query.upper())
        
        # Add lowercase variations with hyphens/spaces
        for term in search_terms[:]:  # Iterate over a copy to avoid modification during iteration
            if ' ' in term:
                search_terms.append(term.replace(' ', '-').lower())
                search_terms.append(term.replace(' ', '-').title())
                search_terms.append(term.replace(' ', '-').upper())
            if '-' in term:
                search_terms.append(term.replace('-', ' ').lower())
                search_terms.append(term.replace('-', ' ').title())
                search_terms.append(term.replace('-', ' ').upper())
        
        # Remove duplicates while preserving order
        seen = set()
        unique_search_terms = []
        for term in search_terms:
            if term not in seen:
                seen.add(term)
                unique_search_terms.append(term)
        
        search_terms = unique_search_terms
        print(f"Search terms generated: {search_terms}")
        
        # Build query conditions for all search terms
        conditions = Q()
        for term in search_terms:
            term_condition = (
                Q(name__icontains=term) | 
                Q(category__name__icontains=term) | 
                Q(description__icontains=term)
            )
            conditions |= term_condition  # Use OR to combine terms
        
        # Search for products matching the query
        products = Product.objects.filter(conditions).distinct().order_by('-id')  # Show newest products first
        
        # If no products found, try case-insensitive exact match as fallback
        if not products.exists() and search_terms:
            fallback_conditions = Q()
            for term in search_terms:
                fallback_condition = (
                    Q(name__iexact=term) | 
                    Q(category__name__iexact=term) | 
                    Q(description__iexact=term)
                )
                fallback_conditions |= fallback_condition
            products = Product.objects.filter(fallback_conditions).distinct().order_by('-id')
        
        # Debug: Print number of products found
        print(f"Products found: {products.count()}")
        if products.exists():
            print(f"Product names: {[p.name for p in products]}")
    
    categories = get_categories()
    head_categories = get_head_categories()
    context = {
        'query': query,
        'products': products,
        'categories': categories,
        'head_categories': head_categories
    }
    return render(request, 'app/product/search_results.html', context)


def search_suggestions(request):
    """API endpoint for search suggestions"""
    query = request.GET.get('q', '')
    suggestions = []
    
    if query:
        # Get products matching the query
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(category__name__icontains=query)
        ).distinct()[:8]  # Limit to 8 suggestions
        
        # Format suggestions
        for product in products:
            suggestions.append({
                'name': product.name,
                'category': product.category.name,
                'slug': product.slug
            })
    
    return JsonResponse(suggestions, safe=False)


def add_to_cart(request):
    """Add a product to the cart"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            size_id = data.get('size_id')
            shoe_size_id = data.get('shoe_size_id')  # New field for shoe sizes
            quantity = int(data.get('quantity', 1))
            
            # Get the product
            product = get_object_or_404(Product, id=product_id)
            
            # Get the size or shoe size based on product type
            size = None
            shoe_size = None
            if product.is_footwear:
                # For footwear products, only use shoe_size_id
                if shoe_size_id:
                    shoe_size = get_object_or_404(ShoeSize, id=shoe_size_id)
                # If no shoe size is selected for footwear, this is an error
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Please select a shoe size for footwear products'
                    })
            else:
                # For clothing products, only use size_id
                if size_id:
                    size = get_object_or_404(Size, id=size_id)
                # If no size is selected for clothing, this is an error
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Please select a size for clothing products'
                    })
            
            # Get or create cart
            cart = get_or_create_cart(request)
            
            # Check if item already exists in cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                size=size,
                shoe_size=shoe_size,
                defaults={'quantity': quantity}
            )
            
            # If item exists, update quantity
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            # Return success response
            return JsonResponse({
                'success': True,
                'message': f'{product.name} added to cart successfully!',
                'cart_total_items': cart.get_total_items()
            })
        except Exception as e:
            # Log the actual error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error adding product to cart: {str(e)}", exc_info=True)
            
            return JsonResponse({
                'success': False,
                'message': f'Error adding product to cart: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })


def update_cart_item(request):
    """Update quantity of a cart item"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_id = data.get('item_id')
            quantity = int(data.get('quantity'))
            
            # Get the cart item
            cart = get_or_create_cart(request)
            cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
            
            if quantity <= 0:
                # Remove item if quantity is 0 or less
                cart_item.delete()
            else:
                # Update quantity
                cart_item.quantity = quantity
                cart_item.save()
            
            # Return success response with updated totals
            return JsonResponse({
                'success': True,
                'message': 'Cart updated successfully!',
                'subtotal': float(cart.get_total_price()),
                'total_items': cart.get_total_items()
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Error updating cart item'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })


def remove_cart_item(request):
    """Remove an item from the cart"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_id = data.get('item_id')
            
            # Get the cart item
            cart = get_or_create_cart(request)
            cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
            
            # Remove item
            cart_item.delete()
            
            # Return success response with updated totals
            return JsonResponse({
                'success': True,
                'message': 'Item removed from cart!',
                'subtotal': float(cart.get_total_price()),
                'total_items': cart.get_total_items()
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Error removing cart item'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })


def view_cart(request):
    """Display the cart page"""
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()
    categories = get_categories()
    head_categories = get_head_categories()
    
    context = {
        'cart_items': cart_items,
        'cart': cart,
        'categories': categories,
        'head_categories': head_categories
    }
    return render(request, 'app/product/cart.html', context)


def checkout(request):
    """Display the checkout page"""
    # Make sure user is authenticated
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to checkout')
        return redirect('login')
    
    # Get user's cart
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()
    
    # Check if cart is empty
    if not cart_items.exists():
        messages.error(request, 'Your cart is empty')
        return redirect('view_cart')
    
    # Get or create user's profile
    try:
        profile = request.user.profile
    except:
        from .models import Profile
        profile = Profile.objects.create(user=request.user)
    
    categories = get_categories()
    head_categories = get_head_categories()
    
    context = {
        'cart_items': cart_items,
        'cart': cart,
        'profile': profile,
        'categories': categories,
        'head_categories': head_categories
    }
    return render(request, 'app/product/checkout.html', context)


def process_checkout(request):
    """Process the checkout form submission"""
    if request.method == 'POST':
        # Make sure user is authenticated
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'message': 'Please login to checkout'
            })
        
        # Get user's cart
        cart = get_or_create_cart(request)
        cart_items = cart.items.all()
        
        # Check if cart is empty
        if not cart_items.exists():
            return JsonResponse({
                'success': False,
                'message': 'Your cart is empty'
            })
        
        try:
            # Get form data
            full_name = request.POST.get('fullName')
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            address_line1 = request.POST.get('address1')
            address_line2 = request.POST.get('address2', '')
            city = request.POST.get('city')
            state = request.POST.get('state')
            pincode = request.POST.get('pincode')
            payment_method = request.POST.get('paymentMethod')
            
            # Debug: Print received data
            print(f"Received data: full_name={full_name}, phone={phone}, email={email}, address_line1={address_line1}, city={city}, state={state}, pincode={pincode}, payment_method={payment_method}")
            
            # Validate required fields with specific error messages
            missing_fields = []
            if not full_name:
                missing_fields.append("Full Name")
            if not phone:
                missing_fields.append("Phone Number")
            if not email:
                missing_fields.append("Email Address")
            if not address_line1:
                missing_fields.append("Address Line 1")
            if not city:
                missing_fields.append("City")
            if not state:
                missing_fields.append("State")
            if not pincode:
                missing_fields.append("Pincode")
            if not payment_method:
                missing_fields.append("Payment Method")
                
            if missing_fields:
                return JsonResponse({
                    'success': False,
                    'message': f'Please fill in the following required fields: {", ".join(missing_fields)}'
                })
            
            # Update user's profile with address information
            profile = request.user.profile
            profile.full_name = full_name
            profile.address = f"{address_line1}\n{address_line2}".strip()
            profile.city = city
            profile.state = state
            profile.pincode = pincode
            profile.save()
            
            # Update user's phone number
            request.user.phone_no = phone
            request.user.save()
            
            # TODO: Implement actual payment processing here
            # For now, we'll just simulate a successful payment
            
            # Clear the cart after successful checkout
            cart.items.all().delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Order placed successfully!',
                'redirect_url': '/thank-you/'  # Redirect to payment done page after successful checkout
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'An error occurred while processing your order. Please try again.'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })


# ----------------------------- Extra Page Views STARTING---------------------------------

def faq(request):
    categories = get_categories()
    head_categories = get_head_categories()
    return render(request, 'app/extra/faq.html', {'categories': categories, 'head_categories': head_categories})


def sizeGuide(request):
    categories = get_categories()
    head_categories = get_head_categories()
    return render(request, 'app/extra/sizeGuide.html', {'categories': categories, 'head_categories': head_categories})


def storeLocations(request):
    categories = get_categories()
    head_categories = get_head_categories()
    return render(request, 'app/extra/storeLocations.html', {'categories': categories, 'head_categories': head_categories})

def careInstruction(request):
    categories = get_categories()
    head_categories = get_head_categories()
    return render(request, 'app/extra/careInstruction.html', {'categories': categories, 'head_categories': head_categories})

def returnExchanges(request):
    categories = get_categories()
    head_categories = get_head_categories()
    return render(request, 'app/extra/returnExchanges.html', {'categories': categories, 'head_categories': head_categories})


def sustainability(request):
    categories = get_categories()
    head_categories = get_head_categories()
    return render(request, 'app/extra/Sustainability.html', {'categories': categories, 'head_categories': head_categories})


def press(request):
    categories = get_categories()
    head_categories = get_head_categories()
    return render(request, 'app/extra/press.html', {'categories': categories, 'head_categories': head_categories})


def ourstory(request):
    categories = get_categories()
    head_categories = get_head_categories()
    return render(request, 'app/extra/ourstory.html', {'categories': categories, 'head_categories': head_categories})


def paymentdone(request):
    categories = get_categories()
    head_categories = get_head_categories()
    return render(request, 'app/extra/paymentdone.html', {'categories': categories, 'head_categories': head_categories})


# ----------------------------- Extra Page Views ENDING---------------------------------


# -------------------- Social Page STARTING -----------------------------

def instagram(request):
    categories = get_categories()
    head_categories = get_head_categories()
    return render(request, 'app/social/instagram.html', {'categories': categories, 'head_categories': head_categories})


# -------------------- Social Page ENDING -----------------------------


# ----------------------------- Extra Page Views  ENDING ---------------------------------