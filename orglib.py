from exeptions.custom_exeptions import *


class AdminHandler:
    def __init__(self, password):
        self._ids = []
        self._processing = []
        self._pass = password
        self._asking = []

    def need_to_call(self, cid):
        return cid in self._processing

    def asking(self, cid):
        return cid in self._asking

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

    def add_asking(self, cid):
        self._asking.append(cid)

    def remove_asking(self, cid):
        self._asking.remove(cid)
