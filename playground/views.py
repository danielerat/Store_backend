from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from store.models import Product, Collection
from tags.models import TaggedItem


# Create your views here.
def say_hello(request):
    products = Product.objects.all()

    return render(request, 'playground/index.html',
                  {'products': products})
