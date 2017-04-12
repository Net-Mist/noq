from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template.context_processors import csrf
from .forms import UpdateProfile
from .models import Shop
from .admin import UserCreationForm


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


def profile(request):
    if not request.user.is_authenticated:
        return redirect('home')
    else:
        context = dict()
        if request.method == 'POST':
            form = UpdateProfile(request.POST, instance=request.user)
            if form.is_valid():
                print('Form is valid')
                form.save()
                return redirect('success')
            else:
                print('Form is not valid')
                return redirect('home')
        else:
            context['form'] = UpdateProfile(instance=request.user)
        return render(request, 'main/update.html', context)


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
