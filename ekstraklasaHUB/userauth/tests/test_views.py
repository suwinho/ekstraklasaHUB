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
        unknown = User.objects.create_user(username="unk", password="asd")
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