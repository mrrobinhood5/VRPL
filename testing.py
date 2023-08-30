import asyncio
from datetime import datetime
from pprint import pp
from utils import all_models
from database import Database
from discord import Embed

from beanie import init_beanie, WriteRules
from beanie.operators import In, Where, ElemMatch
from beanie.odm.fields import Link
from bson.dbref import DBRef
from models import *


async def reset_db(db):
    for collection in await db.list_collection_names():
        await db[collection].drop()


async def create_players():
    if not await PlayerBase.find_all().to_list():
        player_1 = NormalPlayer(discord_id=188481379305127936,
                                name='Player One',
                                game_uid='gxq789asg123',
                                height=5.2,
                                location=Location.US)
        player_2 = NormalPlayer(discord_id=960435300037967913,
                                name='Player Two',
                                game_uid='123adsf546g',
                                height=4.0,
                                location=Location.SA)
        player_3 = NormalPlayer(discord_id=1055872495451914270,
                                name='Player Three',
                                game_uid='7868xagdsasfd',
                                height=5.0,
                                location=Location.US)
        player_4 = NormalPlayer(discord_id=552891061471805444,
                                name='Player Four',
                                game_uid='3464573fhsdfsd',
                                height=5.1,
                                location=Location.JP)
        player_5 = NormalPlayer(discord_id=388371441474863114,
                                name='Player Five',
                                game_uid='1335adfa342',
                                height=4.2,
                                location=Location.NZ)
        await NormalPlayer.insert_many([player_5, player_4, player_3, player_2, player_1])


async def create_team(player):
    captain = CaptainPlayer(**player.dict())
    (await player.delete(), await captain.save())

    team_1 = StandardTeam(name="Great Team",
                          region=Region.NA,
                          motto="My Great Motto",
                          members=[captain])
    await team_1.save()
    return team_1


async def build_team(team, players):
    for player in players:
        if isinstance(player, NormalPlayer):
            team.members.append(player)
    for member in team.members:
        if isinstance(member, NormalPlayer):
            cocaptain = CoCaptainPlayer(**member.dict())
            (await member.delete(), await cocaptain.save())
            team.members.append(cocaptain)
            break
    await team.save()

async def make_caster_request():
    players = await PlayerBase.find({}, with_children=True).to_list()
    for player in players:
        if isinstance(player, NormalPlayer):
            caster = Caster(links=['https://www.twitch.tv/k1nggam355'],
                            player=player)
            requestor = player
            await caster.save()
            break
    approver = [player for player in players if player.captain]
    approval = CasterRequestApproval(requestor=requestor,
                                     target=caster,
                                     approver=approver[0])
    await approval.save()

async def approve_caster():
    approval = await CasterRequestApproval.find({}, fetch_links=True).first_or_none()

    if not approval:
        print('No approvals')
    else:
        await approval.target.set({approval.property:approval.action})

    approval = await CasterRequestApproval.find({}, fetch_links=True).first_or_none()
    pp(approval.target)


async def main():
    db = Database().db
    await reset_db(db)
    models = all_models()
    await init_beanie(database=db, document_models=models)

    # create 5 normal Players
    await create_players()

    # make a team, make one captain
    team = await create_team(await PlayerBase.find_all(with_children=True).first_or_none())

    # add the rest of the players to the team
    await build_team(team, await PlayerBase.find({}, with_children=True).to_list())

    # make one a caster request
    await make_caster_request()

    # approve caster approval
    await approve_caster()

if __name__ == "__main__":
    asyncio.run(main())
