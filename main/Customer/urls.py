from django.conf.urls import url
from . import views


app_name = 'customer'

urlpatterns = [
    # url(r'^$', views.index, name='index'),
    url(r'^fooditems/(?P<shop_id>[0-9]+)/$', views.fooditems, name="fooditems"),
    url(r'^buyitem/(?P<fooditem_id>[0-9]+)/$', views.buy_fooditem, name="buy_fooditem")
]