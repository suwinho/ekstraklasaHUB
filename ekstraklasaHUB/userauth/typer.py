from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from .models import Prediction, Wallet
from .utils import send_prediction_notification
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse, Http404


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