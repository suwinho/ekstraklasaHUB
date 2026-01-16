from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, LoginForm
from django.http import JsonResponse, Http404
from .utils import fetch_data, fetch_league_table, fetch_last_events, fetch_team_details, fetch_last_matches

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
    fav_team = request.user.profile.favorite_team

    team_details = fetch_team_details(fav_team)

    if team_details:
                team_id = -1
                for index, (name, _) in enumerate(EKSTRAKLASA_TEAMS):
                    if name == fav_team:
                        team_id = index
                        break
                
                favorite_team_data = {
                    'name': team_details.get('strTeam'),
                    'badge': team_details.get('strTeamBadge'),
                    'bg': team_details.get('strTeamFanart1') or team_details.get('strStadiumThumb'),
                    'id': team_id
                }

    context = {
        'username': request.user.username,
        'matches': matches,
        'table': table,      
        'results': results,  
        'favorite_team': favorite_team_data,
        'error': None
    }
    
    if not matches and not table:
        context['error'] = "API error"

    return render(request, 'dashboard.html', context)

def main_view(request):
    return render(request, "main.html")

EKSTRAKLASA_TEAMS = [
    ('Jagiellonia Białystok', 'Jagiellonia Białystok'),
    ('Wisła Płock', 'Wisła Płock'),
    ('Legia Warszawa', 'Legia Warszawa'),
    ('Pogoń Szczecin', 'Pogoń Szczecin'),
    ('Lech Poznań', 'Lech Poznań'),
    ('Górnik Zabrze', 'Górnik Zabrze'),
    ('Raków Częstochowa', 'Raków Częstochowa'),
    ('Zagłębie Lubin', 'Zagłębie Lubin'),
    ('Widzew Łódź', 'Widzew Łódź'),
    ('Piast Gliwice', 'Piast Gliwice'),
    ('Bruk-Bet Termalica Nieciecza', 'Bruk-Bet Termalica Nieciecza'),
    ('Arka Gdynia', 'Arka Gdynia'),
    ('Cracovia', 'Cracovia'),
    ('Korona Kielce', 'Korona Kielce'),
    ('Radomiak Radom', 'Radomiak Radom'),
    ('Lechia Gdańsk', 'Lechia Gdańsk'),
    ('GKS Katowice', 'GKS Katowice'),
    ('Motor Lublin', 'Motor Lublin'),
]

def search_clubs_api(request):
    search_query = request.GET.get('search', '').lower()
    
    results = []
    
    if search_query:
        for index, team in enumerate(EKSTRAKLASA_TEAMS):
            team_name = team[0] 
            
            if search_query in team_name.lower():
                results.append({
                    'id': index,   
                    'name': team_name
                })
    
    return JsonResponse({'results': results})

def club_stats_view(request, club_id):
    try:
        team_tuple = EKSTRAKLASA_TEAMS[club_id]
        local_name = team_tuple[0] 
    except (IndexError, ValueError):
        raise Http404("Klub nie istnieje")

    context = {
        'club_id': club_id,    
        'local_name': local_name,
        'last_matches': [] 
    }

    team_details = fetch_team_details(local_name)
    
    if team_details:
        context['team'] = team_details
        
        api_id = team_details.get('idTeam')
        if api_id:
            raw_matches = fetch_last_matches(api_id)
            cleaned_matches = []
            
            my_team_name = team_details.get('strTeam', '')

            for match in raw_matches:
                home = match.get('strHomeTeam', '')
                away = match.get('strAwayTeam', '')
                
                if home == my_team_name:
                    opponent = away
                else:
                    opponent = home
                
                cleaned_matches.append({
                    'opponent': opponent,
                    'date': match.get('dateEvent'),
                    'score': f"{match.get('intHomeScore')}-{match.get('intAwayScore')}",
                    'raw_match': match 
                })
            
            context['last_matches'] = cleaned_matches
            
    return render(request, 'stats.html', context)

