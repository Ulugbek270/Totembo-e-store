from django import template
from store.models import Category, FavoriteProduct


register = template.Library()


@register.simple_tag()
def get_categories():   # Функция которая вернёт все категории у котторых Нет родителя
    return Category.objects.filter(parent=None)


@register.simple_tag()
def get_sorted():
    sorters = [
        {
            'title': 'По цене',
            'sorters': [
                ('price', 'По возрастанию'),
                ('-price', 'По убыванию')
            ]
        },
        {
            'title': 'По цвету',
            'sorters': [
                ('color', 'От А до Я'),
                ('-color', 'От Я до А')
            ]
        },
        {
            'title': 'По размеру',
            'sorters': [
                ('size', 'По возрастанию'),
                ('-size', 'По убыванию')
            ]
        }
    ]

    return sorters



# Функция которая вернёт избранные товары полдьзователя
@register.simple_tag()
def get_favorite_products(user):
    favs = FavoriteProduct.objects.filter(user=user)
    products = [i.product for i in favs]
    return products





