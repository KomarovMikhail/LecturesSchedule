import openpyxl


class AuthHandler:
    def __init__(self, db_path):
        self._auth_queue = {}
        self._auth_num = 0
        self._db_path = db_path
        self._init_db()

    def _init_db(self):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Participants'

        labels = ['id', 'name', 'job', 'interests', 'is_active']
        ws.append(labels)

        wb.save(filename=self._db_path)

    def _increment_step(self, client_id):
        self._auth_queue[client_id]['step'] += 1

    def _remove_client(self, client_id):
        self._auth_queue.pop(client_id)

    def _get_step(self, client_id):
        return self._auth_queue[client_id]['step']

    def _append_data(self, client_id, data):
        self._auth_queue[client_id]['data'].append(data)

    def _add_to_db(self, client_id):
        wb = openpyxl.load_workbook(filename=self._db_path)
        ws = wb['Participants']
        self._auth_num += 1

        ws.append(self._auth_queue[client_id]['data'])

        wb.save(self._db_path)

    def get_auth_num(self):
        return self._auth_num

    def add_client(self, client_id):
        self._auth_queue[client_id] = {
            'step': 0,
            'data': []
        }

    def is_authorized(self, client_id):
        """
        Возвращает True, если пользователь еще не делал запрос на авторизацию,
        либо уже авторизировался, False - иначе
        """
        return self._auth_queue.get(client_id) is None

    def make_step(self, client_id, message, bot):
        step = self._get_step(client_id)
        if step == 0:
            self._append_data(client_id, message.chat.id)
            self._increment_step(client_id)
            bot.send_message(message.chat.id, "Как тебя зовут?")
        elif step == 1:
            self._append_data(client_id, message.text)
            self._increment_step(client_id)
            bot.send_message(message.chat.id, "Кем ты работаешь?")
        elif step == 2:
            self._append_data(client_id, message.text)
            self._increment_step(client_id)
            bot.send_message(message.chat.id, "Расскажи немного о себе и своих интересах")
        elif step == 3:
            self._append_data(client_id, message.text)
            self._append_data(client_id, True)

            self._add_to_db(client_id)
            self._remove_client(client_id)
            bot.send_message(message.chat.id, "Спасибо! Я записал тебя в список участников")
