from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, HeadCategory, Category, Product, ProductImage, Profile, Size


# --- CustomUser Admin ---
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'phone_no', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone_no',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('phone_no',)}),
    )


# --- HeadCategory Admin ---
@admin.register(HeadCategory)
class HeadCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


# --- Size Admin ---
@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


# --- ProductImage Inline (for multiple product images) ---
class ProductImageInline(admin.TabularInline):  # or StackedInline for larger previews
    model = ProductImage
    extra = 1  # shows one empty image field by default


# --- Product Admin ---
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price']
    search_fields = ['name', 'category__name']
    list_filter = ['category']
    filter_horizontal = ('available_sizes',)  # Use filter_horizontal for many-to-many fields
    inlines = [ProductImageInline]  # ✅ Allows adding multiple images directly from product page


# --- Category Admin ---
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'head_category']
    search_fields = ['name']
    list_filter = ['head_category']


# --- Profile Admin ---
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'gender', 'city', 'state']
    search_fields = ['user__username', 'full_name', 'city']
    list_filter = ['gender', 'state']