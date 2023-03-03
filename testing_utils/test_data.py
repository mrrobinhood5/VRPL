from testing_utils.utils import generate_link

seasons = [
    {
        'name': 'Season 1',
        'description': 'Season one will be the best season ever, marks the start of VRCL',
        'start_date': '1/1/2023',
        'end_date': '6/1/2023'
    },
    {
        'name': 'Season 2',
        'description': 'Season two will be better than the first one!!',
        'start_date': '7/1/2023',
        'end_date': '12/1/2023'
    }]

games = [
    {
        'name': 'Contractor$',
        'description': 'Contractors, a game by Caveman. https://cavemangames.com'
    },
    {
        'name': 'Breachers',
        'description': 'Breachers is still in beta but its a popular game!'
    }
]

tournaments = [{
        'name': "Comp Control",
        'description': 'Comp Control is a popular mode to play where you have to keep control of an area',
        'rules': f'rules are long, here is the link {generate_link()}',
        'max_match_players_per_team': 5, },
    {
        'name': "1v1",
        'description': 'Free for all style game to find the best of the best single players',
        'rules': 'rules are simple.. Survive..',
        'individual': True,
        'max_match_players_per_team': 1,
    },
    {
        'name': 'Base Tournament',
        'description': 'Regular blue vs red game. find the bomb and pew pew pew',
        'rules': f'link to rules is {generate_link()}',
        'max_match_players_per_team': 6
    },
    {
        'name': 'Iron Man',
        'description': 'First of a kind, 7 game modes in one sitting, all you can eat',
        'rules': f'the rules are soo soo soo long, link here: {generate_link()}',
        'max_match_players_per_team': 8,
    },
    {
        'name': 'Iron Man v2',
        'description': 'This is the second go around for this game, fixing things from the first one',
        'rules': f'the rules are soo soo soo long, link here: {generate_link()}',
        'max_match_players_per_team': 8,
    }
]
team_names = iter(["Deadfire Captivity",
                   "Mortal Scream",
                   "Chromatic Death",
                   "Dream Scream Maniacs",
                   "Manic Bloom Kill",
                   "Brutal Thrill",
                   "Myriad Death Stomp",
                   "Scramble Tyrants",
                   "Diligent Kill Admirals",
                   "Calm Carnage",
                   "Purple Stomp",
                   "Deadwing Destiny",
                   "Mind Morph Maniacs",
                   "Abstract Death Poets",
                   "Ultra Doom Dreadheads",
                   "Fuzz Demons",
                   "Cluster Premonition",
                   "Wipeout Rebels",
                   "Death Immunity",
                   "Mighty Morph Midgets",
                   "Rogue Blend",
                   "Mute Bandits",
                   "Cult Lunatics",
                   "Dreamcry Apocalypse",
                   "Liquid Bash",
                   "Pain Messiahs",
                   "Blank Crash",
                   "Scream Shadow",
                   "Diabolic Death Squad",
                   "Freak Dimension",
                   "Rustic Absurdity",
                   "Spell Wizards",
                   "Epic Rising",
                   "Hellcore Rebels",
                   "Epic Death Givers",
                   "Sonic Bone Crush",
                   "Cryptic Firehunt",
                   "Endrospace Lords",
                   "Vicious Thrill Seekers",
                   "Bashful Bliss",
                   "Synergy Clan",
                   "Daydream Death Slayers",
                   "Tranquil Flesh Poets",
                   "Crash Logic",
                   "The Sinister Hack",
                   "Bone Bash Theory",
                   "Mellow Skin Peelers",
                   "Slaughter Bot Poltergeists",
                   "Bloodbath Bunnies",
                   "Cyber Demon Anarchy", ])
