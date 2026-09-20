class UnauthorizedError(Exception):
    pass

class UrlAlreadyExistsError(Exception):
    pass

class InvalidCodeError(Exception):
    pass

class ForbiddenResourceError(Exception):
    pass

class UrlNotFoundError(Exception):
    pass

class UserAlreadyExistsError(Exception):
    pass

class IncorrectLoginDataError(Exception):
    pass