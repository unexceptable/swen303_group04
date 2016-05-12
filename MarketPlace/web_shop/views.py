from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect
from web_shop.forms import SearchForm
from .models import Product, Category
from django.db.models import Q
from django.contrib.auth import authenticate, login


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

def signin_process(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            # Redirect to home
            return redirect("/")
        else:
            # Return a 'disabled account' error message
            context = {'feedback': 'Disabled account'}
            template = loader.get_template("feedback.html")
            return HttpResponse(template.render(context))
    else:
        # Return an 'invalid login' error message.
        context = {'feedback': 'Invalid account'}
        template = loader.get_template("feedback.html")
        return HttpResponse(template.render(context))


def category_view(request, category):
    try:
        print(category)
        c = Category.objects.get(category=category)
        #print(help(c.product_set.))
        product_list = c.product_set.all()
        #print("product list: "+ product_list)
        print ("here?")
        context = {
            'category': c,
            'product_list': product_list
        }

        template = loader.get_template("category_view.html")

        return HttpResponse(template.render(context))
    except Category.DoesNotExist:
        return render(
            request, '404.html',
            {'errorMessage':
                'That category does not exist'})
