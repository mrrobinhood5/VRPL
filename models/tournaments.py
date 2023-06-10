# # OBSOLETE LEFT OBER FROM LAST VERSION
# aclasses import dataclass, field
# from models.base_classes import Base, Player, Team, Tournament
# from datetime import datetime
# from typing import Union
# from errors import MatchError
#
# from bson import ObjectId
# from enum import Enum, auto
#
# # TODO i think passing all references by instance instead of ObjectID
# @dataclass
# class Tournament(Base):
#     description: str
#     rules: str
#     max_match_players_per_team: int
#     belongs_to_game: ObjectId
#     belongs_to_season: ObjectId
#     swaps_allowed: bool = True
#     individual: bool = False
#     active: bool = True
#     start_date: Union[datetime, str] = datetime.today()
#     end_date: Union[datetime, str] = datetime.today() + relativedelta(months=3)
#     # participants: List[Member] = field(default_factory=list) this is probably a property
#     id: ObjectId = field(default_factory=ObjectId)
#     _instances = []
#     _teams = []
#     # match_frequency = 7 days
#     # maps_per_match = 2
#     # map_frequency = 2
#     # roster_lock_after = 14 weeks
#     # participant_type = individual / team
#     #
#
#     def __post_init__(self):
#         # we need to parse the start/end date if it's a str
#         if isinstance(self.start_date, str):
#             self.start_date = datetime.strptime(self.start_date, "%m/%d/%Y")
#         elif not isinstance(self.start_date, datetime):
#             raise ValueError('That\'s is not a valid date format')
#
#         if isinstance(self.end_date, str):
#             self.end_date = datetime.strptime(self.end_date, "%m/%d/%Y")
#         elif not isinstance(self.end_date, datetime):
#             raise ValueError('That\'s is not a valid date format')
#
#         # Tournament Creation must be within Season window
#         _s = Season.lookup(self.belongs_to_season)
#         if _s.start_date > self.start_date or _s.end_date < self.end_date:
#             raise TournamentError(f'Season is from {_s.start_date}-{_s.end_date} but Tourney '
#                                   f'is from {self.start_date}-{self.end_date}')
#
#         # Tournament name cannot be the same as any other
#         if isinstance(Tournament.instances(), List):
#             if self.name in [x.name for x in Tournament.instances()]:
#                 raise TournamentError('Tournament name is already in use')
#
#         self.logger.log(TransactionType.TOURNAMENT_CREATE, requestor=None, obj=self)
#
#         self.__class__._instances.append(self)
#
#     @property
#     def teams(self) -> List:
#         if isinstance(Team.instances(), List):
#             return [x for x in Team.instances() if self in x.belongs_to_tournament]
#
#     @property
#     def players(self) -> List:
#         if self.individual:
#             if isinstance(Player.instances(), List):
#                 return [x for x in Player.instances() if self in x.belongs_to_tournament]
#             else:
#                 return Player.instances() if Player.instances().belongs_to_tournament == self else []
#         else:
#             return []
#
#     @property
#     def to_dict(self):
#         _r = {
#             'id': str(self.id),
#             'start_date': str(self.start_date),
#             'end_date': str(self.end_date),
#             'description': self.description,
#             'name': self.name,
#             'rules': self.rules,
#             'max_match_players_per_team': self.max_match_players_per_team,
#             'belongs_to_game': str(self.belongs_to_game),
#             'belongs_to_season': str(self.belongs_to_season),
#             'swaps_allowed': self.swaps_allowed,
#             'individual': self.individual,
#             'active': self.active,
#             'teams': [str(x.id) for x in self.teams],
#             'players': [str(x.id) for x in self.players]
#
#         }
#         return _r
#
#
# @dataclass
# class Division(Base):
#     description: str
#     belongs_to_tournament: Tournament
#     id: ObjectId = field(default_factory=ObjectId)
#
#     def __post_init__(self):
#         self.logger.log(TransactionType.DIVISION_CREATE, requestor=None, obj=self)
#
#         self.__class__._instances.append(self)
#
#     @property
#     def teams(self):
#         return [x for x in Team.instances() if x.belongs_to_division == self]
#
#     @property
#     def to_dict(self):
#         _r = {
#             'name': self.name,
#             'description': self.description,
#             'belongs_to_tournament': str(self.belongs_to_tournament.id),
#             'id': str(self.id),
#             'teams': [str(x.id) for x in self.teams]
#         }
#         return _r
#
# class MatchScore(Enum):
#     FORFEIT = 0
#     DISQUALIFY = 0
#
#
# class MatchTransaction(Enum):
#     PROPOSE_DATE = auto()
#     APPROVE_DATE = auto()
#     SUBMIT_SCORE = auto()
#     APPROVE_SCORE = auto()
#
#
# @dataclass
# class Match(Base):
#     """ The order of events is:
#     Match created between two players/teams
#     Either player/captain/co-captain can propose a date
#     The other player/captain/co-captain must accept
#     The home player/team must submit scores
#     The away player/team must accept scores
#     """
#     home: ObjectId
#     away: ObjectId
#     belongs_to_tournament: ObjectId
#     belongs_to_week: ObjectId
#     match_date: Union[datetime, None] = None
#
#     home_score: Union[int, MatchScore, None] = None
#     away_score: Union[int, MatchScore, None] = None
#
#     _proposed_date: datetime = None
#     _proposed_date_submitter: Union[ObjectId, None] = None
#     _approved_date_by: Union[ObjectId, None] = None
#     _score_submitted_by: Union[ObjectId, None] = None
#     _score_approved_by: Union[ObjectId, None] = None
#     id: ObjectId = field(default_factory=ObjectId)
#
#     def __post_init__(self):
#         if self.individual:
#             try:
#                 _h = Player.lookup(self.home)
#                 _a = Player.lookup(self.away)
#             except MatchError as e:
#                 raise MatchError(e)
#         else:
#             try:
#                 _h = Team.lookup(self.home)
#                 _a = Team.lookup(self.away)
#             except MatchError as e:
#                 raise MatchError(e)
#         _t = Tournament.lookup(self.belongs_to_tournament)
#
#         self.name = f'{_h.name} vs {_a.name} - {_t.name} - Week #'
#
#     def propose_date(self, requester: ObjectId, proposed_date: datetime):
#         """ First step, propose a date by any party as long as its inside the alloted week/tournament"""
#         if self.scheduled:
#             raise MatchError('Match has been scheduled already, Approver must Dissapprove')
#
#         if not self.dates_in_week_scope(proposed_date):
#             raise MatchError('Dates not within scope')
#
#         if not self.authorized_submitter(requester, MatchTransaction.PROPOSE_DATE):
#             raise MatchError('Only a Player/Team in the Match can propose a date')
#         else:
#             self._proposed_date = proposed_date
#             self._proposed_date_submitter = requester
#         return True
#
#     def approve_date(self, requester: ObjectId, approve: bool):
#         if self.scheduled:
#             raise MatchError('Already scheduled, cannot approve again. ')
#
#         if not self._proposed_date_submitter:
#             raise MatchError('Cannot approve a date before submitting a date')
#
#         if requester == self._proposed_date_submitter:
#             raise MatchError('Requester cannot be Approver')
#
#         if not self.authorized_submitter(requester, MatchTransaction.APPROVE_DATE):
#             raise MatchError('Only a Player/Team in the Match can propose a date')
#
#         if approve:
#             self.match_date = self._proposed_date
#             self._approved_date_by = requester
#             return True
#
#     def disapprove_date(self, submitter: ObjectId):
#         """ Used to unlock the Match (from scheduled) back to date picking """
#         if submitter == self._approved_date_by:
#             self.match_date = None
#             self._approved_date_by = None
#         else:
#             raise MatchError('You are not approver, you cannot Disapprove')
#
#     def submit_score(self, submitter: ObjectId, home_score: Union[int, MatchScore],
#     away_score: Union[int, MatchScore]):
#         """ Home team captain/co-captain are the only ones to scores, Away team captain/co-captain validates scores"""
#         # Scores cannot be submitted before the match is scheduled
#         if not self.scheduled:
#             raise MatchError('Cannot submit scores before scheduling a match')
#
#         # check if individual or team
#         if not self.authorized_submitter(submitter, MatchTransaction.SUBMIT_SCORE):
#             raise MatchError('Only the home team captain/co-captain can submit scores')
#
#         self.home_score, self.away_score = home_score, away_score
#         self._score_submitted_by = submitter
#         return True
#
#     def approve_score(self, submitter: ObjectId, approve: bool):
#         """ Away Team can approve or deny the submitted scores """
#         # check to see if match has been scheduled
#         if not self.scheduled:
#             raise MatchError('Cannot submit scores before scheduling a match')
#
#         # check to see if score has been submitted first
#         if not self._score_submitted_by:
#             raise MatchError('Scores have not been Submitted yet')
#
#         if not self.authorized_submitter(submitter, MatchTransaction.APPROVE_SCORE):
#             raise MatchError('Only Away Team/Player can approve scores')
#
#         if approve:
#             self._score_approved_by = submitter
#             return True
#         else:
#             return False
#
#     @property
#     def winner(self) -> Union[ObjectId, None]:
#         if not self.home_score or not self.away_score:
#             return None
#         if self.home_score > self.away_score:
#             return self.home
#         elif self.away_score > self.home_score:
#             return self.away
#
#     @property
#     def tie(self) -> bool:
#         if not self.home_score or not self.away_score:
#             return False
#         if self.away_score == self.home_score:
#             return True
#         else:
#             return False
#
#     @property
#     def individual(self) -> bool:
#         return Tournament.lookup(self.belongs_to_tournament).individual
#
#     @property
#     def completed(self) -> bool:
#         if self._score_approved_by:
#             return True
#         else:
#             return False
#
#     @property
#     def scheduled(self) -> bool:
#         return True if self.match_date else False
#
#     def dates_in_week_scope(self, proposed_date: datetime) -> bool:
#         _t = Tournament.lookup(self.belongs_to_tournament)
#         return True if _t.start_date < proposed_date < _t.end_date else False
#
#     def authorized_submitter(self, requester: ObjectId, transaction: MatchTransaction) -> bool:
#         match transaction:
#             case MatchTransaction.PROPOSE_DATE | MatchTransaction.APPROVE_DATE:
#                 if self.individual:
#                     return True if requester in self.match_participants() else False
#                 else:
#                     return True if requester in self.match_participants() else False
#             case MatchTransaction.SUBMIT_SCORE:
#                 if self.individual:
#                     return True if requester == self.home else False
#                 else:
#                     return True if requester in self.match_participants('home') else False
#             case MatchTransaction.APPROVE_SCORE:
#                 if self.individual:
#                     return True if requester == self.away else False
#                 else:
#                     return True if requester in self.match_participants('away') else False
#
#     def match_participants(self, f=None):
#         if self.individual:
#             return self.home, self.away
#         _h = Team.lookup(self.home)
#         _a = Team.lookup(self.away)
#         match f:
#             case None:
#                 return _h.captain, _h.co_captain, _a.captain, _a.co_captain
#             case 'away':
#                 return _a.captain, _a.co_captain
#             case 'home':
#                 return _h.captain, _h.co_captain
