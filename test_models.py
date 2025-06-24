import unittest
import os
import random
from models import Player, Team, Tournament
import time


# Ustawienie stałego ziarna losowości dla powtarzalności testów
random.seed(42)


class TestTournamentModels(unittest.TestCase):

    def setUp(self):
        """Metoda uruchamiana przed każdym testem. Tworzy świeżą instancję turnieju."""
        self.tournament = Tournament()
        self.test_filename = "test_tournament_save.json"

    def tearDown(self):
        """Metoda uruchamiana po każdym teście. Sprząta po testach, np. usuwa pliki."""
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    def test_player_creation_with_specific_stats(self):
        """Testuje, czy gracz jest tworzony z poprawnie przypisanymi statystykami."""
        player = Player("Jan", "Kowalski", "Test Team", attack=10, defense=8, aggression=3)
        self.assertEqual(player.first_name, "Jan")
        self.assertEqual(player.last_name, "Kowalski")
        self.assertEqual(player.team_name, "Test Team")
        self.assertEqual(player.attack, 10)
        self.assertEqual(player.defense, 8)
        self.assertEqual(player.aggression, 3)

    def test_player_creation_with_random_stats(self):
        """Testuje, czy graczowi są losowane statystyki, gdy nie są podane."""
        player = Player("Anna", "Nowak", "Test Team")
        self.assertIsInstance(player.attack, int)
        self.assertTrue(3 <= player.attack <= 10)
        self.assertTrue(3 <= player.defense <= 10)
        self.assertTrue(1 <= player.aggression <= 10)

    def test_team_add_player(self):
        """Testuje dodawanie gracza do drużyny (po poprawce w models.py)."""
        team = Team("Mistrzowie Kodu")
        team.add_player("Linus", "Torvalds")
        self.assertEqual(len(team.players), 1)
        self.assertEqual(team.players[0].name, "Linus Torvalds")
        self.assertEqual(team.players[0].team_name, "Mistrzowie Kodu")

    def test_team_calculates_total_stats(self):
        """Testuje, czy drużyna poprawnie sumuje statystyki swoich graczy."""
        team = Team("Statystycy")
        p1 = Player("Gracz", "Jeden", "Statystycy", attack=10, defense=5)
        p2 = Player("Gracz", "Dwa", "Statystycy", attack=7, defense=8)
        team.players.extend([p1, p2])
        self.assertEqual(team.total_attack, 17)
        self.assertEqual(team.total_defense, 13)

    def test_tournament_add_team(self):
        """Testuje dodawanie drużyny do turnieju za pomocą jej nazwy."""
        self.tournament.add_team("FC Python")
        self.assertEqual(len(self.tournament.teams), 1)
        self.assertIsInstance(self.tournament.teams[0], Team)
        self.assertEqual(self.tournament.teams[0].name, "FC Python")

    def test_tournament_add_duplicate_team_raises_error(self):
        """Testuje, czy próba dodania drużyny o tej samej nazwie rzuci błąd."""
        self.tournament.add_team("FC Unikat")
        with self.assertRaises(ValueError):
            self.tournament.add_team("FC Unikat")

    def test_start_tournament_validation_not_16_teams(self):
        """Testuje walidację liczby drużyn przed startem turnieju."""
        self.tournament.add_team("Jedyna Drużyna")
        with self.assertRaisesRegex(ValueError, "Turniej musi mieć dokładnie 16 drużyn"):
            self.tournament.start_tournament()

    def test_start_tournament_validation_not_11_players(self):
        """Testuje walidację liczby graczy w drużynie przed startem turnieju."""
        for i in range(16):
            self.tournament.add_team(f"Drużyna {i + 1}")
        with self.assertRaisesRegex(ValueError, "musi mieć dokładnie 11 zawodników"):
            self.tournament.start_tournament()

    def test_generate_random_tournament_and_start(self):
        """Testuje, czy losowe generowanie turnieju działa poprawnie."""
        self.tournament.generate_random_tournament()  # Ta metoda wywołuje też start_tournament
        self.assertEqual(len(self.tournament.teams), 16)
        self.assertEqual(len(self.tournament.teams[0].players), 11)
        self.assertEqual(self.tournament.phase, "GROUP_STAGE")
        self.assertIn("Grupa A", self.tournament.groups)
        self.assertEqual(len(self.tournament.matches),
                         48)

    def test_full_tournament_simulation_flow(self):
        """Kompleksowy test symulujący cały turniej od początku do końca."""
        self.tournament.generate_random_tournament()
        self.assertEqual(self.tournament.phase, "GROUP_STAGE")

        # Symulacja 6 kolejek fazy grupowej
        for i in range(6):
            status = self.tournament.simulate_next_round()
            if self.tournament.phase == "GROUP_STAGE":
                self.assertIn(f"Zakończono kolejkę {i + 1}", status)
            else:
                # Po zagraniu 6. kolejki status od razu informuje o końcu fazy grupowej
                self.assertEqual(status, "Faza grupowa zakończona. Czas na ćwierćfinały!")

        self.assertEqual(self.tournament.phase, "KNOCKOUT_STAGE")
        self.assertIn("Quarter-finals", self.tournament.knockout_matches)

        # Ćwierćfinały
        status = self.tournament.simulate_next_round()
        self.assertEqual(status, "Zakończono Quarter-finals. Czas na Semi-finals!")

        # Półfinały
        status = self.tournament.simulate_next_round()
        self.assertEqual(status, "Zakończono Semi-finals. Czas na Final!")

        # Finał
        status = self.tournament.simulate_next_round()
        self.assertTrue(status.startswith("Turniej wygrywa"))

        # Sprawdzenie, czy zwycięzca został ustawiony
        self.assertIsNotNone(self.tournament.winner)
        self.assertIsInstance(self.tournament.winner, Team)

    def test_performance_of_tournament_generation(self):

        start_time = time.time()

        self.tournament.generate_random_tournament()

        end_time = time.time()

        duration = end_time - start_time

        print(f"\n[INFO] Czas generowania turnieju: {duration:.4f}s")

        self.assertLess(duration, 1.0, "Generowanie turnieju trwało zbyt długo!")


if __name__ == '__main__':
    unittest.main()