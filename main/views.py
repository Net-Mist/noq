import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template.context_processors import csrf

from .forms import UpdateProfile

from .models import Shop, Customer, ShopOwner, Order

from .admin import UserCreationForm, UserChangeForm

from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import User


# from django.contrib.gis.geoip2 import GeoIP2

def get_customer_position(request):
    # g = GeoIP2()
    # ip = request.META.get('REMOTE_ADDR', None)
    # print(g.lat_lon(ip))
    # print(ip)
    return 1.294949, 103.773680


def compute_square_distance(p1, p2):
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2


def order_shop(shops, customer_position):
    if len(shops) <= 1:
        return shops
    pivot = shops[0]
    distance_pivot = compute_square_distance(customer_position, (pivot.latitude, pivot.longitude))
    nearer_shop = [s for s in shops[1:] if
                   compute_square_distance(customer_position, (s.latitude, s.longitude)) <= distance_pivot]
    farer_shop = [s for s in shops[1:] if
                  compute_square_distance(customer_position, (s.latitude, s.longitude)) > distance_pivot]
    return order_shop(nearer_shop, customer_position) + [pivot] + order_shop(farer_shop, customer_position)


def select_nearest_shop(request, n=5):
    """
    
    :param n: number of shop to get 
    :return: 
    """
    customer_position = get_customer_position(request)
    shops = Shop.objects.all()
    shops = order_shop(shops, customer_position)
    return shops[:n]


def home(request):
    shops = select_nearest_shop(request)
    return render(request, 'main/home.html', {'shops': shops})


def success(request):
    return render(request, 'main/success.html', dict())


def update(request):
    return render(request, 'main/update.html', dict())


def history(request):
    if not request.user.is_authenticated:
        return redirect('home')
    else:
        orders = Order.objects.select_related().filter(customer_id=1)
        context = {}
        if orders is None:
            context['order'] = ['No Order']
            context['orderMsg'] = "You don't have any Past Order"
        else:
            context['orders'] = orders
            context['orderMsg'] = "Order History"
            print(orders)
        return render(request, 'main/history.html', context)


def profile(request):
    if not request.user.is_authenticated:
        return redirect('home')
    else:
        context = {}
        print(request.user.firstName)
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
