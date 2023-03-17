from dataclasses import dataclass, field
from typing import Any, Union, List
from bson.objectid import ObjectId
from enum import Enum, auto
from discord import Member
from datetime import datetime
from queue import Queue

import database
from db_interface import DbInterface
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase


class TransactionType(Enum):
    # Player Transactions
    PLAYER_REGISTER = "REGISTERED PLAYER"
    PLAYER_CHANGE = "PLAYER UPDATE"
    TEAM_CREATE = "CREATED TEAM"
    TEAM_JOIN = "JOINED TEAM"

    # Team Transactions
    TOURNAMENT_JOIN = "JOINED TOURNAMENT"
    CAPTAIN_CHANGE = "CHANGED CAPTAIN"
    CO_CAPTAIN_CHANGE = "CHANGED CO-CAPTAIN"


@dataclass
class TransactionLogger:
    queue: Queue = field(default_factory=Queue)

    def log(self, t_type: TransactionType, requestor: Any, obj: Any):
        _id = ObjectId()
        transaction = {
            '_id': _id,
            'type': t_type.value,
            'requestor_id': requestor.id,
            'requestor_name': requestor.name,
            'timestamp': datetime.now()
        }
        if t_type is TransactionType.PLAYER_REGISTER:
            self.player_register(transaction, obj)
        elif t_type is TransactionType.TOURNAMENT_JOIN:
            self.tournament_join(transaction, obj)

    def player_register(self, transaction: dict, obj: Any):
        transaction.update({'data': obj.to_dict})
        self.queue.put(transaction)
        print(f'[{transaction["type"]}] [{datetime.now()}] '
              f'Discord Member Name registered a new player with the name of {obj.name}')

    def tournament_join(self, transaction: dict, obj: Any):
        transaction.update({'tournament': obj.name})
        self.queue.put(transaction)
        print(f'[{transaction["type"]}] [{datetime.now()}] '
              f'Discord Member Name joined the {obj.name} Tournament')
    #
    # def player_update(self, transaction: dict, obj: Any):
    #     # cls.queue.append(transaction)
    #     pass

