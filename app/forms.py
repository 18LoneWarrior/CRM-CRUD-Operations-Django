from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.forms import ModelChoiceField
from django.urls import reverse, reverse_lazy
from .models import Record, Person, City, Country, State


class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="",
                             widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    first_name = forms.CharField(label="", max_length=100,
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(label="", max_length=100,
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'User Name'
        self.fields['username'].label = ''
        self.fields[
            'username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password1'].label = ''
        self.fields[
            'password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['password2'].label = ''
        self.fields[
            'password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'


# Create a new record form
class AddRecordForm(forms.ModelForm):
    first_name = forms.CharField(required=True, widget=forms.widgets.TextInput(
        attrs={'placeholder': 'First Name', 'class': 'form-control'}), label='')
    last_name = forms.CharField(required=True, widget=forms.widgets.TextInput(
        attrs={'placeholder': 'Last Name', 'class': 'form-control'}), label='')
    email = forms.CharField(required=True, widget=forms.widgets.TextInput(
        attrs={'placeholder': 'Email', 'class': 'form-control'}), label='')
    phone = forms.CharField(required=True, widget=forms.widgets.TextInput(
        attrs={'placeholder': 'Phone No', 'class': 'form-control'}), label='')
    address = forms.CharField(required=True, widget=forms.widgets.TextInput(
        attrs={'placeholder': 'Address', 'class': 'form-control'}), label='')
    city = forms.CharField(required=True,
                           widget=forms.widgets.TextInput(attrs={'placeholder': 'City', 'class': 'form-control'}),
                           label='')
    state = forms.CharField(required=True, widget=forms.widgets.TextInput(
        attrs={'placeholder': 'State', 'class': 'form-control'}), label='')
    zipcode = forms.CharField(required=True, widget=forms.widgets.TextInput(
        attrs={'placeholder': 'Zipcode', 'class': 'form-control'}), label='')

    class Meta:
        model = Record
        exclude = ('user',)


class UploadRecord(forms.Form):
    class Meta:
        model = Record
        fields = '__all__'


class RecordSearchForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = ['city', 'state']

    city = forms.ModelChoiceField(queryset=Record.objects.values_list
    ('city', flat=True).distinct(), empty_label="--_--", required=False)
    state = forms.ModelChoiceField(queryset=Record.objects.values_list
    ('state', flat=True).distinct(), empty_label="--_--", required=False)


class PersonSearchForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['state', 'city']

    state = forms.ModelChoiceField(queryset=State.objects.all(), empty_label="--_--", required=False)
    city = forms.ModelChoiceField(queryset=City.objects.none(), empty_label="--_--", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['city'].queryset = City.objects.none()

        # Add HTMX attributes to the form fields
        self.fields['state'].widget.attrs['hx-get'] = reverse_lazy('admin:city_choices')
        self.fields['state'].widget.attrs['hx-target'] = '#id_city'
        self.fields['state'].widget.attrs['hx-swap'] = 'innerHTML'
