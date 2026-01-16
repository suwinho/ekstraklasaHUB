from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .forms import UserRegistrationForm, LoginForm
from django.http import JsonResponse, Http404
from .utils import fetch_data, fetch_league_table, fetch_last_events, fetch_team_details, fetch_last_matches
from .models import Prediction, Wallet
from .utils import send_prediction_notification
import json
from decimal import Decimal

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
        team_tuple = EKSTRAKLASA_TEAMS[int(club_id)]
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

@csrf_exempt
@login_required
def predict_match(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)

    if request.method == 'GET':
        preds = list(Prediction.objects.filter(user=request.user).values())
        return JsonResponse({
            'predictions': preds,
            'balance': float(wallet.balance) 
        })

    if request.method == 'POST':
        data = json.loads(request.body)
        new_stake = Decimal(data['stake'])
        
        if new_stake <= 0:
            return JsonResponse({'error': 'Stawka musi być dodatnia!'}, status=400)

        try:
            prediction = Prediction.objects.get(user=request.user, match_id=data['match_id'])
            
            wallet.balance += prediction.stake
            
            if wallet.balance < new_stake:
                wallet.balance -= prediction.stake 
                return JsonResponse({'error': 'Brak wystarczających środków!'}, status=400)
            
            wallet.balance -= new_stake
            created = False
            
        except Prediction.DoesNotExist:
            if wallet.balance < new_stake:
                return JsonResponse({'error': 'Brak wystarczających środków!'}, status=400)
            
            wallet.balance -= new_stake
            created = True
            prediction = Prediction(user=request.user, match_id=data['match_id'])

        wallet.save()

        prediction.home_team = data['home_team']
        prediction.away_team = data['away_team']
        prediction.home_score = int(data['home_score'])
        prediction.away_score = int(data['away_score'])
        prediction.stake = new_stake
        prediction.save()
        
        # MQTT Notification
        action = f"postawił {new_stake} PLN na" if created else f"zmienił zakład ({new_stake} PLN) na"
        send_prediction_notification(request.user.username, f"{prediction.home_team}-{prediction.away_team}", action)
        
        return JsonResponse({
            'status': 'ok', 
            'action': 'created' if created else 'updated',
            'new_balance': float(wallet.balance)
        })

    if request.method == 'DELETE':
        data = json.loads(request.body)
        try:
            pred = Prediction.objects.get(user=request.user, match_id=data['match_id'])
            
            wallet.balance += pred.stake
            wallet.save()
            
            match_name = f"{pred.home_team}-{pred.away_team}"
            pred.delete()
            
            send_prediction_notification(request.user.username, match_name, "wycofał zakład z")
            
            return JsonResponse({'status': 'deleted', 'new_balance': float(wallet.balance)})
        except Prediction.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)

    return JsonResponse({'error': 'Method not allowed'}, status=405)