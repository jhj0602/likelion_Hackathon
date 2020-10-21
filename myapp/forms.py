from django import forms
from django.forms import ModelForm, Textarea,TextInput,Select
from .models import CustomUser
from django.contrib.auth.models import User


class UserForm(forms.ModelForm):
    class Meta:
        model = CustomUser

        help_texts = {
            'username': None,
        }
        
        widgets = {
            'name': TextInput(attrs={'placeholder':"Your name.."}),
            'username': TextInput(attrs={'placeholder':"Your Id.."}),
            'password': TextInput(attrs={'placeholder':"Your Password.."}),
            'gender': TextInput(attrs={'placeholder':"Your Id.."}),
            'gender': Select(attrs={'placeholder':"gender.." }),
            'address': Select(attrs={'placeholder':"address.." }),
            'phone_number': TextInput(attrs={'placeholder':"전화번호를 '-'를 제외하고 입력하시오."}),
        }
    
        fields = ['username', 'password', 'name','gender', 'address', 'phone_number',] 
        