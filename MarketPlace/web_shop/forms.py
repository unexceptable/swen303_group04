from django import forms


class ProductForm(forms.Form):
    # need to check that the name is only spaces or alpha-num or spaces
    name = forms.CharField(max_length=100, required=True)
    desciption = forms.CharField(required=True)
    price = forms.DecimalField(required=True,  max_digits=20, decimal_places=2)
    visible = forms.BooleanField()


class SearchForm(forms.Form):
    search = forms.CharField(required=True)
