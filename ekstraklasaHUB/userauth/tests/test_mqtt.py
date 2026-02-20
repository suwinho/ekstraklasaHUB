from django.test import TestCase
import unittest
from unittest.mock import patch, MagicMock
from userauth.utils import send_prediction_notification

class TestMqtt(unittest.TestCase):
    @patch('paho.mqtt.client.Client')
    def test_send_prediction_notification(self, mock_mqtt):
        mock_client = mock_mqtt.return_value
        send_prediction_notification("Mateusz","Lech - Legia")

        self.assertTrue(mock_client.connect.called)
        self.assertTrue(mock_client.publish.called)