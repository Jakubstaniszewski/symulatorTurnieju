import sys
import logging
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QListWidget,
    QMessageBox, QLabel, QTabWidget, QTextBrowser, QInputDialog, QDialog,
    QFormLayout, QLineEdit, QDialogButtonBox, QSplitter,QFileDialog
)
from PyQt6.QtGui import QFont ,QPalette, QColor, QPixmap
from PyQt6.QtCore import Qt
from models import Tournament, PlayerStatsReporter

import shutil
import matplotlib.pyplot as plt
import seaborn as sns

# Konfiguracja debugowania
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(message)s')


class AddPlayerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dodaj nowego zawodnika")
        self.first_name_input = QLineEdit(self)
        self.last_name_input = QLineEdit(self)

        form_layout = QFormLayout(self)
        form_layout.addRow("Imię:", self.first_name_input)
        form_layout.addRow("Nazwisko:", self.last_name_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form_layout.addWidget(buttons)

    def get_data(self):
        return self.first_name_input.text().strip(), self.last_name_input.text().strip()


class TournamentApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tournament = Tournament()
        self.setWindowTitle("Symulator Turnieju Piłkarskiego 🏆")
        self.setGeometry(100, 100, 1400, 900)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.create_top_panel()
        self.create_main_content_tabs()
        self.refresh_all_views()

    def create_top_panel(self):
        top_panel_layout = QHBoxLayout()
        self.simulate_btn = QPushButton("Symuluj następną kolejkę")
        self.simulate_btn.clicked.connect(self.run_simulation)
        self.simulate_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))

        self.reset_btn = QPushButton("Resetuj Turniej do Konfiguracji")
        self.reset_btn.clicked.connect(self.reset_tournament)

        self.status_label = QLabel()
        self.status_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))

        self.save_btn = QPushButton("Zapisz stan")
        self.save_btn.clicked.connect(self.save_tournament_state)
        self.load_btn = QPushButton("Wczytaj stan")
        self.load_btn.clicked.connect(self.load_tournament_state)

        top_panel_layout.addWidget(self.save_btn)
        top_panel_layout.addWidget(self.load_btn)
        top_panel_layout.addWidget(self.simulate_btn)
        top_panel_layout.addWidget(self.reset_btn)
        top_panel_layout.addStretch()
        top_panel_layout.addWidget(self.status_label)
        self.main_layout.addLayout(top_panel_layout)
        self.save_btn.clicked.connect(self.save_tournament_state)


    def create_main_content_tabs(self):
        self.main_tabs = QTabWidget()
        management_widget = self.create_management_widget()
        tournament_view_widget = self.create_tournament_view_widget()
        stats_widget = self.create_player_stats_widget()
        results_widget = self.create_results_widget()

        visualization_widget = self.create_visualization_widget()

        self.main_tabs.addTab(management_widget, "Zarządzanie Turniejem")

        self.main_tabs.addTab(tournament_view_widget, "Turniej")
        self.main_tabs.addTab(stats_widget, "Statystyki Graczy")
        self.main_tabs.addTab(results_widget, "Wyniki Meczów")
        self.main_tabs.addTab(visualization_widget, "Wizualizacje Danych")

        self.main_layout.addWidget(self.main_tabs)


    def create_management_widget(self):
        widget = QWidget()
        main_layout = QHBoxLayout(widget)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        teams_panel = QWidget()
        teams_layout = QVBoxLayout(teams_panel)
        teams_layout.addWidget(QLabel("<h3>Drużyny (0/16)</h3>"))
        self.teams_list_widget = QListWidget()
        self.teams_list_widget.itemSelectionChanged.connect(self.update_player_list)
        teams_layout.addWidget(self.teams_list_widget)

        team_buttons_layout = QHBoxLayout()
        self.add_team_btn = QPushButton("Dodaj drużynę")
        self.add_team_btn.clicked.connect(self.add_team)
        self.remove_team_btn = QPushButton("Usuń drużynę")
        self.remove_team_btn.clicked.connect(self.remove_team)
        team_buttons_layout.addWidget(self.add_team_btn)
        team_buttons_layout.addWidget(self.remove_team_btn)
        teams_layout.addLayout(team_buttons_layout)

        players_panel = QWidget()
        players_layout = QVBoxLayout(players_panel)
        self.players_label = QLabel("<h3>Zawodnicy w wybranej drużynie (0/11)</h3>")
        players_layout.addWidget(self.players_label)
        self.players_list_widget = QListWidget()
        players_layout.addWidget(self.players_list_widget)

        player_buttons_layout = QHBoxLayout()
        self.add_player_btn = QPushButton("Dodaj zawodnika")
        self.add_player_btn.clicked.connect(self.add_player)
        self.remove_player_btn = QPushButton("Usuń zawodnika")
        self.remove_player_btn.clicked.connect(self.remove_player)
        player_buttons_layout.addWidget(self.add_player_btn)
        player_buttons_layout.addWidget(self.remove_player_btn)
        players_layout.addLayout(player_buttons_layout)

        splitter.addWidget(teams_panel)
        splitter.addWidget(players_panel)
        main_layout.addWidget(splitter)

        start_panel_layout = QHBoxLayout()
        self.start_tournament_btn = QPushButton("Rozpocznij Turniej")
        self.start_tournament_btn.clicked.connect(self.start_tournament)
        self.generate_random_btn = QPushButton("Wygeneruj Losowy Turniej")
        self.generate_random_btn.clicked.connect(self.generate_random)
        start_panel_layout.addWidget(self.generate_random_btn)
        start_panel_layout.addWidget(self.start_tournament_btn)
        main_layout.addLayout(start_panel_layout)

        return widget

    def create_tournament_view_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.tabs_groups = QTabWidget()
        self.group_tables = {}
        for group_name in ["Grupa A", "Grupa B", "Grupa C", "Grupa D"]:
            table = QTableWidget()
            self.group_tables[group_name] = table
            self.tabs_groups.addTab(table, group_name)
        self.knockout_tab = QTextBrowser()
        self.knockout_tab.setFont(QFont("Courier New", 10))
        self.tabs_groups.addTab(self.knockout_tab, "Drabinka Pucharowa")
        layout.addWidget(self.tabs_groups)
        return widget

    def create_player_stats_widget(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        scorers_layout = QVBoxLayout()
        scorers_layout.addWidget(QLabel("<h3>Najlepsi Strzelcy</h3>"))
        self.scorers_table = QTableWidget()
        scorers_layout.addWidget(self.scorers_table)

        cards_layout = QVBoxLayout()
        cards_layout.addWidget(QLabel("<h3>Żółte Kartki</h3>"))
        self.yellow_cards_table = QTableWidget()
        cards_layout.addWidget(self.yellow_cards_table)
        cards_layout.addWidget(QLabel("<h3>Czerwone Kartki</h3>"))
        self.red_cards_table = QTableWidget()
        cards_layout.addWidget(self.red_cards_table)

        layout.addLayout(scorers_layout, 2)
        layout.addLayout(cards_layout, 1)
        return widget

    def create_results_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("<h2>Szczegółowe wyniki meczów</h2>"))
        self.results_table = QTableWidget()
        layout.addWidget(self.results_table)
        return widget

    def add_team(self):
        name, ok = QInputDialog.getText(self, "Dodaj drużynę", "Nazwa drużyny:")
        if ok and name.strip():
            try:
                self.tournament.add_team(name.strip())
                logging.debug(f"Dodano drużynę: {name.strip()}")
                self.refresh_all_views()
            except ValueError as e:
                QMessageBox.warning(self, "Błąd", str(e))

    def remove_team(self):
        selected_items = self.teams_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Błąd", "Najpierw zaznacz drużynę do usunięcia.")
            return
        team_name = selected_items[0].text()
        reply = QMessageBox.question(self, "Potwierdzenie", f"Czy na pewno chcesz usunąć drużynę '{team_name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.tournament.remove_team(team_name)
                logging.debug(f"Usunięto drużynę: {team_name}")
                self.refresh_all_views()
            except ValueError as e:
                QMessageBox.warning(self, "Błąd", str(e))

    def add_player(self):
        selected_teams = self.teams_list_widget.selectedItems()
        if not selected_teams:
            QMessageBox.warning(self, "Błąd", "Najpierw zaznacz drużynę, do której chcesz dodać zawodnika.")
            return
        team_name = selected_teams[0].text()
        team = next((t for t in self.tournament.teams if t.name == team_name), None)
        if team:
            dialog = AddPlayerDialog(self)
            if dialog.exec():
                first_name, last_name = dialog.get_data()
                if first_name and last_name:
                    try:
                        team.add_player(first_name, last_name)
                        logging.debug(f"Dodano zawodnika: {first_name} {last_name} do {team_name}")
                        self.update_player_list()
                    except ValueError as e:
                        QMessageBox.warning(self, "Błąd", str(e))

    def remove_player(self):
        selected_players = self.players_list_widget.selectedItems()
        selected_teams = self.teams_list_widget.selectedItems()
        if not selected_teams or not selected_players:
            QMessageBox.warning(self, "Błąd", "Zaznacz drużynę i zawodnika do usunięcia.")
            return

        team_name = selected_teams[0].text()
        player_name = selected_players[0].text()
        team = next(t for t in self.tournament.teams if t.name == team_name)

        reply = QMessageBox.question(self, "Potwierdzenie", f"Czy na pewno chcesz usunąć zawodnika '{player_name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                team.remove_player(player_name)
                logging.debug(f"Usunięto zawodnika: {player_name}")
                self.update_player_list()
            except ValueError as e:
                QMessageBox.warning(self, "Błąd", str(e))

    def start_tournament(self):
        try:
            self.tournament.start_tournament()
            logging.info("Turniej został rozpoczęty.")
            filename = f"teams_snapshot_round0.json"
            message = self.tournament.export_teams_to_json(filename)
            logging.info(message)
            QMessageBox.information(self, "Start", "Turniej został rozpoczęty!")
            self.refresh_all_views()
            self.main_tabs.setCurrentIndex(1)
        except ValueError as e:
            QMessageBox.critical(self, "Błąd startu", str(e))

    def generate_random(self):
        reply = QMessageBox.question(self, "Potwierdzenie",
                                     "Spowoduje to usunięcie wszystkich obecnych drużyn i rozpoczęcie nowego, losowego turnieju. Kontynuować?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.tournament.generate_random_tournament()
            logging.info("Wygenerowano losowy turniej.")
            filename = f"teams_snapshot_random.json"
            message = self.tournament.export_teams_to_json(filename)
            logging.info(message)
            QMessageBox.information(self, "Sukces", "Wygenerowano i rozpoczęto losowy turniej.")
            self.refresh_all_views()
            self.main_tabs.setCurrentIndex(1)

    def run_simulation(self):
        message = self.tournament.simulate_next_round()
        logging.info(f"Symulacja: {message}")

        self.refresh_all_views()
        QMessageBox.information(self, "Wynik symulacji", message)

        if self.tournament.winner:
            QMessageBox.information(self, "Koniec Turnieju",
                                    "Turniej zakończony! Generuję podsumowanie w konsoli...")


            QApplication.processEvents()

            print("\n" + "=" * 25)
            print("TURNIEJ ZAKOŃCZONY! GENEROWANIE PODSUMOWANIA W KONSOLI...")
            print("=" * 25)

            try:
                if self.tournament.all_players:
                    reporter = PlayerStatsReporter(self.tournament.all_players)
                    reporter.display_full_stats_table()
                    reporter.display_top_scorers()
                    reporter.display_card_offenders()
                else:
                    print("Brak zawodników do wygenerowania raportu.")

                print("\nPodsumowanie dostępne w konsoli, w której uruchomiono aplikację.")
                print("=" * 25 + "\n")
            except Exception as e:
                print(f"Wystąpił nieoczekiwany błąd podczas generowania raportu: {e}")
                logging.error(f"Błąd w raporcie konsolowym: {e}")



    def reset_tournament(self):
        self.tournament.reset_to_setup()
        logging.info("Turniej zresetowany.")
        self.refresh_all_views()
        QMessageBox.information(self, "Reset", "Turniej został zresetowany do fazy konfiguracji.")

    def refresh_all_views(self):
        self.update_ui_state()
        self.update_management_lists()
        self.update_status_label()
        if self.tournament.phase != "SETUP":
            for group_name, table in self.group_tables.items(): self.populate_group_table(group_name, table)
            self.populate_knockout_tab()
            self.populate_player_stats_tables()
            self.populate_results_table()

    def update_ui_state(self):
        is_setup_phase = self.tournament.phase == "SETUP"
        is_finished = self.tournament.winner is not None

        # Zakładki
        self.main_tabs.setTabEnabled(0, is_setup_phase)  # Zarządzanie
        self.main_tabs.setTabEnabled(1, not is_setup_phase)  # Turniej
        self.main_tabs.setTabEnabled(2, not is_setup_phase)  # Statystyki
        self.main_tabs.setTabEnabled(3, not is_setup_phase)  # Wyniki

        # Przyciski
        self.simulate_btn.setEnabled(not is_setup_phase and not is_finished)
        self.start_tournament_btn.setEnabled(is_setup_phase and len(self.tournament.teams) == 16 and all(
            len(t.players) == 11 for t in self.tournament.teams))

    def update_management_lists(self):
        # Lista drużyn
        self.teams_list_widget.clear()
        self.teams_list_widget.addItems([team.name for team in self.tournament.teams])
        self.teams_list_widget.parent().findChild(QLabel).setText(f"<h3>Drużyny ({len(self.tournament.teams)}/16)</h3>")

        # Lista zawodników
        self.update_player_list()

    def update_player_list(self):
        self.players_list_widget.clear()
        selected_items = self.teams_list_widget.selectedItems()
        if selected_items:
            team_name = selected_items[0].text()
            team = next((t for t in self.tournament.teams if t.name == team_name), None)
            if team:
                self.players_list_widget.addItems([player.name for player in team.players])
                self.players_label.setText(f"<h3>Zawodnicy w {team_name} ({len(team.players)}/11)</h3>")
        else:
            self.players_label.setText("<h3>Zawodnicy w wybranej drużynie</h3>")

    def update_status_label(self):
        if self.tournament.phase == "SETUP":
            text = "Faza Konfiguracji: Dodaj drużyny i zawodników"
        elif self.tournament.winner:
            winner_text = f"🏆 MISTRZ: {self.tournament.winner.name}! 🏆"
            top_scorers = self.tournament.top_scorer
            scorer_text = ""
            if top_scorers: scorers_names = ", ".join([s.name for s in
                                                       top_scorers]); scorer_text = f" | 👑 Król Strzelców: {scorers_names} ({top_scorers[0].goals} goli)"
            text = f"{winner_text}{scorer_text}"
        elif self.tournament.phase == "GROUP_STAGE":
            text = f"Faza grupowa: Kolejka {self.tournament.current_round}/6"
        else:
            text = f"Faza pucharowa: {['Quarter-finals', 'Semi-finals', 'Final'][self.tournament.current_round]}"
        self.status_label.setText(text)

    def populate_group_table(self, group_name, table):
        if group_name not in self.tournament.groups: return
        teams = sorted(self.tournament.groups[group_name], key=lambda t: (t.points, t.goal_difference, t.goals_for),
                       reverse=True)
        headers = ['#', 'Drużyna', 'M', 'Pkt', 'Z', 'R', 'P', 'B+', 'B-', '+/-']
        data = [[i + 1, t.name, t.matches_played, t.points, t.wins, t.draws, t.losses, t.goals_for, t.goals_against,
                 f"{t.goal_difference:+d}"] for i, t in enumerate(teams)]
        self.populate_table(table, headers, data)

    def populate_player_stats_tables(self):
        players = self.tournament.all_players;
        scorers = sorted([p for p in players if p.goals > 0], key=lambda p: p.goals, reverse=True);
        self.populate_table(self.scorers_table, ["Gracz", "Drużyna", "Gole"],
                            [[p.name, p.team_name, p.goals] for p in scorers])
        yellows = sorted([p for p in players if p.yellow_cards > 0], key=lambda p: p.yellow_cards, reverse=True);
        self.populate_table(self.yellow_cards_table, ["Gracz", "Drużyna", "ŻK"],
                            [[p.name, p.team_name, p.yellow_cards] for p in yellows])
        reds = sorted([p for p in players if p.red_cards > 0], key=lambda p: p.red_cards, reverse=True);
        self.populate_table(self.red_cards_table, ["Gracz", "Drużyna", "CZK"],
                            [[p.name, p.team_name, p.red_cards] for p in reds])

    def populate_results_table(self):
        played_matches = [m for m in self.tournament.matches if m.is_played] + [m for r in
                                                                                self.tournament.knockout_matches.values()
                                                                                for m in r if m.is_played]
        headers = ["Mecz", "Wynik", "Strzelcy goli"];
        data = []
        for match in sorted(played_matches, key=lambda m: (m.phase, m.round)):
            scorers_list = [f"{event['player'].name} ({event['minute']}')" for event in match.events if
                            event['type'] == 'GOAL'];
            scorers_str = ", ".join(scorers_list) if scorers_list else "Brak"
            data.append([f"{match.team1.name} vs {match.team2.name}", f"{match.score1} - {match.score2}", scorers_str])
        self.populate_table(self.results_table, headers, data);
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents);
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)

    def populate_knockout_tab(self):
        html = "<h1>Drabinka Pucharowa</h1>"
        for round_name in ["Quarter-finals", "Semi-finals", "Final"]:
            if round_name in self.tournament.knockout_matches:
                html += f"<h2>{round_name.replace('-', ' ')}</h2><ul>"
                for match in self.tournament.knockout_matches[round_name]:
                    if match.is_played:
                        team1_str = f"<b>{match.team1.name}</b>" if match.winner == match.team1 else match.team1.name;
                        team2_str = f"<b>{match.team2.name}</b>" if match.winner == match.team2 else match.team2.name
                        html += f"<li>{team1_str} {match.score1} - {match.score2} {team2_str}</li>"
                    else:
                        html += f"<li>{match.team1.name} vs {match.team2.name}</li>"
                html += "</ul>"
        if self.tournament.winner:
            scorer_html = "";
            top_scorers = self.tournament.top_scorer
            if top_scorers: scorers_names = ", ".join([s.name for s in
                                                       top_scorers]); scorer_html = f"<h3>👑 Król Strzelców: {scorers_names} ({top_scorers[0].goals} goli)</h3>"
            html += f"<hr><h1>🏆 Zwycięzca: {self.tournament.winner.name} 🏆</h1>{scorer_html}"
        self.knockout_tab.setHtml(html)

    def populate_table(self, table, headers, data):
        table.setColumnCount(len(headers));
        table.setHorizontalHeaderLabels(headers);
        table.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            for col_idx, cell_data in enumerate(row_data): table.setItem(row_idx, col_idx,
                                                                         QTableWidgetItem(str(cell_data)))
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch);

        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def save_tournament_state(self):
        """Otwiera okno dialogowe do zapisu stanu turnieju w pliku .json."""
        filename, _ = QFileDialog.getSaveFileName(self, "Zapisz turniej", "", "Pliki JSON (*.json)")

        if filename:
            try:
                self.tournament.save_to_file(filename)
                QMessageBox.information(self, "Sukces", f"Turniej został pomyślnie zapisany w pliku:\n{filename}")
                logging.info(f"Zapisano stan turnieju do {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Błąd zapisu", f"Nie udało się zapisać pliku: {e}")
                logging.error(f"Błąd podczas zapisu do pliku {filename}: {e}")

    def load_tournament_state(self):
        """Otwiera okno dialogowe do wczytania stanu turnieju z pliku .json."""
        reply = QMessageBox.question(self, "Potwierdzenie",
                                     "Spowoduje to nadpisanie obecnego stanu turnieju. Kontynuować?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.No:
            return

        filename, _ = QFileDialog.getOpenFileName(self, "Wczytaj turniej", "", "Pliki JSON (*.json)")

        if filename:
            try:
                self.tournament.load_from_file(filename)
                self.refresh_all_views()
                QMessageBox.information(self, "Sukces", "Turniej został pomyślnie wczytany.")
                logging.info(f"Wczytano stan turnieju z {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Błąd wczytywania", f"Nie udało się wczytać pliku: {e}")
                logging.error(f"Błąd podczas wczytywania pliku {filename}: {e}")

    def create_visualization_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Kontener na przyciski
        buttons_layout = QHBoxLayout()
        self.generate_chart_btn = QPushButton("Generuj wykres najlepszych strzelców")
        self.generate_chart_btn.clicked.connect(self.generate_scorers_chart)

        self.save_chart_btn = QPushButton("Zapisz wykres jako...")
        self.save_chart_btn.clicked.connect(self.save_chart_as)
        self.save_chart_btn.setEnabled(False)  # Przycisk jest nieaktywny na początku

        buttons_layout.addWidget(self.generate_chart_btn)
        buttons_layout.addWidget(self.save_chart_btn)
        buttons_layout.addStretch()

        # Etykieta, w której wyświetlimy wykres
        self.chart_label = QLabel("Kliknij 'Generuj...', aby wyświetlić wykres.")
        self.chart_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chart_label.setFont(QFont("Arial", 14))

        layout.addLayout(buttons_layout)
        layout.addWidget(self.chart_label)

        # Przechowamy ścieżkę do wygenerowanego pliku
        self.current_chart_path = None

        return widget

    def generate_scorers_chart(self):
        """Generuje wykres słupkowy dla 10 najlepszych strzelców, zapisuje go
        do tymczasowego pliku i wyświetla w aplikacji."""


        all_scorers = [p for p in self.tournament.all_players if p.goals > 0]

        if not all_scorers:
            QMessageBox.warning(self, "Brak danych", "Brak strzelców do wyświetlenia na wykresie.")
            return

        sorted_scorers = sorted(all_scorers, key=lambda p: p.goals, reverse=True)

        top_10_scorers = sorted_scorers[:10]


        player_names = [p.name for p in top_10_scorers]
        player_goals = [p.goals for p in top_10_scorers]

        plt.figure(figsize=(12, 7))
        sns.set_style("whitegrid")  #

        bar_plot = sns.barplot(x=player_goals, y=player_names, palette="viridis", orient='h')

        plt.xlabel("Liczba goli", fontsize=12)
        plt.ylabel("Zawodnik", fontsize=12)
        plt.title("Najlepsi Strzelcy Turnieju", fontsize=16, weight='bold')
        plt.tight_layout()

        self.current_chart_path = "top_scorers_chart.png"
        try:
            plt.savefig(self.current_chart_path)
            logging.info(f"Wykres zapisany tymczasowo jako {self.current_chart_path}")
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się zapisać wykresu: {e}")
            return
        finally:
            plt.close()

        pixmap = QPixmap(self.current_chart_path)
        self.chart_label.setPixmap(pixmap.scaled(self.chart_label.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                                 Qt.TransformationMode.SmoothTransformation))

        self.save_chart_btn.setEnabled(True)

    def save_chart_as(self):
        if not self.current_chart_path:
            QMessageBox.warning(self, "Brak wykresu", "Najpierw wygeneruj wykres.")
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Zapisz wykres jako...",
            "najlepsi_strzelcy.png",
            "Pliki obrazów (*.png *.jpg)"
        )

        if save_path:
            try:
                shutil.copy(self.current_chart_path, save_path)
                QMessageBox.information(self, "Sukces", f"Wykres został zapisany w:\n{save_path}")
                logging.info(f"Użytkownik zapisał wykres jako {save_path}")
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Nie udało się zapisać pliku: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TournamentApp()
    window.show()
    sys.exit(app.exec())
