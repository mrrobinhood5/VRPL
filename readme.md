# VRCL Bot

---
The basic functionalily for this bot will be to keep a record of the VRCL lifecycle. I am planning on implementing in multiple phases:

- Phase 1: Management of Seasons, Games, Tournaments, Teams, Players
  - Add an API for the front end
- Phase 2: Extending functionality to provide **Team Captains** to schedule an agreed upon time and log scores. 
- Phase 3: Adding ability to store player stats 

## Phase 1: Initial Functionality

Discord Roles will have the following permissions

| Role        | Permissions                                                              |
|-------------|--------------------------------------------------------------------------|
| @VRCL Staff | Can create, update, modify a season                                      |
| @VRCL Staff | Can create, update, modify a new game                                    |
| @VRCL Staff | Can create, update, modify a Tournament                                  |
| @XX Captain | Can create, update, modify their own teams, join tournaments and seasons |
| @XX Captain | Can add co-captains to help manage a team add players and schedule       |
| co-captain  | Can add players and schedule                                             |

The data will be stored as follows:

### Season Object
|             | name        | datatype              | description                                                                            |
|-------------|-------------|-----------------------|----------------------------------------------------------------------------------------|
| attribute   | _id         | BSON.ObjectId         | required unique id for MongoDB                                                         |
| attribute   | name        | str                   | Name of the season, searchable with .get()                                             |
| attribute   | description | str                   | Brief description of the season, maybe a link to something                             |
| attribute   | start_date  | datetime              | defaults to today() but can be set to any date                                         |
| attribute   | end_date    | datetime              | defaults to 6 months from start_date but can be set to any date                        |
| property    | id          | str                   | string representation of _id                                                           |
| property    | active      | bool                  | True if end date is after today()                                                      |
| property    | games       | List[Game]            | returns a list of Game objects that match this season                                  |
| property    | tournaments | List[Tournament]      | returns a list of Tournament objects that match this Season                            |
| method      | to_dict()   | dict                  | returns a dict representation of the object to store in the DB                         |
| classmethod | get()       | Union[Obj, List[Obj]] | returns any matches to a search term, or just one object if only one match in the name |
| classmethod | count()     | int                   | returns the count of instances created                                                 |

### Game Object
| associations | name        | data type             | description                                                                            |
|--------------|-------------|-----------------------|----------------------------------------------------------------------------------------|
| attribute    | _id         | BSON.ObjectId         | required unique id for MongoDB                                                         |
| attribute    | name        | str                   | Name of the game, searchable with .get()                                               |
| attribute    | description | str                   | Brief description of the game, maybe a link to something                               |
| method       | to_dict()   | dict                  | returns a dict representation of the object to store in the DB                         |
| classmethod  | get()       | Union[Obj, List[Obj]] | returns any matches to a search term, or just one object if only one match in the name |
| classmethod  | count()     | int                   | returns the count of instances created                                                 |

### Tournament Object
| associations | name                       | data type             | description                                                                            |
|--------------|----------------------------|-----------------------|----------------------------------------------------------------------------------------|
| attribute    | _id                        | BSON.ObjectId         | required unique id for MongoDB                                                         |
| attribute    | name                       | str                   | Name of the game, searchable with .get()                                               |
| attribute    | description                | str                   | Brief description of the game, maybe a link to something                               |
| attribute    | rules                      | str                   | either a link to the rules, or the detaild rules                                       |
| attribute    | individual                 | bool                  | if True, it will not allow Teams to be attached to it only Players                     |
| attribute    | active                     | bool                  | if True, it will allow additions, or changes to the tournament                         |
| attribute    | swaps_allowed              | bool                  | if True, changes in teams rosters will be allowed                                      |
| attribute    | max_match_players_per_team | int                   | number of players allowed per match                                                    |
| attribute    | belongs_to_game            | Game                  | which game this Tournament plays                                                       |
| attribute    | belong_to_season           | Season                | which season this tournament belongs to                                                |
| property     | teams                      | List[Team]            | returns a list of teams that have registered in the Tournament                         |
| property     | players                    | List[Player]          | returns a list of players that have registered in the Tournament                       |
| method       | to_dict()                  | dict                  | returns a dict representation of the object to store in the DB                         |
| classmethod  | get()                      | Union[Obj, List[Obj]] | returns any matches to a search term, or just one object if only one match in the name |
| classmethod  | count()                    | int                   | returns the count of instances created                                                 |

### Team Object
| associations | name                  | data type             | description                                                                            |
|--------------|-----------------------|-----------------------|----------------------------------------------------------------------------------------|
| attribute    | _id                   | BSON.ObjectId         | required unique id for MongoDB                                                         |
| attribute    | name                  | str                   | Name of the game, searchable with .get()                                               |
| attribute    | description           | str                   | Brief description of the game, maybe a link to something                               |
| attribute    | captain               | Player                | Player object who will act as captain                                                  |
| attribute    | co-captain            | Player                | Player object who will act as co-captain                                               |
| attribute    | active                | bool                  | if True, team can be changed and modified                                              |
| attribute    | belongs_to_tournament | Tournament            | which tournament this team belongs to                                                  |
| property     | team_full             | bool                  | returns True if there are 10 players registered to the team                            |
| property     | player_count          | int                   | returns the number of players registered in the team                                   |
| property     | players               | List[Player]          | returns the list of Player Objects in this team                                        |
| classmethod  | get()                 | Union[Obj, List[Obj]] | returns any matches to a search term, or just one object if only one match in the name |
| classmethod  | count()               | int                   | returns the count of instances created                                                 |

### Player Object
| associations | name                  | data type             | description                                                                                          |
|--------------|-----------------------|-----------------------|------------------------------------------------------------------------------------------------------|
| attribute    | _id                   | BSON.ObjectId         | required unique id for MongoDB                                                                       |
| attribute    | game_uid              | str                   | the game uid/guid for reference                                                                      |
| attribute    | belongs_to_team       | List[Team]            | list of teams that a player belongs to. Keep in mind, only one team per tournament per game is valid |
| attribute    | belongs_to_tournament | List[Tournament]      | list of tournaments the player has registered under                                                  |
| attribute    | in_game_name          | str                   | the name that is registered for this player                                                          |
| method       | join_tournament()     | bool                  | returns true if player successfully joins individual tournaments                                     |
| classmethod  | get()                 | Union[Obj, List[Obj]] | returns any matches to a search term, or just one object if only one match in the name               |
| classmethod  | count()               | int                   | returns the count of instances created                                                               |
