from django.test import TestCase

import datetime

from django.test import TestCase
from django.test.client import Client, RequestFactory
from django.utils import timezone


class QuestionModelTests(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

    def test_was_published_recently_with_future_question(self):
        client = Client()
        response = client.get('polls/index.html')
        request = response.wsgi_request
        neo4j_crud = request.neo4j_crud
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = neo4j_crud.create_question("Question")
        self.assertIs(future_question.was_published_recently(), False)
