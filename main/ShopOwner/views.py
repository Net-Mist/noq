from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from ..models import Shop, SubscriptionType, FoodItem, Category, Order
from django import forms
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions
from crispy_forms.utils import render_crispy_form
from django.utils import timezone
import urllib3
import json


def get_gps_coordinate(post_code: int):
    http = urllib3.PoolManager()
    r = http.request('GET', 'https://maps.googleapis.com/maps/api/geocode/json?address=' + str(
        post_code) + ',+Singapore&key=AIzaSyA3VQzOg4WzjmDwFT8vP4ptCYbj0edQvPw')

    content = json.loads(r.data.decode('utf-8'))

    lat = content['results'][0]['geometry']['location']['lat']
    lng = content['results'][0]['geometry']['location']['lng']

    print(lat)
    print(lng)

    return lat, lng


def generate_subscription_choose():
    subscription_objects = SubscriptionType.objects.all()
    subscription_list = []
    for subscription in subscription_objects:
        subscription_list.append(
            (str(subscription.id), subscription.description + ": " + str(subscription.price) + " SGD"))

    return subscription_list


def generate_category_choose():
    objects = Category.objects.all()
    list = []
    for object in objects:
        list.append((str(object.id), object.name + ", " + object.description))
    return list


class NewShopForm(forms.Form):
    shop_name = forms.CharField()

    subscription = forms.ChoiceField(
        choices=(generate_subscription_choose()),
        widget=forms.RadioSelect,
        initial='1',
    )

    postal_code = forms.IntegerField()

    # Uni-form
    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Field('shop_name', css_class='input-xlarge'),
        'subscription',
        'postal_code',
        FormActions(
            Submit('save_changes', 'Save changes', css_class="btn-primary"),
            Submit('cancel', 'Cancel'),
        )
    )


class NewMealForm(forms.Form):
    name = forms.CharField()
    price = forms.FloatField()
    category = forms.ChoiceField(
        choices=(generate_category_choose()),
        widget=forms.RadioSelect,
        initial='1',
    )

    # Uni-form
    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Field('name', css_class='input-xlarge'),
        'price',
        'category',
        FormActions(
            Submit('save_changes', 'Save changes', css_class="btn-primary"),
            Submit('cancel', 'Cancel'),
        )
    )


def index(request):
    shop_list = Shop.objects.order_by('name')
    return render(request, 'main/index_shopowner.html', {'shop_list': shop_list})


def shop(request, shop_id):
    current_shop = get_object_or_404(Shop, pk=shop_id)
    current_order = Order.objects.filter(fooditem__shop=shop_id).filter(isServed=False).order_by(
        'order_date').distinct()
    return render(request, 'main/shop.html', {'shop': current_shop, 'orders': current_order})


def newmeal(request, shop_id):
    current_shop = get_object_or_404(Shop, pk=shop_id)
    form = NewMealForm(request.POST or None)
    if form.is_valid():
        # Create the new meal
        new_meal = FoodItem(price=request.POST['price'], name=request.POST['name'],
                            shop_id=shop_id, category_id=request.POST['category'])
        new_meal.save()
        # return to the shop page
        return HttpResponseRedirect(reverse('shopowner:shop', args=(shop_id)))

    return render(request, 'main/newmeal.html', {'form': form})


def newshop(request):
    form = NewShopForm(request.POST or None)
    if form.is_valid():
        # Create the new shop

        postal_code = request.POST['postal_code']
        lat, lng = get_gps_coordinate(postal_code)

        new_shop = Shop(name=request.POST['shop_name'], postal_code=postal_code,
                        subscription_id=request.POST['subscription'],
                        latitude=lat,
                        longitude=lng,
                        shop_owner_id=1)  # TODO remplace with the good id
        new_shop.save()

        # return to the shop page
        return HttpResponseRedirect(reverse('shopowner:index'))
    return render(request, 'main/newshop.html', {'form': form})


def food_ready(request, shop_id, food_id):
    current_shop = get_object_or_404(Shop, pk=shop_id)
    current_order = get_object_or_404(Order, pk=food_id)
    current_order.isServed = True

    current_order.save()

    return shop(request, shop_id)


def food_available(request, shop_id, food_id):
    current_shop = get_object_or_404(Shop, pk=shop_id)
    current_food_item = get_object_or_404(FoodItem, pk=food_id)
    current_food_item.is_available = not current_food_item.is_available

    current_food_item.save()

    return shop(request, shop_id)
