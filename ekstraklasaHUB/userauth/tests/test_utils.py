from django.test import TestCase
import unittest
from unittest.mock import patch, MagicMock
from userauth.utils import fetch_data, fetch_league_table, fetch_last_events, fetch_team_details, fetch_last_matches

# Create your tests here.

class TestApi(unittest.TestCase):
    @patch('requests.get')
    def test_fetch_data_success(self,mock_get):
        mock_get.return_value.json.return_value = {'events': [{'idEvent': '123'}]}
        mock_get.return_value.status_code = 200

        result = fetch_data()
        self.assertEqual(len(result),1)
        self.assertEqual(result[0]['idEvent'],'123')
    
    @patch('requests.get')
    def test_fetch_data_fail(self, mock_get):
        mock_get.side_effect = Exception("Timeout")
        result = fetch_data()
        self.assertEqual(result, [])
    
    @patch('requests.get')
    def test_fetch_league_table_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'table': [{'strTeam': 'Lech', 'intRank': '1'}]}
        result = fetch_league_table()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['strTeam'], 'Lech')

    @patch('requests.get')
    def test_fetch_team_details_soccer(self, mock_get):
        mock_get.return_value.json.return_value = {
            'teams': [
                {'strTeam': 'Lech Poznan', 'strSport': 'Soccer'},
                {'strTeam': 'Lech Basket', 'strSport': 'Basketball'}
            ]
        }
        result = fetch_team_details("Lech Poznan")
        self.assertEqual(result['strSport'], 'Soccer')

    @patch('requests.get')
    def test_fetch_last_matches_empty(self, mock_get):
        mock_get.return_value.json.return_value = {'results': None}
        result = fetch_last_matches("1337")
        self.assertEqual(result, [])
