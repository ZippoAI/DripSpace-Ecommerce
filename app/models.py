from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.core.exceptions import ValidationError


class CustomUser(AbstractUser):
    phone_no = models.CharField(max_length=13, blank=True)


class HeadCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(blank=True, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='headcategories/', blank=True, null=True)
    
    def save(self, *args, **kwargs):
        # Generate slug if missing or if name has changed
        if not self.slug or slugify(self.name) != self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Category(models.Model):
    head_category = models.ForeignKey(HeadCategory, on_delete=models.CASCADE, related_name='categories', null=True, blank=True)
    name = models.CharField(max_length=50)
    slug = models.SlugField(blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    def save(self, *args, **kwargs):
        # Generate slug if missing or if name has changed
        if not self.slug or slugify(self.name) != self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Size(models.Model):
    SIZE_CHOICES = [
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
    ]
    
    name = models.CharField(max_length=10, choices=SIZE_CHOICES, unique=True)
    
    def __str__(self):
        return str(self.name)


class ShoeSize(models.Model):
    # Shoe sizes for footwear (US sizes)
    SIZE_CHOICES = [
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('10', '10'),
        ('11', '11'),
        ('12', '12'),
        ('13', '13'),
    ]
    
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, unique=True)
    
    def __str__(self):
        return str(self.size)


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    description = models.TextField(blank=True)
    
    # Many-to-many relationship for available sizes
    available_sizes = models.ManyToManyField(Size, blank=True, related_name='products')
    # Many-to-many relationship for available shoe sizes
    available_shoe_sizes = models.ManyToManyField(ShoeSize, blank=True, related_name='products')

    def save(self, *args, **kwargs):
        # Generate slug if missing or outdated
        if not self.slug or slugify(self.name) != self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.name)

    @property
    def is_footwear(self):
        """Check if this product belongs to a footwear category"""
        if self.category and self.category.head_category:
            return self.category.head_category.name == 'Footwear'
        return False


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    def delete(self, *args, **kwargs):
        self.image.delete(save=False)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - Image {self.id}"


class Profile(models.Model):
    GENDER_CHOICES_DICT = {
        'Male': 'Male',
        'Female': 'Female',
        'Other': 'Other',
    }

    SIZE_CHOICES_DICT = {
        'XS': 'XS',
        'S': 'S',
        'M': 'M',
        'L': 'L',
        'XL': 'XL',
        'XXL': 'XXL',
    }

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=[(k, v) for k, v in GENDER_CHOICES_DICT.items()],
        blank=True
    )
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    size = models.CharField(
        max_length=10,
        choices=[(k, v) for k, v in SIZE_CHOICES_DICT.items()],
        blank=True
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        else:
            return f"Cart for session {self.session_key}"

    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE, null=True, blank=True)
    shoe_size = models.ForeignKey(ShoeSize, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_total_price(self):
        return self.product.price * self.quantity

    def clean(self):
        """Validate that footwear products use shoe_size and clothing products use size"""
        # Skip validation if product is not set
        if not self.product:
            return
            
        if self.product.is_footwear:
            # For footwear products, shoe_size must be set and size must be None
            if self.size is not None:
                raise ValidationError("Footwear products should not have a clothing size")
            # Only require shoe_size if this is a new item being created (not updating quantity)
            if self.shoe_size is None and self.pk is None:
                # Check if we're creating a new item
                if hasattr(self, '_state') and not self._state.adding:
                    # This is an update, so we don't need to validate shoe_size
                    pass
                else:
                    # This is a new item, so shoe_size is required
                    raise ValidationError("Please select a shoe size for footwear products")
        else:
            # For clothing products, size must be set and shoe_size must be None
            if self.shoe_size is not None:
                raise ValidationError("Clothing products should not have a shoe size")
            # Only require size if this is a new item being created (not updating quantity)
            if self.size is None and self.pk is None:
                # Check if we're creating a new item
                if hasattr(self, '_state') and not self._state.adding:
                    # This is an update, so we don't need to validate size
                    pass
                else:
                    # This is a new item, so size is required
                    raise ValidationError("Please select a size for clothing products")

    def save(self, *args, **kwargs):
        """Override save to enforce validation"""
        self.clean()
        super().save(*args, **kwargs)

    @property
    def display_size(self):
        """Return the appropriate size for display based on product type"""
        if self.product and self.product.is_footwear and self.shoe_size:
            return self.shoe_size.size
        elif self.size:
            return self.size.name
        return None
