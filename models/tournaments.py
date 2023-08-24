from beanie import Link
from .base import TournamentBase, PlayerBase, TeamBase, VRPLObject, WeekBase, MatchBase, MapBase
from models.enums import TournamentParticipation, MapTypes


class SwissSystemPlayerControlTournament(TournamentBase):
    is_joinable: bool = True
    elimination: bool = False
    participation: TournamentParticipation = TournamentParticipation.PLAYER
    map_types: MapTypes = MapTypes.ONE

    participants: list[Link[PlayerBase]]

    def create_playoffs(self, number: int) -> list[PlayerBase]:
        """ will take the top %number% and return those objects """
        return True


class InvitationalPlayerControlTournament(TournamentBase):
    is_joinable: bool = False
    elimination: bool = True
    participation: TournamentParticipation = TournamentParticipation.PLAYER
    map_types: MapTypes = MapTypes.ONE

    participants: list[Link[PlayerBase]]


class SwissSystemTeamCompTournament(TournamentBase):
    is_joinable: bool = True
    elimination: bool = False
    participation: TournamentParticipation = TournamentParticipation.TEAM
    map_types: MapTypes = MapTypes.COMP

    participants: list[Link[TeamBase]]


class InvitationalTeamCompTournament(TournamentBase):
    is_joinable: bool = False
    elimination: bool = True
    participation: TournamentParticipation = TournamentParticipation.TEAM
    map_types: MapTypes = MapTypes.COMP

    participants: list[Link[TeamBase]]
