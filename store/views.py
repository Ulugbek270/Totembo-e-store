from random import randint

from django.shortcuts import render, redirect
from .models import *
from django.views.generic import ListView, DetailView
from django.contrib.auth import login, logout
from .forms import LoginForm, RegisterForm, ReviewForm, CustomerForm, ShippingForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import CartForAuthenticatedUser, get_cart_data
from shop import settings
import stripe

# Create your views here.

class ProductList(ListView):
    model = Product
    context_object_name = 'categories'
    template_name = 'store/product_list.html'
    extra_context = {
        'title': 'Главная страница'
    }

    def get_queryset(self):
        categories = Category.objects.filter(parent=None)
        return categories



class CategoryPage(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'store/category_page.html'  # Укзал для какой страницы данная вьюшка
    paginate_by = 3

    # Метод для получения товаров
    def get_queryset(self):
        sort_field = self.request.GET.get('sort')
        type_field = self.request.GET.get('type')

        if type_field:
            products = Product.objects.filter(category__slug=type_field)
            return products

        main_category = Category.objects.get(slug=self.kwargs['slug']) # По slug получ глав категорию
        subcategories = main_category.subcategories.all()  # Из категории поличи подкатегории
        products = Product.objects.filter(category__in=subcategories)  # Получ все продукты подкатегорий
        if sort_field:
            products = products.order_by(sort_field)

        return products

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        main_category = Category.objects.get(slug=self.kwargs['slug'])
        context['category'] = main_category
        context['title'] = f'Категория: {main_category.title}'
        return context



class ProductDetail(DetailView):
    model = Product
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        product = Product.objects.get(slug=self.kwargs['slug'])
        context['title'] = f'{product.category}: {product.title}'

        products = Product.objects.all()
        data = []  # В этот список будут попадать рандомные товары
        for i in range(4):
            random_index = randint(0, len(products)-1)
            p = products[random_index]
            if p not in data:
                data.append(p)

        context['products'] = data
        context['reviews'] = Review.objects.filter(product=product)
        if self.request.user.is_authenticated:
            context['review_form'] = ReviewForm()


        return context




def user_login(request):
    form = LoginForm(data=request.POST)
    if form.is_valid():
        user = form.get_user()
        login(request, user)
        page = request.META.get('HTTP_REFERER', 'product_list')  # Получаем Адрес страницы запроса
        messages.success(request, 'Успешный вход в Аккаунт')
        return redirect(page)
    else:
        page = request.META.get('HTTP_REFERER', 'product_list')
        messages.error(request, 'Не верный логин или пароль')
        return redirect(page)



def user_logout(request):
    logout(request)
    page = request.META.get('HTTP_REFERER', 'product_list')  # Получаем Адрес страницы запроса
    messages.warning(request, 'Вы вышли из Аккаунта')
    return redirect(page)




def register_user(request):
    form = RegisterForm(data=request.POST)
    if form.is_valid():
        user = form.save()
        messages.success(request, 'Регистрация прошла успешно. Войдите в аккаунт')
    else:
        for field in form.errors:
            messages.error(request, form.errors[field].as_text())

    page = request.META.get('HTTP_REFERER', 'product_list')
    return redirect(page)



def save_review(request, slug):
    form = ReviewForm(data=request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.author = request.user
        product = Product.objects.get(slug=slug)  # Получаем продукт
        review.product = product  # Добавили продукт для отзыва
        review.save()
        messages.success(request, 'Ваш отзыв оставлен')
    else:
        pass

    return redirect('product_detail', product.slug)



# Функция для добавления продукта в избранное
def save_favorite_product(request, slug):
    if request.user.is_authenticated:
        user = request.user
        product = Product.objects.get(slug=slug)
        favorite_products = FavoriteProduct.objects.filter(user=user)  # Получаем избранные товары пользователя
        if user:
            if product not in [i.product for i in favorite_products]:
                FavoriteProduct.objects.create(user=user, product=product)
                messages.success(request, 'Продукт добавлен в избранное')
            else:
                fav_product = FavoriteProduct.objects.get(user=user, product=product)
                fav_product.delete()
                messages.warning(request, 'Продукт удалён из Избранного')

    else:
        messages.error(request, 'Авторизуйтесь что бы добавить в Избранное')

    page = request.META.get('HTTP_REFERER', 'product_list')
    return redirect(page)




class FavoriteProductView(LoginRequiredMixin ,ListView):
    model = FavoriteProduct
    context_object_name = 'products'
    template_name = 'store/favorite.html'
    login_url = 'product_list'

    # Нужео реализовать метод для получения товаро изранного самого пользователя
    def get_queryset(self):
        user = self.request.user
        favorite_products = FavoriteProduct.objects.filter(user=user)
        products = [i.product for i in favorite_products]
        return products




# Функция для страницы корзины
def cart(request):
    cart_info = get_cart_data(request)

    context = {
        'title': 'Моя корзина',
        'order': cart_info['order'],
        'products': cart_info['products']
    }

    return render(request, 'store/cart.html', context)

# Функция для добавления товара в корзину
def to_cart(request, product_id, action):
    if request.user.is_authenticated:
        user_cart = CartForAuthenticatedUser(request, product_id, action)
        messages.success(request, 'Проверь корзину')
        page = request.META.get('HTTP_REFERER', 'product_list')
        return redirect(page)
    else:
        messages.success(request, 'Авторизуйтесь что бы добавить в корзину')
        page = request.META.get('HTTP_REFERER', 'product_list')
        return redirect(page)



# Функция для страницы оформления заказаз
def checkout(request):
    if request.user.is_authenticated:
        cart_info = get_cart_data(request)

        context = {
            'title': 'Оформление заказа',
            'order': cart_info['order'],
            'items': cart_info['products'],

            'customer_form': CustomerForm(),
            'shipping_form': ShippingForm()
        }

        return render(request, 'store/checkout.html', context)




# Функция для совершения оплаты и сохранения данных пользователя с Адресом доставки
def create_checkout_session(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if request.method == 'POST':
        user_cart = CartForAuthenticatedUser(request)  # Получ корзину покупателя
        cart_info = user_cart.get_cart_info()  # Из корзины при помощи метода получаем информацию о корзине


        # Сохранение данных покупателя
        customer_form = CustomerForm(data=request.POST)
        if customer_form.is_valid():
            customer = Customer.objects.get(user=request.user)  # Получиди покупателя по пользователю
            customer.first_name = customer_form.cleaned_data['first_name']  # Указали имя покупателю по данным из формы
            customer.last_name = customer_form.cleaned_data['last_name']
            customer.save()

        # Сохранение данных Адреса доставки
        shipping_form = ShippingForm(data=request.POST)
        if shipping_form.is_valid():
            address = shipping_form.save(commit=False)
            address.customer = Customer.objects.get(user=request.user)
            address.order = user_cart.get_cart_info()['order']
            address.save()

        total_price = cart_info['cart_total_price']
        session = stripe.checkout.Session.create(
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Покупка на сайте TOTEMBO'
                    },
                    'unit_amount': int(total_price * 100)
                },
                'quantity': 1
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('success')),
            cancel_url=request.build_absolute_uri(reverse('checkout'))
        )

        return redirect(session.url, 303)




# Функция для страницы успешной оплаты
def success_payment(request):
    if request.user.is_authenticated:
        user_cart = CartForAuthenticatedUser(request)
        cart_info = user_cart.get_cart_info()
        order = cart_info['order']  # Получили заказа
        order_save = SaveOrder.objects.create(customer=order.customer, total_price=order.get_cart_total_price)  # Создаём
        order_save.save()  # Сохраеняем
        order_products = order.orderproduct_set.all()
        for item in order_products:
            save_order_product = SaveOrderProducts.objects.create(order_id=order_save.pk,
                                                                  product=str(item),
                                                                  quantity=item.quantity,
                                                                  product_price=item.product.price,
                                                                  final_price=item.get_total_price,
                                                                  photo=item.product.get_image_product())
            print(f'Заказанный продукт {item} сохранён')
            save_order_product.save()


        user_cart.clear()  # После успешной оплаты вызвали метод что бы очистить корзину
        messages.success(request, 'Ваша оплата прошла успешно')
        return render(request, 'store/success.html')




# Вьюшка для очищения корзины
def clear_cart(request):
    user_cart = CartForAuthenticatedUser(request)
    order = user_cart.get_cart_info()['order']
    order_products = order.orderproduct_set.all()
    for order_product in order_products:
        quantity = order_product.quantity
        product = order_product.product
        order_product.delete()
        product.quantity += quantity
        product.save()
    return redirect('my_cart')



def save_mail(request):
    if request.user.is_authenticated:
        email = request.POST.get('email')
        user = request.user
        if email:
            try:
                Mail.objects.create(mail=email, user=user)
                messages.success(request, 'Ваша почта сохранена')
            except:
                messages.warning(request, 'Ваша почта уже сохраенна')

        page = request.META.get('HTTP_REFERER', 'product_list')
        return redirect(page)



from shop import settings
from django.core.mail import send_mail
def send_mail_to_customer(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            text = request.POST.get('text')
            mail_list = Mail.objects.all()
            for email in mail_list:
                mail = send_mail(
                    subject='У нас для вас новинки',
                    message=text,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email], # Указали кому отправлять
                    fail_silently=False
                )
                print(f'Рассылка выполнена на почту {email}? - {bool(mail)}')
        else:
            pass

        return render(request, 'store/send_mail.html')

    else:
        return redirect('product_list')




