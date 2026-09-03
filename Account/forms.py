from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
import re

# Apnar custom user model get korar best practice
User = get_user_model()

# Amader premium design er input field classes
INPUT_CLASSES = "w-full bg-paper border border-ink/20 rounded-md px-4 py-3 text-sm text-ink placeholder-ink/35 outline-none focus:border-pine focus:ring-1 focus:ring-pine transition"

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}))
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password'}))

    class Meta:
        model = User
        # Username nai, email hocche main
        fields = ['email', 'phone', 'address']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'you@example.com'}),
            'phone': forms.TextInput(attrs={'placeholder': 'e.g. 017XXXXXXXX'}),
            'address': forms.TextInput(attrs={'placeholder': 'Your full address'}),
        }
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already in use.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter.")
        if not re.search(r'[0-9]', password):
            errors.append("Password must contain at least one digit.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character.")
        if errors:
            raise forms.ValidationError(errors)
        
        return password

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Apnar model e max_length=11 ache, tai ekhane 11 digit er validation dilam
        if phone and not re.match(r'^\d{11}$', phone):
            raise forms.ValidationError("Phone number must be exactly 11 digits.")
        return phone
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        # user.is_active = False # Jodi email verification on rakhte chan
        if commit:
            user.save()
        return user
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Sob field e loop chalaye amader tailwind classes add kore dicchi
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': INPUT_CLASSES})
            field.help_text = None


class LoginForm(AuthenticationForm):
    # AuthenticationForm by default 'username' namer field khoje, amra setake Email type kore dicchi
    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'placeholder': 'you@example.com'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': INPUT_CLASSES})