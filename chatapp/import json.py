import json
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client

# chatapp/test_views.py

class ScholarProfilesTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    @patch("chatapp.views.scholarly.search_author")
    @patch("chatapp.views.scholarly.fill")
    def test_scholar_profiles(self, mock_fill, mock_search_author):
        # Mock data for search_author
        mock_author = MagicMock()
        mock_author.get.side_effect = lambda key: {
            "name": "Dr. John Doe",
            "affiliation": "The Catholic University of America",
            "interests": ["AI", "Machine Learning"],
            "scholar_id": "12345",
            "email_domain": "cua.edu",
        }.get(key)
        mock_search_author.return_value = [mock_author]

        # Mock data for fill
        mock_filled_author = mock_author
        mock_filled_author.get.side_effect = lambda key: {
            "publications": [
                {
                    "bib": {
                        "title": "Deep Learning Models",
                        "pub_year": "2021",
                        "venue": "AI Journal"
                    }
                },
                {
                    "bib": {
                        "title": "Natural Language Processing",
                        "pub_year": "2020",
                        "venue": "NLP Conference"
                    }
                },