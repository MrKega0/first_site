from django.shortcuts import render
from userapp.forms import LoginForm

# Create your views here.
def login(request):
    login_form = LoginForm()
    context = {'login_form': login_form}
    return render(request, 'userapp/login.html',context)