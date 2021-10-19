from datetime import date, datetime, timedelta
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions

from aerpay_main.customer_serializers import CartOrderAcceptSrlzr, CartOrderCstmrGetSrlzr, CartOrderCstmrListSrlzr, CartOrderStrGetSrlzr, CartOrderStrListSrlzr, CartSelectPaymentAndSaveOrderSrlzr, CartUpdateOrderStageSrlzr, OrderCreateSrlzr, OrderStagesGetSrlzr, UsedCouponGetSrlzr
from aerpay_main.models import CartOrder, Coupon, CouponUsed, OrderTrackingStage, Product, ProductOrder, Store

# all of this should be combined into one view and that is 
# one order view
# add the checks for changing inventory here aswell, during payment
# save the model if the payment method has been selected and before the 
# online payment is made

# make a coupon set api that will 

class OrderTrackingStagesListView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        myStages = OrderTrackingStage.objects.all()  
        mySerialized = OrderStagesGetSrlzr(
            myStages, many = True)
        myResponse = Response(
            {'message': 'success', 'data': mySerialized.data})
        return myResponse

class OrderCreateView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = OrderCreateSrlzr

    def post(self, request, *args, **kwargs):
        myUser = request.user
        product_ids_and_quantities = request.data['products']
        store_id = request.data['store_id']
        if Store.objects.filter(id = store_id).exists():
            myStore = Store.objects.filter(id = store_id).first()
        else:
            return Response({'message': 'You have not provided a store id'})
        product_ids = []
        if product_ids_and_quantities:
            for product_id_and_quantity in product_ids_and_quantities:
                product_ids.append(product_id_and_quantity['id'])
        else:
            return Response({'message': 'You have not chosen any product'})
        products = Product.objects.filter(pk__in=product_ids)
        myProducts = list(products)
        for index in range(len(myProducts)):
            myProduct = myProducts[index]
            my_product_id_and_quantity = product_ids_and_quantities[index]
            if my_product_id_and_quantity['id'] == myProduct.id:
                if my_product_id_and_quantity['quantity'] > myProduct.quantity_in_stock:
                    return Response({'message': 'During the process of your order, the quantity of product: ' + myProduct.name + ' dropped below the quantity you demanded, please refresh and demand a different quantity'})
        # im assuming that it acnnot demand a product from a different store, so yeah

        if request.data['customer_name'] == None or request.data['customer_name'] == '':
            customerName = myUser.name
        else:
            customerName = request.data['customer_name']
        if request.data['customer_address'] == None or request.data['customer_address'] == '':
            customerAddress = myUser.address
        else:
            customerAddress = request.data['customer_address']
        if request.data['customer_address_latitude'] == None or request.data['customer_address_latitude'] == '':
            customerAddressLatitude = myUser.address_latitude
        else:
            customerAddressLatitude = request.data['customer_address_latitude']
        if request.data['customer_address_longitude'] == None or request.data['customer_address_longitude'] == '':
            customerAddressLongitude = myUser.address_longitude
        else:
            customerAddressLongitude = request.data['customer_address_longitude']
        if request.data['customer_phone_number'] == None or request.data['customer_phone_number'] == '':
            customerPhoneNumber = myUser.phone_number
        else:
            customerPhoneNumber = request.data['customer_phone_number']

        myCart = CartOrder.objects.create(
            customer = myUser,
            store = myStore,
            coupon_code = request.data['coupon_code'],
            customer_name = customerName,
            customer_address = customerAddress,
            customer_address_latitude = customerAddressLatitude,
            customer_address_longitude = customerAddressLongitude,
            customer_phone_number = customerPhoneNumber,
        )
# the coupon u entered belonged to no product nor category in the cart and there
# fore was not used
        myCoupon = None
        myMessage = 'success'
        if myCart.coupon_code != None:
            myMessage = 'Coupon activated'
            myCoupon = Coupon.objects.filter(code = myCart.coupon_code).first()
            if myCoupon == None:
                myMessage = 'The coupon you entered does not belong to any store, the order was placed successfully'

        for index in range(len(myProducts)):
            myProduct = myProducts[index]
            my_product_id_and_quantity = product_ids_and_quantities[index]    
            if my_product_id_and_quantity['id'] == myProduct.id:
                myProduct.quantity_in_stock = myProduct.quantity_in_stock - my_product_id_and_quantity['quantity']
                myProduct.number_of_orders_for_this_product_uptill_now = myProduct.number_of_orders_for_this_product_uptill_now + 1
                myProduct.save()
                myProductOrder = ProductOrder.objects.create(
                    cart = myCart,
                    product = myProduct,
                    product_name = myProduct.name,
                    product_image = myProduct.image,
                    priced_at = myProduct.price,
                    discounted_priced_at = myProduct.discounted_price,
                    quantity_demanded = my_product_id_and_quantity['quantity'],
                    total_price = float(my_product_id_and_quantity['quantity']) * float(myProduct.discounted_price)
                )
                myCart.total_price = float(myCart.total_price) + float(myProductOrder.total_price)
        myCart.discounted_total_price = myCart.total_price
        myCart.save()
        if myCoupon != None:
            orderedProducts = myCart.products.all()
            usedCoupon = None
            is_limit_reached = False
            if hasattr(myUser, 'coupons_in_use') and list(myUser.coupons_in_use.all()):
                usedCoupons = myUser.coupons_in_use.all()
                if usedCoupons != None:
                    if usedCoupons.filter(coupon__id = myCoupon.id).exists():
                        usedCoupon = usedCoupons.filter(coupon__id = myCoupon.id).first()
                        if usedCoupon.uses_used >= myCoupon.uses_per_customer:
                            myMessage = 'Coupon use limit has been reached and therefore was not used, the order was placed successfully'
                            is_limit_reached = True
                            myCart.coupon_code = None
                            myCart.save()
            if myCoupon.store != None and myCoupon.store.id == myStore.id and not is_limit_reached:
                if myCart.total_price >= myCoupon.minimum_order_Rs:
                    if myCoupon.discount_type == 'Flat':
                        myCart.discounted_total_price = float(myCart.total_price) - float(myCoupon.discount_amount)
                    elif myCoupon.discount_type == 'Percentage':
                        myCart.discounted_total_price = float(myCart.total_price) * (1.00 - float(myCoupon.discount_amount) * 0.01)
                    myCart.save()
                    myMessage = 'Coupon used on whole store bill, the order was placed successfully'
                    if usedCoupon != None:
                        usedCoupon.uses_used = usedCoupon.uses_used + 1
                        usedCoupon.save()
                    else:
                        CouponUsed.objects.create(
                            coupon = myCoupon,
                            user = myUser,
                            uses_used = 1,
                        )
                else:
                    myMessage = 'You do not fulfill the minimum order requirement of this coupon, the order was placed successfully'
            elif myCoupon.store != None and myCoupon.store.id != myStore.id:
                myMessage = 'Coupon does not belong to this store, the order was placed successfully'
            elif myCoupon.category != None:
                categ_product_orders = orderedProducts.filter(product__category__id = myCoupon.category.id)
                my_categ_product_orders = list(categ_product_orders)
                print(is_limit_reached)
                print(my_categ_product_orders)
                print(myCoupon.owner)
                if my_categ_product_orders and not is_limit_reached:
                    past_price = 0.0
                    for my_categ_product_order in my_categ_product_orders:
                        past_price = past_price + float(my_categ_product_order.total_price)
                    if past_price >= myCoupon.minimum_order_Rs:
                        if myCoupon.discount_type == 'Flat':
                            myCart.discounted_total_price = float(myCart.total_price ) - float(myCoupon.discount_amount)
                        elif myCoupon.discount_type == 'Percentage':
                            myCart.discounted_total_price = (float(myCart.total_price) - past_price) + past_price * (1.00 - float(myCoupon.discount_amount) * 0.01)
                        myMessage = 'Coupon used on category, the order was placed successfully'
                        myCart.save()
                        if usedCoupon != None:
                            usedCoupon.uses_used = usedCoupon.uses_used + 1
                            usedCoupon.save()
                        else:
                            CouponUsed.objects.create(
                                coupon = myCoupon,
                                user = myUser,
                                uses_used = 1,
                            )
                    else:
                        myMessage = 'You do not fulfill the minimum order requirement of this coupon, the order was placed successfully'
                else:
                    myMessage = 'Either coupon limit has been reached or coupon code does not refer to any coupon of this store, the order was placed successfully'
            elif myCoupon.product != None:
                my_prod_product_order = orderedProducts.filter(product__id = myCoupon.product.id).first()
                if my_prod_product_order != None and not is_limit_reached:
                    if my_prod_product_order.total_price >= myCoupon.minimum_order_Rs:
                        if myCoupon.discount_type == 'Flat':
                            myCart.discounted_total_price = float(myCart.total_price) - float(myCoupon.discount_amount)
                        elif myCoupon.discount_type == 'Percentage':
                            myCart.discounted_total_price = (float(myCart.total_price) - float(my_prod_product_order.total_price)) + float(my_prod_product_order.total_price) * (1.00 - float(myCoupon.discount_amount) * 0.01)
                        myCart.save()
                        myMessage = 'Coupon used on product, the order was placed successfully'
                        if usedCoupon != None:
                            usedCoupon.uses_used = usedCoupon.uses_used + 1
                            usedCoupon.save()
                        else:
                            CouponUsed.objects.create(
                                coupon = myCoupon,
                                user = myUser,
                                uses_used = 1,
                            )
                    else:
                        myMessage = 'You do not fulfill the minimum order requirement of this coupon, the order was placed successfully'
                else:
                    myMessage = 'Either coupon limit has been reached or coupon code does not refer to any coupon of this store, the order was placed successfully'

        mySerialized = CartOrderCstmrGetSrlzr(myCart)
        myResponse = Response(
                {'message': myMessage, 'data': mySerialized.data})
        return myResponse

class OrderAcceptView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = CartOrderAcceptSrlzr

    def post(self, request, *args, **kwargs):
        myUser = request.user
        # print(myUser.id)
        if hasattr(myUser, 'store') and myUser.store != None:
            myStore = myUser.store
            cart_id = request.data['cart_id']
            myCart = myStore.orders.all().filter(id = cart_id).first()
            if myCart == None:
                return Response({'message': 'This is not your cart'})
            else:
                isAccepted = request.data['accepted']
                if not isAccepted:
                    # but before, return the inventory
                    if hasattr(myCart, 'products') and list(myCart.products.all()):
                        productOrders = myCart.products.all()
                        myProductOrders = list(productOrders)
                        for myProductOrder in myProductOrders:
                            if myProductOrder.product != None:
                                myProduct = myProductOrder.product
                                myProduct.quantity_in_stock = float(myProduct.quantity_in_stock) + float(myProductOrder.quantity_demanded)
                                myProduct.number_of_orders_for_this_product_uptill_now = myProduct.number_of_orders_for_this_product_uptill_now - 1
                                myProduct.save()
                    if myCart.coupon_code != None and len(myCart.coupon_code) > 5:
                        usedCoupon = CouponUsed.objects.filter(coupon__code = myCart.coupon_code).first()
                        if usedCoupon != None and usedCoupon.coupon.owner.id == myUser.id and usedCoupon.uses_used > 0:
                            usedCoupon.uses_used = usedCoupon.uses_used - 1
                            usedCoupon.save()
                    myCart.delete()
                    return Response({'message': 'Cart cancelled, inventory recovered'})
                else:
                    myCart.is_accepted = True
                    myCart.order_accepted_at = datetime.now()
                    myCart.save()
                    mySerialized = CartOrderStrGetSrlzr(myCart)
                    myResponse = Response(
                            {'message': 'success', 'data': mySerialized.data})
                    return myResponse
        else:
            return Response({'message': 'You have no store'})

class SelectPaymentAndSaveCartView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = CartSelectPaymentAndSaveOrderSrlzr

    def post(self, request, *args, **kwargs):
        myUser = request.user
        cart_id = request.data['cart_id']
        myCart = myUser.orders.all().filter(id = cart_id).first()
        if myCart.customer.id != myUser.id:
            return Response({'message': 'This order was not placed by you'})
        else:
            if request.data['is_save_cart'] != None:
                myCart.is_save_cart = request.data['is_save_cart']
            myCart.is_payment_method_selected = True
            myCart.payment_method = request.data['payment_method']
            myCart.payment_method_selected_at = datetime.now()
            first_stage = OrderTrackingStage.objects.filter(order_tracking_stage_number = 1).first()
            if first_stage != None:
                myCart.order_tracking_stage_number = 1
                myCart.order_tracking_stage_label = first_stage.order_tracking_stage_label
            myCart.save()
            mySerialized = CartOrderCstmrGetSrlzr(myCart)
            myResponse = Response(
                    {'message': 'success', 'data': mySerialized.data})
            return myResponse

class UpdateOrderTrackingStageView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = CartUpdateOrderStageSrlzr

    def post(self, request, *args, **kwargs):
        myUser = request.user
        if hasattr(myUser, 'store') and myUser.store != None:
            myStore = myUser.store
            print(myStore)
            cart_id = request.data['cart_id']
            myCart = myStore.orders.all().filter(id = cart_id).first()
            if myCart != None:
                if myCart.store.id != myStore.id:
                    return Response({'message': 'This order was not placed for you'})
                else:
                    myCart.order_tracking_stage_number = request.data['order_tracking_stage_number']
                    myCart.order_tracking_stage_label = request.data['order_tracking_stage_label']
                    myCart.save()
                    mySerialized = CartOrderStrGetSrlzr(myCart)
                    myResponse = Response(
                            {'message': 'success', 'data': mySerialized.data})
                    return myResponse
            else:
                return Response({'message': 'This order was not placed for you'})
        else:
            return Response({'message': 'you have no store'})

class CartOrdersCstmrListView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        ######## pagenation area #############
        myUser = request.user
        myCartOrders = myUser.orders.all()
        if list(myCartOrders):
            mySerialized = CartOrderCstmrListSrlzr(
                myCartOrders, many = True)
            myResponse = Response(
                {'message': 'success', 'data': mySerialized.data})
            return myResponse
        else:
            return Response(
                {'message': 'no past orders'})

class CartOrdersCstmrGetView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        ######## pagenation area #############
        myUser = request.user
        myCartOrder = CartOrder.objects.filter(id=kwargs['cart_id']).first()
        if myCartOrder != None and myCartOrder.customer.id == myUser.id:
            mySerialized = CartOrderCstmrGetSrlzr(
                myCartOrder)
            myResponse = Response(
                {'message': 'success', 'data': mySerialized.data})
            return myResponse
        else:
            return Response(
                {'message': 'no order exists for you with this id'})

class SavedOrdersListView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        ######## pagenation area #############
        myUser = request.user
        mySavedOrders = myUser.orders.all().filter(is_save_cart = True)
        if list(mySavedOrders):
            mySerialized = CartOrderCstmrListSrlzr(
                mySavedOrders, many = True)
            myResponse = Response(
                {'message': 'success', 'data': mySerialized.data})
            return myResponse
        else:
            return Response(
                {'message': 'no past orders'})

class CartOrdersStrListView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        ######## pagenation area #############
        myUser = request.user
        if hasattr(myUser, 'store') and myUser.store != None:
            myStore = myUser.store
            myCartOrders = myStore.orders.all()
            if list(myCartOrders):
                mySerialized = CartOrderStrListSrlzr(
                    myCartOrders, many = True)
                myResponse = Response(
                    {'message': 'success', 'data': mySerialized.data})
                return myResponse
            else:
                return Response(
                    {'message': 'no past orders'})
        else:
            return Response({'message': 'You have no store'})

class CartOrdersStrGetView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        ######## pagenation area #############
        myUser = request.user
        if hasattr(myUser, 'store') and myUser.store != None:
            myStore = myUser.store
            myCartOrder = CartOrder.objects.filter(id=kwargs['cart_id']).first()
            if myCartOrder != None and myCartOrder.store.id == myStore.id:
                mySerialized = CartOrderStrGetSrlzr(
                    myCartOrder)
                myResponse = Response(
                    {'message': 'success', 'data': mySerialized.data})
                return myResponse
            else:
                return Response(
                    {'message': 'no order exists for you with this id'})
        else:
            return Response({'message': 'You have no store'})

class UsedCouponsListView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        ######## pagenation area #############
        myUser = request.user
        myUsedCoupons = myUser.coupons_in_use.all()
        if list(myUsedCoupons):
            mySerialized = UsedCouponGetSrlzr(
                myUsedCoupons, many = True)
            myResponse = Response(
                {'message': 'success', 'data': mySerialized.data})
            return myResponse
        else:
            return Response(
                {'message': 'no FMCG products available'})

