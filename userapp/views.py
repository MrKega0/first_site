from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from userapp.forms import LoginForm, RegisterForm
from django.contrib import auth

# Create your views here.
def login(request):
    if request.method == "GET":
        login_form = LoginForm()
    else:
        login_form = LoginForm(data = request.POST)
        if login_form.is_valid():
            user_name = request.POST.get("username")
            user_password = request.POST.get("password")
            user = auth.authenticate(request, username = user_name, password = user_password)
            if user:
                auth.login(request, user)
                return HttpResponseRedirect("/")
    context = {'login_form': login_form}
    return render(request, 'userapp/login.html',context)

def profile(request):

    context = {}
    return render(request,'userapp/profile.html',context)

def registration(request):
    if request.method == "GET":
        register_form = RegisterForm()
    else:
        register_form =  RegisterForm(data = request.POST)
        if register_form.is_valid():
            register_form.save()
            return HttpResponseRedirect("/user/login/")
    context = {'register_form': register_form}
    return render(request, 'userapp/registration.html',context)