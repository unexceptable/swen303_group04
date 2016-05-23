from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect
from web_shop.forms import (
    SearchForm, LoginForm, EditCredentialsForm, CartForm,
    ChatForm, MessageForm, AddressForm, SortTypeForm,
    ItemsPerPageForm, ContactForm, ImageForm, ProductForm,
    EditProductForm, CategoryForm, EditCategoryForm,
    CustomRegistrationForm)
from .models import (
    Product, Category, ChatHistory, Address, SalesOrder,
    OrderItem, Contact, WishList, WishListItem, Tag,
    Notification, Image)
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from cart.cart import Cart
from django.http import HttpResponseRedirect, HttpResponse
from django.core.paginator import Paginator
import operator
from django.forms import formset_factory
from itertools import chain


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
    keywords = search.split()
    # This is an AWFUL search... but at least something to start with.

    tags = Tag.objects.filter(
        reduce(operator.and_, (Q(name__icontains=x) for x in keywords)))

    if request.user.is_superuser:
        products = Product.objects.filter(
            (Q(reduce(operator.and_, (Q(name__icontains=x) for x in keywords))) | Q(tags__in=tags)),
        ).distinct()
    else:
        products = Product.objects.filter(
            (Q(reduce(operator.and_, (Q(name__icontains=x) for x in keywords))) | Q(tags__in=tags)),
            visible=True).distinct()

    context = {
        'search': form.data["search"],
        'products': products,
        'cart': Cart(request),
    }

    #sorting stuff
    sort_type=""
    if request.method=="GET":
        sort_type=request.GET.get('sort_type')

        if sort_type:
            if sort_type=='A-Z':
                products=products.order_by('name')
            elif sort_type=='Z-A':
                products=products.order_by('-name')
            elif sort_type=="Lowest Price":
                products=products.order_by('price')
            elif sort_type=="Highest Price":
                products=products.order_by('-price')
        else:
            products=products.order_by('name')

        context.update({'products':products})
        context.update({'sort_type':sort_type})

    return render(request, "products.html", context)


def add_product(request):
    ImageFormSet = formset_factory(
        form=ImageForm, extra=5)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        imgformset = ImageFormSet(request.POST, request.FILES)

        if form.is_valid() and imgformset.is_valid():
            tags = []
            for tag in form.cleaned_data['tags']:
                try:
                    tags.append(Tag.objects.get(name=tag))
                except Tag.DoesNotExist:
                    _tag = Tag(name=tag)
                    _tag.save()
                    tags.append(_tag)

            product = Product(
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'],
                price=form.cleaned_data['price'],
                visible=form.cleaned_data['visible'],
                category=Category.objects.get(
                    pk=form.cleaned_data['category']),
                thumbnail=form.cleaned_data['thumbnail'],
                main_image=form.cleaned_data['main_image'],
            )
            product.save()
            product.tags.add(*tags)

            for imgform in imgformset.cleaned_data:
                try:
                    image = imgform['image']
                    image = Image(product=product, image=image)
                    image.save()
                except KeyError:
                    pass
            return redirect("/product/%s" % product.pk)
        else:
            print (form.errors, imgformset.errors)
    else:
        form = ProductForm()
        imgformset = ImageFormSet()
    return render(
        request, 'product_add.html',
        {'form': form, 'imgformset': imgformset})


def edit_product(request, p_id):
    try:
        product = Product.objects.get(pk=p_id)
        images = product.image_set.all()

        ImageFormSet = formset_factory(
            form=ImageForm, extra=5)

        if request.method == 'POST':
            form = EditProductForm(request.POST, request.FILES)
            imgformset = ImageFormSet(request.POST, request.FILES)

            if form.is_valid() and imgformset.is_valid():
                tags = []
                for tag in form.cleaned_data['tags']:
                    try:
                        tags.append(Tag.objects.get(name=tag))
                    except Tag.DoesNotExist:
                        _tag = Tag(name=tag)
                        _tag.save()
                        tags.append(_tag)

                product.name = form.cleaned_data['name']
                product.description = form.cleaned_data['description']
                product.price = form.cleaned_data['price']
                product.visible = form.cleaned_data['visible']
                product.category = Category.objects.get(
                    pk=form.cleaned_data['category'])
                if form.cleaned_data['thumbnail']:
                    product.thumbnail = form.cleaned_data['thumbnail']
                if form.cleaned_data['main_image']:
                    product.main_image = form.cleaned_data['main_image']
                product.save()
                product.tags.clear()
                product.tags.add(*tags)

                for imgform in imgformset.cleaned_data:
                    try:
                        image = imgform['image']
                        image = Image(product=product, image=image)
                        image.save()
                    except KeyError:
                        pass
                return redirect("/product/%s" % product.pk)
        else:
            form = EditProductForm({
                'name': product.name,
                'description': product.description,
                'price': product.price,
                'visible': product.visible,
                'category': product.category.pk,
            })
            imgformset = ImageFormSet()

        context = {
            'product': product,
            'tags': product.tags.all(),
            'images': images,
            'form': form,
            'imgformset': imgformset,
            'cart': Cart(request),
        }
        return render(request, "product_edit.html", context)

    except Product.DoesNotExist:
        return render(
            request, '404.html',
            {
                'username': request.user.username,
                'errorMessage':
                    'The product with the id ' + p_id + ' does not exist',
                'cart': Cart(request),
            })


def delete_image(request, img_id):
    if request.user.is_superuser:
        try:
            img = Image.objects.get(pk=img_id)
            img.delete()
            return HttpResponse("Image Deleted")
        except Image.DoesNotExist:
            return HttpResponse("Image does not exist.")
    else:
        return HttpResponse("nope")


def product_detail(request, p_id):
    # here we need to get the product via the id

    try:
        product = Product.objects.get(pk=p_id)
        if not product.visible and not request.user.is_superuser:
            raise Product.DoesNotExist

        form = CartForm()

        images = product.image_set.all()

        in_cart = 0
        cart = Cart(request)
        for item in cart:
            if item.product.pk == product.pk:
                in_cart = item.quantity

        if request.user.is_authenticated():
            try:
                wishlist = WishList.objects.get(user=request.user)
                product = Product.objects.get(pk=p_id)
                item = WishListItem.objects.get(wishlist=wishlist, object_id=product.pk)
                if item:
                    on_wishlist = True
            except (WishList.DoesNotExist, WishListItem.DoesNotExist):
                on_wishlist = False
        else:
            on_wishlist = False

        context = {
            'product': product,
            'tags': product.tags.all(),
            'images': images,
            'in_cart': in_cart,
            'on_wishlist': on_wishlist,
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

    next = request.POST.get('next')
    if next:
        return redirect(next)
    else:
        return redirect("/product/%s" % product.pk)


def product_wishlist(request, p_id):
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

    if not request.user.is_authenticated():
        return redirect("/product/%s" % p_id)

    try:
        wishlist = WishList.objects.get(user=request.user)
    except WishList.DoesNotExist:
        wishlist = WishList(user=request.user)
        wishlist.save()

    try:
        wishlist = WishList.objects.get(user=request.user)
        product = Product.objects.get(pk=p_id)
        item = WishListItem.objects.get(wishlist=wishlist, object_id=product.pk)
        item.delete()
    except WishListItem.DoesNotExist:
        item = WishListItem(wishlist=wishlist, product=product)
        item.save()

    return redirect("/product/%s" % p_id)


def register(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CustomRegistrationForm(request.POST)
        # check whether it's valid:

        next = request.POST.get('next', None)

        if form.is_valid():
            # process the data in form.cleaned_data as required      

            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email']
            )
            user.save()
            user = authenticate(
                username=user.username,
                password=form.cleaned_data['password1'])

            login(request, user)
            # Redirect to home
            print next
            if next and next != "/register/":
                return redirect(next)
            else:
                return redirect("/")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = CustomRegistrationForm()
        next = request.GET.get('next', None)    

    return render(
        request, 'registration_form.html',
        {
            'next': next,
            'form': form,
            'cart': Cart(request),
        })


def signin(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = LoginForm(request.POST)
        # check whether it's valid:

        next = request.POST.get('next', None)

        if form.is_valid():
            # process the data in form.cleaned_data as required
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    # Redirect to home
                    print next
                    if next:
                        return redirect(next)
                    else:
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
        next = request.GET.get('next', None)    

    return render(
        request, 'login.html',
        {
            'next': next,
            'username': request.user.username,
            'form': form,
            'cart': Cart(request),
        })


def category_view(request, category_name):
    try:
        if(category_name == 'all'):
            category_list = Category.objects.filter(parent=None)
            context = {
                'category': category_name,
                'categories': category_list,
                'cart': Cart(request),
            }

        else:
            c = Category.objects.get(name=category_name)
            sub_cat_list = c.children
            if request.user.is_superuser:
                product_list = c.product_set.all()
            else:
                product_list = c.product_set.filter(visible=True)
            context = {
                'category': c,
                'subcategories': sub_cat_list,
                'product_list': product_list,
                'cart': Cart(request),
                'parent_path': c.get_parent_path,
                'last_cat': c.get_parent_path[-1]
            }



            #initial sorting values
            display_type = 'box'
            sort_type = 'AtoZ'
            items_per_page = '24'

            if request.method == "GET":
                sort_type = request.GET.get('sortBy')
                items_per_page = request.GET.get('nItems')
                display_type = request.GET.get('view')
                page_num = request.GET.get('page_num')
                min_price = request.GET.get('minPrice')
                max_price = request.GET.get('maxPrice')

                #product view
                if display_type:
                    display_type = request.GET.get('view')
                else:
                    display_type = 'box'

                #get products of children categories
                product_list = get_all_products(sub_cat_list, product_list)
                #sort the products
                if sort_type:
                    if sort_type == 'AtoZ':
                        #product_list.sort()
                        product_list= product_list.extra(select={'case_insensitive_name': 'lower(name)'}).order_by('case_insensitive_name')
                    elif sort_type == 'ZtoA':
                        product_list= product_list.extra(select={'case_insensitive_name': 'lower(name)'}).order_by('-case_insensitive_name')
                    elif sort_type == 'priceLow':
                        product_list= product_list.order_by('price')
                    elif sort_type == 'priceHigh':
                        product_list= product_list.order_by('-price')
                else:
                    product_list= product_list.extra(select={'case_insensitive_name': 'lower(name)'}).order_by('case_insensitive_name')

                #highest cost item
                highest_price = product_list.order_by('-price')[0].price

                #if min_price and max_price:
                    #filter out all products below
                #    product_list = product_list.filter(price__lt=min_price, price__gt=max_price)
                if max_price:
                    #filter out all products above
                    product_list = product_list.filter(price__lt=max_price)
                if min_price:
                    product_list = product_list.filter(price__gt=min_price)

                # number of pages
                if items_per_page:
                    print(items_per_page)
                    if items_per_page == 'all':
                        items_per_page = len(product_list)
                        print(len(product_list))

                    if page_num:
                        p = Paginator(product_list, items_per_page)
                        num_pages = p.num_pages
                        current_page = p.page(page_num)
                        product_list = current_page.object_list
                        print(num_pages)
                        context.update({'num_pages': num_pages})
                        context.update({'path': request.get_full_path() })
                        context.update({'p': p})
                        context.update({'current_page':current_page})
                    else:
                        page_num = 1
                        p = Paginator(product_list, items_per_page)
                        num_pages = p.num_pages
                        current_page = p.page(page_num)
                        product_list = current_page.object_list
                        print(num_pages)
                        context.update({'num_pages': num_pages})
                        context.update({'path': request.get_full_path() })
                        context.update({'p': p})
                        context.update({'current_page':current_page})



                context.update({'highest_price': highest_price})
                context.update({'display_type': display_type})
                context.update({'items_per_page': items_per_page})
                context.update({'sort_type': sort_type})
                context.update({'product_list': product_list})
                context.update({'display_type': display_type})
                context.update({'page_num': page_num})
                context.update({'min_price': min_price})
                context.update({'max_price': max_price})
            #elif request.method == "POST":

        return render(request, "category_view.html", context)
    except Category.DoesNotExist:
        return render(
            request, '404.html',
            {
                'errorMessage':
                    'That category does not exist',
                'cart': Cart(request),
            })

def get_all_products(subcat_list, product_list):
    if subcat_list:
        res = []
        for category in subcat_list:
            #product_list = list(chain(get_all_products(category.children, product_list), category.product_set.all()))
            product_list = get_all_products(category.children, product_list) | category.product_set.all()
        return product_list
    else:
        return product_list

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

            if User.objects.filter(username=form.data["chat"]).exists():
                context = {
                    'user': form.data["chat"],
                    'form' : MessageForm(initial={'to': form.data["chat"]})
                }
                return render(request, "chat.html", context)
            else:
                # Return an error message.
                context = {
                    'heading': 'Error',
                    'feedback': 'User does not exist',
                    'cart': Cart(request),
                }
                return render(request, "feedback.html", context)

        #Process data sent
        else:
            form = MessageForm(request.POST)
            if form.is_valid():
                if User.objects.filter(username=request.POST['to']).exists():
                    #create message
                    ChatHistory.objects.create(origin=request.user.username, to= request.POST['to'], message=request.POST['message'])
                    #create notif if not exist
                    if not Notification.objects.filter(to = User.objects.get(username=request.POST['to']), notif = 'Message from '+request.user.username):
                        Notification.objects.create(
                            to = User.objects.get(username=request.POST['to']),
                            notif = 'Message from '+request.user.username,
                            link = '/chat?chat='+request.user.username
                            )
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


def edit_address(request, uid):
    #Check login
    if request.user.is_authenticated():
        if Address.objects.get(pk=uid).user == request.user or request.user.is_superuser:
            # if this is a GET request we need to pre-fill AddressForm
            if request.method == 'GET':
                #in DB
                try:
                    entry = Address.objects.get(pk=uid)
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
                    # Return an error message.
                    context = {
                        'heading': 'Error',
                        'feedback': 'Page does not exist',
                        'cart': Cart(request),
                    }
                    return render(request, "feedback.html", context)

            #Process data sent
            else:
                form = AddressForm(request.POST)
                if form.is_valid():
                    #in DB
                    try:
                        entry = Address.objects.get(pk=uid)
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
                            'feedback': entry.user.username+' has updated billing address with ID'+
                                    str(entry.pk)+' to '+
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
                        # Return an error message.
                        context = {
                            'heading': 'Error',
                            'feedback': 'Page does not exist',
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
            # Return an error message.
            context = {
                'heading': 'Error',
                'feedback': 'Page does not exist',
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

        if not cart.count():
            return redirect("/cart")

        addresses = request.user.address_set.filter(visible=True)
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
        address_id = request.POST.get('address', None)       

        try:
            address = request.user.address_set.get(pk=address_id)
        except (Address.DoesNotExist, ValueError):
            cart = Cart(request)
            addresses = request.user.address_set.filter(visible=True)
            try:
                default = request.user.address_set.get(default=True)
            except Address.DoesNotExist:
                default = None

            context = {
                'address_error': True,
                'cart': cart,
                'addresses': addresses,
                'default': default,
            }

            return render(request, 'checkout.html', context)

        cart = Cart(request)

        order = SalesOrder(buyer=request.user, address=address)
        order.save()
        
        #create notif if not exist
        if not Notification.objects.filter(to = User.objects.get(username='admin'), notif = 'Sales order from '+request.user.username):
            Notification.objects.create(
                to = User.objects.get(username='admin'),
                notif = 'Sales order from '+request.user.username,
                link = '/sales-details/'+str(order.pk)
                )

        for item in cart:
            order_item = OrderItem(
                order=order, quantity=item.quantity,
                unit_price=item.unit_price, product=item.product)
            order_item.save()

        cart.clear()

        return render(
            request, 'checkedout.html',
            {'order': order})


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

def contact(request):
    #Check login
    if request.user.is_authenticated() and request.method == 'GET':
        # if this is a GET request we need to pre-fill ContactForm
        form = ContactForm(initial={
            'email':request.user.email,
            'message_type': 'general'
            })
        context = {
            'form': form,
            'cart': Cart(request),
        }
        return render(request, "contact.html", context)

    #not logged in
    elif not request.user.is_authenticated() and request.method == 'GET':
        context = {
            'form': ContactForm(initial={'message_type': 'general'}),
            'cart': Cart(request),
        }
        return render(request, "contact.html", context)

    #process data sent
    elif request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            newInstance = Contact.objects.create(
            subject=form.cleaned_data['subject'],
            message_type=form.cleaned_data['message_type'],
            message=form.cleaned_data['message'],
            email=form.cleaned_data['email'],
            status = 'open',
            )
            
            #create notif if not exist
            if not Notification.objects.filter(to = User.objects.get(username='admin'), notif = 'Support ticket from '+request.user.username):
                Notification.objects.create(
                    to = User.objects.get(username='admin'),
                    notif = 'Support ticket from '+request.user.username,
                    link = '/listcontacts/'
                    )

            # Return ok.
            context = {
                'heading': 'Enquiry sent',
                'feedback': 'We will contact you in the email  '+
                        form.cleaned_data['email']+'. Check your inbox',
                'cart': Cart(request),
            }
            return render(request, "feedback.html", context)
        else:
            # Return an error message.
            context = {
                'heading': 'Error',
                'feedback': 'All fields are required and a valid email must be supplied',
                'cart': Cart(request),
            }
            return render(request, "feedback.html", context)

    else:
        # Redirect to home
        return redirect("/")

def wishlist(request):
    if not request.user.is_authenticated():
        return redirect("/")

    try:
        wishlist = WishList.objects.get(user=request.user)
        context = {
            'items': WishListItem.objects.filter(wishlist=wishlist),
            'cart': Cart(request),
        }
        return render(request, "wishlist.html", context)
    except WishList.DoesNotExist:
        wishlist = WishList(user=request.user)
        wishlist.save()

        context = {
            'items': [],
            'cart': Cart(request),
        }
        return render(request, "wishlist.html", context)


def wishlist_update(request, p_id):
    if not request.user.is_authenticated():
        return redirect("/")

    try:
        wishlist = WishList.objects.get(user=request.user)
        product = Product.objects.get(pk=p_id)
        item = WishListItem.objects.get(wishlist=wishlist, object_id=product.pk)
        item.delete()
        return redirect("/wishlist")
    except (WishList.DoesNotExist, Product.DoesNotExist):
        return redirect("/wishlist")

def wishlist_cart(request, p_id):
    if not request.user.is_authenticated():
        return redirect("/")

    try:
        wishlist = WishList.objects.get(user=request.user)
        product = Product.objects.get(pk=p_id)
        item = WishListItem.objects.get(wishlist=wishlist, object_id=product.pk)
        item.delete()
        Cart(request).add(product, product.price, 1)
        return redirect("/cart")
    except (WishList.DoesNotExist, Product.DoesNotExist):
        return redirect("/wishlist")


def listcontacts(request):
    #Check login
    if request.user.is_authenticated() and request.user.is_superuser:
        #process selected
        if request.method=="POST":
            entries = request.POST.getlist('selected')
            if 'Open' in request.POST:
                for uid in entries:
                    entry = Contact.objects.get(pk=uid)
                    if entry.status == 'close':
                        entry.status = 'open'
                        entry.save()

            elif 'Close' in request.POST:
                for uid in entries:
                    entry = Contact.objects.get(pk=uid)
                    if entry.status == 'open':
                        entry.status = 'close'
                        entry.save()

        #show users
        context = {
            'heading': ('','Subject','Type','Message', 'Email', 'Status'),
            'contacts': Contact.objects.all(),
            'cart': Cart(request),
        }
        return render(request, "all_contacts.html", context)

    else:
        return redirect("/")

"""
    This function handles 'delete' and display
"""
def listaddresses(request):
    #Check login
    if not request.user.is_authenticated():
        return redirect("/")
    #process selected
    if request.method=="POST":
        entries = request.POST.getlist('selected')
        if 'Delete' in request.POST:
            for uid in entries:
                entry = Address.objects.get(pk=uid)
                if request.user.is_superuser or request.user == entry.user:
                    entry.visible = False
                    entry.default = False
                    entry.save()
        elif 'Add New Address' in request.POST:
            return redirect('/addaddress/')

    addresses = Address.objects.filter(user=request.user, visible=True)

    #show addresses
    context = {
        'heading': ('','User','Default','Address', 'Update', 'Set to Default'),
        'addresses': addresses,
        'cart': Cart(request),
    }
    return render(request, "all_addresses.html", context)


def default_address(request,uid):
    #Check login
    if not request.user.is_authenticated():
        return redirect("/")

    if Address.objects.get(pk=uid).user == request.user or request.user.is_superuser:
        if request.method == 'GET':
            entry = Address.objects.get(pk=uid)
            addresses = Address.objects.filter(user=entry.user,default=True)

            for address in addresses:
                address.default=False
                address.save()


            entry.default = True
            entry.save()
            return redirect("/listaddresses")
        else:
            # Return an error message.
            context = {
                'heading': 'Error',
                'feedback': 'Page does not exist',
                'cart': Cart(request),
            }
            return render(request, "feedback.html", context)
    else:
        # Return an error message.
        context = {
            'heading': 'Error',
            'feedback': 'Page does not exist',
            'cart': Cart(request),
        }
        return render(request, "feedback.html", context)


def add_address(request):
    #Check login
    if not request.user.is_authenticated():
        return redirect("/")

    #blank form
    if request.method == 'GET':
        next = request.GET.get('next', None)
        context = {
            'next': next,
            'form': AddressForm(),
            'cart': Cart(request),
        }
        return render(request, "add_address.html", context)

    #Process data sent
    else:
        form = AddressForm(request.POST)
        if form.is_valid():
            addresses = Address.objects.filter(user=request.user, visible=True)

            default = True
            if addresses:
                default= False

            Address.objects.create(
            user=request.user,
            default=default,
            number_street=form.cleaned_data['number_street'],
            suburb=form.cleaned_data['suburb'],
            city=form.cleaned_data['city'],
            region=form.cleaned_data['region'],
            country=form.cleaned_data['country'],
            postcode=form.cleaned_data['postcode'],
            )
            next = request.POST.get('next', None)
            if next:
                return redirect(next)
            else:
                return redirect("/listaddresses")
        else:
            next = request.POST.get('next', None)
            context = {
                'next': next,
                'heading': 'Error',
                'feedback': 'All fields must be filled and postcode must be between 1000 to 9999 (inclusive)',
                'cart': Cart(request),
            }
            return render(request, "feedback.html", context)

def listnotifications(request):
    #Check login
    if not request.user.is_authenticated():
        return redirect("/")

    #process selected
    if request.method=="POST":
        entries = request.POST.getlist('selected')
        if 'Clear Selected' in request.POST:
            for uid in entries:
                entry = Notification.objects.get(pk=uid)
                if request.user == entry.to:
                    entry.delete()

    #show notifs
    #Notifications variable passed in globally,do not fetch
    #heading has 'select all checkbox'
    context = {
        'heading': ('Description','Link'),
        'cart': Cart(request),
    }
    return render(request, "all_notifications.html", context)

def listcategories(request):
    #Check login
    if not request.user.is_authenticated() or not request.user.is_superuser:
        return redirect("/")

    #process selected
    if request.method=="POST":
        entries = request.POST.getlist('selected')
        if 'Delete' in request.POST:
            for uid in entries:
                entry = Category.objects.get(pk=uid)
                entry.delete()

        elif 'Add New Category' in request.POST:
            return redirect('/addcategory/') 
            
    categories = Category.objects.all()
    #show addresses
    context = {
        'heading': ('','Name','Image','Main Category', 'Children', 'Update'),
        'categories': categories,
        'cart': Cart(request),
    }
    return render(request, "all_categories.html", context)

def edit_category(request,uid):
    #Check login
    if not request.user.is_authenticated() or not request.user.is_superuser:
        return redirect("/")

    try:
        entry = Category.objects.get(pk=uid)
        #process selected
        if request.method=="POST":
            form = EditCategoryForm(request.POST, request.FILES)
            if form.is_valid():
                entry.name = form.cleaned_data['name']
                if request.FILES['main_image']:
                    entry.main_image = request.FILES['main_image']

                if form.cleaned_data['parent']:
                    entry.parent = Category.objects.get(name=form.cleaned_data['parent'])
                else:
                    entry.parent = None

                entry.save()
                # Return ok.
                context = {
                    'heading': 'Success',
                    'feedback': 'Category with ID '+str(entry.pk)+' has now been updated to '+entry.name+' with parent '+str(entry.parent),
                    'cart': Cart(request),
                }
                return render(request, "feedback.html", context)
            else:
                # Return an error message.
                context = {
                    'heading': 'Error',
                    'feedback': 'Invalid image or parent category',
                    'cart': Cart(request),
                }
                return render(request, "feedback.html", context)
        #pre-fill
        else:
            form = EditCategoryForm({
                'name': entry.name,
                'main_image': entry.main_image,
                'parent': entry.parent,
            })
            context = {
                'main_image':entry.main_image,
                'form': form,
                'cart': Cart(request),
            }
            return render(request, "edit_category.html", context)
    except Category.DoesNotExist:
        # Return an error message.
        context = {
            'heading': 'Error',
            'feedback': 'Page does not exist',
            'cart': Cart(request),
        }
        return render(request, "feedback.html", context)

def add_category(request):
    #Check login
    if not request.user.is_authenticated() or not request.user.is_superuser:
        return redirect("/")

    #process selected
    if request.method=="POST":
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():

            parent = None
            if form.cleaned_data['parent'] and Category.objects.filter(name=form.cleaned_data['parent']).exists():
                parent = Category.objects.get(name=form.cleaned_data['parent'])

            Category.objects.create(
            name=form.cleaned_data['name'],
            main_image=request.FILES['main_image'],
            parent=parent,
            )

            # Return ok.
            context = {
                'heading': 'Success',
                'feedback': 'New category '+form.cleaned_data['name']+' with parent(s) '+str(parent),
                'cart': Cart(request),
            }
            return render(request, "feedback.html", context)
        else:
            # Return an error message.
            context = {
                'heading': 'Error',
                'feedback': 'Image field and name field must be filled',
                'cart': Cart(request),
            }
            return render(request, "feedback.html", context)

    #display form
    else:
        form = CategoryForm()
        context = {
            'form': form,
            'cart': Cart(request),
        }
        return render(request, "add_category.html", context)
