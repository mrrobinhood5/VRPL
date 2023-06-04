from random import randint
from essential_generators import DocumentGenerator, StatisticTextGenerator
# from testing_utils.test_data import team_names
from wonderwords import RandomWord

# from classes.errors import PlayerError

doc_gen = DocumentGenerator(text_generator=StatisticTextGenerator())
team_gen = RandomWord()


def get_discord_ids():
    ids = [188481379305127936, 960435300037967913, 1055872495451914270, 552891061471805444, 832067515894333461, 388371441474863114, 512853483137925140, 829173829334466590, 781663875161653268, 297166430263050243, 290162179531997185, 169161943511203840, 769009471719866378, 937877915364892682, 292327430302203904, 271812482119499784, 881746893598765127, 505133469341581332, 1048411125185773659, 623277032930803742, 148180986847297537, 942627248769466398, 211221306211958785, 1027340746136748032, 1041774831030505492, 954546858561273907, 662211833339445260, 308813424677093378, 670991230619877398, 863872178381783060, 1045365648936673380, 934288584524042282, 942019745971052564, 791411755124523018, 810405815390306334, 939740067784716328, 993032193741959279, 219314163455885314, 815768069405933640, 977753837706305579, 949848148560449676, 393141102846148613, 1112621234442743858, 761301553180180530, 959251781647474728, 894978441303195688, 1030342700442075166, 940175314875731988, 800063954272780318, 563220660285997074, 966380315608219648, 183830692554080256, 974230167767613470, 503270407978221568, 711805779178684493, 859523993106251836, 788199960570101760, 693633669494997103, 1025762556385706035, 474570675135447041, 956915581808951366, 968873601304526848, 567804381496606742, 957658024447733841, 806778056131477524, 200340887639818241, 710184102460129382, 968001148676100186, 934613419271802930, 781833750933012512, 941722322010796042, 290209006088355861, 741334418056282303, 401351645834903553, 141967229523591168, 790330702189166644, 924386135428456488, 962493237006860319, 259133196602572812, 356932644107190275, 300921939826835458, 810159478750052443, 714469427537641474, 653305913125371921, 208934380679200770, 998766899141808128, 944095319065509959, 1007394834509725726, 1087933933448073326, 344732185749618688, 781185512215937034, 421140347284881438, 301423883851005952, 1044449755809448007, 998769668074508319, 955896131404038154, 1057391558778957916, 1047869908115005482, 992394019885813770, 393441211102265345, 711015436183142422, 781779934837735446, 930570595752640522, 699928061365321809, 501882942625284116, 998080408908472391, 1095537359090618378, 988956779914342410, 175124435970293763, 134498100197851141, 653278791896137728, 448671422873600000, 931328032499699803, 956388834424283176, 985831015878639637, 1032788836809441280, 629526880126631937, 985985480921350254, 310291550175494144, 960801274738122843, 460499091819069460, 948835677896855572, 871127219458703420, 509228759661150208, 737429970174869555, 191622351589212160, 145502229544042497]

    index = 0

    while True:
        yield ids[index]
        index = (index + 1) % len(ids)


# def generate_players(amount: int) -> bool:
#     """
#     generates Player objects for testing
#     :param amount: how many player objects to create
#     :return: True if successful
#     """
#     for x in range(0, amount):
#         try:
#             Player(game_uid=generate_guid(),
#                    name=generate_username())
#         except PlayerError as e:
#             print(f'PlayerError: {e}')
#     return True


def make_member_id() -> str:
    _id = randint(99999999999999999, 999999999999999999)
    return str(_id)


def generate_team_name() -> str:
    t = randint(1, 3)
    _f = []
    if t == 1:
        _f.append(team_gen.word(include_parts_of_speech=['noun'], word_min_length=10))
    elif t == 2:
        _f.append(team_gen.word(include_parts_of_speech=['adjective'], word_min_length=4))
        _f.append(team_gen.word(include_parts_of_speech=['noun'], word_min_length=4))
    else:
        _f.append(team_gen.word(include_parts_of_speech=['adjective'], word_min_length=4))
        _f.append(team_gen.word(include_parts_of_speech=['verb'], word_min_length=4))
        _f.append(team_gen.word(include_parts_of_speech=['noun'], word_min_length=4))
    return ' '.join(_f).title()


def generate_username() -> str:
    _username = doc_gen.email().split('@')[0]
    if len(_username) < 6:
        return generate_username()
    else:
        return _username


def generate_email() -> str:
    return doc_gen.email()


def generate_link() -> str:
    return doc_gen.url()


def generate_description() -> str:
    return doc_gen.gen_sentence(min_words=10, max_words=25)


def generate_guid() -> str:
    return doc_gen.guid().replace('-', '')[:18]
