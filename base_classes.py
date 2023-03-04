from datetime import datetime
from dataclasses import dataclass, field
from bson.objectid import ObjectId
from typing import List, Union, Any
from errors import TournamentError, TeamError
from dateutil.relativedelta import relativedelta
from json import dumps


@dataclass
class Base:
    name: str
    _instances = []

    @classmethod
    def lookup(cls, obj:ObjectId) -> Any:
        """
        Returns a matching object with that id
        :param obj: ObjectID to look for
        :return: The matching object
        """
        _ = [x for x in cls.instances() if x.id is obj]
        if not _:
            return None
        else:
            return _[0]

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
    id: ObjectId = field(default_factory=ObjectId)
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
            return [x for x in Tournament.instances() if self.id is x.belongs_to_season]
        elif Tournament.instances().belongs_to_season== self:
            return [Tournament.instances()]
        else:
            return []

    def to_dict(self) -> dict:
        _r = {
            'id': str(self.id),
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

    @property
    def tournaments(self) -> List:
        if isinstance(Tournament.instances(), List):
            return [x for x in Tournament.instances() if self.id is x.belongs_to_game]
        elif Tournament.instances().belongs_to_game == self:
            return [Tournament.instances()]
        else:
            return []

@dataclass
class Tournament(Base):
    description: str
    rules: str
    max_match_players_per_team: int
    belongs_to_game: ObjectId
    belongs_to_season: ObjectId
    swaps_allowed: bool = True
    individual: bool = False
    active: bool = True
    start_date: Union[datetime, str] = datetime.today()
    end_date: Union[datetime, str] = datetime.today() + relativedelta(months=3)
    # participants: List[Member] = field(default_factory=list) this is probably a property
    id: ObjectId = ObjectId()
    _instances = []
    _teams = []

    def __post_init__(self):
        # we need to parse the start/end date if it's a str
        if isinstance(self.start_date, str):
            self.start_date = datetime.strptime(self.start_date, "%m/%d/%Y")
        elif not isinstance(self.start_date, datetime):
            raise ValueError('That\'s is not a valid date format')

        if isinstance(self.end_date, str):
            self.end_date = datetime.strptime(self.end_date, "%m/%d/%Y")
        elif not isinstance(self.end_date, datetime):
            raise ValueError('That\'s is not a valid date format')

        # Tournament Creation must be within Season window
        _s = Season.lookup(self.belongs_to_season)
        if _s.start_date > self.start_date or _s.end_date < self.end_date:
            raise TournamentError(f'Season is from {_s.start_date}-{_s.end_date} but Tourney '
                                  f'is from {self.start_date}-{self.end_date}')

        # Tournament name cannot be the same as any other
        if isinstance(Tournament.instances(), List):
            if self.name in [x.name for x in Tournament.instances()]:
                raise TournamentError('Tournament name is already in use')

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
    captain: ObjectId
    co_captain: Union[ObjectId, None] = None
    belongs_to_tournament: Union[Tournament, List[Tournament]] = field(default_factory=list)
    id: ObjectId = ObjectId()
    active: bool = True
    _instances = []

    def __post_init__(self):
        # Check to see if the team name is not duplicate
        if isinstance(Team.instances(), List):
            if self.name in [x.name for x in Team.instances()]:
                raise TeamError('Team name is already in use')

        # Add captain to the team
        Player.lookup(self.captain).join_team(self)

        self.__class__._instances.append(self)

    def join_tournament(self, requestor: ObjectId, tournament: Tournament):
        # check to see who requested it, make sure its captain
        if requestor is not self.captain:
            raise TournamentError('You are not the captain')

        # check oto see if tournament is active
        if not tournament.active:
            raise TournamentError('Thats not a valid tournament ID')

        # check the tournament passed if its individual. If so, team cannot be created.
        if tournament.individual:
            raise TournamentError('This is not a team tournament')

        # check to see if the team is already in
        if self in tournament.teams:
            raise TournamentError('You are already in this tournament')

        self.belongs_to_tournament.append(tournament)

        return True

    @property
    def team_full(self) -> bool:
        if isinstance(Player.instances(), List):
            _ = len([x for x in Player.instances() if self in x.belongs_to_team ])
            return True if _ >= 10 else False
        else:
            return False

    @property
    def player_count(self) -> int:
        return len([x for x in Player.instances() if self in x.belongs_to_team])

    @property
    def players(self) -> List:
        if isinstance(Player.instances(), List):
            return [x for x in Player.instances() if self in x.belongs_to_team]
        elif Player.instances().belongs_to_team == self:
            return [Player.instances()]
        else:
            return []

    def make_co_captain(self, requestor: ObjectId, co_captain: ObjectId) -> bool:
        # check to see if requestor is the captain
        if requestor is not self.captain:
            raise TeamError("You are not captain, not allowed to make changes")

        # check to see if co_captain is in the team
        if co_captain not in [x.id for x in self.players]:
            raise TeamError("That Player is not on this team")

        self.co_captain = co_captain
        return True


@dataclass
class Player(Base):
    game_uid: Union[str, None] = None
    height: Union[str, None] = None
    belongs_to_team: List[Team] = field(default_factory=list)
    belongs_to_tournament: List[Tournament] = field(default_factory=list)
    id: ObjectId = field(default_factory=ObjectId)
    _instances = []


    # at some point check to see if the same uid or in_game_name is not in use
    @property
    def in_game_name(self):
        return self.name

    def __post_init__(self):
        self.__class__._instances.append(self)

    def join_tournament(self, tournament: Tournament):
        if tournament.individual:
            if not self.belongs_to_tournament:
                self.belongs_to_tournament = [tournament]
            else:
                self.belongs_to_tournament.append(tournament)
        else:
            raise TournamentError('Cannot join tournament without a team')

    def join_team(self, team: Team) -> bool:
        """
        Adds the team object to its teams. It should check to see if the team is full first
        :param team:
        :return:
        """
        if team.team_full:
            raise TeamError('Cannot join team, max players allowed has been reached')
        elif team in self.belongs_to_team:
            raise TeamError('You are already part of this team. Doh!')
        else:
            self.belongs_to_team.append(team)
            return True
