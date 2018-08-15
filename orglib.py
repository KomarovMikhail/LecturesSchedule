class AdminHandler:
    def __init__(self, password):
        self._ids = []
        self._map = {}
        self._pass = password

    def need_to_call(self, cid):
        return self._map.get(cid) is not None

