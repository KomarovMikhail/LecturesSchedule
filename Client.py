class Client:
    def __init__(self):
        self._personal_data_step = 0
        self._is_authorized = False

    def is_authorized(self):
        return self._personal_data_step == 0

    def increment_step(self):
        self._personal_data_step += 1

    def clean_step(self):
        self._personal_data_step = 0

    def get_step(self):
        return self._personal_data_step
