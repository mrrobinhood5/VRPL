from __future__ import annotations
from base_classes import *
from errors import TournamentError, TeamError
from testing_utils.test_data import seasons, games, c_tournaments
# from random import randint
from testing_utils.utils import *

# Generate players
for x in range(0, 500):
    Player(game_uid=generate_guid(),
           name=generate_username())

# choose 50 players to be captains and make teams
for x in range(0, 50):
    try:
        Team(name=generate_team_name(),
             description=generate_description(),
             captain=Player.instances()[x].id,
             )
    except TeamError as e:
        print(f'Error creating team: {e}')

# go through the rest of the players to make teams
for player in Player.instances():
    try:
        player.join_team(Team.instances()[randint(0, len(Team.instances()) - 1)])
    except TeamError as e:
        print(f'Team error: {e}')

# have captains choose co-captains
for team in Team.instances():
    try:
        team.make_co_captain(team.captain, team.players[randint(0, len(team.players) - 1)].id)
    except TeamError as e:
        print(f"Error Making Co Captain: {e}")

# define test seasons, games and tournaments
for season in seasons:
    Season(**season)

for game in games:
    Game(**game)

for tournament in c_tournaments:
    try:
        Tournament(**tournament,
                   belongs_to_game=Game.get('con').id,
                   belongs_to_season=Season.get('2').id)
    except TournamentError as e:
        print(f'Error creating tournament: {e}')

# random players join the 1v1 tournament
singles_tournament = Tournament.get('1v1')
for player in Player.instances():
    _ = randint(0, 1)
    if _:
        player.join_tournament(singles_tournament)

# team captains join the other team tournaments
for team in Team.instances():
    try:
        team.join_tournament(team.captain, Tournament.instances()[randint(0, len(Tournament.instances())-1)])
    except TournamentError as e:
        print(f'Tournament error: {e}')


# Statistics
total_seasons = Season.count()
total_games = Game.count()
total_tournaments = Tournament.count()
active_tournaments = len([x for x in Tournament.instances() if x.active])
total_teams = Team.count()
active_teams = len([x for x in Team.instances() if x.active])
total_players = Player.count()
teamed_players = len([x for x in Player.instances() if x.belongs_to_team])

stats = f'VRCL test data: \n\n' \
        f'There are {total_seasons} Seasons configured \n' \
        f'There are {total_games} Games configured \n' \
        f'There are {total_tournaments} Tournaments, {active_tournaments} of them are active\n' \
        f'We have {total_teams} teams registered, of which {active_teams} are active\n' \
        f'We have {total_players} players registered, {teamed_players} are in teams' \
        f'\n\n'
for season in Season.instances():
    stats += f'{season.name}: {season.description}\n'
    for tournament in season.tournaments:
        stats += f'\t{tournament.name} ({Game.lookup(tournament.belongs_to_game).name}): {tournament.description}\n'
        if tournament.individual:
            for player in tournament.players:
                stats += f'\t \t{player.name}\n'
        else:
            for team in tournament.teams:
                stats += f'\t \t{team.name} : {team.description}\n'
                for player in team.players:
                    stats += f'\t \t \t {player.name}'
                    if player.id is team.captain:
                        stats += f' (Captain)\n'
                    elif player.id is team.co_captain:
                        stats += f' (Co-Captain)\n'
                    else:
                        stats += f'\n'

print(stats)


# TODO: IMPLEMENT TRANSACTION LOG
# TODO: I COMPLETELY FORGOT ABOUT DIVISIONS
