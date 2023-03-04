from testing_utils.utils import generate_link

seasons = [
    {
        'name': 'Season 1',
        'description': 'Season one will be the best season ever, marks the start of VRCL',
        'start_date': '10/1/2022',
        'end_date': '1/1/2023'
    },
    {
        'name': 'Season 2',
        'description': 'Season two will be better than the first one!!',
        'start_date': '2/1/2023',
        'end_date': '7/1/2023'
    },
    {
        'name': 'Season 3',
        'description': 'Season 3 is the most exciting yet, lots of new players',
        'start_date': '1/1/2024'
    }]

games = [
    {
        'name': 'Contractor$',
        'description': 'Contractors, a game by Caveman. https://cavemangames.com'
    },
    {
        'name': 'Breachers',
        'description': 'Breachers is still in beta but its a popular game!'
    },
    {
        'name': 'HyperDash',
        'description': 'Just like breachers but your dash around and shoot stuff'
    },
    {
        'name': 'Vail',
        'description': 'Yea i dont know anything about vail. I think its a slow version of C$'
    }
]

c_tournaments = [{
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
        'name': 'Bomb Defusal',
        'description': 'Find the bomb but dont die, if you die, you lose',
        'rules': f'link to rules is {generate_link()}',
        'max_match_players_per_team': 5
    },
    {
        'name': 'Iron Man',
        'description': 'First of a kind, 7 game modes in one sitting, all you can eat',
        'rules': f'the rules are soo soo soo long, link here: {generate_link()}',
        'max_match_players_per_team': 8,
    },
    {
        'name': 'Team Death Match',
        'description': 'Gather up your best team and play in a fast paced, spawn killing fest',
        'rules': f'the rules are soo soo soo long, link here: {generate_link()}',
        'max_match_players_per_team': 5,
    },
    {
        'name': 'Kill Confirmed',
        'description': 'collect all them tags or camp out in the one room all game, you chooose',
        'rules': f'rules are here: {generate_link()}',
        'max_match_players_per_team': 5,
    },
    {
        'name': 'Long Guns',
        'description': 'Shoot far or noscope everyone. pew pew pew',
        'rules': f'link to rules here: {generate_link()}',
        'max_match_players_per_team': 4,
    },
    {
        'name': 'Melee ONly',
        'description': 'otherwise known as onlypans. ',
        'rules': f'link again is here: {generate_link()}',
        'max_match_players_per_team': 5,
    },
    {
        'name': 'Pairs',
        'description': 'Grab a battle buddy and settle in',
        'rules': f'rules: {generate_link()}',
        'max_match_players_per_team': 2
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
