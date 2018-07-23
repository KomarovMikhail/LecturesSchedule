class Advisor:
    def __init__(self):
        self._map = {}

    def set_offer(self, client_id, offers):
        self._map[client_id] = offers

    def get_offer(self, client_id):
        return self._map.get(client_id)

    def del_client(self, client_id):
        self._map.pop(client_id)
