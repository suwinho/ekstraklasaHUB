import json
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch
from userauth.models import Prediction, Wallet

class TestTyper(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="abc", password = "asd")
        self.client.login(username="abc", password= "asd")
        self.wallet = Wallet.objects.create(user = self.user, balance = Decimal('100.00'))
        self.url = reverse('predict_match')
    
    @patch('userauth.typer.send_prediction_notification')
    def test_create_prediction_success(self, mock_notify):
        payload = {
            'match_id': 'match_01',
            'home_team': 'Lech',
            'away_team': 'Legia',
            'home_score': 2,
            'away_score': 1,
            'stake': '20.00'
        }
        response = self.client.post(self.url, data = json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('80.00'))
        self.assertTrue(Prediction.objects.filter(match_id = 'match_01').exists())

    def test_not_enough_balance(self):
        payload = {
            'match_id': 'match_02',
            'home_team': 'Lechia',
            'away_team': 'Widzew',
            'home_score': 0,
            'away_score': 0,
            'stake': '200.00' 
        }
        response = self.client.post(self.url, data = json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Brak wystarczających środków!')
    
    def test_delete_notification(self):
        pred = Prediction.objects.create(user=self.user, match_id='match_01', home_team='A', away_team='B',home_score=1, away_score=1, stake=Decimal('30.00'))
        self.wallet.balance -= Decimal('30.00')
        self.wallet.save()
        response = self.client.delete(self.url, data=json.dumps({'match_id': 'match_01'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('100.00'))
