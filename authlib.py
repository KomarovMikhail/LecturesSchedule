import random
from constants.config import IMG_PATH, NO_PHOTO_FLAG
import psycopg2
from constants.queries import *
from botlib import skip_button, main_menu_button
import array


class AuthHandler:
    def __init__(self, db_path):
        self._auth_queue = {}
        self._db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = psycopg2.connect(self._db_path, sslmode='require')
        cursor = conn.cursor()
        cursor.execute(IF_DROP_PARTICIPANTS)
        cursor.execute(IF_CREATE_PARTICIPANTS)

        # test labels
        # cursor.execute(INSERT_PARTICIPANTS.format(1, 'username1', 'name1', 'job1', 'interests1', "B'1'", None))
        # cursor.execute(INSERT_PARTICIPANTS.format(2, 'username2', 'name2', 'job2', 'interests2', "B'1'", None))

        conn.commit()
        conn.close()

    def _increment_step(self, client_id):
        self._auth_queue[client_id]['step'] += 1

    def _remove_client(self, client_id):
        self._auth_queue.pop(client_id)

    def _get_step(self, client_id):
        return self._auth_queue[client_id]['step']

    def _append_data(self, client_id, data):
        self._auth_queue[client_id]['data'].append(data)

    def _add_to_db(self, client_id):
        conn = psycopg2.connect(self._db_path, sslmode='require')
        cursor = conn.cursor()

        data = self._auth_queue[client_id]['data']
        cursor.execute(EXISTS_PARTICIPANTS.format(client_id))
        exists = cursor.fetchall()

        data_insert_img = {
            'data': psycopg2.Binary(open(data[6], 'rb').read())
        }

        if exists[0][0]:
            cursor.execute(UPDATE_PARTICIPANTS.format(data[0], data[1], data[2], data[3], data[4], data[5]),
                           data_insert_img)
        else:
            cursor.execute(INSERT_PARTICIPANTS.format(data[0], data[1], data[2], data[3], data[4], data[5]),
                           data_insert_img)

        conn.commit()
        conn.close()

    def _exists_prev(self, client_id):
        return self._auth_queue[client_id]['prev'] is not None

    def add_client(self, client_id):
        prev = self.get_profile(client_id)
        self._auth_queue[client_id] = {
            'step': 0,
            'data': [],
            'prev': prev
        }

    def is_in_queue(self, client_id):
        """
        Возвращает True, если пользователь еще не делал запрос на авторизацию,
        либо уже авторизировался, False - иначе
        """
        return self._auth_queue.get(client_id) is None

    def make_step(self, client_id, message, bot):
        """
        Прим.: на шаге 0 обрабатывается сообщение от бота, на последующих - от пользователя
        """
        step = self._get_step(client_id)
        if step == 0:
            self._append_data(client_id, message.chat.id)
            self._increment_step(client_id)
            reply_markup = skip_button(take_from_profile=True)
            bot.send_message(message.chat.id, "Как тебя зовут?", reply_markup=reply_markup)
        elif step == 1:
            reply_markup = skip_button()
            self._append_data(client_id, message.from_user.username)
            if message.text == "Взять из профиля":
                name = '{0} {1}'.format(message.from_user.first_name, message.from_user.last_name)
                self._append_data(client_id, name)
            elif message.text != 'Пропустить':
                self._append_data(client_id, message.text)
            else:
                if self._exists_prev(client_id):
                    self._append_data(client_id, self._auth_queue[client_id]['prev']['fullname'])
                else:
                    self._append_data(client_id, 'Не указано')
            self._increment_step(client_id)
            bot.send_message(message.chat.id, "Кем ты работаешь?", reply_markup=reply_markup)
        elif step == 2:
            reply_markup = skip_button()
            if message.text != 'Пропустить':
                self._append_data(client_id, message.text)
            else:
                if self._exists_prev(client_id):
                    self._append_data(client_id, self._auth_queue[client_id]['prev']['job'])
                else:
                    self._append_data(client_id, 'Не указано')
            self._increment_step(client_id)
            bot.send_message(message.chat.id, "Расскажи немного о себе и своих интересах.", reply_markup=reply_markup)
        elif step == 3:
            if message.text != 'Пропустить':
                self._append_data(client_id, message.text)
            else:
                if self._exists_prev(client_id):
                    self._append_data(client_id, self._auth_queue[client_id]['prev']['interests'])
                else:
                    self._append_data(client_id, 'Не указано')
            self._append_data(client_id, "B'1'")
            self._increment_step(client_id)
            reply_markup = skip_button(take_from_profile=True)
            bot.send_message(message.chat.id, "Загрузи фото для твоего профиля.", reply_markup=reply_markup)
        elif step == 4:
            if message.text == "Взять из профиля":
                request = bot.get_user_profile_photos(message.from_user.id)
                file_info = bot.get_file(request.photos[0][-1].file_id)
                downloaded = bot.download_file(file_info.file_path)

                src = IMG_PATH + str(message.chat.id)
                with open(src, 'wb') as new_file:
                    new_file.write(downloaded)
                self._append_data(client_id, src)
            elif message.text != 'Пропустить':
                file_info = bot.get_file(message.photo[-1].file_id)
                downloaded = bot.download_file(file_info.file_path)

                src = IMG_PATH + str(message.chat.id)
                with open(src, 'wb') as new_file:
                    new_file.write(downloaded)
                self._append_data(client_id, src)
            else:
                if self._exists_prev(client_id):
                    self._append_data(client_id, self._auth_queue[client_id]['prev']['photo'])
                else:
                    self._append_data(client_id, NO_PHOTO_FLAG)

            self._add_to_db(client_id)
            self._remove_client(client_id)
            main_menu = main_menu_button()
            user = self.get_profile(client_id)
            text = "Спасибо! Я записал тебя в список участников. Вот твой текущий профиль:\nИмя: {0}\nГде работаешь: " \
                   "{1}\nИнтересы: {2}".format(user['fullname'], user['job'], user['interests'])
            bot.send_message(client_id, text, reply_markup=main_menu)

            src = IMG_PATH + str(message.chat.id) + 'buf'
            # b = bytearray()
            # b.extend(map(ord, user['photo']))
            # print(type(b))
            f = open(src, 'wb')
            f.write(user['photo'])
            f.close()
            # with open(src, 'wb') as new_file:
            #     new_file.write(user['photo'])
            bot.send_photo(client_id, open(src, 'rb'))

    def get_profile(self, client_id):
        conn = psycopg2.connect(self._db_path, sslmode='require')
        cursor = conn.cursor()

        cursor.execute(SELECT_BY_ID_PARTICIPANTS.format(client_id))
        data = cursor.fetchall()
        conn.commit()
        conn.close()
        if len(data) == 0:
            return None
        else:
            return {
                'id': client_id,
                'username': data[0][0],
                'fullname': data[0][1],
                'job': data[0][2],
                'interests': data[0][3],
                'active': data[0][4],
                'photo': data[0][5]
            }

    def is_authorized(self, client_id):
        conn = psycopg2.connect(self._db_path, sslmode='require')
        cursor = conn.cursor()
        cursor.execute(EXISTS_PARTICIPANTS.format(client_id))
        data = cursor.fetchall()
        conn.commit()
        conn.close()
        return data[0][0]

    def get_participant(self, client_id):
        conn = psycopg2.connect(self._db_path, sslmode='require')
        cursor = conn.cursor()
        cursor.execute(SELECT_POSSIBLE_IDS_PARTICIPANTS.format(client_id))
        data = cursor.fetchall()
        possible = [item[0] for item in data]
        try:
            r = random.choice(possible)
            cursor.execute(SELECT_BY_ID_PARTICIPANTS.format(r))
            data = cursor.fetchall()
            conn.commit()
            conn.close()
            return {
                'id': r,
                'username': data[0][0],
                'fullname': data[0][1],
                'job': data[0][2],
                'interests': data[0][3],
                'active': data[0][4],
                'photo': data[0][5]
            }
        except IndexError:
            conn.commit()
            conn.close()
            return None

    def get_all_ids(self):
        conn = psycopg2.connect(self._db_path, sslmode='require')
        cursor = conn.cursor()
        cursor.execute(SELECT_ALL_IDS_PARTICIPANTS)
        data = cursor.fetchall()
        conn.commit()
        conn.close()
        return [item[0] for item in data]

    def get_users(self):
        conn = psycopg2.connect(self._db_path, sslmode='require')
        cursor = conn.cursor()
        cursor.execute(SELECT_ALL_PARTICIPANTS)
        data = cursor.fetchall()
        conn.commit()
        conn.close()
        return data

