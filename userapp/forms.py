from django.contrib.auth.forms import AuthenticationForm
from userapp.models import MyUser

class LoginForm(AuthenticationForm):
    class Meta:
        model = MyUser