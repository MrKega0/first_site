from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from userapp.models import MyUser

class LoginForm(AuthenticationForm):
    class Meta:
        model = MyUser

class RegisterForm(UserCreationForm):
    class Meta:
        model = MyUser
        fields = ["username","email","password1","password2"]