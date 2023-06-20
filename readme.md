# Virtual Reality Pro League Team Manager

---
The basic functionalily for this bot will be to keep a record of the VRPL lifecycle. I am planning on implementing in multiple phases:

- Phase 1: Allows for Player and Team registrations. Players can request to join Teams. Team captain or co-captains can approve their requests, remove players from teams and update team data
- Phase 2: Extends functionality to create Tournaments. Team captains/co-captains can join tournaments and auto-match scheduling. Scores will be submitted by home team and away team will confirm scores. App will generate MMR type scoring
- Phase 3: Extends functionality to include auto weekly map selection, tournament types (such as 1v1s), and maybe challenges 

## Phase 1: Initial Functionality

Discord will be used for authentication. The following commands are available:

- `Admins`
  - `/config` - Used to config which channels will be used as record keepers
- `Players`
  - Registration is done through the message in the configured player channel. By clicking the Register button a discord user can register to be a player in the league
  - `/players me` - Will show a private message with more information available about warnings and infractions
  - `/players list` - Will show a carousel of all registered players
  - `/players search` - Will show a carousel of players from a search term
  - `/teams my_team` - Displays the team that you belong in
- `Team Captains / Co-Captains`
  - Registration is done through the message in the configured teams channel. By clicking the Register Button a discord user can register a team
  - Joins will be done by the message in the teams channel. By clicking the Join Team, a player will be able to choose a team to request to join
  - `/teams my_team` - A team captain has the option to approve team joins, select a co-captain, and remove players from a team
  - `/teams list` - A carousel of teams that have registered
  - `/teams search` - Same as teams list but with a search term

## Phase 2: Extending

- `Admins`
  - Will have the ability to ban a player, issue warnings or offences to a player or team
  - Will be able to create tournaments team captains can join and have matches scheduled against it
- `Teams`
  - Will have the ability to submit scores after a match, and the other team approve the scores

## Phase 3: Future capabilities
TBD
