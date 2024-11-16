import django.forms as forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm

# from django.contrib.auth.models import User
from .models import Profile, Skills, User

class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ['user', 'is_active']
        widgets = {}
        
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        
        for name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full bg-gray-100 bg-opacity-50 rounded border border-gray-300 focus:border-red-500 focus:bg-transparent focus:ring-2 focus:ring-red-200 text-xl outline-none text-gray-700 py-1 px-3 leading-8 transition-colors duration-200 ease-in-out'
            })


class SkillForm(ModelForm):
    class Meta:
        model = Skills
        fields = ['name', 'level', 'bg_color', 'fg_color']
        widgets = {
            'level' : forms.NumberInput(
                attrs={
                    'min': 1,
                    'max': 10
                }),
            'bg_color': forms.TextInput(
                attrs={
                    'type': 'color'
                }),
            'fg_color': forms.TextInput(
                attrs={
                    'type': 'color'
                }),
            }
        
    
    def __init__(self, *args, **kwargs):
        super(SkillForm, self).__init__(*args, **kwargs)
        
        for name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full bg-gray-100 bg-opacity-50 rounded border border-gray-300 focus:border-red-500 focus:bg-transparent focus:ring-2 focus:ring-red-200 text-base outline-none text-gray-700 py-1 px-3 leading-8 transition-colors duration-200 ease-in-out'
            })


class UserRegistrationForm(UserCreationForm):
    
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email"]
        widgets = {
          'email' : forms.TextInput(
            attrs={
              'type': 'email'
            })
        }

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'w-full bg-gray-100 bg-opacity-50 rounded border border-gray-300 focus:border-red-500 focus:bg-transparent focus:ring-2 focus:ring-red-200 text-base outline-none text-gray-700 py-1 px-3 leading-8 transition-colors duration-200 ease-in-out'})