from django.test import TestCase

from posts.factories import SuperHeroFactory


class SuperHeroModelTest(TestCase):
    """
    Test the SuperHero model.
    """

    def setUp(self):
        self.superhero = SuperHeroFactory(name="Spider-Man", power="Web-slinging")

    def test_superhero_str_method(self):
        """
        Test the __str__ method of the SuperHero model.
        """
        self.assertEqual(str(self.superhero), "Spider-Man")

    def test_superhero_creation(self):
        """
        Test that a SuperHero instance is created and saved correctly.
        """
        self.assertEqual(self.superhero.name, "Spider-Man")
        self.assertEqual(self.superhero.power, "Web-slinging")
