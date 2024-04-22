from django.urls import path
from .views import *

# Сдесь будим писать пути для вьюшек
urlpatterns = [
    path('', ProductList.as_view(), name='product_list'),
    path('category/<slug:slug>/', CategoryPage.as_view(), name='category_page'),
    path('product/<slug:slug>/', ProductDetail.as_view(), name='product_detail'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('register/', register_user, name='register'),
    path('save_review/<slug:slug>/', save_review, name='save_review'),
    path('add_favorite/<slug:slug>/', save_favorite_product, name='add_favorite'),
    path('my_favorite/', FavoriteProductView.as_view(), name='my_favorite'),
    path('cart/', cart, name='my_cart'),
    path('to_cart/<int:product_id>/<str:action>/', to_cart, name='to_cart'),
    path('checkout/', checkout, name='checkout'),
    path('payment/', create_checkout_session, name='payment'),
    path('success/', success_payment, name='success'),
    path('clear_cart/', clear_cart, name='clear_cart'),
    path('save_mail/', save_mail, name='save_mail'),
    path('send_mail/', send_mail_to_customer, name='send_mail')

]