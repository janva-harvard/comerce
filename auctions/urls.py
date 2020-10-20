from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("new_listing", views.new_listing_view, name="new_listing"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listing/<int:id>", views.listing_view, name="listing"),
    path("listing/category/<int:id>",
         views.category_listing_view,
         name="category_listing"),
    path("listing/watched/<int:id>", views.watchlist_view, name="watchlist"),
    path("categories", views.categories_view, name="categories"),
]
