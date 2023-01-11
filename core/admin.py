from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib import admin
from store.admin import ProductAdmin
from tags.models import TaggedItem
from store.models import Product
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


# Register our Extended user admin
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "password1", "password2", "email", "first_name", "last_name"),
        }),
    )


class TagInline(GenericTabularInline):
    model = TaggedItem
    autocomplete_fields = ['tag']


class CustomProductAdmin(ProductAdmin):
    inlines = [TagInline]


admin.site.unregister(Product)
admin.site.register(Product, CustomProductAdmin)
