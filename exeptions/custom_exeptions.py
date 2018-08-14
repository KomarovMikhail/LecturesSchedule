class TimeError(Exception):
    """
    Содержит поле доклада, информация о котором неправлльно заполнена.
    """
    def __init__(self, *args, lecture=None):
        super(TimeError, self).__init__(*args)
        self._lecture = lecture

    def get_lecture(self):
        return self._lecture
