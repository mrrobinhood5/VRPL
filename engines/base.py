from models import VRPLObject
from typing import Type, TypeVar, Optional
from pydantic import ValidationError


base = VRPLObject
B = TypeVar('B', bound=VRPLObject)


class BaseEngine:

    async def count(self, base: Optional[Type[B]] = base) -> int:
        return await base.find({}, with_children=True).count()

    async def get_all(self, base: Type[B], f: Optional[dict] = None) -> list[B]:
        return await base.find(f if f else {}, with_children=True, fetch_links=True).to_list()

    async def get_all_basic(self, base: Optional[Type[B]] = base, f: Optional[dict] = None) -> list[Type[B]]:
        """ Same as get_all() but without fetching links """
        return await base.find(f if f else {}, with_children=True).to_list()

    async def update(self, base: Type[B], updates: dict) -> Type[B]:
        try:
            return await base.set(updates)
        except ValidationError as e:
            raise e