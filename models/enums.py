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


class PlayerSearchType(Enum):
    ByDiscord = 'by Discord'
    ByName = 'by Name'

class PlayersSearchType(Enum):
    LOCATION = 'By Location'
    ALIAS = 'By Alias'
    BANNED = 'If Banned'
    SUSPENDED = 'If Suspended'
    CAPTAINS = 'If Captain'
    COCAPTAINS = 'If CoCaptain'
