class NotificationHandler:
    def __init__(self):
        self._map = {}

    def try_add_item(self, item):
        """
        Первый элемент списка 'flags' - уведомление на текущий доклад еще не отправлено
        Второй - доклад еще не начался
        """
        if self._map.get(item['id']) is None:
            self._map[item['id']] = {
                'flag': True,
                'data': item
            }

    def is_in_queue(self, key):
        return self._map.get(key) is not None

    def need_to_send(self, key):
        if self._map.get(key) is not None:
            return self._map[key]['flag']

    def set_flag_false(self, key):
        if self._map.get(key) is not None:
            self._map[key]['flag'] = False

    def rm_key(self, key):
        self._map.pop(key)

    def get_data(self):
        return [item['data'] for item in self._map.values()]
