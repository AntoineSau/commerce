from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:auction_id>", views.auction, name="auction"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("createlisting", views.createlisting, name="createlisting"),
    path("register", views.register, name="register"),
    path("categories", views.categories, name="categories"),
]
