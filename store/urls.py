from django.urls import path

from . import views
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('products', views.ProductViewSet)
router.register('collections', views.CollectionViewSet)
router.register('carts', views.CartViewSet)
router.register('customers', views.CustomerViewSet)
router.register('orders', views.OrderViewSet, basename='orders')

products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('reviews', views.ReviewViewSet, basename='product-reviews')

carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', views.CartItemViewSet, basename='cart-items')

orders_router = routers.NestedDefaultRouter(router, 'orders', lookup='order')
orders_router.register('items', views.OrderViewSet, basename='order-items')

# URLConf
urlpatterns = router.urls + products_router.urls + carts_router.urls + orders_router.urls
