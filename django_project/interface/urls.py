from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^home/$', views.home),
    url(r'^upload/', views.upload),
    url(r'^test/',views.test),
]