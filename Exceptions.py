class BadCreditentials(Exception):
    def __init__(self, message):
        super(BadCreditentials, self).__init__(message)
    

class UnknownError(Exception):
    def __init__(self, message):
        super(UnknownError, self).__init__(message)


class BadToken(Exception):
    def __init__(self, message):
        super(BadToken, self).__init__(message)


class BadPeriode(Exception):
    def __init__(self):
        super(BadPeriode, self).__init__()


class BadMatiere(Exception):
    def __init__(self):
        super(BadMatiere, self).__init__()
