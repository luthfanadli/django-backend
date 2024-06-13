from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from django.contrib.auth.models import User
from django.db.models import Q
from argon2 import PasswordHasher
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

from BusinessCase.models import User,Product,Order,OrderHistory
from BusinessCase.serializers import UserSerializer,ProductSerializer,OrderSerializer,OrderHistorySerializer 

# Create your views here.

@api_view(['GET', 'POST', 'DELETE'])
@csrf_exempt
def product(request, id=0):
    if request.method == 'GET':
        if id != 0:
            try:
                product = Product.objects.get(product_id=id)
                product_serializer = ProductSerializer(product)
                return JsonResponse(product_serializer.data, safe=False)
            except Product.DoesNotExist:
                return JsonResponse("Product not found", safe=False)
        else:
            products = Product.objects.all()

            # Filtering
            min_price = request.GET.get('min_price')
            max_price = request.GET.get('max_price')
            if min_price and max_price:
                products = products.filter(price__range=(min_price, max_price))
            elif min_price:
                products = products.filter(price__gte=min_price)
            elif max_price:
                products = products.filter(price__lte=max_price)

            # Sorting
            sort_by = request.GET.get('sort')
            if sort_by == 'price_asc':
                products = products.order_by('price')
            elif sort_by == 'price_desc':
                products = products.order_by('-price')

            # Search
            search_query = request.GET.get('search')
            if search_query:
                products = products.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))

            product_serializer = ProductSerializer(products, many=True)
            return JsonResponse(product_serializer.data, safe=False)
        
    elif request.method=='POST':
        product_data=JSONParser().parse(request)
        product_serializer=ProductSerializer(data=product_data)
        if product_serializer.is_valid():
            product_serializer.save()
            return JsonResponse("Added Successfully", safe=False)
        return JsonResponse("Failed to Add", safe=False)

    elif request.method=='DELETE':
        try:
            product = Product.objects.get(product_id=id)
            product.delete()
            return JsonResponse("Deleted Successfully", safe=False)
        except Product.DoesNotExist:
            return JsonResponse("Product not found", safe=False)


@api_view(['POST'])
@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        name = data.get('name')
        email = data.get('email')
        raw_password = data.get('password')

        if not (name and email and raw_password):
            return JsonResponse({'error': 'name, email, and password are required.'}, status=400)

        # Hash password using argon2
        ph = PasswordHasher()
        hashed_password = ph.hash(raw_password)

        try:
            user = User.objects.create(name=name, email=email, password=hashed_password)
            user.save()
            return JsonResponse({'success': 'User registered successfully.'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed.'}, status=405)


@api_view(['POST'])
def login_user(request: Request):
    if request.method == 'POST':
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not (email and password):
            return Response({'error': 'Email and password are required.'}, status=400)

        user = User.objects.filter(email=email).first()

        if user is not None:
            ph = PasswordHasher()
            if ph.verify(user.password, password):
                refresh = RefreshToken.for_user(user)
                return Response({
                    'access_token': str(refresh.access_token),
                    'user_id': user.user_id,
                    'name': user.name,
                    'email': user.email,
                    'home_latitude': user.home_latitude,
                    'home_longitude': user.home_longitude,
                })
        
        return Response({'error': 'Invalid credentials.'}, status=401)
    else:
        return Response({'error': 'Method not allowed.'}, status=405)


@api_view(['DELETE'])
@csrf_exempt
def delete_user(request, id):
    if request.method == 'DELETE':
        try:
            user = User.objects.get(id=id)
            user.delete()
            return JsonResponse({'success': 'User deleted successfully.'}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found.'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed.'}, status=405)


@api_view(['GET'])
@csrf_exempt
def view_all_users(request):
    if request.method == 'GET':
        users = User.objects.all()
        user_serializer = UserSerializer(users, many=True)
        return JsonResponse(user_serializer.data, safe=False)
    else:
        return JsonResponse({'error': 'Method not allowed.'}, status=405)


@api_view(['POST'])
def create_order(request):
    if request.method == 'POST':
        user_id = request.data.get('user_id')
        product_id = request.data.get('product_id')

        try:
            user = User.objects.get(user_id=user_id)
            product = Product.objects.get(product_id=product_id)
        except (User.DoesNotExist, Product.DoesNotExist):
            return JsonResponse({'error': 'User or Product not found'}, status=404)

        # Check if the user has already ordered this product
        if Order.objects.filter(user=user, product=product).exists():
            return JsonResponse({'error': 'You have already ordered this product'}, status=400)

        order = Order(user=user, product=product)
        order.save()
        
        # Save to OrderHistory
        order_history = OrderHistory(order=order)
        order_history.save()

        order_serializer = OrderSerializer(order)
        return JsonResponse(order_serializer.data, status=201)


@api_view(['GET'])
def get_order_history(request, user_id):
    try:
        order_history = OrderHistory.objects.filter(order__user__user_id=user_id)
    except OrderHistory.DoesNotExist:
        return Response({'error': 'No order history found for this user'}, status=404)

    order_history_serializer = OrderHistorySerializer(order_history, many=True)
    return Response(order_history_serializer.data)


@api_view(['POST'])
@csrf_exempt
def register_user_location(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        user_id = data.get('user_id')  
        home_longitude = data.get('home_longitude')
        home_latitude = data.get('home_latitude')

        if not (user_id and home_longitude and home_latitude):
            return JsonResponse({'error': 'User ID, longitude, and latitude are required.'}, status=400)

        try:
            user = User.objects.get(user_id=user_id)
            user.home_longitude = home_longitude
            user.home_latitude = home_latitude
            user.save()
            return JsonResponse({'success': 'User location registered successfully.'}, status=201)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed.'}, status=405)