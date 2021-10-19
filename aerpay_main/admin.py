from django.contrib import admin
from .models import AerUser, CartOrder, Category, Coupon, CouponUsed, FMCGProduct, FMCGTransaction, OrderTrackingStage, Product, ProductOrder, QuantityType, Store, SubscriptionPrice
from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

@admin.register(SubscriptionPrice)
class SubscriptionPriceAdmin(admin.ModelAdmin):
    list_display = ['id', 'new_price', 'changed_or_added_at']
    search_fields = ['new_price', 'changed_or_added_at']

@admin.register(QuantityType)
class QuantityTypeAdmin(admin.ModelAdmin):
    list_display = ['type_label',]
    search_fields = ['type_label']

@admin.register(OrderTrackingStage)
class OrderTrackingStageAdmin(admin.ModelAdmin):
    list_display = ['order_tracking_stage_label', 'order_tracking_stage_number']
    search_fields = ['order_tracking_stage_label']

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'email', 'last_paid_subscription_date', 'subscription_renewal_date', 'phone_number']
    search_fields = ['name']
    readonly_fields=['owner', 'email', 'help_desk_email', 'name', 'phone_number', 'image', 'base64Image', 'imageType', 'address', 'address_latitude', 'address_longitude', 'default_subscription_price', 'subscription_renewal_price', 'last_paid_subscription_date', 'subscription_renewal_date', 'own_referal_code', 'refered_by_store_referal_code', 'no_of_ratings', 'rating']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'store', 'id']
    search_fields = ['name']
    readonly_fields=['name', 'store']

@admin.register(FMCGProduct)
class FMCGProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'quantity_in_stock', 'quantity_type', 'price', 'discounted_price']
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'id', 'category', 'quantity_in_stock', 'quantity_type', 'price', 'discounted_price', 'number_of_orders_for_this_product_uptill_now']
    search_fields = ['name']
    readonly_fields=['name', 'category', 'initial_quantity', 'quantity_in_stock', 'quantity_type', 'price', 'discounted_price', 'is_out_of_stock', 'number_of_orders_for_this_product_uptill_now']

@admin.register(FMCGTransaction)
class FMCGTransactionAdmin(admin.ModelAdmin):
    list_display = ['fmcg_product', 'id', 'store', 'transaction_occured_at', 'quantity_taken_from_fmcg', 'total_cost_at_the_time']
    search_fields = ['fmcg_product__name']
    readonly_fields=['fmcg_product', 'store', 'transaction_occured_at', 'quantity_taken_from_fmcg', 'total_cost_at_the_time']

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'owner', 'store', 'category', 'product', 'minimum_order_Rs', 'discount_amount', 'discount_type', 'uses_per_customer']
    search_fields = ['code']
    readonly_fields=['code', 'owner', 'store', 'category', 'product', 'minimum_order_Rs', 'discount_amount', 'discount_type', 'uses_per_customer']

@admin.register(CouponUsed)
class CouponUsedAdmin(admin.ModelAdmin):
    list_display = ['coupon', 'user', 'uses_used']
    search_fields = ['coupon__code']
    readonly_fields=['coupon', 'user', 'uses_used']

@admin.register(CartOrder)
class CartOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'customer', 'store', 'id', 'total_price', 'discounted_total_price', 'order_accepted_at', 'order_tracking_stage_label']
    search_fields = ['customer_name']
    readonly_fields=['customer', 'store', 'coupon_code', 'customer_name', 'customer_address', 'customer_address_latitude', 'customer_address_longitude', 'customer_phone_number', 'total_price', 'discounted_total_price', 'order_placed_at', 'is_accepted', 'order_accepted_at', 'is_payment_method_selected', 'payment_method_selected_at', 'payment_method', 'is_online_payment_sent', 'is_save_cart', 'order_tracking_stage_number', 'order_tracking_stage_label']

@admin.register(ProductOrder)
class ProductOrderAdmin(admin.ModelAdmin):
    list_display = ['cart', 'id', 'product', 'product_name', 'priced_at', 'discounted_priced_at', 'quantity_demanded', 'total_price']
    search_fields = ['product__name']
    readonly_fields=['cart', 'product', 'product_name', 'priced_at', 'discounted_priced_at', 'quantity_demanded', 'total_price']

class AerUserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'name', 'is_admin')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'phone_number', 'image', 'address', 'address_latitude', 'address_longitude')}),
        ('Permissions', {'fields': ('is_admin',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'name')
    ordering = ('email',)
    filter_horizontal = ()
    list_display = ['id', 'email', 'name']


# Now register the new UserAdmin...
admin.site.register(AerUser, AerUserAdmin)

# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)