from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect
from web_shop.forms import SearchForm, LoginForm, EditCredentialsForm
from .models import Product, Category
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout


def index(request):
    context = {
        'username': request.user.username,
    }
    template = loader.get_template("index.html")
    return HttpResponse(template.render(context))


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
        'username': request.user.username,
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
            'username': request.user.username,
            'product': product
        }
        template = loader.get_template("detail.html")
        return HttpResponse(template.render(context))
    except Product.DoesNotExist:
        return render(
            request, '404.html',
            {
                'username': request.user.username,
                'errorMessage':
                    'The product with the id ' + p_id + ' does not exist'})


def signin(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = LoginForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
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
                    context = {
                        'username': request.user.username,
                        'feedback': 'Disabled account'}
                    template = loader.get_template("feedback.html")
                    return HttpResponse(template.render(context))
            else:
                # Return an 'invalid login' error message.
                context = {
                    'username': request.user.username,
                    'feedback': 'Invalid account'}
                template = loader.get_template("feedback.html")
                return HttpResponse(template.render(context))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = LoginForm()

    return render(
        request, 'login.html',
        {'username': request.user.username, 'form': form})


def category_view(request, category_name):
    try:
        #print(type(category))
        if(category_name=='all'):
            category_list = Category.objects.all()
            context = {
                'category': category_name,
                'categories': category_list,
            }
        #    return render(request, 'category_view.html', context})
        else:
            c = Category.objects.get(category=category_name)
            product_list = c.product_set.all()
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


def logout_user(request):
    logout(request)
    # Redirect to home
    return redirect("/")

def edit_details(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = EditCredentialsForm(request.POST)
        if form.is_valid():
            if request.user.check_password(request.POST['oldPass']):
                firstName = request.POST['firstName']
                lastName = request.POST['lastName']
                email = request.POST['email']
                newPass = request.POST['newPass']

                request.user.first_name = firstName
                request.user.last_name = lastName
                request.user.email = email
                if newPass:
                    request.user.set_password(newPass)

                request.user.save()

                if newPass:
                    # auto re-login
                    user = authenticate(username=request.user.username, password=newPass)
                    login(request, user)

                # Redirect to home
                return redirect("/")
            else:
                # Return an error message.
                context = {
                    'username': request.user.username,
                    'feedback': 'Invalid current password'}
                template = loader.get_template("feedback.html")
                return HttpResponse(template.render(context))

        else:
            # Return an error message.
            context = {
                'username': request.user.username,
                'feedback': 'Either new password does not match with retyped or invalid email'}
            template = loader.get_template("feedback.html")
            return HttpResponse(template.render(context))
    # if a GET (or any other method) we'll create a blank form
    else:
        form = EditCredentialsForm(initial={
            'firstName': request.user.first_name,
            'lastName': request.user.last_name,
            'email': request.user.email,
            })

        return render(
            request, 'edit_details.html',
            {'username': request.user.username, 'form': form})
