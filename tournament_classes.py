from dataclasses import dataclass, field
from base_classes import Base, Player, Team, Tournament
from datetime import datetime
from typing import Union
from errors import MatchError

from bson import ObjectId
from enum import Enum, auto

# TODO i think passing all references by instance instead of ObjectID

class MatchScore(Enum):
    FORFEIT = 0
    DISQUALIFY = 0


class MatchTransaction(Enum):
    PROPOSE_DATE = auto()
    APPROVE_DATE = auto()
    SUBMIT_SCORE = auto()
    APPROVE_SCORE = auto()


@dataclass
class Match(Base):
    """ The order of events is:
    Match created between two players/teams
    Either player/captain/co-captain can propose a date
    The other player/captain/co-captain must accept
    The home player/team must submit scores
    The away player/team must accept scores
    """
    home: ObjectId
    away: ObjectId
    belongs_to_tournament: ObjectId
    belongs_to_week: ObjectId
    match_date: Union[datetime, None] = None

    home_score: Union[int, MatchScore, None] = None
    away_score: Union[int, MatchScore, None] = None

    _proposed_date: datetime = None
    _proposed_date_submitter: Union[ObjectId, None] = None
    _approved_date_by: Union[ObjectId, None] = None
    _score_submitted_by: Union[ObjectId, None] = None
    _score_approved_by: Union[ObjectId, None] = None
    id: ObjectId = field(default_factory=ObjectId)

    def __post_init__(self):
        if self.individual:
            try:
                _h = Player.lookup(self.home)
                _a = Player.lookup(self.away)
            except MatchError as e:
                raise MatchError(e)
        else:
            try:
                _h = Team.lookup(self.home)
                _a = Team.lookup(self.away)
            except MatchError as e:
                raise MatchError(e)
        _t = Tournament.lookup(self.belongs_to_tournament)

        self.name = f'{_h.name} vs {_a.name} - {_t.name} - Week #'

    def propose_date(self, requester: ObjectId, proposed_date: datetime):
        """ First step, propose a date by any party as long as its inside the alloted week/tournament"""
        if self.scheduled:
            raise MatchError('Match has been scheduled already, Approver must Dissapprove')

        if not self.dates_in_week_scope(proposed_date):
            raise MatchError('Dates not within scope')

        if not self.authorized_submitter(requester, MatchTransaction.PROPOSE_DATE):
            raise MatchError('Only a Player/Team in the Match can propose a date')
        else:
            self._proposed_date = proposed_date
            self._proposed_date_submitter = requester
        return True

    def approve_date(self, requester: ObjectId, approve: bool):
        if self.scheduled:
            raise MatchError('Already scheduled, cannot approve again. ')

        if not self._proposed_date_submitter:
            raise MatchError('Cannot approve a date before submitting a date')

        if requester == self._proposed_date_submitter:
            raise MatchError('Requester cannot be Approver')

        if not self.authorized_submitter(requester, MatchTransaction.APPROVE_DATE):
            raise MatchError('Only a Player/Team in the Match can propose a date')

        if approve:
            self.match_date = self._proposed_date
            self._approved_date_by = requester
            return True

    def disapprove_date(self, submitter: ObjectId):
        """ Used to unlock the Match (from scheduled) back to date picking """
        if submitter == self._approved_date_by:
            self.match_date = None
            self._approved_date_by = None
        else:
            raise MatchError('You are not approver, you cannot Disapprove')

    def submit_score(self, submitter: ObjectId, home_score: Union[int, MatchScore], away_score: Union[int, MatchScore]):
        """ Home team captain/co-captain are the only ones to scores, Away team captain/co-captain validates scores"""
        # Scores cannot be submitted before the match is scheduled
        if not self.scheduled:
            raise MatchError('Cannot submit scores before scheduling a match')

        # check if individual or team
        if not self.authorized_submitter(submitter, MatchTransaction.SUBMIT_SCORE):
            raise MatchError('Only the home team captain/co-captain can submit scores')

        self.home_score, self.away_score = home_score, away_score
        self._score_submitted_by = submitter
        return True

    def approve_score(self, submitter: ObjectId, approve: bool):
        """ Away Team can approve or deny the submitted scores """
        # check to see if match has been scheduled
        if not self.scheduled:
            raise MatchError('Cannot submit scores before scheduling a match')

        # check to see if score has been submitted first
        if not self._score_submitted_by:
            raise MatchError('Scores have not been Submitted yet')

        if not self.authorized_submitter(submitter, MatchTransaction.APPROVE_SCORE):
            raise MatchError('Only Away Team/Player can approve scores')

        if approve:
            self._score_approved_by = submitter
            return True
        else:
            return False

    @property
    def winner(self) -> Union[ObjectId, None]:
        if not self.home_score or not self.away_score:
            return None
        if self.home_score > self.away_score:
            return self.home
        elif self.away_score > self.home_score:
            return self.away

    @property
    def tie(self) -> bool:
        if not self.home_score or not self.away_score:
            return False
        if self.away_score == self.home_score:
            return True
        else:
            return False

    @property
    def individual(self) -> bool:
        return Tournament.lookup(self.belongs_to_tournament).individual

    @property
    def completed(self) -> bool:
        if self._score_approved_by:
            return True
        else:
            return False

    @property
    def scheduled(self) -> bool:
        return True if self.match_date else False

    def dates_in_week_scope(self, proposed_date: datetime) -> bool:
        _t = Tournament.lookup(self.belongs_to_tournament)
        return True if _t.start_date < proposed_date < _t.end_date else False

    def authorized_submitter(self, requester: ObjectId, transaction: MatchTransaction) -> bool:
        match transaction:
            case MatchTransaction.PROPOSE_DATE | MatchTransaction.APPROVE_DATE:
                if self.individual:
                    return True if requester in self.match_participants() else False
                else:
                    return True if requester in self.match_participants() else False
            case MatchTransaction.SUBMIT_SCORE:
                if self.individual:
                    return True if requester == self.home else False
                else:
                    return True if requester in self.match_participants('home') else False
            case MatchTransaction.APPROVE_SCORE:
                if self.individual:
                    return True if requester == self.away else False
                else:
                    return True if requester in self.match_participants('away') else False

    def match_participants(self, f=None):
        if self.individual:
            return self.home, self.away
        _h = Team.lookup(self.home)
        _a = Team.lookup(self.away)
        match f:
            case None:
                return _h.captain, _h.co_captain, _a.captain, _a.co_captain
            case 'away':
                return _a.captain, _a.co_captain
            case 'home':
                return _h.captain, _h.co_captain
