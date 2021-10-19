from django.db import models

from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.contrib.auth.hashers import make_password
from django.db.models.fields.related import OneToOneField

from myStorage import OverwriteStorage
from datetime import datetime, timedelta
from django.dispatch import receiver

# add 2 models: 1 for order tracking, and one for quantity types

class AerUserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class AerUser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    image = models.ImageField(
        upload_to='profile_images', blank=True, null=True, storage=OverwriteStorage())
    base64Image = models.TextField(blank=True, null=True)
    imageType = models.CharField(max_length=10, blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    address = models.TextField(blank=True, null=True)
    address_latitude = models.CharField(max_length=50, blank=True, null=True)
    address_longitude = models.CharField(max_length=50, blank=True, null=True)

    objects = AerUserManager()

    USERNAME_FIELD = 'email'

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    def __str__(self):
        return 'ID: ' + str(self.id) + ', USER EMAIL: ' + self.email    

class SubscriptionPrice(models.Model):
    new_price = models.DecimalField(default=0.0, max_digits=12,decimal_places=2)
    changed_or_added_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-changed_or_added_at']

    def __str__(self):
        return 'ID: ' + str(self.id) + ', SUBSCRIPTION PRICE: ' + str(self.new_price)  


class QuantityType(models.Model):
    type_label = models.CharField(max_length=20, blank=True, null=True)

class OrderTrackingStage(models.Model):
    order_tracking_stage_number = models.IntegerField()
    order_tracking_stage_label = models.CharField(max_length=20, blank=True, null=True)

class Store(models.Model):
    # add a save mwthod to store the personal info here
    owner = OneToOneField(AerUser, related_name='store', on_delete=models.CASCADE, blank=True, null=True)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    help_desk_email = models.EmailField(
        max_length=255,
    )
    name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    image = models.ImageField(
        upload_to='store_images', blank=True, null=True, storage=OverwriteStorage())
    base64Image = models.TextField(blank=True, null=True)
    imageType = models.CharField(max_length=10, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    address_latitude = models.CharField(max_length=50, blank=True, null=True)
    address_longitude = models.CharField(max_length=50, blank=True, null=True)
    default_subscription_price = models.DecimalField(default=0.0, max_digits=12,decimal_places=2)
    subscription_renewal_price = models.DecimalField(default=0.0, max_digits=12,decimal_places=2)
    last_paid_subscription_date = models.DateField(blank=True, null=True)
    subscription_renewal_date = models.DateField(blank=True, null=True)
    # how will it know that today is payday and reset
    # it will reset everytime the payment is made
    # will need an api to generate new referal codes bsically, will always be unique because it will be a 
    # length 5 string + store id + store name. length 5 string can be same, but store id can never be
    own_referal_code = models.CharField(max_length=100, blank=True, null=True)
    refered_by_store_referal_code = models.CharField(max_length=100, blank=True, null=True)
    no_of_ratings = models.IntegerField(default=0)
    rating = models.DecimalField(default=0.0, max_digits=3,decimal_places=2)
# so before any function, it will check if today is not beyond the next renewal date, or if
# (next renewel date and last paid date is not none), else it will logout

    def __str__(self):
        return 'ID: ' + str(self.id) + ', STORE: ' + self.name

    class Meta:
        ordering = ['-rating']

# cost_after_discounts in order details
# create a category of general products for the case where no category is chosen for a product
class Category(models.Model):
    store = models.ForeignKey(Store, related_name='categories', on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=200,)
    image = models.ImageField(
        upload_to='category_images', blank=True, null=True, storage=OverwriteStorage())
    base64Image = models.TextField(blank=True, null=True)
    imageType = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return 'ID: ' + str(self.id) + ', CATEGORY NAME: ' + self.name  

class FMCGProduct(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(
        upload_to='product_images', blank=True, null=True, storage=OverwriteStorage())
    base64Image = models.TextField(blank=True, null=True)
    imageType = models.CharField(max_length=10, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    quantity_type = models.CharField(max_length=50)
    initial_quantity = models.DecimalField(default=0.0, max_digits=16,decimal_places=3)
    quantity_in_stock = models.DecimalField(default=0.0, max_digits=16,decimal_places=3)
    price = models.DecimalField(default=0.0, max_digits=15,decimal_places=2)
    discounted_price = models.DecimalField(default=0.0, max_digits=15,decimal_places=2)
    is_out_of_stock = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.quantity_in_stock <= 0.0:
            self.is_out_of_stock = True
        else:
            self.is_out_of_stock = False

        if self.discounted_price == None or self.discounted_price == 0.0:
            self.discounted_price = self.price
        if self.id == None:
            self.quantity_in_stock = self.initial_quantity

        super(FMCGProduct, self).save(False)
    
    def __str__(self):
        return 'ID: ' + str(self.id) + ', FMCG NAME: ' + self.name  

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=100)
    image = models.ImageField(
        upload_to='product_images', blank=True, null=True, storage=OverwriteStorage())
    base64Image = models.TextField(blank=True, null=True)
    imageType = models.CharField(max_length=10, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    quantity_type = models.CharField(max_length=50)
    initial_quantity = models.DecimalField(default=0.0, max_digits=16,decimal_places=3)
    # quantity in stock will be read only managed from change in initial quantity
    # in presave
    quantity_in_stock = models.DecimalField(default=0.0, max_digits=16,decimal_places=3)
    price = models.DecimalField(default=0.0, max_digits=15,decimal_places=2)
    discounted_price = models.DecimalField(default=0.0, max_digits=15,decimal_places=2)
    is_out_of_stock = models.BooleanField(default=False)
    number_of_orders_for_this_product_uptill_now = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.discounted_price == None or self.discounted_price == 0.0:
            self.discounted_price = self.price
        if self.id == None:
            self.quantity_in_stock = self.initial_quantity
            
        if self.quantity_in_stock <= 0.0:
            self.is_out_of_stock = True
        else:
            self.is_out_of_stock = False
            
        super(Product, self).save(False)

    class Meta:
        ordering = ['-number_of_orders_for_this_product_uptill_now']

    def __str__(self):
        return 'ID: ' + str(self.id) + ', PRODUCT NAME: ' + self.name  
# yeah, add all logic in the apis, save the models only after the payment is made, make the transaction go
# to celery
class FMCGTransaction(models.Model):
    store = models.ForeignKey(Store, related_name='fmcg_purchases', on_delete=models.CASCADE, blank=True, null=True)
    fmcg_product = models.ForeignKey(FMCGProduct, related_name='fmcg_transactions', on_delete=models.CASCADE)
    transaction_occured_at = models.DateTimeField(auto_now_add=True)
    quantity_taken_from_fmcg = models.DecimalField(default=0.0, max_digits=16,decimal_places=3)
    total_cost_at_the_time = models.DecimalField(default=0.0, max_digits=15,decimal_places=2)

    class Meta:
            ordering = ['-transaction_occured_at']

    def __str__(self):
        return 'ID: ' + str(self.id) + ', FMCG TRANSACTION COST: ' + str(self.total_cost_at_the_time ) 

# this will also be a one time generation
class Coupon(models.Model):
    owner = models.ForeignKey(AerUser, related_name='coupons', on_delete=models.CASCADE, blank=True, null=True)
    store = models.ForeignKey(Store, related_name='coupons', on_delete=models.CASCADE, blank=True, null=True)
    category = models.ForeignKey(Category, related_name='coupons', on_delete=models.CASCADE, blank=True, null=True)
    product = models.ForeignKey(Product, related_name='coupons', on_delete=models.CASCADE, blank=True, null=True)
    code = models.CharField(max_length=300, blank=True, null=True)
    minimum_order_Rs = models.DecimalField(default=0.0, max_digits=16,decimal_places=3)
    discount_type = models.CharField(max_length=50, default= 'Flat')
    discount_amount = models.DecimalField(default=0.0, max_digits=4,decimal_places=2)
    uses_per_customer = models.IntegerField(default=0)

    def __str__(self):
        if self.code!= None:
            return 'ID: ' + str(self.id) + ', COUPON CODE: ' + self.code 
        else:
            return 'ID: ' + str(self.id)

class CouponUsed(models.Model):
    coupon = models.ForeignKey(Coupon, related_name='coupon_users', on_delete=models.CASCADE)
    user = models.ForeignKey(AerUser, related_name='coupons_in_use', on_delete=models.CASCADE)
    uses_used = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Coupons used data"

    def __str__(self):
        return 'ID: ' + str(self.id) + ', COUPON: ' + self.coupon.code

# what if the merchant changes the prices

class CartOrder(models.Model):
    # again, this is one time non refundable payment
    customer = models.ForeignKey(AerUser, related_name='orders', on_delete=models.CASCADE)
    store = models.ForeignKey(Store, related_name='orders', on_delete=models.CASCADE)
    # if coupon entered, run the logic in the presave function
    coupon_code = models.CharField(max_length=100, blank=True, null=True)
    customer_name = models.CharField(max_length=100, blank=True, null=True)
    customer_address = models.TextField(blank=True, null=True)
    customer_address_latitude = models.CharField(max_length=50, blank=True, null=True)
    customer_address_longitude = models.CharField(max_length=50, blank=True, null=True)
    customer_phone_number = models.CharField(max_length=15, blank=True, null=True)
    total_price = models.DecimalField(default=0.0, max_digits=16,decimal_places=3)
    discounted_total_price = models.DecimalField(default=0.0, max_digits=16,decimal_places=3)
    order_placed_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)
    order_accepted_at = models.DateTimeField(blank=True, null=True)
    is_payment_method_selected = models.BooleanField(default=False)
    payment_method_selected_at = models.DateTimeField(blank=True, null=True)
    payment_method = models.CharField(max_length=200)
    is_online_payment_sent = models.BooleanField(default=False)
    is_save_cart = models.BooleanField(default=False)
    order_tracking_stage_number = models.IntegerField(default=0)
    order_tracking_stage_label = models.CharField(max_length=50, blank=True, null=True)

    # for all cases, if payment is successful, only then save the model, and take this to celery

    # add all logic in the api calls, make all fields read only in the admin pannel that are user dependent

    class Meta:
        ordering = ['-payment_method_selected_at']

    def __str__(self):
        return 'ID: ' + str(self.id)
# keep product name, and product, and on delete, do not do cascade, but jus make it none

class ProductOrder(models.Model):
    cart = models.ForeignKey(CartOrder, related_name='products', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='orders', on_delete=models.DO_NOTHING, blank=True, null=True)
    product_name = models.CharField(max_length=100, blank=True, null=True)
    product_image = models.ImageField(upload_to='order_images', blank=True, null=True, storage=OverwriteStorage())
    priced_at = models.DecimalField(default=0.0, max_digits=16,decimal_places=3)
    discounted_priced_at = models.DecimalField(default=0.0, max_digits=16,decimal_places=3)
    quantity_demanded = models.DecimalField(default=0.0, max_digits=16,decimal_places=2)
    total_price = models.DecimalField(default=0.0, max_digits=16,decimal_places=3)

    def __str__(self):
        return 'ID: ' + str(self.id)