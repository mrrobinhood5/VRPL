# OBSOLETE, LEFT OVER FROM LAST VERSION
from dataclasses import dataclass, field
from typing import Any, Optional
from bson.objectid import ObjectId
from enum import Enum
# from discord import Member
from datetime import datetime
from queue import Queue


class TransactionType(Enum):
    # Player Transactions
    PLAYER_REGISTER = "REGISTERED PLAYER"
    PLAYER_CHANGE = "PLAYER UPDATE"
    TEAM_JOIN = "JOINED TEAM"
    PLAYER_PROMOTE = "PLAYER PROMOTION"

    # Team Transactions
    TEAM_CREATE = "TEAM CREATED"
    TOURNAMENT_JOIN = "JOINED TOURNAMENT"
    CAPTAIN_CHANGE = "CHANGED CAPTAIN"
    CO_CAPTAIN_CHANGE = "CHANGED CO-CAPTAIN"

    # Season Transactions
    SEASON_CREATE = "SEASON CREATED"

    # Game Transactions
    GAME_CREATE = "GAME CREATED"

    # Tournament Transactions
    TOURNAMENT_CREATE = "TOURNAMENT CREATED"

    # Division Transactions
    DIVISION_CREATE = "DIVISION CREATED"


@dataclass
class TransactionLogger:
    queue: Queue = field(default_factory=Queue)

    def log(self, t_type: TransactionType, requestor: Any, obj: Any, additional: Optional[Any] = None):
        _id = ObjectId()
        transaction = {
            '_id': _id,
            'type': t_type.value,
            'requestor_id': requestor.id if requestor else None,
            'requestor_name': requestor.name if requestor else None,
            'timestamp': datetime.now()
        }
        if t_type is TransactionType.PLAYER_REGISTER:
            self.player_register(transaction, obj)
        elif t_type is TransactionType.TOURNAMENT_JOIN:
            self.tournament_join(transaction, obj)
        elif t_type is TransactionType.SEASON_CREATE:
            self.season_create(transaction, obj)
        elif t_type is TransactionType.GAME_CREATE:
            self.game_create(transaction, obj)
        elif t_type is TransactionType.TOURNAMENT_CREATE:
            self.tournament_create(transaction, obj)
        elif t_type is TransactionType.DIVISION_CREATE:
            self.division_create(transaction, obj)
        elif t_type is TransactionType.TEAM_CREATE:
            self.team_create(transaction, obj)
        elif t_type is TransactionType.TEAM_JOIN:
            self.team_join(transaction, obj)
        elif t_type is TransactionType.PLAYER_PROMOTE:
            self.player_promote(transaction, obj, additional)

    def season_create(self, transaction: dict, obj: Any):
        transaction.update({'season': obj.to_dict})
        self.queue.put(transaction)
        print(f'[{transaction["type"]}] [{datetime.now()}] '
              f'A new season was created with the name of {obj.name}')

    def game_create(self, transaction: dict, obj: Any):
        transaction.update({'game': obj.to_dict})
        self.queue.put(transaction)
        print(f'[{transaction["type"]}] [{datetime.now()}] '
              f'A new game was created with the name of {obj.name}')

    def tournament_create(self, transaction: dict, obj: Any):
        transaction.update({'tournament': obj.to_dict})
        self.queue.put(transaction)
        print(f'[{transaction["type"]}] [{datetime.now()}] '
              f'A new tournament was created with the name of {obj.name}')

    def division_create(self, transaction: dict, obj: Any):
        transaction.update({'division': obj.to_dict})
        self.queue.put(transaction)
        print(f'[{transaction["type"]}] [{datetime.now()}] '
              f'A new division was created with the name of {obj.name}')

    def player_register(self, transaction: dict, obj: Any):
        transaction.update({'player': obj.to_dict})
        self.queue.put(transaction)
        print(f'[{transaction["type"]}] [{datetime.now()}] '
              f'Discord Member Name registered a new player with the name of {obj.name}')

    def player_promote(self, transaction: dict, obj: Any, target: Any):
        transaction.update({'team': obj.to_dict})
        transaction.update({'promoted': target.to_dict})
        self.queue.put(transaction)
        print(f'[{transaction["type"]}] [{datetime.now()}] '
              f'{transaction["requestor_name"]} has promoted {target.name} in team {obj.name}')

    def team_create(self, transaction: dict, obj: Any):
        transaction.update({'team': obj.to_dict})
        self.queue.put(transaction)
        print(f'[{transaction["type"]}] [{datetime.now()}] '
              f'{transaction["requestor_name"]} created a new team with the name of {obj.name}')

    def team_join(self, transaction: dict, obj: Any):
        transaction.update({'team': obj.to_dict})
        self.queue.put(transaction)
        print(f'[{transaction["type"]}] [{datetime.now()}] '
              f'{transaction["requestor_name"]} joined team: {obj.name}')

    def tournament_join(self, transaction: dict, obj: Any):
        transaction.update({'tournament': obj.name})
        self.queue.put(transaction)
        print(f'[{transaction["type"]}] [{datetime.now()}] '
              f'{transaction["requestor_name"]} joined the {obj.name} Tournament')
    #
    # def player_update(self, transaction: dict, obj: Any):
    #     # cls.queue.append(transaction)
    #     pass
