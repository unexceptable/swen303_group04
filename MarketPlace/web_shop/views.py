from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect
from web_shop.forms import (
    SearchForm, LoginForm, EditCredentialsForm, CartForm, ChatForm, MessageForm)
from .models import Product, Category, ChatHistory
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils.encoding import smart_text
from cart.cart import Cart
from django.http import HttpResponseRedirect

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
        Q(name__contains=search) | Q(description__contains=search),
        visible=True)
    context = {
        'search': form.data["search"],
        'products': products,
    }
    return render(request, "products.html", context)


def product_detail(request, p_id):
    # here we need to get the product via the id

    try:
        product = Product.objects.get(pk=p_id)
        if not product.visible:
            raise Product.DoesNotExist

        form = CartForm()

        images = product.image_set.all()

        in_cart = 0
        cart = Cart(request)
        for item in cart:
            if item.product.pk == product.pk:
                in_cart = item.quantity

        context = {
            'username': request.user.username,
            'product': product,
            'images': images,
            'in_cart': in_cart,
            'form': form,
        }
        return render(request, "detail.html", context)
    except Product.DoesNotExist:
        return render(
            request, '404.html',
            {
                'username': request.user.username,
                'errorMessage':
                    'The product with the id ' + p_id + ' does not exist'})


def product_cart(request, p_id):
    if request.method != 'POST':
        return redirect("/product/%s" % p_id)
    try:
        product = Product.objects.get(pk=p_id)
        if not product.visible:
            raise Product.DoesNotExist
    except Product.DoesNotExist:
        return render(
            request, '404.html',
            {
                'username': request.user.username,
                'errorMessage':
                    'The product with the id ' + p_id + ' does not exist'})

    in_cart = False
    cart = Cart(request)
    for item in cart:
        print item.product.name
        if item.product.pk == product.pk:
            in_cart = True

    form = CartForm(request.POST)
    if form.is_valid():
        if in_cart:
            if form.data.get('update'):
                cart.update(product, form.data['quantity'], product.price)
            else:
                print("removing!")
                cart.remove(product)
        else:
                print("adding!")
                cart.add(product, product.price, form.data['quantity'])

    return redirect("/product/%s" % product.pk)


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
                        'feedback': 'Disabled account'}
                    return render(request, "feedback.html", context)
            else:
                # Return an 'invalid login' error message.
                context = {
                    'feedback': 'Invalid account'}
                return render(request, "feedback.html", context)

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

        return render(request, "category_view.html", context)
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
                    'feedback': 'Invalid current password'}
                return render(request, "feedback.html", context)

        else:
            # Return an error message.
            context = {
                'feedback': 'Either new password does not match with retyped or invalid email'}
            return render(request, "feedback.html", context)
    # if a GET (or any other method) we'll create a blank form
    else:
        form = EditCredentialsForm(initial={
            'firstName': request.user.first_name,
            'lastName': request.user.last_name,
            'email': request.user.email,
            })

        return render(
            request, 'edit_details.html',
            {'form': form})


def cart(request):
    cart = Cart(request)
    return render(request, 'cart.html', dict(cart=cart))


def cart_remove(request, p_id):
    product = Product.objects.get(pk=p_id)
    cart = Cart(request)
    cart.remove(product)
    return render(request, 'cart.html', dict(cart=cart))


def chat(request):
    # if this is a GET request we need to show chat history
    if request.method == 'GET':
        form = ChatForm(request.GET)
        if not form.is_valid():
            # if the form isn't valid (empty basically) redirect to home.
            return redirect("/")

        chat = form.data['chat']
        history = ChatHistory.objects.filter(
            (Q(origin__contains=chat) & Q(to__contains=request.user.username)) | (Q(origin__contains=request.user.username) & Q(to__contains=chat)) )
        context = {
            'user': form.data["chat"],
            'history': history,
            'form' : MessageForm(initial={'to': chat})
        }
        return render(request, "chat.html", context)
    #Process data sent
    else:
        form = MessageForm(request.POST)
        if form.is_valid():
            if User.objects.filter(username=request.POST['to']).exists():
                ChatHistory.objects.create(origin=request.user.username, to= request.POST['to'], message=request.POST['message'])
                return HttpResponseRedirect("?chat="+request.POST["to"])
            else:
                # if the form isn't valid (empty basically) redirect to home.
                return redirect("/")
        else:
            # if the form isn't valid (empty basically) redirect to home.
            return redirect("/")
