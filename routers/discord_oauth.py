from fastapi import APIRouter, Depends
from fastapi.exception_handlers import JSONResponse
from fastapi_discord import DiscordOAuthClient, RateLimited, Unauthorized, User
from fastapi_discord.models import GuildPreview
from typing import List

router = APIRouter(tags=['discord'], prefix='')

discord = DiscordOAuthClient(
    client_id='1111121560007364638',
    client_secret='zKR2OL0IfPk7JZ7imFU8uhSPye-8o4AZ',
    redirect_uri='http://136.50.242.109:8080/callback',
    scopes=('identify', 'guilds', 'email')
)


@router.get('/login')
async def login():
    await discord.init()
    return {"url": discord.oauth_login_url}


@router.get("/callback")
async def callback(code: str):
    token, refresh_token = await discord.get_access_token(code)
    return {"access_token": token, "refresh_token": refresh_token}


@router.get("/authenticated", dependencies=[Depends(discord.requires_authorization)], response_model=bool,)
async def isAuthenticated(token: str = Depends(discord.get_token)):
    try:
        auth = await discord.isAuthenticated(token)
        return auth
    except Unauthorized:
        return False


@router.get("/user", dependencies=[Depends(discord.requires_authorization)], response_model=User)
async def get_user(user: User = Depends(discord.user)):
    return user


@router.get("/guilds", dependencies=[Depends(discord.requires_authorization)], response_model=List[GuildPreview])
async def get_guilds(guilds: List = Depends(discord.guilds)):
    return guilds
