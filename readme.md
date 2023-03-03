# VRCL Bot

---
The basic functionalily for this bot will be to keep a record of the VRCL lifecycle. I am planning on implementing in multiple phases:

- Phase 1: Management of Seasons, Games, Tournaments, Teams, Players
  - Add an API for the front end
- Phase 2: Extending functionality to provide **Team Captains** to schedule an agreed upon time and log scores. 
- Phase 3: Adding ability to store player stats 

## Phase 1: Initial Functionality

Discord Roles will have the following permissions

| Role        | Permissions                                                        |
|-------------|--------------------------------------------------------------------|
| @VRCL Staff | Can create, update, modify a season                                |
| @VRCL Staff | Can create, update, modify a new game                              |
| @VRCL Staff | Can create, update, modify a Tournament                            |
| @XX Captain | Can create, update, modify their own teams                         |
| @XX Captain | Can add co-captains to help manage a team add players and schedule |
| co-captain  | Can add players and schedule                                       |

The data will be stored as follows:

### Season Object
| associations | data type  | data               | example                                              |
|--------------|------------|--------------------|------------------------------------------------------|
| unique       | id         | _id                | 61da2d145899aa9fcf0effa4                             |
|              | text       | season name        | "Season 1: The First Season"                         |
|              | date_time  | start_date         | 1/1/2023                                             |
|              | date_time  | end_date           | 3/1/2023                                             |
|              | text       | description        | "*Do we even need a description?*"                   |

### Game Object
| associations | data type  | data               | example                                              |
|--------------|------------|--------------------|------------------------------------------------------|
| unique       | id         | _id                | 61db9c86720364fbecca9056                             |
|              | text       | name               | "Contractor$ "                                       |
|              | text       | description        | "*Do we even need a description?*"                   |

### Tournament Object
| associations  | data type         | data          | example                                              |
|---------------|-------------------|---------------|------------------------------------------------------|
| unique        | id                | _id           | 6180251e0f97f37119e9f6eb                             |
|               | text              | name          | "C$ 1v1 "                                            |
|               | text              | description   | "Singles Tournament, winner takes all"               |
|               | text              | rules         | "1. 2. 3. 4. etc.."                                  |
| has_many (or) | Team              | Team Objects  | [61e063d607af5708133436df, 61e1f1f901d2268267f5ca77] |
| has_many      | Discord Member.id | participants  | [754...541, 321...615]                               |
| belongs_to    | Game              | Game Object   | 61db9c86720364fbecca9056                             |
| belongs_to    | Season            | Season Object | 61da2d145899aa9fcf0effa4                             |

### Team Object
| associations | data type          | data              | example                                                    |
|--------------|--------------------|-------------------|------------------------------------------------------------|
| unique       | id                 | _id               | 61e063d607af5708133436df                                   |
|              | text               | name              | "The Plumbers "                                            |
|              | text               | description       | "*Plumbing our way downtown, plumbing fast, faces splash*" |
| has_one      | Discord Member.id  | team_captain      | "623...123"                                                |
| has_one      | Discord Member.id  | team_cocaptain    | "623...124"                                                |
| has_many     | Discord Member.ids | players           | [123...124, 121...014, 145...654]                          |
| has_many     | Discord Member.ids | players           | [123...124, 121...014, 145...654]                          |
| belongs_to   | Tournament         | Tournament Object | 6180251e0f97f37119e9f6eb                                   |
| belongs_to   | Game               | Game Object       | 61db9c86720364fbecca9056                                   |
| belongs_to   | Season             | Season Object     | 61da2d145899aa9fcf0effa4                                   |

### Player Object
| associations | data type | data            | example                  |
|--------------|-----------|-----------------|--------------------------|
| unique       | id        | _id             | 61db9c86720364fbecca9056 |
| belongs_to   | Team      | Team Object     | 61e063d607af5708133436df |
|              | text      | contractors_uid | rrxcypavaw2cb            |
|              | text      | ingame_name     | mrrobinhood5             |