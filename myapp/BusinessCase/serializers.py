from rest_framework import serializers
from BusinessCase.models import User,Product,Order,OrderHistory

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=('user_id', 'name', 'email', 'password', 'home_latitude', 'home_longitude' )

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields=('product_id','name','description','imageUrl','price')

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model=Order
        fields=('order_id', 'user', 'product', 'ordered_at')

class OrderHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model=OrderHistory
        fields=('order', 'ordered_at')