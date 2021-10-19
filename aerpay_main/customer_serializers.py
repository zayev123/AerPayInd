from rest_framework import serializers

from aerpay_main.models import CartOrder, CouponUsed, OrderTrackingStage, ProductOrder
from aerpay_main.store_serializers import CouponGetSrlzr

class OrderStagesGetSrlzr(serializers.ModelSerializer):
    class Meta:
        model = OrderTrackingStage
        fields = ('id', 'order_tracking_stage_number', 'order_tracking_stage_label',)

class ProductOrderGetSrlzr(serializers.ModelSerializer):
    class Meta:
        model = ProductOrder
        fields = ('id', 'product', 'product_name', 'product_image', 
                  'priced_at', 'discounted_priced_at', 'quantity_demanded', 'total_price')

class ProductOrderDeleteSrlzr(serializers.Serializer):
    id = serializers.IntegerField()

class OrderCreateSrlzr(serializers.Serializer):
    coupon_code = serializers.CharField()
    store_id = serializers.IntegerField()
    customer_name = serializers.CharField()
    customer_address = serializers.CharField()
    customer_address_latitude = serializers.CharField()
    customer_address_longitude = serializers.CharField()
    customer_phone_number = serializers.CharField()
    products = serializers.JSONField()

class CartOrderStrGetSrlzr(serializers.ModelSerializer):
    product_orders = ProductOrderGetSrlzr(
        many=True, read_only=True, source='products')
    
    class Meta:
        model = CartOrder
        fields = ('id', 'coupon_code', 'product_orders', 'customer_name', 'customer_address',
                  'customer_address_latitude', 'customer_address_longitude', 
                  'customer_phone_number', 'total_price', 'discounted_total_price', 'order_placed_at', 
                  'is_accepted', 'order_accepted_at', 'is_payment_method_selected', 'payment_method_selected_at', 
                  'payment_method', 'is_online_payment_sent', 'order_tracking_stage_number', 'order_tracking_stage_label')

class CartOrderCstmrGetSrlzr(serializers.ModelSerializer):
    product_orders = ProductOrderGetSrlzr(
        many=True, read_only=True, source='products')
    
    class Meta:
        model = CartOrder
        fields = ('id', 'store', 'product_orders', 'coupon_code', 'customer_name', 'customer_address',
                  'customer_address_latitude', 'customer_address_longitude',
                  'customer_phone_number', 'total_price', 'discounted_total_price', 'order_placed_at', 
                  'is_accepted', 'order_accepted_at', 'is_payment_method_selected', 'payment_method_selected_at', 
                  'payment_method', 'is_online_payment_sent', 'order_tracking_stage_number', 'order_tracking_stage_label')
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['store'] = instance.store.name
        return rep

class CartOrderStrListSrlzr(serializers.ModelSerializer):
    class Meta:
        model = CartOrder
        fields = ('id', 'customer_name', 'customer_address',
                  'total_price', 'discounted_total_price', 'order_placed_at', 
                  'payment_method', 'is_online_payment_sent', 'order_tracking_stage_number', 'order_tracking_stage_label')
    

class CartOrderCstmrListSrlzr(serializers.ModelSerializer):
    class Meta:
        model = CartOrder
        fields = ('id', 'store', 'customer_name', 'customer_address',
                  'total_price', 'discounted_total_price', 'order_placed_at', 
                  'payment_method', 'is_online_payment_sent', 'order_tracking_stage_number', 'order_tracking_stage_label')
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['store'] = instance.store.name
        return rep

class CartOrderAcceptSrlzr(serializers.Serializer):
    cart_id = serializers.IntegerField()
    accepted = serializers.BooleanField(default=False)

class CartSelectPaymentAndSaveOrderSrlzr(serializers.Serializer):
    cart_id = serializers.IntegerField()
    is_save_cart = serializers.BooleanField(default=False)
    payment_method = serializers.CharField()


class CartUpdateOrderStageSrlzr(serializers.Serializer):
    cart_id = serializers.IntegerField()
    order_tracking_stage_number = serializers.IntegerField()
    order_tracking_stage_label = serializers.CharField()

class CartOrderDeleteSrlzr(serializers.Serializer):
    id = serializers.IntegerField()

class UsedCouponGetSrlzr(serializers.ModelSerializer):
    class Meta:
        model = CouponUsed
        fields = ('id', 'coupon', 'uses_used')

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['coupon'] = CouponGetSrlzr(instance.coupon).data
        return rep