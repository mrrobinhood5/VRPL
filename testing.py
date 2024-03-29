import asyncio
import pprint
import random
from datetime import timedelta
from functools import wraps

import discord
import iso3166

from utils import all_models
from database import Database


from beanie import init_beanie, WriteRules
from engines import *
from testing_utils.old_utils import generate_link, get_discord_ids, generate_username, make_member_id, generate_team_name, generate_guid, generate_description
from random import randrange
from monggregate import Pipeline, S
import time

ids = get_discord_ids()
def random_date(start, end):
    r = end - start
    d = random.randint(0, r.days)
    return start + timedelta(days=d)

async def reset_db(db, collection = None):
    if not collection:
        for collection in await db.list_collection_names():
            await db[collection].drop()
    else:
        await db[collection].drop()


def generate_player(game):
    return {'games': [game], 'discord_id': next(ids), 'name': generate_username(), 'game_uid': generate_guid(),
            'height': randrange(4, 6), 'location': random.choice([c.name for c in iso3166.countries])}


def generate_team(game, captain):
    return {'game': game, 'name': generate_team_name(), 'region': random.choice(list(Region)),
            'motto': generate_description(), 'members':[captain]}


#
# async def build_teams(teams, players):
#     for team in teams:
#         for _ in range(4):
#             team.members.append(players.pop()) if players else 0
#         for member in team.members:
#             if isinstance(member, NormalPlayer):
#                 cocaptain = CoCaptainPlayer(**member.dict())
#                 (await member.delete(), await cocaptain.save(), team.members.pop(team.members.index(member)))
#                 team.members.append(cocaptain)
#                 break
#         await team.save()

async def make_caster_request(game, player):
    caster = Caster(game=game, links=['https://www.twitch.tv/k1nggam355'], player=player)
    await caster.save()

    approver = await CaptainPlayer.find({}).first_or_none()
    approval = CasterRequestApproval(game=game, requestor=player, target=caster, approver=approver)
    await approval.save()

async def process_approval(approval):
    await approval.target.set({approval.property: approval.action})
    await approval.delete()

async def make_maps(game, number):
    maps = []
    for _ in range(number):
        map = MapBase(game=game, name=generate_username(), image=generate_link())
        maps.append(await map.insert())
    return maps

async def make_tournament(game, teams, maps) -> TournamentBase:
    _ = SwissSystemTeamCompTournament(name="Season 1 Comp Control League",
                                      game=game,
                                               description=generate_description(),
                                               next_round=datetime.now()+timedelta(days=1),
                                               start_date=datetime.now(),
                                               prizes='stuff n stuff',
                                               active=True,
                                               round_frequency=1,
                                               maps_per_round=2,
                                               no_repeat_maps_for= 2,
                                               participants=teams,
                                               maps=maps)
    t = await _.insert()
    t = await TournamentBase.find({}, fetch_links=True, with_children=True).first_or_none()
    await t.fetch_link('participants')
    return t

async def make_weeks(tournament, number) -> TournamentBase:
    week_number = 1
    start_date = datetime.now()
    for _ in range(number):
        next_week = start_date + timedelta(tournament.round_frequency)
        week = Week(order=week_number, start_date=start_date, end_date=next_week,
                    tournament=tournament, maps=random.sample(tournament.maps, 2))
        await week.insert(link_rule=WriteRules.WRITE)
        week_number += 1
        start_date = next_week

    return await TournamentBase.find({}, with_children=True, fetch_links=True).first_or_none()

async def make_matches(tournament, week = 1) -> WeekBase:
    # create matches equal to the number of teams divided by two
    week = await WeekBase.find(WeekBase.order == week, with_children=True).first_or_none()
    x = len(tournament.participants)
    x = x // 2

    # MMR thing needs to be updated.
    for _ in range(x):
        team1 = tournament.participants.pop()
        team2 = tournament.participants.pop()
        match = TeamMatch(week=week, tournament=tournament, maps=week.maps, participants=[team1, team2])
        await match.save()
    week = await WeekBase.find_one(WeekBase.id == week.id, fetch_links=True, with_children=True)
    return week

async def schedule_matches(game, week):
    for match in week.matches:
        await match.fetch_link('participants')
        match_date = random_date(week.start_date, week.end_date)
        requestor = match.participants[0].captain
        approver = match.participants[1].leadership
        approval = MatchDateApproval(game=game, requestor=requestor, target=match, property='match_date',
                                     action=match_date, approver=approver)
        await approval.save()
    return await ApprovalBase.find_all(with_children=True).to_list()

async def main():
    db = Database().db
    await reset_db(db)

    pe = PlayerEngine()
    te = TeamEngine()
    ge = GameEngine()

    models = all_models()

    st = time.time()
    await init_beanie(database=db, document_models=models)
    et = time.time()
    print(f'beanie loaded in {et - st}')


    # create a game
    game = await ge.create_function(document={'name': "Contractors"}, base=Game)

    # create Players if there are none already
    if not await pe.count(PlayerBase):
        for _ in range(40):
            await pe.register_player(**generate_player(game))
    players = pe.get_by()

    # make a teams if no teams already exists
    if not await te.count(TeamBase):
        for _ in range(8):
            c = await anext(players)
            captain = await pe.make_captain(c.item)
            await te.register_team(**generate_team(game, captain))

        normal_players = pe.get_by()
        teams = te.get_by()

        for x in range(await te.count(TeamBase)):
            p = await anext(normal_players)
            team = await anext(teams)
            co_cap = await pe.make_co_captain(p.item)
            await te.add_player(team=team.item, player=co_cap)
            for _ in range(3):
                p = await anext(normal_players)
                await te.add_player(team.item, p.item)

    games = ge.get_by(name='Contractors')
    for _ in range(await ge.count()):
        game = await anext(games)
        assert len(game.item.players) == 40
        assert len(game.item.teams) == 8

    # test_player = pe.get_by(captain=True)
    # print(anext(test_player.item).name)
    # test_player = test_player[0].name[2:5]
    # test_player = await pe.get_by_name(name=test_player)
    # print(test_player.name)



    #
    # # make one a caster request
    # casters = await CasterBase.find_all(with_children=True).to_list()
    # if not casters:
    #     await make_caster_request(game, await NormalPlayer.find({}).first_or_none())
    #
    #     # approve caster approval
    #     await process_approval(await CasterRequestApproval.find({}, fetch_links=True).first_or_none())
    #
    # maps = await MapBase.find_all(with_children=True).to_list()
    # if not maps:
    #     # make some maps
    #     maps = await make_maps(game, 4)
    #
    #
    # # make a tournament
    # # await reset_db(db, 'TournamentBase')
    # # await reset_db(db, 'WeekBase')
    # # await reset_db(db, 'MatchBase')
    # tournaments = await TournamentBase.find_all(with_children=True).to_list()
    # if not tournaments:
    #     tournament = await make_tournament(game, await TeamBase.find_all(with_children=True).to_list(), maps)
    #
    # # start a weeks
    # weeks = await WeekBase.find_all(with_children=True).to_list()
    # if not weeks:
    #     tournament = await make_weeks(tournament, 7)
    #
    # # make all matches in a week
    # matches = await MatchBase.find_all(with_children=True).to_list()
    # if not matches:
    #     week = await make_matches(tournament, 1)
    #
    # # make approvals for the matches
    # approvals = await ApprovalBase.find_all().to_list()
    # if not approvals:
    #     approvals = await schedule_matches(game=game, week=await WeekBase.find(WeekBase.order == 1, with_children=True, fetch_links=True).first_or_none())
    #     async for approval in MatchDateApproval.find_all(with_children=True, fetch_links=True):
    #         await process_approval(approval)

async def decorator_test():
    # db = Database().db

    # pe = PlayerEngine()
    # te = TeamEngine()
    # ge = GameEngine()


    # models = all_models()



    # st = time.time()
    # await init_beanie(database=db, document_models=[Player], recreate_views=True)
    # et = time.time()
    # print(f'beanie loaded in {et-st}')

    class Engine:

        @staticmethod
        def dashboard(child_dashboard):
            print(f'ONE # Ran when defined. variables here acutally go into the wrapper')
            a = 'a'
            @wraps(child_dashboard)
            async def wrapped_dashboard(self, /, *args, **kwargs):
                dashboard = discord.ui.View()
                dashboard.add_item(discord.ui.Button(label='Back'))
                print('FOUR # inside of method wrapper, calling the implemented method')
                dashboard = await child_dashboard(self, *args, **kwargs, dashboard=dashboard)
                print(f'SIX # returned from implemented method')
                print(f'a is {a}')
                return dashboard


            return wrapped_dashboard

    class GameEngine(Engine):

        def embed_maker(self) -> discord.Embed:
            embed = discord.Embed(title='test', description='test')
            return embed

        @Engine.dashboard
        async def dashboard(self, /, dashboard: discord.ui.View,  *args, **kwargs, ) -> discord.ui.View:
            print('FIVE # inside the implemented method')
            embed = self.embed_maker()
            dashboard.embed = embed
            dashboard.add_item(discord.ui.Button(label='Games'))

            return dashboard

    print('TWO # Right before instantiating the class')
    g = GameEngine()
    print(f'THREE # class instantiated, running the wrapped method')
    h = await g.dashboard(text='Custom Text')
    print(f'SEVEN # returned to main, from the call to the wrapped method')
    pprint.pp(h.children)
    pprint.pp(h.embed.to_dict())

    # order of things should be:
    # 1. call super dash and get a View instance
    # 2. superdash adds two buttons
    # 3. call class embeed maker to set default embed
    # 4. add child buttons
    # 5. return completed View

async def current_test():
    db = Database().db

    # pe = PlayerEngine()
    # te = TeamEngine()
    # ge = GameEngine()


    # models = all_models()

    class Todo(Document):
        description: str

    class TodoItem(Document):
        order: int
        todo: Link[Todo]

    class TodoList(Document):
        owner: str
        todos: List[TodoItem]



    st = time.time()
    await init_beanie(database=db, document_models=[Todo, TodoList, TodoItem], recreate_views=True)
    et = time.time()
    print(f'beanie loaded in {et-st}')


if __name__ == "__main__":
    asyncio.run(main())
