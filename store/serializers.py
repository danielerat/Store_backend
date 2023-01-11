from decimal import Decimal
from store.models import Product, Collection, Review, Cart, CartItem, Customer, Order, OrderItem
from rest_framework import serializers
from django.db import transaction
from .signals import order_created


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection  
        fields = ['id', 'title', 'products_count']

    products_count = serializers.IntegerField(read_only=True)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug', 'inventory', 'unit_price', 'price_with_tax', 'collection']

    price_with_tax = serializers.SerializerMethodField(
        method_name='calculate_tax')

    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'date', 'name', 'description']

        # overide the save or create method in the serializer object
        def create(self, validated_data):
            product_id = self.context['product_id']
            return Review.objects.create(product_id=product_id, **validated_data)


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price']


# Cart Serializer

class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart_item: CartItem):
        return cart_item.product.unit_price * cart_item.quantity

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']


# Creating the Cart Serializer class
class CartSerializer(serializers.ModelSerializer):
    # Set the id of the serializer to readOnly so that we won't supply it to be able
    # to create a freaking cart
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    # In this method we are going to try to raise an error in case we get an issue with,
    # The product_id, the validate_field_name(self,value) method, allow us to bring our custom validations
    def validate_product_id(self, value):
        # If we do not have the product in our database, value is the pk of the product
        if not Product.objects.filter(pk=value).exists():
            # We raise an arror saying that yes there is really an issue the product does not exist
            raise serializers.ValidationError("No Product with The given id Found.")
        # We return the value of id of the product if it exists
        return value

    # overiding the save method of our class to make sure what is saved is what we want to be saved, in our case
    # if a product exists then we simply update it's quantity otherwise , we are going to create it
    def save(self, **kwargs):
        # Since the cart Id is in the url, in our view we have to send the context of the url back to our view
        # So that we can save it as a variable and actually work with is.
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        try:
            # If we get a cart, then we are updating it's item,
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
        return self.instance
        # If we reach here, means there is no such product in the cart, thus, we have to create it

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'phone', 'birth_date', 'membership']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'unit_price']


class OrderSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'placed_at', 'payment_status', 'items']


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        # check if the cart is valid, aka exists
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError('No cart with the given id returned')
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('The Cart is empty')
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            user = self.context['user_id']
            cart_id = self.validated_data['cart_id']
            customer = Customer.objects.get(user_id=user)

            # creating the order using the customer object
            order = Order.objects.create(customer=customer)

            # creating the order items using items in from the cart
            cart_items = CartItem.objects.select_related('product').filter(cart_id=cart_id)
            # List comprehension to get all cart items
            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=item.product.unit_price
                ) for item in cart_items
            ]

            # Create all order Items
            OrderItem.objects.bulk_create(order_items)
            # Deleting the cart
            Cart.objects.filter(pk=cart_id).delete()

            order_created.send_robus(self.__class__, order=order)
            return order
