from random import randint
from essential_generators import DocumentGenerator, StatisticTextGenerator
# from testing_utils.test_data import team_names
from wonderwords import RandomWord

doc_gen = DocumentGenerator(text_generator=StatisticTextGenerator())
team_gen = RandomWord()


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


def generate_link() -> str:
    return doc_gen.url()


def generate_description() -> str:
    return doc_gen.gen_sentence(min_words=10, max_words=25)


def generate_guid() -> str:
    return doc_gen.guid().replace('-', '')[:18]
