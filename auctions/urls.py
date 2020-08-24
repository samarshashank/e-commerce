from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("createnew", views.createnew, name="createlisting"),
    path("categories", views.categories, name="categories"),
    path("category/<str:category>", views.category, name="category"),
    path("watchlist/<int:listing_id>", views.addedwatchlist, name="watchlist_an_item"),
    path("close/<int:listing_id>", views.closeauction, name="close_auction"),
    path("<int:listing_id>",views.listing, name="listing")
]
