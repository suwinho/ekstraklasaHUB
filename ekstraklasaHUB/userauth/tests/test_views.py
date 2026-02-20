from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
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