# from dataclasses import dataclass
from bson.objectid import ObjectId
from typing import List, Union, Any
from classes.errors import BaseError
from transactions.transaction_log import TransactionLogger
from pydantic import BaseModel, Field


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class Base(BaseModel):
    name: str

    _instances = []

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Item Name",
            }
        }

    def __post_init__(self):
        # at some point check to see if the same uid or in_game_name is not in use
        Base._instances.append(self)

    @classmethod
    def lookup(cls, obj: PyObjectId) -> Any:
        """
        Returns a matching object with that id
        :param obj: ObjectID to look for
        :return: The matching object
        """
        _ = [x for x in cls.instances() if x.id == obj]
        if not _:
            raise BaseError('None Found')
        else:
            return _[0]

    @classmethod
    def get(cls, search_term) -> List[Any]:
        """
        Returns a list of instances matching the search term
        :param search_term: String representation of the search term
        :return:
        """
        _search = [s for s in cls.instances() if search_term.lower() in s.name.lower()]

        return _search

    @classmethod
    def instances(cls) -> List[Union['Player', 'Tournament', 'Team']]:
        """
        Returns a list ...
        :return: A list of all instances in this class
        """
        return cls._instances

    @classmethod
    def count(cls) -> int:
        return len(cls._instances)

    @property
    def to_dict(self):
        return None

class Offence:
    pass


class LeagueWarning:
    pass


class Map(Base):
    name: str

    # def toJSON(self):
    #     return dumps(self, default=lambda o: o.to_dict(), sort_keys=True, indent=4)


# TODO I think Game should be the top level. Games have Tournaments. We dont need seasons? Just tournaments,
#  Then rounds or weeks, then matches
# TODO whats the difference between Open and Closed season
# TODO Tournaments create Weeks/Rounds