from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect
from forms import SearchForm
from models import Product
from django.db.models import Q


def index(request):
    return render(request, "index.html")


def search(request):
    form = SearchForm(request.GET)
    if not form.is_valid():
        # if the form isn't valid (empty basically) redirect to home.
        return redirect("/")

    search = form.data['search']
    # This is an AWFUL search... but at least something to start with.
    products = Product.objects.filter(
        Q(name__contains=search) | Q(desciption__contains=search))
    context = {
        'search': form.data["search"],
        'products': products,
    }
    template = loader.get_template("products.html")
    return HttpResponse(template.render(context))


def product_detail(request, p_id):
    # here we need to get the product via the id

    try:
        product = Product.objects.get(pk=p_id)
        context = {
            'product': product
        }
        template = loader.get_template("detail.html")
        return HttpResponse(template.render(context))
    except Product.DoesNotExist:
        return render(
            request, '404.html',
            {'errorMessage':
                'The product with the id ' + p_id + ' does not exist'})
