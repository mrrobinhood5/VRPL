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

