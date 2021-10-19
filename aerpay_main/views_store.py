from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions
from aerpay_main.models import Category, Coupon, FMCGProduct, FMCGTransaction, Product, QuantityType, Store, SubscriptionPrice
from aerpay_main.store_serializers import CategoryCreateSrlzr, CategoryDeleteSrlzr, CategoryGetSrlzr, CategoryMdlSrlzr, CategoryUpdateSrlzr, CouponDeleteSrlzr, CouponGetSrlzr, CouponGnrtSrlzr, FMCGStrProductGetSrlzr, FMCGTrnsctnCreateSrlzr, FMCGTrnsctnGetSrlzr, ProductCreateSrlzr, ProductDeleteSrlzr, ProductGetSrlzr, ProductUpdateSrlzr, QuantityTypesGetSrlzr, RefillProductSrlzr, StoreGetSrlzr, StoreListSrlzr, StoreRegisterSrlzr, StoreUpdateSrlzr, StoreUsrGetSrlzr, SubscriptionPriceGetSrlzr
from view_functions import createPostWithImage, putWithImage

from django.utils.crypto import get_random_string

class SubscriptionPriceGetView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        subscription_price = SubscriptionPrice.objects.first()
        if subscription_price != None:
            mySerialized = SubscriptionPriceGetSrlzr(
                subscription_price)
            myResponse = Response(
                {'message': 'success', 'data': mySerialized.data})
            return myResponse
        else:
            return Response(
                {'message': 'no price quoted yet'})

class QuantityTypesView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        myQuanTypes = QuantityType.objects.all()
        if list(myQuanTypes):
            mySerialized = QuantityTypesGetSrlzr(
                myQuanTypes, many = True)
            myResponse = Response(
                {'message': 'success', 'data': mySerialized.data})
            return myResponse
        else:
            return Response(
                {'message': 'no quantity types available'})

class RegisterStoreView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = StoreRegisterSrlzr

    def post(self, request, *args, **kwargs):
        myUser = request.user
        myObject = Store()
        mySerialized = StoreGetSrlzr(myObject, data=request.data)
        mySerialized.is_valid(raise_exception=True)
        copy = createPostWithImage(mySerialized, myObject, 'store')
        myObject.owner = myUser
        myObject.default_subscription_price = SubscriptionPrice.objects.first().new_price
        myObject.subscription_renewal_price = myObject.default_subscription_price
        myObject.last_paid_subscription_date = date.today()
        myObject.subscription_renewal_date = date.today() + relativedelta(months=1)
        myObject.save()
        myString = ''
        if myObject.refered_by_store_referal_code != None:
            myStores = Store.objects.all()
            stores = list(myStores)
            if stores:
                if myStores.filter(own_referal_code = myObject.refered_by_store_referal_code).exists():
                    # you need to check what its date is and what the store's expiry date is in this case
                    # actually no, this way, more people can come onto the app
                    myStore = myStores.filter(own_referal_code = myObject.refered_by_store_referal_code).first()
                    myStore.subscription_renewal_price = float(myStore.subscription_renewal_price) * 0.85
                    myStore.save()
                else:
                    myString = 'No store exists with the referal code you entered'
            else:
                myString = 'No stores exist yet that may have refered you'
        copy['owner'] = myUser.name
        copy['default_subscription_price'] = myObject.default_subscription_price
        copy['subscription_renewal_price'] = myObject.subscription_renewal_price
        copy['last_paid_subscription_date'] = myObject.last_paid_subscription_date
        copy['subscription_renewal_date'] = myObject.subscription_renewal_date
        if myString == '':
            return Response({'message': 'success', 'data': copy})
        else:
            return Response({'message': myString, 'data': copy})

class StoreUpdateView(APIView):

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = StoreUpdateSrlzr

    def post(self, request, *args, **kwargs):
        myUser = request.user
        if hasattr(myUser, 'store') and myUser.store != None:
            myObject = myUser.store

            mySerialized = StoreGetSrlzr(myObject, data=request.data)
            mySerialized.is_valid(raise_exception=True)

            putData = putWithImage(mySerialized, myObject, 'store')
            
            return Response({'message': 'success', 'data': putData})
        else:
            return Response({'message': 'You have no registered store'})

class StoreRefCodeGenView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        myUser = request.user
        if hasattr(myUser, 'store') and myUser.store != None:
            myStore = myUser.store
            unique_code = get_random_string(length=7)
            own_ref_code = str(myStore.id) + str(myStore.name) + unique_code
            myStore.own_referal_code = own_ref_code
            myStore.save()
            mySerialized = StoreGetSrlzr(
            myStore)
            myResponse = Response(
                {'message': 'success', 'data': mySerialized.data})
            return myResponse
        else:
            return Response({'message': 'You have no registered store'})

class StoreStrDetailsView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        myUser = request.user
        if hasattr(myUser, 'store') and myUser.store != None:
            myStore = myUser.store
            mySerialized = StoreGetSrlzr(
            myStore)
            myResponse = Response(
                {'message': 'success', 'data': mySerialized.data})
            return myResponse
        else:
            return Response({'message': 'You have no registered store'})

class StoreUsrDetailsView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        myStore = Store.objects.filter(id=kwargs['store_id']).first()
        if myStore == None:
            return Response({'message': 'Store is null, you entered the wrong id in the url'})
        mySerialized = StoreUsrGetSrlzr(
            myStore)
        myResponse = Response(
            {'message': 'success', 'data': mySerialized.data})
        return myResponse

# this is how the search filter is going to work here:
# get all products in which the search string entered is contined in
# either the product name,
# or the category_name of the product,
# or the store name of the category
# in any case, store the id of the store of all three cases into a list
# then make another database query to get all the stores that have ids in that list
# get all products of that store that have that string or whose category is in that string (done in context)
# then get the top 5 of hose products to show in the stores list

class StoresListView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        ######## pagenation area #############
        myStores = Store.objects.all()
        if list(myStores):
            mySerialized = StoreListSrlzr(
                myStores, many = True)
            myResponse = Response(
                {'message': 'success', 'data': mySerialized.data})
            return myResponse
        else:
            return Response(
                {'message': 'no stores available'})

class StoreDeleteView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def post(self, request, *args, **kwargs):
        myUser = request.user
        if hasattr(myUser, 'store') and myUser.store != None:
            myStore = myUser.store
            myStore.delete()
            return Response(
                {'message': 'Store deleted!'})
        else:
            return Response(
                {'message': 'no store to delete'})


class CategoryCreateView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = CategoryCreateSrlzr

    def post(self, request, *args, **kwargs):
        myUser = request.user
        if hasattr(myUser, 'store') and myUser.store != None:
            myStore = myUser.store
            myObject = Category()
            mySerialized = CategoryMdlSrlzr(myObject, data=request.data)
            mySerialized.is_valid(raise_exception=True)
            copy = createPostWithImage(mySerialized, myObject, 'category')
            myObject.store = myStore
            myObject.save()
            copy['store'] = myStore.name
            return Response({'message': 'success', 'data': copy})
        else:
            return Response({'message': 'Store doent exist'})

class CategoryUpdateView(APIView):

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = CategoryUpdateSrlzr

    def post(self, request, *args, **kwargs):
        myUser = request.user
        myId=kwargs['categ_id']
        myCategory = Category.objects.filter(id=myId).first()
        if myCategory == None:
            return Response({'message': 'Category is null, you entered the wrong id in the url'})
        store = myCategory.store
        owner = store.owner
        if owner.id != myUser.id:
            return Response({'message': 'This category does not belong to your store'})
        else:
            myCategory = myCategory
            mySerialized = CategoryMdlSrlzr(myCategory, data=request.data)
            mySerialized.is_valid(raise_exception=True)
            putData = putWithImage(mySerialized, myCategory, 'category')             
            return Response({'message': 'success', 'data': putData})

class CategoriesOnStorePageDetailsView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        myStore = Store.objects.filter(id=kwargs['store_id']).first()
        if myStore == None:
            return Response({'message': 'Store is null, you entered the wrong id in the url'})
        myCategories = myStore.categories.all()
        mySerialized = CategoryGetSrlzr(
            myCategories, many = True)
        myResponse = Response(
            {'message': 'success', 'data': mySerialized.data})
        return myResponse

class SingleCategoryOnStorePageDetailsView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        myCategory = Category.objects.filter(id=kwargs['categ_id']).first()
        mySerialized = CategoryGetSrlzr(
            myCategory)
        myResponse = Response(
            {'message': 'success', 'data': mySerialized.data})
        return myResponse

class CategoriesProductPageDetailsView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        myUser = request.user
        if hasattr(myUser, 'store') and myUser.store != None:
            myStore = myUser.store
            myCategories = myStore.categories.all()
            mySerialized = CategoryMdlSrlzr(
                myCategories, many = True)
            myResponse = Response(
                {'message': 'success', 'data': mySerialized.data})
            return myResponse
        else:
            Response(
                {'message': 'You have no store to hold any categories'})

class CategoryDeleteView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = CategoryDeleteSrlzr

    def post(self, request, *args, **kwargs):
        myUser = request.user
        categ_id = request.data['id']
        if categ_id == None:
            return Response({'message': 'Category is null, you entered the wrong id'})
        myCategory = Category.objects.filter(id=categ_id).first()
        if myCategory == None:
            return Response({'message': 'Category is null, you entered the wrong id'})
        store = myCategory.store
        owner = store.owner
        if owner.id != myUser.id:
            return Response({'message': 'This category does not belong to your store'})
        else:
            myCategory = myCategory
            myCategory.delete()           
            return Response({'message': 'Category has been deleted!'})

class FMCGProductsListView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        ######## pagenation area #############
        myFmcgs = FMCGProduct.objects.all()
        if list(myFmcgs):
            mySerialized = FMCGStrProductGetSrlzr(
                myFmcgs, many = True)
            myResponse = Response(
                {'message': 'success', 'data': mySerialized.data})
            return myResponse
        else:
            return Response(
                {'message': 'no FMCG products available'})

class FMCGProductGetView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        ######## pagenation area #############
        myFmcg = FMCGProduct.objects.filter(id=kwargs['fmcg_id']).first()
        if myFmcg != None:
            mySerialized = FMCGStrProductGetSrlzr(
                myFmcg)
            myResponse = Response(
                {'message': 'success', 'data': mySerialized.data})
            return myResponse
        else:
            return Response(
                {'message': 'this FMCG product doesnt exist'})

# lets first get the product model dealt with before moving on to transactions
class ProductCreateView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = ProductCreateSrlzr

    def post(self, request, *args, **kwargs):
        myUser = request.user
        categ_id=request.data['category']
        if categ_id == None:
            return Response({'message': 'You cannot create a product without a category'})
        if hasattr(myUser, 'store') and myUser.store != None:
            myStore = myUser.store
            if hasattr(myStore, 'categories') and list(myStore.categories.all()):
                myCategories = myStore.categories.all()
                if myCategories.filter(id=categ_id).exists():
                    myObject = Product()
                    mySerialized = ProductGetSrlzr(myObject, data=request.data)
                    mySerialized.is_valid(raise_exception=True)
                    copy = createPostWithImage(mySerialized, myObject, 'product')
                    copy['is_out_of_stock'] = myObject.is_out_of_stock
                    return Response({'message': 'success', 'data': copy})
                else:
                    return Response({'message': 'You cannot assign a product to a category that does not belong to you'})
            else:
                return Response({'message': 'You have no categories to assign products to'})
        else:
            return Response({'message': 'You have no store to assign products to'})
                
class ProductUpdateView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = ProductUpdateSrlzr

    def post(self, request, *args, **kwargs):
        myUser = request.user
        myProduct = Product.objects.filter(id=kwargs['product_id']).first()
        if myProduct == None:
            return Response({'message': 'Product is null, you entered the wrong id in the url'})
        category = myProduct.category
        store = category.store
        owner = store.owner
        if owner.id != myUser.id:
            return Response({'message': 'This product does not belong to your store'})
        else:
            myObject = myProduct
            mySerialized = ProductGetSrlzr(myObject, data=request.data)
            mySerialized.is_valid(raise_exception=True)
            copy = putWithImage(mySerialized, myObject, 'product')
            return Response({'message': 'success', 'data': copy})

class RefillQuantityInStockView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = RefillProductSrlzr
    
    def post(self, request, *args, **kwargs):
        myUser = request.user
        myProduct = Product.objects.filter(id=kwargs['product_id']).first()
        if myProduct == None:
            return Response({'message': 'Product is null, you entered the wrong id in the url'})
        category = myProduct.category
        store = category.store
        owner = store.owner
        if owner.id != myUser.id:
            return Response({'message': 'This product does not belong to your store'})
        else:
            new_quantity_in_stock = request.data['new_quantity_in_stock']
            myProduct.initial_quantity = new_quantity_in_stock
            myProduct.quantity_in_stock = new_quantity_in_stock
            myProduct.save()
            mySerialized = ProductGetSrlzr(myProduct)
            return Response({'message': 'success', 'data': mySerialized.data})

class ProductGetDetailsView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        myProduct = Product.objects.filter(id=kwargs['product_id']).first()
        if myProduct == None:
            return Response({'message': 'Product is null, you entered the wrong id in the url'})
        mySerialized = ProductGetSrlzr(
            myProduct)
        myResponse = Response(
            {'message': 'success', 'data': mySerialized.data})
        return myResponse

class ProductDeleteView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = ProductDeleteSrlzr

    def post(self, request, *args, **kwargs):
        myUser = request.user
        product_id = request.data['id']
        if product_id == None:
            return Response({'message': 'Product is null, you entered the wrong id'})
        myProduct = Product.objects.filter(id=product_id).first()
        if myProduct == None:
            return Response({'message': 'Product is null, you entered the wrong id'})
        category = myProduct.category
        store = category.store
        owner = store.owner
        if owner.id != myUser.id:
            return Response({'message': 'This product does not belong to your store'})
        else:
            if hasattr(myProduct, 'orders') and list(myProduct.orders.all()):
                prodOrders = myProduct.orders.all()
                myProdOrders = list(prodOrders)
                for myProdOrder in myProdOrders:
                    myProdOrder.product = None
                    myProdOrder.save()
            myProduct.delete()           
            return Response({'message': 'Product has been deleted!'})



# no, make a get call to check the status jus before the fmcg transact
# for the buyer transact, the payment is made later in any case, so doesnt matter

class FMCGTrnsctnCreateView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = FMCGTrnsctnCreateSrlzr

    def post(self, request, *args, **kwargs):
        myUser = request.user
        if hasattr(myUser, 'store') and myUser.store != None:
            myStore = myUser.store
            myObject = FMCGTransaction()
            mySerialized = FMCGTrnsctnGetSrlzr(myObject, data=request.data)
            mySerialized.is_valid(raise_exception=True)
            mySerialized.save()
            myObject.store = myStore
            myObject.save()
            myFmcgProduct = myObject.fmcg_product
            myFmcgProduct.quantity_in_stock = myFmcgProduct.quantity_in_stock - myObject.quantity_taken_from_fmcg
            myFmcgProduct.save()
            return Response({'message': 'success', 'data': mySerialized.data})
        else:
            return Response({'message': 'You have no store to register a transaction to',})


# you can send the notification que from the model instance of the 
# property function of the model

class FMCGTrnsctnsListView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        ######## pagenation area #############
        myUser = request.user
        if hasattr(myUser, 'store') and myUser.store != None:
            myStore = myUser.store
            if hasattr(myStore, 'fmcg_purchases') and list(myStore.fmcg_purchases.all()):
                myFmcgPurchases = myStore.fmcg_purchases.all()
                mySerialized = FMCGTrnsctnGetSrlzr(
                    myFmcgPurchases, many = True)
                myResponse = Response(
                    {'message': 'success', 'data': mySerialized.data})
                return myResponse
            else:
                return Response(
                    {'message': 'No previous fmcg transactions exist',})
        else:
            return Response(
                    {'message': 'You dont have a store to hold any fmcg transactions',})

class CouponGenView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = CouponGnrtSrlzr

    def post(self, request, *args, **kwargs):
        myUser = request.user
        if hasattr(myUser, 'store') and myUser.store != None:
            myStore = myUser.store
        else:
            return Response({'message': 'You have no registered store'})

        categ_id=request.data['category']
        product_id = request.data['product']
        if categ_id != None and product_id != None:
            return Response({'message': "The coupon cannot be generated for both a category and a product at the same time. Choose one or the other, or leave both blank to assign the coupon for the whole store's bill"})
        elif categ_id != None:
            myCategory = Category.objects.filter(id = categ_id).first()
            categ_store = myCategory.store
            if categ_store.id != myStore.id:
                return Response({'message': 'The category you entered does not belong to your store'})
        elif product_id != None:
            myProduct = Product.objects.filter(id = product_id).first()
            prod_categ = myProduct.category
            prod_store = prod_categ.store
            if prod_store.id != myStore.id:
                return Response({'message': 'The product you entered does not belong to your store'})

        myObject = Coupon()
        mySerialized = CouponGetSrlzr(myObject, data=request.data)
        mySerialized.is_valid(raise_exception=True)
        mySerialized.save()
        copy = mySerialized.data
        unique_code = get_random_string(length=8)
        coupon_code = str(myObject.id) + unique_code + myStore.name
        myObject.code = coupon_code
        myObject.owner = myUser
        copy['code'] = myObject.code
        if categ_id == None and product_id == None:
            myObject.store = myStore
        myObject.save()
        return Response({'message': 'success', 'data': copy})

class CouponsGetView(APIView):

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        myUser = request.user
        if hasattr(myUser, 'coupons') and list(myUser.coupons.all()):
            myCoupons = myUser.coupons.all()
            mySerialized = CouponGetSrlzr(
                myCoupons, many = True)
            myResponse = Response(
                {'message': 'success', 'data': mySerialized.data})
            return myResponse
        else:
            return Response({'message': 'Either your store does not have any coupons yet or you donot have a store'})

class CouponDeleteView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = CouponDeleteSrlzr

    def post(self, request, *args, **kwargs):
        myUser = request.user
        coupon_id = request.data['id']
        if coupon_id == None:
            return Response({'message': 'Coupon is null, you entered the wrong id'})
        myCoupon = Coupon.objects.filter(id=coupon_id).first()
        if myCoupon == None:
            return Response({'message': 'Coupon is null, you entered the wrong id'})
        owner = myCoupon.owner
        if owner.id != myUser.id:
            return Response({'message': 'This coupon does not belong to your store'})
        else:
            myCoupon.delete()           
            return Response({'message': 'Coupon has been deleted!'})