from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=150, verbose_name='Название категории')
    image = models.ImageField(upload_to='categories/',blank=True, null=True ,verbose_name='Картинки категорий')
    slug = models.SlugField(unique=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                               related_name='subcategories', verbose_name='Категория')

    # Умная ссылка для категорий
    def get_absolute_url(self):
        return reverse('category_page', kwargs={'slug': self.slug})

    # Метод для получения картинок категории
    def get_image_category(self):
        if self.image:
            return self.image.url
        else:
            return ''

    def __str__(self):
        return self.title


    def __repr__(self):
        return f'Категория: pk={self.pk}, title={self.title}'


    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Product(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название продукта')
    price = models.FloatField(verbose_name='Цена')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    quantity = models.IntegerField(default=0, verbose_name='Количество товара')
    description = models.TextField(default='Описание скоро будит', verbose_name='Описание товара')
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 verbose_name='Категория', related_name='products')
    slug = models.SlugField(unique=True, null=True)
    size = models.IntegerField(default=30, verbose_name='Размер')
    color = models.CharField(max_length=30, default='Серебро', verbose_name='Цвет/Материал')

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})

    # Метод для получения картинок категории
    def get_image_product(self):
        if self.images:
            try:
                return self.images.first().image.url
            except:
                return ''
        else:
            return ''

    def __str__(self):
        return self.title


    def __repr__(self):
        return f'Категория: pk={self.pk}, title={self.title}, price={self.price}'


    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'




class Gallery(models.Model):
    image = models.ImageField(upload_to='products/', verbose_name='Картинки продуктов')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')

    class Meta:
        verbose_name = 'Картинка'
        verbose_name_plural = 'Картинки'




class Review(models.Model):
    text = models.TextField(verbose_name='Отзыв покупателя')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Покупатель')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Продукт отзыва')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата отзыва')

    def __str__(self):
        return self.author.username

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'




# Моделька Избранное
class FavoriteProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Покупатель')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Продукт избранного')

    def __str__(self):
        return self.product.title

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'




class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Пользователь')
    first_name = models.CharField(max_length=250, default='', verbose_name='Имя покупателя')
    last_name = models.CharField(max_length=250, default='', verbose_name='Фамилия покупателя')


    def __str__(self):
        return self.first_name

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'



class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Покупатель')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')
    is_completed = models.BooleanField(default=False, verbose_name='Заказ выполнен')
    shipping = models.BooleanField(default=True, verbose_name='Доставка')

    def __str__(self):
        return str(self.pk)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    # Метод для получения суммы заказа
    @property
    def get_cart_total_price(self):
        order_products = self.orderproduct_set.all() # Получаем заказанные продукты самого заказа
        total_price = sum([product.get_total_price for product in order_products])
        return total_price

    @property
    def get_cart_total_quantity(self):
        order_products = self.orderproduct_set.all()  # Получаем заказанные продукты самого заказа
        total_quantity = sum([product.quantity for product in order_products])
        return total_quantity




class OrderProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name='Продукт')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, verbose_name='Заказ')
    quantity = models.IntegerField(default=0, null=True, blank=True, verbose_name='Количество')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    def __str__(self):
        return self.product.title

    class Meta:
        verbose_name = 'Заказанный товар'
        verbose_name_plural = 'Заказанные товары'

    # Метод который вернёт сумму товара в его кол-ве
    @property  # Декоратер нужен что бы можно было вызывать метод в другой модели(классе)
    def get_total_price(self):
        total_price = self.product.price * self.quantity
        return total_price




# Модель доставки
class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, verbose_name='Покупатель')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, verbose_name='Заказ')
    address = models.CharField(max_length=300, verbose_name='Адрес (ул, дом, кв)')
    city = models.ForeignKey('City', on_delete=models.CASCADE, verbose_name='Город')
    region = models.CharField(max_length=300, verbose_name='Регион')
    phone = models.CharField(max_length=250, verbose_name='Номер телефона')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата доставки')

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = 'Адрес доставки'
        verbose_name_plural = 'Адреса доставок'


class City(models.Model):
    city = models.CharField(max_length=300, verbose_name='Город')


    def __str__(self):
        return self.city

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'




# Модель для сохранения почт
class Mail(models.Model):
    mail = models.EmailField(unique=True, verbose_name='Название почты')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Пользователь')

    def __str__(self):
        return self.mail

    class Meta:
        verbose_name = 'Почта'
        verbose_name_plural = 'Почтовые Адреса'



# Модель для сохраенния Заказов
class SaveOrder(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Покупатель')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')
    total_price = models.FloatField(default=0, verbose_name='Сумма заказа')


    def __str__(self):
        return f'Заказ №: {self.pk}'


    class Meta:
        verbose_name = 'История заказа'
        verbose_name_plural = 'Истории заказов'


# Модель для сохранения заказанных продуктов
class SaveOrderProducts(models.Model):
    order = models.ForeignKey(SaveOrder, on_delete=models.CASCADE, null=True, related_name='products')
    product = models.CharField(max_length=400, verbose_name='Товар')
    quantity = models.IntegerField(default=0, verbose_name='Количество')
    product_price = models.FloatField(verbose_name='Цена товара')
    final_price = models.FloatField(verbose_name='На сумму')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата покупки')
    photo = models.ImageField(upload_to='images/', verbose_name='Фото товара')

    def __str__(self):
        return f'{self.product}'


    class Meta:
        verbose_name = 'История заказанного товара'
        verbose_name_plural = 'Истории заказанных товаров'










