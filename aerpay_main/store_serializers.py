from rest_framework import serializers

from aerpay_main.models import Category, Coupon, FMCGProduct, FMCGTransaction, Product, QuantityType, Store, SubscriptionPrice

class SubscriptionPriceGetSrlzr(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPrice
        fields = ('id', 'new_price',)

class QuantityTypesGetSrlzr(serializers.ModelSerializer):
    class Meta:
        model = QuantityType
        fields = ('id', 'type_label',)

class StoreRegisterSrlzr(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ('email', 'help_desk_email',
                  'name', 'phone_number', 'image', 'base64Image', 'imageType', 
                  'description', 'address', 'address_latitude', 'address_longitude', 
                  'refered_by_store_referal_code',)

class StoreProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'category', 'name', 'image', 'quantity_type', 'price', 'discounted_price', 'is_out_of_stock')

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['category'] = instance.category.name
        return rep

class StoreListSrlzr(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    class Meta:
        model = Store
        fields = ('id','name', 'image', 'address', 
                  'description', 'no_of_ratings', 'rating', 'products')
    
    def get_products(self, obj):
        selected_products = Product.objects.filter(
            category__store=obj).distinct()[0:5]
        return StoreProductsSerializer(selected_products, many=True).data

class StoreGetSrlzr(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ('id', 'email', 'help_desk_email',
                  'name', 'phone_number', 'image', 'base64Image', 'imageType', 'address', 'address_latitude', 'address_longitude', 
                  'description', 'default_subscription_price', 'subscription_renewal_price', 
                  'last_paid_subscription_date', 'subscription_renewal_date', 
                  'refered_by_store_referal_code', 'own_referal_code', 'no_of_ratings', 'rating')


class StoreUpdateSrlzr(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ('email', 'help_desk_email',
                  'name', 'phone_number', 'image', 'base64Image', 'imageType', 
                  'description', 'address', 'address_latitude', 'address_longitude',)


class CategoryMdlSrlzr(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'image', 'base64Image', 'imageType')

class ProductCreateSrlzr(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('category', 'name', 'image', 'base64Image', 'imageType', 
                  'description', 'quantity_type', 'initial_quantity',
                  'price', 'discounted_price',)

class ProductGetSrlzr(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'category', 'name', 'image', 'base64Image', 'imageType', 'description', 'quantity_type',
                  'initial_quantity', 'quantity_in_stock', 'price', 'discounted_price', 
                  'is_out_of_stock')

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['category'] = CategoryMdlSrlzr(
            instance.category).data
        return rep

class ProductUpdateSrlzr(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('category', 'name', 'image', 'base64Image', 'imageType', 
                  'description', 'quantity_type',
                  'price', 'discounted_price',)

class RefillProductSrlzr(serializers.Serializer):
    new_quantity_in_stock = serializers.IntegerField()

class ProductDeleteSrlzr(serializers.Serializer):
    id = serializers.IntegerField()

class CategoryCreateSrlzr(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'image', 'base64Image', 'imageType')

class CatProductsSrlzr(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'image', 'description', 'quantity_type',
                  'quantity_in_stock', 'price', 'discounted_price', 
                  'is_out_of_stock')

class CategoryGetSrlzr(serializers.ModelSerializer):
    products = CatProductsSrlzr(
        many=True, read_only=True)
    class Meta:
        model = Category
        fields = ('id', 'name', 'image', 'products')

class StoreUsrGetSrlzr(serializers.ModelSerializer):
    categories = CategoryGetSrlzr(
        many=True, read_only=True)
    class Meta:
        model = Store
        fields = ('id', 'email', 'help_desk_email',
                  'name', 'phone_number', 'image', 'address', 'address_latitude', 'address_longitude', 
                  'description', 'no_of_ratings', 'rating', 'categories')


class CategoryUpdateSrlzr(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'image', 'base64Image', 'imageType')

class CategoryDeleteSrlzr(serializers.Serializer):
    id = serializers.IntegerField()

class FMCGStrProductGetSrlzr(serializers.ModelSerializer):
    class Meta:
        model = FMCGProduct
        fields = ('id', 'name', 'image', 'description', 'quantity_type',
                  'quantity_in_stock', 'price', 'discounted_price', 
                  'is_out_of_stock')

class FMCGTrnsctnCreateSrlzr(serializers.ModelSerializer):
    class Meta:
        model = FMCGTransaction
        fields = ('fmcg_product', 
                  'quantity_taken_from_fmcg', 'total_cost_at_the_time')

class FMCGTrnsctnGetSrlzr(serializers.ModelSerializer):
    class Meta:
        model = FMCGTransaction
        fields = ('id', 'fmcg_product', 'transaction_occured_at', 
                  'quantity_taken_from_fmcg', 'total_cost_at_the_time',)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['fmcg_product'] = FMCGStrProductGetSrlzr(
            instance.fmcg_product).data
        return rep

class CouponGnrtSrlzr(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ('category', 'product',
                  'minimum_order_Rs', 'discount_type',
                  'discount_amount', 'uses_per_customer')

class CouponGetSrlzr(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ('id', 'category', 'product', 'code',
                  'minimum_order_Rs', 'discount_type',
                  'discount_amount', 'uses_per_customer')
                
class CouponDeleteSrlzr(serializers.Serializer):
    id = serializers.IntegerField()

