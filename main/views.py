import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template.context_processors import csrf

from .forms import UpdateProfile

from .models import Shop, Customer, ShopOwner, Order, FoodItem

from .admin import UserCreationForm, UserChangeForm

from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import User

# from django.contrib.gis.geoip2 import GeoIP2
from math import radians, cos, sin, asin, sqrt


def haversine(p1, p2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    lon1, lat1 = p1
    lon2, lat2 = p2
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    return km


def get_customer_position(request):
    return 1.294949, 103.773680


def order_shop(shops, customer_position):
    if len(shops) <= 1:
        return shops
    pivot = shops[0]
    distance_pivot = haversine(customer_position, (pivot.latitude, pivot.longitude))
    nearer_shop = [s for s in shops[1:] if
                   haversine(customer_position, (s.latitude, s.longitude)) <= distance_pivot]
    farer_shop = [s for s in shops[1:] if
                  haversine(customer_position, (s.latitude, s.longitude)) > distance_pivot]
    return order_shop(nearer_shop, customer_position) + [pivot] + order_shop(farer_shop, customer_position)


def select_nearest_shop(request, n=5):
    customer_position = get_customer_position(request)
    shops = Shop.objects.all()
    shops = order_shop(shops, customer_position)
    return shops[:n]


def home(request):
    shops = select_nearest_shop(request)
    distances = []
    customer_position = get_customer_position(request)
    for s in shops:
        distances.append(haversine(customer_position, (s.latitude, s.longitude)))

    shop_and_distances = zip(shops, distances)
    return render(request, 'main/home.html', {'shops': shops, 'distances': shop_and_distances})


def success(request):
    return render(request, 'main/success.html', dict())


def update(request):
    return render(request, 'main/update.html', dict())


def history(request):
    if not request.user.is_authenticated:
        return redirect('home')
    else:
        if not request.user.is_shop_owner:
            orders = Order.objects.filter(customer_id=request.user.id).order_by('-id')
            context = {}
            if not orders:
                context['ordersPresent'] = False
                context['orderMsg'] = "You don't have any Past Order"
            else:
                context['orders'] = orders
                context['ordersPresent'] = True
            return render(request, 'main/history.html', context)
        else:
            context = {}
            shops = Shop.objects.filter(shop_owner_id=request.user.shopowner.id)
            sid = -1
            for shop in shops:
                sid = shop.id
            if not sid == -1:
                current_order = Order.objects.filter(fooditem__shop=sid).order_by('-id')
                if current_order:
                    orders = current_order.all()
                    context['orders'] = orders
                    context['ordersPresent'] = True
                else:
                    context['ordersPresent'] = False
                    context['orderMsg'] = "No Customer has order from your shop till now"
            else:
                context['ordersPresent'] = False
                context['orderMsg'] = "You don't have any Shop"
            return render(request, 'main/shophistory.html', context)


def profile(request):
    if not request.user.is_authenticated:
        return redirect('home')
    else:
        context = {}
        context['user'] = request.user
        if not request.user.is_shop_owner:
            customer = get_object_or_404(Customer, user_id=request.user.id)
            context['balance'] = customer.balance
        else:
            owner = get_object_or_404(ShopOwner, user_id=request.user.id)
            context['balance'] = owner.credit
        return render(request, 'main/profile.html', context)


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success')

    context = {}
    context.update(csrf(request))
    context['form'] = UserCreationForm()

    return render(request, 'registration/register.html', context)
