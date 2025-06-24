import random
import json
from data import team_names, first_names, last_names  # Import danych do generowania losowego


class Player:
    """Reprezentuje pojedynczego zawodnika ze statystykami."""

    def __init__(self, first_name, last_name, team_name, attack=None, defense=None, aggression=None):
        self.first_name = first_name
        self.last_name = last_name
        self.team_name = team_name
        self.name = f"{self.first_name} {self.last_name}"

        # Statystyki umiejętności: użyj podanych lub wylosuj, jeśli nie istnieją
        self.attack = attack if attack is not None else random.randint(3, 10)
        self.defense = defense if defense is not None else random.randint(3, 10)
        self.aggression = aggression if aggression is not None else random.randint(1, 10)

        # Statystyki zdobyte podczas turnieju
        self.goals = 0
        self.yellow_cards = 0
        self.red_cards = 0

    def to_dict(self):
        """Konwertuje obiekt gracza na słownik, idealny do zapisu w formacie JSON."""
        return {
            "name": self.name,
            "skills": {
                "attack": self.attack,
                "defense": self.defense,
                "aggression": self.aggression
            },
            "tournament_stats": {
                "goals": self.goals,
                "yellow_cards": self.yellow_cards,
                "red_cards": self.red_cards
            }
        }

    def __repr__(self):
        return f"{self.name}"


class Team:
    """Reprezentuje drużynę składającą się z zawodników."""

    def __init__(self, name, group=None):
        self.name = name
        self.group = group
        self.players = []  # Drużyna startuje z pustym składem

        # Statystyki drużyny w fazie grupowej
        self.points = 0
        self.matches_played = 0
        self.wins = 0
        self.draws = 0
        self.losses = 0
        self.goals_for = 0
        self.goals_against = 0

    def add_player(self, first_name, last_name):
        # Sprawdzamy, czy imię i nazwisko nie są pustymi stringami
        if not first_name or not last_name:
            raise ValueError("Imię i nazwisko gracza nie mogą być puste.")

        # Tworzymy gracza, podając mu jego imię, nazwisko ORAZ nazwę drużyny (self.name)
        player = Player(first_name, last_name, self.name)  # <--- POPRAWIONA LINIA
        self.players.append(player)


    def remove_player(self, player_name):
        """Usuwa zawodnika z drużyny na podstawie jego imienia i nazwiska."""
        player_to_remove = next((p for p in self.players if p.name == player_name), None)
        if player_to_remove:
            self.players.remove(player_to_remove)
        else:
            raise ValueError("Nie znaleziono takiego zawodnika w drużynie.")

    @property
    def total_attack(self):
        """Oblicza sumę ataku wszystkich aktywnych (bez czerwonej kartki) zawodników."""
        return sum(p.attack for p in self.players if p.red_cards == 0)

    @property
    def total_defense(self):
        """Oblicza sumę obrony wszystkich aktywnych zawodników."""
        return sum(p.defense for p in self.players if p.red_cards == 0)

    @property
    def goal_difference(self):
        """Oblicza różnicę bramek."""
        return self.goals_for - self.goals_against

    def add_match_result(self, goals_for, goals_against):
        """Aktualizuje statystyki drużyny po rozegranym meczu grupowym."""
        self.matches_played += 1
        self.goals_for += goals_for
        self.goals_against += goals_against
        if goals_for > goals_against:
            self.wins += 1
            self.points += 3
        elif goals_for == goals_against:
            self.draws += 1
            self.points += 1
        else:
            self.losses += 1

    def get_all_players(self):
        return self.players

    def to_dict(self):
        """Konwertuje obiekt drużyny i jej zawodników na słownik do zapisu w JSON."""
        return {
            "name": self.name,
            "group": self.group,
            "group_stage_stats": {
                "points": self.points,
                "matches_played": self.matches_played,
                "wins": self.wins,
                "draws": self.draws,
                "losses": self.losses,
                "goals_for": self.goals_for,
                "goals_against": self.goals_against
            },
            "players": [player.to_dict() for player in self.players]
        }

    def __repr__(self):
        return self.name


class Match:
    """Reprezentuje pojedynczy mecz wraz z jego zdarzeniami."""

    def __init__(self, team1, team2, round_num, phase):
        self.team1 = team1
        self.team2 = team2
        self.round = round_num
        self.phase = phase
        self.score1 = None
        self.score2 = None
        self.winner = None
        self.events = []

    @property
    def is_played(self):
        return self.score1 is not None

    def add_event(self, minute, event_type, player, details=""):
        self.events.append({"minute": minute, "type": event_type, "player": player, "details": details})

    def __repr__(self):
        if self.is_played:
            return f"{self.team1.name} {self.score1} - {self.score2} {self.team2.name}"
        return f"{self.team1.name} vs {self.team2.name}"


class Tournament:
    """Główna klasa zarządzająca całym stanem i logiką turnieju."""

    def to_dict(self):
        """Konwertuje obiekt drużyny i jej zawodników na słownik do zapisu w JSON."""
        return {
            "name": self.name,
            "group": self.group,
            "group_stage_stats": {
                "points": self.points,
                "matches_played": self.matches_played,
                "wins": self.wins,
                "draws": self.draws,
                "losses": self.losses,
                "goals_for": self.goals_for,
                "goals_against": self.goals_against
            },
            "players": [player.to_dict() for player in self.players]
        }

    def __init__(self):
        self.reset_to_setup()

    def reset_to_setup(self):
        """Resetuje turniej do pustego stanu konfiguracji, gotowego na nowe dane."""
        self.teams = []
        self.all_players = []
        self.groups = {}
        self.phase = "SETUP"  # Faza początkowa, w której użytkownik dodaje dane
        self.current_round = 0
        self.matches = []
        self.knockout_matches = {}
        self.winner = None

    def add_team(self, name):
        if not name or not name.strip():
            raise ValueError("Nazwa drużyny nie może być pusta.")
        """Dodaje nową drużynę do turnieju (tylko w fazie SETUP)."""
        if self.phase != "SETUP":
            raise ValueError("Nie można dodawać drużyn po rozpoczęciu turnieju.")
        if any(t.name.lower() == name.lower() for t in self.teams):
            raise ValueError(f"Drużyna o nazwie '{name}' już istnieje.")
        team = Team(name)
        self.teams.append(team)

    def remove_team(self, name):
        """Usuwa drużynę z turnieju (tylko w fazie SETUP)."""
        if self.phase != "SETUP":
            raise ValueError("Nie można usuwać drużyn po rozpoczęciu turnieju.")
        team_to_remove = next((t for t in self.teams if t.name == name), None)
        if team_to_remove:
            self.teams.remove(team_to_remove)
        else:
            raise ValueError("Nie znaleziono takiej drużyny.")

    def find_team(self, name):
        """Wyszukuje i zwraca obiekt drużyny o podanej nazwie."""
        for team in self.teams:
            if team.name == name:
                return team
        return None

    def save_to_file(self, filename):
        """Zapisuje stan turnieju do pliku JSON."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=4)

    def generate_random_tournament(self):
        """Automatycznie generuje pełny turniej z losowymi drużynami i graczami."""
        self.reset_to_setup()
        selected_team_names = random.sample(team_names, 16)
        for name in selected_team_names:
            self.add_team(name)
            team = next(t for t in self.teams if t.name == name)
            players_added = 0
            while players_added < 11:
                team.add_player(random.choice(first_names), random.choice(last_names))
                players_added += 1
        self.start_tournament()

    def start_tournament(self):
        """Waliduje stan turnieju i rozpoczyna fazę grupową."""
        if len(self.teams) != 16:
            raise ValueError("Turniej musi mieć dokładnie 16 drużyn, aby go rozpocząć.")
        for team in self.teams:
            if len(team.players) != 11:
                raise ValueError(f"Drużyna '{team.name}' musi mieć dokładnie 11 zawodników.")

        self.all_players = [p for t in self.teams for p in t.players]
        random.shuffle(self.teams)
        self.groups = {
            "Grupa A": self.teams[0:4], "Grupa B": self.teams[4:8],
            "Grupa C": self.teams[8:12], "Grupa D": self.teams[12:16],
        }
        for name, teams_in_group in self.groups.items():
            for team in teams_in_group:
                team.group = name

        self.phase = "GROUP_STAGE"
        self.current_round = 1
        self._schedule_group_stage()

    @property
    def top_scorer(self):
        """Zwraca listę graczy z największą liczbą goli w turnieju."""
        if not self.all_players: return []
        max_goals = max(p.goals for p in self.all_players)
        if max_goals == 0: return []
        return [p for p in self.all_players if p.goals == max_goals]

    def export_teams_to_json(self, filename="teams_data.json"):
        """Eksportuje dane wszystkich drużyn i ich zawodników do pliku JSON."""
        data = [team.to_dict() for team in self.teams]
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return f"Dane drużyn zostały pomyślnie wyeksportowane do pliku '{filename}'"

    def simulate_next_round(self):
        """Symuluje wszystkie mecze w bieżącej kolejce lub rundzie pucharowej."""
        if self.winner:
            return "Turniej zakończony."

        if self.phase == "GROUP_STAGE":
            matches_to_play = [m for m in self.matches if m.round == self.current_round and not m.is_played]
            for match in matches_to_play:
                self._simulate_match_result(match)

            if self.current_round == 6:
                self.phase = "KNOCKOUT_STAGE"
                self.current_round = 0
                self._create_knockout_bracket()
                return "Faza grupowa zakończona. Czas na ćwierćfinały!"
            else:
                self.current_round += 1
                return f"Zakończono kolejkę {self.current_round - 1}."

        elif self.phase == "KNOCKOUT_STAGE":
            round_names = ["Quarter-finals", "Semi-finals", "Final"]
            current_knockout_round = round_names[self.current_round]
            matches_to_play = self.knockout_matches[current_knockout_round]

            for match in matches_to_play:
                self._simulate_match_result(match)

            winners = [m.winner for m in matches_to_play]

            if current_knockout_round == "Final":
                self.winner = winners[0]
                return f"Turniej wygrywa {self.winner.name}!"

            next_knockout_round_name = round_names[self.current_round + 1]
            self.knockout_matches[next_knockout_round_name] = []

            for i in range(0, len(winners), 2):
                new_match = Match(winners[i], winners[i + 1], self.current_round + 2, "KNOCKOUT")
                self.knockout_matches[next_knockout_round_name].append(new_match)

            self.current_round += 1
            return f"Zakończono {current_knockout_round}. Czas na {next_knockout_round_name}!"

    def _schedule_group_stage(self):
        """Tworzy sprawiedliwy terminarz dla fazy grupowej (mecz i rewanż)."""
        self.matches = []
        for group_teams in self.groups.values():

            teams = list(group_teams)

            if len(teams) % 2:
                teams.append(None)

            num_teams = len(teams)
            num_rounds = num_teams - 1

            first_leg_rounds = []
            for round_num in range(num_rounds):
                current_round_matches = []
                for i in range(num_teams // 2):
                    team1 = teams[i]
                    team2 = teams[num_teams - 1 - i]

                    if team1 is not None and team2 is not None:
                        current_round_matches.append(Match(team1, team2, round_num + 1, "GROUP"))

                first_leg_rounds.append(current_round_matches)

                teams.insert(1, teams.pop())

            second_leg_rounds = []
            for i, round_matches in enumerate(first_leg_rounds):
                current_round_matches = []
                for match in round_matches:
                    current_round_matches.append(Match(match.team2, match.team1, num_rounds + i + 1, "GROUP"))
                second_leg_rounds.append(current_round_matches)

            all_rounds = first_leg_rounds + second_leg_rounds

            random.shuffle(all_rounds)

            round_counter = 1
            for round_matches in all_rounds:
                for match in round_matches:
                    match.round = round_counter
                    self.matches.append(match)
                round_counter += 1

    def _simulate_match_result(self, match):
        """Symuluje wynik jednego meczu na podstawie statystyk i losowości."""
        strength1 = match.team1.total_attack
        strength2 = match.team2.total_attack

        score1 = max(0, int(random.gauss(strength1 / 55, 1.5)))
        score2 = max(0, int(random.gauss(strength2 / 55, 1.5)))

        match.score1 = score1
        match.score2 = score2
        self._simulate_events(match)

        if match.phase == "GROUP":
            match.team1.add_match_result(score1, score2)
            match.team2.add_match_result(score2, score1)
        else:  # KNOCKOUT
            if score1 > score2:
                match.winner = match.team1
            elif score2 > score1:
                match.winner = match.team2
            else:
                match.winner = random.choice([match.team1, match.team2])
                match.add_event(91, "INFO", None,
                                f"Mecz rozstrzygnięty w rzutach karnych. Wygrywa: {match.winner.name}")

    def _simulate_events(self, match):
        """Symuluje kto strzelił gole i kto dostał kartki w meczu."""
        # Przypisanie goli dla drużyny 1
        for _ in range(match.score1):
            scorers_pool = [p for p in match.team1.players if p.red_cards == 0]
            if not scorers_pool: continue
            scorer = random.choices(scorers_pool, weights=[p.attack for p in scorers_pool], k=1)[0]
            scorer.goals += 1
            match.add_event(random.randint(1, 90), "GOAL", scorer)

        for _ in range(match.score2):
            scorers_pool = [p for p in match.team2.players if p.red_cards == 0]
            if not scorers_pool: continue
            scorer = random.choices(scorers_pool, weights=[p.attack for p in scorers_pool], k=1)[0]
            scorer.goals += 1
            match.add_event(random.randint(1, 90), "GOAL", scorer)

        # Przypisanie kartek
        all_players_in_match = match.team1.players + match.team2.players
        for player in all_players_in_match:
            # Szansa na żółtą kartkę rośnie z agresją
            if random.randint(1, 100) < player.aggression * 2:
                if player.yellow_cards % 2 == 1:
                    player.red_cards += 1
                    match.add_event(random.randint(1, 90), "RED_CARD", player, "Druga żółta")
                else:
                    player.yellow_cards += 1
                    match.add_event(random.randint(1, 90), "YELLOW_CARD", player)

    def _create_knockout_bracket(self):
        """Tworzy drabinkę pucharową z 2 najlepszych drużyn z każdej grupy."""
        qualifiers = {}
        for name, teams_in_group in self.groups.items():
            sorted_teams = sorted(teams_in_group, key=lambda t: (t.points, t.goal_difference, t.goals_for),
                                  reverse=True)
            qualifiers[name] = sorted_teams[:2]

        # Standardowe pary ćwierćfinałowe (A1 vs B2, C1 vs D2, itd.)
        qf_matches = [
            Match(qualifiers["Grupa A"][0], qualifiers["Grupa B"][1], 1, "KNOCKOUT"),
            Match(qualifiers["Grupa C"][0], qualifiers["Grupa D"][1], 1, "KNOCKOUT"),
            Match(qualifiers["Grupa B"][0], qualifiers["Grupa A"][1], 1, "KNOCKOUT"),
            Match(qualifiers["Grupa D"][0], qualifiers["Grupa C"][1], 1, "KNOCKOUT"),
        ]
        self.knockout_matches["Quarter-finals"] = qf_matches


class PlayerStatsReporter(Player):
    def __init__(self, all_players_list):

        super().__init__(first_name="Stat-Bot", last_name="Reporter", team_name="System")

        self.players_to_report_on = all_players_list


    def get_top_scorers_ranking(self, top_n=5):

        sorted_by_goals = sorted(self.players_to_report_on, key=lambda p: p.goals, reverse=True)

        ranking = []
        for i, player in enumerate(sorted_by_goals[:top_n]):
            if player.goals > 0:
                ranking_entry = (i + 1, player)
                ranking.append(ranking_entry)
            else:

                break
        return ranking

    def display_top_scorers(self, top_n=5):
        print(f"\n--- NAJLEPSI STRZELCY (TOP {top_n}) ---")

        top_scorers_ranking = self.get_top_scorers_ranking(top_n)

        if not top_scorers_ranking:
            print("Nikt jeszcze nie strzelił gola.")
            return

        for position, player in top_scorers_ranking:
            print(f"{position}. {player.name} ({player.team_name}) - {player.goals} goli")

    def display_card_offenders(self):
        print("\n--- ZAWODNICY Z NAJWIĘKSZĄ LICZBĄ KARTEK ---")

        offenders = list(filter(
            lambda p: p.yellow_cards > 0 or p.red_cards > 0,
            self.players_to_report_on
        ))

        sorted_by_cards = sorted(
            offenders,
            key=lambda p: (p.red_cards * 3 + p.yellow_cards),
            reverse=True
        )

        if not sorted_by_cards:
            print("Żaden zawodnik nie otrzymał kartki.")
            return

        for player in sorted_by_cards[:5]:
            print(f"- {player.name}: {player.yellow_cards} żółtych, {player.red_cards} czerwonych")

    def display_full_stats_table(self):
        print("\n--- PEŁNE STATYSTYKI ZAWODNIKÓW ---")
        header = f"{'Zawodnik':<25} | {'Drużyna':<20} | {'Gole':>5} | {'Ż.K.':>5} | {'Cz.K.':>5}"
        print(header)
        print("-" * len(header))

        sorted_players = sorted(self.players_to_report_on, key=lambda p: p.last_name)

        format_row = lambda p: (
            f"{p.name:<25} | {p.team_name:<20} | {p.goals:>5} | {p.yellow_cards:>5} | {p.red_cards:>5}"
        )

        formatted_rows_iterator = map(format_row, sorted_players)

        for row in formatted_rows_iterator:
            print(row)

        print("-" * len(header))
