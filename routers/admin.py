from fastapi import APIRouter, Body

from database import db, db_get_settings, db_add_one
from models.base import PyObjectId
from models.settings import SettingsModel, UpdateSettingsModel

router = APIRouter(tags=['admin'], prefix='/admin')


@router.get('/db_drop', response_description='Reset the WHOLE database')
async def drop_db():
    for coll in await db.list_collection_names():
        await db.drop_collection(coll)


@router.get('/get_settings', response_description='Get the discord server settings', response_model=SettingsModel)
async def get_settings():
    if (settings := await db_get_settings()) is None:
        _ = SettingsModel(**{"players_channel": None, "teams_channel": None, "name": ""})
        await db_add_one('settings', _)
        settings = _.dict()
    return settings


@router.put('/set_settings', response_description='Set the discord server settings', response_model=UpdateSettingsModel)
async def set_settings(settings: SettingsModel = Body(...)):
    settings.id = PyObjectId()
    update = await db_add_one('settings', settings)
    return update
