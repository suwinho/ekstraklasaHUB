from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
from userauth.models import Message, Profile
import json

class TestUserAuth(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='abc', password = 'asd')
        Profile.objects.create(user = self.user, favorite_team = 'Lechia Gdańsk')
        self.msg = Message.objects.create(user=self.user, content="test")
    
    def test_dashboard_access_denied_for_anonymous(self):
        url = reverse('dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_search_clubs(self):
        url = reverse('search_clubs_api') + "?search=Lechia"
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(item['name'] == 'Lechia Gdańsk' for item in data['results']))
    
    def test_delete_message(self):
        self.client.login(username="abc", password="asd")
        url = reverse('message_detail', args=[self.msg.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code,200)
        self.assertFalse(Message.objects.filter(id=self.msg.id).exists())

    def test_delete_message_by_other(self):
        User.objects.create_user(username="unk", password="asd")
        self.client.login(username='unk',password='asd')
        url = reverse('message_detail', args = [self.msg.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Message.objects.filter(id=self.msg.id).exists())

    def test_update_message(self):
        self.client.login(username='abc', password='asd')
        url = reverse('message_detail', args=[self.msg.id])
        edited_data = {'text': 'edited'}
        response = self.client.put(url, data = json.dumps(edited_data), content_type='application/json')
        self.assertEqual(response.status_code,200)
        self.msg.refresh_from_db()
        self.assertEqual(self.msg.content, 'edited')
        self.assertEqual(response.json()['text'],'edited')

    def test_login_invalid(self):
        url = reverse('login')
        response = self.client.post(url, {'username': 'wrong', 'password': 'user'})
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertTrue(any('Błędna nazwa użytkownika' in str(m) for m in messages))

    @patch('userauth.views.fetch_data')
    @patch('userauth.views.fetch_league_table')
    def test_dashboard_api_error_handling(self,mock_table, mock_data):
        self.client.login(username='abc', password='asd')
        mock_data.return_value = []
        mock_table.return_value = []
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.context['error'],"API error")
        
    def test_send_message_api_success(self):
        self.client.login(username="abc", password="asd")
        url = reverse('chat_send_http')
        payload = {'text': 'new text', 'use_mqtt': False}

        response = self.client.post(
            url, 
            data=json.dumps(payload), 
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')
        self.assertTrue(Message.objects.filter(content='new text').exists())
    
    def test_register_succes(self):
        url = reverse('register')
        data = {
            'username': 'new_user',
            'password': 'asd',
            'confirm_password': 'asd',
            'favorite_team': 'Motor Lublin'
        }
        response = self.client.post(url,data)
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='new_user').exists())
    
    def test_register_fail(self):
        url = reverse('register')
        data = {
            'username': 'new_user',
            'password': 'asd',
            'confirm_password': 'asd1',
            'favorite_team': 'Motor Lublin'
        }
        response = self.client.post(url,data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], None, 'Hasła nie są identyczne.')

    @patch('userauth.views.fetch_team_details')
    @patch('userauth.views.fetch_last_matches')
    def test_club_stats_view_success(self,mock_matches, mock_details):
        mock_details.return_value = {
            'idTeam': '1337',
            'strTeam': 'Lech Poznań',
            'strTeamBadge': 'http://image.com/badge.png',
            'strBadge': 'http://image.com/badge.png',
            'strFanart1': 'http://image.com/fanart.png', 
            'strStadiumThumb': 'http://image.com/stadium.png' 
        }
        mock_matches.return_value = [
            {'strHomeTeam': 'Lech Poznań', 
             'strAwayTeam': 'Legia', 
             'intHomeScore': '2', 
             'intAwayScore': '0', 
             'dateEvent': '2025-01-01'}
        ]
        url = reverse('club_stats', args=[4]) 
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Lech Poznań', response.content.decode())
        self.assertEqual(len(response.context['last_matches']), 1)
    
    def test_club_stats_view_fail(self):
        url = reverse('club_stats', args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    @patch('userauth.views.fetch_team_details')
    @patch('userauth.views.fetch_data')
    @patch('userauth.views.fetch_league_table')
    @patch('userauth.views.fetch_last_events')
    def test_dashboard_favorite_team(self, mock_results, mock_table, mock_data, mock_details):
        self.client.login(username='abc', password = 'asd')
        mock_details.return_value = {
        'strTeam': 'Lechia Gdańsk',
        'strTeamBadge': 'badge.png',
        'strTeamFanart1': 'art.png'
        }
        mock_data.return_value = [{'event': 'mecz'}]
        mock_table.return_value = [{'team': 'Lechia'}] 
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.context['favorite_team']['name'], 'Lechia Gdańsk')
    
    @patch('userauth.views.fetch_data')
    @patch('userauth.views.fetch_league_table')
    def test_dashboard_api_fail(self, mock_data, mock_table):
        self.client.login(username='abc', password = 'asd')
        mock_data.return_value = []
        mock_table.return_value = []
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.context['error'], "API error")