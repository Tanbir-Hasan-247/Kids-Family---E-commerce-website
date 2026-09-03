from pyexpat.errors import messages

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth import get_user_model, login, logout
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm, LoginForm
from django.contrib.auth.tokens import default_token_generator
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import UserPassesTestMixin
# Create your views here.
User = get_user_model()


class UserRegistrationView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'signup.html'
    success_url = reverse_lazy('login')
    
    # def dispatch(self, request, *args, **kwargs):
    #     if request.user.is_authenticated:
    #         user = request.user
    #         if user.role == 'agent':
    #             return redirect('agent_dashboard')
    #         if user.role == 'admin' or user.is_superuser:
    #             return redirect('admin_dashboard')
    #         return redirect('home')
        
        # return super().dispatch(request, *args, **kwargs)


class UserLoginView(LoginView):
    form_class = LoginForm
    template_name = 'signin.html'
    
    # def dispatch(self, request, *args, **kwargs):
    #     if request.user.is_authenticated:
    #         user = request.user
    #         if user.role == 'agent':
    #             return redirect('agent_dashboard')
    #         if user.role == 'admin' or user.is_superuser:
    #             return redirect('admin_dashboard')
    #         return redirect('home')
    #     return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        # user = self.request.user
        # if user.role == 'agent':
        #     return reverse_lazy('agent_dashboard')
        # if user.role == 'admin' or user.is_superuser:
        #     return reverse_lazy('admin_dashboard')
        return reverse_lazy('home')


class UserLogoutView(LogoutView):
    next_page = 'home'