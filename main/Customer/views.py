from django.shortcuts import render

from django.contrib import messages

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from ..models import Shop, User, Customer, FoodItem


def fooditems(request, shop_id):
    shops = Shop.objects.all()
    current_shop = get_object_or_404(Shop, pk=shop_id)
    return render(request, 'main/fooditems.html', {'shop': current_shop})


def buy_fooditem(request, fooditem_id):
    if not request.user.is_authenticated:
        print("user not authenticated")
        messages.add_message(request, messages.INFO, 'You must be logged in to place an order')
        return redirect('home')
    else:
        print(request.META.get('HTTP_REFERER'))
        print('Inside buy food post method')
        fooditem = get_object_or_404(FoodItem, pk=fooditem_id)
        current_user = get_object_or_404(Customer, user_id=request.user.id)

        fooditem.shop.shop_owner.credit += fooditem.price
        fooditem.shop.shop_owner.save()

        current_user.balance -= fooditem.price
        current_user.save()
        print(fooditem.shop_id)
        context = {'fooditem': fooditem, 'user': current_user, 'shop': fooditem.shop_id}

        return render(request, "main/order_confirmation.html", context)
