import datetime

from django.shortcuts import render, redirect,get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template.context_processors import csrf
from .forms import UpdateProfile
from .models import Shop,Customer,ShopOwner,Order

from .admin import UserCreationForm


def home(request):
    shops = Shop.objects.all()
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
