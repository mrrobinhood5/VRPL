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
