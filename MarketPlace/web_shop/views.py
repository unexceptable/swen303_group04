from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect
from web_shop.forms import (
    SearchForm, LoginForm, EditCredentialsForm, CartForm,
    ChatForm, MessageForm, AddressForm)
from .models import (
    Product, Category, ChatHistory, Address, SalesOrder,
    OrderItem)
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from cart.cart import Cart
from django.http import HttpResponseRedirect, HttpResponse

def index(request):
    category_list = Category.objects.all()
    context = {
        'cart': Cart(request),
        'categories': category_list,
    }
    return render(request, "index.html", context)


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
        'cart': Cart(request),
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
            'cart': Cart(request),
        }
        return render(request, "detail.html", context)
    except Product.DoesNotExist:
        return render(
            request, '404.html',
            {
                'username': request.user.username,
                'errorMessage':
                    'The product with the id ' + p_id + ' does not exist',
                'cart': Cart(request),
            })


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
                    'The product with the id ' + p_id + ' does not exist',
                'cart': Cart(request),
            })

    in_cart = False
    cart = Cart(request)
    for item in cart:
        if item.product.pk == product.pk:
            in_cart = True

    form = CartForm(request.POST)
    if form.is_valid():
        if in_cart:
            if (form.cleaned_data.get('update') and
                    form.cleaned_data['quantity'] > 0):
                cart.update(
                    product, form.cleaned_data['quantity'], product.price)
            else:
                cart.remove(product)
        else:
                cart.add(product, product.price, form.cleaned_data['quantity'])

    return redirect("/product/%s" % product.pk)


def signin(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = LoginForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    # Redirect to home
                    return redirect("/")
                else:
                    # Return a 'disabled account' error message
                    context = {
                        'heading': 'Error',
                        'feedback': 'Disabled account',
                        'cart': Cart(request),
                    }
                    return render(request, "feedback.html", context)
            else:
                # Return an 'invalid login' error message.
                context = {
                    'heading': 'Error',
                    'feedback': 'Invalid account',
                    'cart': Cart(request),
                }
                return render(request, "feedback.html", context)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = LoginForm()

    return render(
        request, 'login.html',
        {
            'username': request.user.username,
            'form': form,
            'cart': Cart(request),
        })


def category_view(request, category_name):
    try:
        if(category_name == 'all'):
            category_list = Category.objects.all()
            context = {
                'category': category_name,
                'categories': category_list,
                'cart': Cart(request),
            }
        #    return render(request, 'category_view.html', context})
        else:
            c = Category.objects.get(category=category_name)
            product_list = c.product_set.all()
            context = {
                'category': c,
                'product_list': product_list,
                'cart': Cart(request),
            }

        return render(request, "category_view.html", context)
    except Category.DoesNotExist:
        return render(
            request, '404.html',
            {
                'errorMessage':
                    'That category does not exist',
                'cart': Cart(request),
            })


def logout_user(request):
    logout(request)
    # Redirect to home
    return redirect("/")


def edit_details(request):
    #Check login
    if request.user.is_authenticated():
        # if this is a POST request we need to process the form data
        if request.method == 'POST':
            # create a form instance and populate it with data from the request:
            form = EditCredentialsForm(request.POST)
            if form.is_valid():
                if request.user.check_password(form.cleaned_data['oldPass']):
                    firstName = form.cleaned_data['firstName']
                    lastName = form.cleaned_data['lastName']
                    email = form.cleaned_data['email']
                    newPass = form.cleaned_data['newPass']

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

                    # Return ok.
                    context = {
                        'heading': 'Success',
                        'feedback': 'Credentials updated',
                        'cart': Cart(request),
                    }
                    return render(request, "feedback.html", context)
                else:
                    # Return an error message.
                    context = {
                        'heading': 'Error',
                        'feedback': 'Invalid current password',
                        'cart': Cart(request),
                    }
                    return render(request, "feedback.html", context)

            else:
                # Return an error message.
                context = {
                    'heading': 'Error',
                    'feedback': 'Either new password does not match with retyped or invalid email',
                    'cart': Cart(request),
                }
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
                {
                    'form': form,
                    'cart': Cart(request),
                })
    else:
        # Redirect to home
        return redirect("/")


def cart_view(request):
    cart = Cart(request)

    form = CartForm()

    context = {
        'cart': cart,
        'form': form,
    }

    return render(request, 'cart.html', context)


def cart_update(request, p_id):
    try:
        product = Product.objects.get(pk=p_id)
    except Product.DoesNotExist:
        return redirect("/cart")

    cart = Cart(request)

    form = CartForm(request.POST)
    if form.is_valid():
        if (form.cleaned_data.get('update') and
                form.cleaned_data['quantity'] > 0):
            cart.update(product, form.cleaned_data['quantity'], product.price)
        else:
            cart.remove(product)

    return redirect("/cart")

def chat(request):
    #Check login
    if request.user.is_authenticated():
        # if this is a GET request we need to show chat history
        if request.method == 'GET':
            form = ChatForm(request.GET)
            if not form.is_valid():
                # Return an error message.
                context = {
                    'heading': 'Error',
                    'feedback': 'Cannot be empty',
                    'cart': Cart(request),
                }
                return render(request, "feedback.html", context)

            context = {
                'user': form.data["chat"],
                'form' : MessageForm(initial={'to': form.data["chat"]})
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
                    # if user does not exist
                    return redirect("/")
            else:
                # Return an error message.
                context = {
                    'heading': 'Error',
                    'feedback': 'Cannot be empty',
                    'cart': Cart(request),
                }
                return render(request, "feedback.html", context)
    else:
        # Redirect to home
        return redirect("/")

def chat_reload(request):
    form = ChatForm(request.GET)
    chat = form.data['chat']
    history = ChatHistory.objects.filter(
        (Q(origin__exact=chat) & Q(to__exact=request.user.username)) | (Q(origin__exact=request.user.username) & Q(to__exact=chat)) )
    context = {
        'user': form.data["chat"],
        'history': history,
    }
    return render(request, "conversation.html", context)

def edit_address(request):
    #Check login
    if request.user.is_authenticated():
        # if this is a GET request we need to pre-fill AddressForm
        if request.method == 'GET':

            #in DB
            try:
                entry = Address.objects.get(user=request.user)
                form = AddressForm(initial={
                'number_street':entry.number_street,
                'suburb':entry.suburb,
                'city':entry.city,
                'region':entry.region,
                'country':entry.country,
                'postcode':entry.postcode,
                })
                context = {'form': form}
                return render(request, "edit_address.html", context)
            #not in DB
            except Address.DoesNotExist:
                context = {'form': AddressForm()}
                return render(request, "edit_address.html", context)

        #Process data sent
        else:
            form = AddressForm(request.POST)
            if form.is_valid():
                #in DB
                try:
                    entry = Address.objects.get(user=request.user)
                    entry.number_street=form.cleaned_data['number_street']
                    entry.suburb=form.cleaned_data['suburb']
                    entry.city=form.cleaned_data['city']
                    entry.region=form.cleaned_data['region']
                    entry.country=form.cleaned_data['country']
                    entry.postcode=form.cleaned_data['postcode']
                    entry.save()

                    # Return ok.
                    context = {
                        'heading': 'Success',
                        'feedback': 'Your new billing address is '+
                                form.cleaned_data['number_street']+', '+
                                form.cleaned_data['suburb']+' '+
                                form.cleaned_data['city']+', '+
                                form.cleaned_data['country']+' '+
                                request.POST['postcode'],
                        'cart': Cart(request),
                    }
                    return render(request, "feedback.html", context)
                #not in DB
                except Address.DoesNotExist:
                    Address.objects.create(
                    user=request.user,
                    number_street=form.cleaned_data['number_street'],
                    suburb=form.cleaned_data['suburb'],
                    city=form.cleaned_data['city'],
                    region=form.cleaned_data['region'],
                    country=form.cleaned_data['country'],
                    postcode=form.cleaned_data['postcode'],
                    )

                    # Return ok.
                    context = {
                        'heading': 'Success',
                        'feedback': 'Your new billing address is '+
                                form.cleaned_data['number_street']+', '+
                                form.cleaned_data['suburb']+' '+
                                form.cleaned_data['city']+', '+
                                form.cleaned_data['country']+' '+
                                request.POST['postcode'],
                        'cart': Cart(request),
                    }
                    return render(request, "feedback.html", context)
            else:
                # Return an error message.
                context = {
                    'heading': 'Error',
                    'feedback': 'All fields must be filled and postcode must be between 1000 to 9999 (inclusive)',
                    'cart': Cart(request),
                }
                return render(request, "feedback.html", context)

    else:
        # Redirect to home
        return redirect("/")

def listusers(request):
    #Check login
    if request.user.is_authenticated() and request.user.is_superuser:
        #process selected
        if request.method=="POST":
            entries = request.POST.getlist('selected')
            if 'Enable' in request.POST:
                for username in entries:
                    user = User.objects.get(username=username)
                    if not user.is_active:
                        user.is_active = True
                        user.save()

            elif 'Disable' in request.POST:
                for username in entries:
                    user = User.objects.get(username=username)
                    if user.is_active:
                        user.is_active = False
                        user.save()

        #show users
        context = {
            'heading': ('','Username','First Name','Last Name', 'Email', 'Active'),
            'users': User.objects.filter(is_superuser=False),
            'cart': Cart(request),
        }
        return render(request, "all_users.html", context)

    else:
        return redirect("/")


def checkout(request):
    if request.method == 'GET':
        cart = Cart(request)
        addresses = request.user.address_set.all()
        try:
            default = request.user.address_set.get(default=True)
        except Address.DoesNotExist:
            default = None

        context = {
            'cart': cart,
            'addresses': addresses,
            'default': default,
        }

        return render(request, 'checkout.html', context)
    if request.method == 'POST':
        print request.POST
        address_id = request.POST.get('address', None)

        if not address_id:
            return redirect("/")

        try:
            address = request.user.address_set.get(pk=address_id)
        except Address.DoesNotExist:
            return redirect("/")

        cart = Cart(request)

        order = SalesOrder(buyer=request.user, address=address)
        order.save()

        for item in cart:
            order_item = OrderItem(
                order=order, quantity=item.quantity,
                unit_price=item.unit_price, product=item.product)
            order_item.save()

        return render(request, 'checkedout.html')

def listsales(request):
    #Check login superuser
    if request.user.is_authenticated() and request.user.is_superuser:
        #process selected
        if request.method=="POST":
            entries = request.POST.getlist('selected')
            if 'New' in request.POST:
                for uid in entries:
                    sale = SalesOrder.objects.get(pk=uid)
                    if not sale.status == 'new':
                        sale.status = 'new'
                        sale.save()

            elif 'Shipped' in request.POST:
                for uid in entries:
                    sale = SalesOrder.objects.get(pk=uid)
                    if not sale.status == 'shipped':
                        sale.status = 'shipped'
                        sale.save()

            elif 'Completed' in request.POST:
                for uid in entries:
                    sale = SalesOrder.objects.get(pk=uid)
                    if not sale.status == 'completed':
                        sale.status = 'completed'
                        sale.save()

            elif 'Cancelled' in request.POST:
                for uid in entries:
                    sale = SalesOrder.objects.get(pk=uid)
                    if not sale.status == 'cancelled':
                        sale.status = 'cancelled'
                        sale.save()

        #show sales
        context = {
            'heading': ('','ID','Buyer','Address','Order Date', 'Status'),
            'sales': SalesOrder.objects.all(),
            'cart': Cart(request),
        }
        return render(request, "all_sales.html", context)

    #Check login standard user
    elif request.user.is_authenticated() and not request.user.is_superuser:
        #show sales
        context = {
            'heading': ('Sales Order ID','Buyer','Address','Order Date', 'Status'),
            'sales': SalesOrder.objects.filter(buyer=request.user),
            'cart': Cart(request),
        }
        return render(request, "all_sales.html", context)

    #Redirect to home
    else:
        return redirect("/")

def sales_details(request, s_id):
    #Check login superuser
    if request.user.is_authenticated() and request.user.is_superuser:
        try:
            sale = SalesOrder.objects.get(pk=s_id)
            #process selected
            if request.method=="POST":
                if 'New' in request.POST:
                    if not sale.status == 'new':
                        sale.status = 'new'
                        sale.save()

                elif 'Shipped' in request.POST:
                    if not sale.status == 'shipped':
                        sale.status = 'shipped'
                        sale.save()

                elif 'Completed' in request.POST:
                    if not sale.status == 'completed':
                        sale.status = 'completed'
                        sale.save()

                elif 'Cancelled' in request.POST:
                    if not sale.status == 'cancelled':
                        sale.status = 'cancelled'
                        sale.save()

        except SalesOrder.DoesNotExist:
            print 'HEREEEEEEEEEEEEEEEEE44444444444444444444'
            # Return an error message.
            context = {
                'heading': 'Error',
                'feedback': 'This sale does not exist',
                'cart': Cart(request),
            }
            return render(request, "feedback.html", context)

        #show orders
        context = {
            'heading': ('Product','Quantity','Price','Type','Total'),
            'sale': sale,
            'items': OrderItem.objects.filter(order=SalesOrder.objects.get(pk=s_id)),
            'cart': Cart(request),
        }
        return render(request, "sales_details.html", context)

    #Check login standard user
    elif request.user.is_authenticated() and not request.user.is_superuser:
        try:
            #show orders
            context = {
                'heading': ('Product','Quantity','Price','Type','Total'),
                'sale': SalesOrder.objects.get(pk=s_id, buyer=request.user),
                'items': OrderItem.objects.filter(order=SalesOrder.objects.get(pk=s_id)),
                'cart': Cart(request),
            }
            return render(request, "sales_details.html", context)
        except SalesOrder.DoesNotExist:
            # Return an error message.
            context = {
                'heading': 'Error',
                'feedback': 'This sale does not exist',
                'cart': Cart(request),
            }
            return render(request, "feedback.html", context)

    #Redirect to home
    else:
        return redirect("/")
