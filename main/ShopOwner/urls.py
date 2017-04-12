from django.conf.urls import url
from . import views

app_name = 'shopowner'
urlpatterns = [
    # ex: /noq/shopowner/
    url(r'^$', views.index, name='index'),
    # ex: /noq/shopowner/5/
    url(r'^(?P<shop_id>[0-9]+)/$', views.shop, name='shop'),
    # ex: /noq/shopowner/newshop/
    url(r'^newshop/$', views.newshop, name='newshop'),
    url(r'^newmeal/(?P<shop_id>[0-9]+)/$', views.newmeal, name='newmeal'),
    url(r'^(?P<shop_id>[0-9]+)/foodready/(?P<food_id>[0-9]+)/$', views.food_ready, name='food_ready'),
    url(r'^(?P<shop_id>[0-9]+)/foodavailable/(?P<food_id>[0-9]+)/$', views.food_available, name='food_available'),

]
