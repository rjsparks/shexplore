from django.test import TestCase
from sh import models


class ExplorationTests(TestCase):
    def test_exploration(self):
        import doctest

        print(doctest.testmod(models))
