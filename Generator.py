import json
import random
import os

import emoji_data
import constants


def photo_dict(message):
    photo_list = os.curdir + '/Quiz/'
    with open(constants.user_list) as data_file:
        user_data = json.load(data_file)
    language = user_data[str(message.from_user.id)][3]
    if language == 'ru':
        with open(photo_list + 'photo_id_ru.json', encoding='utf-8') as data_file:
            list_full = json.load(data_file)
        return list_full
    elif language == 'eng':
        with open(photo_list + 'photo_id_eng.json', encoding='utf-8') as data_file:
            list_full = json.load(data_file)
        return list_full
    else:
        return 0


def audio_dict(message):
    audio_list = os.curdir + '/Quiz/'
    with open(constants.user_list) as data_file:
        user_data = json.load(data_file)
    language = user_data[str(message.from_user.id)][3]
    if language == 'ru':
        with open(audio_list + 'music_id_ru.json', encoding='utf-8') as data_file:
            music_list = json.load(data_file)
        return music_list
    elif language == 'eng':
        with open(audio_list + 'music_id_eng.json', encoding='utf-8') as data_file:
            music_list = json.load(data_file)
        return music_list
    else:
        return 0


def add_photo(difficulty, anime_name, user_id, photo_id):
    photo_list = os.curdir + '/Quiz/'
    with open(constants.user_list) as data_file:
        user_data = json.load(data_file)
    language = user_data[user_id][3]
    with open(photo_list + 'photo_id_{0}.json'.format(language), encoding='utf-8') as data_file:
        database_photo = json.load(data_file)
    if anime_name in database_photo[difficulty]:
        database_photo[difficulty][anime_name].append(photo_id)
    else:
        database_photo[difficulty].update({anime_name: [photo_id]})
    try:
        with open(photo_list + 'photo_id_{0}.json'.format(language), 'w', encoding='utf-8') as file:
            json.dump(database_photo, file, indent=2, ensure_ascii=False)
    except Exception:
        pass


def emoji_dict(message):
    with open(constants.user_list) as data_file:
        user_data = json.load(data_file)
    language = user_data[str(message.from_user.id)][3]
    if language == 'ru':
        return emoji_data.emoji_dict_ru
    elif language == 'eng':
        return emoji_data.emoji_dict_eng
    else:
        return 0


def theme_question(dict_theme, count):
    """ Random bust coupe anime-theme and writing to the list """
    anime = []
    theme = []
    level = "easy"
    if count < 80:
        level = "easy"
    elif (count >= 80) and (count < 150):
        level = "medium"
    elif count >= 150:
        level = "hard"
    for i in range(0, 4):
        while 1:
            anime_v, themes_v = random.choice(list(dict_theme[level].items()))
            if anime_v in anime:
                pass
            else:
                anime.append(anime_v)
                theme.append(random.choice(themes_v))
                break
    question_mas = [anime[0], anime[1], anime[2], anime[3], theme[0]]
    return question_mas


def lang(message):
    with open(constants.user_list) as data_file:
        user_data = json.load(data_file)
        if str(message.from_user.id) in user_data:
            if user_data[str(message.from_user.id)][3] == 'ru':
                with open(constants.lang_text, encoding='utf-8') as d_file:
                    lang = json.load(d_file)['ru']
            else:
                with open(constants.lang_text, encoding='utf-8') as d_file:
                    lang = json.load(d_file)['eng']
        else:
            with open(constants.lang_text, encoding='utf-8') as d_file:
                lang = json.load(d_file)['eng']
    return lang


def delet_bans():
    try:
        with open(constants.ban_list, encoding='utf-8') as data_file:
            ban_list = json.load(data_file)
    except Exception:
        pass
    for language in ban_list:
        for typeQv in ban_list[language]:
            for element in ban_list[language][typeQv]:
                if len(ban_list[language][typeQv][element]) > 10:
                    if typeQv == 'photo':
                        photo_list = os.curdir + '/Quiz/'
                        with open(photo_list + 'photo_id_{0}.json'.format(language), encoding='utf-8') as data_file:
                            list_of_photo = json.load(data_file)
                        for complexity in list_of_photo:
                            for anime in list_of_photo[complexity]:
                                for photo_num in list_of_photo[complexity][anime]:
                                    if photo_num[:15] == element:
                                        list_of_photo[complexity][anime].remove(photo_num)
                                        ban_list[language][typeQv][element].clear()
                                    else:
                                        pass
                        photo_list = os.curdir + '/Quiz/'
                        with open(photo_list + 'photo_list_{0}.json'.format(language), "w", encoding='utf-8') as file:
                            json.dump(list_of_photo, file, indent=2, ensure_ascii=False)
    with open(constants.ban_list, "w") as data_file:
        json.dump(ban_list, data_file, indent=2, ensure_ascii=False)


