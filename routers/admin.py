from fastapi import APIRouter
from database import db

router = APIRouter(tags=['admin'], prefix='/admin')


@router.get('/db_drop', response_description='Reset the WHOLE database')
async def drop_db():
    for coll in await db.list_collection_names():
        await db.drop_collection(coll)
