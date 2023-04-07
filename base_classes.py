from datetime import datetime
from dataclasses import dataclass, field
from bson.objectid import ObjectId
from typing import List, Union, Any
from errors import TournamentError, TeamError, PlayerError, BaseError
from dateutil.relativedelta import relativedelta
from transactions.transaction_log import TransactionLogger, TransactionType
from enum import Enum


class Offence:
    pass


class LeagueWarning:
    pass


@dataclass
class Map:
    name: str


@dataclass
class Base:
    _instances = []
    logger: TransactionLogger
    name: str

    @classmethod
    def lookup(cls, obj: ObjectId) -> Any:
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

        self.logger.log(TransactionType.SEASON_CREATE, requestor=None, obj=self)

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
        """ This should return a list of games that belong to this season"""
        return []

    @property
    def tournaments(self) -> List:
        if isinstance(Tournament.instances(), List):
            return [x for x in Tournament.instances() if self.id == x.belongs_to_season]
        elif Tournament.instances().belongs_to_season == self:
            return [Tournament.instances()]
        else:
            return []

    @property
    def to_dict(self) -> dict:
        _r = {
            'id': str(self.id),
            'start_date': str(self.start_date),
            'end_date': str(self.end_date),
            'description': self.description,
            'name': self.name
        }
        return _r

    # def toJSON(self):
    #     return dumps(self, default=lambda o: o.to_dict(), sort_keys=True, indent=4)


@dataclass
class Game(Base):
    description: str
    id: ObjectId = field(default_factory=ObjectId)
    _instances = []

    def __post_init__(self):
        self.logger.log(TransactionType.GAME_CREATE, requestor=None, obj=self)

        self.__class__._instances.append(self)

    @property
    def tournaments(self) -> List:
        if isinstance(Tournament.instances(), List):
            return [x for x in Tournament.instances() if self.id == x.belongs_to_game]
        else:
            return []

    @property
    def to_dict(self):
        _r = {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'tournaments': [str(x.id) for x in self.tournaments]
        }
        return _r


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
    id: ObjectId = field(default_factory=ObjectId)
    _instances = []
    _teams = []
    # match_frequency = 7 days
    # maps_per_match = 2
    # map_frequency = 2
    # roster_lock_after = 14 weeks
    # participant_type = individual / team
    #

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

        self.logger.log(TransactionType.TOURNAMENT_CREATE, requestor=None, obj=self)

        self.__class__._instances.append(self)

    @property
    def teams(self) -> List:
        if isinstance(Team.instances(), List):
            return [x for x in Team.instances() if self in x.belongs_to_tournament]

    @property
    def players(self) -> List:
        if self.individual:
            if isinstance(Player.instances(), List):
                return [x for x in Player.instances() if self in x.belongs_to_tournament]
            else:
                return Player.instances() if Player.instances().belongs_to_tournament == self else []
        else:
            return []

    @property
    def to_dict(self):
        _r = {
            'id': str(self.id),
            'start_date': str(self.start_date),
            'end_date': str(self.end_date),
            'description': self.description,
            'name': self.name,
            'rules': self.rules,
            'max_match_players_per_team': self.max_match_players_per_team,
            'belongs_to_game': str(self.belongs_to_game),
            'belongs_to_season': str(self.belongs_to_season),
            'swaps_allowed': self.swaps_allowed,
            'individual': self.individual,
            'active': self.active,
            'teams': [str(x.id) for x in self.teams],
            'players': [str(x.id) for x in self.players]

        }
        return _r


@dataclass
class Division(Base):
    description: str
    belongs_to_tournament: Tournament
    id: ObjectId = field(default_factory=ObjectId)

    def __post_init__(self):
        self.logger.log(TransactionType.DIVISION_CREATE, requestor=None, obj=self)

        self.__class__._instances.append(self)

    @property
    def teams(self):
        return [x for x in Team.instances() if x.belongs_to_division == self]

    @property
    def to_dict(self):
        _r = {
            'name': self.name,
            'description': self.description,
            'belongs_to_tournament': str(self.belongs_to_tournament.id),
            'id': str(self.id),
            'teams': [str(x.id) for x in self.teams]
        }
        return _r


@dataclass
class Team(Base):
    description: str
    captain: ObjectId
    belongs_to_division: Division
    co_captain: Union[ObjectId, None] = None
    belongs_to_tournament: Union[Tournament, List[Tournament]] = field(default_factory=list)
    id: ObjectId = field(default_factory=ObjectId)
    active: bool = True
    _instances = []

    def __post_init__(self):
        # Check to see if the team name is not duplicate
        if isinstance(Team.instances(), List):
            if self.name in [x.name for x in Team.instances()]:
                raise TeamError('Team name is already in use')

        self.logger.log(TransactionType.TEAM_CREATE, requestor=Player.lookup(self.captain), obj=self)

        # Add captain to the team
        Player.lookup(self.captain).join_team(self)

        self.__class__._instances.append(self)

    def join_tournament(self, requestor: ObjectId, tournament: Tournament):
        # check to see who requested it, make sure its captain
        if requestor is not self.captain:
            raise TournamentError('You are not the captain')

        # check oto see if tournament is active
        if not tournament.active:
            raise TournamentError('That\'s not a valid tournament ID')

        # check the tournament passed if its individual. If so, team cannot be created.
        if tournament.individual:
            raise TournamentError('This is not a team tournament')

        # check to see if the team is already in
        if self in tournament.teams:
            raise TournamentError('You are already in this tournament')

        self.logger.log(TransactionType.TOURNAMENT_JOIN,
                        requestor=self,
                        obj=tournament)

        self.belongs_to_tournament.append(tournament)

        return True

    @property
    def team_full(self) -> bool:
        if isinstance(Player.instances(), List):
            _ = len([x for x in Player.instances() if self in x.belongs_to_team])
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

        # check to see if captain is not co-captain
        if co_captain is self.captain:
            raise TeamError("Captain cannot be Co-Captain")

        self.co_captain = co_captain

        self.logger.log(TransactionType.PLAYER_PROMOTE,
                        requestor=Player.lookup(requestor),
                        obj=self,
                        additional=Player.lookup(co_captain))
        return True

    def kick_player(self, requestor: ObjectId, kicked_player: ObjectId) -> bool:
        # implement kick player by a team_captain or co-captain
        pass

    @property
    def matches(self):
        # implement a count of how many matches the team has played
        return True

    @property
    def to_dict(self):
        _r = {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'captain': str(self.captain),
            'belongs_to_division': str(self.belongs_to_division.id),
            'co_captain': None or str(self.co_captain),
            'belongs_to_tournament': [str(x.id) for x in self.belongs_to_tournament],
            'active': self.active,
            'team_full': self.team_full,
            'player_count': self.player_count,
            'players': [str(x.id) for x in self.players]
        }
        return _r


@dataclass
class Player(Base):
    game_uid: Union[str, None] = None
    height: Union[str, None] = None
    belongs_to_team: List[Team] = field(default_factory=list)
    belongs_to_tournament: List[Tournament] = field(default_factory=list)
    id: ObjectId = field(default_factory=ObjectId)
    is_banned = False
    is_suspended = False
    offences: List[Offence] = field(default_factory=list)
    warnings: List[Warning] = field(default_factory=list)
    _instances = []

    # at some point it needs to hold the Discord Member ID

    @property
    def to_dict(self) -> dict:
        """
        Used to return a dict representation to clean up for the DB
        :return:
        """
        _r = {
            'id': str(self.id),
            'name': self.name,
            'game_uid': self.game_uid,
            'height': self.height,
            'belongs_to_team': [str(x.id) for x in self.belongs_to_team] if self.belongs_to_team else [],
            'belongs_to_tournament': [str(x.id) for x in
                                      self.belongs_to_tournament] if self.belongs_to_tournament else [],
            'is_banned': self.is_banned,
            'is_suspended': self.is_suspended,
            'offences': self.offences,
            'warnings': self.warnings
        }
        return _r

    @property
    def in_game_name(self):
        return self.name

    def __post_init__(self):
        # at some point check to see if the same uid or in_game_name is not in use
        if self.game_uid:
            if Player.instances() is List:
                if self.game_uid in [_.game_uid for _ in Player.instances()]:
                    raise PlayerError('UID is already in use.')

        # log the player registration
        self.logger.log(TransactionType.PLAYER_REGISTER, requestor=self, obj=self)

        # add it player to Player instances
        self.__class__._instances.append(self)

    def join_tournament(self, tournament: Tournament):
        if tournament.individual:
            if not self.belongs_to_tournament:
                self.belongs_to_tournament = [tournament]
            else:
                self.belongs_to_tournament.append(tournament)
        else:
            raise TournamentError('Cannot join tournament without a team')

        # log the tournament join
        self.logger.log(TransactionType.TOURNAMENT_JOIN, requestor=self, obj=tournament)

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
            # log the tournament join
            self.logger.log(TransactionType.TEAM_JOIN, requestor=self, obj=team)

            self.belongs_to_team.append(team)
            return True

# TODO I think Game should be the top level. Games have Tournaments. We dont need seasons? Just tournaments,
#  Then rounds or weeks, then matches
# TODO whats the difference between Open and Closed season
# TODO Tournaments create Weeks/Rounds