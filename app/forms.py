

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import CBCReport
from django.core.files.storage import FileSystemStorage
from django.conf import settings

#---------signup model------------------
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name','email','username','password1','password2']

class uploadcbc(forms.ModelForm):
    class Meta:
        model = CBCReport
        fields = ('title' , 'cbcrawfile','description',)
        
  