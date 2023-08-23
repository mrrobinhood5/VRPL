from beanie import Link
from .base import TournamentBase, PlayerBase, TeamBase, VRPLObject, WeekBase, MatchBase, MapBase
from models.enums import TournamentParticipation, MapTypes


class SwissSystemPlayerControlTournament(TournamentBase):
    is_joinable = True
    elimination = False
    participation = TournamentParticipation.PLAYER
    map_types = MapTypes.ONE

    participants: list[Link[PlayerBase]]

    def create_playoffs(self, number: int) -> list[PlayerBase]:
        """ will take the top %number% and return those objects """
        return True


class InvitationalPlayerControlTournament(TournamentBase):
    is_joinable = False
    elimination = True
    participation = TournamentParticipation.PLAYER
    map_types = MapTypes.ONE

    participants: list[Link[PlayerBase]]


class SwissSystemTeamCompTournament(TournamentBase):
    is_joinable = True
    elimination = False
    participation = TournamentParticipation.TEAM
    map_types = MapTypes.COMP

    participants: list[Link[TeamBase]]


class InvitationalTeamCompTournament(TournamentBase):
    is_joinable = False
    elimination = True
    participation = TournamentParticipation.TEAM
    map_types = MapTypes.COMP

    participants: list[Link[TeamBase]]
