from django.test import TestCase
import unittest
from unittest.mock import patch, MagicMock
from userauth.utils import write_logs_to_file

class TestLogs(unittest.TestCase):
    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_wite_logs_to_file(self, mock_file):
        write_logs_to_file("Test")
        mock_file().write.assert_called()
        args, _ = mock_file().write.call_args
        self.assertIn("Test", args[0])