from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import *

# Register your models here.

class GalleryInline(admin.TabularInline):
    fk_name = 'product'
    model = Gallery
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'parent', 'get_count_products')
    prepopulated_fields = {'slug': ('title',)}

    # Метод для получения количество товара категории
    def get_count_products(self, obj):
        if obj.products:
            return str(len(obj.products.all()))
        else:
            return '0'

    get_count_products.short_description = 'Количество товара'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'category', 'quantity', 'price', 'size', 'color', 'created_at', 'get_photo')
    list_editable = ('quantity', 'price', 'size', 'color')  # Какие поля можно редактировать
    list_display_links = ('title',)
    list_filter = ('title', 'price', 'category')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [GalleryInline]

    # Метод который вернёт в Админку картинку товара
    def get_photo(self, obj):
        if obj.images:
            try:
                return mark_safe(f'<img src="{obj.images.all()[0].image.url}" width="75">')
            except:
                return '-'
        else:
            return '-'

    get_photo.short_description = 'Изображение'


# admin.site.register(Category)
# admin.site.register(Product)
admin.site.register(Gallery)
admin.site.register(Review)
admin.site.register(FavoriteProduct)

admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderProduct)
admin.site.register(ShippingAddress)
admin.site.register(City)

admin.site.register(Mail)

admin.site.register(SaveOrder)
admin.site.register(SaveOrderProducts)