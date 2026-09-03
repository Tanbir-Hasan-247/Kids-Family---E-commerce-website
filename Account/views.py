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



from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# আপনার প্রজেক্টের স্ট্রাকচার অনুযায়ী ইম্পোর্টগুলো ঠিক করে নেবেন
from Order.models import Order 
from Wishlist.models import FavoriteItem 

# Helper function (যদি আগে থেকে ইম্পোর্ট করা না থাকে)
def get_user_identity(request):
    if request.user.is_authenticated:
        return {'user': request.user}
    
    if not request.session.session_key:
        request.session.create()
    return {'session_key': request.session.session_key}

# ==========================================
# DASHBOARD VIEW
# ==========================================
@login_required
def dashboard_view(request):
    identity = get_user_identity(request)

    # ১. টোটাল অর্ডার কাউন্ট
    total_orders = Order.objects.filter(**identity).count()

    # ২. পেন্ডিং/প্রসেসিং অর্ডার কাউন্ট (pending, confirmed, processing)
    pending_orders = Order.objects.filter(
        **identity, 
        status__in=['pending', 'confirmed', 'processing']
    ).count()

    # ৩. উইশলিস্ট কাউন্ট
    wishlist_count = FavoriteItem.objects.filter(**identity).count()

    # ৪. রিসেন্ট অর্ডার (সর্বশেষ ৪টি অর্ডার)
    recent_orders = Order.objects.filter(**identity).order_by('-created_at')[:4]

    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'wishlist_count': wishlist_count,
        'recent_orders': recent_orders,
    }

    return render(request, 'dashboard.html', context)