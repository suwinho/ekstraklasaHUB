from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, LoginForm
from .utils import fetch_data, fetch_league_table, fetch_last_events

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            team = form.cleaned_data.get('favorite_team')
            
            messages.success(request, f'Konto dla {username} zostało utworzone! Witaj kibicu {team}!')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Błędna nazwa użytkownika lub hasło.')
        else:
            messages.error(request, 'Błąd formularza.')
    else:
        form = LoginForm()
    return render(request, 'index.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'Zostałeś wylogowany.')
    return redirect('login')

@login_required(login_url='login')
def dashboard_view(request):
    matches = fetch_data()
    table = fetch_league_table()
    results = fetch_last_events()

    context = {
        'username': request.user.username,
        'matches': matches,
        'table': table,      
        'results': results,  
        'error': None
    }
    
    if not matches and not table:
        context['error'] = "API error"

    return render(request, 'dashboard.html', context)

def main_view(request):
    return render(request, "main.html")