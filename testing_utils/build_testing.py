from __future__ import annotations
from base_classes import *
from errors import TournamentError, TeamError, DivisionError
from testing_utils.test_data import seasons, games, c_tournaments, divisions
# from random import randint
from database import db
from testing_utils.utils import *
from rich.progress import track
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.text import Text

main_console = Console()
secondary_console = Console()
logger = TransactionLogger()

players = 500
captains = 50

main_console.rule(title='Generators', characters='-')

# define test seasons, games and tournaments
for season in seasons:
    Season(**season,
           logger=logger)

for game in games:
    Game(**game,
         logger=logger)

for tournament in track(c_tournaments,
                        description='Making Tournaments'):
    try:
        Tournament(**tournament,
                   belongs_to_game=Game.get('con')[0].id,
                   belongs_to_season=Season.get('2')[0].id,
                   logger=logger)
    except TournamentError as e:
        pass
        # print(f'Error creating tournament: {e}')

for division in track(divisions,
                      description='Making Divisions'):
    try:
        Division(**division,
                 belongs_to_tournament=Tournament.get('comp')[0],
                 logger=logger)
    except DivisionError as e:
        pass

# Generate players
for x in track(range(0, 500),
               description=f'Generating {players} Players',
               console=main_console,
               refresh_per_second=50):
    Player(game_uid=generate_guid(),
           name=generate_username(),
           logger=logger)

# choose 50 players to be captains and make teams
for x in track(range(0, 50),
               description=f'Choosing {captains} Captains'):
    try:
        Team(name=generate_team_name(),
             description=generate_description(),
             captain=Player.instances()[x].id,
             logger=logger,
             belongs_to_division=Division.instances()[randint(0,1)]
             )
    except TeamError as e:
        pass
        # print(f'Error creating team: {e}')

# go through the rest of the players to make teams
for player in track(Player.instances(),
                    description='Assigning Players to Teams'):
    try:
        player.join_team(Team.instances()[randint(0, len(Team.instances()) - 1)])
    except TeamError as e:
        pass
        # print(f'Team error: {e}')

# have captains choose co-captains
for team in track(Team.instances(),
                  description='Choosing Co-Captains'):
    try:
        team.make_co_captain(team.captain, team.players[randint(0, len(team.players) - 1)].id)
    except TeamError as e:
        pass
        # print(f"Error Making Co Captain: {e}")


# random players join the 1v1 tournament
singles_tournament = Tournament.get('1v1')[0]
for player in track(Player.instances(),
                    description='Players Joining 1v1 Tournament'):
    _ = randint(0, 1)
    if _:
        player.join_tournament(singles_tournament)

# team captains join the other team tournaments
for team in track(Team.instances(),
                  description='Captains Joining Team Tournaments'):
    try:
        team.join_tournament(team.captain, Tournament.instances()[randint(0, len(Tournament.instances())-1)])
    except TournamentError as e:
        pass
        # print(f'Tournament error: {e}')


# Statistics
# vrcl = Tree(label='VREL',)
#
# secondary_console.rule(title='Statistics',
#                        characters='-')
#
# for season in Season.instances():
#     s_tree = Tree(label=season.name)
#     vrcl.add(s_tree)
#     for tournament in season.tournaments:
#         t_tree = Tree(label=tournament.name)
#         s_tree.add(t_tree)
#         for team in tournament.teams:
#             team_tree = Tree(label=f'{team.name} - {team.belongs_to_division.name}')
#             t_tree.add(team_tree)
#             for player in team.players:
#                 team_tree.add(Text(f'{player.name}{" - Captain" if team.captain is player.id else " - Co-Captain" if team.co_captain is player.id else ""}'))
#
# secondary_console.print(vrcl)
vrcl = {}
for season in Season.instances():
    vrcl.update({season.name: {}})
    for tournament in season.tournaments:
        if '1v1' in tournament.name:
            vrcl[season.name].update({tournament.name: []})
            for player in tournament.players:
                vrcl[season.name][tournament.name].append(player.name)
        else:
            vrcl[season.name].update({tournament.name:{}})
        for team in tournament.teams:
            vrcl[season.name][tournament.name].update({f'{team.name}-{team.belongs_to_division.name}':[]})
            for player in team.players:
                vrcl[season.name][tournament.name][f'{team.name}-{team.belongs_to_division.name}'].append(f'{player.name}{" - Captain" if team.captain == player.id else " - Co-Captain" if team.co_captain == player.id else ""}')

# TODO: IMPLEMENT TRANSACTION LOG
# TODO: IMPLEMENT BANS
# TODO: IMPLEMENT TEAM POINTS (OR POINT SYSTEM)
# TODO: IMPLEMENT TOURNAMENT ROUNDS
# TODO: IMPLEMENT MAP SELECTION (IS IT BY WEEK? OR IT DEPENDS ON
# TODO: IMPLEMENT SUSPENSIONS
# TODO: IMPLEMENT OFFENCES
# TODO: IMPLEMENT PLAYER WARNINGS