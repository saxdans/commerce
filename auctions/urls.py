from django.urls import path

from . import views

#app_name = 'auctions'
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("newlisting", views.newlisting, name="newlisting"),
    path("<str:listing_title>/", views.viewlisting, name="viewlisting"),
    path("mylistings", views.mylistings, name="mylistings"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category>", views.categorylist, name="categorylist"),
    path("nosuchpage", views.nosuchpage, name="nosuchpage"),
    path("closedlistings",views.closedlistings, name="closedlistings")
]
