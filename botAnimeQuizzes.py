# -*- coding: UTF-8 -*-
import telebot
import random
import json
import time


import Generator
import constants


bot = telebot.TeleBot(constants.token, threaded=False)

print(bot.get_me())
mas_photo_quiz = {}
mas_audio_quiz = {}
mas_emoji_quiz = {}


def write_json_ladder(id_pars: str, file_type: str, score_last: int, type_quiz: str):
    """ Запись значения в ладер файл """
    try:
        with open(file_type, encoding='utf-8') as data_file:
            data = json.load(data_file)
    except Exception:
        data = {}
    if type_quiz in data:
        if str(id_pars) in data[type_quiz]:
            score_present = data[type_quiz][str(id_pars)]
        else:
            score_present = 0
    else:
        data.update({type_quiz: {}})
        score_present = 0
    if file_type == constants.score_table:
        """ For count score in last game"""
        score_present += 1
        data[type_quiz].update({str(id_pars): score_present})
        with open(constants.score_table, 'w') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
    elif file_type == constants.ladder:
        """ For write to ladder if need"""
        if score_last > score_present:
            data[type_quiz].update({str(id_pars): score_last})
            with open(constants.ladder, 'w') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)


def ladder_print(message, type_quiz: str, lang_text: dict):
    with open(constants.ladder, encoding='utf-8') as data_file:
        data = json.load(data_file)
    counter = 0
    lad_list = ['{0}'.format(lang_text["ladder"][5])]
    for ids in sorted(data[type_quiz], key=data[type_quiz].get, reverse=True):
        counter += 1
        if counter == 50:
            break
        else:
            lad_list.append('{0}.  {1} - {2}'.format(counter, ids, data[type_quiz][ids]))
            if str(message.from_user.id) == str(ids):
                lad_list.insert(-1, '{0}.  {1} - {2} <--- {3}'.format(counter, ids, data[type_quiz][ids],
                                                                      lang_text['ladder'][6]))
                lad_list.pop(-1)
    lad_markup = telebot.types.ReplyKeyboardMarkup(True, True)
    lad_markup.row('{0}'.format(lang_text["exit"]))
    bot.send_message(message.from_user.id, '\n'.join(lad_list), reply_markup=lad_markup)


def log(message):
    print("\n ------------------------")
    from datetime import datetime
    print(datetime.now())
    print("Сообщение от {0} {1}.(id = {2}) \nТекст - {3}".format(message.from_user.first_name,
                                                                 message.from_user.last_name,
                                                                 str(message.from_user.id),
                                                                 message.text.encode("utf-8")))


def handle_lose(message, score_last: int, lang_text, type_quiz: str):
    lose_markup = telebot.types.ReplyKeyboardMarkup(True, True)
    lose_markup.row('{0}'.format(lang_text["refresh"][type_quiz]))
    lose_markup.row('{0}'.format(lang_text["exit"]))
    bot.send_message(message.from_user.id, '{0}{1}'.format(lang_text["refresh"]["lose"], score_last),
                     reply_markup=lose_markup)


@bot.message_handler(commands=["start"])
def handle_start(message):
    menu_markup = telebot.types.ReplyKeyboardMarkup(True, True)
    menu_markup.row('/ru')
    menu_markup.row('/eng')
    bot.send_message(message.from_user.id, '*Choose language*', parse_mode="Markdown",
                     reply_markup=menu_markup)


@bot.message_handler(commands=["help"])
def handle_help(message):
    lang_text = Generator.lang(message)
    bot.send_message(message.from_user.id, '*{0}*'.format(lang_text['help'][0]), parse_mode="Markdown")


@bot.message_handler(commands=['stop'])
def handle_stop(message):
    hide_markup = telebot.types.ReplyKeyboardRemove(True)
    bot.send_message(message.from_user.id, '..', reply_markup=hide_markup)


@bot.message_handler(commands=['menu'])
def handle_menu(message):
    lang_text = Generator.lang(message)
    #print('ALARM')
    menu_markup = telebot.types.ReplyKeyboardMarkup(True, True)
    menu_markup.row('{0}'.format(lang_text["menu"][0]))
    menu_markup.row('{0}'.format(lang_text["menu"][1]))
    menu_markup.row('{0}'.format(lang_text["menu"][4]))
    menu_markup.row('{0}'.format(lang_text["menu"][2]))
    bot.send_message(message.from_user.id, '*{0}*'.format(lang_text["menu"][3]), parse_mode="Markdown",
                     reply_markup=menu_markup)


@bot.message_handler(commands=['ru', 'eng'])
def handle_user_list(message):
    try:
        us_list = json.load(open(constants.user_list))
    except Exception:
        us_list = {}
    if not(str(message.from_user.id) in us_list):
        us_list.update({str(message.from_user.id): {}})
    us_list.update({str(message.from_user.id): [message.from_user.first_name, message.from_user.last_name,
                                                message.from_user.username, message.text.split("/")[1]]})
    with open(constants.user_list, 'w') as file:
        json.dump(us_list, file, indent=2, ensure_ascii=False)
        file.close()
    handle_menu(message)


@bot.message_handler(commands=['photoQuiz'])
def handle_photo_quiz(message, lang_text):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, True)
    global mas_photo_quiz
    with open(constants.score_table, encoding='utf-8') as data_file:
        data = json.load(data_file)
    if str(message.from_user.id) in data['photo']:
        score_table = data['photo'][str(message.from_user.id)]
    else:
        score_table = 0
    mas_photo_quiz[str(message.from_user.id)] = []
    photo_list = Generator.photo_dict(message)
    question_photo = Generator.theme_question(photo_list, score_table)
    mas_photo_quiz[str(message.from_user.id)] = question_photo.copy()
    ban_button = telebot.types.InlineKeyboardMarkup()
    callback_button = telebot.types.InlineKeyboardButton(text='{0}'.format(lang_text['ban']['req']),
                                                         callback_data='photo {0} {1}'.format(question_photo[4][:15],
                                                                                              message.from_user.id))
    ban_button.add(callback_button)
    img_quiz = question_photo.pop(4)
    user_markup.row(question_photo.pop(random.randrange(len(question_photo))),
                    question_photo.pop(random.randrange(len(question_photo))))
    user_markup.row(question_photo.pop(random.randrange(len(question_photo))),
                    question_photo.pop(random.randrange(len(question_photo))))
    user_markup.row('{0}'.format(lang_text["exit"]))
    bot.send_message(message.from_user.id, '{0}'.format(lang_text["guess"]), reply_markup=user_markup)
    bot.send_chat_action(message.from_user.id, 'upload_photo')
    bot.send_photo(message.from_user.id, img_quiz, reply_markup=ban_button)
    #print(mas_photo_quiz)


@bot.message_handler(commands=['musicQuiz'])
def handle_audio_quiz(message, lang_text):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, True)
    global mas_audio_quiz
    with open(constants.score_table, encoding='utf-8') as data_file:
        data = json.load(data_file)
    if str(message.from_user.id) in data['audio']:
        score_table = data['audio'][str(message.from_user.id)]
    else:
        score_table = 0
    mas_audio_quiz[str(message.from_user.id)] = []
    audio_list = Generator.audio_dict(message)
    question_audio = Generator.theme_question(audio_list, score_table)
    mas_audio_quiz[str(message.from_user.id)] = question_audio.copy()
    ban_button = telebot.types.InlineKeyboardMarkup()
    callback_button = telebot.types.InlineKeyboardButton(text='{0}'.format(lang_text['ban']['req']),
                                                         callback_data='audio {0} {1}'.format(question_audio[4],
                                                                                              message.from_user.id))
    ban_button.add(callback_button)
    music_quiz = question_audio.pop(4)
    user_markup.row(question_audio.pop(random.randrange(len(question_audio))),
                    question_audio.pop(random.randrange(len(question_audio))))
    user_markup.row(question_audio.pop(random.randrange(len(question_audio))),
                    question_audio.pop(random.randrange(len(question_audio))))
    user_markup.row('{0}'.format(lang_text["exit"]))
    bot.send_message(message.from_user.id, '{0}'.format(lang_text["guess"]), reply_markup=user_markup)
    bot.send_chat_action(message.from_user.id, 'upload_audio')
    bot.send_voice(message.from_user.id, music_quiz, reply_markup=ban_button)
    #print(mas_audio_quiz)


@bot.message_handler(commands=['emojiQuiz'])
def handle_emoji_quiz(message, lang_text):
    emoji_markup = telebot.types.ReplyKeyboardMarkup(True, True)
    global mas_emoji_quiz
    with open(constants.score_table, encoding='utf-8') as data_file:
        data = json.load(data_file)
    if str(message.from_user.id) in data['emoji']:
        score_table = data['emoji'][str(message.from_user.id)]
    else:
        score_table = 0
    mas_emoji_quiz[str(message.from_user.id)] = []
    emoji_list = Generator.emoji_dict(message)
    question_emoji = Generator.theme_question(emoji_list, score_table)
    mas_emoji_quiz[str(message.from_user.id)] = question_emoji.copy()
    emoji_quiz = question_emoji.pop(4)
    emoji_markup.row(question_emoji.pop(random.randrange(len(question_emoji))),
                     question_emoji.pop(random.randrange(len(question_emoji))))
    emoji_markup.row(question_emoji.pop(random.randrange(len(question_emoji))),
                     question_emoji.pop(random.randrange(len(question_emoji))))
    emoji_markup.row('{0}'.format(lang_text["exit"]))
    bot.send_message(message.from_user.id, emoji_quiz, reply_markup=emoji_markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    call_type, call_photo, user_id = call.data.split(' ')
    try:
        with open(constants.ban_list, encoding='utf-8') as data_file:
            ban_list = json.load(data_file)
    except Exception:
        ban_list = {}
    with open(constants.user_list) as data_file:
        user_data = json.load(data_file)
        if user_data[str(user_id)][3] == 'ru':
            with open(constants.lang_text,  encoding='utf-8') as d_file:
                lang = json.load(d_file)['ru']
        else:
            with open(constants.lang_text,  encoding='utf-8') as d_file:
                lang = json.load(d_file)['eng']
    language = user_data[user_id][3]
    if call_type in ban_list[language]:
        pass
    else:
        ban_list[language].update({call_type: {}})
    print(ban_list[language][call_type])
    if call_photo in ban_list[language][call_type]:
        if user_id in ban_list[language][call_type][call_photo]:
            back_message = '{0}'.format(lang['ban']['alr'])
        else:
            ban_list[language][call_type][call_photo].append(user_id)
            back_message = '{0}'.format(lang['ban']['ty'])
    else:
        ban_list[language][call_type].update({call_photo: []})
        ban_list[language][call_type][call_photo].append(user_id)
        back_message = '{0}'.format(lang['ban']['ty'])
    with open(constants.ban_list, 'w') as file:
        json.dump(ban_list, file, indent=2, ensure_ascii=False)
    bot.send_message(user_id, back_message)


@bot.message_handler(commands=['settings'])
def setiings(message):
    lang_text = Generator.lang(message)
    settings_markup = telebot.types.ReplyKeyboardMarkup(True, True)
    settings_markup.row('{0}'.format(lang_text["settings"]))
    settings_markup.row('{0}'.format(lang_text["exit"]))
    bot.send_message(message.from_user.id, 'Меню настроек', reply_markup=settings_markup)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    #log(message)
    global score_ind, ladder_type
    score_ind = 2
    lang_text = Generator.lang(message)
    """ Меню"""
    """ Виды викторины"""
    if message.text == '{0}'.format(lang_text["menu"][0]):
        if str(message.from_user.id) in mas_photo_quiz:
            mas_photo_quiz.pop(str(message.from_user.id))
        elif str(message.from_user.id) in mas_emoji_quiz:
            mas_emoji_quiz.pop(str(message.from_user.id))
        quiz_markup = telebot.types.ReplyKeyboardMarkup(True, True)
        quiz_markup.row('{0}'.format(lang_text["playQuiz"][0]))
        quiz_markup.row('{0}'.format(lang_text["playQuiz"][1]))
        quiz_markup.row('{0}'.format(lang_text["playQuiz"][2]))
        quiz_markup.row('{0}'.format(lang_text["playQuiz"][3]))
        bot.send_message(message.from_user.id, '{0}'.format(lang_text["playQuiz"][4]), reply_markup=quiz_markup)
        Generator.delet_bans()
        """Типы ладера"""
    elif message.text == '{0}'.format(lang_text["menu"][1]):
        ladder_markup = telebot.types.ReplyKeyboardMarkup(True, True)
        ladder_markup.row('{0}'.format(lang_text["ladder"][0]))
        ladder_markup.row('{0}'.format(lang_text["ladder"][1]))
        ladder_markup.row('{0}'.format(lang_text["ladder"][2]))
        ladder_markup.row('{0}'.format(lang_text["ladder"][3]))
        bot.send_message(message.from_user.id, '{0}'.format(lang_text["ladder"][4]), reply_markup=ladder_markup)
        """ Выход в меню"""
    elif message.text == '{0}'.format(lang_text["exit"]):
        """ Удаление из хранилища"""
        if str(message.from_user.id) in mas_photo_quiz:
            mas_photo_quiz.pop(str(message.from_user.id))
        elif str(message.from_user.id) in mas_emoji_quiz:
            mas_emoji_quiz.pop(str(message.from_user.id))
        elif str(message.from_user.id) in mas_audio_quiz:
            mas_audio_quiz.pop(str(message.from_user.id))
        handle_menu(message)
        """ Викторины """
        """ Обновление """
    elif message.text == '{0}'.format(lang_text["refresh"]["photo"]):
        handle_photo_quiz(message, lang_text)
    elif message.text == '{0}'.format(lang_text["refresh"]["audio"]):
        handle_audio_quiz(message, lang_text)
    elif message.text == '{0}'.format(lang_text["refresh"]["emoji"]):
        handle_emoji_quiz(message, lang_text)
        """ Фото викторина """
    elif message.text == '{0}'.format(lang_text["playQuiz"][0]):
        ladder_type = 'photo'
        handle_photo_quiz(message, lang_text)
    elif str(message.from_user.id) in mas_photo_quiz:
        if message.text == mas_photo_quiz[str(message.from_user.id)][0]:
            score_ind = 1
            bot.send_message(message.from_user.id, '{0}'.format(lang_text["win"]))
            handle_photo_quiz(message, lang_text)
        elif (message.text == mas_photo_quiz[str(message.from_user.id)][1]) \
                or (message.text == mas_photo_quiz[str(message.from_user.id)][2])\
                or (message.text == mas_photo_quiz[str(message.from_user.id)][3]):
            score_ind = 0
            with open(constants.score_table, encoding='utf-8') as data_file:
                sc_table = json.load(data_file)
            if str(message.from_user.id) in sc_table[ladder_type]:
                handle_lose(message, sc_table[ladder_type][str(message.from_user.id)], lang_text, ladder_type)
            else:
                handle_lose(message, 0, lang_text, ladder_type)
        """Музыкальная викториа"""
    elif message.text == '{0}'.format(lang_text["playQuiz"][1]):
        ladder_type = 'audio'
        handle_audio_quiz(message, lang_text)
    elif str(message.from_user.id) in mas_audio_quiz:
        if message.text == mas_audio_quiz[str(message.from_user.id)][0]:
            score_ind = 1
            bot.send_message(message.from_user.id, '{0}'.format(lang_text["win"]))
            handle_audio_quiz(message, lang_text)
        elif (message.text == mas_audio_quiz[str(message.from_user.id)][1]) \
                or (message.text == mas_audio_quiz[str(message.from_user.id)][2]) \
                or (message.text == mas_audio_quiz[str(message.from_user.id)][3]):
            score_ind = 0
            with open(constants.score_table, encoding='utf-8') as data_file:
                sc_table = json.load(data_file)
            if str(message.from_user.id) in sc_table[ladder_type]:
                handle_lose(message, sc_table[ladder_type][str(message.from_user.id)], lang_text, ladder_type)
            else:
                handle_lose(message, 0, lang_text, ladder_type)
        """Емоджи викторина"""
    elif message.text == '{0}'.format(lang_text["playQuiz"][2]):
        ladder_type = 'emoji'
        handle_emoji_quiz(message, lang_text)
    elif str(message.from_user.id) in mas_emoji_quiz:
        if message.text == (mas_emoji_quiz[str(message.from_user.id)][0]):
            score_ind = 1
            bot.send_message(message.from_user.id, '{0}'.format(lang_text["win"]))
            handle_emoji_quiz(message, lang_text)
        elif (message.text == mas_emoji_quiz[str(message.from_user.id)][1]) or \
                (message.text == mas_emoji_quiz[str(message.from_user.id)][2]) or \
                (message.text == mas_emoji_quiz[str(message.from_user.id)][3]):
            score_ind = 0
            with open(constants.score_table, encoding='utf-8') as data_file:
                sc_table = json.load(data_file)
            if str(message.from_user.id) in sc_table[ladder_type]:
                handle_lose(message, sc_table[ladder_type][str(message.from_user.id)], lang_text, ladder_type)
            else:
                handle_lose(message, 0, lang_text, ladder_type)
        """ Рейтинги """
    elif message.text == '{0}'.format(lang_text["ladder"][0]):
        ladder_print(message, 'photo', lang_text)
    elif message.text == '{0}'.format(lang_text["ladder"][1]):
        ladder_print(message, 'audio', lang_text)
    elif message.text == '{0}'.format(lang_text["ladder"][2]):
        ladder_print(message, 'emoji', lang_text)
        "Добавление контента"
    elif message.text == '{0}'.format(lang_text["menu"][4]):
        bot.send_message(message.from_user.id, '{0}'.format(lang_text["content"]))
        """Смена языка """
    elif message.text == '{0}'.format(lang_text["settings"]):
        handle_start(message)
    else:
        bot.send_message(message.from_user.id, 'Invalid command or text!')

    if score_ind == 1:
        #print(ladder_type)
        write_json_ladder(message.from_user.id, constants.score_table, 0, ladder_type)
    elif score_ind == 0:
        with open(constants.score_table, encoding='utf-8') as data_file:
            sc_table = json.load(data_file)
        if str(message.from_user.id) in sc_table[ladder_type]:
            if sc_table[ladder_type][str(message.from_user.id)] > 0:
                write_json_ladder(message.from_user.id, constants.ladder, sc_table[ladder_type][str(message.from_user.id)],
                                  ladder_type)
            sc_table[ladder_type].pop(str(message.from_user.id))
        with open(constants.score_table, 'w') as file:
            json.dump(sc_table, file, indent=2, ensure_ascii=False)


@bot.message_handler(content_types=['photo'])
def handler_photo(message):
    print('upload photo')
    fileID = message.photo[-1].file_id
    photo_info = message.caption
    print(fileID)
    file_info = bot.get_file(fileID)
    if photo_info is not "None":
        diff, *name_split = photo_info.split(' ')
        anime_name = ' '.join(name_split)
        if diff == "easy" or diff == "medium" or diff == "hard":
            if len(name_split) is not 0:
                Generator.add_photo(diff, anime_name, str(message.from_user.id), fileID)
        else:
            pass
    else:
        pass


bot.polling(none_stop=True)

"""while True:
    try:
        bot.polling(none_stop=True)

    except Exception as e:
        print(e)
        time.sleep(10)"""