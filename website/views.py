from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.utils import timezone
from .forms import RegisterForm

def home(request):
    return render(request, 'website/home.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('website:home')

    if request.method == 'POST':
        ip = request.META.get('REMOTE_ADDR', 'unknown')
        attempts = cache.get(f'login_attempts_{ip}', 0)
        if attempts >= 5:
            messages.error(request, 'Demasiados intentos fallidos. Intente más tarde.')
            return render(request, 'website/login.html', {'form': AuthenticationForm()})

        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            cache.set(f'login_attempts_{ip}', 0, 900)
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if not user.is_active:
                    messages.error(request, 'Cuenta deshabilitada.')
                    return render(request, 'website/login.html', {'form': form})
                login(request, user)
                request.session['last_activity'] = timezone.now().isoformat()
                messages.success(request, f'¡Bienvenido de vuelta, {user.first_name or user.username}!')
                return redirect('website:home')
            cache.set(f'login_attempts_{ip}', attempts + 1, 900)
        messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = AuthenticationForm()

    return render(request, 'website/login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('website:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Registro exitoso! Bienvenido a Angelow.')
            return redirect('website:home')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = RegisterForm()

    return render(request, 'website/register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión.')
    return redirect('website:login')

@login_required
def favorites_view(request):
    return render(request, 'website/favorites.html')