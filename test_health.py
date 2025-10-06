import unittest
from main import check_database, check_disk_usage
import re

class TestHealthChecks(unittest.TestCase):
    def test_check_database_returns_valid_status(self):
        result = check_database()
        self.assertIn(result, ["ok", "fail"])
    
    def test_check_disk_usage_returns_valid_status(self):
        result = check_disk_usage()
        self.assertIn(result, ["ok", "warn", "fail"])

if __name__ == '__main__':
    unittest.main()