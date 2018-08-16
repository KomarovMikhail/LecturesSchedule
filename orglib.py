from exeptions.custom_exeptions import *


class AdminHandler:
    def __init__(self, password):
        self._ids = []
        self._processing = []
        self._pass = password

    def need_to_call(self, cid):
        return cid in self._processing

    def add_user(self, cid):
        if cid in self._ids:
            raise AlreadyAdminError
        self._processing.append(cid)

    def try_login(self, cid, password):
        if password == self._pass:
            self._ids.append(cid)
            self._processing.remove(cid)
            return True
        else:
            self._processing.remove(cid)
            return False

    def get_ids(self):
        return self._ids
