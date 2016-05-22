from django import forms
from registration.forms import RegistrationFormUniqueEmail
from registration.forms import RegistrationFormTermsOfService

class ProductForm(forms.Form):
    # need to check that the name is only spaces or alpha-num or spaces
    name = forms.CharField(max_length=100, required=True)
    desciption = forms.CharField(required=True)
    price = forms.DecimalField(required=True, max_digits=20, decimal_places=2)
    visible = forms.BooleanField()


class SearchForm(forms.Form):
    search = forms.CharField(required=True)


class CartForm(forms.Form):
    quantity = forms.IntegerField(initial=1, required=False, min_value=0)
    update = forms.BooleanField(required=False, initial=True)


class LoginForm(forms.Form):
    username = forms.CharField(label='Username', required=True)
    password = forms.CharField(label='Password', required=True, widget=forms.PasswordInput())


class CustomRegistrationForm(RegistrationFormUniqueEmail, RegistrationFormTermsOfService):
    pass

class EditCredentialsForm(forms.Form):
    firstName = forms.CharField(label='First Name', required=False)
    lastName = forms.CharField(label='Last Name', required=False)
    email = forms.EmailField(label='Email*', required=True)

    oldPass = forms.CharField(label='Current Password*', required=True, widget=forms.PasswordInput())

    newPass = forms.CharField(label='New Password', required=False, widget=forms.PasswordInput())
    retypeNewPass = forms.CharField(label='Retype New Password', required=False, widget=forms.PasswordInput())

    def clean(self):
        password1 = self.cleaned_data.get('newPass')
        password2 = self.cleaned_data.get('retypeNewPass')

        if (password1) and (password1 != password2):
            raise forms.ValidationError("New password don't match")

        return self.cleaned_data

class ChatForm(forms.Form):
    chat = forms.CharField(required=True)

class MessageForm(forms.Form):
    to = forms.CharField(widget=forms.HiddenInput())
    message = forms.CharField(widget=forms.Textarea, required=True)

class AddressForm(forms.Form):
    number_street = forms.CharField(label='House number and street name', required=True)
    suburb = forms.CharField(required=True)
    city = forms.CharField(required=True)
    region = forms.CharField(required=True)
    country = forms.CharField(required=True)
    postcode = forms.CharField(required=True)

class ContactForm(forms.Form):
	subject = forms.CharField(required=True)
	types = (
				('refunds', 'Refund and Cancellation'),
				('missing', 'Where is my stuff?'),
				('violation', 'Report violation of Terms of Service'),
				('phishing', 'Report a phishing incident'),
				('general', 'Report general issue'),
			)
	message_type = forms.CharField(label='Type',widget=forms.Select(choices=types))
	message = forms.CharField(widget=forms.Textarea, required=True)
	email = forms.EmailField(required=True)


class DisplayTypeForm(forms.Form):
    display_type = forms.ChoiceField(widget=forms.RadioSelect, choices=(("box", "Box"), ("details", "Details"), ("mix", "Mix")))


class SortTypeForm(forms.Form):
    options = (
        ("AtoZ", "A to Z"),
        ("ZtoA", "Z to A"),
        ("priceLow", "Price Low to High"),
        ("priceHigh", "Price High to Low")
        )
    sortType = forms.ChoiceField(widget=forms.Select, choices=options, label="", required=False)

class ItemsPerPageForm(forms.Form):
    options = (
        ("24", "24"),
        ("48", "48"),
        ("72", "72"),
        ("all", "All")
        )
    itemsPerPage = forms.ChoiceField(widget=forms.Select, choices=options, label="", required=False)
