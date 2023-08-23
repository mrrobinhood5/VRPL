from models.base import ReprimandBase, TeamBase


class Warned(ReprimandBase):
    pass


class Suspended(ReprimandBase):
    pass


class Banned(ReprimandBase):
    pass
