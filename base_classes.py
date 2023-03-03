from datetime import datetime
from dataclasses import dataclass, field
from bson.objectid import ObjectId
from typing import List, Union
from discord import Member
from errors import TournamentError, TeamError
from dateutil.relativedelta import relativedelta
from json import dumps




@dataclass
class Base:
    name: str
    _instances = []

    @classmethod
    def get(cls, search_term):
        """
        Returns a list of instances matching the searchterm
        :param search_term: String representation of the search term
        :return:
        """
        _search = [s for s in cls.instances() if search_term.lower() in s.name.lower()]
        if len(_search) == 1:
            return _search[0]
        else:
            return _search

    @classmethod
    def instances(cls):
        """
        Returns a list ...
        :return: A list of all instances in this class
        """
        if len(cls._instances) == 1:
            return cls._instances[0]
        else:
            return cls._instances

    @classmethod
    def count(cls) -> int:
        return len(cls._instances)


@dataclass
class Season(Base):
    start_date: Union[datetime, str] = datetime.today()
    end_date: Union[datetime, str] = datetime.today() + relativedelta(months=6)
    description: str = ''
    _id: ObjectId = field(default_factory=ObjectId)
    _instances = []

    def __post_init__(self):
        """
        Post Init will validate date format. It must be a string or an actual datetime object
        Also adds every instance created to the Class instance.
        """
        if isinstance(self.start_date, str):
            self.start_date = datetime.strptime(self.start_date, "%m/%d/%Y")
        elif not isinstance(self.start_date, datetime):
            raise ValueError('That\'s is not a valid date format')

        if isinstance(self.end_date, str):
            self.end_date = datetime.strptime(self.end_date, "%m/%d/%Y")
        elif not isinstance(self.end_date, datetime):
            raise ValueError('That\'s is not a valid date format')

        self.__class__._instances.append(self)

    @property
    def id(self) -> dict:
        """
        will return _id for use in dictionary, im not sure if this is the best option though
        :return:
        """
        return {'_id': str(self._id)}

    @property
    def active(self) -> bool:
        """
        :return: True if today is before end_date
        """
        if datetime.today() >= self.end_date:
            return False
        else:
            return True

    @property
    def games(self) -> List:
        """ This should return a list of games that have belong to this season"""
        return []

    @property
    def tournaments(self) -> List:
        if isinstance(Tournament.instances(), List):
            return [x for x in Tournament.instances() if x.belongs_to_season == self]
        elif Tournament.instances().belongs_to_team == self:
            return [Tournament.instances()]
        else:
            return []

    def to_dict(self) -> dict:
        _r = {
            'id': str(self._id),
            'start_date': str(self.start_date),
            'end_date': str(self.end_date),
            'description': self.description,
            'name': self.name
        }
        return _r

    def toJSON(self):
        return dumps(self, default=lambda o: o.to_dict(), sort_keys=True, indent=4)

@dataclass
class Game(Base):
    description: str
    id: ObjectId = ObjectId()
    _instances = []

    def __post_init__(self):
        self.__class__._instances.append(self)


@dataclass
class Tournament(Base):
    description: str
    rules: str
    max_match_players_per_team: int
    belongs_to_game: Game
    belongs_to_season: Season
    swaps_allowed: bool = True
    individual: bool = False
    active: bool = True
    # participants: List[Member] = field(default_factory=list) this is probably a property
    id: ObjectId = ObjectId()
    _instances = []
    _teams = []

    def __post_init__(self):
        self.__class__._instances.append(self)

    @property
    def teams(self) -> List:
        if isinstance(Team.instances(), List):
            return [x for x in Team.instances() if self in x.belongs_to_tournament]

    @property
    def players(self) -> List:
        if self.individual:
            if isinstance(Player.instances(), List):
                return [x for x in Player.instances() if self in x.belongs_to_tournament ]
            else:
                return Player.instances() if Player.instances().belongs_to_tournament == self else []
        else:
            return []

@dataclass
class Team(Base):
    description: str
    captain: Union[Member, str]
    co_captain: Union[Member, str]
    belongs_to_tournament: Union[Tournament, List[Tournament]] = field(default_factory=list)
    id: ObjectId = ObjectId()
    active: bool = True
    _instances = []
    _players = []

    def __post_init__(self):
        # check the tournament passed if its individual. If so, team cannot be created.
        if self.belongs_to_tournament.individual:
            raise TournamentError('Team cannot join a individual tournament')

        if not isinstance(self.belongs_to_tournament, List):
            self.belongs_to_tournament = [self.belongs_to_tournament]

        self.__class__._instances.append(self)
        # you also have to check if a team with the same name exists

    @property
    def team_full(self) -> bool:
        if isinstance(Player.instances(), List):
            _ = len([x for x in Player.instances() if x.belongs_to_team == self])
            return True if _ >= 10 else False
        else:
            return False

    @property
    def player_count(self) -> int:
        return len([x for x in Player.instances() if x.belongs_to_team == self])

    @property
    def players(self) -> List:
        if isinstance(Player.instances(), List):
            return [x for x in Player.instances() if x.belongs_to_team == self]
        elif Player.instances().belongs_to_team == self:
            return [Player.instances()]
        else:
            return []


@dataclass
class Player(Base):
    game_uid: str
    belongs_to_team: Union[Team, None] = None
    belongs_to_tournament: List[Tournament] = field(default_factory=list)
    id: ObjectId = ObjectId()
    _instances = []


    # at some point check to see if the same uid or in_game_name is not in use
    @property
    def in_game_name(self):
        return self.name

    def __post_init__(self):
        # check to see if a team is full
        if self.belongs_to_team:
            if self.belongs_to_team.team_full:
                raise TeamError('Team is full')

        self.__class__._instances.append(self)

    def join_tournament(self, tournament: Tournament):
        if tournament.individual:
            if not self.belongs_to_tournament:
                self.belongs_to_tournament = [tournament]
            else:
                self.belongs_to_tournament.append(tournament)
        else:
            raise TournamentError('Cannot join tournament without a team')
