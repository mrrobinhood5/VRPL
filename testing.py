import asyncio
import random
from datetime import datetime, timedelta
from pprint import pp
from utils import all_models
from database import Database
from discord import Embed

from beanie import init_beanie, WriteRules
from beanie.operators import In, Where, ElemMatch
from beanie.odm.fields import Link
from bson.dbref import DBRef
from models import *
from testing_utils.old_utils import generate_link, get_discord_ids, generate_username, make_member_id, generate_team_name, generate_guid, generate_description
from random import randrange

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


async def create_players(game, number):
    ids = get_discord_ids()
    for _ in range(number):
        await NormalPlayer(games=[game], discord_id=next(ids), name=generate_username(), game_uid=generate_guid(),
                           height=randrange(4, 6), location=random.choice(list(Location))).save()


async def create_teams(game, players) -> list:
    teams = []
    for player in players:
        captain = CaptainPlayer(**player.dict())
        (await player.delete(), await captain.save())
        teams.append(await StandardTeam(game = game, name=generate_team_name(), region=random.choice(list(Region)),
                                        motto=generate_description(), members=[captain]).insert())
    return teams


async def build_teams(teams, players):
    for team in teams:
        for _ in range(4):
            team.members.append(players.pop()) if players else 0
        for member in team.members:
            if isinstance(member, NormalPlayer):
                cocaptain = CoCaptainPlayer(**member.dict())
                (await member.delete(), await cocaptain.save(), team.members.pop(team.members.index(member)))
                team.members.append(cocaptain)
                break
        await team.save()

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
    models = all_models()
    await init_beanie(database=db, document_models=models)

    # create a game
    game = await Game(name="Contractor$").insert()


    # create Players if there are none already
    players = await PlayerBase.find_all(with_children=True).to_list()
    if not players:
        await create_players(game, 20)

    # make a teams if no teams already exists
    teams = await TeamBase.find_all(with_children=True).to_list()
    if not teams:
        players = [player for player in players if issubclass(NormalPlayer, player)]
        teams = await create_teams(game, players[:4])

        # add the rest of the players to the team
        await build_teams(teams, await NormalPlayer.find({}, with_children=True).to_list())

    # make one a caster request
    casters = await CasterBase.find_all(with_children=True).to_list()
    if not casters:
        await make_caster_request(game, await NormalPlayer.find({}).first_or_none())

        # approve caster approval
        await process_approval(await CasterRequestApproval.find({}, fetch_links=True).first_or_none())

    maps = await MapBase.find_all(with_children=True).to_list()
    if not maps:
        # make some maps
        maps = await make_maps(game, 4)


    # make a tournament
    # await reset_db(db, 'TournamentBase')
    # await reset_db(db, 'WeekBase')
    # await reset_db(db, 'MatchBase')
    tournaments = await TournamentBase.find_all(with_children=True).to_list()
    if not tournaments:
        tournament = await make_tournament(game, await TeamBase.find_all(with_children=True).to_list(), maps)

    # start a weeks
    weeks = await WeekBase.find_all(with_children=True).to_list()
    if not weeks:
        tournament = await make_weeks(tournament, 7)

    # make all matches in a week
    matches = await MatchBase.find_all(with_children=True).to_list()
    if not matches:
        week = await make_matches(tournament, 1)

    # make approvals for the matches
    approvals = await ApprovalBase.find_all().to_list()
    if not approvals:
        approvals = await schedule_matches(game=game, week=await WeekBase.find(WeekBase.order == 1, with_children=True, fetch_links=True).first_or_none())
        async for approval in MatchDateApproval.find_all(with_children=True, fetch_links=True):
            await process_approval(approval)

async def quicktest():
    db = Database().db
    models = all_models()
    await init_beanie(database=db, document_models=models)

    # create a game
    game = await GameBase.find({}, with_children=True, fetch_links=True).first_or_none()
    pp(game.matches)


if __name__ == "__main__":
    asyncio.run(quicktest())
