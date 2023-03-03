from __future__ import annotations
from base_classes import *
from errors import TournamentError, TeamError
from testing_utils.test_data import team_names, seasons, games, tournaments
from random import randint
from testing_utils.utils import *

# define test seasons

for season in seasons:
    Season(**season)

for game in games:
    Game(**game)

for tournament in tournaments:
    Tournament(**tournament,
               belongs_to_game=Game.instances()[randint(0, 1)],
               belongs_to_season=Season.instances()[randint(0, 1)])

# Generate 50 teams
for x in range(0, 50):
    try:
        Team(name=generate_team_name(),
             description=doc_gen.gen_sentence(min_words=10, max_words=25),
             captain=make_member_id(),
             co_captain=make_member_id(),
             belongs_to_tournament=Tournament.instances()[randint(0, len(Tournament.instances())-1)])
    except TournamentError as e:
        print(f"Error creating team: {e}")

# Generate 100 players
for x in range(0, 500):
    try:
        Player(game_uid=generate_guid(),
               name=generate_username(),
               belongs_to_team= [Team.instances()[randint(0, len(Team.instances())-1)], None][randint(0, 1)])
    except TeamError as e:
        print(f"Error joining the team")

# join the 1v1 tournament
singles_tournament = Tournament.get('1v1')
for player in Player.instances():
    _ = randint(0, 1)
    if _:
        player.join_tournament(singles_tournament)

# Statistics
total_seasons = Season.count()
total_games = Game.count()
total_tournaments = Tournament.count()
active_tournaments = len([x for x in Tournament.instances() if x.active])
total_teams = Team.count()
active_teams = len([x for x in Team.instances() if x.active])
total_players = Player.count()
teamed_players = len([x for x in Player.instances() if x.belongs_to_team])

stats =  f'VRCL test data: \n\n' \
         f'There are {total_seasons} Seasons configured \n' \
         f'There are {total_games} Games configured \n' \
         f'There are {total_tournaments} Tournaments, {active_tournaments} of them are active\n' \
         f'We have {total_teams} teams registered, of which {active_teams} are active' \
         f'We have {total_players} players registered, {teamed_players} are in teams' \
         f'\n\n'
for season in Season.instances():
    stats += f'{season.name}: {season.description}\n'
    for tournament in season.tournaments:
        stats += f'\t{tournament.name} ({tournament.belongs_to_game.name}): {tournament.description}\n'
        if tournament.individual:
            for player in tournament.players:
                stats += f'\t \t{player.name}\n'
        else:
            for team in tournament.teams:
                stats += f'\t \t{team.name} : {team.description}\n' \
                         f'\t \t \t Captain: {team.captain}\n' \
                         f'\t \t \t Co-Cap: {team.co_captain}\n'
                for player in team.players:
                    stats += f'\t \t \t {player.name}\n'

print(stats)

# TODO: Team captains and co captains need to be player objects
# TODO: Create all player objects before all
# TODO: add methods for players to join team / tournament
# TODO: add tournament limits
