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
    quantity = forms.IntegerField(initial=1, required=False)
    update = forms.BooleanField(required=False, initial=True)


class LoginForm(forms.Form):
    username = forms.CharField(label='Username', required=True)
    password = forms.CharField(label='Password', required=True, widget=forms.PasswordInput())


class CustomRegistrationForm(RegistrationFormUniqueEmail, RegistrationFormTermsOfService):
    pass

class EditCredentialsForm(forms.Form):
    firstName = forms.CharField(label='First Name')
    lastName = forms.CharField(label='Last Name')
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
