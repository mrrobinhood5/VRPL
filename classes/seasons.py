# OBSOLETE: LEFT OVER FROM LAST VERSION
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
