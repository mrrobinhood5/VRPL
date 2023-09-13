from enum import Enum


class Location(Enum):
    US = 'United States'
    SA = 'South America'
    CA = 'Canada'
    UK = 'United Kingdom'
    AU = 'Australia'
    NZ = 'New Zealand'
    BR = 'Brazil'
    JP = 'Japan'
    CH = 'China'


class Region(Enum):
    NA = 'North America'
    APJ = 'Asia, Pacific, Japan'
    EU = 'Europe'


class MapTypes(Enum):
    COMP = 'Comp Control'
    DOM = 'Domination'
    ONE = 'Singles'


class TournamentParticipation(Enum):
    PLAYER = 'Player'
    TEAM = 'Team'


class SearchType(Enum):
    ALL = 'ALL'
    ByDiscord = 'by Discord'
    ByName = 'by Name'
    # ByLocation = 'By Location'
    # ByAlias = 'By Alias'
    # IsBanned = 'Is Banned'
    # IsSuspended = 'Is Suspended'
    # IsCaptain = 'Is Captain'
    # IsCoCaptain = 'Is CoCaptain'


class SearchOutputType(Enum):
    WithLinksToList = 'WithLinksToList'
    WithLinksOnlyOne = 'WithLinksOnlyOne'
    NoLinksToList = 'NoLinksToList'
    NoLinksOnlyOne = 'NoLinksOnlyOne'
    OnlyNames = 'OnlyNames'


